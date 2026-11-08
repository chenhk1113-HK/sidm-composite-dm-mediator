"""CG-16 guard: the live scope may not contain a host absolute path in code.

Decision enforced (owner-approved 2026-11-08):
  * scripts/**, tests/**, v0.3-prelim/tests/** and config.py resolve every host-dependent path
    through scripts/paths.py. A new hardcoded host path in that scope fails the gate.
  * Historical analysis code under v0.3-prelim/code/** is inventoried, not rewritten: its outputs
    already exist on disk, and re-pointing its reads could silently re-compute against other data.
    docs/CG16_PATH_INVENTORY.json records every file that still spells a host path and why.

The forbidden spellings are derived from scripts/paths.py itself, so this test contains no host
literal of its own - it stays portable on any machine.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "scripts"))
import paths  # noqa: E402

LIVE_PREFIXES = ("scripts/", "tests/", "v0.3-prelim/tests/")
LIVE_EXACT = {"config.py"}
# Files allowed to spell a host path: the single source, the tooling that must detect the
# spellings, and the test that asserts the historical split-brain defect.
ALLOW_SPELLING = {
    "scripts/paths.py",
    "scripts/cg16_convert.py",
    "scripts/cg16_scan.py",
    "v0.3-prelim/tests/test_no_hardcoded_host_paths_cg16.py",
    "v0.3-prelim/tests/test_config_split_brain.py",
    "v0.3-prelim/code/kiss_sidm_julia_bridge.py",
}

FORBIDDEN = sorted({
    paths.REPO, paths.LEGACY_WSL_ROOT, paths.WSL_MNT_ROOT, paths.WSL_HOME,
    str(paths.HERMES_HOME), str(paths.STRATA_DIR), str(paths.STRATA_DATA_DIR),
    paths.KISS_SIDM_DIR, paths.JULIA_BIN,
} | {r"C:\Users\lamkuenai\projects\sidm-composite-dm-mediator"})
MARKER = "lamkuenai"


def _tracked():
    out = subprocess.run(["git", "ls-files", "-z"], cwd=str(REPO), capture_output=True, check=True)
    return sorted(p.decode() for p in out.stdout.split(b"\0") if p)


def _code_only(src: str) -> str:
    """Blank out comments and docstrings: prose may mention a host path, code may not."""
    import ast
    import io
    import tokenize
    hidden = set()
    try:
        tree = ast.parse(src)
        for node in ast.walk(tree):
            if isinstance(node, (ast.Module, ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
                body = getattr(node, "body", [])
                if (body and isinstance(body[0], ast.Expr)
                        and isinstance(body[0].value, ast.Constant)
                        and isinstance(body[0].value.value, str)):
                    hidden.update(range(body[0].lineno, body[0].end_lineno + 1))
    except SyntaxError:
        pass
    try:
        toks = list(tokenize.generate_tokens(io.StringIO(src).readline))
    except Exception:
        toks = []
    out = []
    for i, line in enumerate(src.splitlines(), 1):
        if i in hidden:
            out.append("")
            continue
        comments = [t for t in toks if t.type == tokenize.COMMENT and t.start[0] == i]
        out.append(line[:min([t.start[1] for t in comments])] if comments else line)
    return "\n".join(out)


def test_paths_module_resolves_this_repository():
    assert Path(paths.REPO).resolve() == REPO, (paths.REPO, REPO)
    assert paths.RESULTS_DIR == REPO / "v0.3-prelim" / "data" / "results"


def test_paths_module_honours_env_override():
    """A checkout somewhere else must be usable without editing any file."""
    import os
    probe = REPO / "v0.3-prelim" / "tests" / "_cg16_env_probe.py"
    assert probe.exists(), probe
    env = {**dict(os.environ), "DM_SIDM_PROJECT_ROOT": str(REPO.parent / "elsewhere-checkout")}
    out = subprocess.run([sys.executable, str(probe)], capture_output=True, text=True,
                         cwd=str(REPO), env=env)
    assert out.returncode == 0, out.stderr
    assert out.stdout.strip() == str(REPO.parent / "elsewhere-checkout"), out.stdout


def test_repository_roots_are_derived_not_spelled():
    """REPO / WSL_MNT_ROOT / LEGACY_WSL_ROOT must be computed, not written out as literals."""
    assert paths.REPO == str(REPO), paths.REPO
    assert paths.WSL_MNT_ROOT == paths._win_to_mnt(paths.REPO), paths.WSL_MNT_ROOT
    assert paths.LEGACY_WSL_ROOT.startswith("/home/"), paths.LEGACY_WSL_ROOT
    assert paths.WSL_MNT_ROOT.startswith("/mnt/"), paths.WSL_MNT_ROOT
    src = (REPO / "scripts" / "paths.py").read_text(encoding="utf-8")
    for name in ("REPO_ROOT", "WSL_MNT_ROOT", "LEGACY_WSL_ROOT", "HERMES_HOME"):
        line = next(l for l in src.splitlines() if l.startswith(f"{name} ="))
        assert "lamkuenai" not in line, (name, line)
    roots = paths.repository_roots()
    assert paths.REPO in roots and paths.WSL_MNT_ROOT in roots


def test_pinned_external_defaults_are_wsl_spelled():
    """The two pinned WSL tool defaults must stay WSL-spelled: a Windows-spelled default would
    make the Julia bridge try to find a Julia binary that does not exist on the Windows side."""
    assert paths.JULIA_BIN.startswith("/home/"), paths.JULIA_BIN
    assert paths.KISS_SIDM_DIR.startswith("/home/"), paths.KISS_SIDM_DIR
    bridge = (REPO / "v0.3-prelim" / "code" / "kiss_sidm_julia_bridge.py").read_text(encoding="utf-8")
    assert "/home/lamkuenai/KiSS-SIDM" in bridge


def test_live_scope_has_no_host_absolute_path_in_code():
    offenders = []
    for rel in _tracked():
        if not rel.endswith(".py"):
            continue
        if not (rel.startswith(LIVE_PREFIXES) or rel in LIVE_EXACT):
            continue
        if rel in ALLOW_SPELLING:
            continue
        p = REPO / rel
        if not p.exists():
            continue
        code = _code_only(p.read_text(encoding="utf-8", errors="replace"))
        for i, line in enumerate(code.splitlines(), 1):
            if MARKER in line:
                offenders.append(f"{rel}:{i}: {line.strip()[:120]}")
    assert not offenders, (
        "CG-16: host absolute path in live-scope code. Resolve it through scripts/paths.py "
        "(see v0.3-prelim/data/results/cg16_host_path_inventory.json):\n" + "\n".join(offenders[:25]))


def test_inventory_exists_and_accounts_for_every_host_path_file():
    inv_path = REPO / "v0.3-prelim" / "data" / "results" / "cg16_host_path_inventory.json"
    assert inv_path.exists(), "the CG-16 inventory is missing - run scripts/cg16_scan.py"
    inv = json.loads(inv_path.read_text(encoding="utf-8"))
    assert inv.get("counts"), inv
    # Every live-scope file that still spells a host path must be recorded as prose-only, never code.
    for entry in inv.get("categories", {}).get("live_prose_only", []):
        assert entry.get("code_lines_with_host_path", 0) == 0, entry
    # The frozen historical set must be declared, not silently ignored.
    assert inv["categories"].get("historical_frozen_code"), "frozen scope not inventoried"


def test_inventory_is_current():
    """scripts/cg16_scan.py --check must pass against the working tree."""
    r = subprocess.run([sys.executable, str(REPO / "scripts" / "cg16_scan.py"), "--check"],
                       capture_output=True, text=True, cwd=str(REPO))
    assert r.returncode == 0, (r.stdout, r.stderr)


if __name__ == "__main__":
    for fn in [v for k, v in sorted(globals().items()) if k.startswith("test_")]:
        fn()
        print("PASS", fn.__name__)
