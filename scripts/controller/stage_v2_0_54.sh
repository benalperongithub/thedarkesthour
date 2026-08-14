#!/usr/bin/env bash
set -Eeuo pipefail

SERVICE="strategy-lab-supervisor-v2.1.service"
BASE="/srv/tdh-collab/controller/strategy-lab-v2"
SRC="$BASE/v2.0.53"
DST="$BASE/staging/v2.0.54"
TMP="$BASE/staging/.v2.0.54-build-$$"
REPO="/home/tdw/the-darkest-hour"
REPO_SOURCE="$REPO/controller/staging/v2.0.54"
GATE="/usr/local/sbin/tdh-lab-admin-gate"

EXPECTED_CONTROLLER_SHA256="9f74453a28cabf957b3f92c73666c0cb98d224559a2d0f5011afe735a5b637ff"
EXPECTED_TEST_SHA256="f087bd85dcee9413165f03db006aef27d66aa2a513f6610ed059b11646f43e1c"
EXPECTED_SCHEMA_SHA256="b0826d75783dd5d66f30f6c6a95079e3e4fd311262e9dd85d39c82e962c78449"

cleanup() {
    if [[ -d "$TMP" && "$TMP" == "$BASE/staging/.v2.0.54-build-"* ]]; then
        rm -rf --one-file-system "$TMP"
    fi
}
trap cleanup EXIT

echo "===== 1. STOP AND BLOCK v2.0.53 DURING UPGRADE ====="
systemctl mask --runtime --now "$SERVICE" || true
sleep 1

if [[ "$(systemctl is-active "$SERVICE" || true)" == "active" ]]; then
    echo "BLOCKED: supervisor is still active"
    exit 2
fi

echo "===== 2. VERIFY SEALED v2.0.53 ====="
test -d "$SRC"
test -f "$SRC/SHA256SUMS"
(
    cd "$SRC"
    sha256sum -c SHA256SUMS >/dev/null
)
"$GATE" preflight v2.0.53 >/tmp/tdh-v2.0.53-before-v254-preflight.log

echo "===== 3. VERIFY REPOSITORY SOURCES ====="
test "$(git -C "$REPO" branch --show-current)" = "main"
test -f "$REPO_SOURCE/strategy_lab_controller.py"
test -f "$REPO_SOURCE/tests/test_v254_frontier_scout.py"
test -f "$REPO_SOURCE/research/frontier-inbox.schema.json"
echo "$EXPECTED_CONTROLLER_SHA256  $REPO_SOURCE/strategy_lab_controller.py" | sha256sum -c -
echo "$EXPECTED_TEST_SHA256  $REPO_SOURCE/tests/test_v254_frontier_scout.py" | sha256sum -c -
echo "$EXPECTED_SCHEMA_SHA256  $REPO_SOURCE/research/frontier-inbox.schema.json" | sha256sum -c -

if [[ -e "$DST" ]]; then
    echo "BLOCKED: staging destination already exists: $DST"
    exit 3
fi

echo "===== 4. BUILD v2.0.54 STAGING ====="
mkdir -p "$BASE/staging"
mkdir -p "$TMP"
cp -a "$SRC/." "$TMP/"
rm -f "$TMP/SHA256SUMS"

install -m 0755 \
    "$REPO_SOURCE/strategy_lab_controller.py" \
    "$TMP/strategy_lab_controller.py"
install -m 0644 \
    "$REPO_SOURCE/tests/test_v254_frontier_scout.py" \
    "$TMP/tests/test_v254_frontier_scout.py"
install -m 0644 \
    "$REPO_SOURCE/research/frontier-inbox.schema.json" \
    "$TMP/research/frontier-inbox.schema.json"

python3 -m py_compile \
    "$TMP/strategy_lab_controller.py" \
    "$TMP/tests/test_v254_frontier_scout.py"
python3 -m json.tool \
    "$TMP/research/frontier-inbox.schema.json" \
    >/dev/null

echo "===== 5. PUBLISH STAGING ATOMICALLY ====="
mv -- "$TMP" "$DST"

sha256sum \
    "$DST/strategy_lab_controller.py" \
    "$DST/tests/test_v254_frontier_scout.py" \
    "$DST/research/frontier-inbox.schema.json"

echo "SERVICE_STATE=$(systemctl is-active "$SERVICE" || true)"
echo "TDH_V254_STAGE_COMPLETE"
