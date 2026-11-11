"""CI wiring guard (ReviewResponse round, 2026-11-11).

Stdlib only on purpose: CI installs numpy + pandas + pytest (requirements-ci.txt), and PyYAML is
not in it. A guard written with `pytest.importorskip("yaml")` would silently SKIP in CI and guard
nothing, which is worse than not writing it. So the trigger block is parsed by a small
line-based reader instead.

Three drift classes this repo has actually been bitten by:

  1. README documents one Python, CI pins another. The quick start said `python3.11` while
     self_check.yml pinned 3.12 and the working venv was 3.12.13 - a reader who followed the
     README got a venv the test pins were not written for.
  2. CI triggers drift away from the branch that carries the workflow. A workflow that does not
     list the branch you push to simply never runs, and nothing says so locally.
  3. CI installs bare `pytest` while the tests import numpy at module level, so the job dies
     during collection (exit 2) instead of reporting a failed assertion - documented in the
     workflow's own comment as the 2026-11-03 fix.

Branch coverage was last measured against GitHub's API on 2026-11-11: the Self-check workflow is
`active`, the repository has 842 runs, and the 15 most recent runs are all `Self-check` on
`wip/v19.2-F-init` via `push`, completed `success` (2026-11-08 .. 2026-11-10).
"""
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "scripts"))
import paths  # noqa: E402

WORKFLOWS = REPO / ".github" / "workflows"
SELF_CHECK = WORKFLOWS / "self_check.yml"

# The branches this repo is actively pushed to. master is the remote default
# (origin/HEAD -> origin/master, measured 2026-11-11).
EXPECTED_TRIGGER_BRANCHES = {"master", "wip/cloud-9-relhic", "wip/v19.2-F-init"}


def _text() -> str:
    return SELF_CHECK.read_text(encoding="utf-8")


def _workflow_name(text: str) -> str:
    m = re.search(r"^name:\s*(.+?)\s*$", text, re.M)
    return m.group(1).strip("'\"") if m else ""


def _trigger_branches(text: str, event: str) -> set[str]:
    """Read `branches:` under `<event>:`, inline list or block list, stdlib only."""
    lines = text.splitlines()
    try:
        start = next(i for i, ln in enumerate(lines)
                     if re.match(rf"^\s{{2}}{event}:\s*$", ln))
    except StopIteration:
        raise AssertionError(f"{event}: trigger block not found in {SELF_CHECK.name}")
    base = len(re.match(r"^\s*", lines[start]).group(0))
    branches: set[str] = set()
    i = start + 1
    while i < len(lines):
        ln = lines[i]
        if ln.strip() and not ln.strip().startswith("#"):
            indent = len(re.match(r"^\s*", ln).group(0))
            if indent <= base:
                break  # left the event block
            inline = re.match(r"^\s*branches:\s*\[(.*?)\]\s*$", ln)
            if inline:
                branches |= {b.strip().strip("'\"") for b in inline.group(1).split(",") if b.strip()}
                break
            if re.match(r"^\s*branches:\s*$", ln):
                sub_base = indent
                i += 1
                while i < len(lines):
                    sub = lines[i]
                    if sub.strip() and not sub.strip().startswith("#"):
                        sub_indent = len(re.match(r"^\s*", sub).group(0))
                        if sub_indent <= sub_base:
                            break
                        m = re.match(r"^\s*-\s*(.+?)\s*$", sub)
                        if m:
                            branches.add(m.group(1).strip("'\""))
                    i += 1
                break
        i += 1
    return branches


def test_self_check_workflow_exists_and_declares_triggers():
    assert SELF_CHECK.exists(), "the Self-check workflow is missing"
    text = _text()
    assert _workflow_name(text) == "Self-check"
    for event in ("push", "pull_request"):
        covered = _trigger_branches(text, event)
        assert covered, f"{event} declares no branches"
        missing = EXPECTED_TRIGGER_BRANCHES - covered
        assert not missing, f"{event} does not trigger on {sorted(missing)}"
    assert re.search(r"^\s{2,}workflow_dispatch:", text, re.M), "manual trigger removed"


def test_current_branch_is_covered_by_the_push_trigger():
    """A push to the branch carrying this file must actually start a run."""
    proc = subprocess.run(["git", "rev-parse", "--abbrev-ref", "HEAD"],
                          capture_output=True, text=True, encoding="utf-8",
                          errors="replace", cwd=str(REPO), timeout=60)
    branch = (proc.stdout or "").strip()
    if branch in ("HEAD", ""):
        pytest.skip("detached HEAD has no branch name")
    if not (branch == "master" or branch.startswith("wip/")):
        pytest.skip(f"{branch} is not an active-branch name; coverage is not asserted")
    assert branch in _trigger_branches(_text(), "push"), (
        f"pushes to {branch} would not run Self-check")


def test_readme_python_matches_ci_python():
    """The documented interpreter and the CI interpreter must be the same minor version."""
    ci = re.search(r"python-version:\s*[\"']?(\d+\.\d+)", _text())
    assert ci, "self_check.yml does not pin a Python version"
    readme = (REPO / "README.md").read_text(encoding="utf-8")
    documented = set(re.findall(r"python3\.\d+", readme))
    assert documented, "README no longer states a Python version in the quick start"
    ci_minor = ci.group(1)
    assert documented == {f"python{ci_minor}"}, (
        f"CI pins {ci_minor} but README tells the reader to use {sorted(documented)}")


def test_ci_installs_the_pinned_requirements_not_bare_pytest():
    text = _text()
    assert "requirements-ci.txt" in text, "CI no longer installs the pinned test requirements"
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("pip install"):
            assert "requirements" in stripped, f"CI installs unpinned deps: {stripped!r}"


def test_requirements_ci_covers_what_the_ci_test_layer_imports():
    """A module-level numpy import in a CI-run test dies in collection if numpy is not pinned."""
    pins = {re.match(r"([A-Za-z0-9_.-]+)", ln).group(1).lower()
            for ln in (REPO / "requirements-ci.txt").read_text(encoding="utf-8").splitlines()
            if re.match(r"^[A-Za-z0-9_.-]+==", ln)}
    assert "numpy" in pins, "requirements-ci.txt no longer pins numpy"
    for name in ("test_physical_invariants.py", "test_physical_constraints.py",
                 "test_independent_and_robustness.py"):
        src = (paths.TESTS_DIR / name).read_text(encoding="utf-8")
        for mod in re.findall(r"^(?:import|from)\s+([A-Za-z_][A-Za-z0-9_]*)", src, re.M):
            if mod in {"numpy", "scipy", "pandas", "matplotlib", "emcee", "dynesty"}:
                assert mod.lower() in pins, f"{name} imports {mod}, not pinned in requirements-ci.txt"


def test_this_guard_runs_without_pyyaml():
    """The guard is only useful if CI can actually run it: no third-party import here."""
    src = Path(__file__).read_text(encoding="utf-8")
    third_party = re.findall(r"^(?:import|from)\s+([A-Za-z_][A-Za-z0-9_]*)", src, re.M)
    allowed = {"re", "subprocess", "sys", "pathlib", "__future__", "paths", "pytest"}
    offenders = {m for m in third_party if m not in allowed}
    assert not offenders, f"guard imports {sorted(offenders)}; CI does not install them"


def test_the_disabled_workflow_stays_disabled():
    """ci.yml was switched off by owner decision D12 by renaming it; a .yml copy must not reappear."""
    assert (WORKFLOWS / "ci.yml.disabled").exists()
    assert not (WORKFLOWS / "ci.yml").exists(), "ci.yml reappeared - D12 said keep it off"
