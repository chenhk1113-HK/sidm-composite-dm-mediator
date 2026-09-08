"""Tests for the VERSION drift-guard added in scripts/t82_audit.py (T83.6).

Per Updated review1.docx §1 (received 2026-09-03): the raw VERSION file
once lagged behind the badge/CITATION/CHANGELOG, and only a manual
human review caught the drift. These tests pin the audit-script's
VERSION-drift behavior so any future VERSION-mismatch is caught
automatically.

Test strategy:
1. The audit script exposes `CANONICAL_STANDING_VERSION = "0.4-prelim+T88E"`.
2. The actual VERSION file in the project root currently equals
   "0.4-prelim+T88E" (matching the canonical).
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
    # Restore (current canonical = "0.4-prelim+T88E")
    t82_audit.CANONICAL_STANDING_VERSION = "0.4-prelim+T88E"
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
        # Specifically check VERSION drift-guard passed (current canonical = "0.4-prelim+T88E")
        assert "VERSION = '0.4-prelim+T88E' matches canonical" in out

    def test_total_check_count_at_least_78(self):
        # Was >= 32 (with the original 10 README checks; pre-T86.7).
        # Post-T86.7: 10 README + 4 CITATION + 5 MODEL_ASSUMPTIONS +
        # 8 CURRENT.md + 3 EXTRACT + 6 LAYMAN + 2 CHANGELOG + 1 VERSION
        # = 39 doc-presence + 1 VERSION drift-guard = 40 total.
        # Post-T90 (2026-09-08): +6 T90 needles = 46 + 1 + 3 README = 50.
        # Post-T110 (2026-09-08): +4 T110 needles = 54 total.
        # Post-Tier A (2026-09-08): +4 Door B status needles = 58 total.
        # Post-Tier B + D (2026-09-08): +3 Tier B + D needles = 61 total
        # (Tier B Door D log Z needle dropped; delta only is sufficient).
        # Post-Door B refs (2026-09-08): +6 Door B paper/data needles = 67 total.
        # Post-T112/T113/T114 (2026-09-08): +5 reviewer-driven needles = 72 total.
        # Post-T112 breakthrough (2026-09-08): +6 T112 breakthrough needles = 78 total.
        rc, out = _capture_main()
        assert rc == 0
        for line in out.splitlines():
            if line.startswith("ALL CLEAR"):
                n_str = line.split("ALL CLEAR: ")[1].split("/")[0]
                assert int(n_str) >= 78, (
                    f"Expected ≥78 total checks, got {n_str}"
                )

    def test_t90_door_b_section_in_model_assumptions(self):
        """T90 (2026-09-08) magnetic-moment 'Door B' section must be in
        MODEL_ASSUMPTIONS_AND_LIMITATIONS.md. This pins the section
        against accidental deletion."""
        rc, out = _capture_main()
        assert rc == 0
        assert "T90 Door B section heading" in out
        assert "T90 8D log Z" in out
        assert "T90 8D delta log Z" in out
        assert "T90 8D MAP m_chi" in out
        assert "T90 8D MAP delta" in out
        assert "T90 8D MAP sigma_PortalB" in out
        # T110 (2026-09-08) 7D dynesty needles
        assert "T110 7D log Z" in out
        assert "T110 7D delta log Z" in out
        assert "T110 7D MAP m_chi" in out
        assert "T110 7D MAP mu_x" in out
        # Tier A (2026-09-08) Door B best LZ candidate
        assert "Tier A Door B best door heading" in out
        assert "Tier A Door B status text" in out
        assert "Tier A Door B Delta log Z" in out
        assert "Tier A Door C closed marker" in out
        # Tier B + D (2026-09-08) Door D multi-component + closure
        assert "Tier B Door D delta log Z" in out
        assert "Tier D all doors closed heading" in out
        assert "Tier D Door D closed marker" in out
        # Door B references (2026-09-08) - 5 papers + future data
        assert "Door B Di Mauro 2026 ref" in out
        assert "Door B Berlin Ferraro 2025 ref" in out
        assert "Door B Cline 2024 ref" in out
        assert "Door B DIAMX 2026 ref" in out
        assert "Door B XENONnT 2025 ref" in out
        assert "Door B LZ Run 4 future data" in out
        # T112/T113/T114 reviewer-driven actions (2026-09-08)
        assert "T112 high-res dynesty nlive" in out
        assert "T112 tight delta prior" in out
        assert "T113 LZ Run 4 forecast" in out
        assert "T113 DarkSide-20k forecast" in out
        assert "T114 Xe124 DEC systematic" in out
        # T112 breakthrough (2026-09-08) - T90 merge criterion #5 satisfied
        assert "T112 breakthrough delta log Z" in out
        assert "T112 breakthrough log Z uncertainty" in out
        assert "T112 breakthrough MAP delta keV" in out
        assert "T112 breakthrough criterion 5 status" in out
        assert "T112 breakthrough 3 of 5 status" in out
        assert "T112 breakthrough merge eligible" in out


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
            "CURRENT.md",
            "EXTRACT.md",
            "docs/LAYMAN_SUMMARY.md",
            "CHANGELOG.md",
            "VERSION",
        ):
            assert f"=== {label}" in out, f"{label} section missing from output"
        # And the drift-guard section
        assert "VERSION (drift-guard)" in out


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
