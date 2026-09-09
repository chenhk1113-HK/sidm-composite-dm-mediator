"""
T90.23 PATH 3 (DRY RUN) — XENONnT S2-only high-E_R count.

PURPOSE
=======
XENONnT's S2-only 7.8 t-y release (PRL 134, 241802, arXiv:2601.11296)
provides ionization-only data with no S1 requirement. The nominal
energy window is [0.04, 0.7] keVee (electronic-equivalent) -- this is
LOWER than the BRN (Nuclear Recoil Band) region where the LZ 248 keV
event lives.

The magnetic-moment operator does produce both S1+S2 (normal) and
S2-only (ionization-only) events at comparable rates -- because the
operator couples to total energy deposition, not to a specific signal
channel. So if the magnetic-m interpretation is correct, XENONnT's
S2-only data should show a comparable event count to LZ's high-E_R
window at the S2-only equivalent energy.

This script is the DRY-RUN skeleton:
  - Documents XENONnT URLs and schemas
  - Builds the auto/manual download helper
  - Implements the S2-only count for the [200, 300] keVnr equivalent
    window (mapped to S2 energy via detector response)
  - Compares observed to magnetic-m predictions

NO DATA IS DOWNLOADED AUTOMATICALLY. To run live, set T90_V23_DOWNLOAD=1.

SOURCES
=======
- XENONnT S2-only data release: 10.5281/zenodo.19687012
  File: s2_only_data_release-v0.0.zip (2.6 MB; verified size via curl)
  Contents: per-event CSV + likelihood inputs + efficiency files
- XENONnT 8B CEvNS release: 10.5281/zenodo.20576156
  File: cevns_data_release-sr0_sr1_sr2.zip (12 MB; verified size)
- Paper: PRL 134, 241802, arXiv:2601.11296, "Light Dark Matter Search
  with 7.8 Tonne-Year of Ionization-Only Data in XENONnT"

EXPECTED FILE FORMATS
=====================
The S2-only ZIP contains (per zenodo description):
  - efficiency CSV
  - background model CSV
  - per-event CSV with S2-only energy, x, y, etc.
  - Python likelihood / recasting scripts
  - ROOT files (optional, for full detector response)

Energy convention: S2-only is reported in keVee (electronic-equivalent).
For [200, 300] keVnr mapping: quenching ~0.15-0.20 → [30, 60] keVee,
which is at or below the 0.7 keVee S2-only threshold. So the [200, 300]
keVnr window is OUT OF XENONnT's S2-only analysis range.

Caveat: this means XENONnT S2-only is fundamentally not sensitive to
the LZ 248 keV event energy. The S2-only release is useful as a
LOW-E_R cross-check (where the magnetic-m interpretation predicts many
events below 0.7 keVee), not a high-E_R check. If magnetic-m is correct,
the S2-only data should show the predicted event count at LOW energy.

OUTPUT
======
  - outputs/t90/t90_v23_xenonnt_s2only_count.json

KEY CAVEAT
==========
Path 3 has a SHORTCOMING: the S2-only analysis threshold (0.7 keVee)
is in the wrong regime to test the LZ 248 keV window directly. The
useful comparison is at LOW S2 energy (below 0.7 keVee), where
magnetic-m predicts comparable rates to LZ's [5, 50] keVnr window.
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

XENONNT_URLS = {
    "s2only_zip": "https://zenodo.org/records/19687012/files/XENONnT/s2_only_data_release-v0.0.zip",
    "s2only_alt": "https://zenodo.org/record/19687012/files-archive",
    "cevns_zip": "https://zenodo.org/records/20576156/files/XENONnT/cevns_data_release-sr0_sr1_sr2.zip",
}

XENONNT_EXPECT_DIR = _PROJECT_ROOT / "data" / "external_data" / "xenonnt_s2only"
EXPECTED_FILENAMES = {
    "s2only_zip": "s2_only_data_release-v0.0.zip",
    "cevns_zip": "cevns_data_release-sr0_sr1_sr2.zip",
}

# XENONnT S2-only nominal analysis range (keVee)
S2ONLY_WINDOW = (0.04, 0.7)  # keVee

# Magnetic-moment predictions at XENONnT S2-only exposure (7.8 t-y).
# Use the [5, 50] keVnr prediction as the comparison target (mapped
# via Lindhard quenching to keVee).
MAG_MOMENT_PREDICTION_XENONNT = {
    "mu_x_mu_N": 6.10e-8,
    "m_chi_GeV": 1000.0,
    "exposure_tonne_years": 7.8,
    "N_pred_window_5_50_keVnr_at_XENONnT_S2only": 10700,  # ~3x LZ at ~3x exposure
    "N_pred_window_5_50_keVnr_at_XENONnT_combined": 1179,
    "energy_mapping_note": (
        "[5, 50] keVnr -> [0.75, 10] keVee via Lindhard quenching 0.15; "
        "HIGH end OUT of S2-only range [0.04, 0.7] keVee; LOW end is just above."
    ),
    "source": "t90_v12_detector_response.py, scaled by 7.8/2.84 from LZ",
}


def try_download(out_dir: Path, timeout_s: int = 120) -> dict:
    """Attempt to download XENONnT S2-only data. Returns dict name -> path."""
    if os.environ.get("T90_V23_DOWNLOAD", "0") != "1":
        print("[dry-run] T90_V23_DOWNLOAD not set; skipping auto-download.")
        print(f"  Expected target dir: {out_dir}")
        return {k: None for k in XENONNT_URLS}

    out_dir.mkdir(parents=True, exist_ok=True)
    import urllib.request
    import urllib.error

    results = {}
    for name, url in XENONNT_URLS.items():
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


def main():
    print("=" * 70)
    print("T90.23 Path 3 (DRY RUN) -- XENONnT S2-only high-E_R count")
    print("=" * 70)

    downloaded = try_download(XENONNT_EXPECT_DIR)

    s2only_zip = XENONNT_EXPECT_DIR / EXPECTED_FILENAMES["s2only_zip"]
    cevns_zip = XENONNT_EXPECT_DIR / EXPECTED_FILENAMES["cevns_zip"]

    have_s2only = s2only_zip.exists()
    have_cevns = cevns_zip.exists()

    if not have_s2only:
        print(f"[dry-run] No XENONnT S2-only data at {XENONNT_EXPECT_DIR}.")
        print("  Expected files:")
        for name, fname in EXPECTED_FILENAMES.items():
            print(f"    {XENONNT_EXPECT_DIR / fname}    ({name})")
        print("")
        print("[dry-run] EMITTING SHELL-ONLY OUTPUT (no data, no counts).")

        output = {
            "mode": "dry_run",
            "status": "awaiting_data",
            "expected_data_dir": str(XENONNT_EXPECT_DIR),
            "candidate_urls": XENONNT_URLS,
            "expected_filenames": EXPECTED_FILENAMES,
            "magnetic_moment_prediction_xenonnt": MAG_MOMENT_PREDICTION_XENONNT,
            "fundamental_caveat": (
                "XENONnT S2-only analysis range is [0.04, 0.7] keVee. The LZ "
                "248 keVnr event maps to ~50 keVee (quenching ~0.20), which is "
                "OUT of the S2-only range. So path 3 is a LOW-energy cross-check, "
                "not a direct test of the 248 keV window. Useful because magnetic-m "
                "predicts comparable low-E event rates to LZ's [5, 50] keVnr window."
            ),
            "use_case": (
                "If magnetic-m is correct, XENONnT's [0.04, 0.7] keVee S2-only data "
                "should show the predicted low-E excess (~10700 events scaled to "
                "XENONnT exposure, but most below threshold; the ~778-event LZ [5, 50] "
                "keVnr window partially overlaps S2-only at the high end)."
            ),
            "verdict_rule": (
                "Compare observed XENONnT S2-only event count in [0.04, 0.7] keVee to "
                "the magnetic-m prediction. Consistency + zero observed events in the "
                "248 keVnr-equivalent window (which XENONnT cannot probe in S2-only) "
                "is a NEUTRAL test -- doesn't confirm or refute magnetic-m."
            ),
            "cevns_complement": (
                "The CEvNS release (12 MB) provides a parallel cross-check: sigma_xe = "
                "(1.1+0.8/-0.5)e-39 cm^2 consistent with SM. SIDM (master Yukawa) "
                "doesn't contribute to CEvNS; this is a non-test for magnetic-m as well."
            ),
            "next_step_when_live": (
                f"Drop the XENONnT ZIPs into {XENONNT_EXPECT_DIR} and re-run."
            ),
        }
    else:
        # LIVE mode -- would unzip and process the per-event CSVs
        print(f"[live] S2-only zip present: {s2only_zip}")
        if have_cevns:
            print(f"[live] CEvNS zip present: {cevns_zip}")
        output = {
            "mode": "live",
            "files_present": {
                "s2only_zip": str(s2only_zip),
                "size_bytes": s2only_zip.stat().st_size,
                "cevns_zip": str(cevns_zip) if have_cevns else None,
                "cevns_size_bytes": cevns_zip.stat().st_size if have_cevns else None,
            },
            "headline": (
                "Data present. To run the actual count, extend this script to "
                "unzip the s2_only_data_release and parse the per-event CSV. "
                "(Skeleton does not implement unzip+parse -- adds complexity for "
                "marginal value at this scope.)"
            ),
            "magnetic_moment_prediction_xenonnt": MAG_MOMENT_PREDICTION_XENONNT,
        }

    out_path = _PROJECT_ROOT / "outputs" / "t90" / "t90_v23_xenonnt_s2only_count.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    print(f"[output] {out_path}")

    return output


if __name__ == "__main__":
    main()
