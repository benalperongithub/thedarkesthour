#!/usr/bin/env bash
set -Eeuo pipefail

SERVICE="strategy-lab-supervisor-v2.1.service"
BASE="/srv/tdh-collab/controller/strategy-lab-v2"
SRC="$BASE/v2.0.63"
DST="$BASE/staging/v2.0.64"
TMP="$BASE/staging/.v2.0.64-build-$$"
REPO="/home/tdw/the-darkest-hour"
REPO_SOURCE="$REPO/controller/staging/v2.0.64"
GATE="/usr/local/sbin/tdh-lab-admin-gate"
PYTHON="/srv/tdh-research/phoenix-venv/bin/python"

EXPECTED_CONTROLLER_SHA256="7d4e569eb9b22c12ced572a3d68b1d8315a732157cfbe9f6f47c22635eb19051"
EXPECTED_TEST_SHA256="4ae499ac103cf2f936bc3617a121b339def273644c8f349d64c04c32a4c147f3"
EXPECTED_V263_COMPAT_TEST_SHA256="50df69141239a9c6f063a41a4a3b16e0e13b0e5f1bf3cd093d396b6d5b1543b4"

cleanup() {
    if [[ -d "$TMP" && "$TMP" == "$BASE/staging/.v2.0.64-build-"* ]]; then
        rm -rf --one-file-system "$TMP"
    fi
}
trap cleanup EXIT

echo "===== 1. KEEP FAILED v2.0.63 RUNTIME STOPPED ====="
systemctl mask --runtime --now "$SERVICE" || true
sleep 1
test "$(systemctl is-active "$SERVICE" || true)" != "active"

echo "===== 2. VERIFY SEALED v2.0.63 ====="
test -d "$SRC"
test -f "$SRC/SHA256SUMS"
(
    cd "$SRC"
    sha256sum -c SHA256SUMS >/dev/null
)
"$GATE" preflight v2.0.63 >/tmp/tdh-v2.0.63-before-v264-preflight.log
grep -q '"status": "PREFLIGHT_OK"' /tmp/tdh-v2.0.63-before-v264-preflight.log

echo "===== 3. VERIFY REPOSITORY SOURCES ====="
test "$(git -C "$REPO" branch --show-current)" = "main"
test -f "$REPO_SOURCE/strategy_lab_controller.py"
test -f "$REPO_SOURCE/tests/test_v264_checkpoint_startup.py"
test -f "$REPO_SOURCE/tests/test_v263_checkpoint_resume.py"
test ! -L "$REPO_SOURCE/strategy_lab_controller.py"
test ! -L "$REPO_SOURCE/tests/test_v264_checkpoint_startup.py"
test ! -L "$REPO_SOURCE/tests/test_v263_checkpoint_resume.py"
echo "$EXPECTED_CONTROLLER_SHA256  $REPO_SOURCE/strategy_lab_controller.py" | sha256sum -c -
echo "$EXPECTED_TEST_SHA256  $REPO_SOURCE/tests/test_v264_checkpoint_startup.py" | sha256sum -c -
echo "$EXPECTED_V263_COMPAT_TEST_SHA256  $REPO_SOURCE/tests/test_v263_checkpoint_resume.py" | sha256sum -c -

if [[ -e "$DST" ]]; then
    echo "BLOCKED: staging destination already exists: $DST"
    exit 3
fi

echo "===== 4. BUILD v2.0.64 STAGING ====="
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
    "$REPO_SOURCE/tests/test_v264_checkpoint_startup.py" \
    "$TMP/tests/test_v264_checkpoint_startup.py"
install -T -m 0644 -- \
    "$REPO_SOURCE/tests/test_v263_checkpoint_resume.py" \
    "$TMP/tests/test_v263_checkpoint_resume.py"

"$PYTHON" -m py_compile \
    "$TMP/strategy_lab_controller.py" \
    "$TMP/tests/test_v263_checkpoint_resume.py" \
    "$TMP/tests/test_v264_checkpoint_startup.py"

/usr/bin/python3 "$TMP/tests/test_v263_checkpoint_resume.py"
/usr/bin/python3 "$TMP/tests/test_v264_checkpoint_startup.py"

"$PYTHON" - "$TMP/strategy_lab_controller.py" <<'PY'
import importlib.util
import sys

path = sys.argv[1]
spec = importlib.util.spec_from_file_location('tdh_v264_stage_smoke', path)
if spec is None or spec.loader is None:
    raise SystemExit('BLOCKED: v2.0.64 controller import failed')
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
assert contract['v264_inherited_executor_owns_fresh_round_directory'] is True
assert contract['controller_only_recovery_policy'] is True
assert contract['policy_change'] is False
assert contract['trading_actions'] is False
assert contract['exchange_api_access'] is False
print('V264_CHECKPOINT_STARTUP_SMOKE_OK')
PY

echo "===== 5. PUBLISH STAGING ATOMICALLY ====="
mv -- "$TMP" "$DST"

sha256sum \
    "$DST/strategy_lab_controller.py" \
    "$DST/tests/test_v263_checkpoint_resume.py" \
    "$DST/tests/test_v264_checkpoint_startup.py"

echo "SERVICE_STATE=$(systemctl is-active "$SERVICE" || true)"
echo "TDH_V264_STAGE_COMPLETE"
