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

echo "===== 5. VERIFY RUNTIME CROSSES POST-S1 HEADROOM BOUNDARY ====="
VERIFY_DEADLINE_EPOCH="$((
    $(date -u +%s) + RUNTIME_VERIFY_TIMEOUT_SECONDS
))"
LATEST_RUN=""
LATEST_STATE=""
S1_EVIDENCE_PATH=""
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

    LATEST_STATE="$(find "$BASE/runs" -mindepth 2 -maxdepth 2 \
        -type f -name 'STATE.json' -newer "$RUN_MARKER" -print \
        | sort | tail -n 1)"

    if [[ -n "$LATEST_STATE" ]]; then
        LATEST_RUN="${LATEST_STATE%/STATE.json}"
        if ! RUNTIME_STAGE="$(python3 - "$LATEST_STATE" <<'PY'
import json
import sys

with open(sys.argv[1], encoding='utf-8') as handle:
    state = json.load(handle)
print(str(state.get('stage') or 'UNKNOWN'))
PY
)"; then
            RUNTIME_STAGE="STATE_UNREADABLE"
        fi

        if [[ "$RUNTIME_STAGE" != "$LAST_RUNTIME_STAGE" ]]; then
            echo "RUNTIME_PROGRESS_STAGE=$RUNTIME_STAGE"
            LAST_RUNTIME_STAGE="$RUNTIME_STAGE"
        fi

        if [[ "$RUNTIME_STAGE" == "BLOCKED" ]]; then
            echo "BLOCKED: v2.0.81 runtime entered BLOCKED state"
            python3 -m json.tool "$LATEST_STATE" || true
            activation_fail 10
        fi
    fi

    S1_EVIDENCE_PATH="$(find "$BASE/runs" -mindepth 3 -maxdepth 3 \
        -type f -path '*/round-01/S1_FINANCIAL_EVIDENCE.json' \
        -newer "$RUN_MARKER" -print | sort | tail -n 1)"
    if [[ -n "$S1_EVIDENCE_PATH" ]]; then
        LATEST_RUN="${S1_EVIDENCE_PATH%/round-01/S1_FINANCIAL_EVIDENCE.json}"
        break
    fi

    if (( $(date -u +%s) >= VERIFY_DEADLINE_EPOCH )); then
        echo "BLOCKED: timed out waiting for v2.0.81 S1 financial evidence"
        echo "RUNTIME_VERIFY_TIMEOUT_SECONDS=$RUNTIME_VERIFY_TIMEOUT_SECONDS"
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

echo "S1_FINANCIAL_EVIDENCE_READY=$S1_EVIDENCE_PATH"
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
print('V281_RUNTIME_POST_S1_FOLD_COUNTEREXAMPLE_OK')
PY
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
