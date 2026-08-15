#!/usr/bin/env bash
set -Eeuo pipefail

SERVICE="strategy-lab-supervisor-v2.1.service"
BASE="/srv/tdh-collab/controller/strategy-lab-v2"
SRC="$BASE/v2.0.67"
DST="$BASE/staging/v2.0.68"
TMP="$BASE/staging/.v2.0.68-build-$$"
REPO="/home/tdw/the-darkest-hour"
REPO_SOURCE="$REPO/controller/staging/v2.0.68"
GATE="/usr/local/sbin/tdh-lab-admin-gate"
PYTHON="/srv/tdh-research/phoenix-venv/bin/python"

EXPECTED_CONTROLLER_SHA256="7cb1c52d2f0736f1f796adf99cca72d61ed2ce0c9f4688be15747613b6864857"
EXPECTED_KERNEL_SHA256="2f864067b8b4c8142565dceb97cda31ee7fb2cbb2bb25b9fb17adbb759ec55ea"
EXPECTED_SEEDS_SHA256="f9ce0bab8e13bcdde024290947810e0324bb5b0fbfaeae2e39d8f7cd20f99019"
EXPECTED_ADAPTER_SHA256="29392dfa12d2581075fcba12416d0f3352e7f4f6cec7d0483c181d4d0e663e68"
EXPECTED_TEST_SHA256="290b36ac9243b131878d8cb1c48d8344258c197e7015c3e1e7b7c9baf453a9f7"
EXPECTED_V267_TEST_SHA256="65cfbc292ca068477361da397b97919e02ab9e15773c8085eac6ed6f5a63541c"
EXPECTED_V266_TEST_SHA256="ebea3780c4d8c30b355b137f27ad73ee5daa510b3df9469475a63904d6f8d6e6"
EXPECTED_LEGACY_TEST_SHA256="ff68dfd372fb3c73de8c4126f7d30703d40286f0349f65bbb02af9a64e1fcae3"

cleanup() {
    if [[ -d "$TMP" && "$TMP" == "$BASE/staging/.v2.0.68-build-"* ]]; then
        rm -rf --one-file-system "$TMP"
    fi
}
trap cleanup EXIT

echo "===== 1. STOP AND BLOCK v2.0.67 DURING UPGRADE ====="
systemctl mask --runtime --now "$SERVICE" || true
sleep 1
test "$(systemctl is-active "$SERVICE" || true)" != "active"

echo "===== 2. VERIFY SEALED v2.0.67 ====="
test -d "$SRC"
test -f "$SRC/SHA256SUMS"
(
    cd "$SRC"
    sha256sum -c SHA256SUMS >/dev/null
)
"$GATE" preflight v2.0.67 >/tmp/tdh-v2.0.67-before-v268-preflight.log
grep -q '"status": "PREFLIGHT_OK"' /tmp/tdh-v2.0.67-before-v268-preflight.log

echo "===== 3. VERIFY REPOSITORY SOURCES ====="
REPO_BRANCH="$(git -C "$REPO" branch --show-current)"
case "$REPO_BRANCH" in
    main|agent/v2-0-68-volume-tsmom-ablation) ;;
    *)
        echo "BLOCKED: unexpected repository branch: $REPO_BRANCH"
        exit 4
        ;;
esac
test -f "$REPO_SOURCE/strategy_lab_controller.py"
test -f "$REPO_SOURCE/research/research_kernel.py"
test -f "$REPO_SOURCE/research/v268-volume-tsmom-ablation-seeds-v1.jsonl"
test -f "$REPO_SOURCE/adapter/tdh_strategy_lab_research_adapter.py"
test -f "$REPO_SOURCE/tests/test_v268_volume_tsmom_ablation.py"
test -f "$REPO_SOURCE/tests/test_v267_data_capability_supersession.py"
test -f "$REPO_SOURCE/tests/test_v266_frontier_producer_admission.py"
test -f "$REPO_SOURCE/tests/test_v265_frontier_inbox_lifecycle.py"
test ! -L "$REPO_SOURCE/strategy_lab_controller.py"
test ! -L "$REPO_SOURCE/research/research_kernel.py"
test ! -L "$REPO_SOURCE/research/v268-volume-tsmom-ablation-seeds-v1.jsonl"
test ! -L "$REPO_SOURCE/adapter/tdh_strategy_lab_research_adapter.py"
test ! -L "$REPO_SOURCE/tests/test_v268_volume_tsmom_ablation.py"
test ! -L "$REPO_SOURCE/tests/test_v267_data_capability_supersession.py"
test ! -L "$REPO_SOURCE/tests/test_v266_frontier_producer_admission.py"
test ! -L "$REPO_SOURCE/tests/test_v265_frontier_inbox_lifecycle.py"
echo "$EXPECTED_CONTROLLER_SHA256  $REPO_SOURCE/strategy_lab_controller.py" | sha256sum -c -
echo "$EXPECTED_KERNEL_SHA256  $REPO_SOURCE/research/research_kernel.py" | sha256sum -c -
echo "$EXPECTED_SEEDS_SHA256  $REPO_SOURCE/research/v268-volume-tsmom-ablation-seeds-v1.jsonl" | sha256sum -c -
echo "$EXPECTED_ADAPTER_SHA256  $REPO_SOURCE/adapter/tdh_strategy_lab_research_adapter.py" | sha256sum -c -
echo "$EXPECTED_TEST_SHA256  $REPO_SOURCE/tests/test_v268_volume_tsmom_ablation.py" | sha256sum -c -
echo "$EXPECTED_V267_TEST_SHA256  $REPO_SOURCE/tests/test_v267_data_capability_supersession.py" | sha256sum -c -
echo "$EXPECTED_V266_TEST_SHA256  $REPO_SOURCE/tests/test_v266_frontier_producer_admission.py" | sha256sum -c -
echo "$EXPECTED_LEGACY_TEST_SHA256  $REPO_SOURCE/tests/test_v265_frontier_inbox_lifecycle.py" | sha256sum -c -

if [[ -e "$DST" ]]; then
    echo "BLOCKED: staging destination already exists: $DST"
    exit 3
fi

echo "===== 4. BUILD v2.0.68 STAGING ====="
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
    "$REPO_SOURCE/research/research_kernel.py" \
    "$TMP/research/research_kernel.py"
install -T -m 0644 -- \
    "$REPO_SOURCE/research/v268-volume-tsmom-ablation-seeds-v1.jsonl" \
    "$TMP/research/v268-volume-tsmom-ablation-seeds-v1.jsonl"
install -T -m 0644 -- \
    "$REPO_SOURCE/adapter/tdh_strategy_lab_research_adapter.py" \
    "$TMP/adapter/tdh_strategy_lab_research_adapter.py"
install -T -m 0644 -- \
    "$REPO_SOURCE/tests/test_v268_volume_tsmom_ablation.py" \
    "$TMP/tests/test_v268_volume_tsmom_ablation.py"
install -T -m 0644 -- \
    "$REPO_SOURCE/tests/test_v267_data_capability_supersession.py" \
    "$TMP/tests/test_v267_data_capability_supersession.py"
install -T -m 0644 -- \
    "$REPO_SOURCE/tests/test_v266_frontier_producer_admission.py" \
    "$TMP/tests/test_v266_frontier_producer_admission.py"
install -T -m 0644 -- \
    "$REPO_SOURCE/tests/test_v265_frontier_inbox_lifecycle.py" \
    "$TMP/tests/test_v265_frontier_inbox_lifecycle.py"

"$PYTHON" -m py_compile \
    "$TMP/strategy_lab_controller.py" \
    "$TMP/research/research_kernel.py" \
    "$TMP/adapter/tdh_strategy_lab_research_adapter.py" \
    "$TMP/tests/test_v268_volume_tsmom_ablation.py" \
    "$TMP/tests/test_v265_frontier_inbox_lifecycle.py" \
    "$TMP/tests/test_v266_frontier_producer_admission.py" \
    "$TMP/tests/test_v267_data_capability_supersession.py"

"$PYTHON" "$TMP/tests/test_v265_frontier_inbox_lifecycle.py"
"$PYTHON" "$TMP/tests/test_v266_frontier_producer_admission.py"
"$PYTHON" "$TMP/tests/test_v267_data_capability_supersession.py"
"$PYTHON" "$TMP/tests/test_v268_volume_tsmom_ablation.py"

"$PYTHON" - "$TMP/strategy_lab_controller.py" <<'PY'
import importlib.util
import sys

path = sys.argv[1]
spec = importlib.util.spec_from_file_location('tdh_v268_stage_smoke', path)
if spec is None or spec.loader is None:
    raise SystemExit('BLOCKED: v2.0.68 controller import failed')
module = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = module
spec.loader.exec_module(module)

contract = module.runtime_binding_contract()
assert contract['v265_raw_inbox_count_is_not_actionable_capacity'] is True
assert contract['v265_reviewed_registry_is_controller_owned'] is True
assert contract['v265_duplicate_and_registered_proposals_are_terminal'] is True
assert contract['v265_invalid_inbox_fails_closed'] is True
assert contract['v265_pending_implementation_blocks_paid_scout'] is True
assert contract['v265_raw_proposals_are_preserved'] is True
assert contract['v265_untrusted_text_never_executes'] is True
assert contract['v266_one_proposal_per_bounded_epoch'] is True
assert contract['v266_exact_registered_family_identity_only'] is True
assert contract['v266_installed_offline_data_only'] is True
assert contract['v266_candidate_baseline_negative_control_required'] is True
assert contract['v266_raw_proposal_never_executes'] is True
assert contract['v266_sealed_registry_change_required'] is True
assert contract['v266_provider_blocked_while_implementation_pending'] is True
assert contract['v267_ohlcv_derivations_are_not_external_data'] is True
assert contract['v267_external_data_requirements_fail_closed'] is True
assert contract['v267_ambiguous_data_requires_review'] is True
assert contract['v267_legacy_decisions_are_preserved'] is True
assert contract['v267_hash_bound_supersession'] is True
assert contract['v267_one_decision_or_migration_per_epoch'] is True
assert contract['v268_source_proposal_hash_bound'] is True
assert contract['v268_source_decision_hash_bound'] is True
assert contract['v268_candidate_baseline_negative_control_bound'] is True
assert contract['v268_causal_volume_shuffle_only'] is True
assert contract['v268_raw_proposal_never_executes'] is True
assert contract['v268_s1_only'] is True
assert contract['controller_only_recovery_policy'] is True
assert contract['policy_change'] is False
assert contract['trading_actions'] is False
assert contract['exchange_api_access'] is False
print('V268_VOLUME_TSMOM_ABLATION_SMOKE_OK')
PY

echo "===== 5. PUBLISH STAGING ATOMICALLY ====="
mv -- "$TMP" "$DST"

sha256sum \
    "$DST/strategy_lab_controller.py" \
    "$DST/research/research_kernel.py" \
    "$DST/research/v268-volume-tsmom-ablation-seeds-v1.jsonl" \
    "$DST/adapter/tdh_strategy_lab_research_adapter.py" \
    "$DST/tests/test_v268_volume_tsmom_ablation.py" \
    "$DST/tests/test_v265_frontier_inbox_lifecycle.py" \
    "$DST/tests/test_v266_frontier_producer_admission.py" \
    "$DST/tests/test_v267_data_capability_supersession.py"

echo "SERVICE_STATE=$(systemctl is-active "$SERVICE" || true)"
echo "TDH_V268_STAGE_COMPLETE"
