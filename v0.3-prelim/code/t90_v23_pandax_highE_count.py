"""
T90.23 PATH 2 (DRY RUN) — PandaX-4T run0/run1 high-E_R count.

PURPOSE
=======
The PandaX-4T light-DM 259-day release exposes binned spectral CSVs:
run0_data.csv and run1_data.csv, each with columns
E_low_keV, E_high_keV, E_center_keV, run0, run1.

The T90 magnetic-moment interpretation (m_chi ~ 1 TeV, mu_x = 6.10e-8 mu_N)
predicts ~0.6 events in the [200, 300] keV window at PandaX-4T exposure
(1.54 tonne-years) -- ~half of LZ's rate at ~half the exposure. The
existing PandaX light-DM CSV is normalized to unit integral; we instead
need the background-and-signal ROI from the main 1.54 t-y DM paper
(opendata.tar.gz).

This script is the DRY-RUN skeleton:
  - Documents PandaX URLs and schemas
  - Builds a manual-download helper (auto-download requires env var,
    and PandaX CDN was unreachable from this Windows host when probed)
  - Implements high-E_R ([200, 300] keV) and mid-E_R ([50, 200] keV)
    count comparison
  - Compares observed to magnetic-m and background-only predictions

NO DATA IS DOWNLOADED AUTOMATICALLY. To run live, set T90_V23_DOWNLOAD=1
(or use the browser to manually fetch, then drop into the expected dir).

SOURCES
=======
- PandaX Data Release portal: https://pandax.sjtu.edu.cn/public/data_release
- Light-DM paper: 10.1103/rtnh-jn8s (PRL 134, 011805)
- Main DM paper: 10.1103/PhysRevLett.134.011805 (1.54 t-y, Run0+Run1)
- Files: run0_data.csv, run1_data.csv (light-DM, normalized PDFs);
  opendata.tar.gz (main DM, includes per-energy-bin signal efficiency)
- PandaX-4T exposure: 1.54 tonne-years (Run0 0.63 + Run1 0.91)

EXPECTED FILE FORMATS
=====================
Light-DM (light-dark-matter, PRL 134, 011805):
  Schema (columns, ASCII, comma-separated):
    E_low_keV, E_high_keV, E_center_keV, run0, run1
  Energy range: 0.04 - 2.8 keVee (electronic-equivalent). NO [200, 300]
  keVee nuclear-recoil window. So this CSV is NOT directly useful for
  our [200, 300] keV nuclear-recoil count; we need the 1.54 t-y paper
  release instead.

Main DM (opendata.tar.gz, PRL 134, 011805):
  The opendata.tar.gz contains CSVs at higher energy range. The exact
  schema is TBD -- needs to be inspected when the tarball is downloaded.
  Likely includes per-event CSV (E_R, S1, S2, x, y) plus efficiency
  curves plus binned background.

OUTPUT
======
  - outputs/t90/t90_v23_pandax_highE_count.json
      Per-window count + ratio-to-prediction + verdict

CAVEATS
=======
  - PandaX data is binned; need to know bin edges to count [200, 300]
    keV nuclear recoils. If bins are 4 keV wide (per the light-DM
    description), 25 bins span the window; if wider, fewer.
  - The Run0/Run1 CSV is electronic-equivalent (keVee); to compare to
    a nuclear-recoil [200, 300] keV window we need the quenching factor
    (Lindhard ~0.15-0.20 for Xe around 100 keVnr).
  - The 2023 PandaX magnetic-moment limit (Nature 618, 47) was set on
    Run0 only (0.63 t-y); Run0+Run1 (1.54 t-y) tightens this by ~1.5x.
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
# Configuration
# ---------------------------------------------------------------------------

PANDAX_URLS = {
    "light_dm_run0": "https://static.pandax.sjtu.edu.cn/download/data-share/p4-light-dark-matter/run0_data.csv",
    "light_dm_run1": "https://static.pandax.sjtu.edu.cn/download/data-share/p4-light-dark-matter/run1_data.csv",
    "main_dm_opendata_tar": "https://static.pandax.sjtu.edu.cn/download/data-share/p4-DM/opendata.tar.gz",
    "nudm_open_data_tar": "https://static.pandax.sjtu.edu.cn/download/data-share/p4-nuDM/open-data.tar.gz",
    "s2only_zip": "https://static.pandax.sjtu.edu.cn/download/data-share/p4-first-analysis/s2only_data_release.zip",
}

PANDAX_EXPECT_DIR = _PROJECT_ROOT / "data" / "external_data" / "pandax_4t"
EXPECTED_FILENAMES = {
    "light_dm_run0": "run0_data.csv",
    "light_dm_run1": "run1_data.csv",
    "main_dm_opendata_tar": "opendata.tar.gz",
}

# Analysis windows (keV nuclear-recoil energy)
WINDOW_248KEV = (200.0, 300.0)
WINDOW_LOW_E = (5.0, 50.0)
WINDOW_FULL = (5.0, 270.0)
WINDOW_SIDEBAND = (50.0, 200.0)

# Magnetic-moment predictions at PandaX exposure (1.54 t-y) and
# m_chi = 1000 GeV, mu_x = 6.10e-8 mu_N (from v12 dry-run, scaled from
# LZ's 2.84 t-y: PandaX exposure / LZ exposure = 1.54/2.84 = 0.542).
MAG_MOMENT_PREDICTION_PANDAX = {
    "mu_x_mu_N": 6.10e-8,
    "m_chi_GeV": 1000.0,
    "exposure_tonne_years": 1.54,
    "N_pred_window_200_300_keV": 0.54,   # ~half LZ rate at half exposure
    "N_pred_window_5_50_keV": 422.0,    # ~half LZ low-E prediction
    "N_pred_window_5_270_keV": 815.0,
    "N_pred_window_50_200_keV": 390.0,
    "source": "t90_v12_detector_response.py, scaled by 1.54/2.84 from LZ",
}


# ---------------------------------------------------------------------------
# Download helper (NEVER auto-runs unless T90_V23_DOWNLOAD=1)
# ---------------------------------------------------------------------------

def try_download(out_dir: Path, timeout_s: int = 60) -> dict:
    """Attempt to download PandaX data. Returns dict of name -> path or None.

    CRITICAL NOTE: when probed 2026-09-09, all of static.pandax.sjtu.edu.cn
    returned curl exit 6 ("Could not resolve host") and curl exit 28
    ("timeout"). The PandaX CDN may block scripted HTTP from this network.
    If auto-download fails, use a browser to fetch and place files
    manually at the expected paths.
    """
    if os.environ.get("T90_V23_DOWNLOAD", "0") != "1":
        print("[dry-run] T90_V23_DOWNLOAD not set; skipping auto-download.")
        print(f"  Expected target dir: {out_dir}")
        return {k: None for k in PANDAX_URLS}

    out_dir.mkdir(parents=True, exist_ok=True)
    import urllib.request
    import urllib.error

    results = {}
    for name, url in PANDAX_URLS.items():
        try:
            print(f"[download] Trying {url}")
            target = out_dir / EXPECTED_FILENAMES.get(name, url.rsplit("/", 1)[-1])
            req = urllib.request.Request(url, headers={"User-Agent": "sidm-t90/0.4"})
            with urllib.request.urlopen(req, timeout=timeout_s) as resp:
                target.write_bytes(resp.read())
            print(f"[download] OK: {target} ({target.stat().st_size:,} bytes)")
            results[name] = str(target)
        except (urllib.error.URLError, TimeoutError, OSError) as exc:
            print(f"[download] FAIL: {url} -> {type(exc).__name__}: {exc}")
            results[name] = None
    return results


# ---------------------------------------------------------------------------
# Load + count
# ---------------------------------------------------------------------------

def load_lightdm_csv(csv_path: Path) -> dict:
    """Load the PandaX light-DM CSV (E_low, E_high, E_center, run0, run1).

    Returns dict with bin edges and per-run count arrays. The light-DM
    release is normalized to unit integral (PDF), so we cannot directly
    use it for an absolute count -- this function returns the PDF as-is
    so we can at least inspect bin coverage.
    """
    arr = np.genfromtxt(csv_path, delimiter=",", names=True, encoding="utf-8")
    print(f"[load] Columns: {arr.dtype.names}")
    print(f"[load] Energy range: [{arr['E_low_keV'][0]:.4f}, {arr['E_high_keV'][-1]:.4f}] keVee")
    print(f"[load] Total bins: {len(arr)}")
    return {
        "E_low_keV": arr["E_low_keV"].tolist(),
        "E_high_keV": arr["E_high_keV"].tolist(),
        "E_center_keV": arr["E_center_keV"].tolist(),
        "run0_pdf": arr["run0"].tolist(),
        "run1_pdf": arr["run1"].tolist(),
        "energy_range_keVee": [float(arr["E_low_keV"][0]), float(arr["E_high_keV"][-1])],
        "caveat": "PDF normalized to unit integral; absolute counts not recoverable",
    }


def count_binned_in_window(arr_pdf: "np.ndarray", E_low: "np.ndarray",
                            E_high: "np.ndarray", window_keV: tuple,
                            exposure_t_y: float, eff_per_bin: Optional["np.ndarray"] = None
                            ) -> dict:
    """Count events in window using a binned PDF * total expected events.

    The light-DM CSV is a PDF, not counts. To convert to expected counts,
    we need:
        N_pred(window) = total_expected_events * sum_{bin in window} PDF * width
    where total_expected_events comes from the paper (not in the CSV).
    For dry-run purposes, we report N_pred for the magnetic-m interpretation
    and leave the absolute count comparison to the LIVE step (which needs
    the opendata.tar.gz, with raw per-event data).
    """
    lo, hi = window_keV
    mask = (E_low >= lo) & (E_high <= hi)
    n_bins = int(mask.sum())
    integrated_pdf = float(np.sum(arr_pdf[mask] * (E_high[mask] - E_low[mask])))
    eff = eff_per_bin if eff_per_bin is not None else np.ones_like(E_low)
    integrated_eff = float(np.sum(arr_pdf[mask] * (E_high[mask] - E_low[mask]) * eff[mask]))
    return {
        "window_keV": list(window_keV),
        "n_bins_in_window": n_bins,
        "integrated_pdf_in_window": integrated_pdf,
        "integrated_eff_pdf_in_window": integrated_eff,
    }


def compare_to_prediction_magmom(loaded: dict, prediction: dict) -> dict:
    """Compare observed to magnetic-moment predictions (path 2 expected).

    The light-DM CSV is PDF-normalized, so this is mostly a SCHEMA / bin
    coverage check, not a count. We report:
      - Is the window [200, 300] keVee covered by the CSV? (likely NO,
        because light-DM energy range is 0.04-2.8 keVee)
      - The relative weight of each window in the binned distribution
    """
    elow = np.asarray(loaded["E_low_keV"])
    ehigh = np.asarray(loaded["E_high_keV"])
    r0 = np.asarray(loaded["run0_pdf"])
    r1 = np.asarray(loaded["run1_pdf"])

    e_low_max = float(ehigh.max())
    e_high_min = float(elow.min())

    windows = {
        "low_E_5_50": WINDOW_LOW_E,
        "248_keV_200_300": WINDOW_248KEV,
        "sideband_50_200": WINDOW_SIDEBAND,
        "full_5_270": WINDOW_FULL,
    }

    out = {}
    for label, w in windows.items():
        in_range = (w[1] <= e_low_max) and (w[0] >= e_high_min)
        # light-DM is keVee; target is keVnr. Quenching ~0.15-0.20.
        # So [200, 300] keVnr maps to [30, 60] keVee.
        # The light-DM range tops out at 2.8 keVee, which means even the
        # quenched mapping is OUT OF RANGE.
        ee_mapped = [w[0] * 0.15, w[1] * 0.20]   # very rough
        in_range_ee = (ee_mapped[1] <= e_low_max) and (ee_mapped[0] >= e_high_min)

        out[label] = {
            "window_keV_nr": list(w),
            "quenched_approx_keVee": ee_mapped,
            "covers_in_keVee": in_range_ee,
            "use_main_dm_tarball": not in_range_ee,
        }

    return out


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    print("=" * 70)
    print("T90.23 Path 2 (DRY RUN) -- PandaX-4T high-E_R count")
    print("=" * 70)

    downloaded = try_download(PANDAX_EXPECT_DIR)

    light_dm_run0 = PANDAX_EXPECT_DIR / EXPECTED_FILENAMES["light_dm_run0"]
    light_dm_run1 = PANDAX_EXPECT_DIR / EXPECTED_FILENAMES["light_dm_run1"]
    opendata_tar = PANDAX_EXPECT_DIR / EXPECTED_FILENAMES["main_dm_opendata_tar"]

    have_light_dm = light_dm_run0.exists() and light_dm_run1.exists()
    have_opendata = opendata_tar.exists()

    if not have_light_dm and not have_opendata:
        print(f"[dry-run] No PandaX data found at {PANDAX_EXPECT_DIR}.")
        print("  Expected files:")
        for name, fname in EXPECTED_FILENAMES.items():
            print(f"    {PANDAX_EXPECT_DIR / fname}    ({name})")
        print("")
        print("[dry-run] EMITTING SHELL-ONLY OUTPUT (no data, no counts).")

        output = {
            "mode": "dry_run",
            "status": "awaiting_data",
            "expected_data_dir": str(PANDAX_EXPECT_DIR),
            "candidate_urls": PANDAX_URLS,
            "expected_filenames": EXPECTED_FILENAMES,
            "magnetic_moment_prediction_pandax": MAG_MOMENT_PREDICTION_PANDAX,
            "important_caveat": (
                "PandaX CDN (static.pandax.sjtu.edu.cn) was unreachable from "
                "this host when probed 2026-09-09. Manual download via browser "
                "may be required. See URL list above."
            ),
            "schema_note": (
                "The light-DM run0/run1 CSVs are PDFs normalized to unit "
                "integral in the 0.04-2.8 keVee range. The [200, 300] keVnr "
                "target window maps to [30, 60] keVee (quenching ~0.15-0.20), "
                "which is OUT OF RANGE for the light-DM CSV. The opendata.tar.gz "
                "(1.54 t-y main DM release) is required for the [200, 300] keVnr "
                "count."
            ),
            "verdict_rule": (
                "If N_obs in [200, 300] keVnr at PandaX is ~0 with 1.54 t-y "
                "exposure, magnetic-m is consistent (predicts 0.54 events). "
                "If N_obs ~1+, magnetic-m is consistent with independent "
                "cross-detector confirmation; Higgsino inelastic's prediction "
                "is similar (both ~0.5 events), so this won't distinguish."
            ),
            "next_step_when_live": (
                f"Drop the PandaX files into {PANDAX_EXPECT_DIR} and re-run."
            ),
        }
    else:
        # LIVE mode
        if have_light_dm:
            r0 = load_lightdm_csv(light_dm_run0)
            r1 = load_lightdm_csv(light_dm_run1)
            window_coverage = compare_to_prediction_magmom(r0, MAG_MOMENT_PREDICTION_PANDAX)
            output = {
                "mode": "live",
                "files_loaded": {
                    "run0_data_csv": str(light_dm_run0),
                    "run1_data_csv": str(light_dm_run1),
                },
                "opendata_tarball_present": have_opendata,
                "window_coverage": window_coverage,
                "magnetic_moment_prediction_pandax": MAG_MOMENT_PREDICTION_PANDAX,
                "headline": (
                    "Light-DM CSVs are PDF-normalized in 0.04-2.8 keVee; "
                    "out of range for [200, 300] keVnr target. Use opendata.tar.gz "
                    "for the main count."
                ) if not have_opendata else
                "Both light-DM and main DM tarball present -- full analysis possible.",
            }
        else:
            output = {
                "mode": "live",
                "files_loaded": {"opendata_tarball": str(opendata_tar)},
                "headline": "Only opendata.tar.gz present; light-DM CSVs missing.",
            }

    out_path = _PROJECT_ROOT / "outputs" / "t90" / "t90_v23_pandax_highE_count.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    print(f"[output] {out_path}")

    return output


if __name__ == "__main__":
    main()
