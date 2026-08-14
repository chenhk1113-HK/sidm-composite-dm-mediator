#!/usr/bin/env bash
# sync_to_win.sh — Copy WSL-side dm-sidm-pipeline to Windows mirror.
#
# Direction: /home/lamkuenai/dm-sidm-pipeline
#      --> C:/Users/lamkuenai/projects/dm-sidm-pipeline
#
# Pattern: per-file `wsl -- cat src > dst` so each file lands at the right
# path on the Windows side (rsync across the WSL boundary is unreliable
# because /home/lamkuenai/... paths don't exist on the Windows side directly).
#
# Idempotent: re-running is safe; existing files are overwritten.
#
# Usage:
#   bash sync_to_win.sh                  # sync everything
#   bash sync_to_win.sh tests v0.3-prelim  # sync specific subdirs
#
# Why this exists: Mirror of sync_to_wsl.sh. Most edits happen on Windows
# (write_file / patch tools), and need to flow to WSL for dynesty runs.
# This script handles the rarer reverse direction: a file edited in WSL
# during a long background run should land back on Windows for the next
# `write_file` to merge cleanly.
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
    local src_wsl="$1"
    local dst_win="$2"
    # Inverse of sync_to_wsl.sh: read WSL src, write Windows dst.
    # Strategy: invoke `wsl -- bash -c "cat src"` and pipe to dst_win on
    # the Windows side. mkdir -p on Windows side first.
    local dst_dir
    dst_dir=$(dirname "$dst_win")
    mkdir -p "$dst_dir" 2>/dev/null || true
    if ! wsl -- bash -c "cat '$src_wsl'" > "$dst_win" 2>/dev/null; then
        echo "FAIL: $src_wsl -> $dst_win" >&2
        return 1
    fi
}

copied=0
failed=0

for sub in "${SUBDIRS[@]}"; do
    src_root="$WSL_ROOT/$sub"
    dst_root="$WIN_ROOT/$sub"

    # Get file list from WSL side
    if [ -f "$src_root" ]; then
        if copy_file "$src_root" "$dst_root"; then
            copied=$((copied+1))
        else
            failed=$((failed+1))
        fi
    elif [ -d "$src_root" ]; then
        # Walk via wsl find
        while IFS= read -r -d '' f; do
            rel="${f#$src_root/}"
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
        done < <(wsl -- bash -c "find '$src_root' -type f -print0")
    fi
done

echo "sync_to_win.sh: $copied copied, $failed failed"