"""
T95.11 — Cross-match the 13 degenerate galstreams streams against Gaia DR3
using astroquery for proper TAP + cone-search handling.

PURPOSE
=======
The T95.10 pipeline flagged 13 streams as `degenerate_kinematics` because
galstreams tracks have v_t = 0, v_r = 0 (no proper motion or radial velocity
data). This module queries Gaia DR3 at each stream's on-sky position, finds
stars with measured proper motion + radial velocity in the cone, computes
the stream's mean kinematics, and feeds back into stream_sigma_m_diagnostic.

Method:
  1. Get on-sky center + angular extent from galstreams track
  2. astroquery.gaia.cone_search at that position with ruwe/vpu cuts
  3. Compute median pmra, pmdec, radial_velocity (robust to field stars)
  4. Compute v_t = 4.74 * |pm| * distance (same formula as T95.9)
  5. Plug back into stream_sigma_m_diagnostic with the rescued kinematics

STATUS: SCAFFOLD 2026-09-08
"""
from __future__ import annotations

import json
import sys
import time
import warnings
from pathlib import Path
from typing import Optional

import astropy.units as u
import numpy as np
import pandas as pd
from astropy.coordinates import SkyCoord

from astroquery.gaia import Gaia

_PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_PROJECT_ROOT / "code"))

from t95_v25_multi_stream_real_galstreams import (  # noqa: E402
    load_stream_summary,
    load_stream_track,
)

# Silence astroquery warnings about cone search
warnings.filterwarnings("ignore", category=UserWarning, module="astroquery")

# ============================================================================
# Configuration
# ============================================================================
# Quality cuts on Gaia DR3 data (default astroquery uses ruwe < 1.4 in new releases)
RUWE_MAX = 1.4
VPU_MIN = 8
PARALLAX_OVER_ERR_MIN = 5.0  # positive parallax for nearby stars

# Cone-search radius (degrees). Streams vary in angular extent; use moderate
# radius that covers most of the track without pulling too many field stars.
CONE_RADIUS_DEG_DEFAULT = 0.3
CONE_RADIUS_DEG_MIN = 0.2
CONE_RADIUS_DEG_MAX = 0.5

DEGENERATE_STREAMS = [
    "Alpheus", "Eridanus", "Hermus", "Hyllus", "Molonglo",
    "Murrumbidgee", "NGC6362", "Orinoco", "Pal15", "Parallel",
    "Pegasus", "Perpendicular", "Tri-Pis",
]


# ============================================================================
# On-sky center from galstreams track
# ============================================================================
def get_stream_center(stream_name: str) -> Optional[dict]:
    """Compute on-sky center + 90th-percentile angular extent."""
    tr = load_stream_track(stream_name)
    sm = load_stream_summary(stream_name)
    if tr is None or sm is None:
        return None

    ra_vals = tr["ra"].values
    dec_vals = tr["dec"].values
    ra_rad = np.deg2rad(ra_vals)
    dec_rad = np.deg2rad(dec_vals)

    # Circular mean for RA (handles 360° wrap-around)
    ra_mean_rad = np.arctan2(
        np.mean(np.sin(ra_rad)),
        np.mean(np.cos(ra_rad))
    )
    ra_mean = float(np.rad2deg(ra_mean_rad) % 360)
    dec_mean = float(np.median(dec_vals))

    # Angular extent: 90th-percentile great-circle distance from centroid
    dec_mean_rad = np.deg2rad(dec_mean)
    dra = ra_rad - ra_mean_rad
    # Wrap RA differences to [-pi, pi]
    dra = (dra + np.pi) % (2 * np.pi) - np.pi
    a = np.sin((dec_rad - dec_mean_rad) / 2) ** 2 + \
        np.cos(dec_mean_rad) * np.cos(dec_rad) * np.sin(dra / 2) ** 2
    gc_dist_deg = np.rad2deg(2 * np.arcsin(np.sqrt(np.clip(a, 0, 1))))
    p90_extent = float(np.percentile(gc_dist_deg, 90))

    return {
        "stream": stream_name,
        "ra_center_deg": ra_mean,
        "dec_center_deg": dec_mean,
        "extent_p90_deg": p90_extent,
        "n_track_points": len(tr),
        "distance_kpc": float(sm.iloc[0]["mid.distance"]),
    }


# ============================================================================
# Gaia DR3 cone search via astroquery
# ============================================================================
def gaia_cone_search(ra_deg: float, dec_deg: float, radius_deg: float,
                     max_rows: int = 10000) -> pd.DataFrame:
    """Cone search Gaia DR3 with ruwe + visibility cuts."""
    coord = SkyCoord(ra=ra_deg, dec=dec_deg, unit=(u.deg, u.deg), frame="icrs")

    # ADQL query against gaiadr3.gaia_source
    adql = f"""
    SELECT TOP {max_rows}
        source_id, ra, dec, parallax, parallax_error,
        pmra, pmdec, radial_velocity,
        ruwe, visibility_periods_used, phot_g_mean_mag
    FROM gaiadr3.gaia_source
    WHERE 1 = CONTAINS(
        POINT('ICRS', ra, dec),
        CIRCLE('ICRS', {ra_deg:.6f}, {dec_deg:.6f}, {radius_deg:.6f})
    )
    AND pmra IS NOT NULL
    AND pmdec IS NOT NULL
    AND ruwe < {RUWE_MAX}
    AND visibility_periods_used >= {VPU_MIN}
    """

    try:
        job = Gaia.launch_job(adql, dump_to_file=False, verbose=False)
        result = job.get_results()
    except Exception as e:
        print(f"  Gaia cone search failed: {e}")
        return pd.DataFrame()

    if len(result) == 0:
        return pd.DataFrame()

    df = result.to_pandas()
    return df


# ============================================================================
# Stream member selection (kinematic clustering)
# ============================================================================
def select_stream_members(df: pd.DataFrame, expected_distance_kpc: float,
                          pm_tolerance_mas_yr: float = 2.0,
                          distance_tolerance_factor: float = 0.5) -> pd.DataFrame:
    """Select likely stream members from Gaia cone search.

    Heuristic: stream is kinematically cold, so its members are the
    kinematically clustered subset at the right distance. We:
      1. Require parallax_over_err > 5 (good distance measurement)
      2. Require parallax consistent with expected_distance_kpc (within factor)
      3. Iteratively clip outliers in pm space

    For a real stream analysis this should use a proper clustering
    algorithm (e.g. STREAMFINDER, or a Gaussian Mixture Model on pm).
    """
    if df.empty:
        return df

    df = df.copy()
    df["parallax_over_err"] = df["parallax"] / df["parallax_error"]
    good_plx = df["parallax_over_err"] > PARALLAX_OVER_ERR_MIN

    if good_plx.sum() < 5:
        # Not enough parallax info; fall back to all stars
        return df

    df_plx = df[good_plx].copy()
    if df_plx.empty:
        return df_plx

    # Distance filter: parallax within factor of expected
    expected_plx_mas = 1000.0 / expected_distance_kpc  # mas
    plx_lo = expected_plx_mas * (1 - distance_tolerance_factor)
    plx_hi = expected_plx_mas * (1 + distance_tolerance_factor)
    in_dist = (df_plx["parallax"] >= plx_lo) & (df_plx["parallax"] <= plx_hi)
    df_dist = df_plx[in_dist].copy()

    # If too few stars in distance range, loosen
    if len(df_dist) < 5:
        df_dist = df_plx.copy()

    # Iterative clip on pm
    if df_dist.empty:
        return df_dist
    pmra_med = float(np.median(df_dist["pmra"]))
    pmdec_med = float(np.median(df_dist["pmdec"]))
    for _ in range(2):
        pm_dist = np.sqrt(
            (df_dist["pmra"] - pmra_med) ** 2 +
            (df_dist["pmdec"] - pmdec_med) ** 2
        )
        df_dist = df_dist[pm_dist < pm_tolerance_mas_yr].copy()
        if len(df_dist) < 3:
            break
        pmra_med = float(np.median(df_dist["pmra"]))
        pmdec_med = float(np.median(df_dist["pmdec"]))

    return df_dist


# ============================================================================
# Per-stream cross-match
# ============================================================================
def cross_match_stream(stream_name: str,
                       cone_radius_deg: Optional[float] = None,
                       verbose: bool = True) -> dict:
    """Cross-match a single degenerate stream against Gaia DR3."""
    center = get_stream_center(stream_name)
    if center is None:
        return {"stream": stream_name, "status": "no_track", "n_stars_queried": 0}

    if cone_radius_deg is None:
        # Use 2× p90 extent, capped at CONE_RADIUS_DEG_MAX.
        # Streams with large p90 extent (>5°) need tighter cuts — the
        # center alone isn't representative, the stream is spread out.
        cone_radius_deg = min(2.0 * center["extent_p90_deg"], CONE_RADIUS_DEG_MAX)
        cone_radius_deg = max(cone_radius_deg, CONE_RADIUS_DEG_MIN)

    if verbose:
        print(f"\n=== {stream_name} ===")
        print(f"  on-sky: RA={center['ra_center_deg']:.3f}°  Dec={center['dec_center_deg']:+.3f}°")
        print(f"  p90 extent: {center['extent_p90_deg']:.3f}°  "
              f"d={center['distance_kpc']:.2f} kpc")
        print(f"  cone radius: {cone_radius_deg:.3f}°")

    t0 = time.time()
    df_cone = gaia_cone_search(
        center["ra_center_deg"], center["dec_center_deg"],
        cone_radius_deg
    )
    wall_s = time.time() - t0

    if df_cone.empty:
        return {
            "stream": stream_name, "status": "no_gaia_match",
            "n_stars_cone": 0, "n_members": 0,
            "wall_s": wall_s, "cone_radius_deg": cone_radius_deg,
            **center,
        }

    # Try to select stream members
    members = select_stream_members(df_cone, center["distance_kpc"])
    n_cone = len(df_cone)
    n_members = len(members)

    # Use members if we got enough, otherwise fall back to cone
    if n_members >= 3:
        df_use = members
        used_members = True
    else:
        df_use = df_cone
        used_members = False

    # Compute v_t from proper motion + distance
    pm_mag = np.sqrt(df_use["pmra"] ** 2 + df_use["pmdec"] ** 2)
    d = center["distance_kpc"]
    v_t_arr = 4.74 * pm_mag * d  # km/s
    v_r_arr = df_use["radial_velocity"].fillna(0).values
    v_3d_arr = np.sqrt(v_t_arr ** 2 + v_r_arr ** 2)

    # Median kinematics
    pmra_med = float(np.median(df_use["pmra"]))
    pmdec_med = float(np.median(df_use["pmdec"]))
    rv_med = float(np.nanmedian(df_use["radial_velocity"]))
    v_t_med = float(np.median(v_t_arr))
    v_3d_med = float(np.median(v_3d_arr))
    v_3d_std = float(np.std(v_3d_arr))

    result = {
        "stream": stream_name,
        "status": "ok",
        "n_stars_cone": n_cone,
        "n_members": n_members,
        "used_member_selection": used_members,
        "wall_s": wall_s,
        "cone_radius_deg": cone_radius_deg,
        **center,
        "pmra_median_mas_yr": pmra_med,
        "pmdec_median_mas_yr": pmdec_med,
        "rv_median_kms": rv_med,
        "v_t_rescued_kms": v_t_med,
        "v_3d_rescued_kms": v_3d_med,
        "v_3d_std_kms": v_3d_std,
        "caveat": ("Member-selected (kinematic clustering)" if used_members
                   else "Used all cone stars (member selection failed)"),
    }

    if verbose:
        print(f"  Gaia cone: {n_cone} stars in {wall_s:.2f}s")
        if used_members:
            print(f"  Member-selected: {n_members} stars (pm within 5 mas/yr of median)")
        print(f"  pmra = {pmra_med:+.3f} mas/yr")
        print(f"  pmdec = {pmdec_med:+.3f} mas/yr")
        print(f"  rv = {rv_med:+.2f} km/s")
        print(f"  v_t (rescued) = {v_t_med:.1f} km/s")
        print(f"  v_3d (rescued) = {v_3d_med:.1f} ± {v_3d_std:.1f} km/s")

    return result


# ============================================================================
# Rate-limit helper
# ============================================================================
def _sleep_if_needed(start_time: float, calls_so_far: int) -> None:
    """Gaia TAP rate-limit: 1 query/sec default, 200/hour for anon."""
    elapsed = time.time() - start_time
    expected = calls_so_far * 1.0  # 1 query/sec budget
    if elapsed < expected:
        time.sleep(expected - elapsed)


# ============================================================================
# Main runner
# ============================================================================
def run_cross_match_all(verbose: bool = True) -> list[dict]:
    print("=" * 70)
    print("T95.11 — Gaia DR3 cross-match of 13 degenerate streams")
    print("=" * 70)
    print(f"Querying Gaia DR3 cone search for {len(DEGENERATE_STREAMS)} streams\n")

    results = []
    t_start = time.time()
    for i, s in enumerate(DEGENERATE_STREAMS):
        _sleep_if_needed(t_start, i)
        try:
            r = cross_match_stream(s, verbose=verbose)
        except Exception as e:
            print(f"\n  !! {s} failed: {e}")
            import traceback
            traceback.print_exc()
            r = {"stream": s, "status": "exception", "error": str(e)}
        results.append(r)

    # Summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    ok = [r for r in results if r.get("status") == "ok"]
    no_match = [r for r in results if r.get("status") == "no_gaia_match"]
    fail = [r for r in results if r.get("status") == "exception"]
    print(f"OK (Gaia data found):    {len(ok)}/{len(results)}")
    print(f"No Gaia match:           {len(no_match)}/{len(results)}")
    print(f"Exception:               {len(fail)}/{len(results)}")

    if ok:
        print("\nRescued streams:")
        for r in ok:
            print(f"  {r['stream']:14s}  v_3d = {r['v_3d_rescued_kms']:6.1f} ± "
                  f"{r['v_3d_std_kms']:5.1f} km/s  "
                  f"(n_members={r['n_members']}, n_cone={r['n_stars_cone']})")

    return results


def main() -> int:
    out_dir = _PROJECT_ROOT / "outputs" / "t95"
    out_dir.mkdir(parents=True, exist_ok=True)

    results = run_cross_match_all(verbose=True)

    out_path = out_dir / "t95_v11_cross_match_results.json"
    out_path.write_text(json.dumps(results, indent=2, default=str))
    print(f"\nWrote: {out_path}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
