#!/usr/bin/env bash
set -Eeuo pipefail

SERVICE="strategy-lab-supervisor-v2.1.service"
BASE="/srv/tdh-collab/controller/strategy-lab-v2"
SRC="$BASE/v2.0.60"
DST="$BASE/staging/v2.0.61"
TMP="$BASE/staging/.v2.0.61-build-$$"
REPO="/home/tdw/the-darkest-hour"
REPO_SOURCE="$REPO/controller/staging/v2.0.61"
GATE="/usr/local/sbin/tdh-lab-admin-gate"
PYTHON="/srv/tdh-research/phoenix-venv/bin/python"

EXPECTED_CONTROLLER_SHA256="2f532755823cf78d091b05eee020a7b3719669e58aeb97f68831704678a90103"
EXPECTED_KERNEL_SHA256="8ef579d433586a9575a3b2de9110eaad1cb328bed0937a0f70926bba6f94ce71"
EXPECTED_ADAPTER_SHA256="9d69355d028a471277420e7f1c8a0c79140023672682e300e60a475ded8ba386"
EXPECTED_SEEDS_SHA256="c3567832b09df7aa8898da03110a40e4ef0c2d8f5a18076f980aeb6d2506c5f8"
EXPECTED_TEST_SHA256="6d98b7f7d0285e554a566c90e5a62dabac090bd7415a5cd7066bd1d76ab45aaa"

cleanup() {
    if [[ -d "$TMP" && "$TMP" == "$BASE/staging/.v2.0.61-build-"* ]]; then
        rm -rf --one-file-system "$TMP"
    fi
}
trap cleanup EXIT

echo "===== 1. STOP AND BLOCK v2.0.60 DURING UPGRADE ====="
systemctl mask --runtime --now "$SERVICE" || true
sleep 1
test "$(systemctl is-active "$SERVICE" || true)" != "active"

echo "===== 2. VERIFY SEALED v2.0.60 ====="
test -d "$SRC"
test -f "$SRC/SHA256SUMS"
(
    cd "$SRC"
    sha256sum -c SHA256SUMS >/dev/null
)
"$GATE" preflight v2.0.60 >/tmp/tdh-v2.0.60-before-v261-preflight.log
grep -q '"status": "PREFLIGHT_OK"' /tmp/tdh-v2.0.60-before-v261-preflight.log

echo "===== 3. VERIFY REPOSITORY SOURCES ====="
test "$(git -C "$REPO" branch --show-current)" = "main"
echo "$EXPECTED_CONTROLLER_SHA256  $REPO_SOURCE/strategy_lab_controller.py" | sha256sum -c -
echo "$EXPECTED_KERNEL_SHA256  $REPO_SOURCE/research/research_kernel.py" | sha256sum -c -
echo "$EXPECTED_ADAPTER_SHA256  $REPO_SOURCE/adapter/tdh_strategy_lab_research_adapter.py" | sha256sum -c -
echo "$EXPECTED_SEEDS_SHA256  $REPO_SOURCE/research/rsi-gated-reversion-seeds-v1.jsonl" | sha256sum -c -
echo "$EXPECTED_TEST_SHA256  $REPO_SOURCE/tests/test_v261_rsi_gated_reversion.py" | sha256sum -c -

if [[ -e "$DST" ]]; then
    echo "BLOCKED: staging destination already exists: $DST"
    exit 3
fi

echo "===== 4. BUILD v2.0.61 STAGING ====="
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
    "$REPO_SOURCE/research/rsi-gated-reversion-seeds-v1.jsonl" \
    "$TMP/research/rsi-gated-reversion-seeds-v1.jsonl"
install -T -m 0644 -- \
    "$REPO_SOURCE/adapter/tdh_strategy_lab_research_adapter.py" \
    "$TMP/adapter/tdh_strategy_lab_research_adapter.py"
install -T -m 0644 -- \
    "$REPO_SOURCE/tests/test_v261_rsi_gated_reversion.py" \
    "$TMP/tests/test_v261_rsi_gated_reversion.py"

"$PYTHON" -m py_compile \
    "$TMP/strategy_lab_controller.py" \
    "$TMP/research/research_kernel.py" \
    "$TMP/adapter/tdh_strategy_lab_research_adapter.py" \
    "$TMP/tests/test_v261_rsi_gated_reversion.py"

"$PYTHON" "$TMP/tests/test_v261_rsi_gated_reversion.py"

"$PYTHON" - "$TMP/strategy_lab_controller.py" <<'PY'
import importlib.util
import sys

path = sys.argv[1]
spec = importlib.util.spec_from_file_location('tdh_v261_stage_smoke', path)
if spec is None or spec.loader is None:
    raise SystemExit('BLOCKED: v2.0.61 controller import failed')
module = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = module
spec.loader.exec_module(module)

contract = module.runtime_binding_contract()
assert contract['v259_runtime_kernel_overlay_bound'] is True
assert contract['v260_spoofed_or_freeform_seed_transition_fails_closed'] is True
assert contract['v261_only_reviewed_packet_a_is_auto_admitted'] is True
assert contract['v261_candidate_baseline_negative_control_bound'] is True
assert contract['v261_closed_bar_only'] is True
assert contract['v261_s1_only'] is True
assert contract['v261_scout_capacity_checked_before_provider'] is True
assert contract['v261_full_inbox_never_invokes_provider'] is True
assert contract['v261_frontier_rollover_usage_accounted'] is True
assert contract['controller_only_promotion'] is True
assert contract['trading_actions'] is False
assert contract['exchange_api_access'] is False

status = module.kernel.v261_registry_status()
assert status['seed_count'] == 1
assert status['family_registered'] is True
assert status['experiment_registered'] is True
assert status['trading_actions'] is False
assert status['exchange_api_access'] is False
print('V261_RSI_GATED_REVERSION_SMOKE_OK')
PY

echo "===== 5. PUBLISH STAGING ATOMICALLY ====="
mv -- "$TMP" "$DST"

sha256sum \
    "$DST/strategy_lab_controller.py" \
    "$DST/research/research_kernel.py" \
    "$DST/research/rsi-gated-reversion-seeds-v1.jsonl" \
    "$DST/adapter/tdh_strategy_lab_research_adapter.py" \
    "$DST/tests/test_v261_rsi_gated_reversion.py"

echo "SERVICE_STATE=$(systemctl is-active "$SERVICE" || true)"
echo "TDH_V261_STAGE_COMPLETE"
