#!/usr/bin/env bash
set -Eeuo pipefail

SERVICE="strategy-lab-supervisor-v2.1.service"
BASE="/srv/tdh-collab/controller/strategy-lab-v2"
SRC="$BASE/v2.0.66"
DST="$BASE/staging/v2.0.67"
TMP="$BASE/staging/.v2.0.67-build-$$"
REPO="/home/tdw/the-darkest-hour"
REPO_SOURCE="$REPO/controller/staging/v2.0.67"
GATE="/usr/local/sbin/tdh-lab-admin-gate"
PYTHON="/srv/tdh-research/phoenix-venv/bin/python"

EXPECTED_CONTROLLER_SHA256="931975b5dbe68d537b60f75adb360af5473183a8039e378cc0516014ebf6d2b5"
EXPECTED_TEST_SHA256="65cfbc292ca068477361da397b97919e02ab9e15773c8085eac6ed6f5a63541c"
EXPECTED_V266_TEST_SHA256="ebea3780c4d8c30b355b137f27ad73ee5daa510b3df9469475a63904d6f8d6e6"
EXPECTED_LEGACY_TEST_SHA256="ff68dfd372fb3c73de8c4126f7d30703d40286f0349f65bbb02af9a64e1fcae3"

cleanup() {
    if [[ -d "$TMP" && "$TMP" == "$BASE/staging/.v2.0.67-build-"* ]]; then
        rm -rf --one-file-system "$TMP"
    fi
}
trap cleanup EXIT

echo "===== 1. STOP AND BLOCK v2.0.66 DURING UPGRADE ====="
systemctl mask --runtime --now "$SERVICE" || true
sleep 1
test "$(systemctl is-active "$SERVICE" || true)" != "active"

echo "===== 2. VERIFY SEALED v2.0.66 ====="
test -d "$SRC"
test -f "$SRC/SHA256SUMS"
(
    cd "$SRC"
    sha256sum -c SHA256SUMS >/dev/null
)
"$GATE" preflight v2.0.66 >/tmp/tdh-v2.0.66-before-v267-preflight.log
grep -q '"status": "PREFLIGHT_OK"' /tmp/tdh-v2.0.66-before-v267-preflight.log

echo "===== 3. VERIFY REPOSITORY SOURCES ====="
REPO_BRANCH="$(git -C "$REPO" branch --show-current)"
case "$REPO_BRANCH" in
    main|agent/v2-0-67-data-capability-supersession) ;;
    *)
        echo "BLOCKED: unexpected repository branch: $REPO_BRANCH"
        exit 4
        ;;
esac
test -f "$REPO_SOURCE/strategy_lab_controller.py"
test -f "$REPO_SOURCE/tests/test_v266_frontier_producer_admission.py"
test -f "$REPO_SOURCE/tests/test_v265_frontier_inbox_lifecycle.py"
test -f "$REPO_SOURCE/tests/test_v267_data_capability_supersession.py"
test ! -L "$REPO_SOURCE/strategy_lab_controller.py"
test ! -L "$REPO_SOURCE/tests/test_v266_frontier_producer_admission.py"
test ! -L "$REPO_SOURCE/tests/test_v265_frontier_inbox_lifecycle.py"
test ! -L "$REPO_SOURCE/tests/test_v267_data_capability_supersession.py"
echo "$EXPECTED_CONTROLLER_SHA256  $REPO_SOURCE/strategy_lab_controller.py" | sha256sum -c -
echo "$EXPECTED_TEST_SHA256  $REPO_SOURCE/tests/test_v267_data_capability_supersession.py" | sha256sum -c -
echo "$EXPECTED_V266_TEST_SHA256  $REPO_SOURCE/tests/test_v266_frontier_producer_admission.py" | sha256sum -c -
echo "$EXPECTED_LEGACY_TEST_SHA256  $REPO_SOURCE/tests/test_v265_frontier_inbox_lifecycle.py" | sha256sum -c -

if [[ -e "$DST" ]]; then
    echo "BLOCKED: staging destination already exists: $DST"
    exit 3
fi

echo "===== 4. BUILD v2.0.67 STAGING ====="
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
    "$REPO_SOURCE/tests/test_v266_frontier_producer_admission.py" \
    "$TMP/tests/test_v266_frontier_producer_admission.py"
install -T -m 0644 -- \
    "$REPO_SOURCE/tests/test_v265_frontier_inbox_lifecycle.py" \
    "$TMP/tests/test_v265_frontier_inbox_lifecycle.py"
install -T -m 0644 -- \
    "$REPO_SOURCE/tests/test_v267_data_capability_supersession.py" \
    "$TMP/tests/test_v267_data_capability_supersession.py"

"$PYTHON" -m py_compile \
    "$TMP/strategy_lab_controller.py" \
    "$TMP/tests/test_v265_frontier_inbox_lifecycle.py" \
    "$TMP/tests/test_v266_frontier_producer_admission.py" \
    "$TMP/tests/test_v267_data_capability_supersession.py"

"$PYTHON" "$TMP/tests/test_v265_frontier_inbox_lifecycle.py"
"$PYTHON" "$TMP/tests/test_v266_frontier_producer_admission.py"
"$PYTHON" "$TMP/tests/test_v267_data_capability_supersession.py"

"$PYTHON" - "$TMP/strategy_lab_controller.py" <<'PY'
import importlib.util
import sys

path = sys.argv[1]
spec = importlib.util.spec_from_file_location('tdh_v267_stage_smoke', path)
if spec is None or spec.loader is None:
    raise SystemExit('BLOCKED: v2.0.67 controller import failed')
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
assert contract['controller_only_recovery_policy'] is True
assert contract['policy_change'] is False
assert contract['trading_actions'] is False
assert contract['exchange_api_access'] is False
print('V267_DATA_CAPABILITY_SUPERSESSION_SMOKE_OK')
PY

echo "===== 5. PUBLISH STAGING ATOMICALLY ====="
mv -- "$TMP" "$DST"

sha256sum \
    "$DST/strategy_lab_controller.py" \
    "$DST/tests/test_v265_frontier_inbox_lifecycle.py" \
    "$DST/tests/test_v266_frontier_producer_admission.py" \
    "$DST/tests/test_v267_data_capability_supersession.py"

echo "SERVICE_STATE=$(systemctl is-active "$SERVICE" || true)"
echo "TDH_V267_STAGE_COMPLETE"
