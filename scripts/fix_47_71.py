"""Quick fix for the remaining 47.71 at L192."""
# CG-16: every host-dependent path is resolved by scripts/paths.py (single source).
import sys as _sys, pathlib as _pathlib
_CG16_ROOT = next(a for a in _pathlib.Path(__file__).resolve().parents
                  if (a / "scripts" / "paths.py").exists())
_sys.path.insert(0, str(_CG16_ROOT / "scripts"))
from paths import REPO, REPO_ROOT  # noqa: E402
import pathlib

PAPER = pathlib.Path(
    str(REPO_ROOT / "v0.3-prelim/docs/PAPER_V1_DRAFT.md")
)

txt = PAPER.read_text(encoding="utf-8")
old = "σ_peak ≤ 47.71"
new = "σ_peak ≤ 47.67 (interpolated from ratio = 2.86 at σ_peak = 50)"
got = txt.count(old)
print(f"Occurrences of 'σ_peak ≤ 47.71': {got}")
assert got == 1
txt = txt.replace(old, new)
PAPER.write_text(txt, encoding="utf-8")
print(f"Fixed! Remaining '47.71': {txt.count('47.71')}")
print(f"New '47.67' count: {txt.count('47.67')}")