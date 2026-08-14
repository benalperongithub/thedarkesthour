#!/usr/bin/env bash
set -Eeuo pipefail

SERVICE="strategy-lab-supervisor-v2.1.service"
UNIT="/etc/systemd/system/$SERVICE"
BASE="/srv/tdh-collab/controller/strategy-lab-v2"
OLD_VERSION="v2.0.54"
NEW_VERSION="v2.0.55"
NEW_RELEASE="$BASE/$NEW_VERSION"
GATE="/usr/local/sbin/tdh-lab-admin-gate"
STAMP="$(date -u +%Y%m%dT%H%M%SZ)"
START_ISO="$(date -u '+%Y-%m-%d %H:%M:%S UTC')"
BACKUP="${UNIT}.bak-${OLD_VERSION}-to-${NEW_VERSION}-${STAMP}"
VERIFY_UNIT="/tmp/strategy-lab-supervisor-v2.1-v255-verify-${STAMP}.service"
UNIT_UPDATED=false
ACTIVATION_MODE=""
BACKUP_CREATED=false

cleanup() {
    rm -f -- "$VERIFY_UNIT"
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

trap cleanup EXIT
trap rollback_on_error ERR

echo "===== 1. KEEP OLD RUNTIME STOPPED ====="
systemctl mask --runtime --now "$SERVICE" || true
sleep 1

if [[ "$(systemctl is-active "$SERVICE" || true)" == "active" ]]; then
    echo "BLOCKED: supervisor is still active"
    exit 2
fi

echo "===== 2. VERIFY SEALED v2.0.55 ====="
test -d "$NEW_RELEASE"
test -f "$NEW_RELEASE/SHA256SUMS"
(
    cd "$NEW_RELEASE"
    sha256sum -c SHA256SUMS >/dev/null
)

"$GATE" preflight "$NEW_VERSION" >/tmp/tdh-v2.0.55-activation-preflight.log
grep -q '"status": "PREFLIGHT_OK"' /tmp/tdh-v2.0.55-activation-preflight.log

python3 - "$NEW_RELEASE/config.json" <<'PY'
import json
import sys

with open(sys.argv[1], encoding="utf-8") as handle:
    cfg = json.load(handle)

assert cfg.get("research_mode") == "offline"
assert cfg.get("trading_actions") is False
assert cfg.get("exchange_api_access") is False
print("OFFLINE_SAFETY_FLAGS_OK")
PY

echo "===== 3. BUILD AND VERIFY UPDATED SYSTEMD UNIT ====="
test -f "$UNIT"

read -r OLD_COUNT NEW_COUNT < <(
    python3 - "$UNIT" "$OLD_VERSION" "$NEW_VERSION" <<'PY'
from pathlib import Path
import sys

text = Path(sys.argv[1]).read_text(encoding="utf-8")
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

text = source.read_text(encoding="utf-8")
if text.count(old_version) != 5 or new_version in text:
    raise SystemExit("BLOCKED: unit replacement precondition failed")

updated = text.replace(old_version, new_version)
if updated.count(new_version) != 5 or old_version in updated:
    raise SystemExit("BLOCKED: unit replacement postcondition failed")

destination.write_text(updated, encoding="utf-8")
PY
else
    cp -a -- "$UNIT" "$VERIFY_UNIT"
    echo "UNIT_ALREADY_BOUND_TO=$NEW_VERSION"
fi

systemd-analyze verify "$VERIFY_UNIT"
grep -nF "$NEW_VERSION" "$VERIFY_UNIT"

echo "===== 4. INSTALL UNIT AND START v2.0.55 ====="
if [[ "$ACTIVATION_MODE" == "UPDATE_FROM_OLD" ]]; then
    install -o root -g root -m 0644 "$VERIFY_UNIT" "$UNIT"
    UNIT_UPDATED=true
else
    cmp -s -- "$VERIFY_UNIT" "$UNIT"
fi
systemctl daemon-reload
systemctl unmask --runtime "$SERVICE"
systemctl reset-failed "$SERVICE" || true
systemctl start "$SERVICE"
sleep 5

test "$(systemctl is-active "$SERVICE")" = "active"

MAIN_PID="$(systemctl show "$SERVICE" -p MainPID --value)"
if [[ ! "$MAIN_PID" =~ ^[1-9][0-9]*$ ]]; then
    echo "BLOCKED: invalid MainPID: $MAIN_PID"
    exit 4
fi

CMDLINE="$(tr '\0' ' ' <"/proc/$MAIN_PID/cmdline")"
[[ "$CMDLINE" == *"$NEW_RELEASE/strategy_lab_controller.py"* ]] || {
    echo "BLOCKED: runtime command is not bound to v2.0.55"
    echo "CMDLINE=$CMDLINE"
    exit 5
}

echo "MAIN_PID=$MAIN_PID"
echo "CMDLINE=$CMDLINE"

echo "===== 5. VERIFY RUNTIME SURVIVES BOOTSTRAP ====="
sleep 25
test "$(systemctl is-active "$SERVICE")" = "active"

MAIN_PID_AFTER="$(systemctl show "$SERVICE" -p MainPID --value)"
if [[ ! "$MAIN_PID_AFTER" =~ ^[1-9][0-9]*$ ]]; then
    echo "BLOCKED: invalid post-bootstrap MainPID: $MAIN_PID_AFTER"
    exit 6
fi

CMDLINE_AFTER="$(tr '\0' ' ' <"/proc/$MAIN_PID_AFTER/cmdline")"
[[ "$CMDLINE_AFTER" == *"$NEW_RELEASE/strategy_lab_controller.py"* ]] || {
    echo "BLOCKED: post-bootstrap runtime is not bound to v2.0.55"
    echo "CMDLINE=$CMDLINE_AFTER"
    exit 7
}

systemctl show "$SERVICE" \
    -p MainPID \
    -p ExecMainStatus \
    -p ActiveState \
    -p SubState \
    -p ExecStart \
    --no-pager

journalctl -u "$SERVICE" --since "$START_ISO" --no-pager -o short-iso -n 80 || true

UNIT_UPDATED=false
cleanup
trap - ERR EXIT

if [[ "$BACKUP_CREATED" == "true" ]]; then
    echo "BACKUP_UNIT=$BACKUP"
else
    echo "BACKUP_UNIT=NOT_REQUIRED_ALREADY_BOUND"
fi
echo "TDH_V255_ACTIVATION_COMPLETE"
