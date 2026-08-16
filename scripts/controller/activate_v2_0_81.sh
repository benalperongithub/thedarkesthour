#!/usr/bin/env bash
set -Eeuo pipefail

SERVICE="strategy-lab-supervisor-v2.1.service"
UNIT="/etc/systemd/system/$SERVICE"
BASE="/srv/tdh-collab/controller/strategy-lab-v2"
OLD_VERSION="v2.0.79"
NEW_VERSION="v2.0.81"
NEW_RELEASE="$BASE/$NEW_VERSION"
GATE="/usr/local/sbin/tdh-lab-admin-gate"
STAMP="$(date -u +%Y%m%dT%H%M%SZ)"
START_ISO="$(date -u '+%Y-%m-%d %H:%M:%S UTC')"
BACKUP="${UNIT}.bak-${OLD_VERSION}-to-${NEW_VERSION}-${STAMP}"
VERIFY_UNIT="/tmp/strategy-lab-supervisor-v2.1-v281-verify-${STAMP}.service"
PREFLIGHT_LOG="/tmp/tdh-v2.0.81-activation-preflight.log"
RUN_MARKER="/tmp/tdh-v281-activation-run-${STAMP}.marker"
RUNTIME_VERIFY_TIMEOUT_SECONDS=1200
RUNTIME_VERIFY_POLL_SECONDS=10
RUNTIME_REQUIRED_EXHAUSTED_RUNS=3
UNIT_UPDATED=false
ACTIVATION_MODE=""
BACKUP_CREATED=false

cleanup() {
    rm -f -- "$VERIFY_UNIT" "$RUN_MARKER"
}

rollback_on_error() {
    local rc=$?
    trap - ERR
    echo "ACTIVATION_ERROR_RC=$rc"
    systemctl mask --runtime --now "$SERVICE" || true
    if [[ "$UNIT_UPDATED" == "true" && -f "$BACKUP" ]]; then
        install -o root -g root -m 0644 "$BACKUP" "$UNIT"
        systemctl daemon-reload || true
        echo "UNIT_ROLLED_BACK=$BACKUP"
    fi
    cleanup
    echo "FAIL_CLOSED: supervisor left stopped and runtime-masked"
    exit "$rc"
}

activation_fail() {
    return "$1"
}

trap cleanup EXIT
trap rollback_on_error ERR

echo "===== 1. KEEP v2.0.79 STOPPED ====="
systemctl mask --runtime --now "$SERVICE" || true
sleep 1
test "$(systemctl is-active "$SERVICE" || true)" != "active"

echo "===== 2. VERIFY SEALED v2.0.81 ====="
test -d "$NEW_RELEASE"
test -f "$NEW_RELEASE/SHA256SUMS"
(
    cd "$NEW_RELEASE"
    sha256sum -c SHA256SUMS >/dev/null
)
"$GATE" preflight "$NEW_VERSION" >"$PREFLIGHT_LOG"
grep -q '"status": "PREFLIGHT_OK"' "$PREFLIGHT_LOG"

python3 - "$NEW_RELEASE/config.json" <<'PY'
import json
import sys

with open(sys.argv[1], encoding='utf-8') as handle:
    config = json.load(handle)
assert config.get('research_mode') == 'offline'
assert config.get('trading_actions') is False
assert config.get('exchange_api_access') is False
print('OFFLINE_SAFETY_FLAGS_OK')
PY

echo "===== 3. BUILD AND VERIFY UPDATED SYSTEMD UNIT ====="
test -f "$UNIT"
read -r OLD_COUNT NEW_COUNT < <(
    python3 - "$UNIT" "$OLD_VERSION" "$NEW_VERSION" <<'PY'
from pathlib import Path
import sys

text = Path(sys.argv[1]).read_text(encoding='utf-8')
print(text.count(sys.argv[2]), text.count(sys.argv[3]))
PY
)

if [[ "$OLD_COUNT" -eq 5 && "$NEW_COUNT" -eq 0 ]]; then
    ACTIVATION_MODE="UPDATE_FROM_OLD"
elif [[ "$OLD_COUNT" -eq 0 && "$NEW_COUNT" -eq 5 ]]; then
    ACTIVATION_MODE="ALREADY_UPDATED"
else
    echo "BLOCKED: unexpected unit version references"
    echo "OLD_COUNT=$OLD_COUNT"
    echo "NEW_COUNT=$NEW_COUNT"
    exit 3
fi

if [[ "$ACTIVATION_MODE" == "UPDATE_FROM_OLD" ]]; then
    cp -a -- "$UNIT" "$BACKUP"
    BACKUP_CREATED=true
    python3 - "$UNIT" "$VERIFY_UNIT" "$OLD_VERSION" "$NEW_VERSION" <<'PY'
from pathlib import Path
import sys

source = Path(sys.argv[1])
destination = Path(sys.argv[2])
old_version = sys.argv[3]
new_version = sys.argv[4]
text = source.read_text(encoding='utf-8')
if text.count(old_version) != 5 or new_version in text:
    raise SystemExit('BLOCKED: unit replacement precondition failed')
updated = text.replace(old_version, new_version)
if updated.count(new_version) != 5 or old_version in updated:
    raise SystemExit('BLOCKED: unit replacement postcondition failed')
destination.write_text(updated, encoding='utf-8')
PY
else
    cp -a -- "$UNIT" "$VERIFY_UNIT"
    echo "UNIT_ALREADY_BOUND_TO=$NEW_VERSION"
fi

systemd-analyze verify "$VERIFY_UNIT"
grep -nF "$NEW_VERSION" "$VERIFY_UNIT"

echo "===== 4. INSTALL UNIT AND START v2.0.81 ====="
if [[ "$ACTIVATION_MODE" == "UPDATE_FROM_OLD" ]]; then
    install -o root -g root -m 0644 "$VERIFY_UNIT" "$UNIT"
    UNIT_UPDATED=true
else
    cmp -s -- "$VERIFY_UNIT" "$UNIT"
fi
systemctl daemon-reload
systemctl unmask --runtime "$SERVICE"
systemctl reset-failed "$SERVICE" || true
touch "$RUN_MARKER"
systemctl start "$SERVICE"
sleep 5
test "$(systemctl is-active "$SERVICE")" = "active"

MAIN_PID="$(systemctl show "$SERVICE" -p MainPID --value)"
[[ "$MAIN_PID" =~ ^[1-9][0-9]*$ ]]
CMDLINE="$(tr '\0' ' ' <"/proc/$MAIN_PID/cmdline")"
[[ "$CMDLINE" == *"$NEW_RELEASE/strategy_lab_controller.py"* ]]
echo "MAIN_PID=$MAIN_PID"
echo "CMDLINE=$CMDLINE"

echo "===== 5. VERIFY POST-S1 OR NO-FRONTIER CONTINUITY ====="
VERIFY_DEADLINE_EPOCH="$((
    $(date -u +%s) + RUNTIME_VERIFY_TIMEOUT_SECONDS
))"
LATEST_RUN=""
LATEST_STATE=""
S1_EVIDENCE_PATH=""
RUNTIME_BOUNDARY_MODE=""
QUALIFIED_EXHAUSTED_RUNS=0
LAST_QUALIFIED_EXHAUSTED_RUNS=-1
LAST_RUNTIME_STAGE=""

while :; do
    if [[ "$(systemctl is-active "$SERVICE" || true)" != "active" ]]; then
        echo "BLOCKED: v2.0.81 supervisor stopped during runtime verification"
        activation_fail 7
    fi

    MAIN_PID_AFTER="$(systemctl show "$SERVICE" -p MainPID --value)"
    if [[ ! "$MAIN_PID_AFTER" =~ ^[1-9][0-9]*$ ]]; then
        echo "BLOCKED: v2.0.81 supervisor has no live MainPID"
        activation_fail 8
    fi
    CMDLINE_AFTER="$(tr '\0' ' ' <"/proc/$MAIN_PID_AFTER/cmdline")"
    if [[ "$CMDLINE_AFTER" != *"$NEW_RELEASE/strategy_lab_controller.py"* ]]; then
        echo "BLOCKED: v2.0.81 supervisor command line drifted"
        echo "CMDLINE_AFTER=$CMDLINE_AFTER"
        activation_fail 9
    fi

    IFS='|' read -r \
        LATEST_STATE LATEST_RUN RUNTIME_STAGE BLOCKED_RUNS \
        INVALID_STATE_RUNS QUALIFIED_EXHAUSTED_RUNS \
        QUALIFIED_EXHAUSTED_LATEST_RUN S1_EVIDENCE_PATH < <(
        python3 - "$BASE/runs" "$RUN_MARKER" <<'PY'
from pathlib import Path
import json
import sys

runs_root = Path(sys.argv[1])
marker_ns = Path(sys.argv[2]).stat().st_mtime_ns
required = (
    'CODEX_PROPOSAL_SKIPPED_NO_LEGAL_FRONTIER.json',
    'FRONTIER_REPLENISHMENT_V254.json',
    'GLOBAL_MEMORY_QUEUE_FILTER_V274.json',
    'NODE_CHECKPOINTS_V263.json',
    'PACKET_A_GLOBAL_MEMORY_FILTER_V276.json',
    'SEALED_DIVERSIFICATION_BRIDGE_V278.json',
)

state_paths = sorted(
    path for path in runs_root.glob('tdh-strategy-lab-v2-*/STATE.json')
    if path.stat().st_mtime_ns > marker_ns
)
latest_state = state_paths[-1] if state_paths else None
latest_run = latest_state.parent if latest_state else None
latest_stage = 'NO_STATE'
blocked_count = 0
invalid_count = 0
qualified_runs = []
s1_paths = []

for state_path in state_paths:
    run = state_path.parent
    try:
        with state_path.open(encoding='utf-8') as handle:
            state = json.load(handle)
    except (OSError, ValueError, TypeError):
        invalid_count += 1
        continue

    stage = str(state.get('stage') or 'UNKNOWN')
    if state_path == latest_state:
        latest_stage = stage
    if stage == 'BLOCKED':
        blocked_count += 1

    evidence = run / 'round-01' / 'S1_FINANCIAL_EVIDENCE.json'
    if evidence.is_file() and evidence.stat().st_mtime_ns > marker_ns:
        s1_paths.append(evidence)

    round_dir = run / 'round-01'
    if (
        stage == 'ROUND_BUDGET_EXHAUSTED'
        and not state.get('error')
        and not evidence.exists()
        and all((round_dir / name).is_file() for name in required)
    ):
        qualified_runs.append(run)

qualified_latest = qualified_runs[-1] if qualified_runs else None
s1_latest = sorted(s1_paths)[-1] if s1_paths else None
print('|'.join((
    str(latest_state or '-'),
    str(latest_run or '-'),
    latest_stage,
    str(blocked_count),
    str(invalid_count),
    str(len(qualified_runs)),
    str(qualified_latest or '-'),
    str(s1_latest or '-'),
)))
PY
    )

    if (( INVALID_STATE_RUNS > 0 )); then
        echo "BLOCKED: unreadable runtime STATE artifacts detected"
        echo "INVALID_STATE_RUNS=$INVALID_STATE_RUNS"
        activation_fail 10
    fi
    if (( BLOCKED_RUNS > 0 )); then
        echo "BLOCKED: v2.0.81 runtime entered BLOCKED state"
        echo "BLOCKED_RUNS=$BLOCKED_RUNS"
        if [[ "$LATEST_STATE" != "-" ]]; then
            python3 -m json.tool "$LATEST_STATE" || true
        fi
        activation_fail 10
    fi

    if [[ "$RUNTIME_STAGE" != "$LAST_RUNTIME_STAGE" ]]; then
        echo "RUNTIME_PROGRESS_STAGE=$RUNTIME_STAGE"
        LAST_RUNTIME_STAGE="$RUNTIME_STAGE"
    fi
    if [[ "$QUALIFIED_EXHAUSTED_RUNS" != \
        "$LAST_QUALIFIED_EXHAUSTED_RUNS" ]]; then
        echo "QUALIFIED_NO_FRONTIER_RUNS=$QUALIFIED_EXHAUSTED_RUNS"
        LAST_QUALIFIED_EXHAUSTED_RUNS="$QUALIFIED_EXHAUSTED_RUNS"
    fi

    if [[ "$S1_EVIDENCE_PATH" != "-" ]]; then
        LATEST_RUN="${S1_EVIDENCE_PATH%/round-01/S1_FINANCIAL_EVIDENCE.json}"
        RUNTIME_BOUNDARY_MODE="POST_S1_EVIDENCE"
        break
    fi

    if (( QUALIFIED_EXHAUSTED_RUNS >= \
        RUNTIME_REQUIRED_EXHAUSTED_RUNS )); then
        LATEST_RUN="$QUALIFIED_EXHAUSTED_LATEST_RUN"
        RUNTIME_BOUNDARY_MODE="NO_LEGAL_FRONTIER_CONTINUITY"
        break
    fi

    if (( $(date -u +%s) >= VERIFY_DEADLINE_EPOCH )); then
        echo "BLOCKED: timed out waiting for post-S1 or no-frontier continuity"
        echo "RUNTIME_VERIFY_TIMEOUT_SECONDS=$RUNTIME_VERIFY_TIMEOUT_SECONDS"
        echo "QUALIFIED_NO_FRONTIER_RUNS=$QUALIFIED_EXHAUSTED_RUNS"
        echo "LATEST_RUN=${LATEST_RUN:-NOT_CREATED}"
        if [[ -n "$LATEST_RUN" ]]; then
            python3 -m json.tool "$LATEST_RUN/STATE.json" || true
            find "$LATEST_RUN/round-01" -maxdepth 1 -type f -print \
                2>/dev/null | sed 's#.*/##' | sort || true
        fi
        activation_fail 11
    fi

    sleep "$RUNTIME_VERIFY_POLL_SECONDS"
done

if [[ "$RUNTIME_BOUNDARY_MODE" == "POST_S1_EVIDENCE" ]]; then
    echo "S1_FINANCIAL_EVIDENCE_READY=$S1_EVIDENCE_PATH"
else
    echo "NO_LEGAL_FRONTIER_CONTINUITY_RUN=$LATEST_RUN"
    echo "POST_S1_BRIDGE_RUNTIME_EXERCISED=false"
fi
if grep -R -F -q -- \
    'v2.0.41 post-S1 precheck compaction cannot preserve headroom:' \
    "$LATEST_RUN"; then
    echo "BLOCKED: legacy v2.0.41 post-S1 headroom failure repeated"
    activation_fail 5
fi
if grep -R -F -q -- \
    'v2.0.80 post-S1 fold counterexample is missing' \
    "$LATEST_RUN"; then
    echo "BLOCKED: v2.0.80 fold-counterexample mismatch repeated"
    activation_fail 6
fi
python3 - "$LATEST_RUN/STATE.json" <<'PY'
import json
import sys

with open(sys.argv[1], encoding='utf-8') as handle:
    state = json.load(handle)
error = str(state.get('error') or '')
assert 'post-S1 precheck compaction cannot preserve headroom' not in error
assert 'post-S1 fold counterexample is missing' not in error
assert state.get('stage') != 'BLOCKED', state
print('V281_RUNTIME_STATE_OK')
PY
if [[ "$RUNTIME_BOUNDARY_MODE" == "POST_S1_EVIDENCE" ]]; then
    echo "V281_RUNTIME_POST_S1_FOLD_COUNTEREXAMPLE_OK"
else
    echo "V281_RUNTIME_NO_LEGAL_FRONTIER_CONTINUITY_OK"
fi
echo "LATEST_RUN=$LATEST_RUN"

systemctl show "$SERVICE" \
    -p MainPID -p ExecMainStatus -p ActiveState -p SubState -p ExecStart \
    --no-pager
journalctl -u "$SERVICE" --since "$START_ISO" --no-pager -o short-iso -n 100 || true

UNIT_UPDATED=false
cleanup
trap - ERR EXIT
if [[ "$BACKUP_CREATED" == "true" ]]; then
    echo "BACKUP_UNIT=$BACKUP"
else
    echo "BACKUP_UNIT=NOT_REQUIRED_ALREADY_BOUND"
fi
echo "TDH_V281_ACTIVATION_COMPLETE"
