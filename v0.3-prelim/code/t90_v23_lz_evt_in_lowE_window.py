"""
T90.23 PATH 1 (DRY RUN) — LZ 248 keV data release: count [5, 50] keV events.

PURPOSE
=======
The LZ 220-day paper (arXiv:2609.02823, PRL submitted) reports one event at
248 +/- 23 (stat) +/- 23 (sys) keV. The T90 magnetic-moment interpretation
(v12) predicts that the same coupling should ALSO produce ~778 events at
LZ in the [5, 50] keV window (because the magnetic-m recoil spectrum is
broad and peaks at LOWER E_R than 248 keV for heavy DM at m_chi = 1 TeV).

If LZ's low-E_R event count in the public data release is ~778, that
strongly supports the magnetic-m interpretation. If it is ~0 (as the
standard SI/SD analysis expects), the magnetic-m interpretation is
contradicted (because v12 says ~500x more events live at low E_R than at
248 keV for this coupling).

This script is the DRY-RUN skeleton:
  - Documents the URLs and expected schemas for the LZ data release
  - Builds a robust download helper with retry + manual-fallback
  - Implements the per-event counting logic for [5, 50] keV
  - Compares against the magnetic-m prediction from v12

NO DATA IS DOWNLOADED AUTOMATICALLY. To run live:
  - Set T90_V23_DOWNLOAD=1 to attempt automatic download
  - Otherwise, place files in data/external/lz_2026/ manually

SOURCES
=======
- Paper: arXiv:2609.02823, "Search for dark matter particle interactions
  in an extended nuclear recoil energy window with the LUX-ZEPLIN (LZ)
  experiment" (Sept 2026). DOI: pending.
- HEPData record: 10.17182/hepdata.182472.v1 (per arXiv linking page;
  DOI was "not found" when probed 2026-09-09 -- likely mid-activation).
- LZ portal: https://lz.lbl.gov/ (no clean /data/ URL found; check
  preprint supplementary for direct links).
- 4.2 t-y HEPData reference: 10.17182/hepdata.155182.v2 (PRL 135, 011802,
  this is the EARLIER paper; the 248 keV paper has its own record).

EXPECTED FILE FORMATS
=====================
The LZ public data release typically includes:
  - per_event.csv: columns like run_id, event_id, s1_phe, s2_phe,
    drift_time_us, x_cm, y_cm, e_recoil_keV, etc.
  - selection_efficiency.csv: efficiency vs E_R
  - background_model.csv: expected counts per bin
  - (sometimes) likelihood_inputs.root for unbinned fits

The minimum we need is per-event E_R in the 5-270 keV analysis window
(the paper's nominal range).

OUTPUT
======
  - outputs/t90/t90_v23_lz_lowE_count.json
      Per-window count + ratio-to-prediction + verdict

WARNINGS
========
  - LZ raw waveform data is NOT public; only post-selection event lists.
  - The [5, 50] keV window overlaps the LZ standard SI/SD analysis region,
    so background expectations are well-characterized -- if [5, 50] keV has
    an unexplained ~700-event excess on top of standard backgrounds, that's
    the smoking gun.
  - A proper analysis uses E_R-binned Poisson likelihood, not a single
    count; this dry-run is a count comparison only. Full unbinned fit is
    a follow-up.
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import Optional

import numpy as np

# Project imports
_PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_PROJECT_ROOT / "code"))

# ---------------------------------------------------------------------------
# Configuration: where to look for / where to download
# ---------------------------------------------------------------------------

# Candidate URLs for the LZ 248 keV paper data release.
# Order matters: first reachable URL wins.
LZ_DATA_URLS = [
    # HEPData record for arXiv:2609.02823 (the 248 keV paper specifically).
    # DOI was not active when probed 2026-09-09 -- revisit when run.
    "https://www.hepdata.net/record/182472",
    # HEPData YAML for the 4.2 t-y paper (PRL 135, 011802); useful as a
    # schema reference even if not the exact dataset we want.
    "https://www.hepdata.net/download/submission/ins2841863/2/yaml",
    # The earlier PRL data release; has the per-event CSV in the Data table.
    "https://www.hepdata.net/download/table/ins2841863/Data/2/csv",
    # LZ preprint PDF (for offline reference, ~5-10 MB).
    "https://lz.lbl.gov/wp-content/uploads/sites/6/2026/08/LZ_Preprint_260901_Dark_Matter_EFT_Nuclear_Recoil_Search_at_Higher_Energies.pdf",
]

# Where the user (or auto-download) places the per-event CSV.
EXPECTED_DATA_DIR = _PROJECT_ROOT / "data" / "external_data" / "lz_2026"

# Files we look for, in order of preference.
EXPECTED_FILENAMES = [
    "lz_evt_sr0_sr1_per_event.csv",
    "per_event.csv",
    "events.csv",
    "Data.csv",  # HEPData Data table convention
]

# Analysis windows (keV nuclear-recoil energy)
WINDOW_248KEV = (200.0, 300.0)   # the headline event window
WINDOW_LOW_E = (5.0, 50.0)       # where v12 predicts ~778 excess events
WINDOW_FULL = (5.0, 270.0)       # paper's nominal analysis range
WINDOW_SIDEBAND = (50.0, 200.0)  # intermediate region for sanity check

# Magnetic-moment prediction at LZ-tuned coupling (from v12 dry-run,
# computed at mu_x = 6.10e-8 mu_N, m_chi = 1000 GeV).
MAG_MOMENT_PREDICTION = {
    "mu_x_mu_N": 6.10e-8,
    "m_chi_GeV": 1000.0,
    "N_pred_window_200_300_keV": 1.0,   # calibration anchor
    "N_pred_window_5_50_keV": 778.0,    # the smoking-gun prediction
    "N_pred_window_5_270_keV": 1500.0,  # approximate total (5-270 keV)
    "N_pred_window_50_200_keV": 720.0,  # intermediate sanity check
    "source": "t90_v12_detector_response.py at LZ-tuned coupling",
}


# ---------------------------------------------------------------------------
# Download helper (NEVER auto-runs unless T90_V23_DOWNLOAD=1)
# ---------------------------------------------------------------------------

def try_download(out_dir: Path, timeout_s: int = 60) -> Optional[Path]:
    """Attempt to download one of LZ_DATA_URLS into out_dir.

    Returns the local path of the downloaded file, or None if all failed
    or auto-download was disabled.

    IMPORTANT: This function ONLY runs if T90_V23_DOWNLOAD=1 is set in the
    environment. Otherwise it returns None immediately, expecting the user
    to download manually.
    """
    if os.environ.get("T90_V23_DOWNLOAD", "0") != "1":
        print("[dry-run] T90_V23_DOWNLOAD not set; skipping auto-download.")
        print("  To enable:  export T90_V23_DOWNLOAD=1")
        print(f"  Expected target dir: {out_dir}")
        return None

    out_dir.mkdir(parents=True, exist_ok=True)
    import urllib.request
    import urllib.error

    for url in LZ_DATA_URLS:
        try:
            print(f"[download] Trying {url}")
            # Derive filename from URL path
            name = url.rsplit("/", 1)[-1]
            if not name or name == url:
                name = "lz_data"
            target = out_dir / name
            req = urllib.request.Request(url, headers={"User-Agent": "sidm-t90/0.4"})
            with urllib.request.urlopen(req, timeout=timeout_s) as resp:
                target.write_bytes(resp.read())
            print(f"[download] OK: {target} ({target.stat().st_size:,} bytes)")
            return target
        except (urllib.error.URLError, TimeoutError, OSError) as exc:
            print(f"[download] FAIL: {url} -> {type(exc).__name__}: {exc}")
            continue

    print("[download] All candidate URLs failed.")
    return None


# ---------------------------------------------------------------------------
# Locate the per-event CSV (either from manual drop or auto-download)
# ---------------------------------------------------------------------------

def find_event_file(search_dir: Path) -> Optional[Path]:
    """Find the LZ per-event CSV in search_dir. Returns None if missing."""
    if not search_dir.exists():
        return None
    for name in EXPECTED_FILENAMES:
        candidate = search_dir / name
        if candidate.exists() and candidate.stat().st_size > 0:
            return candidate
    # Fall back: any *.csv in the directory
    csvs = sorted(search_dir.glob("*.csv"))
    return csvs[0] if csvs else None


# ---------------------------------------------------------------------------
# Count events in an E_R window
# ---------------------------------------------------------------------------

def load_event_table(csv_path: Path) -> "np.ndarray":
    """Load the LZ per-event CSV. Returns structured numpy array.

    The CSV columns are TBD -- we look for common candidate names for
    E_R (nuclear-recoil energy in keV). If we can't find a likely column,
    we raise with an actionable error.
    """
    # Read header first
    with csv_path.open("r", encoding="utf-8", errors="replace") as f:
        header_line = f.readline().strip().lstrip("#").strip()
    columns = [c.strip() for c in header_line.split(",")]
    print(f"[load] CSV columns: {columns}")

    # Try to find the E_R column. Common naming conventions:
    er_candidates = [
        "e_recoil_keV", "E_R_keV", "er_keV", "nr_energy_keV",
        "recoil_energy_keV", "energy_keV", "E_keV", "ER",
        "nuclear_recoil_energy", "keV",
    ]
    er_col = None
    for cand in er_candidates:
        if cand in columns:
            er_col = cand
            break
    if er_col is None:
        # Last resort: any column with 'keV' or 'energy' or 'recoil' in name
        for c in columns:
            cl = c.lower()
            if "kev" in cl or "recoil" in cl or "energy" in cl:
                er_col = c
                break
    if er_col is None:
        raise ValueError(
            f"Could not find E_R column in {csv_path}. Columns: {columns}. "
            f"Please rename or specify manually."
        )
    print(f"[load] Using E_R column: {er_col}")

    data = np.genfromtxt(
        csv_path, delimiter=",", names=True,
        dtype=None, encoding="utf-8", comments="#",
    )
    er = np.asarray(data[er_col], dtype=float)
    return er


def count_in_window(er_keV: "np.ndarray", window_keV: tuple) -> dict:
    """Count events in a recoil-energy window."""
    lo, hi = window_keV
    mask = (er_keV >= lo) & (er_keV <= hi)
    n = int(mask.sum())
    return {
        "window_keV": list(window_keV),
        "n_events": n,
        "fraction_of_total": float(n / max(len(er_keV), 1)),
    }


def compare_to_prediction(counts: dict, prediction: dict) -> dict:
    """Compare observed counts to magnetic-moment prediction."""
    result = {"windows": {}}
    for label, window in [
        ("low_E_5_50", WINDOW_LOW_E),
        ("248_keV_200_300", WINDOW_248KEV),
        ("sideband_50_200", WINDOW_SIDEBAND),
        ("full_5_270", WINDOW_FULL),
    ]:
        c = counts[label]
        n_pred = prediction[f"N_pred_window_{window[0]:.0f}_{window[1]:.0f}_keV"]
        ratio = c["n_events"] / max(n_pred, 1e-9)
        if ratio < 0.3:
            verdict = "below_prediction (magnetic-m contradicted)"
        elif ratio < 3.0:
            verdict = "consistent_with_magnetic_m"
        else:
            verdict = "above_prediction (magnetic-m under-predicts)"
        result["windows"][label] = {
            **c,
            "n_predicted": n_pred,
            "ratio_obs_to_pred": ratio,
            "verdict": verdict,
        }
    return result


# ---------------------------------------------------------------------------
# Main: dry-run by default, live if env var set
# ---------------------------------------------------------------------------

def main():
    print("=" * 70)
    print("T90.23 Path 1 (DRY RUN) -- LZ 248 keV low-E_R window count")
    print("=" * 70)

    # Step 1: try download (no-op unless env var set)
    downloaded = try_download(EXPECTED_DATA_DIR)

    # Step 2: locate the CSV (either from auto-download or manual drop)
    event_file = find_event_file(EXPECTED_DATA_DIR)
    if event_file is None:
        print(f"[dry-run] No LZ per-event CSV found at {EXPECTED_DATA_DIR}.")
        print("  To run live:")
        print(f"    1. Download from one of: {LZ_DATA_URLS}")
        print(f"    2. Save as: {EXPECTED_DATA_DIR / EXPECTED_FILENAMES[0]}")
        print(f"    3. Re-run this script (with or without T90_V23_DOWNLOAD=1)")
        print("")
        print("[dry-run] EMITTING SHELL-ONLY OUTPUT (no data, no counts).")

        output = {
            "mode": "dry_run",
            "status": "awaiting_data",
            "expected_data_dir": str(EXPECTED_DATA_DIR),
            "candidate_urls": LZ_DATA_URLS,
            "expected_filenames": EXPECTED_FILENAMES,
            "magnetic_moment_prediction": MAG_MOMENT_PREDICTION,
            "what_would_be_counted": {
                "low_E_5_50_keV": {"window": list(WINDOW_LOW_E), "n_predicted": MAG_MOMENT_PREDICTION["N_pred_window_5_50_keV"]},
                "248_keV_200_300": {"window": list(WINDOW_248KEV), "n_predicted": MAG_MOMENT_PREDICTION["N_pred_window_200_300_keV"]},
                "sideband_50_200": {"window": list(WINDOW_SIDEBAND), "n_predicted": MAG_MOMENT_PREDICTION["N_pred_window_50_200_keV"]},
                "full_5_270_keV": {"window": list(WINDOW_FULL), "n_predicted": MAG_MOMENT_PREDICTION["N_pred_window_5_270_keV"]},
            },
            "verdict_rule": (
                "low-E/R ratio < 0.3 -> magnetic-m contradicted; "
                "ratio in [0.3, 3.0] -> consistent; "
                "ratio > 3.0 -> magnetic-m under-predicts."
            ),
            "next_step_when_live": (
                "Drop the per-event CSV into data/external_data/lz_2026/ "
                "and re-run; the script will compute the counts and write "
                "outputs/t90/t90_v23_lz_lowE_count.json"
            ),
        }
    else:
        # LIVE mode: data is present, count events
        print(f"[live] Loading {event_file}")
        er_keV = load_event_table(event_file)
        print(f"[live] Loaded {len(er_keV)} events")

        counts = {
            "low_E_5_50": count_in_window(er_keV, WINDOW_LOW_E),
            "248_keV_200_300": count_in_window(er_keV, WINDOW_248KEV),
            "sideband_50_200": count_in_window(er_keV, WINDOW_SIDEBAND),
            "full_5_270": count_in_window(er_keV, WINDOW_FULL),
        }
        for label, c in counts.items():
            print(f"  {label}: {c['n_events']} events in [{c['window_keV'][0]}, {c['window_keV'][1]}] keV")

        comparison = compare_to_prediction(counts, MAG_MOMENT_PREDICTION)
        output = {
            "mode": "live",
            "data_source": str(event_file),
            "n_events_total": len(er_keV),
            "magnetic_moment_prediction": MAG_MOMENT_PREDICTION,
            "windows": comparison["windows"],
            "headline_verdict": (
                "magnetic-m CONFIRMED" if comparison["windows"]["low_E_5_50"]["ratio_obs_to_pred"] > 0.3
                else "magnetic-m CONTRADICTED by low-E_R absence"
            ),
        }

    # Write output
    out_path = _PROJECT_ROOT / "outputs" / "t90" / "t90_v23_lz_lowE_count.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    print(f"[output] {out_path}")

    return output


if __name__ == "__main__":
    main()
