#!/usr/bin/env python
"""
T7 — Joint 4-channel SIDM cross-section posterior.

Uses dynesty nested sampling to find the joint posterior on
(log_sigma_m_0, a) given:
    Channel 1: SPARC rotation curves (175 galaxies) — implicit prior
                via the sigma/m → r_core → cored profile mechanism
                (encoded as a flat prior since SPARC doesn't constrain σ/m)
    Channel 2: MW dSph kinematics (Horigome+ 2025 bimodal posterior)
    Channel 3: UFD stellar cores (Sanchez-Almeida+ 2025)
    Channel 4: Bullet Cluster JWST (Cha+ 2025 upper limit)

Output: t7_joint_posterior.json with log Z, posterior samples, marginalized posteriors.
"""
from __future__ import annotations
import sys
import json
import time
from pathlib import Path
import numpy as np
import dynesty

sys.path.insert(0, str(Path(__file__).resolve().parent))
from sidm_velocity_dependent import (
    loglike_joint_4channel,
    sigma_m_effective, r_core_from_sigma_m, V_REF,
)

RESULTS_DIR = Path("/home/lamkuenai/sidm-composite-dm-mediator/v0.2-prelim/data/results")
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

# Priors (broad, weakly informative)
LOG_SIGMA_M_0_RANGE = (-3.0, 2.5)  # log10(cm^2/g) at v_ref = 100 km/s
A_RANGE = (-2.0, 2.0)              # velocity power-law index

NLIVE = 500
DLOGZ = 0.10


def main():
    def loglike(theta):
        log_sm, a = theta
        sigma_m_0 = 10**log_sm
        return loglike_joint_4channel(sigma_m_0, a)

    def prior_transform(u):
        return np.array([
            LOG_SIGMA_M_0_RANGE[0] + u[0] * (LOG_SIGMA_M_0_RANGE[1] - LOG_SIGMA_M_0_RANGE[0]),
            A_RANGE[0] + u[1] * (A_RANGE[1] - A_RANGE[0]),
        ])

    print(f"[T7] Running joint 4-channel dynesty fit...")
    print(f"  Priors: log10(sigma/m)_0 in {LOG_SIGMA_M_0_RANGE}")
    print(f"          a in {A_RANGE}")
    print(f"  nlive={NLIVE}, dlogz={DLOGZ}")

    t0 = time.time()
    sampler = dynesty.NestedSampler(
        loglikelihood=loglike,
        prior_transform=prior_transform,
        ndim=2,
        nlive=NLIVE,
        bound='multi', sample='auto', bootstrap=0,
    )
    sampler.run_nested(dlogz=DLOGZ, print_progress=False)
    res = sampler.results
    wall = time.time() - t0

    log_Z = float(res.logz[-1])
    log_Z_err = float(res.logzerr[-1])
    samples = res.samples  # shape (n_samples, 2): (log_sigma_m_0, a)
    weights = np.exp(res.logwt - res.logz[-1])

    # 1D marginal posteriors
    log_sm_samples = samples[:, 0]
    a_samples = samples[:, 1]
    sm_samples = 10**log_sm_samples

    # Find MAP
    imap = int(np.argmax(weights))
    log_sm_MAP = float(log_sm_samples[imap])
    a_MAP = float(a_samples[imap])

    # Credible intervals (16/50/84 percentiles)
    log_sm_p16, log_sm_p50, log_sm_p84 = np.percentile(log_sm_samples, [16, 50, 84])
    a_p16, a_p50, a_p84 = np.percentile(a_samples, [16, 50, 84])
    sm_p16, sm_p50, sm_p84 = np.percentile(sm_samples, [16, 50, 84])

    # BMA evidence splits: bimodal vs unimodal?
    # Compute the two local maxima from the 1D marginalized posterior
    from scipy.signal import find_peaks
    hist, bin_edges = np.histogram(log_sm_samples, bins=50, weights=weights)
    bin_centers = 0.5 * (bin_edges[:-1] + bin_edges[1:])
    peaks, _ = find_peaks(hist, height=hist.max() * 0.1)
    peak_positions = bin_centers[peaks]
    peak_heights = hist[peaks]
    print(f"  Found {len(peaks)} peaks in 1D marginalized posterior:")
    for pos, h in zip(peak_positions, peak_heights):
        print(f"    log10(sigma/m) = {pos:+.2f}  (height {h:.4f})")

    # Effective cross-section at three scales
    V_DWARF = 30.0
    V_GAL = 100.0
    V_CLUSTER = 1500.0
    sm_eff_dwarf = sigma_m_effective(10**log_sm_MAP, a_MAP, V_DWARF)
    sm_eff_gal   = sigma_m_effective(10**log_sm_MAP, a_MAP, V_GAL)
    sm_eff_cluster = sigma_m_effective(10**log_sm_MAP, a_MAP, V_CLUSTER)
    print(f"  At MAP (log_sm={log_sm_MAP:.2f}, a={a_MAP:.2f}):")
    print(f"    sigma/m (v=30 km/s, dwarf):    {sm_eff_dwarf:.3f} cm^2/g")
    print(f"    sigma/m (v=100 km/s, galaxy):  {sm_eff_gal:.3f} cm^2/g")
    print(f"    sigma/m (v=1500 km/s, cluster):{sm_eff_cluster:.3f} cm^2/g")

    out = {
        "test": "T7_joint_4channel",
        "log_Z": log_Z,
        "log_Z_err": log_Z_err,
        "MAP": {
            "log_sigma_m_0": log_sm_MAP,
            "sigma_m_0_cm2_per_g": 10**log_sm_MAP,
            "a": a_MAP,
        },
        "median_posterior": {
            "log_sigma_m_0_p50": float(log_sm_p50),
            "a_p50": float(a_p50),
            "sigma_m_0_cm2_per_g_p50": float(10**log_sm_p50),
            "log_sigma_m_0_p16": float(log_sm_p16),
            "log_sigma_m_0_p84": float(log_sm_p84),
            "a_p16": float(a_p16),
            "a_p84": float(a_p84),
            "sigma_m_0_cm2_per_g_p16": float(sm_p16),
            "sigma_m_0_cm2_per_g_p84": float(sm_p84),
        },
        "effective_cross_sections_at_MAP": {
            "dwarf_v30_kms":    float(sm_eff_dwarf),
            "galaxy_v100_kms":  float(sm_eff_gal),
            "cluster_v1500_kms":float(sm_eff_cluster),
        },
        "bimodal_peaks_log_sigma_m_0": [float(p) for p in peak_positions],
        "bimodal_peaks_sigma_m_0": [float(10**p) for p in peak_positions],
        "bimodal_peak_heights": [float(h) for h in peak_heights],
        "n_samples": int(samples.shape[0]),
        "wall_seconds": float(wall),
        "nlive": int(NLIVE),
        "channels_used": {
            "channel_2_dsph": "Horigome+ 2025 (arXiv 2503.13650) bimodal posterior",
            "channel_3_ufd":  "Sanchez-Almeida+ 2025 A&A, sigma/m = 10^0.92 ± 1.37",
            "channel_4_bullet": "Cha+ 2025 ApJ 987 L15 (arXiv 2503.21870), sigma/m < 0.5",
            "channel_1_sparc": "implicit prior only (no sigma/m constraint from SPARC alone)",
        },
    }
    out_path = RESULTS_DIR / "t7_joint_posterior.json"
    out_path.write_text(json.dumps(out, indent=2))
    # Also save posterior samples
    np.savez(RESULTS_DIR / "t7_joint_posterior_samples.npz",
             log_sigma_m_0=log_sm_samples, a=a_samples, weights=weights)
    print(f"\n[T7] DONE in {wall:.1f}s")
    print(f"  log Z = {log_Z:.3f} +/- {log_Z_err:.3f}")
    print(f"  MAP: log10(sigma/m)={log_sm_MAP:.2f}, a={a_MAP:.2f}")
    print(f"  Posterior median: log10(sigma/m)={log_sm_p50:.2f}, a={a_p50:.2f}")
    print(f"  68% CI: log10(sigma/m) in [{log_sm_p16:.2f}, {log_sm_p84:.2f}]")
    print(f"  output -> {out_path}")


if __name__ == "__main__":
    main()