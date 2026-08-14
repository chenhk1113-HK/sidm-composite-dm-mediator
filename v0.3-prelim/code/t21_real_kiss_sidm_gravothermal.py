"""
T21 — Direction 1 with REAL KiSS-SIDM gravothermal penalty.

This is the publication-quality replacement for t17_kiss_sidm_corrected_fit.py.
Same parameter space (log_sigma_m_0, a) but the gravothermal penalty comes
from the REAL KiSS-SIDM simulation (arXiv:2505.15903v2, Gurian & May 2025),
not the placeholder `gravothermal.py::gravothermal_r_core` fluid model.

The real KISS-SIDM data is at:
  v0.3-prelim/data/results/real_kiss_sidm_aggregated.json

This JSON has:
  - r_over_rs: 21 bin centers
  - time_Gyr: 4781 snapshot times
  - rho_over_rhos: 4781 x 21 density profile
  - v2_mean_km2_s2: 4781 x 21 velocity dispersion
  - canonical_halo: {M_halo_Msun, rho_s, r_s, sigma_m}

The placeholder gravothermal model predicts r_core ~ sqrt(sigma_m * t).
The real KISS-SIDM gives the actual r_core at each time, accounting for:
  - IMFP regime physics
  - Energy exchange with hot halo
  - Conducting fluid breakdown
  - Proper integration of gravothermal equations

Comparing T17 (placeholder) vs T21 (real) tells us:
  - Is the placeholder accurate?
  - Does the IMFP correction matter for the actual fit?
  - What's the headline sigma/m under the paper's exact physics?
"""
from __future__ import annotations
import json
import sys
import time
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "v0.1-prelim" / "code"))

import numpy as np
import dynesty

import t8_v03_joint_fit as t8  # reuses channel likelihoods
import yang2026_likelihood as yl
import kiss_sidm_scalings as kss
import gravothermal as gth

from config import RESULTS_DIR_V03


# Load the real KISS-SIDM data
_REAL_KISS_PATH = Path(__file__).resolve().parent.parent / "data" / "results" / "real_kiss_sidm_aggregated.json"


def _parse_array_string(s):
    """Parse a string representing a 1D or 2D array from Julia's print output.

    Julia prints:
      - 1D vector as: [a b c d]    (space-separated)
      - 2D matrix as: [a b c; d e f; g h i]  (rows separated by ';')
      - Or: [[a,b,c],[d,e,f]]  (JSON-like with commas and brackets)

    This handles all of these by detecting the format.
    """
    s = s.strip()
    if not s:
        return np.array([])

    # Strip outer brackets if present
    if s.startswith('[') and s.endswith(']'):
        s = s[1:-1].strip()

    # Detect separator
    if ';' in s:
        # Julia 2D format: [a b c; d e f]
        rows = s.split(';')
        result = []
        for r in rows:
            r = r.strip()
            if r:
                vals = [float(x.strip()) for x in r.split() if x.strip()]
                result.append(vals)
        # If only one row, return as 1D
        if len(result) == 1:
            return np.array(result[0])
        return np.array(result)
    elif '],' in s or '], ' in s:
        # JSON 2D format: [[a,b,c],[d,e,f]]
        # Use a regex to find each [a,b,c] subarray
        import re
        subarrays = re.findall(r'\[([^\[\]]*)\]', s)
        result = []
        for r in subarrays:
            vals = [float(x.strip()) for x in r.split(',') if x.strip()]
            result.append(vals)
        if len(result) == 1:
            return np.array(result[0])
        return np.array(result)
    else:
        # 1D: comma or space separated
        if ',' in s:
            return np.array([float(x.strip()) for x in s.split(',') if x.strip()])
        else:
            return np.array([float(x) for x in s.split() if x.strip()])


def _load_real_kiss_data():
    with open(_REAL_KISS_PATH) as f:
        raw = json.load(f)
    # The reader wrote 2D arrays as strings; convert them back
    rho_2d = _parse_array_string(raw["rho_over_rhos"])
    v2_2d = _parse_array_string(raw["v2_mean_km2_s2"])
    n_per_bin_2d = _parse_array_string(raw["n_per_bin"])
    return {
        "n_snapshots": raw["n_snapshots"],
        "r_over_rs": np.array(raw["r_over_rs"]),
        "time_Gyr": np.array(raw["time_Gyr"]),
        "rho_over_rhos": rho_2d,
        "v2_mean_km2_s2": v2_2d,
        "n_per_bin": n_per_bin_2d,
        "canonical_halo": raw["canonical_halo"],
    }


def _compute_real_r_core(data, t_target_Gyr: float) -> float:
    """Find the core radius at time t_target_Gyr by interpolating the real
    KISS-SIDM density profile.

    The core radius is where the density first drops below rho_s (or where
    d ln(rho) / d ln(r) = 0 going outward). We use the second definition:
    where the profile is FLATEST (smallest |d rho / d r|).
    """
    times = np.array(data["time_Gyr"])
    rho = np.array(data["rho_over_rhos"])
    r = np.array(data["r_over_rs"])

    # Find snapshot closest to t_target_Gyr
    idx = int(np.argmin(np.abs(times - t_target_Gyr)))
    rho_at_t = rho[idx]
    rho_max = max(rho_at_t)

    # Find where density drops to 50% of peak (core radius proxy)
    r_core_idx = np.argmax(rho_at_t < 0.5 * rho_max)
    if r_core_idx == 0:
        return r[0]  # All values are > 50%; smallest bin is the "core"
    # Interpolate to find the radius where rho = 0.5 * rho_max
    if r_core_idx > 0:
        rho_lo = rho_at_t[r_core_idx - 1]
        rho_hi = rho_at_t[r_core_idx]
        r_lo = r[r_core_idx - 1]
        r_hi = r[r_core_idx]
        if rho_lo > rho_hi:
            frac = (0.5 * rho_max - rho_hi) / (rho_lo - rho_hi)
            return r_lo + frac * (r_hi - r_lo)
    return r[r_core_idx]


def _gravothermal_penalty_with_real_kiss(
    sigma_m: float, t_Gyr: float, kiss_data: dict
) -> float:
    """Compute the gravothermal penalty using the REAL KISS-SIDM
    density profile at time t_Gyr.

    The penalty is the same as in t20:
      pen = -log(r_core / r_max)
    but r_core is taken from the real KISS-SIDM simulation data.
    """
    sigma_m = float(sigma_m)
    if sigma_m <= 0:
        return 0.0
    if t_Gyr <= 0:
        return 0.0

    # Find r_core from real KISS-SIDM
    r_core = _compute_real_r_core(kiss_data, t_Gyr)
    if r_core <= 0:
        return 0.0

    # Use the canonical halo's r_max = 0.045 r_s (from t17)
    r_max = 0.045 * 1.0  # in units of r_s

    ratio = r_core / r_max
    if ratio <= 0:
        return 0.0
    return -np.log(ratio)


def _kiss_sidm_correction(sigma_m: float) -> float:
    """KISS-SIDM IMFP correction factor at a given sigma/m.
    Uses the same canonical halo as t17/t20.
    """
    HALO_RHO_S = 1e7  # M_sun / kpc^3
    HALO_R_S = 10.0   # kpc
    HALO_V_MAX = 100.0  # km/s
    Kn = kss.knudsen_number(HALO_RHO_S, HALO_V_MAX, sigma_m)
    return kss.knudsen_correction_factor(Kn, Kn_threshold=1.0)


def loglike_t21_with_real_kiss(theta):
    """T17 fit with REAL KISS-SIDM gravothermal penalty.

    This is the publication-quality version of t17:
      - Same channels as t8 (5-channel)
      - Same parameter space (log_sigma_m_0, a)
      - Gravothermal penalty from REAL KISS-SIDM simulation
      - KISS-SIDM IMFP correction applied as a soft prior
    """
    log_sigma_m_0, a = theta
    sigma_m_0 = 10 ** log_sigma_m_0
    if sigma_m_0 <= 0:
        return -np.inf
    if not (-2.0 <= a <= 2.0):
        return -np.inf

    # Channel likelihoods (same as t8)
    ll = t8.loglike_5channel(sigma_m_0, a)

    # KISS-SIDM correction as a soft prior
    sigma_m_at_v_ref = sigma_m_0  # at v_ref = 100 km/s
    correction = _kiss_sidm_correction(sigma_m_at_v_ref)
    pen = _gravothermal_penalty_with_real_kiss(sigma_m_0, t_Gyr=10.0, kiss_data=_kiss_data)
    kiss_prior = -1.0 * correction * pen

    return ll + kiss_prior


def loglike_t21_no_kiss_correction(theta):
    """T17 fit with REAL KISS-SIDM gravothermal penalty, but NO KISS-SIDM correction.
    This is the "fluid baseline" version: use real KISS-SIDM r_core, no IMFP correction.
    """
    log_sigma_m_0, a = theta
    sigma_m_0 = 10 ** log_sigma_m_0
    if sigma_m_0 <= 0:
        return -np.inf
    if not (-2.0 <= a <= 2.0):
        return -np.inf

    ll = t8.loglike_5channel(sigma_m_0, a)
    pen = _gravothermal_penalty_with_real_kiss(sigma_m_0, t_Gyr=10.0, kiss_data=_kiss_data)
    return ll - pen  # No correction factor


def prior_transform_2(u):
    return [
        -2.0 + u[0] * 4.0,   # log_sigma_m in (-2, 2)
        -2.0 + u[1] * 4.0,   # a in (-2, 2)
    ]


_kiss_data = None


def main():
    global _kiss_data
    if not _REAL_KISS_PATH.exists():
        print(f"ERROR: Real KISS-SIDM data not found at {_REAL_KISS_PATH}")
        print("Run kiss_sidm_julia_bridge.py then kiss_sidm_julia_reader.py first")
        return
    _kiss_data = _load_real_kiss_data()
    print(f"Loaded real KISS-SIDM data: {_kiss_data['n_snapshots']} snapshots, "
          f"time range {_kiss_data['time_Gyr'][0]:.3f} to {_kiss_data['time_Gyr'][-1]:.3f} Gyr")

    # Compute real r_core at t=10 Gyr
    r_core_real = _compute_real_r_core(_kiss_data, t_target_Gyr=10.0)
    print(f"Real KISS-SIDM r_core at t=10 Gyr: {r_core_real:.4f} r_s")
    print(f"  (placeholder gravothermal.py gives r_core = "
          f"{gth.gravothermal_r_core(50.0, 1e7, 10.0, 100.0, 10.0):.4e} r_s at sigma_m=50)")

    # Check t17 placeholder MAP for comparison
    print()
    print("T21 — Direction 1 with REAL KISS-SIDM gravothermal penalty")
    print("=" * 80)
    print(f"Priors: log10 sigma_m in (-2, 2), a in (-2, 2)")
    print(f"Sampler: dynesty NLIVE=200, DLOGZ=0.1")
    print(f"  (A) WITH KISS-SIDM IMFP correction")
    print(f"  (B) WITHOUT KISS-SIDM correction (fluid baseline)")

    for label, loglike in [
        ("with_kiss_correction", loglike_t21_with_real_kiss),
        ("no_kiss_correction", loglike_t21_no_kiss_correction),
    ]:
        t0 = time.time()
        sampler = dynesty.NestedSampler(
            loglikelihood=loglike, prior_transform=prior_transform_2,
            ndim=2, nlive=200, bound='multi', sample='auto', bootstrap=0,
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
        pcts = np.percentile(samples, [16, 50, 84], axis=0, weights=weights, method='inverted_cdf')

        # Compare to t17 placeholder
        if label == "with_kiss_correction":
            t21_A_log_Z = log_Z
            t21_A_MAP = MAP
            t21_A_wall = wall
        else:
            t21_B_log_Z = log_Z
            t21_B_MAP = MAP
            t21_B_wall = wall
        print(f"  ({label}): log Z = {log_Z:.3f} +/- {log_Z_err:.3f}  "
              f"MAP log_sigma_m={MAP[0]:.3f} a={MAP[1]:.3f}  (wall {wall:.1f}s)")

    # Compare to t17 (placeholder) and t8 (no KISS-SIDM at all)
    print()
    print("=" * 80)
    print("Comparison:")
    # t8 doesn't have module-level log_Z/MAP (it's only in main()); use a fixed reference
    t8_log_Z = -3.683  # from data/results/t8_v03_posterior.json (prior ship)
    t8_MAP = [0.00, -0.118]  # log_sigma_m, a from prior ship
    print(f"  t8 (no gravothermal penalty):       log Z = {t8_log_Z:.3f}, MAP = {t8_MAP}")
    print(f"  t17 placeholder + KISS-SIDM corr:   log Z = -1.31 (from prior ship)")
    print(f"  t17 placeholder, no KISS-SIDM corr: log Z = -1.22 (from prior ship)")
    print(f"  T21 REAL + KISS-SIDM corr:           log Z = {t21_A_log_Z:.3f}")
    print(f"  T21 REAL, no KISS-SIDM corr:         log Z = {t21_B_log_Z:.3f}")
    print()
    print(f"  T21 (REAL, with corr) MAP: log_sigma_m = {t21_A_MAP[0]:.3f} cm^2/g, a = {t21_A_MAP[1]:.3f}")
    print(f"  T21 (REAL, no corr)   MAP: log_sigma_m = {t21_B_MAP[0]:.3f} cm^2/g, a = {t21_B_MAP[1]:.3f}")

    out = {
        "test": "T21_real_kiss_sidm_gravothermal",
        "direction": "TIER 1 STEP 6: Re-run T17 with REAL KISS-SIDM gravothermal penalty",
        "data_source": str(_REAL_KISS_PATH),
        "data_summary": {
            "n_snapshots": _kiss_data["n_snapshots"],
            "time_range_Gyr": [_kiss_data["time_Gyr"][0], _kiss_data["time_Gyr"][-1]],
            "n_bins": len(_kiss_data["r_over_rs"]),
            "halo": _kiss_data["canonical_halo"],
        },
        "r_core_real_at_t10Gyr_over_rs": r_core_real,
        "T21_A_with_kiss_correction": {
            "log_Z": t21_A_log_Z, "MAP": t21_A_MAP, "wall": t21_A_wall,
        },
        "T21_B_no_kiss_correction": {
            "log_Z": t21_B_log_Z, "MAP": t21_B_MAP, "wall": t21_B_wall,
        },
        "t17_placeholder_summary": {
            "log_Z_with_correction": -1.31,  # from prior shipping
            "log_Z_no_correction": -1.22,
            "MAP_with_correction": [0.0, 1.62],  # log_sigma_m, a
            "MAP_no_correction": [0.04, 0.61],
        },
        "t8_baseline": {
            "log_Z": t8_log_Z, "MAP": t8_MAP,
        },
        "verdict": (
            f"With REAL KISS-SIDM gravothermal penalty:\n"
            f"  T21 A (with IMFP correction): log Z = {t21_A_log_Z:.3f}, "
            f"MAP log sigma_m = {t21_A_MAP[0]:.3f}, a = {t21_A_MAP[1]:.3f}\n"
            f"  T21 B (no correction): log Z = {t21_B_log_Z:.3f}, "
            f"MAP log sigma_m = {t21_B_MAP[0]:.3f}, a = {t21_B_MAP[1]:.3f}\n"
            f"  T17 placeholder: log Z = -1.22 (no correction), MAP log sigma_m = 0.04, a = 0.61\n"
            f"Compare to T21 to see if the placeholder gravothermal model is accurate."
        ),
    }
    out_path = RESULTS_DIR_V03 / "t21_real_kiss_sidm_gravothermal.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(out, indent=2))
    print(f"\noutput -> {out_path}")


if __name__ == "__main__":
    main()
