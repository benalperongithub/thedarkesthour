#!/usr/bin/env bash
set -Eeuo pipefail

SERVICE="strategy-lab-supervisor-v2.1.service"
BASE="/srv/tdh-collab/controller/strategy-lab-v2"
SRC="$BASE/v2.0.55"
DST="$BASE/staging/v2.0.56"
TMP="$BASE/staging/.v2.0.56-build-$$"
REPO="/home/tdw/the-darkest-hour"
REPO_SOURCE="$REPO/controller/staging/v2.0.56"
GATE="/usr/local/sbin/tdh-lab-admin-gate"

EXPECTED_CONTROLLER_SHA256="9acbb7388787c1b075d4e4b6bee8699803c7bc8283949b4b42180a0ba9c1ba3d"
EXPECTED_TEST_SHA256="c1d4233ea5816588d85212af527de4236da3a854d87b6d2abc1c3e484e5a38f2"

cleanup() {
    if [[ -d "$TMP" && "$TMP" == "$BASE/staging/.v2.0.56-build-"* ]]; then
        rm -rf --one-file-system "$TMP"
    fi
}
trap cleanup EXIT

echo "===== 1. STOP AND BLOCK v2.0.55 DURING UPGRADE ====="
systemctl mask --runtime --now "$SERVICE" || true
sleep 1

if [[ "$(systemctl is-active "$SERVICE" || true)" == "active" ]]; then
    echo "BLOCKED: supervisor is still active"
    exit 2
fi

echo "===== 2. VERIFY SEALED v2.0.55 ====="
test -d "$SRC"
test -f "$SRC/SHA256SUMS"
(
    cd "$SRC"
    sha256sum -c SHA256SUMS >/dev/null
)
"$GATE" preflight v2.0.55 >/tmp/tdh-v2.0.55-before-v256-preflight.log
grep -q '"status": "PREFLIGHT_OK"' /tmp/tdh-v2.0.55-before-v256-preflight.log

echo "===== 3. VERIFY REPOSITORY SOURCES ====="
test "$(git -C "$REPO" branch --show-current)" = "main"
test -f "$REPO_SOURCE/strategy_lab_controller.py"
test -f "$REPO_SOURCE/tests/test_v256_frontier_exhaustion_scout.py"
echo "$EXPECTED_CONTROLLER_SHA256  $REPO_SOURCE/strategy_lab_controller.py" | sha256sum -c -
echo "$EXPECTED_TEST_SHA256  $REPO_SOURCE/tests/test_v256_frontier_exhaustion_scout.py" | sha256sum -c -

if [[ -e "$DST" ]]; then
    echo "BLOCKED: staging destination already exists: $DST"
    exit 3
fi

echo "===== 4. BUILD v2.0.56 STAGING ====="
mkdir -p "$BASE/staging"
mkdir -p "$TMP"
cp -a "$SRC/." "$TMP/"
rm -f "$TMP/SHA256SUMS"

install -m 0755 \
    "$REPO_SOURCE/strategy_lab_controller.py" \
    "$TMP/strategy_lab_controller.py"
install -m 0644 \
    "$REPO_SOURCE/tests/test_v256_frontier_exhaustion_scout.py" \
    "$TMP/tests/test_v256_frontier_exhaustion_scout.py"

python3 -m py_compile \
    "$TMP/strategy_lab_controller.py" \
    "$TMP/tests/test_v256_frontier_exhaustion_scout.py"

echo "===== 5. PUBLISH STAGING ATOMICALLY ====="
mv -- "$TMP" "$DST"

sha256sum \
    "$DST/strategy_lab_controller.py" \
    "$DST/tests/test_v256_frontier_exhaustion_scout.py"

echo "SERVICE_STATE=$(systemctl is-active "$SERVICE" || true)"
echo "TDH_V256_STAGE_COMPLETE"
