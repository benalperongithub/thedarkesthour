#!/usr/bin/env bash
set -Eeuo pipefail

SERVICE="strategy-lab-supervisor-v2.1.service"
BASE="/srv/tdh-collab/controller/strategy-lab-v2"
SRC="$BASE/v2.0.81"
DST="$BASE/staging/v2.0.82"
TMP="$BASE/staging/.v2.0.82-build-$$"
REPO="/home/tdw/the-darkest-hour"
REPO_SOURCE="$REPO/controller/staging/v2.0.82"
GATE="/usr/local/sbin/tdh-lab-admin-gate"
PYTHON="/srv/tdh-research/phoenix-venv/bin/python"

EXPECTED_CONTROLLER_SHA256="a292881c64a73719b53960e464d922ae697dd3b3846ba2e4c79aaffd8567174e"
EXPECTED_V282_TEST_SHA256="e024a71c70940b924f7fbb9e3cf302ae4a6cbbfdedfff355cd03cf6424fe3c03"

cleanup() {
    if [[ -d "$TMP" && "$TMP" == "$BASE/staging/.v2.0.82-build-"* ]]; then
        rm -rf --one-file-system "$TMP"
    fi
}
trap cleanup EXIT

echo "===== 1. STOP AND BLOCK DURING v2.0.82 LEGAL-FRONTIER RECOVERY ====="
systemctl mask --runtime --now "$SERVICE" || true
sleep 1
test "$(systemctl is-active "$SERVICE" || true)" != "active"

echo "===== 2. VERIFY SEALED v2.0.81 ====="
test -d "$SRC"
test -f "$SRC/SHA256SUMS"
(
    cd "$SRC"
    sha256sum -c SHA256SUMS >/dev/null
)
"$GATE" preflight v2.0.81 >/tmp/tdh-v2.0.81-before-v282-preflight.log
grep -q '"status": "PREFLIGHT_OK"' /tmp/tdh-v2.0.81-before-v282-preflight.log

echo "===== 3. VERIFY REPOSITORY SOURCES ====="
REPO_BRANCH="$(git -C "$REPO" branch --show-current)"
case "$REPO_BRANCH" in
    main|agent/v2-0-82-legal-frontier-recovery) ;;
    *)
        echo "BLOCKED: unexpected repository branch: $REPO_BRANCH"
        exit 4
        ;;
esac
test -f "$REPO_SOURCE/strategy_lab_controller.py"
test -f "$REPO_SOURCE/tests/test_v282_legal_frontier_recovery.py"
test ! -L "$REPO_SOURCE/strategy_lab_controller.py"
test ! -L "$REPO_SOURCE/tests/test_v282_legal_frontier_recovery.py"
echo "$EXPECTED_CONTROLLER_SHA256  $REPO_SOURCE/strategy_lab_controller.py" | sha256sum -c -
echo "$EXPECTED_V282_TEST_SHA256  $REPO_SOURCE/tests/test_v282_legal_frontier_recovery.py" | sha256sum -c -

if [[ -e "$DST" ]]; then
    echo "BLOCKED: staging destination already exists: $DST"
    exit 3
fi

echo "===== 4. BUILD v2.0.82 STAGING ====="
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
    "$REPO_SOURCE/tests/test_v282_legal_frontier_recovery.py" \
    "$TMP/tests/test_v282_legal_frontier_recovery.py"

"$PYTHON" -m py_compile \
    "$TMP/strategy_lab_controller.py" \
    "$TMP/tests/test_v241_post_s1_precheck_compaction.py" \
    "$TMP/tests/test_v278_sealed_diversification_bridge.py" \
    "$TMP/tests/test_v279_v278_adapter_binding.py" \
    "$TMP/tests/test_v280_post_s1_headroom_bridge.py" \
    "$TMP/tests/test_v281_post_s1_fold_counterexample_bridge.py" \
    "$TMP/tests/test_v282_legal_frontier_recovery.py"

"$PYTHON" "$TMP/tests/test_v241_post_s1_precheck_compaction.py"
"$PYTHON" "$TMP/tests/test_v278_sealed_diversification_bridge.py"
"$PYTHON" "$TMP/tests/test_v279_v278_adapter_binding.py"
"$PYTHON" "$TMP/tests/test_v280_post_s1_headroom_bridge.py"
"$PYTHON" "$TMP/tests/test_v281_post_s1_fold_counterexample_bridge.py"
"$PYTHON" "$TMP/tests/test_v282_legal_frontier_recovery.py"

"$PYTHON" - "$TMP/strategy_lab_controller.py" <<'PY'
import importlib.util
import sys

path = sys.argv[1]
spec = importlib.util.spec_from_file_location('tdh_v282_stage_smoke', path)
if spec is None or spec.loader is None:
    raise SystemExit('BLOCKED: v2.0.82 controller import failed')
module = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = module
spec.loader.exec_module(module)

contract = module.runtime_binding_contract()
assert contract['v282_legal_frontier_recovery_version'] == (
    module.V282_LEGAL_FRONTIER_RECOVERY_VERSION
)
assert contract['v282_recovery_schema_version'] == (
    module.V282_RECOVERY_SCHEMA_VERSION
)
assert contract['v282_registry_rotation_is_deterministic'] is True
assert contract['v282_only_exact_registered_kernel_seeds'] is True
assert contract['v282_registry_rotation_hash_bound'] is True
assert contract['v282_single_material_axis_required'] is True
assert contract['v282_authoritative_global_memory_checked'] is True
assert contract['v282_negative_memory_and_quarantine_preserved'] is True
assert contract['v282_duplicate_candidate_never_reproposed'] is True
assert contract['v282_rejection_reasons_recorded'] is True
assert contract['v282_eligible_and_rejected_sets_hash_bound'] is True
assert contract['v282_decision_chained_to_previous_decision'] is True
assert contract['v282_exhausted_registry_fails_closed'] is True
assert contract['v282_new_families_auto_registered'] is False
assert contract['v282_model_generated_executable_code'] is False
assert contract['v282_provider_invoked_by_recovery'] is False
assert contract['v282_s1_only'] is True
assert contract['v282_s1_gates_unchanged'] is True
assert contract['v282_s2_s4_opened'] is False
assert contract['v282_unknown_errors_fail_closed'] is True

# Inherited boundaries must survive the new lane untouched.
assert contract['v281_exact_runtime_artifact_lookup'] is True
assert contract['v281_s1_gates_unchanged'] is True
assert contract['v280_compactor_owner_bound'] is True
assert contract['v280_analysis_max_chars'] == 6200
assert contract['v278_single_primary_change_universe_only'] is True
assert contract['v278_provider_invoked_by_bridge'] is False
assert contract['v251_multi_axis_frontier_filter'] is True
assert contract['v254_only_existing_registered_seeds_auto_admitted'] is True
assert contract['controller_only_promotion'] is True
assert contract['policy_change'] is False
assert contract['trading_actions'] is False
assert contract['exchange_api_access'] is False

# The rotation pool must be a deterministic, complete view of the registry.
pool = module._v282_registry_rotation_pool()
_, experiments = module.kernel.registry()
assert list(pool) == sorted(pool)
assert len(pool) == len(experiments)
assert {experiment_id for _, experiment_id in pool} == set(experiments)
print('V282_LEGAL_FRONTIER_RECOVERY_SMOKE_OK')
PY

echo "===== 5. PUBLISH STAGING ATOMICALLY ====="
mv -- "$TMP" "$DST"

sha256sum \
    "$DST/strategy_lab_controller.py" \
    "$DST/tests/test_v282_legal_frontier_recovery.py"

echo "SERVICE_STATE=$(systemctl is-active "$SERVICE" || true)"
echo "TDH_V282_STAGE_COMPLETE"
