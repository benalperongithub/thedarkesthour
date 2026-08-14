#!/usr/bin/env bash
set -Eeuo pipefail

SERVICE="strategy-lab-supervisor-v2.1.service"
BASE="/srv/tdh-collab/controller/strategy-lab-v2"
SRC="$BASE/v2.0.57"
DST="$BASE/staging/v2.0.58"
TMP="$BASE/staging/.v2.0.58-build-$$"
REPO="/home/tdw/the-darkest-hour"
REPO_SOURCE="$REPO/controller/staging/v2.0.58"
GATE="/usr/local/sbin/tdh-lab-admin-gate"

EXPECTED_CONTROLLER_SHA256="69206364538ab553fbdb7ded2371070bfe1d99d163bdc23c6b9d7ba33b33110b"
EXPECTED_KERNEL_SHA256="ae4c30e5f067efa37fd712c1b39ce468dbc4f807cfaac2d93544bf7e82af65fd"
EXPECTED_SEEDS_SHA256="f2c8df12a017d59dc828c4896b15cb975f76317ec86a6573195bece279c5fed4"
EXPECTED_TEST_SHA256="2dcef0b0fb8e54f2816e03bc7b54feadd2e5144f14f9cfca8ab93b70e4fda25c"

cleanup() {
    if [[ -d "$TMP" && "$TMP" == "$BASE/staging/.v2.0.58-build-"* ]]; then
        rm -rf --one-file-system "$TMP"
    fi
}
trap cleanup EXIT

echo "===== 1. STOP AND BLOCK v2.0.57 DURING UPGRADE ====="
systemctl mask --runtime --now "$SERVICE" || true
sleep 1

if [[ "$(systemctl is-active "$SERVICE" || true)" == "active" ]]; then
    echo "BLOCKED: supervisor is still active"
    exit 2
fi

echo "===== 2. VERIFY SEALED v2.0.57 ====="
test -d "$SRC"
test -f "$SRC/SHA256SUMS"
(
    cd "$SRC"
    sha256sum -c SHA256SUMS >/dev/null
)
"$GATE" preflight v2.0.57 >/tmp/tdh-v2.0.57-before-v258-preflight.log
grep -q '"status": "PREFLIGHT_OK"' /tmp/tdh-v2.0.57-before-v258-preflight.log

echo "===== 3. VERIFY REPOSITORY SOURCES ====="
test "$(git -C "$REPO" branch --show-current)" = "main"
echo "$EXPECTED_CONTROLLER_SHA256  $REPO_SOURCE/strategy_lab_controller.py" | sha256sum -c -
echo "$EXPECTED_KERNEL_SHA256  $REPO_SOURCE/research/research_kernel.py" | sha256sum -c -
echo "$EXPECTED_SEEDS_SHA256  $REPO_SOURCE/research/frontier-scout-approved-seeds-v1.jsonl" | sha256sum -c -
echo "$EXPECTED_TEST_SHA256  $REPO_SOURCE/tests/test_v258_controller_admission.py" | sha256sum -c -

if [[ -e "$DST" ]]; then
    echo "BLOCKED: staging destination already exists: $DST"
    exit 3
fi

echo "===== 4. BUILD v2.0.58 STAGING ====="
mkdir -p "$BASE/staging"
mkdir -p "$TMP"
cp -a "$SRC/." "$TMP/"
rm -f "$TMP/SHA256SUMS"

install -T -m 0755 -- \
    "$REPO_SOURCE/strategy_lab_controller.py" \
    "$TMP/strategy_lab_controller.py"
install -T -m 0644 -- \
    "$REPO_SOURCE/research/research_kernel.py" \
    "$TMP/research/research_kernel.py"
install -T -m 0644 -- \
    "$REPO_SOURCE/research/frontier-scout-approved-seeds-v1.jsonl" \
    "$TMP/research/frontier-scout-approved-seeds-v1.jsonl"
install -T -m 0644 -- \
    "$REPO_SOURCE/tests/test_v258_controller_admission.py" \
    "$TMP/tests/test_v258_controller_admission.py"

python3 -m py_compile \
    "$TMP/strategy_lab_controller.py" \
    "$TMP/research/research_kernel.py" \
    "$TMP/tests/test_v258_controller_admission.py"

python3 - "$TMP/research/frontier-scout-approved-seeds-v1.jsonl" <<'PY'
import json
import sys
from pathlib import Path

rows = [
    json.loads(line)
    for line in Path(sys.argv[1]).read_text(encoding='utf-8').splitlines()
    if line.strip()
]
assert len(rows) == 6
assert len({row['experiment_id'] for row in rows}) == 6
assert {row['family_id'] for row in rows} == {'VOLUME_TSMOM'}
assert {row['timeframe'] for row in rows} == {'1h', '4h', '1d'}
assert all(row['controller_admission']['trading_actions'] is False for row in rows)
assert all(row['controller_admission']['exchange_api_access'] is False for row in rows)
print('V258_STATIC_SEED_CONTRACT_OK')
PY

echo "===== 5. PUBLISH STAGING ATOMICALLY ====="
mv -- "$TMP" "$DST"

sha256sum \
    "$DST/strategy_lab_controller.py" \
    "$DST/research/research_kernel.py" \
    "$DST/research/frontier-scout-approved-seeds-v1.jsonl" \
    "$DST/tests/test_v258_controller_admission.py"

echo "SERVICE_STATE=$(systemctl is-active "$SERVICE" || true)"
echo "TDH_V258_STAGE_COMPLETE"
