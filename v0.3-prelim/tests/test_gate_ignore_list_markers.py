"""Guard for finding F18 / decision D9: gate exclusions must be declared in BOTH places.

The release gate used to hide 15 `--ignore=` strings behind a stale prose comment while 45
tests inside those files were failing. From 2026-11-05 an exclusion is only allowed if:

  1. it is present in `scripts/verify_release_gate.py::GATE_IGNORED_TESTS` with a reason, and
  2. the excluded file carries a `# GATE-IGNORED[<name>]:` marker naming finding F18 and
     decision D9.

These tests check both directions, so the ignore list can neither grow silently (an
unregistered marker fails) nor shrink silently (an unmarked exclusion fails the gate layer).
"""

import importlib.util
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
GATE_PATH = REPO / "scripts" / "verify_release_gate.py"
TESTS_DIR = REPO / "v0.3-prelim" / "tests"


def _load_gate():
    spec = importlib.util.spec_from_file_location("verify_release_gate_under_test", GATE_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


gate = _load_gate()


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def test_exclusions_are_data_with_reasons():
    """The exclusion list may legitimately be EMPTY (every file repaired and re-admitted),
    but it may never be a bare list of file names without a stated reason."""
    ignored = gate.GATE_IGNORED_TESTS
    assert isinstance(ignored, dict), "exclusion list must be a dict of {file: reason}"
    for rel, reason in ignored.items():
        assert rel.startswith("v0.3-prelim/tests/test_"), rel
        assert len(reason) > 40, f"{rel}: exclusion needs a real reason, got {reason!r}"
        assert "F18" in reason and "D9" in reason, f"{rel}: reason must name finding F18 / D9"


def test_gate_no_longer_hard_codes_ignore_strings():
    src = _read(GATE_PATH)
    assert '--ignore=v0.3-prelim' not in src, (
        "hand-written --ignore= strings bypass GATE_IGNORED_TESTS and are the F18 defect class"
    )
    # 2026-11-15 (finding F36/F38): the pytest selection moved from an inline literal in
    # the gate to scripts/gate_pytest_selection.py, shared with the README badge guard.
    # This guard asserted a TEXTUAL pattern inside the gate file only, so the refactor
    # broke it while the invariant it protects stayed intact -- the same "pattern stopped
    # matching the artifact" class as F36. A textual search over scripts/*.py also matches
    # prose that merely mentions `--ignore=`, which is how the first fix failed. The check
    # is now behavioural: call the builder and inspect what it returns.
    assert "gate_pytest_args" in src, (
        "the gate must build its pytest layer through gate_pytest_args(), so the gate and "
        "the README badge guard cannot measure the suite with different filters (F36)"
    )
    spec = importlib.util.spec_from_file_location(
        "gate_pytest_selection_under_test", REPO / "scripts" / "gate_pytest_selection.py"
    )
    selection = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(selection)
    built = selection.gate_pytest_args(
        ["v0.3-prelim/tests/test_a.py", "v0.3-prelim/tests/test_b.py"]
    )
    assert built.count("--ignore=v0.3-prelim/tests/test_a.py") == 1
    assert built.count("--ignore=v0.3-prelim/tests/test_b.py") == 1
    assert " ".join(selection.gate_pytest_args()).count("--ignore=") == 0, (
        "an empty exclusion list must emit no --ignore= argument at all"
    )
    assert built.index("-k") < len(built) - 1 and built[-1] == selection.GATE_PYTEST_K_FILTER, (
        "the -k filter must be the shared constant, not a per-caller literal"
    )


def test_every_exclusion_has_its_in_file_marker():
    violations = gate.gate_ignored_marker_violations(REPO)
    assert violations == [], f"undocumented gate exclusions: {violations}"


def test_marker_lines_name_the_finding_and_the_decision():
    prefix = gate.GATE_IGNORED_MARKER_PREFIX
    for rel in gate.GATE_IGNORED_TESTS:
        lines = [ln for ln in _read(REPO / rel).splitlines() if ln.startswith(prefix)]
        assert len(lines) == 1, f"{rel}: expected exactly one marker line, got {len(lines)}"
        assert "F18" in lines[0] and "D9" in lines[0], f"{rel}: {lines[0]}"


def test_no_marker_without_a_registered_exclusion():
    """A marker in a file the gate does not list would be an unlabelled skip."""
    prefix = gate.GATE_IGNORED_MARKER_PREFIX
    registered = set(gate.GATE_IGNORED_TESTS)
    unregistered = []
    for path in sorted(TESTS_DIR.glob("test_*.py")):
        rel = path.relative_to(REPO).as_posix()
        lines = _read(path).splitlines()
        if any(ln.startswith(prefix) for ln in lines) and rel not in registered:
            unregistered.append(rel)
    assert unregistered == [], f"markers without a registered exclusion: {unregistered}"


def test_exclusion_count_is_disclosed_as_a_small_explicit_set():
    """F18 hid 12-15 files. The repaired set must stay small and every entry must still exist."""
    ignored = sorted(gate.GATE_IGNORED_TESTS)
    missing = [rel for rel in ignored if not (REPO / rel).exists()]
    assert missing == [], f"excluded files that no longer exist: {missing}"
    assert len(ignored) <= 6, (
        f"gate-ignored set has grown to {len(ignored)}; each entry needs a decision, not an ignore"
    )
