"""
T95.12 — STREAMFINDER-lite via 2-component Gaussian Mixture Model.

PURPOSE
=======
T95.11 used a median-pm heuristic for stream-member selection. This
fails when the stream is a small minority of the cone (e.g., 1% stream
+ 99% field), because the median pm is dominated by field stars.

T95.12 replaces the heuristic with a proper 2-component GMM:
  - Stream: tight Gaussian in 5D (pmra, pmdec, parallax, bp_rp, g_mag)
  - Field:  broad Gaussian in 5D
  - Fit via EM (sklearn.mixture.GaussianMixture)
  - Each star gets P(stream | star_i); keep stars with P > 0.5

STATUS: SCAFFOLD 2026-09-08
"""
from __future__ import annotations

import json
import sys
import time
import warnings
from pathlib import Path
from typing import Optional

import numpy as np
import pandas as pd

from sklearn.mixture import GaussianMixture
from sklearn.preprocessing import StandardScaler

from astroquery.gaia import Gaia

import astropy.units as u
from astropy.coordinates import SkyCoord

_PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_PROJECT_ROOT / "code"))

from t95_v11_gaia_cross_match import (  # noqa: E402
    DEGENERATE_STREAMS,
    get_stream_center,
    gaia_cone_search,
    RUWE_MAX,
    VPU_MIN,
    PARALLAX_OVER_ERR_MIN,
)

warnings.filterwarnings("ignore", category=UserWarning, module="astroquery")

# ============================================================================
# GMM-based stream-member selection
# ============================================================================
# Features used for the mixture model
GMM_FEATURES = ["pmra", "pmdec", "parallax", "bp_rp", "phot_g_mean_mag"]

# Probability threshold for "stream member"
P_STREAM_THRESHOLD = 0.5

# Random seed for reproducibility
RANDOM_STATE = 42

# GMM convergence
GMM_MAX_ITER = 200
GMM_TOL = 1e-4
GMM_N_INIT = 5  # try 5 random initializations, keep best


def select_stream_members_gmm(df: pd.DataFrame,
                              expected_distance_kpc: float,
                              random_state: int = RANDOM_STATE,
                              verbose: bool = False,
                              return_gmm: bool = False):
    """Select likely stream members using 2-component GMM.

    Model:
      Component 0: "stream" — tight Gaussian, initialized at median pm
                    of parallax-filtered stars
      Component 1: "field"  — broad Gaussian, initialized at the global
                    mean of all stars
      EM iteration picks up which stars belong to which component.

    Returns the subset of df with P(stream) > P_STREAM_THRESHOLD.

    If return_gmm=True, returns (members, gmm_object, scaler) tuple.

    Returns df unchanged if GMM fails to converge or has too few stars.
    """
    if len(df) < 10:
        if verbose:
            print(f"  GMM skipped: only {len(df)} stars in cone")
        empty = df.iloc[0:0]
        return (empty, None, None) if return_gmm else empty

    # Drop stars with missing values in any feature
    df_clean = df.dropna(subset=GMM_FEATURES).copy()
    if len(df_clean) < 10:
        if verbose:
            print(f"  GMM skipped: only {len(df_clean)} clean rows")
        empty = df_clean.iloc[0:0]
        return (empty, None, None) if return_gmm else empty

    # Build feature matrix
    X = df_clean[GMM_FEATURES].values

    # StandardScaler: critical for EM convergence
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    # Initial guesses
    # Stream: median of parallax-filtered stars (similar to T95.11 init)
    df_clean["parallax_over_err"] = (
        df_clean["parallax"] / df_clean["parallax_error"]
    )
    df_plx = df_clean[df_clean["parallax_over_err"] > PARALLAX_OVER_ERR_MIN]
    if len(df_plx) >= 5:
        stream_init = df_plx[GMM_FEATURES].median().values
    else:
        stream_init = df_clean[GMM_FEATURES].median().values
    field_init = df_clean[GMM_FEATURES].mean().values

    # Scale the initial means
    stream_init_scaled = (stream_init - scaler.mean_) / scaler.scale_
    field_init_scaled = (field_init - scaler.mean_) / scaler.scale_

    # Build init means: 2 components, in scaled space
    init_means = np.vstack([stream_init_scaled, field_init_scaled])

    # Tight initial covariances: stream = tight Gaussian (small diag),
    # field = broad Gaussian (large diag). This biases the EM toward
    # separating a tight cluster from a broad background.
    n_features = len(GMM_FEATURES)
    init_covars = np.zeros((2, n_features, n_features))
    init_covars[0] = 0.01 * np.eye(n_features)  # tight stream
    init_covars[1] = 5.0 * np.eye(n_features)   # broad field

    # Prior weights: assume stream is small minority
    init_weights = np.array([0.05, 0.95])

    # Fit GMM
    try:
        gmm = GaussianMixture(
            n_components=2,
            covariance_type="full",
            means_init=init_means,
            precisions_init=np.linalg.inv(init_covars),
            weights_init=init_weights,
            max_iter=GMM_MAX_ITER,
            tol=GMM_TOL,
            n_init=GMM_N_INIT,
            random_state=random_state,
        )
        gmm.fit(X_scaled)
    except Exception as e:
        if verbose:
            print(f"  GMM fit failed: {e}")
        empty = df_clean.iloc[0:0]
        return (empty, None, None) if return_gmm else empty

    # Predict probabilities (which component is "stream"?)
    probs = gmm.predict_proba(X_scaled)
    # Convention: component 0 is stream (init at parallax-filtered median)
    p_stream = probs[:, 0]

    df_clean = df_clean.copy()
    df_clean["p_stream"] = p_stream

    # Select high-probability stream members
    members = df_clean[df_clean["p_stream"] > P_STREAM_THRESHOLD].copy()

    if verbose:
        # Identify which component is tighter (lower trace of covariance)
        cov_traces = [np.trace(gmm.covariances_[k]) for k in range(2)]
        tight_comp = int(np.argmin(cov_traces))
        print(f"  GMM converged in {gmm.n_iter_} iters, loglik = {gmm.score(X_scaled) * len(X_scaled):.1f}")
        print(f"  Component 0 trace: {cov_traces[0]:.2f},  Component 1 trace: {cov_traces[1]:.2f}")
        print(f"  Stream-membership threshold P>{P_STREAM_THRESHOLD}: {len(members)}/{len(df_clean)} stars")
        # Tighter component is "stream" — verify our convention
        if tight_comp != 0:
            print(f"  WARNING: Component {tight_comp} is tighter (lower trace). "
                  f"Convention assumes comp 0 is stream.")

    return (members, gmm, scaler) if return_gmm else members


# ============================================================================
# Per-stream GMM cross-match
# ============================================================================
def cross_match_stream_gmm(stream_name: str,
                            verbose: bool = True) -> dict:
    """Cross-match a single degenerate stream against Gaia DR3 + GMM selection."""
    center = get_stream_center(stream_name)
    if center is None:
        return {"stream": stream_name, "status": "no_track", "n_stars_queried": 0}

    # Use same cone-radius heuristic as T95.11
    from t95_v11_gaia_cross_match import CONE_RADIUS_DEG_MIN, CONE_RADIUS_DEG_MAX
    cone_radius_deg = min(2.0 * center["extent_p90_deg"], CONE_RADIUS_DEG_MAX)
    cone_radius_deg = max(cone_radius_deg, CONE_RADIUS_DEG_MIN)

    if verbose:
        print(f"\n=== {stream_name} ===")
        print(f"  on-sky: RA={center['ra_center_deg']:.3f}°  Dec={center['dec_center_deg']:+.3f}°")
        print(f"  cone radius: {cone_radius_deg:.3f}°")

    # Fetch Gaia data + bp_rp color (NEW feature for GMM)
    t0 = time.time()
    coord = SkyCoord(ra=center["ra_center_deg"], dec=center["dec_center_deg"],
                     unit=(u.deg, u.deg), frame="icrs")
    adql = f"""
    SELECT TOP 10000
        source_id, ra, dec, parallax, parallax_error,
        pmra, pmdec, radial_velocity,
        ruwe, visibility_periods_used, phot_g_mean_mag, bp_rp
    FROM gaiadr3.gaia_source
    WHERE 1 = CONTAINS(
        POINT('ICRS', ra, dec),
        CIRCLE('ICRS', {center['ra_center_deg']:.6f}, {center['dec_center_deg']:.6f}, {cone_radius_deg:.6f})
    )
    AND pmra IS NOT NULL
    AND pmdec IS NOT NULL
    AND ruwe < {RUWE_MAX}
    AND visibility_periods_used >= {VPU_MIN}
    """
    try:
        job = Gaia.launch_job(adql, dump_to_file=False, verbose=False)
        df_cone = job.get_results().to_pandas()
    except Exception as e:
        print(f"  Gaia cone search failed: {e}")
        return {
            "stream": stream_name, "status": "gaia_failed",
            "wall_s": time.time() - t0, **center,
        }
    wall_s = time.time() - t0

    if len(df_cone) == 0:
        return {
            "stream": stream_name, "status": "no_gaia_match",
            "wall_s": wall_s, "n_stars_cone": 0, "n_members": 0,
            "cone_radius_deg": cone_radius_deg, **center,
        }

    n_cone = len(df_cone)

    # GMM member selection
    gmm_result = select_stream_members_gmm(
        df_cone, center["distance_kpc"], verbose=verbose, return_gmm=True
    )
    if isinstance(gmm_result, tuple):
        members, gmm, scaler = gmm_result
    else:
        # Fallback (shouldn't happen with return_gmm=True, but be safe)
        members = gmm_result
        gmm = None
        scaler = None
    n_members = len(members)

    # If GMM gives too few members, fall back to T95.11 heuristic
    # so we at least have something
    if n_members < 5:
        from t95_v11_gaia_cross_match import select_stream_members
        fallback = select_stream_members(df_cone, center["distance_kpc"])
        if len(fallback) >= n_members:
            members = fallback
            n_members = len(members)
            method = "t95_11_fallback"
        else:
            method = "gmm_only_low_n"
    else:
        method = "gmm"

    # Compute kinematics from members
    if n_members >= 3:
        # Weighted by p_stream (uniform weights if fallback)
        if "p_stream" in members.columns:
            weights = members["p_stream"].values
        else:
            weights = np.ones(n_members)

        # Weighted medians (more robust than weighted means for contaminated data)
        def weighted_median(values, weights):
            """Weighted median via linear interpolation."""
            sorted_idx = np.argsort(values)
            v_sorted = values[sorted_idx]
            w_sorted = weights[sorted_idx]
            cum_w = np.cumsum(w_sorted)
            cum_w /= cum_w[-1]
            idx = np.searchsorted(cum_w, 0.5)
            return float(v_sorted[min(idx, len(v_sorted) - 1)])

        pmra_med = weighted_median(members["pmra"].values, weights)
        pmdec_med = weighted_median(members["pmdec"].values, weights)
        rv_med = float(np.nanmedian(members["radial_velocity"]))

        # Also compute GMM-component-mean kinematics (cleaner estimate of
        # the stream's true pm, less affected by outlier members).
        # Skip if GMM didn't fit (low-N fallback case).
        gmm_pmra = gmm_pmdec = gmm_v_t = gmm_v_3d = 0.0
        gmm_parallax = gmm_g_mag = 0.0
        if gmm is not None and scaler is not None:
            # Stream component is component 0 (initialized at parallax-filtered median)
            stream_mean_scaled = gmm.means_[0]
            stream_mean_unscaled = stream_mean_scaled * scaler.scale_ + scaler.mean_
            gmm_pmra = float(stream_mean_unscaled[0])
            gmm_pmdec = float(stream_mean_unscaled[1])
            gmm_parallax = float(stream_mean_unscaled[2])
            gmm_g_mag = float(stream_mean_unscaled[4])

            # v_t via T95.9 formula, using GMM component mean (cleaner)
            gmm_pm_mag = np.sqrt(gmm_pmra ** 2 + gmm_pmdec ** 2)
            d = center["distance_kpc"]
            gmm_v_t = 4.74 * gmm_pm_mag * d
            # v_r: use weighted median of members (GMM doesn't model v_r directly)
            gmm_v_3d = float(np.sqrt(gmm_v_t ** 2 + rv_med ** 2))

        # v_t_med below is the weighted-median version; report BOTH
        pm_mag = np.sqrt(pmra_med ** 2 + pmdec_med ** 2)
        v_t_med = 4.74 * pm_mag * d
        v_3d_med = float(np.sqrt(v_t_med ** 2 + rv_med ** 2))
    else:
        pmra_med = pmdec_med = rv_med = v_t_med = v_3d_med = 0.0
        gmm_pmra = gmm_pmdec = gmm_v_t = gmm_v_3d = 0.0
        gmm_parallax = gmm_g_mag = 0.0

    # Compute v_3d std (if we have enough members)
    if n_members >= 5 and "p_stream" in members.columns:
        # Per-star v_3d
        pm_mags = np.sqrt(members["pmra"] ** 2 + members["pmdec"] ** 2)
        v_ts = 4.74 * pm_mags * center["distance_kpc"]
        v_rs = members["radial_velocity"].fillna(0).values
        v_3ds = np.sqrt(v_ts ** 2 + v_rs ** 2)
        v_3d_std = float(np.std(v_3ds))
    else:
        v_3d_std = 0.0

    result = {
        "stream": stream_name,
        "status": "ok",
        "member_selection_method": method,
        "n_stars_cone": n_cone,
        "n_members": n_members,
        "wall_s": wall_s,
        "cone_radius_deg": cone_radius_deg,
        **center,
        "pmra_median_mas_yr": pmra_med,
        "pmdec_median_mas_yr": pmdec_med,
        "rv_median_kms": rv_med,
        "v_t_rescued_kms": v_t_med,
        "v_3d_rescued_kms": v_3d_med,
        "v_3d_std_kms": v_3d_std,
        # GMM-component-mean kinematics (cleaner estimate of stream's true pm)
        "gmm_pmra_mas_yr": gmm_pmra,
        "gmm_pmdec_mas_yr": gmm_pmdec,
        "gmm_v_t_kms": gmm_v_t,
        "gmm_v_3d_kms": gmm_v_3d,
        "gmm_parallax_mas": gmm_parallax,
    }

    if verbose:
        print(f"  Gaia cone: {n_cone} stars in {wall_s:.2f}s")
        print(f"  GMM members: {n_members} (method: {method})")
        print(f"  v_t = {v_t_med:.1f} km/s")
        print(f"  v_3d = {v_3d_med:.1f} ± {v_3d_std:.1f} km/s")

    return result


def main() -> int:
    out_dir = _PROJECT_ROOT / "outputs" / "t95"
    out_dir.mkdir(parents=True, exist_ok=True)

    print("=" * 70)
    print("T95.12 — GMM-based stream-member selection")
    print("=" * 70)
    print(f"Streams: {len(DEGENERATE_STREAMS)}")
    print()

    results = []
    t_start = time.time()
    for i, s in enumerate(DEGENERATE_STREAMS):
        # Rate-limit Gaia TAP calls (1/sec default)
        elapsed = time.time() - t_start
        expected = i * 1.0
        if elapsed < expected:
            time.sleep(expected - elapsed)
        try:
            r = cross_match_stream_gmm(s, verbose=True)
        except Exception as e:
            print(f"\n  !! {s} failed: {e}")
            import traceback
            traceback.print_exc()
            r = {"stream": s, "status": "exception", "error": str(e)}
        results.append(r)

    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    ok = [r for r in results if r.get("status") == "ok"]
    print(f"OK: {len(ok)}/{len(results)}")
    if ok:
        print("\nGMM-rescued streams:")
        for r in ok:
            print(f"  {r['stream']:14s}  v_3d = {r['v_3d_rescued_kms']:6.1f} ± "
                  f"{r['v_3d_std_kms']:5.1f} km/s  "
                  f"n_members={r['n_members']} ({r['member_selection_method']})")

    out_path = out_dir / "t95_v12_gmm_cross_match_results.json"
    out_path.write_text(json.dumps(results, indent=2, default=str))
    print(f"\nWrote: {out_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
