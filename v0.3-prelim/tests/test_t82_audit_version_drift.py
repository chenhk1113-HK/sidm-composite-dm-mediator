"""Tests for the VERSION drift-guard added in scripts/t82_audit.py (T83.6).

Per Updated review1.docx §1 (received 2026-09-03): the raw VERSION file
once lagged behind the badge/CITATION/CHANGELOG, and only a manual
human review caught the drift. These tests pin the audit-script's
VERSION-drift behavior so any future VERSION-mismatch is caught
automatically.

Test strategy:
1. The audit script exposes `CANONICAL_STANDING_VERSION = "0.4-prelim+T75"`.
2. The actual VERSION file in the project root currently equals
   "0.4-prelim+T75" (matching the canonical).
3. If anyone bumps the canonical without bumping VERSION, or vice versa,
   the audit script must exit 1.

We test by importing the audit module and exercising its main() against
the real project state. To simulate a FUTURE drift without actually
modifying the project VERSION file, we monkey-patch `CANONICAL_STANDING_VERSION`
to a bogus value and assert the exit code is 1.
"""
from __future__ import annotations

import io
import sys
from pathlib import Path

# Add scripts/ to path so we can import t82_audit
_HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(_HERE.parent.parent / "scripts"))

import t82_audit


def _capture_main(monkey_standing_version: str | None = None):
    """Run t82_audit.main() and capture (exit_code, stdout).

    If monkey_standing_version is provided, monkey-patch the canonical
    constant so we can simulate a mismatch.
    """
    import contextlib

    if monkey_standing_version is not None:
        t82_audit.CANONICAL_STANDING_VERSION = monkey_standing_version

    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        rc = t82_audit.main()
    # Restore
    t82_audit.CANONICAL_STANDING_VERSION = "0.4-prelim+T75"
    return rc, buf.getvalue()


class TestNoDriftState:
    """When standing version matches and docs agree, exit 0."""

    def test_real_project_state_passes(self):
        rc, out = _capture_main()
        assert rc == 0, (
            f"Expected exit 0 (no drift), got {rc}.\n"
            f"Script output:\n{out}"
        )
        assert "ALL CLEAR" in out
        # Specifically check VERSION drift-guard passed
        assert "VERSION = '0.4-prelim+T75' matches canonical" in out

    def test_total_check_count_at_least_33(self):
        # The 32 doc-presence checks + 1 VERSION drift-guard = at least 33
        rc, out = _capture_main()
        assert rc == 0
        # Grep the final summary line
        for line in out.splitlines():
            if line.startswith("ALL CLEAR"):
                # "ALL CLEAR: N/N checks passed — no drift"
                n_str = line.split("ALL CLEAR: ")[1].split("/")[0]
                assert int(n_str) >= 33, (
                    f"Expected ≥33 total checks, got {n_str}"
                )


class TestDriftDetection:
    """When canonical is monkey-patched to a mismatched value, exit 1."""

    def test_version_drift_caught_by_audit(self):
        # Simulate: someone changed the canonical string to a future
        # version (e.g. v0.5) but forgot to bump the actual VERSION file.
        rc, out = _capture_main(
            monkey_standing_version="0.5-prelim+fakecanonical"
        )
        assert rc == 1, (
            f"Expected exit 1 (drift detected), got {rc}.\n"
            f"Script output:\n{out}"
        )
        assert "DRIFT DETECTED" in out
        # The VERSION section should report drift
        assert "does NOT match canonical" in out

    def test_stale_canonical_caught_by_audit(self):
        # Simulate: someone forgot to bump canonical after publishing
        # a new doc version (canonical left at 0.3-prelim+T71.7 but
        # the actual VERSION file is 0.4-prelim+T75).
        rc, out = _capture_main(
            monkey_standing_version="0.3-prelim+T71.7"
        )
        assert rc == 1, (
            f"Expected exit 1 (stale canonical), got {rc}.\n"
            f"Script output:\n{out}"
        )
        assert "DRIFT DETECTED" in out


class TestAuditDocSync:
    """The drift-guard should NOT regress the existing 32 doc-presence checks."""

    def test_doc_checks_still_run(self):
        rc, out = _capture_main()
        assert rc == 0
        # All 7 doc labels should appear
        for label in (
            "README.md",
            "CITATION.cff",
            "MODEL_ASSUMPTIONS_AND_LIMITATIONS.md",
            "EXTRACT.md",
            "docs/LAYMAN_SUMMARY_V04_PRELIM_TIER1.md",
            "CHANGELOG.md",
            "VERSION",
        ):
            assert f"=== {label}" in out, f"{label} section missing from output"
        # And the drift-guard section
        assert "=== VERSION (drift-guard) ===" in out


if __name__ == "__main__":
    import inspect
    fns = [
        (n, f) for n, f in globals().items()
        if inspect.isfunction(f) and n.startswith("test_")
    ]
    for name, fn in fns:
        try:
            fn()
            print(f"PASS {name}")
        except AssertionError as e:
            print(f"FAIL {name}: {e}")
    print(f"\nRan {len(fns)} tests.")
