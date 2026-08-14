"""
T26 — T21 sensitivity to Gaussian width choice (Tier 1 of D7 plan).

Background: T24 (D6) showed that the T8 5-channel fit shifts MAP σ/m
by a factor of 10 when the Gaussian placeholder widths change by 2x.
T21 (the headline fit) uses the same channels but adds a KISS-SIDM
gravothermal penalty on top. Question: does the T21 headline
(σ/m = 1.4-1.7 cm²/g) also depend strongly on the Gaussian width choice?

Procedure: re-run T21 with widths scaled by 0.5x (narrower), 1.0x (default),
and 2.0x (wider). Compare MAP σ/m across the three settings.
"""
from __future__ import annotations
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "v0.1-prelim" / "code"))

import numpy as np
import dynesty

import t21_real_kiss_sidm_gravothermal as t21
import t8_v03_joint_fit as t8
import config

from config import RESULTS_DIR_V03


def loglike_t21_scaled(theta, width_scale: float = 1.0):
    """T21 likelihood with Gaussian widths scaled.

    Replaces t8.loglike_5channel() with a width-scaled version, then
    adds the same KISS-SIDM gravothermal penalty as T21.
    """
    log_sigma_m_0, a = theta
    sigma_m_0 = 10 ** log_sigma_m_0
    if sigma_m_0 <= 0 or not np.isfinite(sigma_m_0):
        return -np.inf
    if not (config.LOG_SIGMA_M_RANGE[0] <= log_sigma_m_0 <= config.LOG_SIGMA_M_RANGE[1]):
        return -np.inf
    if not (config.A_RANGE[0] <= a <= config.A_RANGE[1]):
        return -np.inf

    # Recompute the 5-channel likelihood with scaled widths
    # By monkey-patching the widths inside the module
    import channels_v03 as ch_v03
    orig_loglike_dsph = ch_v03.loglike_dsph_v03
    orig_loglike_ufd = ch_v03.loglike_ufd_v03
    orig_loglike_bullet = ch_v03.loglike_bullet_v03

    def loglike_dsph_scaled(sigma_m_0, a):
        from sidm_velocity_dependent import sigma_m_at_v
        sigma_m_v = sigma_m_at_v(sigma_m_0, a, ch_v03.V_DSPH)
        if sigma_m_v <= 0 or not np.isfinite(sigma_m_v):
            return -np.inf
        log_sm = np.log10(sigma_m_v)
        small_g = -0.5 * ((log_sm - (-1.0)) / (0.4 * width_scale)) ** 2
        large_g = -0.5 * ((log_sm - (1.0)) / (0.4 * width_scale)) ** 2
        log_sum_peaks = np.logaddexp(small_g, large_g)
        dip_g = -0.3 * ((log_sm - 0.0) / (0.5 * width_scale)) ** 2
        return float(log_sum_peaks + dip_g)

    def loglike_ufd_scaled(sigma_m_0, a):
        from sidm_velocity_dependent import sigma_m_at_v
        sigma_m_v = sigma_m_at_v(sigma_m_0, a, ch_v03.V_UFD)
        if sigma_m_v <= 0 or not np.isfinite(sigma_m_v):
            return -np.inf
        log_sm = np.log10(sigma_m_v)
        return -0.5 * ((log_sm - 0.92) / (1.37 * width_scale)) ** 2

    def loglike_bullet_scaled(sigma_m_0, a):
        from sidm_velocity_dependent import sigma_m_at_v
        sigma_m_v = sigma_m_at_v(sigma_m_0, a, ch_v03.V_CLUSTER)
        if sigma_m_v <= 0 or not np.isfinite(sigma_m_v):
            return -np.inf
        log_sm = np.log10(sigma_m_v)
        return -0.5 * max(0, (log_sm - (-0.30)) / (0.30 * width_scale)) ** 2

    # Monkey-patch
    ch_v03.loglike_dsph_v03 = loglike_dsph_scaled
    ch_v03.loglike_ufd_v03 = loglike_ufd_scaled
    ch_v03.loglike_bullet_v03 = loglike_bullet_scaled
    try:
        ll = t8.loglike_5channel(sigma_m_0, a)
    finally:
        ch_v03.loglike_dsph_v03 = orig_loglike_dsph
        ch_v03.loglike_ufd_v03 = orig_loglike_ufd
        ch_v03.loglike_bullet_v03 = orig_loglike_bullet

    # Add KISS-SIDM penalty
    pen = t21._gravothermal_penalty_with_real_kiss(sigma_m_0, t_Gyr=10.0, kiss_data=t21._kiss_data)
    sigma_m_at_v_ref = sigma_m_0
    correction = t21._kiss_sidm_correction(sigma_m_at_v_ref)
    kiss_prior = -1.0 * correction * pen

    return ll + kiss_prior


def prior_transform_2(u):
    return [
        config.LOG_SIGMA_M_RANGE[0] + u[0] * (config.LOG_SIGMA_M_RANGE[1] - config.LOG_SIGMA_M_RANGE[0]),
        config.A_RANGE[0] + u[1] * (config.A_RANGE[1] - config.A_RANGE[0]),
    ]


def run_one(loglike, prior_transform, ndim, label):
    t0 = time.time()
    sampler = dynesty.NestedSampler(
        loglikelihood=loglike, prior_transform=prior_transform,
        ndim=ndim, nlive=200, bound='multi', sample='auto', bootstrap=0,
    )
    sampler.run_nested(dlogz=0.1, print_progress=False)
    res = sampler.results
    log_Z = float(res.logz[-1])
    samples = res.samples
    weights = np.exp(res.logwt - res.logz[-1])
    imap = int(np.argmax(weights))
    MAP = samples[imap].tolist()
    wall = time.time() - t0
    return {"label": label, "log_Z": log_Z, "MAP": MAP, "wall_seconds": wall}


def main():
    print("=" * 80)
    print("T26 — T21 sensitivity to Gaussian width choice")
    print("=" * 80)
    print("Re-runs T21 (with real KISS-SIDM penalty) at 3 width settings.")
    print("T21 default headline: MAP log σ/m = 0.236, σ/m = 1.7 cm²/g (with IMFP)")
    print()

    # Load KISS data first
    if t21._kiss_data is None:
        t21._kiss_data = t21._load_real_kiss_data()

    settings = [
        ("default_1.0x", 1.0),
        ("wider_2.0x", 2.0),
        ("narrower_0.5x", 0.5),
    ]

    fits = []
    for label, scale in settings:
        print(f"Running T26 fit {label} (width scale = {scale})...")
        result = run_one(
            lambda theta, s=scale: loglike_t21_scaled(theta, width_scale=s),
            prior_transform_2, 2, label,
        )
        sm_MAP = result["MAP"][0]
        a_MAP = result["MAP"][1]
        print(f"  log Z = {result['log_Z']:.3f}  MAP log σ/m = {sm_MAP:.3f} (σ/m = {10**sm_MAP:.2f} cm²/g) a = {a_MAP:.3f}  (wall {result['wall_seconds']:.1f}s)")
        fits.append({"label": label, "width_scale": scale, **result,
                     "sigma_m_MAP_cm2_per_g": 10**sm_MAP})

    # Compare to T21 default (which used width_scale=1.0)
    map_default = fits[0]["MAP"][0]
    map_wider = fits[1]["MAP"][0]
    map_narrower = fits[2]["MAP"][0]
    delta_wider = map_wider - map_default
    delta_narrower = map_narrower - map_default
    delta_log_Z_wider = fits[1]["log_Z"] - fits[0]["log_Z"]
    delta_log_Z_narrower = fits[2]["log_Z"] - fits[0]["log_Z"]

    def verdict(d):
        if abs(d) < 0.1:
            return "ROBUST (shift < 0.1 dex)"
        elif abs(d) < 0.3:
            return "MODERATE (0.1-0.3 dex shift)"
        elif abs(d) < 0.5:
            return "SIGNIFICANT (0.3-0.5 dex shift)"
        else:
            return "MAJOR (shift > 0.5 dex)"

    print()
    print("=" * 80)
    print("T21 sensitivity verdict:")
    print(f"  Δ log σ/m (wider vs default): {delta_wider:+.3f}  {verdict(delta_wider)}")
    print(f"  Δ log σ/m (narrower vs default): {delta_narrower:+.3f}  {verdict(delta_narrower)}")
    print(f"  Δ log Z (wider vs default): {delta_log_Z_wider:+.3f}")
    print(f"  Δ log Z (narrower vs default): {delta_log_Z_narrower:+.3f}")

    # Compare to T24 finding (no KISS penalty)
    print()
    print("Comparison to T24 (no KISS penalty):")
    print("  T24: Δ log σ/m (wider vs default) = -1.006 (MAJOR)")
    print(f"  T26: Δ log σ/m (wider vs default) = {delta_wider:+.3f} ({verdict(delta_wider)})")

    out = {
        "test": "T26_t21_width_sensitivity",
        "direction": "Tier 1 of D7 plan: T21 sensitivity to Gaussian width choice",
        "t21_default_headline": {
            "MAP_log_sigma_m": 0.236,
            "sigma_m_cm2_per_g": 1.72,
            "log_Z": -0.660,
        },
        "fits": fits,
        "sensitivity": {
            "delta_log_sm_wider_vs_default": delta_wider,
            "delta_log_sm_narrower_vs_default": delta_narrower,
            "delta_log_Z_wider_vs_default": delta_log_Z_wider,
            "delta_log_Z_narrower_vs_default": delta_log_Z_narrower,
            "verdict_wider": verdict(delta_wider),
            "verdict_narrower": verdict(delta_narrower),
        },
        "comparison_to_t24": {
            "t24_delta_log_sm_wider_vs_default": -1.006,
            "t26_delta_log_sm_wider_vs_default": delta_wider,
            "kiss_penalty_dampens_width_sensitivity": (
                delta_wider > -1.006  # T21 with KISS less sensitive than T24
            ),
        },
        "interpretation": (
            f"T21 (with real KISS-SIDM penalty) sensitivity to Gaussian widths:\n"
            f"  Default (1.0x): MAP log σ/m = {fits[0]['MAP'][0]:.3f} (σ/m = {10**fits[0]['MAP'][0]:.2f} cm²/g)\n"
            f"  2x wider:        MAP log σ/m = {fits[1]['MAP'][0]:.3f} (σ/m = {10**fits[1]['MAP'][0]:.2f} cm²/g) [{verdict(delta_wider)}]\n"
            f"  0.5x narrower:   MAP log σ/m = {fits[2]['MAP'][0]:.3f} (σ/m = {10**fits[2]['MAP'][0]:.2f} cm²/g) [{verdict(delta_narrower)}]\n\n"
            f"Compare to T24 (no KISS penalty): wider case shifted by -1.006 dex (factor of 10).\n"
            f"If T26 shift is much smaller, the KISS-SIDM gravothermal penalty is acting as\n"
            f"a regularizer that anchors the headline against width-choice sensitivity."
        ),
    }
    out_path = RESULTS_DIR_V03 / "t26_t21_width_sensitivity.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(out, indent=2, default=str))
    win_path = Path("/mnt/c/Users/lamkuenai/projects/sidm-composite-dm-mediator/v0.3-prelim/data/results/t26_t21_width_sensitivity.json")
    win_path.write_text(json.dumps(out, indent=2, default=str))
    print(f"\noutput -> {out_path}")
    print(f"        -> {win_path}")


if __name__ == "__main__":
    main()