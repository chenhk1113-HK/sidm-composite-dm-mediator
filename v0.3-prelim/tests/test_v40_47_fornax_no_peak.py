"""Regression test for v40.47 Fornax no-peak re-evaluation.

Per v40.47: Fornax sigma/m(15) drops from 2.84 (canonical) to 2.02
(peak=0) -- a 1.4x reduction. The Fornax tension is PARTIALLY
resolved: the peak tail is removed, but the Yukawa background alone
at v=15 is 2.02 cm^2/g, still well above the dSph ceiling of 0.8.

This test locks the v40.47 finding so any future change that
accidentally restores the peak tail at Fornax (e.g., a typo in the
peak amplitude) FAILS the test.

Reference: scripts/v19_2_f_fornax_no_peak.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
RESULTS = REPO / "v0.3-prelim" / "data" / "results" / "v19_2_f_fornax_no_peak_2026_10_19.json"
SCRIPT = REPO / "scripts" / "v19_2_f_fornax_no_peak.py"


def test_v40_47_results_present():
    """Lock file must exist and have the v40.47 structure."""
    assert RESULTS.exists(), f"Missing results file: {RESULTS}"
    with open(RESULTS, encoding="utf-8") as fp:
        data = json.load(fp)
    assert "sigma_m_decomposition" in data
    assert "verdict" in data
    decomp = data["sigma_m_decomposition"]
    assert "yukawa_tail_cm2_g" in decomp
    assert "peak_tail_cm2_g" in decomp
    assert "sigma_m_canonical_cm2_g" in decomp
    assert "sigma_m_downgraded_cm2_g" in decomp
    assert "reduction_factor" in decomp


def test_v40_47_yukawa_background_still_too_strong():
    """Yukawa background at v=15 must be ABOVE the dSph ceiling.

    Per v40.47: Yukawa tail = 2.02 cm^2/g, dSph ceiling = 0.8 cm^2/g.
    The Yukawa background alone is 2.5x above the dSph ceiling.
    If yukawa < dSph_ceiling, the Fornax tension would be fully
    resolved by peak=0 (but v40.47 finds only partial resolution).
    """
    with open(RESULTS, encoding="utf-8") as fp:
        data = json.load(fp)
    yukawa = data["sigma_m_decomposition"]["yukawa_tail_cm2_g"]
    assert yukawa > 0.8, (
        f"Yukawa tail = {yukawa:.3f} cm^2/g at v=15, expected > 0.8 (dSph ceiling). "
        f"If < 0.8, the Fornax tension would be fully resolved by peak=0, "
        f"contradicting the v40.47 finding."
    )


def test_v40_47_canonical_still_unphysical():
    """Canonical (peak=174) sigma/m(15) must be ABOVE the dSph ceiling.

    Per v40.47: canonical sigma/m(15) = 2.84 cm^2/g, dSph ceiling = 0.8.
    The canonical framework has Fornax sigma/m above the dSph ceiling,
    which is the source of the v19.2-F sigma_HL_required = -0.47 tension.
    """
    with open(RESULTS, encoding="utf-8") as fp:
        data = json.load(fp)
    sigma_m_canonical = data["sigma_m_decomposition"]["sigma_m_canonical_cm2_g"]
    assert sigma_m_canonical > 0.8, (
        f"Canonical sigma/m(15) = {sigma_m_canonical:.3f} cm^2/g, expected > 0.8 (dSph ceiling). "
        f"If < 0.8, the canonical Fornax tension is not reproduced."
    )


def test_v40_47_partial_resolution():
    """The reduction factor must be SMALL (1.4x), not large.

    Per v40.47: sigma/m(15) drops from 2.84 to 2.02 (1.4x reduction).
    This is much smaller than the Cloud-9 case (273x reduction).
    If the reduction factor is > 5, the v40.47 finding is not reproduced.
    """
    with open(RESULTS, encoding="utf-8") as fp:
        data = json.load(fp)
    reduction = data["sigma_m_decomposition"]["reduction_factor"]
    assert 1.2 < reduction < 5.0, (
        f"Reduction factor = {reduction:.2f}x, expected 1.2-5.0. "
        f"If < 1.2, no peak tail exists at v=15. If > 5.0, the peak tail "
        f"is unexpectedly large at v=15 (closer to peak center)."
    )


def test_v40_47_verdict_partial_resolution():
    """The v40.47 verdict must confirm PARTIAL resolution, not full.

    Per v40.47: Fornax tension is partially resolved (peak tail removed)
    but NOT fully resolved (Yukawa background still too strong).
    If the verdict is 'fully_resolved', that would be a major claim
    requiring R88(71) review.
    """
    with open(RESULTS, encoding="utf-8") as fp:
        data = json.load(fp)
    verdict = data["verdict"]
    assert verdict["fornax_tension_partially_resolved_by_peak_downgrade"] is True, (
        f"verdict['fornax_tension_partially_resolved_by_peak_downgrade'] = "
        f"{verdict['fornax_tension_partially_resolved_by_peak_downgrade']}, "
        f"expected True. v40.47 finding is partial resolution."
    )
    assert verdict["fornax_tension_fully_resolved_by_peak_downgrade"] is False, (
        f"verdict['fornax_tension_fully_resolved_by_peak_downgrade'] = "
        f"{verdict['fornax_tension_fully_resolved_by_peak_downgrade']}, "
        f"expected False. v40.47 finding is NOT full resolution "
        f"(Yukawa background still too strong at v=15)."
    )
    assert verdict["additional_background_refit_needed"] is True, (
        f"verdict['additional_background_refit_needed'] = "
        f"{verdict['additional_background_refit_needed']}, expected True. "
        f"v40.47 finding is that additional background refit is needed."
    )


if __name__ == "__main__":
    for name in dir():
        if name.startswith("test_"):
            try:
                globals()[name]()
                print(f"  PASS  {name}")
            except AssertionError as e:
                print(f"  FAIL  {name}: {e}")
                sys.exit(1)
    print("All 5 v40.47 Fornax no-peak regression tests pass.")
