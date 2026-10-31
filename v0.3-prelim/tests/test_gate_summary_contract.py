"""Unit tests for the gate summary contract (closes CG-5 + CG-10 at unit level).

These exercise scripts/verify_release_gate.py's summarize() and run_layer()
directly — no 15-layer subprocess run needed. The end-to-end version of the
same contract lives in scripts/verify_gate_crash_mutation_proof.py (n24 item 2:
"A check that has never been shown to fail is an assumption").

Contract asserted here:
  * --quick can never record pytest as PASS — only SKIP (CG-10).
  * A run with skips never prints a plain green line; skips are named.
  * pytest-internal skips are disclosed, not silently counted green.
  * A failed layer forces exit 1 and removes that layer from 'Checked:'.
  * No output of the gate, ever, contains the old 'ALL GATES PASSED' phrasing.
  * Every summary carries the SCOPE disclosure (CG-5).
"""
import importlib.util
import re
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
GATE_PATH = REPO / "scripts" / "verify_release_gate.py"

_spec = importlib.util.spec_from_file_location("verify_release_gate", GATE_PATH)
gate = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(gate)


def _res(*pairs):
    return [(n, s, "") for n, s in pairs]


class TestSummaryContract:
    def test_all_pass_green_but_scoped(self):
        text, code = gate.summarize(_res(("audit_units.py", "PASS"), ("pytest", "PASS")))
        assert code == 0
        assert "GATE PASSED: all 2 layer(s)" in text
        assert "SCOPE:" in text          # CG-5 disclosure, always
        assert "ALL GATES PASSED" not in text

    def test_quick_skip_is_named_never_green(self):
        text, code = gate.summarize(_res(("audit_units.py", "PASS"), ("pytest", "SKIP")))
        assert code == 0
        assert "[SKIP] pytest" in text
        assert "SKIPPED: pytest" in text          # CG-10: skip named in summary
        assert "asserts nothing" in text
        assert "ALL GATES PASSED" not in text
        assert "Checked:" in text
        checked = [l for l in text.splitlines() if l.startswith("Checked:")][0]
        assert "pytest" not in checked            # a skip never appears as checked

    def test_pytest_internal_skips_disclosed(self):
        text, code = gate.summarize(_res(("pytest", "PASS")), pytest_internal_skips=3)
        assert code == 0
        assert "pytest internal skips: 3" in text  # a skip proves nothing (CG-10)

    def test_failure_exits_1_and_poisoned_layer_not_checked(self):
        text, code = gate.summarize(_res(("pytest", "PASS"), ("audit_stale_strings.py", "FAIL")))
        assert code == 1
        assert "ONE OR MORE GATE LAYERS FAILED" in text
        assert "GATE PASSED" not in text
        checked = [l for l in text.splitlines() if l.startswith("Checked:")][0]
        assert "audit_stale_strings.py" not in checked

    def test_summary_never_emits_legacy_phrase(self):
        for results in (
            _res(("a", "PASS")),
            _res(("a", "PASS"), ("b", "SKIP")),
            _res(("a", "FAIL")),
        ):
            text, _ = gate.summarize(results)
            assert "ALL GATES PASSED" not in text


class TestRunLayerFailureSemantics:
    """n24 item 2's unit-level half: nonzero exit / missing interpreter are
    failures, not 'clean'. End-to-end half: verify_gate_crash_mutation_proof.py."""

    def test_nonzero_exit_is_failure(self):
        ok, out = gate.run_layer("mutant", ["-c", "raise SystemExit(3)"], timeout=60)
        assert ok is False

    def test_zero_exit_is_success(self):
        ok, _ = gate.run_layer("clean", ["-c", "pass"], timeout=60)
        assert ok is True

    def test_missing_interpreter_is_failure_not_crash(self):
        ok, out = gate.run_layer("missing", ["-c", "pass"], timeout=10,
                                 env_python=REPO / "definitely-not-a-python.exe")
        assert ok is False
        assert out == ""


class TestGateSourceContract:
    """Source-level: the gate literally cannot mark a skipped pytest PASS."""

    def test_quick_branch_records_skip_only(self):
        src = GATE_PATH.read_text(encoding="utf-8")
        assert '("pytest", "SKIP", "")' in src
        assert '("pytest", "PASS"' not in src
        assert "record(\"pytest\", ok" in src  # full-run path still records real result

    def test_legacy_green_phrase_absent_from_gate_source(self):
        src = GATE_PATH.read_text(encoding="utf-8")
        assert "ALL GATES PASSED" not in src
