#!/usr/bin/env bash
set -Eeuo pipefail

SERVICE="strategy-lab-supervisor-v2.1.service"
BASE="/srv/tdh-collab/controller/strategy-lab-v2"
STAGING="$BASE/staging/v2.0.68"
REPO="/home/tdw/the-darkest-hour"
SOURCE="$REPO/controller/staging/v2.0.68"
PYTHON="/srv/tdh-research/phoenix-venv/bin/python"
STAMP="$$"
ADAPTER_TMP="$STAGING/adapter/.tdh_strategy_lab_research_adapter.py.v268-compat-$STAMP"
TEST_TMP="$STAGING/tests/.test_v268_volume_tsmom_ablation.py.v268-compat-$STAMP"

OLD_ADAPTER_SHA256="df6357b6dd6ef1c13641fabd03ab126253d8f3eba8545dcb590c42f6ad0390cd"
OLD_TEST_SHA256="5a6ab0dd8bc3ca24875196cddf3155146c8a500acae61aa82e2e580da01b1057"
NEW_ADAPTER_SHA256="29392dfa12d2581075fcba12416d0f3352e7f4f6cec7d0483c181d4d0e663e68"
NEW_TEST_SHA256="290b36ac9243b131878d8cb1c48d8344258c197e7015c3e1e7b7c9baf453a9f7"

cleanup() {
    rm -f -- "$ADAPTER_TMP" "$TEST_TMP"
}
trap cleanup EXIT

echo "===== 1. KEEP UNSEALED v2.0.68 STOPPED ====="
systemctl mask --runtime --now "$SERVICE" || true
test "$(systemctl is-active "$SERVICE" || true)" != "active"
test -d "$STAGING"
test ! -e "$STAGING/SHA256SUMS"

echo "===== 2. VERIFY EXACT CURRENT STAGING ====="
echo "$OLD_ADAPTER_SHA256  $STAGING/adapter/tdh_strategy_lab_research_adapter.py" | sha256sum -c -
echo "$OLD_TEST_SHA256  $STAGING/tests/test_v268_volume_tsmom_ablation.py" | sha256sum -c -

echo "===== 3. VERIFY CORRECTED REPOSITORY SOURCES ====="
case "$(git -C "$REPO" branch --show-current)" in
    main|agent/v2-0-68-volume-tsmom-ablation) ;;
    *) echo "BLOCKED: unexpected repository branch"; exit 4 ;;
esac
test ! -L "$SOURCE/adapter/tdh_strategy_lab_research_adapter.py"
test ! -L "$SOURCE/tests/test_v268_volume_tsmom_ablation.py"
echo "$NEW_ADAPTER_SHA256  $SOURCE/adapter/tdh_strategy_lab_research_adapter.py" | sha256sum -c -
echo "$NEW_TEST_SHA256  $SOURCE/tests/test_v268_volume_tsmom_ablation.py" | sha256sum -c -

echo "===== 4. APPLY ATOMIC TEST-COMPATIBILITY FIX ====="
install -m 0644 -- "$SOURCE/adapter/tdh_strategy_lab_research_adapter.py" "$ADAPTER_TMP"
install -m 0644 -- "$SOURCE/tests/test_v268_volume_tsmom_ablation.py" "$TEST_TMP"
echo "$NEW_ADAPTER_SHA256  $ADAPTER_TMP" | sha256sum -c -
echo "$NEW_TEST_SHA256  $TEST_TMP" | sha256sum -c -
mv -f -- "$ADAPTER_TMP" "$STAGING/adapter/tdh_strategy_lab_research_adapter.py"
mv -f -- "$TEST_TMP" "$STAGING/tests/test_v268_volume_tsmom_ablation.py"

echo "===== 5. VERIFY CORRECTED STAGING ====="
echo "$NEW_ADAPTER_SHA256  $STAGING/adapter/tdh_strategy_lab_research_adapter.py" | sha256sum -c -
echo "$NEW_TEST_SHA256  $STAGING/tests/test_v268_volume_tsmom_ablation.py" | sha256sum -c -
"$PYTHON" -m py_compile \
    "$STAGING/adapter/tdh_strategy_lab_research_adapter.py" \
    "$STAGING/tests/test_v268_volume_tsmom_ablation.py"
python3 "$STAGING/tests/test_v268_volume_tsmom_ablation.py"
python3 - "$STAGING/adapter/tdh_strategy_lab_research_adapter.py" <<'PY'
from pathlib import Path
import sys

source = Path(sys.argv[1]).read_text(encoding='utf-8')
assert 'REFERENCE_INITIAL_CAPITAL_USD = 20_000.0' in source
assert 'ACCOUNTING_BASIS = "REFERENCE_CAPITAL_REPORTING_ONLY"' in source
assert '"reference_capital_reporting_only": True' in source
assert 'v221.hard_target_pass = hard_target_pass' in source
print('V268_INHERITED_SOURCE_CONTRACT_OK')
PY

echo "SERVICE_STATE=$(systemctl is-active "$SERVICE" || true)"
echo "TDH_V268_TEST_COMPATIBILITY_SYNC_COMPLETE"
