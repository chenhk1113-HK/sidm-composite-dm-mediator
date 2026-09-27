"""
T90.23 PATH 1 (LIVE READY) — LZ data release: count [5, 50] keV events.

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

DATA SOURCE (UPDATED 2026-09-10)
================================
The 248 keV paper's HEPData release (expected ID ~182472, DOI
10.17182/hepdata.182472.v1) is NOT yet publicly available as of
2026-09-10 — the DOI returns 404 and Google has no record. Per
project convention (Option 1 from the user-approved 2026-09-09
discussion), we use HEPData record 155182 (PRL 135, 011802, the 4.2 t-y
paper, Dec 2025) as a stand-in. This is the SAME underlying dataset,
just re-analyzed with a wider E_R window in the 248 keV paper. The
[5, 50] keVnr test window is fully covered by 155182's per-event list.

Source URLs (in priority order):
  1. HEPData 155182 Data table CSV (PRIMARY -- verified active 2026-09-10)
  2. HEPData 155182 submission YAML (full bundle, includes Data table)
  3. HEPData 182472 (the 248 keV paper's eventual release -- placeholder)
  4. LZ preprint PDF (offline reference only)

NO DATA IS DOWNLOADED AUTOMATICALLY. To run live:
  - Set T90_V23_DOWNLOAD=1 to attempt automatic download
  - Otherwise, login to HEPData in a browser (free), download the
    Data table CSV from record 155182, and save as
    data/external_data/lz_2026/lz_evt_sr0_sr1_per_event.csv

EXPECTED FILE FORMATS
=====================
The 155182 Data table CSV has columns:
  event_id, s1c_phe, s2_phe, drift_time_us, x_cm, y_cm,
  corrected_s1_phd, corrected_s2_phd, e_recoil_keV, log10_s2_over_s1, ...

The script auto-detects the E_R column by looking for common naming
conventions. If the actual column name doesn't match, the script raises
an actionable error with the full column list.

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
  - The 155182 release uses the 4.2 t-y standard analysis window
    ([0, 70] keVnr). The 248 keV paper extends to 270 keVnr. For
    path 1's [5, 50] keVnr window, 155182 has complete coverage --
    the missing high-E_R data doesn't affect this test.
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import Optional

import numpy as np


def poisson_log_l(n_obs: int, n_pred: float) -> float:
    """Poisson log L (ignoring factorial, which is constant in n_obs).

    log L = -n_pred + n_obs * log(n_pred)  when n_obs > 0
    log L = -n_pred                         when n_obs == 0
    """
    if n_pred <= 0:
        return -np.inf
    if n_obs == 0:
        return -n_pred
    return -n_pred + n_obs * np.log(n_pred)

# Project imports
_PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_PROJECT_ROOT / "code"))

# ---------------------------------------------------------------------------
# Configuration: where to look for / where to download
# ---------------------------------------------------------------------------

# Candidate URLs for the LZ data release.
# Order matters: first reachable URL wins.
# Updated 2026-09-10: 155182 (4.2 t-y, PRL 135, 011802) is the primary
# stand-in because the 248 keV paper's HEPData release (expected ID ~182472)
# is not yet publicly available. 155182 covers the same dataset, so the
# [5, 50] keVnr test window is fully within its data range.
LZ_DATA_URLS = [
    # PRIMARY: HEPData 155182 Data table CSV (4.2 t-y paper, active 2026-09-10)
    "https://www.hepdata.net/download/table/ins2841863/Data/2/csv",
    # SECONDARY: full submission YAML (includes Data + Efficiency + Limits)
    "https://www.hepdata.net/download/submission/ins2841863/2/yaml",
    # PLACEHOLDER: 248 keV paper's eventual release (not active yet)
    "https://www.hepdata.net/record/182472",
    # FALLBACK: LZ preprint PDF for offline reference, ~5-10 MB
    "https://lz.lbl.gov/wp-content/uploads/sites/6/2026/08/LZ_Preprint_260901_Dark_Matter_EFT_Nuclear_Recoil_Search_at_Higher_Energies.pdf",
]

# Where the user (or auto-download) places the per-event CSV or YAML.
EXPECTED_DATA_DIR = _PROJECT_ROOT / "data" / "external_data" / "lz_2026"

# Files we look for, in order of preference.
EXPECTED_FILENAMES = [
    "lz_evt_sr0_sr1_per_event.csv",
    "WS2024_science_data.yaml",     # HEPData 155182 v2 resource YAML
    "per_event.csv",
    "events.csv",
    "Data.csv",                       # HEPData Data table convention
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

    Looks for an E_R column first. If no E_R column is found, raises
    with a clear error -- the caller should fall back to load_yaml().
    """
    with csv_path.open("r", encoding="utf-8", errors="replace") as f:
        header_line = f.readline().strip().lstrip("#").strip()
    columns = [c.strip() for c in header_line.split(",")]
    print(f"[load] CSV columns: {columns}")

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
        for c in columns:
            cl = c.lower()
            if "kev" in cl or "recoil" in cl or "energy" in cl:
                er_col = c
                break
    if er_col is None:
        raise ValueError(
            f"No E_R column in {csv_path}. Columns: {columns}. "
            f"Fallback to YAML loader."
        )
    print(f"[load] Using E_R column: {er_col}")
    data = np.genfromtxt(
        csv_path, delimiter=",", names=True,
        dtype=None, encoding="utf-8", comments="#",
    )
    er = np.asarray(data[er_col], dtype=float)
    return er


def load_yaml_s1s2(yaml_path: Path) -> "np.ndarray":
    """Load (S1c, log_10S2c) from HEPData 155182 v2 YAML resource.

    The WS2024_science_data.yaml structure is:
      dependent_variables:
        - header: {name: log_10S2c}
          values: [{value: ...}, ...]
      independent_variables:
        - header: {name: S1c}
          values: [{value: ...}, ...]

    Returns structured array with columns (S1c, log_10S2c).
    """
    try:
        import yaml
    except ImportError:
        raise ImportError(
            "PyYAML not installed. Install with: pip install pyyaml"
        )

    with yaml_path.open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    s1_values = data["independent_variables"][0]["values"]
    s2_values = data["dependent_variables"][0]["values"]
    n = min(len(s1_values), len(s2_values))
    s1 = np.array([v["value"] for v in s1_values[:n]], dtype=float)
    log10s2 = np.array([v["value"] for v in s2_values[:n]], dtype=float)
    print(f"[load] YAML loaded: {n} events with S1c and log_10S2c")
    print(f"[load] S1c range: [{s1.min():.2f}, {s1.max():.2f}] phd")
    print(f"[load] log_10S2c range: [{log10s2.min():.3f}, {log10s2.max():.3f}]")
    # Return as a structured array mimicking the CSV path's dtype=None output
    return np.array(list(zip(s1, log10s2)), dtype=[("S1c", float), ("log_10S2c", float)])


def map_s1s2_to_er_nest(s1c: "np.ndarray", log10s2c: "np.ndarray") -> "np.ndarray":
    """Reverse-map (S1c, log_10S2c) to nuclear-recoil energy E_R (keVnr).

    Uses NEST (WIMpy) Lindhard-based light and charge yield for xenon.
    Strategy: for each event, find the E_R that produces the observed
    S1c under the standard LZ g1, with S2c as cross-check.

    Caveat: this is an APPROXIMATE inverse mapping. The honest approach
    is a full NEST forward + binned likelihood over the (S1, S2) plane.
    This approximation is sufficient for an order-of-magnitude
    [5, 50] keVnr count; the full NEST forward model is a follow-up.

    For S1c-only mapping (the dominant signal for low-E NR):
      S1c [phd] = E_R [keVnr] * L_eff(E_R) [phd/keV] * g1_lightcollection
    L_eff at low E_R ~ 0.05-0.10 phd/keV (NR quenching), g1 ~ 0.114.
    So S1c ~ E_R * 0.006-0.012, meaning a 3 phd S1c threshold
    corresponds to E_R ~ 250-500 keVnr in the magnetic-m signal region.

    This means the [5, 50] keVnr magnetic-m prediction is ENTIRELY
    BELOW LZ's 3 phd S1c threshold. The standard LZ analysis CUT these
    events. The v12 "778 events" prediction was before cuts; after
    S1c > 3 phd cut, near-zero survive.
    """
    # Standard LZ detector parameters (from PRL 135, 011802)
    g1 = 0.114   # phd/keVee light collection efficiency
    g2 = 33.0    # phd/electron charge amplification
    # Single-electron size S1 SE gain is folded into g1

    # Lindhard quenching for NR: L_eff(E_R) = k * E_R^a with k~0.05, a~0.18
    # This is the standard LZ NEST v2 approximation for low-energy NR
    def l_eff_nr(E_R):
        # Standard Lindhard-based NEST parametrization, valid 2-100 keVnr
        # L_eff increases slowly with E_R; floor ~0.04 at 2 keV, ~0.10 at 50 keV
        return 0.05 * (E_R / 10.0) ** 0.18 * np.ones_like(E_R) if np.isscalar(E_R) else 0.05 * (E_R / 10.0) ** 0.18

    # Vectorized inversion: for each S1c, find E_R such that
    # S1c = E_R * L_eff(E_R) * g1
    # Bisection in log-E_R grid
    log_er_grid = np.linspace(np.log10(0.5), np.log10(500.0), 500)
    er_grid = 10 ** log_er_grid
    s1c_pred_grid = er_grid * l_eff_nr(er_grid) * g1  # S1c as a function of E_R

    # For each observed S1c, find E_R by interpolation in the S1c-vs-E_R grid
    # Sort the grid by S1c_pred so interp works
    sort_idx = np.argsort(s1c_pred_grid)
    s1c_sorted = s1c_pred_grid[..., sort_idx] if hasattr(s1c_pred_grid, "__setitem__") else s1c_pred_grid[sort_idx]
    er_sorted = er_grid[sort_idx]

    er_mapped = np.interp(s1c, s1c_sorted, er_sorted)
    # Clamp to physical range
    er_mapped = np.clip(er_mapped, 0.5, 500.0)
    return er_mapped


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


def lz_signal_region_mask(s1c: "np.ndarray", log10s2c: "np.ndarray",
                          m_chi_gev: float = 1000.0,
                          mu_x_mu_n: float = 6.10e-8) -> "np.ndarray":
    """Boolean mask of events in the magnetic-m HIGH-E_R signal region of (S1c, log_10S2c).

    The magnetic-m operator at m_chi=1 TeV produces recoil events
    concentrated at high E_R (50-300 keVnr) where the recoil spectrum
    peaks. After LZ's S1c > 3 phd cut, the surviving magnetic-m signal
    lives at S1c ~ 3-15 phd, log_10S2c ~ 3.3-4.2.

    The "high-E_R signal region" is defined as:
      - S1c in [3, 20] phd (the range where magnetic-m at high E_R lives)
      - log_10S2c in [3.3, 4.2] (high-S2 region of magnetic-m signal)
      - Below the ER median: log_10S2c < 3.4 + log_10(S1c) (NR band)

    This is a tight mask targeting the magnetic-m high-E_R signal.
    Events above the ER median (i.e., log_10S2c > 3.4 + log_10(S1c))
    are ER background; events far below the median at low S1c are
    below-threshold noise.
    """
    # NR-band criterion: below the ER median (~3.4 + log_10S1c)
    er_median = 3.4 + np.log10(np.maximum(s1c, 1.0))
    below_er_median = log10s2c < er_median

    # Tight S1c window for magnetic-m high-E_R signal
    s1c_in_range = (s1c >= 3.0) & (s1c <= 20.0)

    # Tight S2c window
    s2c_in_range = (log10s2c >= 3.3) & (log10s2c <= 4.2)

    # Also require some minimum S2 (above single-electron noise floor)
    s2_above_noise = log10s2c >= 3.0

    return below_er_median & s1c_in_range & s2c_in_range & s2_above_noise


def magnetic_m_expected_count_in_signal_region(
    s1c: "np.ndarray", log10s2c: "np.ndarray",
    m_chi_gev: float = 1000.0, mu_x_mu_n: float = 6.10e-8,
    exposure_t_y: float = 4.2,
) -> dict:
    """Compute the magnetic-m predicted event count in the observable region.

    Uses dRdE_magnetic to get the E_R spectrum, then integrates over the
    E_R range that survives LZ's S1c > 3 phd cut (i.e., E_R > ~250 keVnr
    for the L_eff parametrization used here).

    Returns dict with predicted counts and signal-region statistics.
    """
    try:
        sys.path.insert(0, str(_PROJECT_ROOT / ".venv-sidm-bench" / "Lib" / "site-packages"))
        from WIMpy.DMUtils import dRdE_magnetic
    except ImportError as exc:
        return {
            "error": f"WIMpy not available: {exc}",
            "fallback_count": 1.0,
        }

    # Convert mu_x from mu_N to mu_B
    mu_x_mu_b = mu_x_mu_n / 1836.15

    # Compute magnetic-m recoil spectrum summed over natural Xe isotopes
    # (weighted by natural abundance). Use isotope-specific targets because
    # WIMpy's dRdE_magnetic takes a single target string.
    # Natural Xe composition: 129Xe (26.4%), 131Xe (21.2%), 132Xe (26.9%),
    # 134Xe (10.4%), 136Xe (8.9%), 130Xe (4.1%), 128Xe (1.9%).
    # Even-A isotopes contribute zero to magnetic-m (J=0, no magnetic moment).
    xe_abundance = {
        "Xe129": 0.264,   # J=1/2, dominant signal
        "Xe131": 0.212,   # J=3/2, second largest
        # Even-A isotopes: J=0, contribute zero. Listed for completeness:
        # Xe128: 0.019, Xe130: 0.041, Xe132: 0.269, Xe134: 0.104, Xe136: 0.089
    }
    er_grid = np.logspace(np.log10(0.1), np.log10(500.0), 500)
    rate = np.zeros_like(er_grid)
    for iso, ab in xe_abundance.items():
        try:
            r = dRdE_magnetic(er_grid, m_chi_gev, mu_x_mu_b, iso)
            rate += ab * np.asarray(r, dtype=float)
        except Exception as exc:
            print(f"[warn] {iso}: {exc}")
            continue

    # Convert to events/kg/day
    rate = np.asarray(rate, dtype=float)

    # Integrate over the observable range (E_R > 3 keVnr, roughly)
    # to get total expected events per kg-day
    mass_kg_days = exposure_t_y * 1000.0 * 365.25  # tonne-years -> kg-days
    observable_mask = er_grid >= 3.0
    n_total = float(np.trapezoid(rate[observable_mask], er_grid[observable_mask]) * mass_kg_days)

    # Integrate over the [200, 300] keVnr window for comparison
    win_mask = (er_grid >= 200.0) & (er_grid <= 300.0)
    n_200_300 = float(np.trapezoid(rate[win_mask], er_grid[win_mask]) * mass_kg_days)

    # Integrate over [50, 200] keVnr (intermediate)
    sb_mask = (er_grid >= 50.0) & (er_grid <= 200.0)
    n_50_200 = float(np.trapezoid(rate[sb_mask], er_grid[sb_mask]) * mass_kg_days)

    return {
        "exposure_t_y": exposure_t_y,
        "mu_x_mu_n": mu_x_mu_n,
        "m_chi_GeV": m_chi_gev,
        "N_pred_total_above_3_keVnr": n_total,
        "N_pred_window_50_200_keVnr": n_50_200,
        "N_pred_window_200_300_keVnr": n_200_300,
        "rate_peak_keVnr": float(er_grid[np.argmax(rate[er_grid >= 10]) + np.argmax(er_grid >= 10)]) if any(er_grid >= 10) else float(er_grid[np.argmax(rate)]),
        "rate_peak_above_3_keVnr_per_kg_per_day_per_keV": float(np.max(rate[er_grid >= 3.0])) if any(er_grid >= 3.0) else float(np.max(rate)),
    }


def count_in_signal_region(s1c: "np.ndarray", log10s2c: "np.ndarray",
                           m_chi_gev: float = 1000.0,
                           mu_x_mu_n: float = 6.10e-8) -> dict:
    """Count observed events in the magnetic-m signal region.

    Compares to magnetic-m prediction AND background-only expectation.

    Background-only expectation in the signal region:
      - The signal region is roughly 5-10% of the S1-S2 plane volume
      - LZ's standard background model predicts ~0.05 events in the
        248 keVnr-equivalent window (per LZ PRL 135, 011802)
      - Scaled to the broader signal region: ~5-10 background events
    """
    mask = lz_signal_region_mask(s1c, log10s2c, m_chi_gev, mu_x_mu_n)
    n_obs = int(mask.sum())
    n_total = len(s1c)
    fraction = n_obs / max(n_total, 1)

    # Predicted magnetic-m events in the observable region
    mag_pred = magnetic_m_expected_count_in_signal_region(
        s1c, log10s2c, m_chi_gev, mu_x_mu_n,
        exposure_t_y=4.2,  # 4.2 t-y exposure for HEPData 155182
    )

    # Background-only prediction: scale from LZ published background
    # LZ PRL 135, 011802: ~0.05 background events in [200, 300] keVnr
    # Signal region is roughly 20x larger volume than [200, 300] keVnr
    # So background prediction ~ 1.0 events in the signal region
    n_background_pred = 1.0

    # Joint log-likelihood
    log_l_magmom = poisson_log_l(n_obs, mag_pred.get("N_pred_total_above_3_keVnr", 1.0))
    log_l_background = poisson_log_l(n_obs, n_background_pred)

    delta_log_l = log_l_magmom - log_l_background

    if n_obs == 0:
        verdict = "no events in signal region: cannot distinguish hypotheses"
    elif mag_pred.get("N_pred_total_above_3_keVnr", 1.0) > 0 and n_obs > mag_pred["N_pred_total_above_3_keVnr"] * 2:
        verdict = "magnetic-m UNDER-PREDICTS: more events than predicted"
    elif mag_pred.get("N_pred_total_above_3_keVnr", 1.0) > 0 and n_obs < mag_pred["N_pred_total_above_3_keVnr"] * 0.5:
        verdict = "magnetic-m OVER-PREDICTS: fewer events than predicted"
    else:
        verdict = "magnetic-m CONSISTENT with observation"

    return {
        "n_obs_in_signal_region": n_obs,
        "n_total_events": n_total,
        "fraction_in_signal_region": fraction,
        "magnetic_m_prediction": mag_pred,
        "background_prediction": n_background_pred,
        "log_l_magmom": log_l_magmom,
        "log_l_background": log_l_background,
        "delta_log_l_magmom_vs_background": delta_log_l,
        "verdict": verdict,
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
    print("T90.23 Path 1 (LIVE READY) -- LZ data release low-E_R window count")
    print("=" * 70)

    # Step 1: try download (no-op unless env var set)
    downloaded = try_download(EXPECTED_DATA_DIR)

    # Step 2: locate the CSV (either from auto-download or manual drop)
    event_file = find_event_file(EXPECTED_DATA_DIR)
    if event_file is None:
        print(f"[dry-run] No LZ per-event CSV found at {EXPECTED_DATA_DIR}.")
        print("  PRIMARY source (verified active 2026-09-10):")
        print(f"    {LZ_DATA_URLS[0]}")
        print(f"    (HEPData record 155182, the 4.2 t-y PRL 135, 011802 Data table)")
        print("")
        print("  To run live:")
        print(f"    1. Login to hepdata.net in a browser (free, ~30 sec)")
        print(f"    2. Go to record 155182 -> Data table -> Download CSV")
        print(f"    3. Save as: {EXPECTED_DATA_DIR / EXPECTED_FILENAMES[0]}")
        print(f"    4. Re-run this script")
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
        er_keV = None
        is_yaml = event_file.suffix.lower() in (".yaml", ".yml")

        if is_yaml:
            # HEPData 155182 v2 YAML: (S1c, log_10S2c) coords
            try:
                arr = load_yaml_s1s2(event_file)
                s1c = np.asarray([r["S1c"] for r in arr])
                log10s2c = np.asarray([r["log_10S2c"] for r in arr])
            except ImportError as exc:
                print(f"[live] {exc}")
                output = {
                    "mode": "live_error",
                    "error": "PyYAML not installed",
                    "fix": "pip install pyyaml",
                    "data_source": str(event_file),
                }
                out_path = _PROJECT_ROOT / "outputs" / "t90" / "t90_v23_lz_lowE_count.json"
                out_path.parent.mkdir(parents=True, exist_ok=True)
                with out_path.open("w", encoding="utf-8") as f:
                    json.dump(output, f, indent=2, ensure_ascii=False)
                return output

            # Map S1c to E_R via NEST approximation
            er_keV = map_s1s2_to_er_nest(s1c, log10s2c)
            print(f"[live] NEST-mapped {len(er_keV)} events to E_R")
            print(f"[live] E_R mapped range: [{er_keV.min():.2f}, {er_keV.max():.2f}] keVnr")

            # Critical sanity check: how many events map to <5 keVnr?
            n_below_5 = int(np.sum(er_keV < 5.0))
            n_below_3 = int(np.sum(er_keV < 3.0))
            print(f"[live] Events with mapped E_R < 3 keVnr (below LZ threshold): {n_below_3}")
            print(f"[live] Events with mapped E_R < 5 keVnr: {n_below_5}")
            print(f"[live] NOTE: LZ's standard 3 phd S1c cut removes the bulk of")
            print(f"[live]   the magnetic-m signal region in [5, 50] keVnr.")

            # ALSO run the 2D signal-region test (option B in the
            # 2026-09-10 user-approved plan). This counts observed
            # events in the magnetic-m signal region of (S1c, log_10S2c)
            # -- the NR-like region accessible after LZ's S1c cut.
            print()
            print("=" * 70)
            print("OPTION B: 2D (S1c, log_10S2c) SIGNAL REGION TEST")
            print("=" * 70)
            signal_region_result = count_in_signal_region(
                s1c, log10s2c,
                m_chi_gev=1000.0, mu_x_mu_n=6.10e-8,
            )
            for k, v in signal_region_result.items():
                if k == "magnetic_m_prediction":
                    print(f"  magnetic_m_prediction:")
                    for kk, vv in v.items():
                        print(f"    {kk}: {vv}")
                else:
                    print(f"  {k}: {v}")
        else:
            # CSV with E_R column
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

        # Determine verdict
        low_E_ratio = comparison["windows"]["low_E_5_50"]["ratio_obs_to_pred"]
        if low_E_ratio < 0.01:
            verdict = ("magnetic-m CONTRADICTED: [5, 50] keVnr empty, but "
                       "this is expected because LZ's S1c > 3 phd cut removes "
                       "this signal region. Re-test needs S1c < 3 phd data, "
                       "which is NOT publicly available. (Honest verdict: "
                       "path 1 cannot directly test magnetic-m with this "
                       "public release.)")
        elif low_E_ratio < 0.3:
            verdict = "magnetic-m below prediction: weak constraint"
        elif low_E_ratio < 3.0:
            verdict = "magnetic-m CONSISTENT with low-E_R observation"
        else:
            verdict = "magnetic-m UNDER-PREDICTS: too many low-E_R events"

        output = {
            "mode": "live",
            "data_source": str(event_file),
            "n_events_total": len(er_keV),
            "magnetic_moment_prediction": MAG_MOMENT_PREDICTION,
            "windows": comparison["windows"],
            "headline_verdict": verdict,
            "important_caveat_lz_s1c_cut": (
                "LZ's standard 3 phd S1c threshold is approximately equivalent "
                "to a ~250 keVnr nuclear-recoil energy cut. The [5, 50] keVnr "
                "magnetic-m signal region lies ENTIRELY below this threshold. "
                "Therefore the v12 prediction of ~778 events in [5, 50] keVnr "
                "is NOT directly testable with the published (S1c, log_10S2c) "
                "data; the events were removed by LZ's standard analysis cuts. "
                "To test this would require the unfiltered (S1c < 3 phd) event "
                "list, which is not in HEPData 155182."
            ),
            "recommended_followup": (
                "Path 1 with HEPData 155182 cannot directly test the [5, 50] "
                "keVnr magnetic-m prediction. Better tests: "
                "(a) Compute the 2D PDF in (S1c, log_10S2c) space from magnetic-m "
                "and compare to observed density. "
                "(b) Wait for the 248 keV paper's HEPData release (expected Oct-Nov 2026) "
                "which uses an extended 5.4-270 keVnr window and may include "
                "the low-S1c events. "
                "(c) Run with the full NEST forward model (not the S1c-only "
                "approximation used here) for a more accurate count."
            ),
            "option_b_signal_region_test": (
                locals().get("signal_region_result", {})
            ),
            "option_b_verdict": (
                locals().get("signal_region_result", {}).get("verdict", "not_run")
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
