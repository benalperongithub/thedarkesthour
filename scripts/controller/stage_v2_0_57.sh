#!/usr/bin/env bash
set -Eeuo pipefail

SERVICE="strategy-lab-supervisor-v2.1.service"
BASE="/srv/tdh-collab/controller/strategy-lab-v2"
SRC="$BASE/v2.0.56"
DST="$BASE/staging/v2.0.57"
TMP="$BASE/staging/.v2.0.57-build-$$"
REPO="/home/tdw/the-darkest-hour"
REPO_SOURCE="$REPO/controller/staging/v2.0.57"
GATE="/usr/local/sbin/tdh-lab-admin-gate"

EXPECTED_CONTROLLER_SHA256="48b42530b4e48c9cd00fc82077acaa4a8c386d5344bdfd3dddb18ed010c1f7e2"
EXPECTED_TEST_SHA256="73872f4ac5d2eec6eafdf5df5815ff6672863a1a3cea416a7d9ec738a59d3024"

cleanup() {
    if [[ -d "$TMP" && "$TMP" == "$BASE/staging/.v2.0.57-build-"* ]]; then
        rm -rf --one-file-system "$TMP"
    fi
}
trap cleanup EXIT

echo "===== 1. STOP AND BLOCK v2.0.56 DURING UPGRADE ====="
systemctl mask --runtime --now "$SERVICE" || true
sleep 1

if [[ "$(systemctl is-active "$SERVICE" || true)" == "active" ]]; then
    echo "BLOCKED: supervisor is still active"
    exit 2
fi

echo "===== 2. VERIFY SEALED v2.0.56 ====="
test -d "$SRC"
test -f "$SRC/SHA256SUMS"
(
    cd "$SRC"
    sha256sum -c SHA256SUMS >/dev/null
)
"$GATE" preflight v2.0.56 >/tmp/tdh-v2.0.56-before-v257-preflight.log
grep -q '"status": "PREFLIGHT_OK"' /tmp/tdh-v2.0.56-before-v257-preflight.log

echo "===== 3. VERIFY REPOSITORY SOURCES ====="
test "$(git -C "$REPO" branch --show-current)" = "main"
test -f "$REPO_SOURCE/strategy_lab_controller.py"
test -f "$REPO_SOURCE/tests/test_v257_scout_response_conformance.py"
echo "$EXPECTED_CONTROLLER_SHA256  $REPO_SOURCE/strategy_lab_controller.py" | sha256sum -c -
echo "$EXPECTED_TEST_SHA256  $REPO_SOURCE/tests/test_v257_scout_response_conformance.py" | sha256sum -c -

if [[ -e "$DST" ]]; then
    echo "BLOCKED: staging destination already exists: $DST"
    exit 3
fi

echo "===== 4. BUILD v2.0.57 STAGING ====="
mkdir -p "$BASE/staging"
mkdir -p "$TMP"
cp -a "$SRC/." "$TMP/"
rm -f "$TMP/SHA256SUMS"

install -m 0755 \
    "$REPO_SOURCE/strategy_lab_controller.py" \
    "$TMP/strategy_lab_controller.py"
install -m 0644 \
    "$REPO_SOURCE/tests/test_v257_scout_response_conformance.py" \
    "$TMP/tests/test_v257_scout_response_conformance.py"

python3 -m py_compile \
    "$TMP/strategy_lab_controller.py" \
    "$TMP/tests/test_v257_scout_response_conformance.py"

echo "===== 5. PUBLISH STAGING ATOMICALLY ====="
mv -- "$TMP" "$DST"

sha256sum \
    "$DST/strategy_lab_controller.py" \
    "$DST/tests/test_v257_scout_response_conformance.py"

echo "SERVICE_STATE=$(systemctl is-active "$SERVICE" || true)"
echo "TDH_V257_STAGE_COMPLETE"
