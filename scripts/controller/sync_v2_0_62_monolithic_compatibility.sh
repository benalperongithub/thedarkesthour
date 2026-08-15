#!/usr/bin/env bash
set -Eeuo pipefail

SERVICE="strategy-lab-supervisor-v2.1.service"
BASE="/srv/tdh-collab/controller/strategy-lab-v2"
STAGE="$BASE/staging/v2.0.62"
RELEASE="$BASE/v2.0.62"
REPO="/home/tdw/the-darkest-hour"
SOURCE="$REPO/controller/staging/v2.0.62"
PYTHON="/srv/tdh-research/phoenix-venv/bin/python"
STAMP="$$"
TMP_CONTROLLER="$STAGE/.strategy_lab_controller.py.v262-monolithic-$STAMP"
TMP_TEST="$STAGE/tests/.test_v262_failure_taxonomy.py.v262-monolithic-$STAMP"

OLD_CONTROLLER_SHA256="c942bda7204ac8fc8da05d00e1f333912fa8f94f7839a6262d80fe7df774de3b"
OLD_TEST_SHA256="c2e55882035ec146556254e09dda11aef1a51b40c115d6dfe4e77eac503c905d"
NEW_CONTROLLER_SHA256="ea404aca971d72571e577a099d20ca307b5c0977ca1279cadc107844f155a4ab"
NEW_TEST_SHA256="ae6d064f8c5919365c68dccd9f40daa99c6d93f1f395334bdb33f7b9c05e12cc"

cleanup() {
    rm -f -- "$TMP_CONTROLLER" "$TMP_TEST"
}
trap cleanup EXIT

echo "===== 1. KEEP UNSEALED v2.0.62 STOPPED ====="
systemctl mask --runtime --now "$SERVICE" || true
sleep 1
test "$(systemctl is-active "$SERVICE" || true)" != "active"
test -d "$STAGE"
test ! -e "$RELEASE"
test ! -e "$STAGE/SHA256SUMS"

echo "===== 2. VERIFY EXACT CURRENT STAGING ====="
echo "$OLD_CONTROLLER_SHA256  $STAGE/strategy_lab_controller.py" | sha256sum -c -
echo "$OLD_TEST_SHA256  $STAGE/tests/test_v262_failure_taxonomy.py" | sha256sum -c -

echo "===== 3. VERIFY MONOLITHIC REPOSITORY SOURCES ====="
test "$(git -C "$REPO" branch --show-current)" = "main"
test ! -L "$SOURCE/strategy_lab_controller.py"
test ! -L "$SOURCE/tests/test_v262_failure_taxonomy.py"
echo "$NEW_CONTROLLER_SHA256  $SOURCE/strategy_lab_controller.py" | sha256sum -c -
echo "$NEW_TEST_SHA256  $SOURCE/tests/test_v262_failure_taxonomy.py" | sha256sum -c -

echo "===== 4. APPLY ATOMIC MONOLITHIC COMPATIBILITY FIX ====="
install -T -m 0755 -- "$SOURCE/strategy_lab_controller.py" "$TMP_CONTROLLER"
install -T -m 0644 -- "$SOURCE/tests/test_v262_failure_taxonomy.py" "$TMP_TEST"
echo "$NEW_CONTROLLER_SHA256  $TMP_CONTROLLER" | sha256sum -c -
echo "$NEW_TEST_SHA256  $TMP_TEST" | sha256sum -c -
"$PYTHON" -m py_compile "$TMP_CONTROLLER" "$TMP_TEST"
mv -fT -- "$TMP_CONTROLLER" "$STAGE/strategy_lab_controller.py"
mv -fT -- "$TMP_TEST" "$STAGE/tests/test_v262_failure_taxonomy.py"

echo "===== 5. VERIFY V2.0.62 FEATURE TESTS ====="
echo "$NEW_CONTROLLER_SHA256  $STAGE/strategy_lab_controller.py" | sha256sum -c -
echo "$NEW_TEST_SHA256  $STAGE/tests/test_v262_failure_taxonomy.py" | sha256sum -c -
/usr/bin/python3 "$STAGE/tests/test_v262_failure_taxonomy.py"

echo "SERVICE_STATE=$(systemctl is-active "$SERVICE" || true)"
echo "TDH_V262_MONOLITHIC_COMPATIBILITY_SYNC_COMPLETE"
