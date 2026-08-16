#!/usr/bin/env bash
set -Eeuo pipefail

SERVICE="strategy-lab-supervisor-v2.1.service"
BASE="/srv/tdh-collab/controller/strategy-lab-v2"
SRC="$BASE/v2.0.78"
DST="$BASE/staging/v2.0.79"
TMP="$BASE/staging/.v2.0.79-build-$$"
REPO="/home/tdw/the-darkest-hour"
REPO_SOURCE="$REPO/controller/staging/v2.0.79"
GATE="/usr/local/sbin/tdh-lab-admin-gate"
PYTHON="/srv/tdh-research/phoenix-venv/bin/python"

EXPECTED_ADAPTER_SHA256="d78ea727a8e774206012cf2994496cfec56327327ca903c73b3800e54ed545b3"
EXPECTED_V279_TEST_SHA256="417b25e29b1e7bad886c8418b4abb2a6c8c2e6c478b679e69c23d2346b378b24"

cleanup() {
    if [[ -d "$TMP" && "$TMP" == "$BASE/staging/.v2.0.79-build-"* ]]; then
        rm -rf --one-file-system "$TMP"
    fi
}
trap cleanup EXIT

echo "===== 1. STOP AND BLOCK v2.0.78 DURING ADAPTER REPAIR ====="
systemctl mask --runtime --now "$SERVICE" || true
sleep 1
test "$(systemctl is-active "$SERVICE" || true)" != "active"

echo "===== 2. VERIFY SEALED v2.0.78 ====="
test -d "$SRC"
test -f "$SRC/SHA256SUMS"
(
    cd "$SRC"
    sha256sum -c SHA256SUMS >/dev/null
)
"$GATE" preflight v2.0.78 >/tmp/tdh-v2.0.78-before-v279-preflight.log
grep -q '"status": "PREFLIGHT_OK"' /tmp/tdh-v2.0.78-before-v279-preflight.log

echo "===== 3. VERIFY REPOSITORY SOURCES ====="
REPO_BRANCH="$(git -C "$REPO" branch --show-current)"
case "$REPO_BRANCH" in
    main|agent/v2-0-79-v278-adapter-binding) ;;
    *)
        echo "BLOCKED: unexpected repository branch: $REPO_BRANCH"
        exit 4
        ;;
esac
test -f "$REPO_SOURCE/adapter/tdh_strategy_lab_research_adapter.py"
test -f "$REPO_SOURCE/tests/test_v279_v278_adapter_binding.py"
test ! -L "$REPO_SOURCE/adapter/tdh_strategy_lab_research_adapter.py"
test ! -L "$REPO_SOURCE/tests/test_v279_v278_adapter_binding.py"
echo "$EXPECTED_ADAPTER_SHA256  $REPO_SOURCE/adapter/tdh_strategy_lab_research_adapter.py" | sha256sum -c -
echo "$EXPECTED_V279_TEST_SHA256  $REPO_SOURCE/tests/test_v279_v278_adapter_binding.py" | sha256sum -c -

if [[ -e "$DST" ]]; then
    echo "BLOCKED: staging destination already exists: $DST"
    exit 3
fi

echo "===== 4. BUILD v2.0.79 STAGING ====="
test -x "$PYTHON"
"$PYTHON" -c 'import numpy, pandas'
mkdir -p "$BASE/staging"
mkdir -p "$TMP"
cp -a "$SRC/." "$TMP/"
rm -f "$TMP/SHA256SUMS"

install -T -m 0755 -- \
    "$REPO_SOURCE/adapter/tdh_strategy_lab_research_adapter.py" \
    "$TMP/adapter/tdh_strategy_lab_research_adapter.py"
install -T -m 0644 -- \
    "$REPO_SOURCE/tests/test_v279_v278_adapter_binding.py" \
    "$TMP/tests/test_v279_v278_adapter_binding.py"

"$PYTHON" -m py_compile \
    "$TMP/adapter/tdh_strategy_lab_research_adapter.py" \
    "$TMP/tests/test_v268_volume_tsmom_ablation.py" \
    "$TMP/tests/test_v278_sealed_diversification_bridge.py" \
    "$TMP/tests/test_v279_v278_adapter_binding.py"

"$PYTHON" "$TMP/tests/test_v268_volume_tsmom_ablation.py"
"$PYTHON" "$TMP/tests/test_v278_sealed_diversification_bridge.py"
"$PYTHON" "$TMP/tests/test_v279_v278_adapter_binding.py"

"$PYTHON" - "$TMP/adapter/tdh_strategy_lab_research_adapter.py" <<'PY'
import importlib.util
import sys

path = sys.argv[1]
spec = importlib.util.spec_from_file_location('tdh_v279_stage_smoke', path)
if spec is None or spec.loader is None:
    raise SystemExit('BLOCKED: v2.0.79 adapter import failed')
module = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = module
spec.loader.exec_module(module)

assert module.V279_EXPERIMENT_IDS == frozenset(module.kernel.V278_IDENTITIES)
assert module.V279_FAMILY == 'VOLUME_TSMOM'
status = module.kernel.v278_registry_status()
assert status['approved_seed_count'] == 3
assert status['symbols'] == ['BTCUSDT', 'ETHUSDT', 'SOLUSDT', 'XRPUSDT']
assert status['raw_proposal_executed'] is False
assert status['s1_only'] is True
assert status['trading_actions'] is False
assert status['exchange_api_access'] is False
print('V279_V278_ADAPTER_BINDING_SMOKE_OK')
PY

echo "===== 5. PUBLISH STAGING ATOMICALLY ====="
mv -- "$TMP" "$DST"

sha256sum \
    "$DST/adapter/tdh_strategy_lab_research_adapter.py" \
    "$DST/tests/test_v279_v278_adapter_binding.py"

echo "SERVICE_STATE=$(systemctl is-active "$SERVICE" || true)"
echo "TDH_V279_STAGE_COMPLETE"
