#!/usr/bin/env bash
set -Eeuo pipefail

SERVICE="strategy-lab-supervisor-v2.1.service"
BASE="/srv/tdh-collab/controller/strategy-lab-v2"
SRC="$BASE/v2.0.79"
DST="$BASE/staging/v2.0.80"
TMP="$BASE/staging/.v2.0.80-build-$$"
REPO="/home/tdw/the-darkest-hour"
REPO_SOURCE="$REPO/controller/staging/v2.0.80"
GATE="/usr/local/sbin/tdh-lab-admin-gate"
PYTHON="/srv/tdh-research/phoenix-venv/bin/python"

EXPECTED_CONTROLLER_SHA256="e490d8b56c6fc02fc2a07aa3530fab5ac21489c6fcd24cd4c9d3ab8ba8728405"
EXPECTED_V280_TEST_SHA256="fef520ac39366670d69e0fa441436431269dd14b1d11c2b32d2e196e342e2f2c"

cleanup() {
    if [[ -d "$TMP" && "$TMP" == "$BASE/staging/.v2.0.80-build-"* ]]; then
        rm -rf --one-file-system "$TMP"
    fi
}
trap cleanup EXIT

echo "===== 1. STOP AND BLOCK v2.0.79 DURING HEADROOM REPAIR ====="
systemctl mask --runtime --now "$SERVICE" || true
sleep 1
test "$(systemctl is-active "$SERVICE" || true)" != "active"

echo "===== 2. VERIFY SEALED v2.0.79 ====="
test -d "$SRC"
test -f "$SRC/SHA256SUMS"
(
    cd "$SRC"
    sha256sum -c SHA256SUMS >/dev/null
)
"$GATE" preflight v2.0.79 >/tmp/tdh-v2.0.79-before-v280-preflight.log
grep -q '"status": "PREFLIGHT_OK"' /tmp/tdh-v2.0.79-before-v280-preflight.log

echo "===== 3. VERIFY REPOSITORY SOURCES ====="
REPO_BRANCH="$(git -C "$REPO" branch --show-current)"
case "$REPO_BRANCH" in
    main|agent/v2-0-80-post-s1-headroom-bridge) ;;
    *)
        echo "BLOCKED: unexpected repository branch: $REPO_BRANCH"
        exit 4
        ;;
esac
test -f "$REPO_SOURCE/strategy_lab_controller.py"
test -f "$REPO_SOURCE/tests/test_v280_post_s1_headroom_bridge.py"
test ! -L "$REPO_SOURCE/strategy_lab_controller.py"
test ! -L "$REPO_SOURCE/tests/test_v280_post_s1_headroom_bridge.py"
echo "$EXPECTED_CONTROLLER_SHA256  $REPO_SOURCE/strategy_lab_controller.py" | sha256sum -c -
echo "$EXPECTED_V280_TEST_SHA256  $REPO_SOURCE/tests/test_v280_post_s1_headroom_bridge.py" | sha256sum -c -

if [[ -e "$DST" ]]; then
    echo "BLOCKED: staging destination already exists: $DST"
    exit 3
fi

echo "===== 4. BUILD v2.0.80 STAGING ====="
test -x "$PYTHON"
"$PYTHON" -c 'import numpy, pandas'
mkdir -p "$BASE/staging"
mkdir -p "$TMP"
cp -a "$SRC/." "$TMP/"
rm -f "$TMP/SHA256SUMS"

install -T -m 0755 -- \
    "$REPO_SOURCE/strategy_lab_controller.py" \
    "$TMP/strategy_lab_controller.py"
install -T -m 0644 -- \
    "$REPO_SOURCE/tests/test_v280_post_s1_headroom_bridge.py" \
    "$TMP/tests/test_v280_post_s1_headroom_bridge.py"

"$PYTHON" -m py_compile \
    "$TMP/strategy_lab_controller.py" \
    "$TMP/tests/test_v241_post_s1_precheck_compaction.py" \
    "$TMP/tests/test_v278_sealed_diversification_bridge.py" \
    "$TMP/tests/test_v279_v278_adapter_binding.py" \
    "$TMP/tests/test_v280_post_s1_headroom_bridge.py"

"$PYTHON" "$TMP/tests/test_v241_post_s1_precheck_compaction.py"
"$PYTHON" "$TMP/tests/test_v278_sealed_diversification_bridge.py"
"$PYTHON" "$TMP/tests/test_v279_v278_adapter_binding.py"
"$PYTHON" "$TMP/tests/test_v280_post_s1_headroom_bridge.py"

"$PYTHON" - "$TMP/strategy_lab_controller.py" <<'PY'
import importlib.util
import sys

path = sys.argv[1]
spec = importlib.util.spec_from_file_location('tdh_v280_stage_smoke', path)
if spec is None or spec.loader is None:
    raise SystemExit('BLOCKED: v2.0.80 controller import failed')
module = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = module
spec.loader.exec_module(module)

contract = module.runtime_binding_contract()
assert contract['v280_exact_legacy_error_only'] is True
assert contract['v280_analysis_max_chars'] == 6200
assert contract['v280_raw_evidence_remains_on_vps'] is True
assert contract['v280_all_current_candidate_configs_preserved'] is True
assert contract['v280_hard_metrics_and_failed_gates_preserved'] is True
assert contract['v280_strongest_counterexample_preserved'] is True
assert contract['v280_negative_memory_and_provenance_bounded'] is True
assert contract['v280_compactor_owner_bound'] is True
assert contract['v280_provider_invoked_by_compactor'] is False
assert contract['v280_s1_gates_unchanged'] is True
assert contract['v280_unknown_errors_fail_closed'] is True
assert contract['controller_only_promotion'] is True
assert contract['trading_actions'] is False
assert contract['exchange_api_access'] is False
print('V280_POST_S1_HEADROOM_BRIDGE_SMOKE_OK')
PY

echo "===== 5. PUBLISH STAGING ATOMICALLY ====="
mv -- "$TMP" "$DST"

sha256sum \
    "$DST/strategy_lab_controller.py" \
    "$DST/tests/test_v280_post_s1_headroom_bridge.py"

echo "SERVICE_STATE=$(systemctl is-active "$SERVICE" || true)"
echo "TDH_V280_STAGE_COMPLETE"
