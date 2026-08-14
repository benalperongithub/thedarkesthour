#!/usr/bin/env bash
set -Eeuo pipefail

SERVICE="strategy-lab-supervisor-v2.1.service"
BASE="/srv/tdh-collab/controller/strategy-lab-v2"
STAGE="$BASE/staging/v2.0.60"
REPO="/home/tdw/the-darkest-hour"
SOURCE="$REPO/controller/staging/v2.0.60"

OLD_CONTROLLER_SHA256="eb7cea802f3b703e5b5c8b2aaf3ec21d8273575814eb10a6b92c057028e02c12"
OLD_TEST_SHA256="b35bee4ef841d6843d0ddc60dcd0e876bb6d3d0a7cf490992c70857d250b2ced"
NEW_CONTROLLER_SHA256="6d3c6f2b9d0b40697002c72e26de175551123a05d808522b6ab40cb73a9bacca"
NEW_TEST_SHA256="642d77febb6c6163f13f7f8f3f6374621adb738dc2e6e212b098b256fdda62fa"

TMP_CONTROLLER="$STAGE/.strategy_lab_controller.py.v260-symbol-fence.$$"
TMP_TEST="$STAGE/tests/.test_v260_registered_seed_transition.py.v260-symbol-fence.$$"

cleanup() {
    rm -f -- "$TMP_CONTROLLER" "$TMP_TEST"
}
trap cleanup EXIT

echo "===== 1. VERIFY STOPPED UNSEALED v2.0.60 ====="
systemctl mask --runtime --now "$SERVICE" || true
sleep 1
test "$(systemctl is-active "$SERVICE" || true)" != "active"
test -d "$STAGE"
test ! -e "$STAGE/SHA256SUMS"

echo "$OLD_CONTROLLER_SHA256  $STAGE/strategy_lab_controller.py" | sha256sum -c -
echo "$OLD_TEST_SHA256  $STAGE/tests/test_v260_registered_seed_transition.py" | sha256sum -c -

echo "===== 2. VERIFY CORRECTED REPOSITORY SOURCES ====="
test "$(git -C "$REPO" branch --show-current)" = "main"
echo "$NEW_CONTROLLER_SHA256  $SOURCE/strategy_lab_controller.py" | sha256sum -c -
echo "$NEW_TEST_SHA256  $SOURCE/tests/test_v260_registered_seed_transition.py" | sha256sum -c -

echo "===== 3. APPLY ATOMIC SYMBOL-FENCE REGRESSION FIX ====="
install -T -m 0755 -- "$SOURCE/strategy_lab_controller.py" "$TMP_CONTROLLER"
install -T -m 0644 -- \
    "$SOURCE/tests/test_v260_registered_seed_transition.py" "$TMP_TEST"

echo "$NEW_CONTROLLER_SHA256  $TMP_CONTROLLER" | sha256sum -c -
echo "$NEW_TEST_SHA256  $TMP_TEST" | sha256sum -c -
python3 -m py_compile "$TMP_CONTROLLER" "$TMP_TEST"

mv -fT -- "$TMP_CONTROLLER" "$STAGE/strategy_lab_controller.py"
mv -fT -- "$TMP_TEST" "$STAGE/tests/test_v260_registered_seed_transition.py"

echo "===== 4. VERIFY CORRECTED STAGING ====="
echo "$NEW_CONTROLLER_SHA256  $STAGE/strategy_lab_controller.py" | sha256sum -c -
echo "$NEW_TEST_SHA256  $STAGE/tests/test_v260_registered_seed_transition.py" | sha256sum -c -
test ! -e "$STAGE/SHA256SUMS"

echo "SERVICE_STATE=$(systemctl is-active "$SERVICE" || true)"
echo "TDH_V260_SYMBOL_FENCE_FIX_SYNC_COMPLETE"
