#!/usr/bin/env bash
set -Eeuo pipefail

SERVICE="strategy-lab-supervisor-v2.1.service"
BASE="/srv/tdh-collab/controller/strategy-lab-v2"
STAGING="$BASE/staging/v2.0.64"
RELEASE="$BASE/v2.0.64"
REPO="/home/tdw/the-darkest-hour"
SOURCE="$REPO/controller/staging/v2.0.64/tests/test_v263_checkpoint_resume.py"
TARGET="$STAGING/tests/test_v263_checkpoint_resume.py"
TMP="$STAGING/tests/.test_v263_checkpoint_resume.py.v264-compat-$$"

EXPECTED_CONTROLLER_SHA256="7d4e569eb9b22c12ced572a3d68b1d8315a732157cfbe9f6f47c22635eb19051"
EXPECTED_V264_TEST_SHA256="4ae499ac103cf2f936bc3617a121b339def273644c8f349d64c04c32a4c147f3"
EXPECTED_STALE_V263_TEST_SHA256="907168a5afcade5d5b6137ef7f3e97e1e122033f457a39a10bb27aeb38f897de"
EXPECTED_FIXED_V263_TEST_SHA256="50df69141239a9c6f063a41a4a3b16e0e13b0e5f1bf3cd093d396b6d5b1543b4"

cleanup() {
    if [[ -f "$TMP" && "$TMP" == "$STAGING/tests/.test_v263_checkpoint_resume.py.v264-compat-"* ]]; then
        rm -f -- "$TMP"
    fi
}
trap cleanup EXIT

echo "===== 1. KEEP UNSEALED v2.0.64 STOPPED ====="
systemctl mask --runtime --now "$SERVICE" || true
sleep 1
test "$(systemctl is-active "$SERVICE" || true)" != "active"
test ! -e "$RELEASE"
test -d "$STAGING"
test ! -e "$STAGING/SHA256SUMS"

echo "===== 2. VERIFY EXACT CURRENT STAGING ====="
test ! -L "$STAGING/strategy_lab_controller.py"
test ! -L "$STAGING/tests/test_v264_checkpoint_startup.py"
test ! -L "$TARGET"
echo "$EXPECTED_CONTROLLER_SHA256  $STAGING/strategy_lab_controller.py" | sha256sum -c -
echo "$EXPECTED_V264_TEST_SHA256  $STAGING/tests/test_v264_checkpoint_startup.py" | sha256sum -c -
echo "$EXPECTED_STALE_V263_TEST_SHA256  $TARGET" | sha256sum -c -

echo "===== 3. VERIFY CORRECTED REPOSITORY FIXTURE ====="
test "$(git -C "$REPO" branch --show-current)" = "main"
test -f "$SOURCE"
test ! -L "$SOURCE"
echo "$EXPECTED_FIXED_V263_TEST_SHA256  $SOURCE" | sha256sum -c -

echo "===== 4. APPLY ATOMIC TEST-FIXTURE COMPATIBILITY FIX ====="
install -T -m 0644 -- "$SOURCE" "$TMP"
echo "$EXPECTED_FIXED_V263_TEST_SHA256  $TMP" | sha256sum -c -
mv -fT -- "$TMP" "$TARGET"

echo "===== 5. VERIFY CORRECTED v2.0.64 TESTS ====="
echo "$EXPECTED_FIXED_V263_TEST_SHA256  $TARGET" | sha256sum -c -
/usr/bin/python3 "$TARGET"
/usr/bin/python3 "$STAGING/tests/test_v264_checkpoint_startup.py"

echo "SERVICE_STATE=$(systemctl is-active "$SERVICE" || true)"
echo "TDH_V264_LEGACY_FIXTURE_SYNC_COMPLETE"
