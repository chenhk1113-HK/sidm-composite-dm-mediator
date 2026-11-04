"""Guard for `sigma_responsiveness_probe.py` and for the D1 scope disclosure.

Three duties:

1. THE PROBE IS NOT VACUOUS. A synthetic profile that genuinely depends on sigma_0 must be
   reported as responsive. Without this, "is_sigma_inert: true" could be an artifact of a
   broken probe instead of a property of the model.

2. THE PRODUCERS' OWN PROFILES ARE MEASURED LIVE. phase39/phase40 must come out sigma-inert and
   phase39b must come out sigma-responsive, from the real functions, not from stored JSON. If
   someone repairs the phase39/phase40 core-radius prescription, these tests fail — which is the
   intended signal to re-derive those phases (same contract as test_sidm_core_radius_invariance.py).

3. THE PRODUCERS PUBLISH THE SCOPE. Both artifact dicts must contain a `verdict_scope` key, so the
   qualification travels with the numbers instead of living only in prose.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pytest

CODE_DIR = Path(__file__).resolve().parents[1] / "code"
if str(CODE_DIR) not in sys.path:
    sys.path.insert(0, str(CODE_DIR))

import phase39_nfw_vs_sidm as p39
import phase39b_sidm_responsive_profile as p39b
import phase40_corrected_comparison as p40
from sigma_responsiveness_probe import (
    INERT_TOLERANCE_KMS,
    PHYSICAL_SIGMA_SWEEP_CM2_PER_G,
    sigma_m_responsiveness_kms,
    scope_sentence,
    worst_case,
)

# The sweep the producers themselves use (1e-3 .. 1e3 cm^2/g brackets the canonical galaxy-scale
# range 0.06-0.68, the BM2 dwarf anchor 7.1, and the Cloud-9 anchors 147.1 / 174).
SIGMA_SWEEP = PHYSICAL_SIGMA_SWEEP_CM2_PER_G


# ---------------------------------------------------------------- duty 1: the probe has teeth
def test_probe_reports_a_genuinely_responsive_profile_as_responsive():
    resp = sigma_m_responsiveness_kms(lambda s0, r: 10.0 + 5.0 * s0, 0.195,
                                      radii_kpc=(1.0, 10.0), sigma_0_values=SIGMA_SWEEP)
    assert not resp["is_sigma_inert"]
    # 5 * (1e3 - 1e-3) = 5000 km/s of movement; anything smaller means the probe is broken.
    assert resp["max_abs_delta_kms"] > 4.0e3
    assert resp["max_relative_delta"] > 1.0


def test_probe_reports_an_identical_profile_as_inert():
    resp = sigma_m_responsiveness_kms(lambda s0, r: 20.0, 0.195, sigma_0_values=SIGMA_SWEEP)
    assert resp["is_sigma_inert"]
    assert resp["max_abs_delta_kms"] == 0.0


def test_probe_rejects_degenerate_input():
    with pytest.raises(ValueError):
        sigma_m_responsiveness_kms(lambda s0, r: 1.0, 0.195, sigma_0_values=[0.195])
    with pytest.raises(ValueError):
        sigma_m_responsiveness_kms(lambda s0, r: 1.0, 0.195, sigma_0_values=[0.0, 1.0])


def test_scope_sentence_matches_the_measurement():
    inert = sigma_m_responsiveness_kms(lambda s0, r: 20.0, 0.195, sigma_0_values=SIGMA_SWEEP)
    live = sigma_m_responsiveness_kms(lambda s0, r: 10.0 + 5.0 * s0, 0.195,
                                      sigma_0_values=SIGMA_SWEEP)
    assert "not evidence" in scope_sentence(inert)
    assert "does respond to sigma/m" in scope_sentence(live)


# ---------------------------------------------------------------- duty 2: live producers
def _phase39_like_kwargs():
    m_chi = 6.58
    a_slope = 0.7
    v_targets = [28.0, 100.0, 300.0, 700.0]
    sigma_peaks = [100.0, 0.07, 0.1, 0.01]
    width_fracs = [0.05, 0.05, 0.05, 0.10]
    resonances = []
    for i, v_t in enumerate(v_targets):
        e_r = p40.kinetic_energy_eV(v_t, m_chi)
        resonances.append({"name": f"R{i}", "E_R_eV": e_r, "Gamma_eV": width_fracs[i] * e_r,
                           "sigma_peak_cm2_per_g": sigma_peaks[i], "v_target_kms": v_t})
    return m_chi, resonances, a_slope


def test_phase39_sidm_profile_is_sigma_inert_on_every_fitted_galaxy():
    """Grounded version: each galaxy's OWN best-fit (log_rho_s, log_r_s) from the stored
    artifact, each galaxy's OWN observed V_max from SPARC, sigma swept 1e-3..1e3 cm2/g."""
    m_chi, resonances, a_slope = _phase39_like_kwargs()
    artifact = json.loads((CODE_DIR.parent / "data" / "results" / "phase39_nfw_vs_sidm.json")
                          .read_text(encoding="utf-8"))
    resp_list = []
    for rec in artifact["results"]["SIDM"]:
        log_rho_s, log_r_s, _ = rec["params"]
        g = p39.load_sparc_galaxy(rec["galaxy"])
        assert g is not None, rec["galaxy"]
        v_max = float(np.max(g["Vobs_kms"]))
        resp_list.append(sigma_m_responsiveness_kms(
            lambda s0, r, a=log_rho_s, b=log_r_s, v=v_max: p39.v_circ_sidm_multi_resonant(
                r, a, b, v, m_chi, resonances, s0, a_slope),
            0.195, sigma_0_values=list(SIGMA_SWEEP)))
    agg = worst_case(resp_list)
    assert agg["n_halos_probed"] >= 10
    assert agg["is_sigma_inert"], agg
    assert agg["max_abs_delta_kms"] < INERT_TOLERANCE_KMS
    # The producer's own artifact must carry a verdict_scope agreeing with this measurement.
    assert "verdict_scope" in artifact, "producer artifact predates the D1 scope disclosure"


def test_phase40_sidm_profile_is_sigma_inert_when_measured_live():
    m_chi, resonances, a_slope = _phase39_like_kwargs()
    resp = sigma_m_responsiveness_kms(
        lambda s0, r: p40.v_circ_sidm(r, 7.0, 1.0, 200.0, m_chi, resonances, s0, a_slope),
        0.195, sigma_0_values=list(SIGMA_SWEEP))
    assert resp["is_sigma_inert"], resp


def test_phase39b_responsive_profile_is_sigma_responsive_when_measured_live():
    resp = sigma_m_responsiveness_kms(
        lambda s0, r: p39b.v_circ_sidm_responsive(r, 7.0, 0.5, sigma_0=s0),
        0.195, radii_kpc=(1.0, 3.0, 10.0, 30.0, 50.0), sigma_0_values=list(SIGMA_SWEEP))
    assert not resp["is_sigma_inert"], resp
    assert resp["max_abs_delta_kms"] > 1.0  # measured ~10.9 km/s in phase39b's own report


def test_inertness_is_a_bound_not_an_absolute_claim():
    """The 0.1*r_s clamp is what makes phase39/40 inert, and the clamp CAN break.

    Measured 2026-11-04: for the 15 galaxies phase39 actually fitted, the clamp holds across
    1e-3..1e3 cm2/g exactly (delta = 0.0). For hypothetical halos outside that fit the breakout
    sigma varies with the halo (measured ~1e6 cm2/g for log_r_s=0.5, ~9e2 for log_rho_s=8/log_r_s=3.5,
    ~1e2 for log_rho_s=9/log_r_s=4). So the correct wording is "inert across the sigma/m range this
    project uses, for every halo it fitted", not "inert always". This test pins the breakout
    behaviour so the probe is known to be able to see a response in the real code.
    """
    m_chi, resonances, a_slope = _phase39_like_kwargs()
    inert_case = sigma_m_responsiveness_kms(
        lambda s0, r: p39.v_circ_sidm_multi_resonant(r, 7.0, 1.0, 200.0, m_chi, resonances, s0, a_slope),
        0.195, sigma_0_values=[1e-3, 1e3])
    broken_case = sigma_m_responsiveness_kms(
        lambda s0, r: p39.v_circ_sidm_multi_resonant(r, 9.0, 4.0, 60.0, m_chi, resonances, s0, a_slope),
        0.195, sigma_0_values=[1e-3, 1e5])
    assert inert_case["is_sigma_inert"] and inert_case["max_abs_delta_kms"] == 0.0
    assert not broken_case["is_sigma_inert"]
    assert broken_case["max_abs_delta_kms"] > 1.0


def test_probe_and_phase39b_report_agree_without_being_the_same_code():
    """phase39b computes its own responsiveness report independently; the two must agree."""
    own = p39b.responsiveness_report()
    probe_inert = sigma_m_responsiveness_kms(
        lambda s0, r: p39.v_circ_sidm_multi_resonant(r, 7.0, 0.5, 110.0, p39b.M_CHI_GEV,
                                                    p39b.build_resonances(), s0, p39b.A_SLOPE),
        0.195, radii_kpc=(1.0, 3.0, 10.0, 30.0, 50.0), sigma_0_values=list(SIGMA_SWEEP))
    assert own["inert_max_abs_dV_kms"] < 1e-3
    assert probe_inert["max_abs_delta_kms"] < 1e-3
    assert own["responsive_max_abs_dV_kms"] > 1.0


# ---------------------------------------------------------------- duty 3: producers publish scope
def test_both_producers_record_verdict_scope_in_their_artifacts():
    for name in ("phase39_nfw_vs_sidm.py", "phase40_corrected_comparison.py"):
        src = (CODE_DIR / name).read_text(encoding="utf-8")
        assert '"verdict_scope": verdict_scope,' in src, name
        assert '"sigma_m_responsiveness_probe": resp,' in src, name
        assert "sigma_m_responsiveness_kms(" in src, name
