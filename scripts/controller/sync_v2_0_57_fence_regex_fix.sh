#!/usr/bin/env bash
set -Eeuo pipefail

SERVICE="strategy-lab-supervisor-v2.1.service"
BASE="/srv/tdh-collab/controller/strategy-lab-v2"
STAGE="$BASE/staging/v2.0.57"
REPO="/home/tdw/the-darkest-hour"
SOURCE="$REPO/controller/staging/v2.0.57/strategy_lab_controller.py"
TARGET="$STAGE/strategy_lab_controller.py"
OLD_SHA256="1127c5e508afe2e4279a11258bc49d0300dc38d11a244c2faf2d316d4462f45e"
NEW_SHA256="1d16142e6d5ee37ee190dbb7b7e9c0c216e6c78bff9fe8a41d4a011a860f92ff"
TMP="$TARGET.new.$$"

cleanup() {
    if [[ -e "$TMP" && "$TMP" == "$STAGE/strategy_lab_controller.py.new."* ]]; then
        rm -f -- "$TMP"
    fi
}
trap cleanup EXIT

echo "===== 1. VERIFY STOPPED UNSEALED v2.0.57 ====="
test "$(systemctl is-active "$SERVICE" || true)" != "active"
test -d "$STAGE"
test ! -e "$STAGE/SHA256SUMS"
test "$(git -C "$REPO" branch --show-current)" = "main"

echo "===== 2. VERIFY REPOSITORY SOURCE ====="
echo "$NEW_SHA256  $SOURCE" | sha256sum -c -
python3 -m py_compile "$SOURCE"

CURRENT_SHA256="$(sha256sum "$TARGET" | awk '{print $1}')"

if [[ "$CURRENT_SHA256" == "$NEW_SHA256" ]]; then
    echo "STAGING_ALREADY_CORRECTED"
elif [[ "$CURRENT_SHA256" == "$OLD_SHA256" ]]; then
    echo "===== 3. ATOMICALLY APPLY BOUNDED REGEX FIX ====="
    install -m 0755 "$SOURCE" "$TMP"
    echo "$NEW_SHA256  $TMP" | sha256sum -c -
    mv -f -- "$TMP" "$TARGET"
else
    echo "BLOCKED: unexpected current staging controller hash"
    echo "CURRENT_SHA256=$CURRENT_SHA256"
    exit 2
fi

echo "===== 4. VERIFY CORRECTED STAGING ====="
echo "$NEW_SHA256  $TARGET" | sha256sum -c -
python3 -m py_compile "$TARGET" "$STAGE/tests/test_v257_scout_response_conformance.py"

echo "SERVICE_STATE=$(systemctl is-active "$SERVICE" || true)"
echo "TDH_V257_FENCE_REGEX_FIX_SYNC_COMPLETE"
