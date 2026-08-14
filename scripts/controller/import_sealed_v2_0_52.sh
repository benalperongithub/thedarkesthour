#!/usr/bin/env bash
set -Eeuo pipefail

BASE="/srv/tdh-collab/controller/strategy-lab-v2"
VERSION="v2.0.52"
SRC="$BASE/$VERSION"
GATE="/usr/local/sbin/tdh-lab-admin-gate"

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)"
REPO_ROOT="$(git -C "$SCRIPT_DIR" rev-parse --show-toplevel)"
REPO_UID="$(stat -c '%u' "$REPO_ROOT")"
REPO_GID="$(stat -c '%g' "$REPO_ROOT")"
DEST_PARENT="$REPO_ROOT/controller/releases/$VERSION"
TARGET="$DEST_PARENT/sealed-tree"
TMP=""

cleanup() {
    if [[ -n "$TMP" && -d "$TMP" && "$TMP" == "$DEST_PARENT/.sealed-tree-import."* ]]; then
        rm -rf --one-file-system "$TMP"
    fi
}
trap cleanup EXIT

echo "===== 1. VERIFY REPOSITORY ====="
test "$(git -C "$REPO_ROOT" remote get-url origin)" = "https://github.com/benalperongithub/thedarkesthour.git"
test "$(git -C "$REPO_ROOT" branch --show-current)" = "main"

if [[ -e "$TARGET" ]]; then
    echo "BLOCKED: target already exists: $TARGET"
    exit 2
fi

echo "===== 2. VERIFY SEALED RELEASE ====="
test -d "$SRC"
test -f "$SRC/SHA256SUMS"
(
    cd "$SRC"
    sha256sum -c SHA256SUMS
)
"$GATE" preflight "$VERSION"

if find "$SRC" -type l -print -quit | grep -q .; then
    echo "BLOCKED: sealed release contains a symlink"
    exit 3
fi

echo "===== 3. COPY BYTE-IDENTICAL SEALED TREE ====="
mkdir -p "$DEST_PARENT"
TMP="$(mktemp -d "$DEST_PARENT/.sealed-tree-import.XXXXXX")"
cp -a --no-preserve=ownership "$SRC/." "$TMP/"

(
    cd "$TMP"
    sha256sum -c SHA256SUMS
)

chown -R "$REPO_UID:$REPO_GID" "$TMP"
mv -- "$TMP" "$TARGET"
TMP=""

echo "===== 4. REPORT IMPORT ====="
echo "TARGET=$TARGET"
echo "FILE_COUNT=$(find "$TARGET" -type f | wc -l)"
echo "TREE_BYTES=$(du -sb "$TARGET" | awk '{print $1}')"
git -C "$REPO_ROOT" status --short -- "controller/releases/$VERSION"

echo "TDH_V252_SEALED_TREE_IMPORTED"
