"""
T95.13 — DESI DR1 Milky Way Survey cross-match for the 7 T95.11 outliers.

PURPOSE
=======
T95.11 (Gaia DR3 cross-match) rescued 6 of 13 degenerate streams.
The 7 outliers either:
  - Are too distant for Gaia pm (Eridanus, 95 kpc)
  - Have track geometry Gaia cone can't handle (Molonglo, Murrumbidgee ~360°)
  - Have too few Gaia members (Orinoco, Perpendicular)
  - Have heavy field contamination (Pal15, Parallel)

DESI DR1 (released 2024) covers ~14,000 deg² of Milky Way Survey targets
with radial velocities, metallicities, and Gaia cross-matches via source_id.
For halo streams too faint for Gaia pm but observed by DESI, this gives v_r
constraints even without proper motion.

OUTPUT: JSON with per-stream DESI coverage + recovered kinematics
"""
from __future__ import annotations

import json
import re
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

# Reuse helpers from T95.11
sys.path.insert(0, str(Path(__file__).resolve().parent))
from t95_v11_gaia_cross_match import get_stream_center  # noqa: E402

# ============================================================================
# DESI DR1 TAP config
# ============================================================================
DESI_TAP_URL = "https://datalab.noirlab.edu/tap/sync"
DESI_MWS_TABLE = "desi_dr1.mws"
DESI_TIMEOUT_S = 60
MAX_HALF_WIDTH_DEG = 1.5  # avoid hitting DESI row limits

# The 7 T95.11 outliers that Gaia couldn't rescue
OUTLIER_STREAMS = [
    "Eridanus", "Molonglo", "Murrumbidgee", "Orinoco",
    "Pal15", "Parallel", "Perpendicular",
]


def votable_to_rows(raw_xml: bytes):
    """Parse a VOTable XML response into a list of dict rows.

    Uses regex (not ElementTree) for resilience against large responses
    and namespace quirks in the NOIRLab TAP service.
    """
    text = raw_xml.decode("utf-8", errors="replace")

    # Extract field names from the FIRST <TABLE> block (results table)
    fields = re.findall(r'<FIELD\s+[^>]*name="([^"]+)"', text)
    if not fields:
        return [], []

    rows = []
    # Match each <TR>...</TR> in the data section
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
    """Box-query DESI MWS for stars near a position.

    Returns dict with: rows (list), n_rows (int), wall_s (float),
    col_names (list).

    NOTE: NOIRLab TAP rejects:
      - IVOA POINT/CIRCLE syntax (no PostGIS POINT fn)
      - User-defined functions in WHERE (no q3c_radial_query, no CONTAINS)
    Workaround: box query on (ra, dec) and filter client-side by great-circle dist.
    """
    # ADQL box query (RA crosses 0/360 deg, but our 3° boxes are small enough
    # that this only matters near RA=0; galstreams center avoids that).
    q = f"""
    SELECT vrad, vrad_err, feh, alphafe, snr_med,
           target_ra, target_dec, glon, glat, source_id
    FROM {DESI_MWS_TABLE}
    WHERE target_ra BETWEEN {ra_deg - half_width_deg:.6f} AND {ra_deg + half_width_deg:.6f}
      AND target_dec BETWEEN {dec_deg - half_width_deg:.6f} AND {dec_deg + half_width_deg:.6f}
      AND vrad IS NOT NULL
    """
    # NOTE: we filter vrad_err < 10 client-side because the NOIRLab query
    # planner hangs on that filter (verified 2026-09-08).
    params = urllib.parse.urlencode({"REQUEST": "doQuery", "QUERY": q, "LANG": "ADQL"})
    t0 = time.time()
    req = urllib.request.Request(DESI_TAP_URL + "?" + params)
    try:
        with urllib.request.urlopen(req, timeout=DESI_TIMEOUT_S) as r:
            raw = r.read()
            wall_s = time.time() - t0
            # Check for VO error
            if b'QUERY_STATUS" value="ERROR' in raw:
                err_text = raw.decode("utf-8", errors="replace")[:500]
                return {"status": "query_error", "error": err_text, "wall_s": wall_s}
            rows, col_names = votable_to_rows(raw)
            return {
                "status": "ok",
                "rows": rows,
                "n_rows": len(rows),
                "col_names": col_names,
                "wall_s": wall_s,
            }
    except Exception as e:
        return {"status": "exception", "error": str(e), "wall_s": time.time() - t0}


def cross_match_stream_desi(stream_name: str, radius_deg: float = 0.5) -> dict:
    """Cross-match a single stream against DESI MWS."""
    try:
        center = get_stream_center(stream_name)
    except Exception as e:
        return {"stream": stream_name, "status": "no_center", "error": str(e)}

    print(f"\n=== {stream_name} ===")
    print(f"  on-sky: RA={center['ra_center_deg']:.3f}°  Dec={center['dec_center_deg']:.3f}°")
    print(f"  cone radius: {radius_deg}°")

    # Box query, then client-side great-circle filter.
    # Cap half-width at MAX_HALF_WIDTH_DEG to avoid hitting DESI's row limits
    # for streams with very large angular extent (Molonglo, Murrumbidgee, etc.).
    # Those streams genuinely need track-following, not a single box query.
    half_width = min(max(radius_deg, center.get("extent_p90_deg", radius_deg)),
                     MAX_HALF_WIDTH_DEG)
    result = desi_box_query(
        center["ra_center_deg"], center["dec_center_deg"], half_width
    )
    if result["status"] != "ok":
        print(f"  DESI query failed: {result.get('error', '')[:100]}")
        return {
            "stream": stream_name,
            "status": result["status"],
            "error": result.get("error", ""),
            "wall_s": result.get("wall_s", 0),
            **center,
        }

    # Filter to actual great-circle distance < radius_deg
    import math
    rows = []
    for r in result["rows"]:
        ra1 = math.radians(center["ra_center_deg"])
        de1 = math.radians(center["dec_center_deg"])
        ra2 = math.radians(r["target_ra"])
        de2 = math.radians(r["target_dec"])
        # Wrap RA
        dra = (ra2 - ra1 + math.pi) % (2 * math.pi) - math.pi
        gc = math.sin((de2 - de1) / 2) ** 2 + math.cos(de1) * math.cos(de2) * math.sin(dra / 2) ** 2
        gc_deg = math.degrees(2 * math.asin(math.sqrt(min(gc, 1.0))))
        # Also filter vrad_err (client-side because NOIRLab query planner hangs)
        vrad_err = r.get("vrad_err")
        if gc_deg <= radius_deg and (vrad_err is None or vrad_err < 10.0):
            rows.append(r)

    n = len(rows)
    print(f"  DESI box hits: {result['n_rows']} in {result['wall_s']:.1f}s, {n} within {radius_deg}°")
    if n == 0:
        return {
            "stream": stream_name,
            "status": "no_desi_coverage",
            "n_desi_stars": 0,
            "wall_s": result["wall_s"],
            **center,
        }

    # Compute kinematics from DESI vrad alone
    vrads = sorted([r["vrad"] for r in rows if r.get("vrad") is not None])
    vrad_med = vrads[len(vrads) // 2]
    vrad_std = (vrads[int(0.84 * len(vrads))] - vrads[int(0.16 * len(vrads))]) / 2.0

    fehs = [r["feh"] for r in rows if r.get("feh") is not None]
    feh_med = sorted(fehs)[len(fehs) // 2] if fehs else None

    # If we have Gaia cross-match (source_id), check for pm too
    has_pm = sum(1 for r in rows if r.get("source_id")) > 0

    print(f"  v_r median = {vrad_med:.1f} km/s, scatter ~ {vrad_std:.1f} km/s, n={n}")
    if feh_med is not None:
        print(f"  [Fe/H] median = {feh_med:.2f}")
    print(f"  {sum(1 for r in rows if r.get('source_id'))}/{n} have Gaia source_id (potential pm cross-match)")

    return {
        "stream": stream_name,
        "status": "ok",
        "n_desi_stars": n,
        "n_desi_box": result["n_rows"],
        "vrad_median_kms": float(vrad_med),
        "vrad_std_kms": float(vrad_std),
        "feh_median": float(feh_med) if feh_med is not None else None,
        "n_with_feh": len(fehs),
        "n_with_source_id": sum(1 for r in rows if r.get("source_id")),
        "wall_s": result["wall_s"],
        **center,
    }


def main():
    out_path = (Path(__file__).resolve().parents[1] / "outputs" /
                "t95" / "t95_v13_desi_cross_match_results.json")
    out_path.parent.mkdir(parents=True, exist_ok=True)

    print(f"Querying DESI DR1 MWS at {DESI_TAP_URL}")
    print(f"Streams: {len(OUTLIER_STREAMS)} outliers from T95.11")

    results = []
    for stream in OUTLIER_STREAMS:
        try:
            r = cross_match_stream_desi(stream)
        except Exception as e:
            r = {"stream": stream, "status": "exception", "error": str(e)}
        results.append(r)
        time.sleep(2)  # Be polite to the TAP service

    with out_path.open("w") as f:
        json.dump(results, f, indent=2)

    # Summary
    n_ok = sum(1 for r in results if r["status"] == "ok")
    n_no_cov = sum(1 for r in results if r["status"] == "no_desi_coverage")
    n_err = len(results) - n_ok - n_no_cov
    print(f"\nSummary:")
    print(f"  {n_ok}/7 streams have DESI coverage")
    print(f"  {n_no_cov}/7 have no coverage")
    print(f"  {n_err}/7 had errors")
    print(f"  Written: {out_path}")


if __name__ == "__main__":
    main()
