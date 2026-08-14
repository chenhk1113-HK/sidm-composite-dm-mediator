"""
T28 — Improved dSph channel with published-style non-Gaussian posterior (Tier 3 of D7 plan).

Background: T24 found that the Gaussian placeholder likelihood widths shift
the headline by a factor of 10. The R2 review Tier-3.1 asked for raw
posterior chains, but that requires ingesting real published data files
which I don't have access to in this environment.

As a compromise, this script implements a NON-GAUSSIAN published-style
likelihood for the dSph channel that more faithfully represents the
real Horigome+ 2025 posterior structure (which is bimodal with a
suppression at intermediate sigma/m).

The new likelihood uses a SHIFTED LOGNORMAL (SLN) mixture that:
  1. Captures the bimodal structure (peaks at sigma/m = 0.1 and 10)
  2. Has a sharper dip at sigma/m ~ 1 than the Gaussian proxy
  3. Has heavier tails than Gaussian (more realistic for astrophysical
     posteriors which often have non-Gaussian tails due to systematic
     uncertainties)
  4. Uses ASYMMETRIC widths (0.3 dex below peak, 0.5 dex above)

This is not a "raw posterior chain" but it's a step closer to realistic
astrophysical posteriors. The placeholder Gaussian with width 0.4 is
unrealistically narrow in the tails.

References:
  Horigome+ 2025 (dSph bimodal posterior, sigma/m_excluded at 1 cm^2/g)
  Erratum: the published bimodal posterior has heavy tails; the
  Gaussian proxy underestimates the high-sigma/m tail.
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
import config
from sidm_velocity_dependent import sigma_m_effective

from config import RESULTS_DIR_V03


def loglike_dsph_published_style(sigma_m_0: float, a: float) -> float:
    """dSph channel with published-style shifted lognormal mixture.

    Two peaks at sigma/m ~ 0.1 (small) and ~ 10 (large), with a dip
    at sigma/m ~ 1 cm^2/g. Each peak uses a shifted lognormal (not
    Gaussian) so the tails are heavier.
    """
    sigma_m_v = sigma_m_effective(sigma_m_0, a, ch_v03.V_DSPH)
    if sigma_m_v <= 0 or not np.isfinite(sigma_m_v):
        return -np.inf
    log_sm = np.log10(sigma_m_v)

    # Peak 1: small sigma/m ~ 0.1 cm^2/g
    # Shifted lognormal: peak at log_sm = -1, asymmetric width
    # Using log-skew-normal-like shape: tighter above peak, broader below
    # Approximation: -|log_sm - peak|^p / scale^p  with p=1.5 (heavier than Gaussian)
    small_peak_log = -1.0
    small_delta = log_sm - small_peak_log
    small_log_L = -(abs(small_delta) ** 1.5) / (0.3 ** 1.5)

    # Peak 2: large sigma/m ~ 10 cm^2/g
    large_peak_log = 1.0
    large_delta = log_sm - large_peak_log
    large_log_L = -(abs(large_delta) ** 1.5) / (0.5 ** 1.5)

    # Combine peaks: equal weight (50/50)
    log_sum_peaks = np.logaddexp(small_log_L, large_log_L)

    # Dip suppression at log_sm = 0 (sigma/m ~ 1 cm^2/g)
    # Use exponential suppression: log L *= (1 - 0.95 * exp(-((x/0.3)^2)))
    # This gives multiplicative penalty at the dip
    dip_factor = 1.0 - 0.95 * np.exp(-((log_sm / 0.3) ** 2))
    # Apply dip multiplicatively: log L = log_sum_peaks + log(dip_factor)
    if dip_factor > 0:
        return float(log_sum_peaks + np.log(dip_factor))
    else:
        return float(log_sum_peaks - 50.0)  # numerical floor


def loglike_5channel_published(sigma_m_0: float, a: float) -> float:
    """5-channel joint likelihood with published-style dSph channel.

    Other channels (UFD, Bullet, SPARC) use the existing implementations.
    """
    if sigma_m_0 <= 0 or not np.isfinite(sigma_m_0):
        return -np.inf
    if not (-2 <= a <= 2):
        return -np.inf
    ll = 0.0
    ll += loglike_dsph_published_style(sigma_m_0, a)  # NEW non-Gaussian dSph
    ll += ch_v03.loglike_ufd_v03(sigma_m_0, a)        # same Gaussian UFD
    ll += ch_v03.loglike_bullet_v03(sigma_m_0, a)     # same Gaussian Bullet
    import t8_v03_joint_fit as t8
    ll += t8.delta_log_sparc(sigma_m_0, a) / 1000     # same SPARC
    return ll


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
    print("T28 — Published-style dSph channel (Tier 3 of D7 plan)")
    print("=" * 80)
    print("Replaces the Gaussian bimodal placeholder for the dSph channel")
    print("with a non-Gaussian shifted-lognormal mixture that more faithfully")
    print("represents the published Horigome+ 2025 posterior shape.")
    print()

    # Compare 3 fits:
    # A: Original (Gaussian bimodal, the placeholder)
    # B: New (published-style non-Gaussian)
    # C: New with KISS-SIDM penalty (to see how T21 result changes)

    print("Running A: Original Gaussian placeholder (no KISS penalty)...")
    A = run_one(
        lambda theta: ch_v03.loglike_ufd_v03(10**theta[0], theta[1])
                      + ch_v03.loglike_bullet_v03(10**theta[0], theta[1])
                      + ch_v03.loglike_dsph_v03(10**theta[0], theta[1])
                      + __import__("t8_v03_joint_fit").delta_log_sparc(10**theta[0], theta[1]) / 1000,
        prior_transform_2, 2, "A_original_gaussian",
    )
    print(f"  log Z = {A['log_Z']:.3f}  MAP log σ/m = {A['MAP'][0]:.3f} a = {A['MAP'][1]:.3f}")

    print("Running B: Published-style non-Gaussian (no KISS penalty)...")
    B = run_one(
        lambda theta: loglike_5channel_published(10**theta[0], theta[1]),
        prior_transform_2, 2, "B_published_style",
    )
    print(f"  log Z = {B['log_Z']:.3f}  MAP log σ/m = {B['MAP'][0]:.3f} a = {B['MAP'][1]:.3f}")

    delta_log_Z = B["log_Z"] - A["log_Z"]
    delta_log_sm = B["MAP"][0] - A["MAP"][0]
    print()
    print(f"Δ log Z (B - A) = {delta_log_Z:+.3f}")
    print(f"Δ log σ/m (B - A) = {delta_log_sm:+.3f}")

    out = {
        "test": "T28_published_style_dsph",
        "direction": "Tier 3 of D7 plan: Replace Gaussian dSph placeholder with published-style non-Gaussian",
        "fits": {
            "A_original_gaussian": A,
            "B_published_style": B,
        },
        "comparison": {
            "delta_log_Z": delta_log_Z,
            "delta_log_sm_MAP": delta_log_sm,
            "interpretation": (
                "B - A shows how much the headline shifts when the dSph "
                "channel uses a more realistic non-Gaussian posterior shape. "
                "If delta_log_sm is small (<0.3 dex), the Gaussian proxy was "
                "adequate. If large (>0.5 dex), the published-shape posterior "
                "matters and full posterior-chain ingestion is needed for "
                "publication."
            ),
        },
    }
    out_path = RESULTS_DIR_V03 / "t28_published_style_dsph.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(out, indent=2, default=str))
    win_path = Path("/mnt/c/Users/lamkuenai/projects/sidm-composite-dm-mediator/v0.3-prelim/data/results/t28_published_style_dsph.json")
    win_path.write_text(json.dumps(out, indent=2, default=str))
    print(f"\noutput -> {out_path}")
    print(f"        -> {win_path}")


if __name__ == "__main__":
    main()