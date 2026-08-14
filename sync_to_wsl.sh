#!/usr/bin/env bash
# sync_to_wsl.sh — Copy Windows-side dm-sidm-pipeline to WSL mirror.
#
# Direction: C:/Users/lamkuenai/projects/dm-sidm-pipeline
#      --> /home/lamkuenai/dm-sidm-pipeline
#
# Pattern: per-file `wsl -- cp` so each file lands at the right path on
# the WSL side (rsync across the WSL boundary is unreliable because
# /home/lamkuenai/... paths don't exist on the Windows side directly).
#
# Idempotent: re-running is safe; existing files are overwritten.
#
# Usage:
#   bash sync_to_wsl.sh                 # sync everything
#   bash sync_to_wsl.sh tests v0.3-prelim   # sync specific subdirs
#
# Why this exists: The D11 env recovery revealed the WSL mirror of
# dm-sidm-pipeline/v0.3-prelim/code/ had drifted to ~20 files while
# the Windows-side had 41 files. Half the project was orphaned on
# the WSL side. This script prevents future drift by syncing per-file
# after every code change.
set -euo pipefail

WIN_ROOT="C:/Users/lamkuenai/projects/dm-sidm-pipeline"
WSL_ROOT="/home/lamkuenai/dm-sidm-pipeline"
SUBDIRS_DEFAULT=(
    "."
    "tests"
    "v0.1-prelim"
    "v0.2-prelim"
    "v0.3-prelim"
)
SUBDIRS=("${@:-${SUBDIRS_DEFAULT[@]}}")

copy_file() {
    local src="$1"
    local dst_wsl="$2"
    # The cleanest reliable sync is: invoke `cp` *inside* the WSL bash with
    # both paths translated to /mnt/c/... on Windows-side.
    #   src  : C:/... -> /mnt/c/...
    #   dst  : /home/... stays the WSL-side path
    local src_wsl
    src_wsl=$(echo "$src" | sed 's|^C:/|/mnt/c/|; s|\\|/|g')
    # Ensure destination dir exists on WSL side (mkdir -p is idempotent).
    local dst_dir
    dst_dir=$(dirname "$dst_wsl")
    wsl -- mkdir -p "$dst_dir" 2>/dev/null || true
    # wsl cp may exit nonzero if src==dst (Windows and WSL see the same
    # file via 9P). Treat that as success. Real errors propagate.
    local out
    out=$(wsl -- cp "$src_wsl" "$dst_wsl" 2>&1) || true
    case "$out" in
        *same\ file*) return 0 ;;
        "") return 0 ;;
        *) echo "FAIL: $src -> $dst_wsl: $out" >&2; return 1 ;;
    esac
}

copied=0
failed=0

for sub in "${SUBDIRS[@]}"; do
    src_root="$WIN_ROOT/$sub"
    [ -e "$src_root" ] || continue
    dst_root="$WSL_ROOT/$sub"

    # Ensure destination dir exists (mkdir -p on WSL side)
    if [ -d "$src_root" ]; then
        wsl -- mkdir -p "$dst_root" 2>/dev/null || true
    fi

    if [ -f "$src_root" ]; then
        if copy_file "$src_root" "$dst_root"; then
            copied=$((copied+1))
        else
            failed=$((failed+1))
        fi
    elif [ -d "$src_root" ]; then
        # Recursive walk (skip __pycache__, *.pyc, data/raw/)
        while IFS= read -r -d '' f; do
            # Compute relative path from src_root
            rel="${f#$src_root/}"
            # Skip excluded paths
            case "$rel" in
                __pycache__*|*.pyc) continue ;;
                */data/raw/*) continue ;;
            esac
            dst="$dst_root/$rel"
            if copy_file "$f" "$dst"; then
                copied=$((copied+1))
            else
                failed=$((failed+1))
            fi
        done < <(find "$src_root" -type f -print0)
    fi
done

echo "sync_to_wsl.sh: $copied copied, $failed failed"