#!/usr/bin/env bash
set -Eeuo pipefail

SERVICE="strategy-lab-supervisor-v2.1.service"
BASE="/srv/tdh-collab/controller/strategy-lab-v2"
SRC="$BASE/v2.0.59"
DST="$BASE/staging/v2.0.60"
TMP="$BASE/staging/.v2.0.60-build-$$"
REPO="/home/tdw/the-darkest-hour"
REPO_SOURCE="$REPO/controller/staging/v2.0.60"
GATE="/usr/local/sbin/tdh-lab-admin-gate"

EXPECTED_CONTROLLER_SHA256="6d3c6f2b9d0b40697002c72e26de175551123a05d808522b6ab40cb73a9bacca"
EXPECTED_TEST_SHA256="642d77febb6c6163f13f7f8f3f6374621adb738dc2e6e212b098b256fdda62fa"

cleanup() {
    if [[ -d "$TMP" && "$TMP" == "$BASE/staging/.v2.0.60-build-"* ]]; then
        rm -rf --one-file-system "$TMP"
    fi
}
trap cleanup EXIT

echo "===== 1. STOP AND BLOCK v2.0.59 DURING UPGRADE ====="
systemctl mask --runtime --now "$SERVICE" || true
sleep 1
test "$(systemctl is-active "$SERVICE" || true)" != "active"

echo "===== 2. VERIFY SEALED v2.0.59 ====="
test -d "$SRC"
test -f "$SRC/SHA256SUMS"
(
    cd "$SRC"
    sha256sum -c SHA256SUMS >/dev/null
)
"$GATE" preflight v2.0.59 >/tmp/tdh-v2.0.59-before-v260-preflight.log
grep -q '"status": "PREFLIGHT_OK"' /tmp/tdh-v2.0.59-before-v260-preflight.log

echo "===== 3. VERIFY REPOSITORY SOURCES ====="
test "$(git -C "$REPO" branch --show-current)" = "main"
echo "$EXPECTED_CONTROLLER_SHA256  $REPO_SOURCE/strategy_lab_controller.py" | sha256sum -c -
echo "$EXPECTED_TEST_SHA256  $REPO_SOURCE/tests/test_v260_registered_seed_transition.py" | sha256sum -c -

if [[ -e "$DST" ]]; then
    echo "BLOCKED: staging destination already exists: $DST"
    exit 3
fi

echo "===== 4. BUILD v2.0.60 STAGING ====="
mkdir -p "$BASE/staging"
mkdir -p "$TMP"
cp -a "$SRC/." "$TMP/"
rm -f "$TMP/SHA256SUMS"

install -T -m 0755 -- \
    "$REPO_SOURCE/strategy_lab_controller.py" \
    "$TMP/strategy_lab_controller.py"
install -T -m 0644 -- \
    "$REPO_SOURCE/tests/test_v260_registered_seed_transition.py" \
    "$TMP/tests/test_v260_registered_seed_transition.py"

python3 -m py_compile \
    "$TMP/strategy_lab_controller.py" \
    "$TMP/tests/test_v260_registered_seed_transition.py"

python3 - "$TMP/strategy_lab_controller.py" <<'PY'
import copy
import importlib.util
import sys

path = sys.argv[1]
spec = importlib.util.spec_from_file_location('tdh_v260_stage_smoke', path)
if spec is None or spec.loader is None:
    raise SystemExit('BLOCKED: v2.0.60 controller import failed')
module = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = module
spec.loader.exec_module(module)

contract = module.runtime_binding_contract()
assert contract['v259_runtime_kernel_overlay_bound'] is True
assert contract['v260_only_exact_controller_registered_seed_is_atomic'] is True
assert contract['v260_spoofed_or_freeform_seed_transition_fails_closed'] is True
assert contract['controller_only_promotion'] is True
assert contract['trading_actions'] is False
assert contract['exchange_api_access'] is False

_, experiments = module.kernel.registry()
source_id = 'TDH-SCOUT-000001-VTM-NODOGE-1H'
target_id = 'TDH-SCOUT-000001-VTM-FULL-4H'
source = module.kernel.validate_config(
    module.kernel.performance_config(experiments[source_id], 'BTCUSDT')
)
target = module.kernel.validate_config(
    module.kernel.performance_config(experiments[target_id], 'BTCUSDT')
)
registration = {
    'version': module.V254_FRONTIER_SCOUT_VERSION,
    'source': 'EXISTING_REGISTERED_KERNEL_SEED',
    'experiment_id': target_id,
    'family_id': 'VOLUME_TSMOM',
    'schema_validated': True,
    'data_eligibility_inherited_from_selection': True,
    'deduplicated': True,
    'model_generated_executable_code': False,
    'controller_only_registration': True,
}
item = {'config': copy.deepcopy(target), 'v254_registration': registration}
assert module._v251_transition_axes(source, target) == (
    'timeframe', 'registered_seed'
)
assert module._v251_legal_frontier_item(source, item) is True

spoofed = copy.deepcopy(item)
spoofed['config']['params']['return_lookback'] += 1
assert module._v251_legal_frontier_item(source, spoofed) is False
assert module._v251_legal_frontier_item(source, {'config': target}) is True
cross_symbol = copy.deepcopy(target)
cross_symbol['symbol'] = 'XRPUSDT'
assert module._v251_legal_frontier_item(
    source, {'config': cross_symbol}
) is False
print('V260_REGISTERED_SEED_TRANSITION_SMOKE_OK')
PY

echo "===== 5. PUBLISH STAGING ATOMICALLY ====="
mv -- "$TMP" "$DST"

sha256sum \
    "$DST/strategy_lab_controller.py" \
    "$DST/tests/test_v260_registered_seed_transition.py"

echo "SERVICE_STATE=$(systemctl is-active "$SERVICE" || true)"
echo "TDH_V260_STAGE_COMPLETE"
