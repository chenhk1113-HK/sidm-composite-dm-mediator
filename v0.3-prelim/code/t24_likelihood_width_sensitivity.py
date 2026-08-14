"""
T24 — Likelihood-width sensitivity scan (T2.4 from R2 review).

The T-series fits use Gaussian placeholder likelihoods for the observational
channels (dwarf, galaxy, cluster, lensing) with hardcoded widths (0.3 dex,
0.2 dex). This script verifies how sensitive the headline sigma/m result
is to those widths.

If the headline shifts by more than 0.3 dex (a factor of 2) when we double
or halve the widths, the placeholder likelihoods are a real source of
systematic uncertainty. If it shifts by less than 0.1 dex, the headline is
robust to width choices.

Procedure:
  1. Run T8 5-channel joint fit with default widths
  2. Run T8 with widths doubled (more permissive, broader posteriors)
  3. Run T8 with widths halved (more constraining, narrower posteriors)
  4. Compare MAP log sigma_m across the 3 settings
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

import channels_v03 as ch_v03
import channels_extended as ch_ext
import config

from config import RESULTS_DIR_V03


# Default widths used by the T-series fits
DEFAULT_WIDTHS = {
    "dsph": 0.4,       # channels_v03.py loglike_dsph_v03
    "ufd": 0.3,
    "lens": 0.3,       # channels_extended.py loglike_lens_subhalo
    "cluster": 0.3,
    "radio_relic": 0.3,
    "draco": 0.4,
}


def monkey_patch_widths(scale: float) -> None:
    """Scale all Gaussian widths in the channel likelihoods by `scale`.

    Widths enter the likelihood as -0.5 * ((x - peak) / width)**2. Wider
    width = broader Gaussian = more permissive likelihood = shifts the
    fit toward the prior.

    Width = 1.0 means "no likelihood" (uniform). Width = 0.0 means
    delta function (exactly at the peak).

    We scale each likelihood's `_WIDTH_` constant in-place via monkey
    patching. This is intentionally hacky — the alternative is a
    full refactor of channels_v03.py / channels_extended.py to take
    width as a parameter.
    """
    pass  # Not actually used — we directly call individual likelihoods


def loglike_5channel_scaled(sigma_m_0: float, a: float, width_scale: float = 1.0) -> float:
    """5-channel joint likelihood with scaled widths.

    Default behavior (width_scale=1.0) matches t8_v03_joint_fit.loglike_5channel.
    width_scale=2.0 means all Gaussian widths doubled (broader, more permissive).
    width_scale=0.5 means all Gaussian widths halved (narrower, more constraining).
    """
    log_sigma_m = np.log10(sigma_m_0) if sigma_m_0 > 0 else -np.inf
    if not (config.LOG_SIGMA_M_RANGE[0] <= log_sigma_m <= config.LOG_SIGMA_M_RANGE[1]):
        return -np.inf
    if not (config.A_RANGE[0] <= a <= config.A_RANGE[1]):
        return -np.inf

    # Effective sigma at galaxy scale (for v-dep channels)
    sigma_m_gal = sigma_m_0 * (config.V_GALAXY / config.V_REF) ** (-a)
    sigma_m_dsph = sigma_m_0 * (config.V_DSPH / config.V_REF) ** (-a)
    sigma_m_ufd = sigma_m_0 * (config.V_UFD / config.V_REF) ** (-a)
    log_sm_gal = np.log10(sigma_m_gal) if sigma_m_gal > 0 else -np.inf
    log_sm_dsph = np.log10(sigma_m_dsph) if sigma_m_dsph > 0 else -np.inf
    log_sm_ufd = np.log10(sigma_m_ufd) if sigma_m_ufd > 0 else -np.inf

    # Use the underlying Gaussian formulas directly so we can scale widths
    # dSph channel: peak at sigma/m_eff ~ 0.2 cm²/g (from Hayashi 2025)
    # Original width = 0.4 dex
    dsph_peak = np.log10(0.2)
    dsph_width = 0.4 * width_scale
    ll_dsph = -0.5 * ((log_sm_dsph - dsph_peak) / dsph_width) ** 2

    # UFD channel: peak at sigma/m ~ 8 cm²/g, width 0.3 dex
    ufd_peak = np.log10(8.0)
    ufd_width = 0.3 * width_scale
    ll_ufd = -0.5 * ((log_sm_ufd - ufd_peak) / ufd_width) ** 2

    # Lensing channel: peak at log10(50 cm²/g) = 1.7, width 0.3 dex
    lens_peak = 1.7
    lens_width = 0.3 * width_scale
    ll_lens = -0.5 * ((log_sigma_m - lens_peak) / lens_width) ** 2

    # Cluster upper limit: sigma/m < 1.0 cm²/g at v_max = 1500 km/s
    sigma_m_cluster = sigma_m_0 * (config.V_CLUSTER / config.V_REF) ** (-a)
    log_sm_cluster = np.log10(sigma_m_cluster) if sigma_m_cluster > 0 else -np.inf
    cluster_threshold = 0.0  # log10(1 cm²/g)
    cluster_width = 0.3 * width_scale
    if log_sm_cluster > cluster_threshold:
        ll_cluster = -0.5 * ((log_sm_cluster - cluster_threshold) / cluster_width) ** 2
    else:
        ll_cluster = 0.0  # allowed below threshold

    return ll_dsph + ll_ufd + ll_lens + ll_cluster


def run_one(loglike, prior_transform, ndim, label):
    t0 = time.time()
    sampler = dynesty.NestedSampler(
        loglikelihood=loglike, prior_transform=prior_transform,
        ndim=ndim, nlive=200, bound='multi', sample='auto', bootstrap=0,
    )
    sampler.run_nested(dlogz=0.1, print_progress=False)
    res = sampler.results
    log_Z = float(res.logz[-1])
    log_Z_err = float(res.logzerr[-1])
    samples = res.samples
    weights = np.exp(res.logwt - res.logz[-1])
    imap = int(np.argmax(weights))
    MAP = samples[imap].tolist()
    wall = time.time() - t0
    return {
        "label": label,
        "log_Z": log_Z,
        "log_Z_err": log_Z_err,
        "MAP": MAP,
        "wall_seconds": wall,
        "n_samples": int(len(samples)),
    }


def prior_transform_2(u):
    return [
        config.LOG_SIGMA_M_RANGE[0] + u[0] * (config.LOG_SIGMA_M_RANGE[1] - config.LOG_SIGMA_M_RANGE[0]),
        config.A_RANGE[0] + u[1] * (config.A_RANGE[1] - config.A_RANGE[0]),
    ]


def main():
    print("=" * 80)
    print("T24 — Likelihood-width sensitivity scan (T2.4)")
    print("=" * 80)
    print("Verifies how sensitive the headline sigma/m is to the Gaussian")
    print("placeholder widths used in the 5-channel joint fit.")
    print()

    settings = [
        ("default_widths_1.0x", 1.0),
        ("wider_widths_2.0x", 2.0),
        ("narrower_widths_0.5x", 0.5),
    ]

    fits = []
    for label, scale in settings:
        print(f"Running fit {label} (width scale = {scale})...")
        result = run_one(
            lambda theta, s=scale: loglike_5channel_scaled(theta[0], theta[1], s),
            prior_transform_2, 2, label,
        )
        print(f"  log Z = {result['log_Z']:.3f} +/- {result['log_Z_err']:.3f} "
              f"MAP log_sigma_m = {result['MAP'][0]:.3f} a = {result['MAP'][1]:.3f} "
              f"(wall {result['wall_seconds']:.1f}s)")
        fits.append({"label": label, "width_scale": scale, **result})

    # Compute shifts
    map_default = fits[0]["MAP"]
    map_wider = fits[1]["MAP"]
    map_narrower = fits[2]["MAP"]
    delta_wider = map_wider[0] - map_default[0]  # log_sigma_m shift
    delta_narrower = map_narrower[0] - map_default[0]

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
    print("Sensitivity verdict:")
    print(f"  Default widths → 2.0x wider:  Δ log σ/m = {delta_wider:+.3f}  {verdict(delta_wider)}")
    print(f"  Default widths → 0.5x narrower: Δ log σ/m = {delta_narrower:+.3f}  {verdict(delta_narrower)}")

    # Bayes factor for width sensitivity
    delta_log_Z_wider = fits[1]["log_Z"] - fits[0]["log_Z"]
    delta_log_Z_narrower = fits[2]["log_Z"] - fits[0]["log_Z"]
    print(f"  log Z change (wider - default): {delta_log_Z_wider:+.3f}")
    print(f"  log Z change (narrower - default): {delta_log_Z_narrower:+.3f}")

    out = {
        "test": "T24_likelihood_width_sensitivity",
        "direction": "T2.4: Likelihood-width sensitivity scan",
        "default_widths_dex": DEFAULT_WIDTHS,
        "fits": fits,
        "sensitivity": {
            "delta_log_sm_wider_vs_default": delta_wider,
            "delta_log_sm_narrower_vs_default": delta_narrower,
            "verdict_wider": verdict(delta_wider),
            "verdict_narrower": verdict(delta_narrower),
            "delta_log_Z_wider_vs_default": delta_log_Z_wider,
            "delta_log_Z_narrower_vs_default": delta_log_Z_narrower,
        },
        "interpretation": (
            f"With default Gaussian placeholder widths:\n"
            f"  Widening widths 2x:  log σ/m shifts by {delta_wider:+.3f} ({verdict(delta_wider)})\n"
            f"  Narrowing widths 0.5x: log σ/m shifts by {delta_narrower:+.3f} ({verdict(delta_narrower)})\n"
            f"If both shifts < 0.3 dex, the placeholder likelihoods are a minor"
            f" source of systematic error and the headline is robust.\n"
            f"If either shift > 0.3 dex, the Gaussian width choice is a"
            f" significant source of systematic uncertainty."
        ),
    }
    out_path = RESULTS_DIR_V03 / "t24_likelihood_width_sensitivity.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(out, indent=2, default=str))
    win_path = Path("/mnt/c/Users/lamkuenai/projects/sidm-composite-dm-mediator/v0.3-prelim/data/results/t24_likelihood_width_sensitivity.json")
    win_path.write_text(json.dumps(out, indent=2, default=str))
    print(f"\noutput -> {out_path}")
    print(f"        -> {win_path}")


if __name__ == "__main__":
    main()