#!/usr/bin/env bash
set -Eeuo pipefail

SERVICE="strategy-lab-supervisor-v2.1.service"
BASE="/srv/tdh-collab/controller/strategy-lab-v2"
STAGE="$BASE/staging/v2.0.62"
RELEASE="$BASE/v2.0.62"
REPO="/home/tdw/the-darkest-hour"
SOURCE="$REPO/controller/staging/v2.0.62/tests/test_v262_failure_taxonomy.py"
PYTHON="/srv/tdh-research/phoenix-venv/bin/python"
TMP="$STAGE/tests/.test_v262_failure_taxonomy.py.v262-semantic-$$"

CONTROLLER_SHA256="c942bda7204ac8fc8da05d00e1f333912fa8f94f7839a6262d80fe7df774de3b"
OLD_TEST_SHA256="0e719b17227c83cf0e0238aebbe0d691e9aa5b66b980962eb78a3310149259a7"
NEW_TEST_SHA256="c2e55882035ec146556254e09dda11aef1a51b40c115d6dfe4e77eac503c905d"

cleanup() {
    rm -f -- "$TMP"
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
echo "$CONTROLLER_SHA256  $STAGE/strategy_lab_controller.py" | sha256sum -c -
echo "$OLD_TEST_SHA256  $STAGE/tests/test_v262_failure_taxonomy.py" | sha256sum -c -

echo "===== 3. VERIFY SEMANTIC TEST SOURCE ====="
test "$(git -C "$REPO" branch --show-current)" = "main"
test ! -L "$SOURCE"
echo "$NEW_TEST_SHA256  $SOURCE" | sha256sum -c -

echo "===== 4. APPLY TEST-ONLY ATOMIC FIX ====="
install -T -m 0644 -- "$SOURCE" "$TMP"
echo "$NEW_TEST_SHA256  $TMP" | sha256sum -c -
"$PYTHON" -m py_compile "$TMP"
mv -fT -- "$TMP" "$STAGE/tests/test_v262_failure_taxonomy.py"

echo "===== 5. VERIFY SEMANTIC RERAISE TEST ====="
echo "$NEW_TEST_SHA256  $STAGE/tests/test_v262_failure_taxonomy.py" | sha256sum -c -
/usr/bin/python3 "$STAGE/tests/test_v262_failure_taxonomy.py"

echo "SERVICE_STATE=$(systemctl is-active "$SERVICE" || true)"
echo "TDH_V262_SEMANTIC_TEST_FIX_SYNC_COMPLETE"
