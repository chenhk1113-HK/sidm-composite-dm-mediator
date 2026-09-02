"""R12 conftest: ensure sys.path includes v0.1-prelim/code (where halo_profiles
and sparc_loader live) BEFORE any test or module tries to import them.

This fixes the import ordering bug where channels_v03.py imports from
halo_profiles, but halo_profiles only exists in v0.1-prelim/code.

Without this conftest, every test that imports channels_v03 fails at
collection time on this codebase because pytest auto-prepends only
v0.3-prelim/code to sys.path.
"""
import sys
from pathlib import Path

WSL = Path("/home/lamkuenai/sidm-composite-dm-mediator")
WIN = Path("C:/Users/lamkuenai/projects/sidm-composite-dm-mediator")
# On Windows, Path("/home/...") resolves to C:\home\... and returns exists()=True
# even if it's not a real WSL path. Use is_dir() + a code sentinel to break ties.
def _is_real_project_root(p):
    if not p.is_dir():
        return False
    return (p / "v0.3-prelim" / "code" / "channels_extended.py").is_file()

PROJ = WSL if _is_real_project_root(WSL) else WIN
if not _is_real_project_root(PROJ):
    # Last-resort fallback: detect from this conftest's own location.
    PROJ = Path(__file__).resolve().parents[2]

if PROJ.exists():
    v01 = str(PROJ / "v0.1-prelim/code")
    v03 = str(PROJ / "v0.3-prelim/code")
    # v0.1-prelim MUST come before v0.3-prelim so that channels_v03.py's
    # `from halo_profiles import ...` resolves correctly.
    if v01 not in sys.path:
        sys.path.insert(0, v01)
    if v03 not in sys.path:
        sys.path.insert(0, v03)