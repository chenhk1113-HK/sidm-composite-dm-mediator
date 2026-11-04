"""Stage-3 sample builder: pick RELHIC-like IllustrisTNG subhalos and pull their merger trees.

Design constraints:
  - PC is a single workstation (RX 7900 XTX, ~64 GB RAM, ~1 TB free). No bulk download: only
    per-subhalo API reads, which are KB-scale each.
  - The API throttles: pace requests, treat HTML bodies / 403 / 504 as retry, not failure.
  - Never trust server-side filters blindly: every accepted candidate is re-verified from its
    detail record (the list endpoint omits len_dm).
Outputs (all small):
  v0.3-prelim/data/results/tng_stage3_sample_manifest.json   (committed provenance + stats)
  v0.3-prelim/data/external/tng/stage3_sample/trees/<run>-<snap>-<subhalo_id>.json  (raw trees)
  v0.3-prelim/data/external/tng/stage3_sample/candidates.csv  (local table, not committed)
"""
from __future__ import annotations
import csv
import gzip
import os
import json
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

REPO = Path(r"C:/Users/lamkuenai/projects/sidm-composite-dm-mediator")
KEY = Path.home().joinpath(".tng_api_key").read_text(encoding="utf-8").strip()
BASE = "https://www.tng-project.org/api/"
OUT_RESULTS = REPO / "v0.3-prelim" / "data" / "results"
SAMPLE_NAME = os.environ.get("TNG_SAMPLE", "stage3_sample")
OUT_EXT = REPO / "v0.3-prelim" / "data" / "external" / "tng" / SAMPLE_NAME
OUT_TREES = OUT_EXT / "trees"
PACE_S = float(os.environ.get("TNG_PACE", "7.0"))
MAX_TRIES = 5
H = 0.6774
UNIT = 1e10 / H            # native SubhaloMass unit in Msun
# Every band parameter is env-overridable so a tier-2 sample is the SAME code, not a fork.
BAND_LO_MSUN = float(os.environ.get("TNG_MASS_LO", 10.0 ** 7.5))
BAND_HI_MSUN = float(os.environ.get("TNG_MASS_HI", 1e9))
VMAX_LO = float(os.environ.get("TNG_VMAX_LO", 15.0))
VMAX_HI = float(os.environ.get("TNG_VMAX_HI", 45.0))
LEN_DM_LO = int(os.environ.get("TNG_LEN_DM_LO", 100))
LEN_DM_HI = int(os.environ.get("TNG_LEN_DM_HI", 4000))
GAS_MIN_NATIVE = float(os.environ.get("TNG_GAS_MIN", "1e-5"))   # >= 1.476e5 Msun native

# mass_dm (Msun) per run, from simulation metadata (probe 9/10, cross-checked against
# catalog mass/len_dm on real records)
MASS_DM = {"TNG50-1": 4.537e5, "TNG100-1": 7.463e6, "TNG300-1": 5.880e7}
TARGETS = json.loads(os.environ.get("TNG_TARGETS", '{"TNG50-1": 60, "TNG100-1": 30}'))


def log(msg: str) -> None:
    print(msg, flush=True)


def api(path: str, *, tries: int = MAX_TRIES):
    last = None
    for attempt in range(tries):
        # the TNG API authenticates with the header name "api-key" (docs:
        # https://www.tng-project.org/data/docs/api/); "X-API-Key" yields HTTP 403
        # "Permission Denied" on every request. Absolute URLs (the tree URLs the detail
        # record advertises) are used verbatim.
        url = path if str(path).startswith("http") else BASE + str(path).lstrip("/")
        try:
            req = urllib.request.Request(url, headers={"api-key": KEY,
                                                       "accept": "application/json"})
            with urllib.request.urlopen(req, timeout=240) as r:
                raw = r.read()
        except urllib.error.HTTPError as exc:
            last = f"HTTP {exc.code}"
            time.sleep(PACE_S * (attempt + 2))
            continue
        except Exception as exc:  # timeouts, connection reset
            last = f"{type(exc).__name__}: {exc}"
            time.sleep(PACE_S * (attempt + 2))
            continue
        if raw[:2] == b"\x1f\x8b":
            raw = gzip.decompress(raw)
        if raw[:1] in (b"<", b"\n", b" "):
            last = "HTML throttle body"
            time.sleep(PACE_S * (attempt + 2))
            continue
        try:
            return json.loads(raw.decode("utf-8"))
        except Exception as exc:
            last = f"json decode failed: {exc}"
            time.sleep(PACE_S)
            continue
    raise RuntimeError(f"API failed for {path}: {last}")


def band_params(run: str) -> str:
    return (f"snapshots/99/subhalos/?primary_flag=1&len_stars__lt=1"
            f"&vmax__gt={VMAX_LO}&vmax__lt={VMAX_HI}"
            f"&mass__gt={BAND_LO_MSUN / UNIT:.6e}&mass__lt={BAND_HI_MSUN / UNIT:.6e}"
            f"&mass_gas__gt={GAS_MIN_NATIVE:.3e}"
            f"&len_dm__gt={LEN_DM_LO}&len_dm__lt={LEN_DM_HI}"
            f"&order=mass&sorting=asc&count=100")


def band_list(run: str, max_pages: int = 25):
    """Paginate the whole band (follows the API's own `next` URL) and return all ids."""
    ids, page_url = [], f"{run}/{band_params(run)}"
    pages = 0
    while page_url and pages < max_pages:
        res = api(page_url)
        rows = res.get("results", [])
        ids.extend(r["id"] for r in rows)
        pages += 1
        nxt = res.get("next")
        page_url = nxt.replace("http://", "https://") if nxt else None
        log(f"  [{run}] page {pages}: {len(rows)} rows (total {len(ids)}, "
            f"server count {res.get('count')})")
        time.sleep(PACE_S / 2)
    return ids, pages


def main() -> int:
    OUT_TREES.mkdir(parents=True, exist_ok=True)
    manifest = {
        "test": "tng_stage3_sample",
        "built_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "band": {"vmax_kms": [VMAX_LO, VMAX_HI], "mass_msun": [BAND_LO_MSUN, BAND_HI_MSUN],
                 "starless": True, "primary_only": True,
                 "gas_min_native": GAS_MIN_NATIVE, "len_dm_window": [LEN_DM_LO, LEN_DM_HI]},
        "native_mass_window": [BAND_LO_MSUN / UNIT, BAND_HI_MSUN / UNIT],
        "unit_msun": UNIT, "h": H, "mass_dm_msun": MASS_DM,
        "runs": {}, "rejected": [],
    }
    rows = []
    for run, want in TARGETS.items():
        log(f"[{run}] paginating the full band list")
        cand_ids, pages = band_list(run)
        log(f"[{run}] band list gave {len(cand_ids)} ids over {pages} page(s); "
            f"thin to {want} by taking every max(1, len//{want})-th "
            f"(mass-ascending order, so the sample spans the band)")
        step = max(1, len(cand_ids) // max(1, want)) if cand_ids else 1
        picked = cand_ids[::step][:want]
        accepted, refused = 0, 0
        manifest["runs"][run] = {"requested": len(picked), "accepted": 0,
                                 "tree_ok": 0, "tree_failed": 0, "detail": []}
        for sid in picked:
            det = api(f"{run}/snapshots/99/subhalos/{sid}/")
            mass_msun = det.get("mass", 0.0) * UNIT
            vmax = det.get("vmax", 0.0)
            len_dm = det.get("len_dm", 0)
            len_stars = det.get("len_stars", 0)
            mass_gas_msun = det.get("mass_gas", 0.0) * UNIT
            primary = det.get("primary_flag", 0)
            # read-back verification of every cut (server filters are not trusted)
            ok = (primary == 1 and len_stars < 1 and VMAX_LO <= vmax <= VMAX_HI
                  and BAND_LO_MSUN <= mass_msun <= BAND_HI_MSUN
                  and mass_gas_msun >= GAS_MIN_NATIVE * UNIT
                  and LEN_DM_LO <= len_dm <= LEN_DM_HI)
            if not ok:
                refused += 1
                manifest["rejected"].append({"run": run, "id": sid, "mass_msun": mass_msun,
                                             "vmax": vmax, "len_dm": len_dm,
                                             "len_stars": len_stars,
                                             "mass_gas_msun": mass_gas_msun})
                log(f"  [{run}/{sid}] REJECTED on read-back "
                    f"mass={mass_msun:.3e} vmax={vmax} len_dm={len_dm} stars={len_stars}")
                continue
            time.sleep(PACE_S)
            tree_ok, tree_keys, n_nodes, n_prog = True, [], 0, 0
            rec_tree_format = None
            # the tree endpoints are advertised BY THE DETAIL RECORD (detail["trees"] -> format:
            # absolute URL). The hand-built ".../trees/" path is not an endpoint and returns HTML.
            tree_urls = {k: v.replace("http://", "https://")
                         for k, v in (det.get("trees") or {}).items() if isinstance(v, str)}
            chosen = None
            for pref in ("sublink_simple", "sublink_mpb", "sublink_full", "lhalotree_full"):
                if pref in tree_urls:
                    chosen = (pref, tree_urls[pref])
                    break
            if chosen is None and tree_urls:
                chosen = sorted(tree_urls.items())[0]
            if chosen is None:
                tree_ok = False
                log(f"  [{run}/{sid}] detail advertises no tree URL "
                    f"(detail keys: {sorted(det.keys())[:10]})")
            else:
                pref, turl = chosen
                try:
                    trees = api(turl)
                    (OUT_TREES / f"{run}-99-{sid}.json").write_text(
                        json.dumps(trees), encoding="utf-8")
                    if isinstance(trees, dict):
                        tree_keys = sorted(trees.keys())
                        for k in ("Main", "Mergers", "Len", "SubhaloID"):
                            if k in trees and isinstance(trees[k], (list, dict)):
                                inner = trees[k]
                                n_nodes = max(n_nodes, len(inner.get("SubhaloID", []))
                                              if isinstance(inner, dict) else len(inner))
                        n_prog = len(trees.get("Mergers", [])) if isinstance(
                            trees.get("Mergers"), list) else 0
                except Exception as exc:
                    tree_ok = False
                    log(f"  [{run}/{sid}] tree fetch failed ({pref}): {exc}")
            if tree_ok and chosen:
                rec_tree_format = chosen[0]
            accepted += 1
            manifest["runs"][run]["accepted"] = accepted
            manifest["runs"][run]["tree_ok"] += int(tree_ok)
            manifest["runs"][run]["tree_failed"] += int(not tree_ok)
            rec = {"run": run, "subhalo_id": sid, "snap": 99, "mass_msun": mass_msun,
                   "vmax_kms": vmax, "veldisp_kms": det.get("vel_disp", None),
                   "len_dm": len_dm, "len_stars": len_stars,
                   "mass_gas_msun": mass_gas_msun, "len_gas": det.get("len_gas", 0),
                   "n_particles_min_resolved": mass_msun / MASS_DM[run],
                   "tree_ok": tree_ok, "tree_nodes": n_nodes,
                   "tree_mergers": n_prog,
                   "tree_format": rec_tree_format if tree_ok else None,
                   "tree_keys": tree_keys[:14]}
            manifest["runs"][run]["detail"].append(rec)
            rows.append(rec)
            log(f"  [{run}/{sid}] OK mass={mass_msun:.3e} Msun vmax={vmax} km/s "
                f"len_dm={len_dm} gas={mass_gas_msun:.2e} Msun "
                f"particles_if_resolved={rec['n_particles_min_resolved']:.0f} tree={tree_ok}")
            time.sleep(PACE_S)
        log(f"[{run}] accepted {accepted} of {len(picked)} (refused {refused})")

    rows.sort(key=lambda r: (r["run"], r["mass_msun"]))
    for run in manifest["runs"]:
        recs = manifest["runs"][run]["detail"]
        if recs:
            n = len(recs)
            manifest["runs"][run]["summary"] = {
                "n": n,
                "trees_ok": sum(1 for r in recs if r["tree_ok"]),
                "trees_failed": sum(1 for r in recs if not r["tree_ok"]),
                "mass_msun_min": min(r["mass_msun"] for r in recs),
                "mass_msun_max": max(r["mass_msun"] for r in recs),
                "vmax_kms_min": min(r["vmax_kms"] for r in recs),
                "vmax_kms_max": max(r["vmax_kms"] for r in recs),
                "len_dm_min": min(r["len_dm"] for r in recs),
                "len_dm_max": max(r["len_dm"] for r in recs),
                "len_dm_median": sorted(r["len_dm"] for r in recs)[n // 2],
            }
    OUT_RESULTS.mkdir(parents=True, exist_ok=True)
    (OUT_RESULTS / f"tng_{SAMPLE_NAME}_manifest.json").write_text(
        json.dumps(manifest, indent=2), encoding="utf-8")
    with open(OUT_EXT / "candidates.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    total_mb = sum(f.stat().st_size for f in OUT_TREES.glob("*.json")) / 1e6
    log(f"DONE candidates={len(rows)} trees={total_mb:.2f} MB "
        f"manifest={OUT_RESULTS / f'tng_{SAMPLE_NAME}_manifest.json'}")
    for run, s in manifest["runs"].items():
        log(f"  {run}: accepted={s['accepted']} trees_ok={s['tree_ok']} "
          f"trees_failed={s['tree_failed']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
