#!/usr/bin/env bash
set -Eeuo pipefail

SERVICE="strategy-lab-supervisor-v2.1.service"
BASE="/srv/tdh-collab/controller/strategy-lab-v2"
STAGE="$BASE/staging/v2.0.63"
RELEASE="$BASE/v2.0.63"
REPO="/home/tdw/the-darkest-hour"
SOURCE="$REPO/controller/staging/v2.0.63/strategy_lab_controller.py"
TEST="$STAGE/tests/test_v263_checkpoint_resume.py"
PYTHON="/srv/tdh-research/phoenix-venv/bin/python"
TMP="$STAGE/.strategy_lab_controller.py.v263-source-contract-$$"

OLD_CONTROLLER_SHA256="54f97b53c69545386c68a36b3de2b036a95b7491053dd43356b984ff9c2a3b1a"
NEW_CONTROLLER_SHA256="8e60c12a724dc2c8d9a946e22af8c9144f0e2e8117f1030404134dd8d93cd73d"
TEST_SHA256="907168a5afcade5d5b6137ef7f3e97e1e122033f457a39a10bb27aeb38f897de"

cleanup() {
    rm -f -- "$TMP"
}
trap cleanup EXIT

echo "===== 1. KEEP UNSEALED v2.0.63 STOPPED ====="
systemctl mask --runtime --now "$SERVICE" || true
sleep 1
test "$(systemctl is-active "$SERVICE" || true)" != "active"
test -d "$STAGE"
test ! -e "$RELEASE"
test ! -e "$STAGE/SHA256SUMS"

echo "===== 2. VERIFY EXACT CURRENT STAGING ====="
echo "$OLD_CONTROLLER_SHA256  $STAGE/strategy_lab_controller.py" | sha256sum -c -
echo "$TEST_SHA256  $TEST" | sha256sum -c -

echo "===== 3. VERIFY CORRECTED REPOSITORY SOURCE ====="
test "$(git -C "$REPO" branch --show-current)" = "main"
test ! -L "$SOURCE"
echo "$NEW_CONTROLLER_SHA256  $SOURCE" | sha256sum -c -
grep -qF "No trading path, paper path or exchange permission is added or weakened." "$SOURCE"

echo "===== 4. APPLY ATOMIC SOURCE-CONTRACT FIX ====="
install -T -m 0755 -- "$SOURCE" "$TMP"
echo "$NEW_CONTROLLER_SHA256  $TMP" | sha256sum -c -
"$PYTHON" -m py_compile "$TMP"
mv -fT -- "$TMP" "$STAGE/strategy_lab_controller.py"

echo "===== 5. VERIFY CORRECTED STAGING ====="
echo "$NEW_CONTROLLER_SHA256  $STAGE/strategy_lab_controller.py" | sha256sum -c -
/usr/bin/python3 "$TEST"

echo "SERVICE_STATE=$(systemctl is-active "$SERVICE" || true)"
echo "TDH_V263_SOURCE_CONTRACT_FIX_SYNC_COMPLETE"
