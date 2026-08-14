#!/usr/bin/env bash
set -Eeuo pipefail

SERVICE="strategy-lab-supervisor-v2.1.service"
UNIT="/etc/systemd/system/strategy-lab-supervisor-v2.1.service"
BASE="/srv/tdh-collab/controller/strategy-lab-v2"
OLD_VERSION="v2.0.51"
NEW_VERSION="v2.0.52"
NEW_RELEASE="$BASE/$NEW_VERSION"
GATE="/usr/local/sbin/tdh-lab-admin-gate"
STAMP="$(date -u +%Y%m%dT%H%M%SZ)"
BACKUP="${UNIT}.bak-${OLD_VERSION}-to-${NEW_VERSION}-${STAMP}"

fail_closed() {
    systemctl mask --runtime --now "$SERVICE" >/dev/null 2>&1 || true
    echo "ACTIVATION_FAILED_FAIL_CLOSED"
    echo "UNIT_BACKUP=$BACKUP"
}
trap fail_closed ERR

echo "===== 1. VERIFY SEALED v2.0.52 ====="
test -d "$NEW_RELEASE"
test -f "$NEW_RELEASE/SHA256SUMS"
(
    cd "$NEW_RELEASE"
    sha256sum -c SHA256SUMS >/dev/null
)
"$GATE" preflight "$NEW_VERSION" >/tmp/tdh-v2.0.52-activation-preflight.log
grep -q '"status": "PREFLIGHT_OK"' /tmp/tdh-v2.0.52-activation-preflight.log

echo "===== 2. BACK UP SYSTEMD UNIT ====="
systemctl mask --runtime --now "$SERVICE" || true
cp -a "$UNIT" "$BACKUP"
echo "UNIT_BACKUP=$BACKUP"

echo "===== 3. UPDATE UNIT TO v2.0.52 ====="
python3 - "$UNIT" "$OLD_VERSION" "$NEW_VERSION" <<'PY'
from pathlib import Path
import sys

unit = Path(sys.argv[1])
old = sys.argv[2]
new = sys.argv[3]
source = unit.read_text(encoding="utf-8")
old_count = source.count(old)
new_count = source.count(new)

if old_count < 4:
    raise SystemExit(
        f"BLOCKED: expected at least 4 references to {old}, found {old_count}"
    )
if new_count:
    raise SystemExit(
        f"BLOCKED: partial {new} references already present: {new_count}"
    )

updated = source.replace(old, new)
if old in updated:
    raise SystemExit("BLOCKED: old version reference remains")

unit.write_text(updated, encoding="utf-8")
print(f"UNIT_VERSION_REFERENCES_UPDATED={old_count}")
PY

grep -nE 'Description=|ConditionPathExists=|WorkingDirectory=|ExecStartPre=|ExecStart=' "$UNIT"

echo "===== 4. ACTIVATE v2.0.52 ====="
systemctl daemon-reload
systemctl unmask --runtime "$SERVICE"
systemctl restart "$SERVICE"
sleep 5

echo "===== 5. VERIFY RUNNING PROCESS ====="
test "$(systemctl is-active "$SERVICE")" = "active"

MAIN_PID="$(systemctl show "$SERVICE" -p MainPID --value)"
[[ "$MAIN_PID" =~ ^[1-9][0-9]*$ ]]
[[ "$MAIN_PID" -gt 1 ]]
test -r "/proc/$MAIN_PID/cmdline"

CMDLINE="$(tr '\0' ' ' <"/proc/$MAIN_PID/cmdline")"
grep -Fq "/v2.0.52/strategy_lab_controller.py" <<<"$CMDLINE"

systemctl show "$SERVICE" \
    -p MainPID \
    -p ExecMainStatus \
    -p ActiveState \
    -p SubState \
    --no-pager

echo "PROCESS_CMDLINE=$CMDLINE"

echo "===== 6. RECENT RUNTIME LOG ====="
journalctl \
    -u "$SERVICE" \
    --since "2 minutes ago" \
    --no-pager \
    -n 100 \
    -o short-iso

trap - ERR
echo "TDH_V252_ACTIVATION_COMPLETE"
