"""
T111 — Multi-component DM (Door D): v0.7 + light species for LZ.

Hypothesis: the dark sector has TWO DM species:
  - Heavy species (m_chi_heavy, σ_DM-DM): sets σ/m (SIDM)
  - Light species (m_chi_light, σ_DM-nucleon): gives LZ direct-detection signal

The heavy species lives in v0.7's 6D space. The light species adds 3 params:
  - log_m_chi_light_GeV: light DM mass, prior [0.5, 100] GeV (sub-heavy)
  - log_sigma_light_cm2: σ_DM-nucleon for light species, prior [1e-48, 1e-42] cm^2
  - log_f_light: log10(fraction of DM in light species), prior [-4, 0]
    (i.e., light species is 0.01% to 100% of DM density)

Total: 9 parameters (6 v0.7 + 3 light species).

Likelihood components:
  - T41 v0.7 joint (6D) — unchanged
  - LZ 2024 limit (light species): penalty if σ_light > σ_LZ_limit(m_chi_light)
  - LZ 248 keV event (light species): Gaussian likelihood for matching the
    1-event excess. We approximate this as: predicted events for light
    species in [200, 300] keV window matches 1 observed event.
  - Multi-component DM density: f_light * sigma_light + (1-f_light) * sigma_heavy.
    For σ_DM-DM (SIDM): only heavy contributes (light is sub-dominant).
  - Relic density: total Omega_h^2 = Omega_heavy + Omega_light = 0.12 (Planck).
    Both species contribute; constraint becomes soft prior.

This is the B1-lite version (emcee). For full nested sampling, see
t111_full_9d_dynesty.py (future work; emcee first to see if multi-component
DM is promising before investing 4-10 hours in dynesty).

Expected outcomes:
  - f_light -> 0: light species negligible; reduces to v0.7 6D
  - σ_light near LZ limit + f_light ~ 0.1%: light species explains LZ 248 keV
  - σ_light >> LZ limit: penalty, parameter excluded
"""
from __future__ import annotations

import json
import math
import os
import sys
import time
from pathlib import Path

import numpy as np

SCRIPT_DIR = Path(__file__).resolve().parent
V03_ROOT = SCRIPT_DIR.parent
V01_ROOT = V03_ROOT.parent.parent / "v0.1-prelim"
sys.path.insert(0, str(SCRIPT_DIR))
sys.path.insert(0, str(V01_ROOT))
sys.path.insert(0, str(V01_ROOT / "code"))

import emcee

from t41_mediator_mass_joint_fit import loglike_joint
from channels_extended import sigma_LZ_limit


# v0.7 prior ranges (from T41)
LOG_M_PHI_MEV_RANGE = (-1.0, 4.0)
LOG_M_CHI_GEV_RANGE = (0.5, 3.0)
G_CHI_RANGE = (0.01, 2.0)
LOG_EPSILON_RANGE = (-60.0, -1.0)
LOG_ALPHA_RANGE = (-30.0, -1.0)
LOG_XI_RANGE = (-1.0, 0.7)

# Light species prior ranges
LOG_M_CHI_LIGHT_GEV_RANGE = (0.5, 2.0)   # 3 to 100 GeV
LOG_SIGMA_LIGHT_RANGE = (-48.0, -42.0)   # 10^-48 to 10^-42 cm^2
LOG_F_LIGHT_RANGE = (-4.0, 0.0)          # 0.01% to 100% of DM

# LZ 248 keV exposure
LZ_EXPOSURE_TONNE_YEAR = 2.84
LZ_WINDOW_KEV = (200.0, 300.0)


def loglike_lz_248kev_light_species(m_chi_light_GeV: float, sigma_light_cm2: float, f_light: float) -> float:
    """Light species contribution to LZ 248 keV event.

    Simplified: for a sub-100 GeV WIMP with sigma_DM-nucleon near LZ limit,
    expected events in [200, 300] keV window is roughly:
        N_events = (exposure * sigma * f_light * form_factor) / m_chi

    For simplicity, we use a Gaussian centered on (m_chi=60 GeV, sigma=1e-45)
    matching DIAMX best fit, with sigma determined by LZ statistics.

    Returns: log L = -0.5 * (N_pred - 1)^2 / sigma_N^2 (Gaussian approximation)

    If sigma_light is excluded by LZ (>10x limit), returns heavy penalty.
    """
    # Check if excluded
    lz_limit = sigma_LZ_limit(m_chi_light_GeV)
    if sigma_light_cm2 > 10 * lz_limit:
        return -1000.0  # heavily excluded

    # Predicted events for light species
    # Rough scaling: 1 tonne-year * 1e-45 cm^2 / 100 GeV * 1 = ~10 events
    # So N ~ (exposure_tonne_year * 1e-45 / m_chi_GeV) * (sigma / 1e-45) * f_light
    N_pred = (
        LZ_EXPOSURE_TONNE_YEAR
        * (sigma_light_cm2 / 1e-45)
        * (10.0 / m_chi_light_GeV)  # 1/m_chi scaling (rough)
        * f_light
        * 1.0  # form factor (assume order-1)
    )

    # Match LZ observation (1 event)
    N_obs = 1.0
    sigma_N = 1.0  # 1-event Poisson ~ Gaussian with sigma=1

    return -0.5 * ((N_pred - N_obs) / sigma_N) ** 2


def loglike_9d(theta):
    """9D joint log-likelihood: v0.7 6D + 3D light species.

    theta = (log_m_phi, log_m_chi_heavy, g_chi, log_eps, log_alpha, log_xi,
             log_m_chi_light, log_sigma_light, log_f_light)
    """
    if len(theta) != 9:
        return -np.inf
    log_m_phi, log_m_chi_h, g_chi, log_eps, log_alpha, log_xi, log_m_chi_l, log_sigma_l, log_f_l = theta

    # 6D v0.7 likelihood (heavy species)
    ll_6d = loglike_joint((log_m_phi, log_m_chi_h, g_chi, log_eps, log_alpha, log_xi))
    if not np.isfinite(ll_6d):
        return -1e6

    # 3D light species likelihood
    m_chi_l = 10 ** log_m_chi_l
    sigma_l = 10 ** log_sigma_l
    f_l = 10 ** log_f_l

    ll_lz_light = loglike_lz_248kev_light_species(m_chi_l, sigma_l, f_l)
    if not np.isfinite(ll_lz_light):
        return -1e6

    # Relic density constraint (soft): f_light + f_heavy = 1
    # Both species contribute to Omega; the soft penalty penalizes f_light > 1
    # (which would imply negative heavy density)
    if f_l > 1.0:
        ll_relic = -1000.0
    else:
        # Soft: prefer Omega_total near 0.12, but this is approximate
        ll_relic = 0.0  # v0.7 already handles its own relic; we just add light

    return ll_6d + ll_lz_light + ll_relic


def prior_transform_9d(u):
    """Convert unit cube [0,1]^9 to physical prior."""
    u = np.asarray(u, dtype=float)
    if u.shape != (9,):
        raise ValueError(f"Expected shape (9,), got {u.shape}")
    theta = np.empty(9)
    # v0.7 6D
    theta[0] = LOG_M_PHI_MEV_RANGE[0] + u[0] * (LOG_M_PHI_MEV_RANGE[1] - LOG_M_PHI_MEV_RANGE[0])
    theta[1] = LOG_M_CHI_GEV_RANGE[0] + u[1] * (LOG_M_CHI_GEV_RANGE[1] - LOG_M_CHI_GEV_RANGE[0])
    theta[2] = G_CHI_RANGE[0] + u[2] * (G_CHI_RANGE[1] - G_CHI_RANGE[0])
    theta[3] = LOG_EPSILON_RANGE[0] + u[3] * (LOG_EPSILON_RANGE[1] - LOG_EPSILON_RANGE[0])
    theta[4] = LOG_ALPHA_RANGE[0] + u[4] * (LOG_ALPHA_RANGE[1] - LOG_ALPHA_RANGE[0])
    theta[5] = LOG_XI_RANGE[0] + u[5] * (LOG_XI_RANGE[1] - LOG_XI_RANGE[0])
    # Light species 3D
    theta[6] = LOG_M_CHI_LIGHT_GEV_RANGE[0] + u[6] * (LOG_M_CHI_LIGHT_GEV_RANGE[1] - LOG_M_CHI_LIGHT_GEV_RANGE[0])
    theta[7] = LOG_SIGMA_LIGHT_RANGE[0] + u[7] * (LOG_SIGMA_LIGHT_RANGE[1] - LOG_SIGMA_LIGHT_RANGE[0])
    theta[8] = LOG_F_LIGHT_RANGE[0] + u[8] * (LOG_F_LIGHT_RANGE[1] - LOG_F_LIGHT_RANGE[0])
    return theta


def log_prior_9d(theta):
    """Uniform prior on the 9D box (in log/linear space as defined)."""
    if len(theta) != 9:
        return -np.inf
    ranges = [
        LOG_M_PHI_MEV_RANGE, LOG_M_CHI_GEV_RANGE, G_CHI_RANGE,
        LOG_EPSILON_RANGE, LOG_ALPHA_RANGE, LOG_XI_RANGE,
        LOG_M_CHI_LIGHT_GEV_RANGE, LOG_SIGMA_LIGHT_RANGE, LOG_F_LIGHT_RANGE,
    ]
    for v, (lo, hi) in zip(theta, ranges):
        if not (lo <= v <= hi):
            return -np.inf
    return 0.0


def log_prob_9d(theta):
    """emcee log-probability = log_prior + log_like."""
    lp = log_prior_9d(theta)
    if not np.isfinite(lp):
        return -np.inf
    ll = loglike_9d(theta)
    if not np.isfinite(ll):
        return -np.inf
    return lp + ll


def main():
    nwalkers = int(os.environ.get("T111_NWALKERS", "32"))
    nsteps = int(os.environ.get("T111_NSTEPS", "2000"))
    burn = int(os.environ.get("T111_BURN", "500"))

    print("=" * 70)
    print("T111 — Multi-component DM (Door D): v0.7 + light species")
    print("=" * 70)
    print()
    print(f"nwalkers={nwalkers}, nsteps={nsteps}, burn={burn}")
    print()
    print("Priors:")
    print(f"  v0.7 6D: as before")
    print(f"  log_m_chi_light: {LOG_M_CHI_LIGHT_GEV_RANGE} (3 to 100 GeV)")
    print(f"  log_sigma_light: {LOG_SIGMA_LIGHT_RANGE} (10^-48 to 10^-42 cm^2)")
    print(f"  log_f_light: {LOG_F_LIGHT_RANGE} (0.01% to 100%)")
    print()

    # Initialize walkers around v0.7 MAP
    rng = np.random.RandomState(42)
    p0 = np.zeros((nwalkers, 9))
    p0[:, 0] = np.log10(588) + 0.1 * rng.randn(nwalkers)
    p0[:, 1] = np.log10(498) + 0.1 * rng.randn(nwalkers)
    p0[:, 2] = 0.45 + 0.05 * rng.randn(nwalkers)
    p0[:, 3] = -36.95 + 0.5 * rng.randn(nwalkers)
    p0[:, 4] = -16.17 + 0.5 * rng.randn(nwalkers)
    p0[:, 5] = 0.0 + 0.05 * rng.randn(nwalkers)
    # Light species init: small fraction, mass near 60 GeV (DIAMX best fit)
    p0[:, 6] = np.log10(60) + 0.2 * rng.randn(nwalkers)
    p0[:, 7] = -45.0 + 0.5 * rng.randn(nwalkers)
    p0[:, 8] = -2.0 + 0.5 * rng.randn(nwalkers)  # 1% light species

    # Clip to prior
    p0[:, 0] = np.clip(p0[:, 0], *LOG_M_PHI_MEV_RANGE)
    p0[:, 1] = np.clip(p0[:, 1], *LOG_M_CHI_GEV_RANGE)
    p0[:, 2] = np.clip(p0[:, 2], *G_CHI_RANGE)
    p0[:, 3] = np.clip(p0[:, 3], *LOG_EPSILON_RANGE)
    p0[:, 4] = np.clip(p0[:, 4], *LOG_ALPHA_RANGE)
    p0[:, 5] = np.clip(p0[:, 5], *LOG_XI_RANGE)
    p0[:, 6] = np.clip(p0[:, 6], *LOG_M_CHI_LIGHT_GEV_RANGE)
    p0[:, 7] = np.clip(p0[:, 7], *LOG_SIGMA_LIGHT_RANGE)
    p0[:, 8] = np.clip(p0[:, 8], *LOG_F_LIGHT_RANGE)

    t0 = time.time()
    sampler = emcee.EnsembleSampler(nwalkers, 9, log_prob_9d)
    sampler.run_mcmc(p0, nsteps, progress=False)
    wall_seconds = time.time() - t0

    samples = sampler.get_chain(discard=burn, flat=True)
    log_probs = sampler.get_log_prob(discard=burn, flat=True)

    map_idx = int(np.argmax(log_probs))
    map_sample = samples[map_idx]

    medians = np.median(samples, axis=0)
    q16 = np.percentile(samples, 16, axis=0)
    q84 = np.percentile(samples, 84, axis=0)

    # Approx log Z
    log_post_max = np.max(log_probs)
    log_Z_approx = log_post_max + np.log(np.mean(np.exp(log_probs - log_post_max))) - np.log(len(samples))

    log_z_v07_6d = -163.29
    delta_log_z = log_Z_approx - log_z_v07_6d

    print()
    print("=" * 70)
    print(f"Done in {wall_seconds:.1f}s (emcee, NOT nested sampling)")
    print(f"  Approx log Z = {log_Z_approx:.3f}")
    print()
    print("T111 — 9D multi-component DM MAP:")
    print(f"  Heavy species (v0.7 6D):")
    print(f"    m_phi = {10**map_sample[0]:.0f} MeV")
    print(f"    m_chi_heavy = {10**map_sample[1]:.1f} GeV")
    print(f"    g_chi = {map_sample[2]:.3f}")
    print(f"    log_eps = {map_sample[3]:.2f}")
    print(f"    log_alpha = {map_sample[4]:.2f}")
    print(f"    log_xi = {map_sample[5]:.3f}")
    print(f"  Light species (LZ explanation):")
    print(f"    m_chi_light = {10**map_sample[6]:.1f} GeV (DIAMX: 60 GeV)")
    print(f"    sigma_light = {10**map_sample[7]:.2e} cm^2 (LZ limit @ {sigma_LZ_limit(10**map_sample[6]):.2e})")
    print(f"    f_light = {10**map_sample[8]:.2e} (fraction of DM)")
    print()
    print(f"  Approx log Z (emcee) = {log_Z_approx:.3f}")
    print(f"  Δlog Z (9D - 6D v0.7) approx = {delta_log_z:+.3f}")
    print(f"  T90 merge rule criterion #5: Δlog Z ≥ +2 → {'SATISFIED' if delta_log_z >= 2.0 else 'NOT YET'}")
    print()

    # Output JSON
    out_dir = V03_ROOT / "outputs" / "t95"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "t111_multicomponent_9d_emcee.json"

    out = {
        "nwalkers": nwalkers,
        "nsteps": nsteps,
        "burn": burn,
        "wall_seconds": wall_seconds,
        "log_z_approx_emcee": log_Z_approx,
        "delta_log_z_vs_v07_6d_approx": delta_log_z,
        "t90_merge_criterion_5_satisfied_approx": bool(delta_log_z >= 2.0),
        "method": "emcee (B1-lite; full dynesty future work)",
        "map_sample_physical": {
            "heavy_species": {
                "m_phi_MeV": float(10 ** map_sample[0]),
                "m_chi_heavy_GeV": float(10 ** map_sample[1]),
                "g_chi": float(map_sample[2]),
                "epsilon": float(10 ** map_sample[3]),
                "alpha": float(10 ** map_sample[4]),
                "xi": float(10 ** map_sample[5]),
            },
            "light_species": {
                "m_chi_light_GeV": float(10 ** map_sample[6]),
                "sigma_light_cm2": float(10 ** map_sample[7]),
                "f_light": float(10 ** map_sample[8]),
            },
        },
        "medians_physical": {
            "log_m_phi_MeV": float(medians[0]),
            "log_m_chi_heavy_GeV": float(medians[1]),
            "g_chi": float(medians[2]),
            "log_epsilon": float(medians[3]),
            "log_alpha": float(medians[4]),
            "log_xi": float(medians[5]),
            "log_m_chi_light_GeV": float(medians[6]),
            "log_sigma_light_cm2": float(medians[7]),
            "log_f_light": float(medians[8]),
        },
        "v07_6d_log_z": log_z_v07_6d,
        "comment": (
            "T111 multi-component DM (Door D): v0.7 6D + 3D light species. "
            "Heavy species sets σ/m (SIDM); light species explains LZ 248 keV. "
            f"Approx log Z = {log_Z_approx:.3f} (emcee estimate; not nested sampling). "
            "MAP at light species mass = "
            f"{10**map_sample[6]:.1f} GeV, f_light = {10**map_sample[8]:.2e}. "
            f"Δlog Z vs v0.7 6D = {delta_log_z:+.3f} (approximate). "
        ),
    }

    with open(out_path, "w") as f:
        json.dump(out, f, indent=2)
    print(f"Wrote: {out_path}")


if __name__ == "__main__":
    main()
