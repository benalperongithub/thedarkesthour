#!/usr/bin/env bash
set -Eeuo pipefail

SERVICE="strategy-lab-supervisor-v2.1.service"
BASE="/srv/tdh-collab/controller/strategy-lab-v2"
SRC="$BASE/v2.0.70"
DST="$BASE/staging/v2.0.71"
TMP="$BASE/staging/.v2.0.71-build-$$"
REPO="/home/tdw/the-darkest-hour"
REPO_SOURCE="$REPO/controller/staging/v2.0.71"
GATE="/usr/local/sbin/tdh-lab-admin-gate"
PYTHON="/srv/tdh-research/phoenix-venv/bin/python"

EXPECTED_CONTROLLER_SHA256="ee948abdb1b7354d6d4ce09dc7a014739dacbf9d5fe507bcd25d7874ceca0923"
EXPECTED_V270_TEST_SHA256="275cce76cfa17c1b4187887fa6c6159c2e57906bb3a7ebd4a035b2e6a6d46996"
EXPECTED_V271_TEST_SHA256="82793f1036a68725f05d5657961411d54ca47bf9581136edc475e39e21464877"

cleanup() {
    if [[ -d "$TMP" && "$TMP" == "$BASE/staging/.v2.0.71-build-"* ]]; then
        rm -rf --one-file-system "$TMP"
    fi
}
trap cleanup EXIT

echo "===== 1. STOP AND BLOCK v2.0.70 DURING UPGRADE ====="
systemctl mask --runtime --now "$SERVICE" || true
sleep 1
test "$(systemctl is-active "$SERVICE" || true)" != "active"

echo "===== 2. VERIFY SEALED v2.0.70 ====="
test -d "$SRC"
test -f "$SRC/SHA256SUMS"
(
    cd "$SRC"
    sha256sum -c SHA256SUMS >/dev/null
)
"$GATE" preflight v2.0.70 >/tmp/tdh-v2.0.70-before-v271-preflight.log
grep -q '"status": "PREFLIGHT_OK"' /tmp/tdh-v2.0.70-before-v271-preflight.log

echo "===== 3. VERIFY REPOSITORY SOURCES ====="
REPO_BRANCH="$(git -C "$REPO" branch --show-current)"
case "$REPO_BRANCH" in
    main|agent/v2-0-71-quarantine-carrier) ;;
    *)
        echo "BLOCKED: unexpected repository branch: $REPO_BRANCH"
        exit 4
        ;;
esac
test -f "$REPO_SOURCE/strategy_lab_controller.py"
test -f "$REPO_SOURCE/tests/test_v270_pre_exhaustion_bridge.py"
test -f "$REPO_SOURCE/tests/test_v271_quarantine_carrier.py"
test ! -L "$REPO_SOURCE/strategy_lab_controller.py"
test ! -L "$REPO_SOURCE/tests/test_v270_pre_exhaustion_bridge.py"
test ! -L "$REPO_SOURCE/tests/test_v271_quarantine_carrier.py"
echo "$EXPECTED_CONTROLLER_SHA256  $REPO_SOURCE/strategy_lab_controller.py" | sha256sum -c -
echo "$EXPECTED_V270_TEST_SHA256  $REPO_SOURCE/tests/test_v270_pre_exhaustion_bridge.py" | sha256sum -c -
echo "$EXPECTED_V271_TEST_SHA256  $REPO_SOURCE/tests/test_v271_quarantine_carrier.py" | sha256sum -c -

if [[ -e "$DST" ]]; then
    echo "BLOCKED: staging destination already exists: $DST"
    exit 3
fi

echo "===== 4. BUILD v2.0.71 STAGING ====="
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
    "$REPO_SOURCE/tests/test_v270_pre_exhaustion_bridge.py" \
    "$TMP/tests/test_v270_pre_exhaustion_bridge.py"
install -T -m 0644 -- \
    "$REPO_SOURCE/tests/test_v271_quarantine_carrier.py" \
    "$TMP/tests/test_v271_quarantine_carrier.py"

"$PYTHON" -m py_compile \
    "$TMP/strategy_lab_controller.py" \
    "$TMP/tests/test_v265_frontier_inbox_lifecycle.py" \
    "$TMP/tests/test_v266_frontier_producer_admission.py" \
    "$TMP/tests/test_v267_data_capability_supersession.py" \
    "$TMP/tests/test_v268_volume_tsmom_ablation.py" \
    "$TMP/tests/test_v269_reviewed_seed_queue.py" \
    "$TMP/tests/test_v270_pre_exhaustion_bridge.py" \
    "$TMP/tests/test_v271_quarantine_carrier.py"

"$PYTHON" "$TMP/tests/test_v265_frontier_inbox_lifecycle.py"
"$PYTHON" "$TMP/tests/test_v266_frontier_producer_admission.py"
"$PYTHON" "$TMP/tests/test_v267_data_capability_supersession.py"
"$PYTHON" "$TMP/tests/test_v268_volume_tsmom_ablation.py"
"$PYTHON" "$TMP/tests/test_v269_reviewed_seed_queue.py"
"$PYTHON" "$TMP/tests/test_v270_pre_exhaustion_bridge.py"
"$PYTHON" "$TMP/tests/test_v271_quarantine_carrier.py"

"$PYTHON" - "$TMP/strategy_lab_controller.py" <<'PY'
import importlib.util
import sys

path = sys.argv[1]
spec = importlib.util.spec_from_file_location('tdh_v271_stage_smoke', path)
if spec is None or spec.loader is None:
    raise SystemExit('BLOCKED: v2.0.71 controller import failed')
module = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = module
spec.loader.exec_module(module)

contract = module.runtime_binding_contract()
assert contract['v268_source_proposal_hash_bound'] is True
assert contract['v268_source_decision_hash_bound'] is True
assert contract['v268_candidate_baseline_negative_control_bound'] is True
assert contract['v268_causal_volume_shuffle_only'] is True
assert contract['v268_raw_proposal_never_executes'] is True
assert contract['v268_s1_only'] is True
assert contract['v269_reviewed_seed_queue_version'] == (
    module.V269_REVIEWED_SEED_QUEUE_VERSION
)
assert contract['v269_exact_reviewed_seed_precedes_frontier_exhaustion'] is True
assert contract['v269_deterministic_priority_and_deduplication'] is True
assert contract['v269_single_axis_symbol_bridge_preserves_transition_gate'] is True
assert contract['v269_untrusted_text_never_enters_reviewed_queue'] is True
assert contract['v269_s1_only'] is True
assert contract['v270_pre_exhaustion_bridge_version'] == (
    module.V270_PRE_EXHAUSTION_BRIDGE_VERSION
)
assert contract['v270_codex_structural_exhaustion_becomes_reviewable_empty_frontier'] is True
assert contract['v270_reviewed_seed_replenishment_runs_before_v252_rollover'] is True
assert contract['v270_claude_peer_semantics_unchanged'] is True
assert contract['v270_unknown_errors_fail_closed'] is True
assert contract['v271_quarantine_carrier_version'] == (
    module.V271_QUARANTINE_CARRIER_VERSION
)
assert contract['v271_exact_registered_carrier_only'] is True
assert contract['v271_carrier_removed_before_provider'] is True
assert contract['v271_structural_quarantine_preserved'] is True
assert contract['v271_v230_nonempty_guard_precedes_reviewed_admission'] is True
assert contract['v271_unknown_errors_fail_closed'] is True
assert contract['controller_only_recovery_policy'] is True
assert contract['policy_change'] is False
assert contract['trading_actions'] is False
assert contract['exchange_api_access'] is False
print('V271_QUARANTINE_CARRIER_SMOKE_OK')
PY

echo "===== 5. PUBLISH STAGING ATOMICALLY ====="
mv -- "$TMP" "$DST"

sha256sum \
    "$DST/strategy_lab_controller.py" \
    "$DST/tests/test_v270_pre_exhaustion_bridge.py" \
    "$DST/tests/test_v271_quarantine_carrier.py"

echo "SERVICE_STATE=$(systemctl is-active "$SERVICE" || true)"
echo "TDH_V271_STAGE_COMPLETE"
