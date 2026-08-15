#!/usr/bin/env bash
set -Eeuo pipefail

SERVICE="strategy-lab-supervisor-v2.1.service"
BASE="/srv/tdh-collab/controller/strategy-lab-v2"
SRC="$BASE/v2.0.62"
DST="$BASE/staging/v2.0.63"
TMP="$BASE/staging/.v2.0.63-build-$$"
REPO="/home/tdw/the-darkest-hour"
REPO_SOURCE="$REPO/controller/staging/v2.0.63"
GATE="/usr/local/sbin/tdh-lab-admin-gate"
PYTHON="/srv/tdh-research/phoenix-venv/bin/python"

EXPECTED_CONTROLLER_SHA256="8e60c12a724dc2c8d9a946e22af8c9144f0e2e8117f1030404134dd8d93cd73d"
EXPECTED_TEST_SHA256="907168a5afcade5d5b6137ef7f3e97e1e122033f457a39a10bb27aeb38f897de"

cleanup() {
    if [[ -d "$TMP" && "$TMP" == "$BASE/staging/.v2.0.63-build-"* ]]; then
        rm -rf --one-file-system "$TMP"
    fi
}
trap cleanup EXIT

echo "===== 1. STOP AND BLOCK v2.0.62 DURING UPGRADE ====="
systemctl mask --runtime --now "$SERVICE" || true
sleep 1
test "$(systemctl is-active "$SERVICE" || true)" != "active"

echo "===== 2. VERIFY SEALED v2.0.62 ====="
test -d "$SRC"
test -f "$SRC/SHA256SUMS"
(
    cd "$SRC"
    sha256sum -c SHA256SUMS >/dev/null
)
"$GATE" preflight v2.0.62 >/tmp/tdh-v2.0.62-before-v263-preflight.log
grep -q '"status": "PREFLIGHT_OK"' /tmp/tdh-v2.0.62-before-v263-preflight.log

echo "===== 3. VERIFY REPOSITORY SOURCES ====="
test "$(git -C "$REPO" branch --show-current)" = "main"
test -f "$REPO_SOURCE/strategy_lab_controller.py"
test -f "$REPO_SOURCE/tests/test_v263_checkpoint_resume.py"
test ! -L "$REPO_SOURCE/strategy_lab_controller.py"
test ! -L "$REPO_SOURCE/tests/test_v263_checkpoint_resume.py"
echo "$EXPECTED_CONTROLLER_SHA256  $REPO_SOURCE/strategy_lab_controller.py" | sha256sum -c -
echo "$EXPECTED_TEST_SHA256  $REPO_SOURCE/tests/test_v263_checkpoint_resume.py" | sha256sum -c -

if [[ -e "$DST" ]]; then
    echo "BLOCKED: staging destination already exists: $DST"
    exit 3
fi

echo "===== 4. BUILD v2.0.63 STAGING ====="
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
    "$REPO_SOURCE/tests/test_v263_checkpoint_resume.py" \
    "$TMP/tests/test_v263_checkpoint_resume.py"

"$PYTHON" -m py_compile \
    "$TMP/strategy_lab_controller.py" \
    "$TMP/tests/test_v263_checkpoint_resume.py"

/usr/bin/python3 "$TMP/tests/test_v263_checkpoint_resume.py"

"$PYTHON" - "$TMP/strategy_lab_controller.py" <<'PY'
import importlib.util
import sys

path = sys.argv[1]
spec = importlib.util.spec_from_file_location('tdh_v263_stage_smoke', path)
if spec is None or spec.loader is None:
    raise SystemExit('BLOCKED: v2.0.63 controller import failed')
module = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = module
spec.loader.exec_module(module)

contract = module.runtime_binding_contract()
assert contract['v263_node_level_checkpoints'] is True
assert contract['v263_exact_input_hash_resume_only'] is True
assert contract['v263_payload_hash_verified'] is True
assert contract['v263_interrupted_nodes_fail_closed'] is True
assert contract['v263_controller_only_resume'] is True
assert contract['v263_automatic_retry_authorized'] is False
assert contract['controller_only_recovery_policy'] is True
assert contract['policy_change'] is False
assert contract['trading_actions'] is False
assert contract['exchange_api_access'] is False
print('V263_CHECKPOINT_RESUME_SMOKE_OK')
PY

echo "===== 5. PUBLISH STAGING ATOMICALLY ====="
mv -- "$TMP" "$DST"

sha256sum \
    "$DST/strategy_lab_controller.py" \
    "$DST/tests/test_v263_checkpoint_resume.py"

echo "SERVICE_STATE=$(systemctl is-active "$SERVICE" || true)"
echo "TDH_V263_STAGE_COMPLETE"
