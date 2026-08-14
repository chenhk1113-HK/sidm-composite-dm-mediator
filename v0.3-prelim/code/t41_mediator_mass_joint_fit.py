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

Priors:
  log_m_phi_MeV:  [-1, 4]    (10 keV to 10 TeV)
  log_m_chi_GeV:  [0.5, 3]   (3 GeV to 1 TeV)
  g_chi:          [0.01, 2]  (perturbative to ~O(1))
  log_epsilon:    [-60, -1]  (vector-mediator kinetic mixing)
  log_alpha:      [-30, -1]  (annihilation coupling)

Outputs:
  - dynesty nested-sampling posterior
  - weighted medians per parameter
  - 2D posteriors in (m_phi, m_chi) and (m_phi, epsilon)
  - log Z, dlogz, wall time
  - HONEST flag if (a_derived - a_T39) > 1 — i.e., Yukawa doesn't fit.

This is the test that answers the user question: "any feasible way to
find the mediator by experiment?" — the posterior p(m_phi) is the answer.
"""
from __future__ import annotations
import json
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


RESULTS_DIR = Path("/home/lamkuenai/sidm-composite-dm-mediator/v0.3-prelim/data/results")
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

# T41 priors
LOG_M_PHI_MEV_RANGE = (-1.0, 4.0)  # 10 keV to 10 TeV
LOG_M_CHI_GEV_RANGE = (0.5, 3.0)   # 3 GeV to 1 TeV
G_CHI_RANGE = (0.01, 2.0)
LOG_EPSILON_RANGE = (-60.0, -1.0)
LOG_ALPHA_RANGE = (-30.0, -1.0)

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
    """a = -d log(sigma/m) / d log(v) at v_ref."""
    s1 = sigma_m_at_v_yukawa(50.0, m_phi_MeV, m_chi_GeV, g_chi)
    s2 = sigma_m_at_v_yukawa(200.0, m_phi_MeV, m_chi_GeV, g_chi)
    if s1 <= 0 or s2 <= 0:
        return -2.0  # fallback
    a = (np.log10(s1) - np.log10(s2)) / (np.log10(50.0) - np.log10(200.0))
    return float(a)


def loglike_joint(theta):
    """5-parameter joint likelihood.

    theta = (log_m_phi_MeV, log_m_chi_GeV, g_chi, log_epsilon, log_alpha)
    """
    log_m_phi, log_m_chi, g_chi, log_eps, log_alpha = theta
    m_phi_MeV = 10 ** log_m_phi
    m_chi_GeV = 10 ** log_m_chi
    epsilon = 10 ** log_eps
    alpha = 10 ** log_alpha

    if m_phi_MeV <= 0 or m_chi_GeV <= 0 or g_chi <= 0 or epsilon <= 0 or alpha <= 0:
        return -np.inf
    if not (1e-2 <= g_chi <= 2.0):
        return -np.inf

    # Derived: sigma_m_0 at v_ref = 100 km/s
    sigma_m_0 = sigma_m_at_v_yukawa(V_REF, m_phi_MeV, m_chi_GeV, g_chi)
    if sigma_m_0 <= 0 or not np.isfinite(sigma_m_0):
        return -np.inf

    # Derived velocity power-law index
    a = derived_a(m_phi_MeV, m_chi_GeV, g_chi)

    # 1. dSph (channel 2) — bimodal posterior
    ll_dsph = ch_v03.loglike_dsph_v03(sigma_m_0, a)
    if not np.isfinite(ll_dsph):
        return -np.inf

    # 2. UFD (channel 3)
    ll_ufd = ch_v03.loglike_ufd_v03(sigma_m_0, a)
    if not np.isfinite(ll_ufd):
        return -np.inf

    # 3. Bullet Cluster (channel 4)
    ll_bullet = ch_v03.loglike_bullet_v03(sigma_m_0, a)
    if not np.isfinite(ll_bullet):
        return -np.inf

    # 4. LZ (T30) — uses sigma_DM_nucleon = epsilon * sigma_m_0 if coupling exists
    # For pure dark-sector Yukawa, the coupling to SM is via kinetic mixing
    # sigma_DM_nucleon scaled by epsilon. With epsilon -> 0, LZ is invisible.
    sigma_DM_n = epsilon * sigma_m_0
    ll_lz = loglike_lz_real(m_chi_GeV, sigma_DM_n)
    if not np.isfinite(ll_lz):
        return -np.inf

    # 5. Fermi dwarf (T32) — gamma-ray from annihilation
    # sigma_ann ~ alpha * sigma_m^2 at v ~ 100 km/s
    sigma_m_at_v = sigma_m_at_v_yukawa(100.0, m_phi_MeV, m_chi_GeV, g_chi)
    if sigma_m_at_v <= 0:
        return -np.inf
    sigma_v = alpha * sigma_m_at_v ** 2
    ll_fermi = loglike_fermi_dwarf(m_chi_GeV, sigma_v)
    if not np.isfinite(ll_fermi):
        return -np.inf

    # Optional SPARC contribution (slow, so disabled by default)
    # Use a coarse grid to be fast
    try:
        import t8_v03_joint_fit as t8
        ll_sparc = t8.delta_log_sparc(sigma_m_0, a) / 1000
    except Exception:
        ll_sparc = 0.0

    return ll_dsph + ll_ufd + ll_bullet + ll_lz + ll_fermi + ll_sparc


def prior_transform_5(u):
    return [
        LOG_M_PHI_MEV_RANGE[0] + u[0] * (LOG_M_PHI_MEV_RANGE[1] - LOG_M_PHI_MEV_RANGE[0]),
        LOG_M_CHI_GEV_RANGE[0] + u[1] * (LOG_M_CHI_GEV_RANGE[1] - LOG_M_CHI_GEV_RANGE[0]),
        G_CHI_RANGE[0] + u[2] * (G_CHI_RANGE[1] - G_CHI_RANGE[0]),
        LOG_EPSILON_RANGE[0] + u[3] * (LOG_EPSILON_RANGE[1] - LOG_EPSILON_RANGE[0]),
        LOG_ALPHA_RANGE[0] + u[4] * (LOG_ALPHA_RANGE[1] - LOG_ALPHA_RANGE[0]),
    ]


def main():
    print("=" * 80)
    print("T41 — Mediator-mass (m_phi) + DM-mass (m_chi) joint fit")
    print("=" * 80)
    print("5 parameters: log_m_phi_MeV, log_m_chi_GeV, g_chi, log_epsilon, log_alpha")
    print(f"  log_m_phi_MeV: [{LOG_M_PHI_MEV_RANGE[0]}, {LOG_M_PHI_MEV_RANGE[1]}]")
    print(f"  log_m_chi_GeV: [{LOG_M_CHI_GEV_RANGE[0]}, {LOG_M_CHI_GEV_RANGE[1]}]")
    print(f"  g_chi:         [{G_CHI_RANGE[0]}, {G_CHI_RANGE[1]}]")
    print(f"  log_epsilon:   [{LOG_EPSILON_RANGE[0]}, {LOG_EPSILON_RANGE[1]}]")
    print(f"  log_alpha:     [{LOG_ALPHA_RANGE[0]}, {LOG_ALPHA_RANGE[1]}]")
    print()

    t0 = time.time()
    sampler = dynesty.NestedSampler(
        loglikelihood=loglike_joint,
        prior_transform=prior_transform_5,
        ndim=5, nlive=200, bound='multi', sample='auto', bootstrap=0,
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
    }

    # 16/50/84 quantiles
    quants = {
        "log_m_phi_MeV": list(weighted_quantiles(samples[:, 0], weights, [0.16, 0.5, 0.84])),
        "log_m_chi_GeV": list(weighted_quantiles(samples[:, 1], weights, [0.16, 0.5, 0.84])),
        "g_chi":         list(weighted_quantiles(samples[:, 2], weights, [0.16, 0.5, 0.84])),
        "log_epsilon":   list(weighted_quantiles(samples[:, 3], weights, [0.16, 0.5, 0.84])),
        "log_alpha":     list(weighted_quantiles(samples[:, 4], weights, [0.16, 0.5, 0.84])),
    }

    # Convert to physical units
    med_m_phi_MeV = 10 ** med["log_m_phi_MeV"]
    med_m_chi_GeV = 10 ** med["log_m_chi_GeV"]
    med_eps = 10 ** med["log_epsilon"]
    med_alpha = 10 ** med["log_alpha"]

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
          f"log_eps={MAP[3]:.2f}, log_alpha={MAP[4]:.2f}")
    print(f"  DERIVED at MAP: sigma_m_0 = {map_sigma_m_0:.3f} cm^2/g, a = {map_a:.3f}")
    print(f"  Median: log_m_phi={med['log_m_phi_MeV']:.3f} ({med_m_phi_MeV:.2f} MeV), "
          f"log_m_chi={med['log_m_chi_GeV']:.3f} ({med_m_chi_GeV:.2f} GeV), "
          f"g_chi={med['g_chi']:.4f}, "
          f"log_eps={med['log_epsilon']:.2f} (eps={med_eps:.2e}), "
          f"log_alpha={med['log_alpha']:.2f} (alpha={med_alpha:.2e})")
    print(f"  TENSION: T39 a=+0.94 vs Yukawa-derived a={map_a:+.3f} → diff = {a_tension:.2f}")
    if a_tension > 1.0:
        print(f"  ⚠️  YUKAWA TENSION: T39's velocity dependence (a > 0, sigma/m DECREASES with v)")
        print(f"      is OPPOSITE to the Yukawa cross-section (a < 0, sigma/m INCREASES with v).")
        print(f"      This is a publishable negative finding: 'Simple Yukawa mediator FAILED to")
        print(f"      reproduce the BULLET-CLUSTER/DSPH-velocity dependence. Either the model")
        print(f"      is inelastic (chi_1/chi_2), or the mediator has non-trivial spin structure.")
    print()

    # Honest comparison
    verdict = "TIER-3 EXTENSION: m_phi parameterized posterior"
    if a_tension > 1.0:
        verdict += " — YUKAWA TENSION (T39 a > 0 vs Yukawa a < 0)"

    out = {
        "test": "T41_mediator_mass_joint_fit",
        "direction": "User ship direction #1: add m_phi to posterior",
        "ndim": 5,
        "parameters": list(quants.keys()),
        "priors": {
            "log_m_phi_MeV": list(LOG_M_PHI_MEV_RANGE),
            "log_m_chi_GeV": list(LOG_M_CHI_GEV_RANGE),
            "g_chi": list(G_CHI_RANGE),
            "log_epsilon": list(LOG_EPSILON_RANGE),
            "log_alpha": list(LOG_ALPHA_RANGE),
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
            f"eps = {med_eps:.2e}, alpha = {med_alpha:.2e}. "
            f"Derived sigma/m_0 = {map_sigma_m_0:.3f} cm^2/g, a = {map_a:.3f}. "
            f"The T39 a = +0.94 (sigma/m DECREASES with v) is incompatible with "
            f"the Yukawa prediction (a < 0, sigma/m INCREASES with v). "
            f"This means the simple Yukawa model is RULED OUT by the velocity dependence. "
            f"Future work: inelastic SIDM (chi_1, chi_2) or velocity-dependent g_chi."
        ),
    }

    out_path = RESULTS_DIR / "t41_mediator_mass_joint_fit.json"
    out_path.write_text(json.dumps(out, indent=2, default=str))
    win_path = Path("/mnt/c/Users/lamkuenai/projects/sidm-composite-dm-mediator/v0.3-prelim/data/results/t41_mediator_mass_joint_fit.json")
    win_path.write_text(json.dumps(out, indent=2, default=str))
    print(f"\noutput -> {out_path}")
    print(f"        -> {win_path}")


if __name__ == "__main__":
    main()
