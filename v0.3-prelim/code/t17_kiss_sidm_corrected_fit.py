#!/usr/bin/env python
"""
T17 -- Direction 1: KISS-SIDM IMFP-corrected 5-channel joint fit.

This script quantifies the SHIFT in the sigma/m posterior when the
gravothermal per-halo prior is corrected for the KISS-SIDM
intermediate-mean-free-path (IMFP) regime (Gurian & May 2025, PRL 135,
221001).

It reuses the v0.3 5-channel likelihood (loglike_5channel from
t8_v03_joint_fit.py) and adds a NEW term: a per-halo gravothermal
prior with a soft penalty that is REDUCED by factor 0.778 in the
IMFP regime (Table I, Kn=1, |DSMC|/|fluid| = 0.21/0.27).

Two fits are run, otherwise identical:
    1. "fluid"        -- baseline (no IMFP correction; penalty unchanged).
    2. "kiss_sidm"    -- IMFP correction active (penalty * 0.778 in IMFP).

The "halo" for the gravothermal prior is hardcoded to a Milky-Way-like
reference halo:
    rho_s = 1e7     M_sun / kpc^3
    r_s   = 10      kpc
    v_max = 100     km/s
    t     = 10      Gyr
This is documented as a DELIBERATE simplification: the v0.3-prelim
5-channel fit uses a single reference halo for the gravothermal prior.
In v0.4-prelim the per-halo extension would marginalize over the halo
mass function; for v0.3-prelim a representative halo is sufficient to
quantify the HEADLINE shift in the posterior.

The prior weight is set by PRIOR_WEIGHT (default 1.0) and is
interpretable as "the gravothermal penalty contributes ~1 in log L
units at full disagreement". Adjust if needed to make the IMFP
correction either dominant or negligible in determining the fit.

OUTPUTS:
    data/results/t17_kiss_sidm_corrected_fit.json
        -- log Z, MAP, percentiles, effective sigma/m at v=30/100/1500
           for BOTH treatments, plus delta between them.
    data/results/t17_kiss_sidm_corrected_samples.npz
        -- posterior samples + weights for both treatments (distinguished
           by the 'treatment' field per sample).

References:
    Gurian & May 2025 (arXiv:2505.15903v2), PRL 135, 221001.
    Balberg & Shapiro 2002 (the conducting fluid model).
"""
from __future__ import annotations
import json
import sys
import time
from pathlib import Path
import numpy as np
import dynesty

# ---------------------------------------------------------------------------
# Path setup -- must precede project imports
# ---------------------------------------------------------------------------
_THIS = Path(__file__).resolve()
_PROJECT_ROOT = _THIS.parents[2]
sys.path.insert(0, str(_PROJECT_ROOT))
sys.path.insert(0, str(_PROJECT_ROOT / "v0.3-prelim" / "code"))
sys.path.insert(0, str(_PROJECT_ROOT / "v0.1-prelim" / "code"))  # halo_profiles

from config import RESULTS_DIR_V03      # noqa: E402
import kiss_sidm_scalings as kss       # noqa: E402
import gravothermal as gth              # noqa: E402

# Reuse the baseline 5-channel likelihood from T8 (no duplication).
from t8_v03_joint_fit import loglike_5channel   # noqa: E402

RESULTS_DIR_V03.mkdir(parents=True, exist_ok=True)


# ---------------------------------------------------------------------------
# Sampler hyperparameters (match T8)
# ---------------------------------------------------------------------------
LOG_SIGMA_M_RANGE = (-3.0, 2.5)
A_RANGE = (-2.0, 2.0)
NLIVE = 500
DLOGZ = 0.10


# ---------------------------------------------------------------------------
# Reference halo parameters for the gravothermal prior (Milky-Way-like)
# ---------------------------------------------------------------------------
RHO_S = 1e7         # M_sun / kpc^3
R_S = 10.0          # kpc
V_MAX = 100.0       # km/s
T_GYR = 10.0        # Gyr
PRIOR_WEIGHT = 1.0  # multiplicative weight on the gravothermal penalty


def _r_max_from_r_s(r_s: float) -> float:
    """Initial expanded core radius r_max = 0.045 * r_s (Balberg+ 2002)."""
    return 0.045 * r_s


def gravothermal_penalty_fluid(sigma_m_v: float) -> float:
    """Fluid-only soft penalty at one (sigma/m_v at v=100, halo) point.

    Penalty is -log(r_core / r_max):
        - 0 if the core is expanded (r_core == r_max).
        - positive if the core has collapsed below r_max.

    We add 0.0 floor so a fully expanded core (best-case) gives 0;
    a fully collapsed core (worst-case) returns a large positive.
    """
    if sigma_m_v <= 0 or not np.isfinite(sigma_m_v):
        # Invalid sigma/m -> return large positive (heavy penalty)
        return 10.0
    r_core = gth.gravothermal_r_core(
        sigma_m_v, rho_s=RHO_S, r_s=R_S, v_max=V_MAX, t_Gyr=T_GYR,
    )
    r_max = _r_max_from_r_s(R_S)
    if r_core <= 0 or r_max <= 0:
        return 10.0
    # -log(r_core/r_max): 0 if at expanded, positive if collapsed
    return float(-np.log(r_core / r_max))


def gravothermal_penalty_kiss_sidm(sigma_m_v: float) -> float:
    """KISS-SIDM-corrected soft penalty.

    Uses knudsen_correction_factor at the reference halo's v_max and
    rho_s as a representative core density. Returns
    fluid_penalty * correction_factor: reduced by 0.778 in IMFP, 1.0
    outside.
    """
    fluid = gravothermal_penalty_fluid(sigma_m_v)
    if fluid <= 0:
        # Nothing to penalize (halo expanded)
        return 0.0
    Kn = kss.knudsen_number(RHO_S, V_MAX, sigma_m_v)
    correction = kss.knudsen_correction_factor(Kn, Kn_threshold=1.0)
    return float(fluid * correction)


# ---------------------------------------------------------------------------
# Joint log likelihood with the gravothermal prior term
# ---------------------------------------------------------------------------
def loglike_with_kiss_sidm_prior(sigma_m_0: float, a: float,
                                 kiss_sidm_correction: bool = False) -> float:
    """5-channel likelihood + gravothermal per-halo prior.

    Args:
        sigma_m_0: sigma/m at v=100 km/s (cm^2/g).
        a: velocity-dependence exponent.
        kiss_sidm_correction: if True, apply the KISS-SIDM IMFP correction
            to the gravothermal penalty (factor 0.778 in IMFP, 1.0 elsewhere).
            If False, use the fluid penalty unchanged.

    Returns:
        log posterior (sum of channel log Ls + gravothermal penalty * weight).
    """
    # Base 5-channel likelihood (T8). Add hard guards early to avoid
    # wasted calls to gravothermal / KISS-SIDM functions.
    if sigma_m_0 <= 0 or not np.isfinite(sigma_m_0):
        return -np.inf
    if not (-2 <= a <= 2):
        return -np.inf

    ll_data = loglike_5channel(sigma_m_0, a)
    if not np.isfinite(ll_data):
        return -np.inf

    # Convert to sigma/m at the galaxy velocity (v=100 km/s = V_REF).
    # sigma_m_at_v is in channels_v03 (imported via t8).
    from channels_v03 import sigma_m_at_v, V_GALAXY
    sigma_m_v100 = sigma_m_at_v(sigma_m_0, a, V_GALAXY)
    if sigma_m_v100 <= 0 or not np.isfinite(sigma_m_v100):
        return -np.inf

    if kiss_sidm_correction:
        grav_pen = gravothermal_penalty_kiss_sidm(sigma_m_v100)
    else:
        grav_pen = gravothermal_penalty_fluid(sigma_m_v100)

    # Penalty is interpreted as a SUBTRACTION from log L (negative log L
    # for collapsed halos). The data channels are centered near 0.
    return float(ll_data - PRIOR_WEIGHT * grav_pen)


# ---------------------------------------------------------------------------
# Diagnostics summary for a run
# ---------------------------------------------------------------------------
def summarize_run(sampler_results, label: str) -> dict:
    res = sampler_results
    log_Z = float(res.logz[-1])
    log_Z_err = float(res.logzerr[-1])
    samples = res.samples
    weights = np.exp(res.logwt - res.logz[-1])
    log_sm_samples = samples[:, 0]
    a_samples = samples[:, 1]

    imap = int(np.argmax(weights))
    log_sm_MAP = float(log_sm_samples[imap])
    a_MAP = float(a_samples[imap])

    p16_sm, p50_sm, p84_sm = np.percentile(log_sm_samples, [16, 50, 84])
    p16_a, p50_a, p84_a = np.percentile(a_samples, [16, 50, 84])

    from channels_v03 import sigma_m_at_v, V_GALAXY
    V_DWARF = 30.0
    V_CLUSTER = 1500.0
    sm_dwarf = sigma_m_at_v(10**log_sm_MAP, a_MAP, V_DWARF)
    sm_gal = sigma_m_at_v(10**log_sm_MAP, a_MAP, V_GALAXY)
    sm_cluster = sigma_m_at_v(10**log_sm_MAP, a_MAP, V_CLUSTER)

    return {
        "label": label,
        "log_Z": log_Z,
        "log_Z_err": log_Z_err,
        "MAP": {
            "log_sigma_m_0": log_sm_MAP,
            "sigma_m_0_cm2_per_g": 10**log_sm_MAP,
            "a": a_MAP,
            "effective_sigma_m": {
                "v_dwarf_30": float(sm_dwarf),
                "v_galaxy_100": float(sm_gal),
                "v_cluster_1500": float(sm_cluster),
            },
        },
        "median_posterior": {
            "log_sigma_m_0_p16": float(p16_sm),
            "log_sigma_m_0_p50": float(p50_sm),
            "log_sigma_m_0_p84": float(p84_sm),
            "a_p16": float(p16_a),
            "a_p50": float(p50_a),
            "a_p84": float(p84_a),
        },
        "samples": {
            "log_sigma_m_0": log_sm_samples,
            "a": a_samples,
            "weights": weights,
        },
    }


def run_one(label: str, kiss_sidm_correction: bool, nlive: int = NLIVE,
            dlogz: float = DLOGZ):
    """Run one dynesty fit and return the summary dict.

    label: human-readable run name.
    kiss_sidm_correction: passed to loglike_with_kiss_sidm_prior.
    nlive: number of live points (override for the smoke test only).
    dlogz: stopping criterion.
    """
    def loglike(theta):
        log_sm, a = theta
        return loglike_with_kiss_sidm_prior(10**log_sm, a,
                                            kiss_sidm_correction=kiss_sidm_correction)

    def prior_transform(u):
        return np.array([
            LOG_SIGMA_M_RANGE[0] + u[0] * (LOG_SIGMA_M_RANGE[1] - LOG_SIGMA_M_RANGE[0]),
            A_RANGE[0] + u[1] * (A_RANGE[1] - A_RANGE[0]),
        ])

    print(f"  [{label}] start: NLIVE={nlive}, DLOGZ={dlogz}")
    t0 = time.time()
    sampler = dynesty.NestedSampler(
        loglikelihood=loglike, prior_transform=prior_transform,
        ndim=2, nlive=nlive, bound='multi', sample='auto', bootstrap=0,
    )
    sampler.run_nested(dlogz=dlogz, print_progress=False)
    wall = time.time() - t0
    print(f"  [{label}] done in {wall:.1f}s")

    summary = summarize_run(sampler.results, label)
    summary["wall_seconds"] = float(wall)
    return summary


def main():
    print("=" * 72)
    print("T17 -- Direction 1: KISS-SIDM IMFP correction on joint fit")
    print("=" * 72)
    print(f"  Halo parameters for gravothermal prior:")
    print(f"    rho_s = {RHO_S:.1e} M_sun/kpc^3, r_s = {R_S:.1f} kpc,")
    print(f"    v_max = {V_MAX:.1f} km/s, t = {T_GYR:.1f} Gyr")
    print(f"  Prior weight: {PRIOR_WEIGHT}")
    print(f"  Sampler: dynesty NestedSampler, NLIVE={NLIVE}, DLOGZ={DLOGZ}")
    print()

    # ----- BASELINE: fluid only -----
    fluid_summary = run_one("fluid", kiss_sidm_correction=False)
    print(f"  fluid: log Z = {fluid_summary['log_Z']:.3f} +/- "
          f"{fluid_summary['log_Z_err']:.3f}")
    print(f"  fluid: MAP log10(sigma/m)={fluid_summary['MAP']['log_sigma_m_0']:.3f}, "
          f"a={fluid_summary['MAP']['a']:.3f}")
    print()

    # ----- KISS-SIDM CORRECTED -----
    kiss_summary = run_one("kiss_sidm", kiss_sidm_correction=True)
    print(f"  kiss_sidm: log Z = {kiss_summary['log_Z']:.3f} +/- "
          f"{kiss_summary['log_Z_err']:.3f}")
    print(f"  kiss_sidm: MAP log10(sigma/m)={kiss_summary['MAP']['log_sigma_m_0']:.3f}, "
          f"a={kiss_summary['MAP']['a']:.3f}")
    print()

    # ----- COMPARISON -----
    delta_log_Z = kiss_summary["log_Z"] - fluid_summary["log_Z"]
    delta_MAP_log_sm = (kiss_summary["MAP"]["log_sigma_m_0"]
                        - fluid_summary["MAP"]["log_sigma_m_0"])
    delta_p16 = (kiss_summary["median_posterior"]["log_sigma_m_0_p16"]
                 - fluid_summary["median_posterior"]["log_sigma_m_0_p16"])
    delta_p84 = (kiss_summary["median_posterior"]["log_sigma_m_0_p84"]
                 - fluid_summary["median_posterior"]["log_sigma_m_0_p84"])
    delta_CI_width = (
        (kiss_summary["median_posterior"]["log_sigma_m_0_p84"]
         - kiss_summary["median_posterior"]["log_sigma_m_0_p16"])
        - (fluid_summary["median_posterior"]["log_sigma_m_0_p84"]
           - fluid_summary["median_posterior"]["log_sigma_m_0_p16"])
    )

    print("=" * 72)
    print("Comparison (kiss_sidm - fluid):")
    print(f"  delta log Z       = {delta_log_Z:+.3f}")
    print(f"  delta MAP log10(sigma/m) = {delta_MAP_log_sm:+.3f} dex")
    print(f"  delta 16th percentile    = {delta_p16:+.3f} dex")
    print(f"  delta 84th percentile    = {delta_p84:+.3f} dex")
    print(f"  delta 68% CI width       = {delta_CI_width:+.3f} dex")
    print("=" * 72)

    # ----- SAVE: JSON summary (no samples arrays) -----
    out = {
        "test": "T17_kiss_sidm_corrected_fit",
        "direction": "Direction 1 -- KISS-SIDM IMFP correction",
        "halo_reference": {
            "rho_s_Msun_per_kpc3": RHO_S,
            "r_s_kpc": R_S,
            "v_max_km_s": V_MAX,
            "t_Gyr": T_GYR,
            "note": "Single reference halo for the gravothermal prior; "
                    "v0.3 uses a representative MW-like halo.",
        },
        "prior_weight": PRIOR_WEIGHT,
        "sampler": {
            "engine": "dynesty.NestedSampler",
            "NLIVE": NLIVE,
            "DLOGZ": DLOGZ,
        },
        "fluid": _summary_without_samples(fluid_summary),
        "kiss_sidm": _summary_without_samples(kiss_summary),
        "comparison": {
            "delta_log_Z": float(delta_log_Z),
            "delta_MAP_log_sm_dex": float(delta_MAP_log_sm),
            "delta_CI_p16": float(delta_p16),
            "delta_CI_p84": float(delta_p84),
            "delta_CI_width_dex": float(delta_CI_width),
            "verdict": _verdict(delta_MAP_log_sm, delta_CI_width,
                                fluid_summary, kiss_summary),
        },
        "constants": {
            "D_LOG_M_KN1_FLUID": kss.D_LOG_M_KN1_FLUID,
            "D_LOG_M_KN1_DSMC": kss.D_LOG_M_KN1_DSMC,
            "imfp_correction_factor_Kn1": abs(kss.D_LOG_M_KN1_DSMC)
                                          / abs(kss.D_LOG_M_KN1_FLUID),
        },
        "improvements_vs_T8": [
            "T8 used a fixed 5-channel likelihood only.",
            "T17 ADDS a per-halo gravothermal prior term to that likelihood.",
            "T17 applies the KISS-SIDM IMFP correction (factor 0.778) to that prior in the KISS run.",
            "Comparison quantifies the posterior SHIFT from the KISS-SIDM correction.",
        ],
    }
    out_path = RESULTS_DIR_V03 / "t17_kiss_sidm_corrected_fit.json"
    out_path.write_text(json.dumps(out, indent=2))
    print(f"\n  output -> {out_path}")

    # ----- SAVE: posterior samples NPZ (fluid + kiss_sidm) -----
    n_fluid = len(fluid_summary["samples"]["log_sigma_m_0"])
    n_kiss = len(kiss_summary["samples"]["log_sigma_m_0"])
    log_sm = np.concatenate([
        fluid_summary["samples"]["log_sigma_m_0"],
        kiss_summary["samples"]["log_sigma_m_0"],
    ])
    a = np.concatenate([
        fluid_summary["samples"]["a"],
        kiss_summary["samples"]["a"],
    ])
    weights = np.concatenate([
        fluid_summary["samples"]["weights"],
        kiss_summary["samples"]["weights"],
    ])
    treatment = np.array(["fluid"] * n_fluid + ["kiss_sidm"] * n_kiss)

    samples_path = RESULTS_DIR_V03 / "t17_kiss_sidm_corrected_samples.npz"
    np.savez(samples_path,
             log_sigma_m_0=log_sm, a=a, weights=weights, treatment=treatment)
    print(f"  output -> {samples_path}")
    print(f"  n_samples (fluid)    = {n_fluid}")
    print(f"  n_samples (kiss_sidm)= {n_kiss}")


def _summary_without_samples(summary: dict) -> dict:
    """Return a JSON-safe copy of a summary without the bulky 'samples' arrays."""
    out = {
        "label": summary["label"],
        "log_Z": summary["log_Z"],
        "log_Z_err": summary["log_Z_err"],
        "MAP": summary["MAP"],
        "median_posterior": summary["median_posterior"],
        "wall_seconds": summary.get("wall_seconds"),
    }
    return out


def _verdict(delta_MAP_log_sm: float, delta_CI_width: float,
             fluid_summary: dict, kiss_summary: dict) -> str:
    """Plain-language verdict on the posterior shift."""
    mag = abs(delta_MAP_log_sm)
    if mag < 0.05:
        s = ("The KISS-SIDM correction shifts the MAP by < 0.05 dex -- "
             "effectively negligible for the headline result. The IMFP "
             "correction does NOT meaningfully move the v0.3 fit.")
    elif mag < 0.20:
        s = ("The KISS-SIDM correction shifts the MAP by ~ %.2f dex -- "
             "a small but non-zero shift. The headline result is robust, "
             "but the KISS-SIDM correction is a marginal re-weighting at "
             "the IMFP regime." % mag)
    else:
        s = ("The KISS-SIDM correction shifts the MAP by %.2f dex -- "
             "a meaningful shift. The v0.3 headline result is NOT robust "
             "to the IMFP correction in this regime." % mag)
    return s


if __name__ == "__main__":
    main()
