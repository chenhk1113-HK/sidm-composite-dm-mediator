#!/usr/bin/env python
"""
T90.58 -- Channel-set ablation sweep on the T90.57 hybrid.

Robustness test: drop each channel in turn (Cloud-9, Galaxy, Bullet, LZ,
KSFR) from the T90.57 5-channel hybrid and re-run the joint fit. Compare
log Z across configurations.

Per-channel ablation questions:
  - Drop Cloud-9:  does the model still need Cloud-9's high sigma/m(28) ~ [30, 500]?
  - Drop Galaxy:   does the model still need the Galactic < 2 cm^2/g constraint?
  - Drop Bullet:   is Bullet actually constraining (the answer is likely no)?
  - Drop LZ:       how much does the LZ magnetic-moment bound matter?
  - Drop KSFR:     does KSFR add prior-volume penalty (~0.5 log-unit)?

Channels available (all defined in t90_v51 + t90_v56 + t90_v57):
  - loglike_cloud9(sm_c9)             from t90_v51_resonant_joint_fit
  - loglike_galaxy(sm_gal)            from t90_v51_resonant_joint_fit
  - loglike_bullet(sm_bul)            from t90_v51_resonant_joint_fit
  - loglike_lz_magnetic_moment(...)   from channels_extended (via T90_MAGNETIC_MOMENT_MU_X env var)
  - loglike_ksfr_pcac_validity(...)   from ksfr_pcac_validity (via KSFR_ENABLED env var)

Settings (matched to T90.56/57):
  nlive = 200 (faster than 500 for ablation; ablation uses Δlog Z deltas)
  dlogz = 0.1
  KSFR  = enabled (per project's default v0.5)

Output:
  data/results/t90_v58_ablation_<channel_set_name>_posterior.json
  data/results/t90_v58_ablation_summary.json (all subsets)
"""

from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))

# Enable KSFR by default for ablation (matches T90.57's KSFR-on run)
os.environ.setdefault("SIDM_DISABLE_KSFR_MASK", "0")

from t90_v56_hybrid_lz import (
    prior_transform_10 as prior_transform_10_v56,
    LOG_RANGES_10,
    PARAM_NAMES_10,
    IS_LOG_10,
    unpack_theta_10,
    _check_wimpy,
)
from t90_v54_hybrid_sigma_m import sigma_m_hybrid
from t90_v51_resonant_joint_fit import (
    loglike_cloud9,
    loglike_galaxy,
    loglike_bullet,
)
from channels_extended import loglike_lz_magnetic_moment
from ksfr_pcac_validity import loglike_ksfr_pcac_validity


def _loglike_subset(theta_log, enabled_channels):
    """10D joint log-likelihood on a SUBSET of channels.

    enabled_channels is a set of channel names from:
      {"Cloud9", "Galaxy", "Bullet", "LZ", "KSFR"}

    Channels are computed independently and summed. KSFR is a hard mask
    (returns -inf outside box, 0 inside); LZ requires WIMpy and returns 0
    silently if unavailable.
    """
    # Prior bounds enforcement
    for i in range(10):
        lo, hi = LOG_RANGES_10[i]
        if not (lo <= theta_log[i] <= hi):
            return -np.inf

    theta_9, mu_x = unpack_theta_10(theta_log)

    sm_c9 = sigma_m_hybrid(28.0, theta_9)["sigma_m_total_cm2_per_g"]
    sm_gal = sigma_m_hybrid(100.0, theta_9)["sigma_m_total_cm2_per_g"]
    sm_bul = sigma_m_hybrid(3000.0, theta_9)["sigma_m_total_cm2_per_g"]

    if sm_c9 <= 0 or sm_gal <= 0 or sm_bul <= 0:
        return -np.inf
    if not (np.isfinite(sm_c9) and np.isfinite(sm_gal) and np.isfinite(sm_bul)):
        return -np.inf

    total = 0.0

    if "Cloud9" in enabled_channels:
        ll = loglike_cloud9(sm_c9)
        if not np.isfinite(ll):
            return -np.inf
        total += ll

    if "Galaxy" in enabled_channels:
        ll = loglike_galaxy(sm_gal)
        if not np.isfinite(ll):
            return -np.inf
        total += ll

    if "Bullet" in enabled_channels:
        ll = loglike_bullet(sm_bul)
        if not np.isfinite(ll):
            return -np.inf
        total += ll

    if "LZ" in enabled_channels:
        m_chi_GeV = theta_9[0]
        ll_lz = loglike_lz_magnetic_moment(m_chi_GeV, mu_x, include_in_fit=True)
        if not np.isfinite(ll_lz):
            ll_lz = 0.0  # silent if WIMpy unavailable
        total += ll_lz

    if "KSFR" in enabled_channels:
        # Map hybrid 10D theta -> KSFR 5-tuple (KSFR expects LOG form)
        log_m_phi_MeV = theta_log[1]
        log_m_chi_GeV = theta_log[0]
        g_chi = theta_log[2]
        log_alpha = theta_log[8]
        theta_ksfr = (log_m_phi_MeV, log_m_chi_GeV, g_chi, -50.0, log_alpha)
        ll_ksfr = loglike_ksfr_pcac_validity(
            theta_ksfr, N_dc=3, N_f=3,
        )
        if not np.isfinite(ll_ksfr):
            return -np.inf
        total += ll_ksfr

    return total


def run_subset(name, enabled_channels, nlive=200, dlogz=0.1, label=None):
    """Run dynesty on a channel subset. Returns summary dict."""
    import dynesty

    label = label or name
    print(f"\n[T90.58] === {label} ===")
    print(f"[T90.58] Enabled channels: {sorted(enabled_channels)}")
    print(f"[T90.58] nlive = {nlive}, dlogz = {dlogz}")

    t0 = time.time()

    sampler = dynesty.NestedSampler(
        lambda theta: _loglike_subset(theta, enabled_channels),
        prior_transform_10_v56,
        ndim=10,
        nlive=nlive,
        bound="multi",
        sample="rwalk",
    )

    sampler.run_nested(dlogz=dlogz, maxiter=100000, print_progress=False)
    wall = time.time() - t0

    res = sampler.results
    log_Z = float(res["logz"][-1])
    log_Z_err = float(res["logzerr"][-1])

    print(f"[T90.58] {label}: log Z = {log_Z:.3f} +/- {log_Z_err:.3f}  wall = {wall:.1f}s")

    # Posterior median predictions
    weights = np.exp(res["logwt"] - res["logz"][-1])
    samples = res["samples"]

    sm_c9_samples = np.array([
        sigma_m_hybrid(28.0, unpack_theta_10(s)[0])["sigma_m_total_cm2_per_g"]
        for s in samples
    ])
    sm_gal_samples = np.array([
        sigma_m_hybrid(100.0, unpack_theta_10(s)[0])["sigma_m_total_cm2_per_g"]
        for s in samples
    ])
    sm_bul_samples = np.array([
        sigma_m_hybrid(3000.0, unpack_theta_10(s)[0])["sigma_m_total_cm2_per_g"]
        for s in samples
    ])

    median_c9 = float(np.average(sm_c9_samples, weights=weights))
    median_gal = float(np.average(sm_gal_samples, weights=weights))
    median_bul = float(np.average(sm_bul_samples, weights=weights))

    summary = {
        "label": label,
        "enabled_channels": sorted(list(enabled_channels)),
        "log_Z": log_Z,
        "log_Z_err": log_Z_err,
        "wall_seconds": wall,
        "n_samples": len(samples),
        "posterior_median_sigma_m": {
            "Cloud9_cm2_per_g": median_c9,
            "Galaxy_cm2_per_g": median_gal,
            "Bullet_cm2_per_g": median_bul,
        },
        "wimpy_available": _check_wimpy(),
        "ksfr_enabled": "KSFR" in enabled_channels,
    }

    out_path = Path(__file__).parent.parent / "data" / "results" / f"t90_v58_ablation_{name}.json"
    with open(out_path, "w") as f:
        json.dump(summary, f, indent=2)
    print(f"[T90.58] Wrote {out_path}")

    return summary


def run_ablation_sweep(nlive=200, dlogz=0.1):
    """Run all 6 ablations: full + 5 single-channel drops."""
    ALL_CHANNELS = {"Cloud9", "Galaxy", "Bullet", "LZ", "KSFR"}

    sweep = {}

    # Baseline: all channels enabled
    sweep["all_5ch"] = run_subset("all_5ch", ALL_CHANNELS, nlive=nlive, dlogz=dlogz,
                                  label="All 5 channels (baseline)")

    # Drop each channel in turn
    for dropped in sorted(ALL_CHANNELS):
        remaining = ALL_CHANNELS - {dropped}
        sweep[f"drop_{dropped}"] = run_subset(
            f"drop_{dropped}", remaining, nlive=nlive, dlogz=dlogz,
            label=f"Drop {dropped} (only {sorted(remaining)} active)",
        )

    # Compute deltas vs baseline
    base_log_Z = sweep["all_5ch"]["log_Z"]
    summary = {
        "baseline": sweep["all_5ch"],
        "ablations": {k: v for k, v in sweep.items() if k != "all_5ch"},
        "delta_log_Z_vs_baseline": {
            k.replace("drop_", ""): sweep[k]["log_Z"] - base_log_Z
            for k in sweep if k != "all_5ch"
        },
        "nlive": nlive,
        "dlogz": dlogz,
        "wimpy_available": _check_wimpy(),
        "ksfr_enabled": True,
    }

    out_path = Path(__file__).parent.parent / "data" / "results" / "t90_v58_ablation_summary.json"
    with open(out_path, "w") as f:
        json.dump(summary, f, indent=2)
    print(f"\n[T90.58] === SUMMARY ===")
    print(f"[T90.58] Baseline (all 5ch) log Z = {base_log_Z:.3f}")
    for k, d in summary["delta_log_Z_vs_baseline"].items():
        sign = "+" if d >= 0 else ""
        print(f"[T90.58]   Drop {k:8s}: delta log Z = {sign}{d:.3f}")
    print(f"[T90.58] Wrote {out_path}")
    return summary


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="T90.58 channel-set ablation sweep")
    parser.add_argument("--nlive", type=int, default=200, help="Number of live points")
    parser.add_argument("--dlogz", type=float, default=0.1, help="Evidence convergence threshold")
    args = parser.parse_args()
    run_ablation_sweep(nlive=args.nlive, dlogz=args.dlogz)
