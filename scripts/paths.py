"""Single source of every host-dependent path in this repository (coverage gap CG-16).

Why this exists: 596 lines in 338 tracked code files spelled out `C:\\Users\\lamkuenai\\...` or
`/home/lamkuenai/...` directly, so the repository could only ever run on one machine. The gate
itself ran only on that machine, which is why the defect stayed invisible.

Rules enforced by v0.3-prelim/tests/test_no_hardcoded_host_paths_cg16.py:
  * no file in the live (gate-run) scope may contain a repository-root literal, this file included
    - every repository path below is derived from the file's own location;
  * files listed as CONVERTED in
    v0.3-prelim/data/results/cg16_host_path_inventory.json must contain the host username nowhere;
  * the only host-spelled values allowed anywhere in the live scope are the external-tool defaults
    pinned in that inventory (the WSL Julia binary and the WSL KiSS-SIDM project, which a
    Windows-side process must not resolve against the Windows home). Portability for those comes
    from the environment override, and the defaults state what this host is in one reviewable
    place instead of scattered across 60 files;
  * any *new* host-path literal anywhere in the live scope fails the gate unless it is deliberately
    added to the inventory with a reason.

Historical scripts under v0.3-prelim/code/ keep their literal paths on purpose: their outputs are
frozen artifacts already on disk, and rewriting the path logic of a script whose numbers are cited
in the paper invites a silent re-read of different data. They are counted and pinned, not hidden.
"""
from __future__ import annotations

import os
import re
from pathlib import Path

# ---------------------------------------------------------------- repository roots
# Derived from this file's own location: scripts/paths.py -> repository root.
_HERE = Path(__file__).resolve().parent
REPO_ROOT = Path(os.environ.get("DM_SIDM_PROJECT_ROOT", str(_HERE.parent)))
REPO = str(REPO_ROOT)

V03 = REPO_ROOT / "v0.3-prelim"
CODE_DIR = V03 / "code"
TESTS_DIR = V03 / "tests"
DATA_DIR = V03 / "data"
RESULTS_DIR = V03 / "data" / "results"
REFERENCE_DIR = V03 / "data" / "reference"
EXTERNAL_DIR = V03 / "data" / "external"
DOCS_DIR = V03 / "docs"
PAPER_MD = DOCS_DIR / "PAPER_V1_DRAFT.md"
CANONICAL_JSON = RESULTS_DIR / "canonical_numbers.json"

SCRIPTS_DIR = REPO_ROOT / "scripts"


def _win_to_mnt(win: str) -> str:
    """Windows path -> the same path as WSL mounts it (/mnt/c/...), with no host name spelled out."""
    m = re.match(r"^([A-Za-z]):[\\/](.*)$", win)
    if not m:
        return win
    return "/mnt/" + m.group(1).lower() + "/" + m.group(2).replace("\\", "/")


# Legacy mirrors of this repository on the WSL side. Both defaults are derived from where this
# repository actually lives, so no username appears here; DM_SIDM_WSL_MNT_ROOT / DM_SIDM_WSL_ROOT
# override them on a machine with a different layout.
WSL_MNT_ROOT = os.environ.get("DM_SIDM_WSL_MNT_ROOT") or _win_to_mnt(REPO)


def _wsl_home_from_mount(mnt: str) -> str | None:
    """/mnt/c/Users/<user>/... implies the WSL home /home/<user>; None if the layout says nothing.

    Built as a POSIX string, never with pathlib: on Windows pathlib would turn the leading slash
    into a backslash and produce a path that WSL does not have.
    """
    parts = [p for p in mnt.split("/") if p]
    if len(parts) >= 4 and parts[0] == "mnt" and parts[2].lower() == "users":
        return "/home/" + parts[3]
    return None


_LEGACY_HOME = _wsl_home_from_mount(WSL_MNT_ROOT)
LEGACY_WSL_ROOT = os.environ.get("DM_SIDM_WSL_ROOT") or (
    _LEGACY_HOME + "/" + REPO_ROOT.name if _LEGACY_HOME else WSL_MNT_ROOT
)


def repository_roots() -> list[str]:
    """Every root a script may legitimately look in, in preference order, deduplicated."""
    out: list[str] = []
    for root in (REPO, WSL_MNT_ROOT, LEGACY_WSL_ROOT):
        if root and root not in out:
            out.append(root)
    return out


# ------------------------------------------------------------- external host tools
# These are not repository files: they are this machine's interpreter, local-model service and
# credential file. Defaults preserve current behaviour on this host; every one can be repointed
# with an environment variable, which is what makes the repository portable.

def env_path(name: str, default: str) -> str:
    return os.environ.get(name, default)


# The host user home implied by the repository location (used for artefacts kept outside the repo).
HOST_HOME = REPO_ROOT.parents[1]
# Deliverable bundles built outside the repository (round-5 PDFs and their companions).
DELIVER_DIR = env_path("SIDM_DELIVER_DIR", HOST_HOME / "round5_deliver")

HERMES_HOME = env_path("SIDM_HERMES_HOME", HOST_HOME / "AppData" / "Local" / "hermes")
STRATA_DIR = Path(env_path("SIDM_STRATA_DIR", str(Path.home() / "Strata")))
STRATA_DATA_DIR = Path(env_path("SIDM_STRATA_DATA_DIR", str(Path.home() / "Strata-data")))
LLAMACPP_SERVER_JSON = HERMES_HOME / "runtimes" / "llamacpp" / "server.json"

# Reference interpreter used by the gate when the venv is unavailable.
REFERENCE_PYTHON = env_path(
    "SIDM_REFERENCE_PYTHON",
    str(Path.home() / "AppData" / "Local" / "Python" / "pythoncore-3.14-64" / "python.exe"),
)
# pdftotext shipped inside the Hermes toolchain (knowledge-base summary build).
PDFTOTEXT_EXE = env_path("SIDM_PDFTOTEXT", "pdftotext")

# WSL-side toolchain used by the KiSS-SIDM Julia bridge. Kept as literals on purpose: a
# Windows-side process must not resolve these against the Windows home, and the guard pins them.
JULIA_BIN = env_path("SIDM_JULIA_BIN", "/home/lamkuenai/.juliaup/bin/julia")
KISS_SIDM_DIR = env_path("SIDM_KISS_SIDM_DIR", "/home/lamkuenai/KiSS-SIDM")

# WSL home implied by the mounted repository path (pinned default: this host's WSL user).
WSL_HOME = env_path("SIDM_WSL_HOME", _LEGACY_HOME or "/home/lamkuenai")

# Interpreters that live outside the repository on this host (venvs used by specific analyses).
WSL_VENV_PYTHON = env_path("SIDM_WSL_VENV_PYTHON", WSL_HOME + "/.venv/bin/python")
WIMPY_VENV_PYTHON = env_path("SIDM_WIMPY_VENV_PYTHON", WSL_HOME + "/wimpy/bin/python")
AMUSE_VENV_PYTHON = env_path("SIDM_AMUSE_VENV_PYTHON", WSL_HOME + "/.local/amuse-py310-venv/bin/python")
HERMES_VENV_PYTHON = env_path(
    "SIDM_HERMES_VENV_PYTHON",
    str(HERMES_HOME / "hermes-agent" / "venv" / "Scripts" / "python.exe"),
)

# IllustrisTNG API key file (never stored in the repository).
TNG_KEY_FILE = env_path("SIDM_TNG_KEY_FILE", str(Path.home() / ".tng_api_key"))

# Scratch output for long-running probes.
SCRATCH_DIR = Path(env_path("SIDM_SCRATCH_DIR", str(HERMES_HOME / "cache" / "scratch")))


def describe() -> dict:
    """Machine-readable snapshot of every resolved path - used by the guard test's diagnostics."""
    return {
        "REPO_ROOT": REPO,
        "RESULTS_DIR": str(RESULTS_DIR),
        "DOCS_DIR": str(DOCS_DIR),
        "LEGACY_WSL_ROOT": LEGACY_WSL_ROOT,
        "WSL_MNT_ROOT": WSL_MNT_ROOT,
        "HERMES_HOME": str(HERMES_HOME),
        "REFERENCE_PYTHON": REFERENCE_PYTHON,
        "JULIA_BIN": JULIA_BIN,
        "KISS_SIDM_DIR": KISS_SIDM_DIR,
        "TNG_KEY_FILE": TNG_KEY_FILE,
    }
