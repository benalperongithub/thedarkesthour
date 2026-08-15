#!/usr/bin/env bash
set -Eeuo pipefail

SERVICE="strategy-lab-supervisor-v2.1.service"
BASE="/srv/tdh-collab/controller/strategy-lab-v2"
STAGE="$BASE/staging/v2.0.61"
REPO="/home/tdw/the-darkest-hour"
REPO_SOURCE="$REPO/controller/staging/v2.0.61"
PYTHON="/srv/tdh-research/phoenix-venv/bin/python"

OLD_ADAPTER_SHA256="1a1f7c29adfedb86639c91ce854a9837340b676eb6384dd1229b97f0665982c0"
OLD_TEST_SHA256="56e324a196037704a8a1f55577c63c00ac77034bc8d351974414ea3a9f8f4cce"
NEW_ADAPTER_SHA256="9d69355d028a471277420e7f1c8a0c79140023672682e300e60a475ded8ba386"
NEW_TEST_SHA256="6d98b7f7d0285e554a566c90e5a62dabac090bd7415a5cd7066bd1d76ab45aaa"

TMP=""
ROLLBACK_READY=0
COMMITTED=0

cleanup() {
    status=$?
    if [[ "$status" -ne 0 && "$ROLLBACK_READY" -eq 1 && "$COMMITTED" -eq 0 ]]; then
        install -T -m 0644 -- "$TMP/old-adapter.py" \
            "$STAGE/adapter/tdh_strategy_lab_research_adapter.py"
        install -T -m 0644 -- "$TMP/old-test.py" \
            "$STAGE/tests/test_v261_rsi_gated_reversion.py"
        echo "ROLLBACK_COMPLETE"
    fi
    if [[ -n "$TMP" && -d "$TMP" && "$TMP" == "$STAGE/.v261-seal-compat."* ]]; then
        rm -rf --one-file-system "$TMP"
    fi
    exit "$status"
}
trap cleanup EXIT

echo "===== 1. KEEP UNSEALED v2.0.61 STOPPED ====="
systemctl mask --runtime --now "$SERVICE" || true
sleep 1
test "$(systemctl is-active "$SERVICE" || true)" != "active"

echo "===== 2. VERIFY EXACT UNSEALED STAGING ====="
test -d "$STAGE"
test ! -e "$STAGE/SHA256SUMS"
test "$(git -C "$REPO" branch --show-current)" = "main"
test -x "$PYTHON"

for path in \
    "$STAGE/adapter/tdh_strategy_lab_research_adapter.py" \
    "$STAGE/tests/test_v261_rsi_gated_reversion.py" \
    "$REPO_SOURCE/adapter/tdh_strategy_lab_research_adapter.py" \
    "$REPO_SOURCE/tests/test_v261_rsi_gated_reversion.py"
do
    test -f "$path"
    test ! -L "$path"
done

echo "$OLD_ADAPTER_SHA256  $STAGE/adapter/tdh_strategy_lab_research_adapter.py" | sha256sum -c -
echo "$OLD_TEST_SHA256  $STAGE/tests/test_v261_rsi_gated_reversion.py" | sha256sum -c -
echo "$NEW_ADAPTER_SHA256  $REPO_SOURCE/adapter/tdh_strategy_lab_research_adapter.py" | sha256sum -c -
echo "$NEW_TEST_SHA256  $REPO_SOURCE/tests/test_v261_rsi_gated_reversion.py" | sha256sum -c -

echo "===== 3. PREPARE ATOMIC COMPATIBILITY SYNC ====="
TMP="$(mktemp -d "$STAGE/.v261-seal-compat.XXXXXX")"
install -m 0644 -- "$STAGE/adapter/tdh_strategy_lab_research_adapter.py" "$TMP/old-adapter.py"
install -m 0644 -- "$STAGE/tests/test_v261_rsi_gated_reversion.py" "$TMP/old-test.py"
install -m 0644 -- "$REPO_SOURCE/adapter/tdh_strategy_lab_research_adapter.py" "$TMP/new-adapter.py"
install -m 0644 -- "$REPO_SOURCE/tests/test_v261_rsi_gated_reversion.py" "$TMP/new-test.py"
ROLLBACK_READY=1

"$PYTHON" -m py_compile "$TMP/new-adapter.py" "$TMP/new-test.py"

echo "===== 4. APPLY AND VERIFY ====="
mv -f -- "$TMP/new-adapter.py" "$STAGE/adapter/tdh_strategy_lab_research_adapter.py"
mv -f -- "$TMP/new-test.py" "$STAGE/tests/test_v261_rsi_gated_reversion.py"

echo "$NEW_ADAPTER_SHA256  $STAGE/adapter/tdh_strategy_lab_research_adapter.py" | sha256sum -c -
echo "$NEW_TEST_SHA256  $STAGE/tests/test_v261_rsi_gated_reversion.py" | sha256sum -c -

"$PYTHON" "$STAGE/tests/test_v261_rsi_gated_reversion.py"

COMMITTED=1
echo "SERVICE_STATE=$(systemctl is-active "$SERVICE" || true)"
echo "TDH_V261_SEAL_GATE_COMPATIBILITY_SYNC_COMPLETE"
