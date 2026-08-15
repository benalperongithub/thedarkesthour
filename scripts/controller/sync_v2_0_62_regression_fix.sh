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
TMP_CONTROLLER="$STAGE/.strategy_lab_controller.py.v262-regression-$STAMP"
TMP_TEST="$STAGE/tests/.test_v262_failure_taxonomy.py.v262-regression-$STAMP"

OLD_CONTROLLER_SHA256="e7c0d2d8661915bcf9116550c29fcd59726a6865ad5303595bf4ccadb70a4188"
OLD_TEST_SHA256="044681d7ed1e746144b6606bf6b8ad4fb5d615673d200d37de4851189a575536"
NEW_CONTROLLER_SHA256="c942bda7204ac8fc8da05d00e1f333912fa8f94f7839a6262d80fe7df774de3b"
NEW_TEST_SHA256="0e719b17227c83cf0e0238aebbe0d691e9aa5b66b980962eb78a3310149259a7"

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

echo "===== 2. VERIFY EXACT FAILED-REGRESSION STAGING ====="
echo "$OLD_CONTROLLER_SHA256  $STAGE/strategy_lab_controller.py" | sha256sum -c -
echo "$OLD_TEST_SHA256  $STAGE/tests/test_v262_failure_taxonomy.py" | sha256sum -c -

echo "===== 3. VERIFY CORRECTED REPOSITORY SOURCES ====="
test "$(git -C "$REPO" branch --show-current)" = "main"
test ! -L "$SOURCE/strategy_lab_controller.py"
test ! -L "$SOURCE/tests/test_v262_failure_taxonomy.py"
echo "$NEW_CONTROLLER_SHA256  $SOURCE/strategy_lab_controller.py" | sha256sum -c -
echo "$NEW_TEST_SHA256  $SOURCE/tests/test_v262_failure_taxonomy.py" | sha256sum -c -

echo "===== 4. PREPARE AND APPLY ATOMIC COMPATIBILITY FIX ====="
install -T -m 0755 -- "$SOURCE/strategy_lab_controller.py" "$TMP_CONTROLLER"
install -T -m 0644 -- "$SOURCE/tests/test_v262_failure_taxonomy.py" "$TMP_TEST"
echo "$NEW_CONTROLLER_SHA256  $TMP_CONTROLLER" | sha256sum -c -
echo "$NEW_TEST_SHA256  $TMP_TEST" | sha256sum -c -
"$PYTHON" -m py_compile "$TMP_CONTROLLER" "$TMP_TEST"

mv -fT -- "$TMP_CONTROLLER" "$STAGE/strategy_lab_controller.py"
mv -fT -- "$TMP_TEST" "$STAGE/tests/test_v262_failure_taxonomy.py"

echo "===== 5. VERIFY CORRECTED UNSEALED STAGING ====="
echo "$NEW_CONTROLLER_SHA256  $STAGE/strategy_lab_controller.py" | sha256sum -c -
echo "$NEW_TEST_SHA256  $STAGE/tests/test_v262_failure_taxonomy.py" | sha256sum -c -
/usr/bin/python3 "$STAGE/tests/test_v262_failure_taxonomy.py"

echo "SERVICE_STATE=$(systemctl is-active "$SERVICE" || true)"
echo "TDH_V262_REGRESSION_FIX_SYNC_COMPLETE"
