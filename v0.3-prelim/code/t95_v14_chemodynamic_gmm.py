"""
T95.14 — Chemodynamic GMM with DESI [Fe/H] prior.

PURPOSE
=======
T95.12's 2-component GMM (pm+parallax+color+mag) failed because the 2
components couldn't separate stream from field when the field is a
multi-modal mix of disk + halo + LMC debris.

T95.13 added DESI radial velocities for Parallel and Perpendicular. The
[Fe/H] column gives a STELLAR POPULATION tag:
  - Disk stars:    [Fe/H] ~ -0.5 to +0.2
  - Halo stars:    [Fe/H] ~ -1.5 to -0.5
  - Dwarf-galaxy streams:  [Fe/H] ~ -2.0 to -1.0
  - Globular cluster streams:  [Fe/H] ~ -0.5 to -2.5 (depends on cluster)

Both Parallel and Perpendicular are presumed halo streams, so a [Fe/H]
cut below -0.5 should remove most disk contamination.

METHOD (T95.14):
  1. Pull DESI MWS stars in a 0.5° cone (T95.13 output)
  2. Filter to [Fe/H] < -0.5 (metal-poor, halo-like)
  3. Cross-match with Gaia via source_id to get proper motions
  4. Fit a tighter GMM (now in a cleaner sub-population)
  5. Compare v_r to T95.11 to validate
"""
from __future__ import annotations

import json
import re
import sys
import time
import urllib.parse
import urllib.request
import warnings
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from t95_v11_gaia_cross_match import get_stream_center  # noqa: E402

from sklearn.mixture import GaussianMixture
from sklearn.preprocessing import StandardScaler

# ============================================================================
# Config
# ============================================================================
DESI_TAP_URL = "https://datalab.noirlab.edu/tap/sync"
DESI_MWS_TABLE = "desi_dr1.mws"
FEH_CUT = -0.5  # Halo-like metallicity threshold
GMM_FEATURES = ["pmra", "pmdec", "parallax", "bp_rp", "phot_g_mean_mag"]
GMM_MAX_ITER = 200
GMM_TOL = 1e-4
GMM_N_INIT = 5
RANDOM_STATE = 42

# Streams with DESI coverage (from T95.13)
CHEMODYNAMIC_STREAMS = ["Parallel", "Perpendicular"]


def votable_to_rows(raw_xml: bytes):
    """Parse VOTable XML response into a list of dict rows."""
    text = raw_xml.decode("utf-8", errors="replace")
    fields = re.findall(r'<FIELD\s+[^>]*name="([^"]+)"', text)
    if not fields:
        return [], []
    rows = []
    for tr_match in re.finditer(r'<TR>(.*?)</TR>', text, re.DOTALL):
        tr_text = tr_match.group(1)
        cells = re.findall(r'<TD[^>]*>([^<]*)</TD>', tr_text)
        row = {}
        for i, val in enumerate(cells):
            if i >= len(fields):
                break
            v = val.strip() if val else None
            if v is None or v == "":
                row[fields[i]] = None
            else:
                try:
                    row[fields[i]] = float(v)
                except (ValueError, TypeError):
                    if v.lower() in ("true", "false"):
                        row[fields[i]] = v.lower() == "true"
                    else:
                        row[fields[i]] = v
        rows.append(row)
    return rows, fields


def desi_box_query(ra_deg: float, dec_deg: float, half_width_deg: float) -> dict:
    """Pull DESI MWS stars in a box around the stream center."""
    q = f"""
    SELECT vrad, vrad_err, feh, alphafe, snr_med,
           target_ra, target_dec, glon, glat, source_id
    FROM {DESI_MWS_TABLE}
    WHERE target_ra BETWEEN {ra_deg - half_width_deg:.6f} AND {ra_deg + half_width_deg:.6f}
      AND target_dec BETWEEN {dec_deg - half_width_deg:.6f} AND {dec_deg + half_width_deg:.6f}
      AND vrad IS NOT NULL
      AND feh IS NOT NULL
    """
    params = urllib.parse.urlencode({"REQUEST": "doQuery", "QUERY": q, "LANG": "ADQL"})
    t0 = time.time()
    req = urllib.request.Request(DESI_TAP_URL + "?" + params)
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            raw = r.read()
            wall_s = time.time() - t0
            if b'QUERY_STATUS" value="ERROR' in raw:
                return {"status": "query_error", "error": raw.decode()[:300], "wall_s": wall_s}
            rows, fields = votable_to_rows(raw)
            return {"status": "ok", "rows": rows, "n_rows": len(rows), "wall_s": wall_s}
    except Exception as e:
        return {"status": "exception", "error": str(e), "wall_s": time.time() - t0}


def cross_match_gaia_source_ids(source_ids):
    """Batch cross-match DESI source_ids to Gaia DR3 for proper motion."""
    if not source_ids:
        return {}
    # Filter out None
    valid_ids = [s for s in source_ids if s is not None]
    if not valid_ids:
        return {}
    # Build IN clause
    id_list = ",".join(str(int(s)) for s in valid_ids[:500])  # cap at 500
    adql = f"""
    SELECT source_id, pmra, pmdec, parallax, parallax_error,
           bp_rp, phot_g_mean_mag, radial_velocity
    FROM gaiadr3.gaia_source
    WHERE source_id IN ({id_list})
    """
    from astroquery.gaia import Gaia
    t0 = time.time()
    try:
        job = Gaia.launch_job(adql, dump_to_file=False, verbose=False)
        table = job.get_results()
        wall_s = time.time() - t0
        out = {}
        for row in table:
            sid = int(row["source_id"])
            out[sid] = {
                "pmra": float(row["pmra"]) if row["pmra"] is not None else None,
                "pmdec": float(row["pmdec"]) if row["pmdec"] is not None else None,
                "parallax": float(row["parallax"]) if row["parallax"] is not None else None,
                "parallax_error": float(row["parallax_error"]) if row["parallax_error"] is not None else None,
                "bp_rp": float(row["bp_rp"]) if row["bp_rp"] is not None else None,
                "phot_g_mean_mag": float(row["phot_g_mean_mag"]) if row["phot_g_mean_mag"] is not None else None,
                "rv_gaia": float(row["radial_velocity"]) if row["radial_velocity"] is not None else None,
            }
        return {"status": "ok", "lookup": out, "n_found": len(out), "wall_s": wall_s}
    except Exception as e:
        return {"status": "exception", "error": str(e), "wall_s": time.time() - t0}


def gmm_select(members_df: pd.DataFrame, expected_distance_kpc: float, verbose=False):
    """Run T95.12 GMM on metal-poor DESI-selected members."""
    df_clean = members_df.dropna(subset=GMM_FEATURES).copy()
    if len(df_clean) < 10:
        if verbose:
            print(f"  GMM skipped: only {len(df_clean)} clean rows after [Fe/H] cut")
        return df_clean, None, None, None

    X = df_clean[GMM_FEATURES].values
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    # Init: stream at parallax-filtered median, field at global mean
    df_clean["plx_snr"] = df_clean["parallax"] / df_clean["parallax_error"]
    df_plx = df_clean[df_clean["plx_snr"] > 5]
    stream_init = df_plx[GMM_FEATURES].median().values if len(df_plx) >= 5 else df_clean[GMM_FEATURES].median().values
    field_init = df_clean[GMM_FEATURES].mean().values
    stream_init_scaled = (stream_init - scaler.mean_) / scaler.scale_
    field_init_scaled = (field_init - scaler.mean_) / scaler.scale_

    n_features = len(GMM_FEATURES)
    init_means = np.vstack([stream_init_scaled, field_init_scaled])
    init_covars = np.zeros((2, n_features, n_features))
    init_covars[0] = 0.01 * np.eye(n_features)
    init_covars[1] = 5.0 * np.eye(n_features)
    init_weights = np.array([0.05, 0.95])

    gmm = GaussianMixture(
        n_components=2, covariance_type="full",
        means_init=init_means,
        precisions_init=np.linalg.inv(init_covars),
        weights_init=init_weights,
        max_iter=GMM_MAX_ITER, tol=GMM_TOL,
        n_init=GMM_N_INIT, random_state=RANDOM_STATE,
    )
    gmm.fit(X_scaled)
    probs = gmm.predict_proba(X_scaled)
    p_stream = probs[:, 0]
    df_clean["p_stream"] = p_stream
    members = df_clean[p_stream > 0.3].copy()  # looser threshold for low-N case
    if verbose:
        print(f"  GMM: {len(members)}/{len(df_clean)} members ({100*len(members)/len(df_clean):.1f}%)")
        print(f"  Stream component pm: ({gmm.means_[0,0]:.2f}, {gmm.means_[0,1]:.2f}) scaled")
    return members, gmm, scaler, df_clean


def cross_match_stream_chemodynamic(stream_name: str, feh_cut: float = FEH_CUT,
                                     radius_deg: float = 0.5, verbose=True) -> dict:
    """Cross-match a stream using DESI [Fe/H] + Gaia pm via source_id."""
    try:
        center = get_stream_center(stream_name)
    except Exception as e:
        return {"stream": stream_name, "status": "no_center", "error": str(e)}

    if verbose:
        print(f"\n=== {stream_name} ===")
        print(f"  on-sky: RA={center['ra_center_deg']:.3f}°  Dec={center['dec_center_deg']:.3f}°")

    # Pull DESI MWS in box (must be smaller than 1.5° to avoid timeout)
    half_width = max(radius_deg, center.get("extent_p90_deg", radius_deg))
    half_width = min(half_width, 1.5)
    r = desi_box_query(center["ra_center_deg"], center["dec_center_deg"], half_width)
    if r["status"] != "ok":
        return {"stream": stream_name, "status": r["status"],
                "error": r.get("error", ""), "wall_s": r.get("wall_s", 0), **center}

    # Apply great-circle filter and feh cut client-side
    import math
    rows = []
    for row in r["rows"]:
        ra1 = math.radians(center["ra_center_deg"])
        de1 = math.radians(center["dec_center_deg"])
        ra2 = math.radians(row["target_ra"])
        de2 = math.radians(row["target_dec"])
        dra = (ra2 - ra1 + math.pi) % (2 * math.pi) - math.pi
        gc = math.sin((de2 - de1) / 2) ** 2 + math.cos(de1) * math.cos(de2) * math.sin(dra / 2) ** 2
        gc_deg = math.degrees(2 * math.asin(math.sqrt(min(gc, 1.0))))
        if gc_deg > radius_deg:
            continue
        # vrad_err filter
        if row.get("vrad_err") is not None and row["vrad_err"] >= 10.0:
            continue
        # [Fe/H] cut
        if row.get("feh") is not None and row["feh"] < feh_cut:
            rows.append(row)

    if verbose:
        print(f"  DESI box: {r['n_rows']}, within {radius_deg}° + [Fe/H]<{feh_cut}: {len(rows)}")

    if len(rows) < 10:
        return {"stream": stream_name, "status": "too_few_metal_poor",
                "n_metal_poor": len(rows), "wall_s": r["wall_s"], **center}

    # Pull Gaia cross-match for these source_ids
    sids = [row.get("source_id") for row in rows if row.get("source_id") is not None]
    gaia_result = cross_match_gaia_source_ids(sids)
    if isinstance(gaia_result, dict) and gaia_result.get("status") != "ok":
        return {"stream": stream_name, "status": "gaia_xmatch_failed",
                "error": gaia_result.get("error", ""), "wall_s": r["wall_s"], **center}

    # Build combined dataframe
    combined = []
    for row in rows:
        sid = row.get("source_id")
        if sid is None or int(sid) not in gaia_result["lookup"]:
            continue
        g = gaia_result["lookup"][int(sid)]
        combined.append({
            "source_id": int(sid),
            "pmra": g["pmra"], "pmdec": g["pmdec"],
            "parallax": g["parallax"], "parallax_error": g["parallax_error"],
            "bp_rp": g["bp_rp"], "phot_g_mean_mag": g["phot_g_mean_mag"],
            "vrad_desi": row.get("vrad"),
            "feh": row.get("feh"),
            "target_ra": row.get("target_ra"),
            "target_dec": row.get("target_dec"),
        })
    df = pd.DataFrame(combined)
    df = df.dropna(subset=GMM_FEATURES + ["vrad_desi"])
    if verbose:
        print(f"  Combined DESI+Gaia: {len(df)} stars")

    # Run GMM on metal-poor subsample
    members, gmm, scaler, df_clean = gmm_select(df, center["distance_kpc"], verbose=verbose)
    if len(members) < 3:
        # GMM too restrictive for low-N. Fall back to member-median of all
        # metal-poor DESI+Gaia stars (already filtered to halo-like [Fe/H]).
        if verbose:
            print(f"  Fallback: using all {len(df)} metal-poor stars (GMM too restrictive)")
        members = df.copy()
        gmm = scaler = None
    if len(members) < 1:
        return {"stream": stream_name, "status": "no_members",
                "n_members": 0, "wall_s": r["wall_s"] + gaia_result["wall_s"], **center}

    if gmm is not None:
        stream_mean = gmm.means_[0] * scaler.scale_ + scaler.mean_
        gmm_pmra = float(stream_mean[0])
        gmm_pmdec = float(stream_mean[1])
        gmm_parallax = float(stream_mean[2])
    else:
        gmm_pmra = gmm_pmdec = gmm_parallax = 0.0

    # Member-median kinematics
    pmra_med = float(members["pmra"].median())
    pmdec_med = float(members["pmdec"].median())
    vrad_med = float(members["vrad_desi"].median())
    feh_med = float(members["feh"].median())
    pm_mag = np.sqrt(pmra_med**2 + pmdec_med**2)
    v_t = 4.74 * pm_mag * center["distance_kpc"]
    v_3d = float(np.sqrt(v_t**2 + vrad_med**2))

    if verbose:
        print(f"  Chemodynamic median: pmra={pmra_med:.2f}, pmdec={pmdec_med:.2f}, "
              f"v_r={vrad_med:.1f} km/s, [Fe/H]={feh_med:.2f}")
        print(f"  v_t = {v_t:.1f}, v_3d = {v_3d:.1f} km/s")
        print(f"  GMM component pm: ({gmm_pmra:.2f}, {gmm_pmdec:.2f})")

    return {
        "stream": stream_name,
        "status": "ok",
        "n_desi_total": r["n_rows"],
        "n_metal_poor": len(rows),
        "n_combined_gaia_desi": len(df),
        "n_members": len(members),
        "feh_cut": feh_cut,
        "pmra_median_mas_yr": pmra_med,
        "pmdec_median_mas_yr": pmdec_med,
        "vrad_median_kms": vrad_med,
        "feh_median": feh_med,
        "v_t_rescued_kms": v_t,
        "v_3d_rescued_kms": v_3d,
        "gmm_pmra_mas_yr": gmm_pmra,
        "gmm_pmdec_mas_yr": gmm_pmdec,
        "wall_s": r["wall_s"] + gaia_result["wall_s"],
        **center,
    }


def main():
    out_path = (Path(__file__).resolve().parents[1] / "outputs" /
                "t95" / "t95_v14_chemodynamic_results.json")
    out_path.parent.mkdir(parents=True, exist_ok=True)

    warnings.filterwarnings("ignore")
    print(f"Chemodynamic GMM with [Fe/H] < {FEH_CUT} cut")
    print(f"Streams: {CHEMODYNAMIC_STREAMS}")

    results = []
    for s in CHEMODYNAMIC_STREAMS:
        warnings.filterwarnings("ignore")
        r = cross_match_stream_chemodynamic(s)
        results.append(r)
        time.sleep(2)

    with out_path.open("w") as f:
        json.dump(results, f, indent=2)

    # Compare to T95.11 / T95.13
    t95_11 = json.load(open(Path(__file__).resolve().parents[1] / "outputs" /
                            "t95" / "t95_v11_cross_match_results.json"))
    t95_13 = json.load(open(Path(__file__).resolve().parents[1] / "outputs" /
                            "t95" / "t95_v13_desi_cross_match_results.json"))

    print("\n=== COMPARISON ===")
    print(f"{'Stream':15s} {'T95.11 v_3d':12s} {'T95.13 v_r':12s} {'T95.14 v_r':12s} {'T95.14 v_3d':12s}")
    for r in results:
        if r["status"] != "ok":
            print(f"{r['stream']:15s} FAILED: {r.get('status')}")
            continue
        t11 = next((x for x in t95_11 if x.get("stream") == r["stream"]), None)
        t13 = next((x for x in t95_13 if x.get("stream") == r["stream"]), None)
        t11_v3d = f"{t11['v_3d_rescued_kms']:.1f}" if t11 else "—"
        t13_vr = f"{t13.get('vrad_median_kms', 0):.1f}" if t13 and t13.get("vrad_median_kms") else "—"
        print(f"{r['stream']:15s} {t11_v3d:>12s} {t13_vr:>12s} "
              f"{r['vrad_median_kms']:>12.1f} {r['v_3d_rescued_kms']:>12.1f}")

    print(f"\nWritten: {out_path}")


if __name__ == "__main__":
    main()
