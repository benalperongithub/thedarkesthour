#!/usr/bin/env bash
set -Eeuo pipefail

SERVICE="strategy-lab-supervisor-v2.1.service"
BASE="/srv/tdh-collab/controller/strategy-lab-v2"
STAGE="$BASE/staging/v2.0.55"
REPO="/home/tdw/the-darkest-hour"
REPO_SOURCE="$REPO/controller/staging/v2.0.55"

OLD_CONTROLLER_SHA256="a46c9d25402057c9240866cbbc139ac6bb80978b10df968a9812aacd6f580296"
OLD_TEST_SHA256="2d892819016fda422be938dc8564f35ed35bc5a522818229e3ccc52430392b73"
NEW_CONTROLLER_SHA256="25a1554ffda30d27db877030fd3c02496d3f74665f0e0b51cd20d1145f9b53aa"
NEW_TEST_SHA256="e9d0bfa9be1ea992a9c1172f03c03f0c6f9c9256ef659975cf348614e396a45c"

CONTROLLER="$STAGE/strategy_lab_controller.py"
TEST="$STAGE/tests/test_v255_scout_cache_continuity.py"
SOURCE_CONTROLLER="$REPO_SOURCE/strategy_lab_controller.py"
SOURCE_TEST="$REPO_SOURCE/tests/test_v255_scout_cache_continuity.py"

echo "===== 1. VERIFY STOPPED UNSEALED STAGING ====="
test "$(systemctl is-active "$SERVICE" || true)" != "active"
test -d "$STAGE"
test ! -e "$STAGE/SHA256SUMS"
test "$(git -C "$REPO" branch --show-current)" = "main"

echo "===== 2. VERIFY CORRECTED REPOSITORY SOURCES ====="
echo "$NEW_CONTROLLER_SHA256  $SOURCE_CONTROLLER" | sha256sum -c -
echo "$NEW_TEST_SHA256  $SOURCE_TEST" | sha256sum -c -

CURRENT_CONTROLLER_SHA256="$(sha256sum "$CONTROLLER" | awk '{print $1}')"
CURRENT_TEST_SHA256="$(sha256sum "$TEST" | awk '{print $1}')"

if [[ 
    "$CURRENT_CONTROLLER_SHA256" == "$NEW_CONTROLLER_SHA256" &&
    "$CURRENT_TEST_SHA256" == "$NEW_TEST_SHA256"
]]; then
    echo "STAGING_ALREADY_CORRECTED"
elif [[
    "$CURRENT_CONTROLLER_SHA256" == "$OLD_CONTROLLER_SHA256" &&
    "$CURRENT_TEST_SHA256" == "$OLD_TEST_SHA256"
]]; then
    echo "===== 3. ATOMICALLY APPLY BOUNDED REGRESSION FIX ====="
    install -m 0755 "$SOURCE_CONTROLLER" "$CONTROLLER.new"
    install -m 0644 "$SOURCE_TEST" "$TEST.new"
    mv -f -- "$CONTROLLER.new" "$CONTROLLER"
    mv -f -- "$TEST.new" "$TEST"
else
    echo "BLOCKED: unexpected current staging hashes"
    echo "CURRENT_CONTROLLER_SHA256=$CURRENT_CONTROLLER_SHA256"
    echo "CURRENT_TEST_SHA256=$CURRENT_TEST_SHA256"
    exit 2
fi

echo "===== 4. VERIFY CORRECTED STAGING ====="
echo "$NEW_CONTROLLER_SHA256  $CONTROLLER" | sha256sum -c -
echo "$NEW_TEST_SHA256  $TEST" | sha256sum -c -
python3 -m py_compile "$CONTROLLER" "$TEST"

echo "SERVICE_STATE=$(systemctl is-active "$SERVICE" || true)"
echo "TDH_V255_REGRESSION_FIX_SYNC_COMPLETE"
