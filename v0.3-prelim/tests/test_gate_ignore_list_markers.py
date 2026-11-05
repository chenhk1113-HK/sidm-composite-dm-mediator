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
    ignored = gate.GATE_IGNORED_TESTS
    assert isinstance(ignored, dict) and ignored, "exclusion list must be a non-empty dict"
    for rel, reason in ignored.items():
        assert rel.startswith("v0.3-prelim/tests/test_"), rel
        assert len(reason) > 40, f"{rel}: exclusion needs a real reason, got {reason!r}"
        assert "F18" in reason and "D9" in reason, f"{rel}: reason must name finding F18 / D9"


def test_gate_no_longer_hard_codes_ignore_strings():
    src = _read(GATE_PATH)
    assert '--ignore=v0.3-prelim' not in src, (
        "hand-written --ignore= strings bypass GATE_IGNORED_TESTS and are the F18 defect class"
    )
    assert "--ignore={rel}" in src, "pytest args must be built from GATE_IGNORED_TESTS"


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
