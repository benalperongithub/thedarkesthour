#!/usr/bin/env bash
set -Eeuo pipefail

SERVICE="strategy-lab-supervisor-v2.1.service"
BASE="/srv/tdh-collab/controller/strategy-lab-v2"
SRC="$BASE/v2.0.80"
DST="$BASE/staging/v2.0.81"
TMP="$BASE/staging/.v2.0.81-build-$$"
REPO="/home/tdw/the-darkest-hour"
REPO_SOURCE="$REPO/controller/staging/v2.0.81"
GATE="/usr/local/sbin/tdh-lab-admin-gate"
PYTHON="/srv/tdh-research/phoenix-venv/bin/python"

EXPECTED_CONTROLLER_SHA256="402c09a814b3bca9f94b0b2936bafcfd81fbd7b809471ef4bfe03c4acc177b70"
EXPECTED_V281_TEST_SHA256="9bb3c4a72ddd0ab68183310195991858334c7c883b69ea1d15c9a5610c50b977"

cleanup() {
    if [[ -d "$TMP" && "$TMP" == "$BASE/staging/.v2.0.81-build-"* ]]; then
        rm -rf --one-file-system "$TMP"
    fi
}
trap cleanup EXIT

echo "===== 1. STOP AND BLOCK DURING v2.0.81 FOLD-BRIDGE REPAIR ====="
systemctl mask --runtime --now "$SERVICE" || true
sleep 1
test "$(systemctl is-active "$SERVICE" || true)" != "active"

echo "===== 2. VERIFY SEALED v2.0.80 ====="
test -d "$SRC"
test -f "$SRC/SHA256SUMS"
(
    cd "$SRC"
    sha256sum -c SHA256SUMS >/dev/null
)
"$GATE" preflight v2.0.80 >/tmp/tdh-v2.0.80-before-v281-preflight.log
grep -q '"status": "PREFLIGHT_OK"' /tmp/tdh-v2.0.80-before-v281-preflight.log

echo "===== 3. VERIFY REPOSITORY SOURCES ====="
REPO_BRANCH="$(git -C "$REPO" branch --show-current)"
case "$REPO_BRANCH" in
    main|agent/v2-0-81-post-s1-fold-counterexample-bridge) ;;
    *)
        echo "BLOCKED: unexpected repository branch: $REPO_BRANCH"
        exit 4
        ;;
esac
test -f "$REPO_SOURCE/strategy_lab_controller.py"
test -f "$REPO_SOURCE/tests/test_v281_post_s1_fold_counterexample_bridge.py"
test ! -L "$REPO_SOURCE/strategy_lab_controller.py"
test ! -L "$REPO_SOURCE/tests/test_v281_post_s1_fold_counterexample_bridge.py"
echo "$EXPECTED_CONTROLLER_SHA256  $REPO_SOURCE/strategy_lab_controller.py" | sha256sum -c -
echo "$EXPECTED_V281_TEST_SHA256  $REPO_SOURCE/tests/test_v281_post_s1_fold_counterexample_bridge.py" | sha256sum -c -

if [[ -e "$DST" ]]; then
    echo "BLOCKED: staging destination already exists: $DST"
    exit 3
fi

echo "===== 4. BUILD v2.0.81 STAGING ====="
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
    "$REPO_SOURCE/tests/test_v281_post_s1_fold_counterexample_bridge.py" \
    "$TMP/tests/test_v281_post_s1_fold_counterexample_bridge.py"

"$PYTHON" -m py_compile \
    "$TMP/strategy_lab_controller.py" \
    "$TMP/tests/test_v241_post_s1_precheck_compaction.py" \
    "$TMP/tests/test_v278_sealed_diversification_bridge.py" \
    "$TMP/tests/test_v279_v278_adapter_binding.py" \
    "$TMP/tests/test_v280_post_s1_headroom_bridge.py" \
    "$TMP/tests/test_v281_post_s1_fold_counterexample_bridge.py"

"$PYTHON" "$TMP/tests/test_v241_post_s1_precheck_compaction.py"
"$PYTHON" "$TMP/tests/test_v278_sealed_diversification_bridge.py"
"$PYTHON" "$TMP/tests/test_v279_v278_adapter_binding.py"
"$PYTHON" "$TMP/tests/test_v280_post_s1_headroom_bridge.py"
"$PYTHON" "$TMP/tests/test_v281_post_s1_fold_counterexample_bridge.py"

"$PYTHON" - "$TMP/strategy_lab_controller.py" <<'PY'
import importlib.util
import sys

path = sys.argv[1]
spec = importlib.util.spec_from_file_location('tdh_v281_stage_smoke', path)
if spec is None or spec.loader is None:
    raise SystemExit('BLOCKED: v2.0.81 controller import failed')
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
assert contract['v281_exact_runtime_artifact_lookup'] is True
assert contract['v281_candidate_run_round_path_bound'] is True
assert contract['v281_worst_fold_from_full_evidence'] is True
assert contract['v281_source_result_hash_bound'] is True
assert contract['v281_strategy_config_hash_bound'] is True
assert contract['v281_raw_folds_remain_on_vps'] is True
assert contract['v281_provider_invoked_by_artifact_bridge'] is False
assert contract['v281_s1_gates_unchanged'] is True
assert contract['v281_unknown_shapes_fail_closed'] is True
assert contract['controller_only_promotion'] is True
assert contract['trading_actions'] is False
assert contract['exchange_api_access'] is False
print('V281_POST_S1_FOLD_COUNTEREXAMPLE_BRIDGE_SMOKE_OK')
PY

echo "===== 5. PUBLISH STAGING ATOMICALLY ====="
mv -- "$TMP" "$DST"

sha256sum \
    "$DST/strategy_lab_controller.py" \
    "$DST/tests/test_v281_post_s1_fold_counterexample_bridge.py"

echo "SERVICE_STATE=$(systemctl is-active "$SERVICE" || true)"
echo "TDH_V281_STAGE_COMPLETE"
