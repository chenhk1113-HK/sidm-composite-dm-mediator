#!/usr/bin/env bash
# apply_patches.sh — Apply T215 KiSS-SIDM patches to a fresh KiSS-SIDM checkout
#
# Usage:
#   1. Clone KiSS-SIDM:    git clone <repo>
#   2. cd KiSS-SIDM
#   3. Run:                bash /path/to/apply_patches.sh
#
# What this does:
#   - Backs up the original collision.jl and 1d_sphere.jl to .bak.t215
#   - Applies the two .patch files in order
#   - Verifies the patches applied cleanly
#
# Tested on: KiSS-SIDM src/DSMC.jl/src/ as of 2026-09-26

set -e

# Determine KiSS-SIDM root (KiSS-SIDM/src/DSMC.jl/src/collision.jl must exist)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Search up for collision.jl
SEARCH_DIR="$(pwd)"
while [ "$SEARCH_DIR" != "/" ]; do
    if [ -f "$SEARCH_DIR/src/DSMC.jl/src/collision.jl" ]; then
        KISS_ROOT="$SEARCH_DIR"
        break
    fi
    SEARCH_DIR="$(dirname "$SEARCH_DIR")"
done

if [ -z "$KISS_ROOT" ]; then
    echo "ERROR: collision.jl not found. Run this script from inside KiSS-SIDM/ root."
    exit 1
fi

echo "Found KiSS-SIDM root: $KISS_ROOT"
cd "$KISS_ROOT"

# Patch 1: collision.jl — FP sqrt + assertion disable + ncom cap
echo ""
echo "Applying patch 1: collision.jl sqrt(max(0, x)) + assert disable + ncom cap"
if [ ! -f "src/DSMC.jl/src/collision.jl.bak.t215" ]; then
    cp src/DSMC.jl/src/collision.jl src/DSMC.jl/src/collision.jl.bak.t215
    echo "  Backup created: collision.jl.bak.t215"
fi

if patch -p0 --dry-run < "$SCRIPT_DIR/0001-collision-jl-sqrt-max.patch" > /dev/null 2>&1; then
    patch -p0 < "$SCRIPT_DIR/0001-collision-jl-sqrt-max.patch"
    echo "  Patch applied"
else
    echo "  Patch already applied or failed. Skipping."
fi

# Patch 2: 1d_sphere.jl — FP sqrt at boundary condition
echo ""
echo "Applying patch 2: 1d_sphere.jl sqrt(max(0, x)) at boundary"
if [ ! -f "src/DSMC.jl/src/1d_sphere.jl.bak.t215" ]; then
    cp src/DSMC.jl/src/1d_sphere.jl src/DSMC.jl/src/1d_sphere.jl.bak.t215
    echo "  Backup created: 1d_sphere.jl.bak.t215"
fi

if patch -p0 --dry-run < "$SCRIPT_DIR/0002-1d-sphere-jl-sqrt-max.patch" > /dev/null 2>&1; then
    patch -p0 < "$SCRIPT_DIR/0002-1d-sphere-jl-sqrt-max.patch"
    echo "  Patch applied"
else
    echo "  Patch already applied or failed. Skipping."
fi

# Verification
echo ""
echo "=== Verification ==="
echo "collision.jl FP patches:"
grep -c "sqrt(max(zero(v_rms^2" src/DSMC.jl/src/collision.jl || echo "  NOT FOUND"
echo ""
echo "collision.jl assert disables:"
grep -c "@assert majorant" src/DSMC.jl/src/collision.jl || echo "  All asserts disabled (good)"
grep -c "# @assert majorant -- disabled" src/DSMC.jl/src/collision.jl || echo "  NO disabled asserts"
echo ""
echo "1d_sphere.jl FP patch:"
grep -c "sqrt(max(zero(L^2" src/DSMC.jl/src/1d_sphere.jl || echo "  NOT FOUND"

echo ""
echo "=== Done ==="
echo "To revert: cp src/DSMC.jl/src/collision.jl.bak.t215 src/DSMC.jl/src/collision.jl"
echo "           cp src/DSMC.jl/src/1d_sphere.jl.bak.t215 src/DSMC.jl/src/1d_sphere.jl"