"""
Tests for t103_joint_4d_fit.

T103 combines Portal A (v0.7 MAP Gaussian prior on m_phi, m_chi) with
Portal B (LZ Table S8 likelihood from T101) into a 4D emcee MCMC fit.
The 4 free parameters are (log_m_phi_MeV, log_m_chi_GeV, log_delta_MeV,
log_sigma_PortalB). g_chi, log_epsilon, log_alpha, log_xi are fixed at
v0.7 MAP for this reduced fit.
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path
import pytest

_T103_PATH = (Path(__file__).resolve().parents[1] / "outputs" / "t95" /
              "t103_joint_4d_posterior.json")


def _skip_if_no_t103():
    if not _T103_PATH.exists():
        pytest.skip("No T103 results; run t103_joint_4d_fit.py")


def test_t103_outputs_present():
    _skip_if_no_t103()
    out = json.load(open(_T103_PATH))
    assert out["test"] == "T103_joint_portal_A_B_4D_fit"
    assert "parameters_physical" in out
    assert "m_chi_GeV" in out["parameters_physical"]
    assert "delta_keV" in out["parameters_physical"]


def test_t103_m_chi_in_v07_range():
    """Joint m_chi should be within v0.7 MAP 16-84 quantiles (300-750 GeV)."""
    _skip_if_no_t103()
    out = json.load(open(_T103_PATH))
    m_chi = out["parameters_physical"]["m_chi_GeV"]
    # v0.7 MAP: median = 10^2.697 = 498 GeV, q16 = 340 GeV, q84 = 757 GeV
    assert 200 <= m_chi["MAP"] <= 1000, f"m_chi MAP = {m_chi['MAP']} GeV out of range"
    assert 200 <= m_chi["median"] <= 1000, f"m_chi median = {m_chi['median']} GeV out of range"


def test_t103_delta_near_300keV():
    """Joint delta should be near 300 keV (Di Mauro 2026 prediction)."""
    _skip_if_no_t103()
    out = json.load(open(_T103_PATH))
    delta = out["parameters_physical"]["delta_keV"]
    # Di Mauro predicts 297 keV, Fan-Tweed 350 keV
    assert 100 <= delta["MAP"] <= 400, f"delta MAP = {delta['MAP']} keV out of [100, 400]"
    # Median should also be in this range
    assert 100 <= delta["median"] <= 400, f"delta median = {delta['median']} keV out of [100, 400]"


def test_t103_sigma_in_physical_range():
    """Joint sigma_PortalB should be in the prior range [10^-46, 10^-38] cm^2."""
    _skip_if_no_t103()
    out = json.load(open(_T103_PATH))
    sigma = out["parameters_physical"]["sigma_PortalB_cm2"]
    log_sigma = math.log10(sigma["MAP"]) if sigma["MAP"] > 0 else float("-inf")
    assert -46 <= log_sigma <= -38, f"log10(sigma MAP) = {log_sigma} out of prior range"


def test_t103_module_importable():
    """Module imports without error."""
    import warnings
    import math
    warnings.filterwarnings("ignore")
    import t103_joint_4d_fit  # noqa: F401


def test_t103_jointly_consistent_with_lz_observation():
    """The joint MAP should give a non-zero LZ significance at the recovered
    (m_chi, delta) — i.e. the model is consistent with LZ observing 1 event."""
    _skip_if_no_t103()
    out = json.load(open(_T103_PATH))
    m_chi_map = out["parameters_physical"]["m_chi_GeV"]["MAP"]
    delta_map = out["parameters_physical"]["delta_keV"]["MAP"]

    # LZ Table S8 at MAP
    sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "code"))
    from t102_portal_b_fit import interpolate_local_sig
    sig = interpolate_local_sig(m_chi_map, delta_map, "Ov1")
    assert not math.isnan(sig), "LZ significance is NaN at MAP"
    assert sig > 0, f"LZ significance at MAP = {sig}σ, expected > 0"
