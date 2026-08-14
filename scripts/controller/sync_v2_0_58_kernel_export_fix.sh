#!/usr/bin/env bash
set -Eeuo pipefail

SERVICE="strategy-lab-supervisor-v2.1.service"
BASE="/srv/tdh-collab/controller/strategy-lab-v2"
STAGE="$BASE/staging/v2.0.58"
REPO="/home/tdw/the-darkest-hour"
SOURCE="$REPO/controller/staging/v2.0.58/research/research_kernel.py"
TARGET="$STAGE/research/research_kernel.py"
TMP="$STAGE/research/.research_kernel.py.v258-export-fix.$$"

EXPECTED_OLD_SHA256="b323f7ad188a444ca927300b499ce663fc5848fe2172ed5b0e6357cd4d06012a"
EXPECTED_NEW_SHA256="ae4c30e5f067efa37fd712c1b39ce468dbc4f807cfaac2d93544bf7e82af65fd"

cleanup() {
    if [[ -f "$TMP" && "$TMP" == "$STAGE/research/.research_kernel.py.v258-export-fix."* ]]; then
        rm -f -- "$TMP"
    fi
}
trap cleanup EXIT

echo "===== 1. KEEP UNSEALED v2.0.58 STOPPED ====="
systemctl mask --runtime --now "$SERVICE" || true
sleep 1
test "$(systemctl is-active "$SERVICE" || true)" != "active"

echo "===== 2. VERIFY BOUNDED UNSEALED STAGING ====="
test -d "$STAGE"
test ! -e "$STAGE/SHA256SUMS"
test "$(git -C "$REPO" branch --show-current)" = "main"
echo "$EXPECTED_NEW_SHA256  $SOURCE" | sha256sum -c -

CURRENT_SHA256="$(sha256sum "$TARGET" | awk '{print $1}')"
if [[ "$CURRENT_SHA256" == "$EXPECTED_NEW_SHA256" ]]; then
    echo "V258_KERNEL_EXPORT_FIX_ALREADY_APPLIED"
elif [[ "$CURRENT_SHA256" == "$EXPECTED_OLD_SHA256" ]]; then
    echo "===== 3. APPLY IMPORT-SAFE NAMESPACE EXPORT FIX ====="
    install -T -m 0644 -- "$SOURCE" "$TMP"
    python3 -m py_compile "$TMP"
    echo "$EXPECTED_NEW_SHA256  $TMP" | sha256sum -c -
    mv -T -- "$TMP" "$TARGET"
else
    echo "BLOCKED: unexpected staging kernel hash: $CURRENT_SHA256"
    exit 2
fi

echo "===== 4. VERIFY CORRECTED STAGING ====="
echo "$EXPECTED_NEW_SHA256  $TARGET" | sha256sum -c -
python3 -m py_compile "$TARGET"
echo "SERVICE_STATE=$(systemctl is-active "$SERVICE" || true)"
echo "TDH_V258_KERNEL_EXPORT_FIX_SYNC_COMPLETE"
