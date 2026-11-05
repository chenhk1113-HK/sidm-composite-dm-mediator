"""F17: the BM2 '2.6% deviation' must name which collapse-time implementation it belongs to.

gravothermal_yang2024.py carries three variants and they disagree by 1.87x at BM2. The paper's
claim is reproducible only for the mixed-units variant that predict_sidm_halo() calls, and that
variant reproduces BM2 by construction (its prefactor was tuned on BM2). This test pins all three
numbers and both validator outcomes, so a future edit cannot quietly move the prefactor or re-claim
universality.
"""
import re
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "v0.3-prelim" / "code"))
sys.path.insert(0, str(REPO))

import gravothermal_yang2024 as g

PAPER = REPO / "v0.3-prelim" / "docs" / "PAPER_V1_DRAFT.md"

# published BM2 state (Yang+ 2024 [43])
T_PUBLISHED = 28.7

# measured 2026-11-05 on this host
EXPECTED = {
    "collapse_time_gyr": 29.438,          # mixed units, CALIBRATED_PREFACTOR = 1.34e12
    "collapse_time_SI_gyr": 15.774,       # literal published 150*C
    "collapse_time_calibrated_gyr": 28.700,  # 1.8194 x the SI form
}


def _bm2_inputs():
    return (g.BM2_SIGMA_EFF_PER_M_CM2_PER_G, g.BM2_RHO_S_MSUN_PER_KPC3, g.BM2_R_S_KPC)


@pytest.mark.parametrize("name", sorted(EXPECTED))
def test_bm2_collapse_time_variant_is_pinned(name):
    value = getattr(g, name)(*_bm2_inputs())
    assert value == pytest.approx(EXPECTED[name], rel=1e-3), (
        f"{name} moved to {value:.4f} Gyr; the paper and CURRENT.md quote the values pinned here")


def test_paper_deviation_matches_the_variant_predict_sidm_halo_uses():
    """The paper says 2.6%; that is only true of collapse_time_gyr. Verify it still is."""
    value = g.collapse_time_gyr(*_bm2_inputs())
    deviation = (value - T_PUBLISHED) / T_PUBLISHED * 100.0
    assert deviation == pytest.approx(2.57, abs=0.05), f"measured deviation {deviation:+.3f}%"
    if PAPER.exists():
        text = PAPER.read_text(encoding="utf-8", errors="replace")
        assert "2.57%" in text, "paper no longer quotes the re-measured +2.57% deviation"
        assert "29.438" in text, "paper no longer quotes the re-measured BM2 t_c"


def test_bm2_agreement_is_not_universality():
    """validate_bm2_calibration passes BY CONSTRUCTION; the independent halo test must stay False."""
    assert g.validate_bm2_calibration() is True
    assert g.validate_cosmo_501_calibration() is False, (
        "Cosmo-501 no longer fails: either the calibration became genuinely universal or the "
        "test halo/constants were changed - either way the paper's 'not a universal constant' "
        "conclusion needs re-reading before it is kept")


def test_variant_spread_is_recorded():
    """The three variants must keep disagreeing by ~1.87x; if they ever agree, the prefactors merged."""
    legacy = g.collapse_time_gyr(*_bm2_inputs())
    literal = g.collapse_time_SI_gyr(*_bm2_inputs())
    assert legacy / literal == pytest.approx(1.866, rel=0.02)


def test_predict_sidm_halo_does_not_use_the_density_profile():
    """F10 (rho_sidm) cannot move any collapse time because the profile is never evaluated there."""
    src = (REPO / "v0.3-prelim" / "code" / "gravothermal_yang2024.py").read_text(encoding="utf-8")
    m = re.search(r"def predict_sidm_halo\(.*?\n(?=\ndef |\nclass )", src, re.S)
    assert m, "predict_sidm_halo not found"
    body = m.group(0)
    assert "rho_sidm(" not in body, "predict_sidm_halo now evaluates rho_sidm - re-derive F17"
    assert "collapse_time_gyr(" in body, "predict_sidm_halo no longer calls collapse_time_gyr"
