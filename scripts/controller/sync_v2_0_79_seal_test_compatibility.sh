#!/usr/bin/env bash
set -Eeuo pipefail

SERVICE="strategy-lab-supervisor-v2.1.service"
BASE="/srv/tdh-collab/controller/strategy-lab-v2"
STAGE="$BASE/staging/v2.0.79"
RELEASE="$BASE/v2.0.79"
REPO="/home/tdw/the-darkest-hour"
REPO_TEST="$REPO/controller/staging/v2.0.79/tests/test_v279_v278_adapter_binding.py"
STAGE_TEST="$STAGE/tests/test_v279_v278_adapter_binding.py"
PYTHON="/srv/tdh-research/phoenix-venv/bin/python"

OLD_TEST_SHA256="417b25e29b1e7bad886c8418b4abb2a6c8c2e6c478b679e69c23d2346b378b24"
NEW_TEST_SHA256="376b9c78d56cb8c0379b92576b29f222e6c8f3760abff81016a18c1a88975a1c"

TMP=""
ROLLBACK_READY=0
COMMITTED=0

cleanup() {
    local status=$?
    if [[ "$status" -ne 0 && "$ROLLBACK_READY" -eq 1 && "$COMMITTED" -eq 0 ]]; then
        install -T -m 0644 -- "$TMP/old-test.py" "$STAGE_TEST"
        echo "ROLLBACK_COMPLETE"
    fi
    if [[ -n "$TMP" && -d "$TMP" && "$TMP" == "$STAGE/.v279-seal-test-compat."* ]]; then
        rm -rf --one-file-system "$TMP"
    fi
    exit "$status"
}
trap cleanup EXIT

echo "===== 1. KEEP v2.0.79 STOPPED ====="
systemctl mask --runtime --now "$SERVICE" || true
sleep 1
test "$(systemctl is-active "$SERVICE" || true)" != "active"

echo "===== 2. VERIFY FAILED-SEALED STAGING AND REPOSITORY SOURCE ====="
test -d "$STAGE"
test ! -e "$STAGE/SHA256SUMS"
test ! -e "$RELEASE"
test -x "$PYTHON"
case "$(git -C "$REPO" branch --show-current)" in
    main|agent/v2-0-79-v278-adapter-binding) ;;
    *)
        echo "BLOCKED: unexpected repository branch"
        exit 3
        ;;
esac
for path in "$STAGE_TEST" "$REPO_TEST"; do
    test -f "$path"
    test ! -L "$path"
done
echo "$OLD_TEST_SHA256  $STAGE_TEST" | sha256sum -c -
echo "$NEW_TEST_SHA256  $REPO_TEST" | sha256sum -c -

echo "===== 3. PREPARE ATOMIC TEST COMPATIBILITY SYNC ====="
TMP="$(mktemp -d "$STAGE/.v279-seal-test-compat.XXXXXX")"
install -m 0644 -- "$STAGE_TEST" "$TMP/old-test.py"
install -m 0644 -- "$REPO_TEST" "$TMP/new-test.py"
ROLLBACK_READY=1

python3 -m py_compile "$TMP/new-test.py"

echo "===== 4. APPLY AND VERIFY BOTH PYTHON ENVIRONMENTS ====="
mv -f -- "$TMP/new-test.py" "$STAGE_TEST"
echo "$NEW_TEST_SHA256  $STAGE_TEST" | sha256sum -c -

python3 -m unittest discover \
    -s "$STAGE/tests" \
    -p 'test_v279_v278_adapter_binding.py' \
    -v
"$PYTHON" "$STAGE_TEST"

COMMITTED=1
echo "SERVICE_STATE=$(systemctl is-active "$SERVICE" || true)"
echo "TDH_V279_SEAL_TEST_COMPATIBILITY_SYNC_COMPLETE"
