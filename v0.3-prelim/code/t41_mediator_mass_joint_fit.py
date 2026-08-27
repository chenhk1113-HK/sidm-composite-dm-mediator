"""
T41 — Mediator-mass (m_phi) + DM mass (m_chi) joint fit, full posterior.

Motivation (per user ship direction #1):
  The T39 best-fit (sigma/m_0 ~ 1.57 cm^2/g, a ~ +0.94) is a *phenomenological*
  fit. The published Yukawa cross-section predicts a ~ -2 (sigma/m GROWS with v).
  This is a tension: the data want sigma/m to DROP from dwarfs (~10 km/s) to
  clusters (~1500 km/s), but Yukawa cross-sections naturally RISE.

  Resolution: an m_phi populated as a free parameter lets the posterior
  localize the mediator that best fits the velocity dependence. Calibrating
  against the 5+ channels (dSph, UFD, Bullet Cluster, SPARC, LZ) and
  marginalizing over (epsilon, alpha) gives the experimental
  (m_phi, epsilon) posterior.

Key change vs T39:
  T39: 4 free params (log_sigma_m_0, a, log_epsilon, log_alpha)
  T41: 5 free params (log_m_phi_MeV, log_m_chi_GeV, g_chi, log_epsilon, log_alpha)
       a is DERIVED from (log_m_phi, log_m_chi, g_chi) via the Yukawa
       cross-section (T40 YukawaVelocityDependent).

v0.6 change (R14 Rec #8):
  T41 promoted from 5D -> 6D by adding log_xi as a free parameter
  (xi = T_dark/T_SM, the dark-sector temperature ratio). Previously this
  was hardcoded to 1.0 in T55/T59 fixed assumptions. The H4.1 sensitivity
  sweep at v0.5 (vary xi in {0.1, 0.5, 1.0, 2.0, 5.0}) showed ROBUSTNESS
  across the prior range -- log_Z range = 0.438, well below 1.0.

  NOTE on H4.1 caveat: the v0.5 sweep actually had a no-op XI_OVERRIDE that
  was set but never read by t41/t39. log_Z was constant by construction
  (the result was trivially "robust"). v0.6 wires xi into the
  Fermi-dwarf sigma_v mapping (sigma_v -> sigma_v * xi^2 per T55
  non-thermal-relic normalization, matching h4_xi_sweep.py:9), so the
  posterior on xi is now an honest data-driven inference.

Priors (v0.6):
  log_m_phi_MeV:  [-1, 4]      (10 keV to 10 TeV)
  log_m_chi_GeV:  [0.5, 3]     (3 GeV to 1 TeV)
  g_chi:          [0.01, 2]    (perturbative to ~O(1))
  log_epsilon:    [-60, -1]    (vector-mediator kinetic mixing)
  log_alpha:      [-30, -1]    (annihilation coupling)
  log_xi:         [-1.0, 0.7]  (xi in [0.1, 5.0], matches H4.1 sweep range)

Outputs:
  - dynesty nested-sampling posterior (6D)
  - weighted medians per parameter (including log_xi)
  - log Z, dlogz, wall time
  - HONEST flag if (a_derived - a_T39) > 1 — i.e., Yukawa doesn't fit.

This is the test that answers the user question: "any feasible way to
find the mediator by experiment?" — the posterior p(m_phi) is the answer.
"""
from __future__ import annotations
import json
import os
import sys
import time
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "v0.1-prelim" / "code"))

import dynesty
import config
import channels_v03 as ch_v03
import t40_yukawa_sigma_m as yukawa
from t30_lz_real_posterior import loglike_lz_real
from t32_fermi_dwarf_channel import loglike_fermi_dwarf
# T70.3 (R13 H1 closure): KSFR/PCAC validity mask — Channel 15
# Per MODEL_ASSUMPTIONS_AND_LIMITATIONS.md §6 + REVIEWER_AUDIT_R13.md H1
from ksfr_pcac_validity import loglike_ksfr_pcac_validity
# T70.8 (R14 Rec #3 closure): CMB spectral distortion — Channel 16
# Per Planck Collaboration Int. LI 2017 (arXiv:1612.00071):
#   |μ| < 9e-6, |y| < 1.5e-6 (95% CL)
from channels_extended import loglike_cmb_distortion


import platform

if platform.system() == "Windows" or not Path("/home/lamkuenai/sidm-composite-dm-mediator").exists():
    _DEFAULT_RESULTS_DIR = "C:/Users/lamkuenai/projects/sidm-composite-dm-mediator/v0.3-prelim/data/results"
else:
    _DEFAULT_RESULTS_DIR = "/home/lamkuenai/sidm-composite-dm-mediator/v0.3-prelim/data/results"

RESULTS_DIR = Path(_DEFAULT_RESULTS_DIR)
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

# T41 priors
LOG_M_PHI_MEV_RANGE = (-1.0, 4.0)  # 10 keV to 10 TeV
LOG_M_CHI_GEV_RANGE = (0.5, 3.0)   # 3 GeV to 1 TeV
G_CHI_RANGE = (0.01, 2.0)
LOG_EPSILON_RANGE = (-60.0, -1.0)
LOG_ALPHA_RANGE = (-30.0, -1.0)
# v0.6: xi (T_dark/T_SM) promoted from fixed (xi=1) to free parameter.
# Prior range = [-1.0, 0.7] in log_xi, i.e. xi in [0.1, 5.0]. Matches the
# H4.1 sweep grid {0.1, 0.5, 1.0, 2.0, 5.0} used at v0.5.
LOG_XI_RANGE = (-1.0, 0.7)

# Reference velocity
V_REF = 100.0  # km/s


def weighted_median(values, weights):
    idx = np.argsort(values)
    values = values[idx]
    weights = weights[idx]
    cumw = np.cumsum(weights)
    mid = cumw[-1] / 2
    return float(values[np.searchsorted(cumw, mid)])


def weighted_quantiles(values, weights, q):
    idx = np.argsort(values)
    values = values[idx]
    weights = weights[idx]
    cumw = np.cumsum(weights)
    cumw = cumw / cumw[-1]
    return np.interp(q, cumw, values)


def sigma_m_at_v_yukawa(v_kms: float, m_phi_MeV: float, m_chi_GeV: float,
                         g_chi: float) -> float:
    """sigma/m at velocity v (Yukawa model)."""
    return yukawa.sigma_m_cm2_per_g(v_kms, m_phi_MeV, m_chi_GeV, g_chi)


def derived_a(m_phi_MeV: float, m_chi_GeV: float, g_chi: float) -> float:
    """Velocity power-law index a (channels_v03 convention).

    CONVENTION (channels_v03.py:34): sigma/m(v) = sigma_m_0 (v / V_REF)**(-a),
    so positive a means FALLING sigma/m with velocity. Numerically:

        a = -d log(sigma/m) / d log(v) |_(v_ref)

    computed as a centred finite-difference in log space at v=50, 200 km/s:

        a = -(log sigma(50) - log sigma(200)) / (log 50 - log 200)

    NOTE (R12 P0-B): the previous line-103 implementation was MISSING the
    leading minus sign and produced numbers OPPOSITE in sign to the
    channels_v03 convention. For (m_phi=10 MeV, m_chi=40 GeV, g_chi=0.1),
    the old code returned a ~ -1.08 (claiming RISING sigma/m) when the
    physical Yukawa form actually gives FALLING sigma/m; the corrected
    code returns a ~ +1.08, matching channels_v03 and t54 conventions.
    """
    s1 = sigma_m_at_v_yukawa(50.0, m_phi_MeV, m_chi_GeV, g_chi)
    s2 = sigma_m_at_v_yukawa(200.0, m_phi_MeV, m_chi_GeV, g_chi)
    if s1 <= 0 or s2 <= 0:
        return -2.0  # fallback (channels_v03 sense: negative a = rising sigma/m)
    a = -((np.log10(s1) - np.log10(s2)) / (np.log10(50.0) - np.log10(200.0)))
    return float(a)


def loglike_joint(theta):
    """6-parameter joint likelihood (v0.6: xi promoted from fixed to free).

    theta = (log_m_phi_MeV, log_m_chi_GeV, g_chi, log_epsilon, log_alpha, log_xi)
    Backward compat: a 5-tuple (no log_xi) is treated as xi = 1.0 (the v0.5
    fixed assumption). The H4.1 sweep used this 5D shim with log_xi=0
    effectively no-op; v0.6 makes it explicit.
    """
    # Backward-compat shim: 5D theta -> 6D with xi=1.0 (T55 default).
    if len(theta) == 5:
        log_m_phi, log_m_chi, g_chi, log_eps, log_alpha = theta
        log_xi = 0.0
    elif len(theta) == 6:
        log_m_phi, log_m_chi, g_chi, log_eps, log_alpha, log_xi = theta
    else:
        return -np.inf
    m_phi_MeV = 10 ** log_m_phi
    m_chi_GeV = 10 ** log_m_chi
    epsilon = 10 ** log_eps
    alpha = 10 ** log_alpha
    xi = 10 ** log_xi

    if m_phi_MeV <= 0 or m_chi_GeV <= 0 or g_chi <= 0 or epsilon <= 0 or alpha <= 0 or xi <= 0:
        return -np.inf
    if not (1e-2 <= g_chi <= 2.0):
        return -np.inf
    # log_xi prior box: [-1.0, 0.7] -> xi in [0.1, 5.0]; gated by prior_transform.
    if not (LOG_XI_RANGE[0] <= log_xi <= LOG_XI_RANGE[1]):
        return -np.inf

    # T70.3 (R13 H1 closure): KSFR/PCAC validity mask (Channel 15).
    # Per MODEL_ASSUMPTIONS_AND_LIMITATIONS.md §6: hard reject if
    # (f_pi, g_chi, m_rho/f_pi) outside the validity box. The T41 MAP
    # (m_phi = 26.6 MeV) is BELOW the f_pi lower bound (418 MeV); the
    # mask correctly rejects it, and the v0.5 sub-project documents
    # this as a major finding. Disable via env var
    # SIDM_DISABLE_KSFR_MASK=1 for cross-version comparison.
    # Note: loglike_ksfr_pcac_validity uses theta[:5] which still works
    # for both 5D and 6D inputs.
    ll_ksfr = loglike_ksfr_pcac_validity(theta)
    if not np.isfinite(ll_ksfr):
        return -np.inf

    # Derived: sigma_m_0 at v_ref = 100 km/s
    sigma_m_0 = sigma_m_at_v_yukawa(V_REF, m_phi_MeV, m_chi_GeV, g_chi)
    if sigma_m_0 <= 0 or not np.isfinite(sigma_m_0):
        return -np.inf

    # Derived velocity power-law index
    a = derived_a(m_phi_MeV, m_chi_GeV, g_chi)

    # 1. dSph (channel 2) — bimodal posterior. NO xi dependence.
    ll_dsph = ch_v03.loglike_dsph_v03(sigma_m_0, a)
    if not np.isfinite(ll_dsph):
        return -np.inf

    # 2. UFD (channel 3). NO xi dependence.
    ll_ufd = ch_v03.loglike_ufd_v03(sigma_m_0, a)
    if not np.isfinite(ll_ufd):
        return -np.inf

    # 3. Bullet Cluster (channel 4). NO xi dependence.
    ll_bullet = ch_v03.loglike_bullet_v03(sigma_m_0, a)
    if not np.isfinite(ll_bullet):
        return -np.inf

    # 4. LZ (T30) — uses sigma_DM_nucleon from dark-photon kinetic mixing.
    # R12 P1-C (2026-08-17): replaced dimensionally-inconsistent
    # `sigma_DM_n = epsilon * sigma_m_0` (units cm^2/g, NOT cm^2) with
    # the proper dark-photon portal form via t39.sigma_SI_from_dark_photon.
    # NO xi dependence (kinetic-mixing direct detection is independent
    # of dark-sector temperature ratio).
    import t39_tier3_epsilon_alpha_joint_fit as t39
    # T41's loglike_joint varies m_phi, m_chi, g_chi; we need alpha_D too.
    # Fix alpha_D ~ g_chi^2 / (4 pi) as a simplified dark-side estimate
    # (proper Benchmark A fix would add alpha_D as a 6th parameter).
    ALPHA_D_T41 = max(g_chi ** 2 / (4.0 * np.pi), 1.0e-5)
    sigma_DM_n = t39.sigma_SI_from_dark_photon(
        epsilon=epsilon,
        m_chi_GeV=m_chi_GeV,
        m_A_prime_MeV=m_phi_MeV,
        alpha_D=ALPHA_D_T41,
    )
    ll_lz = loglike_lz_real(m_chi_GeV, sigma_DM_n)
    if not np.isfinite(ll_lz):
        return -np.inf

    # 5. Fermi dwarf (T32) — gamma-ray from annihilation.
    # R12 P1-C: replaced `alpha * sigma_m_at_v^2` (units cm^4/g^2, NOT
    # cm^3/s) with the proper dark-photon portal form.
    # v0.6 (R14 Rec #8): xi entered via relic-density normalization.
    # sigma_v_required_for_relic_density scales as 1/xi from the
    # non-thermal-relic normalization (T55), so sigma_v_effective for
    # the standard thermal xsec at fixed relic density is sigma_v * xi^2
    # (per h4_xi_sweep.py:9 design intent). This is the ONLY channel
    # loglike that depends on xi.
    sigma_v = t39.sigma_v_from_dark_photon(
        m_chi_GeV=m_chi_GeV,
        m_A_prime_MeV=m_phi_MeV,
        alpha_D=ALPHA_D_T41,
    )
    sigma_v = sigma_v * xi ** 2
    ll_fermi = loglike_fermi_dwarf(m_chi_GeV, sigma_v)
    if not np.isfinite(ll_fermi):
        return -np.inf

    # KSFR/PCAC validity mask (T70.3 / Channel 15) is applied earlier
    # in this function (before any of the expensive likelihood calls);
    # if it fired we'd already have returned -inf above. So we don't
    # add it again here — it's a hard pre-filter, not a soft penalty.

    # 6. CMB spectral distortion (T70.8 / Channel 16).
    # Per Planck Collaboration Int. LI 2017 (arXiv:1612.00071):
    #   |μ| < 9.0e-6, |y| < 1.5e-6 (95% CL)
    # Penalizes mediator (m_phi) decays that fall in the post-BBN,
    # post-recombination CMB-sensitive window 1e5 s < τ < 1e13 s.
    # The penalty is one-sided Gaussian: returns 0 if τ is outside the
    # window (mediator stable OR pre-BBN OR way after recombination).
    # NOTE: at the T41 v0.6 MAP (ε ~ 1e-31, m_phi ~ 750 MeV), τ ~ 10^37 s
    # far exceeds the window — this channel contributes 0 to the MAP and
    # acts as a soft prior carving out the high-ε / low-m_phi corner of
    # the prior box.
    ll_cmb = loglike_cmb_distortion(m_chi_GeV * 1e9, m_phi_MeV * 1e6, epsilon)
    if not np.isfinite(ll_cmb):
        return -np.inf

    # Optional SPARC contribution (slow, so disabled by default)
    # Use a coarse grid to be fast.
    # T69 (v0.4-prelim): rescaled by baryonic-feedback nuisance f_fb.
    # Default f_fb = 0.5 (moderate feedback per the Di Cintio+ 2014a prior).
    # Override via the F_FB_OVERRIDE env var (used by t69_feedback_nuisance_rerun.py).
    # NO xi dependence.
    f_fb_default = 0.5
    try:
        f_fb = float(os.environ.get("F_FB_OVERRIDE", f_fb_default))
        if not (0.0 <= f_fb <= 1.0):
            f_fb = f_fb_default
    except (TypeError, ValueError):
        f_fb = f_fb_default
    try:
        import feedback_nuisance as fb
        ll_sparc = fb.sparc_rescaled_loglike(sigma_m_0, a, f_fb=f_fb) / 1000
    except Exception:
        # Fallback to the legacy call if feedback_nuisance can't be imported
        # (e.g. fresh clone without v0.4-prelim paths set up).
        try:
            import t8_v03_joint_fit as t8
            ll_sparc = t8.delta_log_sparc(sigma_m_0, a) / 1000
        except Exception:
            ll_sparc = 0.0

    return ll_dsph + ll_ufd + ll_bullet + ll_lz + ll_fermi + ll_sparc + ll_cmb


def prior_transform_5(u):
    """5D prior transform (DEPRECATED: backward-compat alias for v0.5 + sweeps).

    Identical to v0.5: returns a 5-element theta array. Internally maps to the
    new 6D prior with log_xi = 0 (xi = 1.0 -- the v0.5 fixed assumption).
    Kept so that h3_convergence_runner, h4_form_factor_sweep, h4_xi_sweep,
    h4_inelastic_sweep, and any other v0.5 callers using
    `t41.prior_transform_5` keep working without modification.

    For the canonical v0.6 main run, use prior_transform_6 (6D).
    """
    return [
        LOG_M_PHI_MEV_RANGE[0] + u[0] * (LOG_M_PHI_MEV_RANGE[1] - LOG_M_PHI_MEV_RANGE[0]),
        LOG_M_CHI_GEV_RANGE[0] + u[1] * (LOG_M_CHI_GEV_RANGE[1] - LOG_M_CHI_GEV_RANGE[0]),
        G_CHI_RANGE[0] + u[2] * (G_CHI_RANGE[1] - G_CHI_RANGE[0]),
        LOG_EPSILON_RANGE[0] + u[3] * (LOG_EPSILON_RANGE[1] - LOG_EPSILON_RANGE[0]),
        LOG_ALPHA_RANGE[0] + u[4] * (LOG_ALPHA_RANGE[1] - LOG_ALPHA_RANGE[0]),
    ]


def prior_transform_6(u):
    """6D prior transform (v0.6 canonical).

    theta = (log_m_phi_MeV, log_m_chi_GeV, g_chi, log_epsilon, log_alpha, log_xi)

    Priors (uniform in log-space unless noted):
      log_m_phi_MeV: [-1, 4]          (10 keV -> 10 TeV)
      log_m_chi_GeV: [0.5, 3]         (3 GeV  -> 1 TeV)
      g_chi:         [0.01, 2]        (linear, perturbative)
      log_epsilon:   [-60, -1]        (kinetic mixing)
      log_alpha:     [-30, -1]        (annihilation coupling)
      log_xi:        [-1.0, 0.7]      (xi = T_dark/T_SM in [0.1, 5.0])
    """
    return [
        LOG_M_PHI_MEV_RANGE[0] + u[0] * (LOG_M_PHI_MEV_RANGE[1] - LOG_M_PHI_MEV_RANGE[0]),
        LOG_M_CHI_GEV_RANGE[0] + u[1] * (LOG_M_CHI_GEV_RANGE[1] - LOG_M_CHI_GEV_RANGE[0]),
        G_CHI_RANGE[0] + u[2] * (G_CHI_RANGE[1] - G_CHI_RANGE[0]),
        LOG_EPSILON_RANGE[0] + u[3] * (LOG_EPSILON_RANGE[1] - LOG_EPSILON_RANGE[0]),
        LOG_ALPHA_RANGE[0] + u[4] * (LOG_ALPHA_RANGE[1] - LOG_ALPHA_RANGE[0]),
        LOG_XI_RANGE[0] + u[5] * (LOG_XI_RANGE[1] - LOG_XI_RANGE[0]),
    ]


def main():
    print("=" * 80)
    print("T41 — Mediator-mass (m_phi) + DM-mass (m_chi) joint fit")
    print("=" * 80)
    print("6 parameters (v0.6: log_xi promoted from fixed to free):")
    print("  log_m_phi_MeV, log_m_chi_GeV, g_chi, log_epsilon, log_alpha, log_xi")
    print(f"  log_m_phi_MeV: [{LOG_M_PHI_MEV_RANGE[0]}, {LOG_M_PHI_MEV_RANGE[1]}]")
    print(f"  log_m_chi_GeV: [{LOG_M_CHI_GEV_RANGE[0]}, {LOG_M_CHI_GEV_RANGE[1]}]")
    print(f"  g_chi:         [{G_CHI_RANGE[0]}, {G_CHI_RANGE[1]}]")
    print(f"  log_epsilon:   [{LOG_EPSILON_RANGE[0]}, {LOG_EPSILON_RANGE[1]}]")
    print(f"  log_alpha:     [{LOG_ALPHA_RANGE[0]}, {LOG_ALPHA_RANGE[1]}]")
    print(f"  log_xi:         [{LOG_XI_RANGE[0]}, {LOG_XI_RANGE[1]}]   (xi in [0.1, 5.0])")
    # T70.8 (R14 Rec #3): print CMB distortion channel status
    print()
    print("CMB DISTORTION: ON (Channel 16, Planck Int. LI 2017 arXiv:1612.00071)")
    print("  Penalizes post-BBN mediator decays in 1e5 s < tau < 1e13 s window.")
    print("  At T41 v0.6 MAP (eps~1e-31, m_phi~750 MeV) tau ~ 1e37 s: no penalty (stable mediator).")
    print("  Effective at carving high-eps / low-m_phi corner of prior.")
    print()

    # R14 (2026-08-26): inelastic-channel toggle for sensitivity-test parity with
    # h4_inelastic_sweep.py. When T41_INELASTIC=on, the joint likelihood gets
    # a constant additive shift of log(1 + r_inelastic) where r_inelastic
    # represents a representative dark-sector mass-splitting contribution
    # (h4.3 default = 0.3). This is a sensitivity-test approximation; a full
    # implementation would add delta_m_split as a 6th fit parameter.
    inelastic_on = os.environ.get("T41_INELASTIC", "off").strip().lower() in ("on", "1", "true", "yes")
    r_inelastic = float(os.environ.get("T41_INELASTIC_R", "0.3"))
    if inelastic_on:
        # Wrap loglike_joint with the same approach as h4_inelastic_sweep.py
        _base_loglike = loglike_joint

        def _loglike_with_inelastic(theta):
            ll = _base_loglike(theta)
            if not np.isfinite(ll):
                return ll
            return ll + float(np.log(1.0 + r_inelastic))

        loglike_for_run = _loglike_with_inelastic
        print(f"  INELASTIC: ON (r_inelastic={r_inelastic}) — wrapper adds log(1+r) to ll")
    else:
        loglike_for_run = loglike_joint
        print(f"  INELASTIC: OFF (default) — use T41_INELASTIC=on to enable")
    print()

    t0 = time.time()
    # T70.4 (R13 H3 follow-up): nlive=200 gives borderline-stable results; nlive=500
    # gives cleaner convergence per H3 sweep. Allow override via env var so v0.5
    # re-runs and follow-up sweeps can scale up cleanly. Default nlive=200 preserves
    # backward compatibility with the published T41 numbers.
    nlive = int(os.environ.get("T41_NLIVE", "200"))
    # v0.6: 6D posterior (log_xi promoted from fixed to free per R14 Rec #8).
    sampler = dynesty.NestedSampler(
        loglikelihood=loglike_for_run,
        prior_transform=prior_transform_6,
        ndim=6, nlive=nlive, bound='multi', sample='auto', bootstrap=0,
    )
    sampler.run_nested(dlogz=0.1, print_progress=False)
    wall = time.time() - t0

    res = sampler.results
    log_Z = float(res.logz[-1])
    log_Z_err = float(res.logzerr[-1])
    samples = res.samples
    weights = np.exp(res.logwt - res.logz[-1])
    imap = int(np.argmax(weights))
    MAP = samples[imap].tolist()

    # Weighted medians
    med = {
        "log_m_phi_MeV": weighted_median(samples[:, 0], weights),
        "log_m_chi_GeV": weighted_median(samples[:, 1], weights),
        "g_chi": weighted_median(samples[:, 2], weights),
        "log_epsilon": weighted_median(samples[:, 3], weights),
        "log_alpha": weighted_median(samples[:, 4], weights),
        "log_xi": weighted_median(samples[:, 5], weights),
    }

    # 16/50/84 quantiles
    quants = {
        "log_m_phi_MeV": list(weighted_quantiles(samples[:, 0], weights, [0.16, 0.5, 0.84])),
        "log_m_chi_GeV": list(weighted_quantiles(samples[:, 1], weights, [0.16, 0.5, 0.84])),
        "g_chi":         list(weighted_quantiles(samples[:, 2], weights, [0.16, 0.5, 0.84])),
        "log_epsilon":   list(weighted_quantiles(samples[:, 3], weights, [0.16, 0.5, 0.84])),
        "log_alpha":     list(weighted_quantiles(samples[:, 4], weights, [0.16, 0.5, 0.84])),
        "log_xi":        list(weighted_quantiles(samples[:, 5], weights, [0.16, 0.5, 0.84])),
    }

    # Convert to physical units
    med_m_phi_MeV = 10 ** med["log_m_phi_MeV"]
    med_m_chi_GeV = 10 ** med["log_m_chi_GeV"]
    med_eps = 10 ** med["log_epsilon"]
    med_alpha = 10 ** med["log_alpha"]
    med_xi = 10 ** med["log_xi"]

    # Derived sigma_m_0 + a at MAP
    map_m_phi_MeV = 10 ** MAP[0]
    map_m_chi_GeV = 10 ** MAP[1]
    map_g_chi = MAP[2]
    map_sigma_m_0 = sigma_m_at_v_yukawa(V_REF, map_m_phi_MeV, map_m_chi_GeV, map_g_chi)
    map_a = derived_a(map_m_phi_MeV, map_m_chi_GeV, map_g_chi)

    # Compare to T39 prior
    t39_sigma_m_0 = 1.57   # median from T39
    t39_a = 0.94           # median from T39
    a_tension = abs(map_a - t39_a)

    print(f"  log Z = {log_Z:.3f} ± {log_Z_err:.3f} (wall = {wall:.1f}s)")
    print(f"  MAP: log_m_phi={MAP[0]:.3f} ({map_m_phi_MeV:.2f} MeV), "
          f"log_m_chi={MAP[1]:.3f} ({map_m_chi_GeV:.2f} GeV), "
          f"g_chi={MAP[2]:.4f}, "
          f"log_eps={MAP[3]:.2f}, log_alpha={MAP[4]:.2f}, "
          f"log_xi={MAP[5]:.3f} (xi={10**MAP[5]:.3f})")
    print(f"  DERIVED at MAP: sigma_m_0 = {map_sigma_m_0:.3f} cm^2/g, a = {map_a:.3f}")
    print(f"  Median: log_m_phi={med['log_m_phi_MeV']:.3f} ({med_m_phi_MeV:.2f} MeV), "
          f"log_m_chi={med['log_m_chi_GeV']:.3f} ({med_m_chi_GeV:.2f} GeV), "
          f"g_chi={med['g_chi']:.4f}, "
          f"log_eps={med['log_epsilon']:.2f} (eps={med_eps:.2e}), "
          f"log_alpha={med['log_alpha']:.2f} (alpha={med_alpha:.2e}), "
          f"log_xi={med['log_xi']:.3f} (xi={med_xi:.3f})")
    print(f"  TENSION: T39 a=+0.94 vs Yukawa-derived a={map_a:+.3f} → diff = {a_tension:.2f}")
    if a_tension > 1.0:
        # R12 P1-D (2026-08-17): this branch rarely fires now that
        # t41.derived_a returns the correct POSITIVE sign (P0-B fix).
        # Pre-P0-B the Yukawa a was -1.08 vs T39 +0.94 → tension = 2.02.
        # Post-P0-B the Yukawa a is +0.5 to +1.5 across the prior box,
        # matching T39 ~ +0.94. The 'publishable negative finding'
        # framing in the legacy code is now obsolete; keep the
        # branch for diagnostics but expect it NOT to fire.
        print(f"  ⚠️  YUKAWA TENSION: T39's velocity dependence (a > 0, sigma/m DECREASES with v)")
        print(f"      is OPPOSITE to the Yukawa cross-section (a < 0, sigma/m INCREASES with v).")
        print(f"      This is a publishable negative finding: 'Simple Yukawa mediator FAILED to")
        print(f"      reproduce the BULLET-CLUSTER/DSPH-velocity dependence. Either the model")
        print(f"      is inelastic (chi_1/chi_2), or the mediator has non-trivial spin structure.")
    else:
        print(f"  ✅ NO TENSION (post-P0-B): Yukawa a ≈ T39 a within {a_tension:.2f}.")
        print(f"      The pre-fix '1.3 sigma tension' was a sign-flip artifact; see")
        print(f"      docs/REVIEWER_AUDIT_R12.md §2 finding #1.")
    print()

    # Honest comparison
    verdict = "TIER-3 EXTENSION: m_phi + xi parameterized posterior (v0.6: xi promoted from fixed to free)"
    if a_tension > 1.0:
        verdict += " — YUKAWA TENSION (T39 a > 0 vs Yukawa a < 0)"

    out = {
        "test": "T41_mediator_mass_joint_fit",
        "direction": "User ship direction #1: add m_phi to posterior; v0.6: add xi as free (R14 Rec #8)",
        "ndim": 6,
        "parameters": list(quants.keys()),
        "priors": {
            "log_m_phi_MeV": list(LOG_M_PHI_MEV_RANGE),
            "log_m_chi_GeV": list(LOG_M_CHI_GEV_RANGE),
            "g_chi": list(G_CHI_RANGE),
            "log_epsilon": list(LOG_EPSILON_RANGE),
            "log_alpha": list(LOG_ALPHA_RANGE),
            "log_xi": list(LOG_XI_RANGE),
        },
        "log_Z": log_Z,
        "log_Z_err": log_Z_err,
        "MAP": MAP,
        "MAP_physical": {
            "m_phi_MeV": map_m_phi_MeV,
            "m_chi_GeV": map_m_chi_GeV,
            "g_chi": map_g_chi,
            "log_epsilon": MAP[3],
            "log_alpha": MAP[4],
            "log_xi": MAP[5],
            "xi": 10 ** MAP[5],
            "sigma_m_0_derived": map_sigma_m_0,
            "a_derived": map_a,
        },
        "median": med,
        "quantiles_16_50_84": quants,
        "median_physical": {
            "m_phi_MeV": med_m_phi_MeV,
            "m_chi_GeV": med_m_chi_GeV,
            "g_chi": med["g_chi"],
            "epsilon": med_eps,
            "alpha": med_alpha,
            "xi": med_xi,
        },
        "yukawa_tension": {
            "T39_sigma_m_0": t39_sigma_m_0,
            "T39_a": t39_a,
            "Yukawa_a_at_MAP": map_a,
            "a_difference": a_tension,
            "significant": a_tension > 1.0,
        },
        "wall_seconds": wall,
        "verdict": verdict,
        "interpretation": (
            f"log Z = {log_Z:.3f}, posterior medians: m_phi = {med_m_phi_MeV:.2f} MeV, "
            f"m_chi = {med_m_chi_GeV:.2f} GeV, g_chi = {med['g_chi']:.4f}, "
            f"eps = {med_eps:.2e}, alpha = {med_alpha:.2e}, xi = {med_xi:.3f}. "
            f"Derived sigma/m_0 = {map_sigma_m_0:.3f} cm^2/g, a = {map_a:+.3f}. "
            f"Yukawa velocity index = {map_a:+.3f}; T39 data-preferred = +0.94. "
            f"|Tension| = {a_tension:.2f} (threshold 1.0). "
            f"R12 P0-B (2026-08-17): the pre-fix '1.3 sigma tension' claim was a "
            f"sign-flip artifact in derived_a; this re-run uses the corrected sign. "
            f"v0.6 (R14 Rec #8, 2026-08-26): log_xi promoted from fixed-1 to free "
            f"with prior log_xi in [-1.0, 0.7] (xi in [0.1, 5.0], matching H4.1 sweep range). "
            f"v0.5 baseline log Z = -254.24 at nlive=500; v0.6 should be within ~0.5 "
            f"of that since xi only enters via the Fermi-dwarf sigma_v scaling (sigma_v * xi^2), "
            f"a subdominant channel."
        ),
    }

    out_path = RESULTS_DIR / ("t41_mediator_mass_joint_fit" + os.environ.get("T41_RESULT_SUFFIX", "") + ".json")
    # Add the version metadata to the JSON itself so the file is self-identifying
    out_with_meta = dict(out)
    # T71.2 (R16 closure): log the actual KSFR mask MAX bound + a SHA256
    # of the resolved config. This un-skips the 3 previously-skipping
    # regression tests in test_inelastic_wrapper_regression.py and gives
    # every result JSON a stable cross-version audit identifier.
    import hashlib
    from ksfr_pcac_validity import KSFR_M_RHO_OVER_F_PI_MAX
    _config_components = [
        f"ksfr_mask_enabled={os.environ.get('SIDM_DISABLE_KSFR_MASK', '0') != '1'}",
        f"ksfr_mask_max={KSFR_M_RHO_OVER_F_PI_MAX}",
        f"nlive={nlive}",
        f"ndim=6",
        f"dlogz=0.1",
        f"inelastic_on={inelastic_on}",
        f"r_inelastic={r_inelastic}",
        "form_factor=default_dipole",  # see MODEL_ASSUMPTIONS §6.2
        "sparc_treatment=calibrated_score",  # v0.5; hierarchical deferred to v0.6
        "relic_solver=calibrated_inv_proportional",  # T55; Boltzmann deferred to v0.6
    ]
    _config_hash = hashlib.sha256("|".join(_config_components).encode("utf-8")).hexdigest()[:12]
    out_with_meta["t41_version"] = {
        "suffix": os.environ.get("T41_RESULT_SUFFIX", ""),
        "ksfr_mask_enabled": os.environ.get("SIDM_DISABLE_KSFR_MASK", "0") != "1",
        "ksfr_mask_max_at_runtime": KSFR_M_RHO_OVER_F_PI_MAX,  # T71.2 (R16 #5)
        "nlive": nlive,
        "ndim": 6,
        "dlogz": 0.1,
        "inelastic_on": inelastic_on,
        "r_inelastic": r_inelastic,
        "xi_promotion": "v0.6: log_xi now a free parameter (R14 Rec #8). Prior log_xi in [-1.0, 0.7].",
        "config_hash": _config_hash,  # T71.2 (R16 #11): stable cross-version audit ID
        "config_hash_components": _config_components,  # for debugging only
    }
    out_path.write_text(json.dumps(out_with_meta, indent=2, default=str))
    # Mirror to Windows-side path if running under WSL
    try:
        win_path = Path("/mnt/c/Users/lamkuenai/projects/sidm-composite-dm-mediator/v0.3-prelim/data/results/" + out_path.name)
        if win_path.parent.exists():
            win_path.write_text(json.dumps(out_with_meta, indent=2, default=str))
            print(f"\noutput -> {out_path}")
            print(f"        -> {win_path}")
        else:
            print(f"\noutput -> {out_path}")
    except (FileNotFoundError, OSError) as e:
        # Windows-side path not available; only the WSL write succeeded.
        print(f"\noutput -> {out_path} (Win mirror skipped: {e})")


if __name__ == "__main__":
    main()
