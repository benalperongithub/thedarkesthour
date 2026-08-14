#!/usr/bin/env bash
set -Eeuo pipefail

SERVICE="strategy-lab-supervisor-v2.1.service"
BASE="/srv/tdh-collab/controller/strategy-lab-v2"
SRC="$BASE/v2.0.52"
DST="$BASE/staging/v2.0.53"
TMP="$BASE/staging/.v2.0.53-build-$$"
REPO="/home/tdw/the-darkest-hour"
REPO_SOURCE="$REPO/controller/staging/v2.0.53"
GATE="/usr/local/sbin/tdh-lab-admin-gate"

EXPECTED_CONTROLLER_SHA256="4da1e3ece6c561e354a8f0a2cf8058be6b83af134eaacf384b414b45d5a3e81f"
EXPECTED_TEST_SHA256="bb28caaa87f2f1b361bcf98a3cbfc227b5c31513f9d8b947264ad9a2117705cc"

cleanup() {
    if [[ -d "$TMP" && "$TMP" == "$BASE/staging/.v2.0.53-build-"* ]]; then
        rm -rf --one-file-system "$TMP"
    fi
}
trap cleanup EXIT

echo "===== 1. KEEP BLOCKED v2.0.52 STOPPED ====="
systemctl mask --runtime --now "$SERVICE" || true
sleep 1

if [[ "$(systemctl is-active "$SERVICE" || true)" == "active" ]]; then
    echo "BLOCKED: supervisor is still active"
    exit 2
fi

echo "===== 2. VERIFY SEALED v2.0.52 ====="
test -d "$SRC"
test -f "$SRC/SHA256SUMS"
(
    cd "$SRC"
    sha256sum -c SHA256SUMS >/dev/null
)
"$GATE" preflight v2.0.52 >/tmp/tdh-v2.0.52-before-v253-preflight.log

echo "===== 3. VERIFY REPOSITORY SOURCES ====="
test "$(git -C "$REPO" branch --show-current)" = "main"
test -f "$REPO_SOURCE/strategy_lab_controller.py"
test -f "$REPO_SOURCE/tests/test_v253_audit_contract_resilience.py"
echo "$EXPECTED_CONTROLLER_SHA256  $REPO_SOURCE/strategy_lab_controller.py" | sha256sum -c -
echo "$EXPECTED_TEST_SHA256  $REPO_SOURCE/tests/test_v253_audit_contract_resilience.py" | sha256sum -c -

if [[ -e "$DST" ]]; then
    echo "BLOCKED: staging destination already exists: $DST"
    exit 3
fi

echo "===== 4. BUILD v2.0.53 STAGING ====="
mkdir -p "$BASE/staging"
mkdir -p "$TMP"
cp -a "$SRC/." "$TMP/"
rm -f "$TMP/SHA256SUMS"

install -m 0755 \
    "$REPO_SOURCE/strategy_lab_controller.py" \
    "$TMP/strategy_lab_controller.py"
install -m 0644 \
    "$REPO_SOURCE/tests/test_v253_audit_contract_resilience.py" \
    "$TMP/tests/test_v253_audit_contract_resilience.py"

python3 -m py_compile \
    "$TMP/strategy_lab_controller.py" \
    "$TMP/tests/test_v253_audit_contract_resilience.py"

echo "===== 5. PUBLISH STAGING ATOMICALLY ====="
mv -- "$TMP" "$DST"

sha256sum \
    "$DST/strategy_lab_controller.py" \
    "$DST/tests/test_v253_audit_contract_resilience.py"

echo "SERVICE_STATE=$(systemctl is-active "$SERVICE" || true)"
echo "TDH_V253_STAGE_COMPLETE"
