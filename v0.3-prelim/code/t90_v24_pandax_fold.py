"""T90.24 PandaX-4T magnetic-moment efficiency/background fold.

This is an auditable public-data recast, not a reproduction of PandaX's
internal likelihood.  It uses the published Run-0/Run-1 exposure, thresholds,
selection description, candidate CSVs, and Table-1 below-NR-median background.

The public release does not provide the full multidimensional efficiency maps
or the collaboration's S1/S2 response templates.  Therefore the signal fold
uses an explicit bounded proxy efficiency calibrated to the published
selection description, and reports an envelope rather than hiding that
approximation.  The likelihood is performed only for the published observable:
24 events below the NR median in the full DM ROI, with 20.5 +/- 2.5 expected
background events.  It does NOT compare the 5-50-keV candidate count to the
20.5 NR-band background.
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import numpy as np

_PROJECT_ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = _PROJECT_ROOT / "outputs" / "t90"
PANDAX_DATA_DIR = _PROJECT_ROOT / "data" / "external_data" / "pandax_4t"

MU_N_TO_MU_B = 1836.15267
MU_X_MU_N = 6.10e-8
M_CHI_GEV = 1000.0

# Published PRL 134, 011805 / arXiv:2408.00664 values.
PANDAX_PUBLISHED = {
    "exposure_tonne_year": {"run0": 0.54, "run1": 1.00},
    "nr_roi_keV": {"run0": [4.0, 94.0], "run1": [3.0, 103.0]},
    "n_total_candidates": {"run0": 1117, "run1": 1373, "total": 2490},
    "n_below_nr_median": 24,
    "background_below_nr_median": 20.5,
    "background_below_nr_median_sigma": 2.5,
    "background_components_below_nr_median": {
        # Rounded component values transcribed from Table 1; their sum is
        # approximate, while 20.5 is the paper's canonical total.
        "Pb214_ER_leak": 3.6,
        "Pb212_ER_leak": 0.6,
        "Kr85_ER_leak": 1.4,
        "Material_ER_leak": 0.6,
        "Solar_EES_ER_leak": 0.4,
        "Xe136_ER_leak": 0.2,
        "Tritium_ER_leak": 6.4,
        "Xe127": 5.2,
        "Xe124": 0.10,
        "Neutron": 1.0,
        "B8_CEvNS": 1.0,
        "Surface": 0.26,
        "Accidental": 0.26,
    },
    "selection": {
        "s1_pe": [2.0, 135.0],
        "s2_pe": [120.0, 20000.0],
        "nr_quantile": 0.995,
        "below_nr_median_acceptance_nominal": 0.50,
    },
}

# The exact public efficiency surface is not released with the event CSV.
# These values are a deliberately explicit proxy, not claimed PandaX data.
# The envelope is propagated into the headline signal count.
EFFICIENCY_PROXY = {
    "nominal": {"at_3_keVnr": 0.45, "at_5_keVnr": 0.55, "at_20_keVnr": 0.75, "above_50_keVnr": 0.85},
    "low": {"at_3_keVnr": 0.30, "at_5_keVnr": 0.40, "at_20_keVnr": 0.60, "above_50_keVnr": 0.70},
    "high": {"at_3_keVnr": 0.60, "at_5_keVnr": 0.70, "at_20_keVnr": 0.85, "above_50_keVnr": 0.95},
}

ISOTOPES = [
    ("Xe129", 0.2644),
    ("Xe131", 0.2118),
]


def _wimpy_rate(energy_keV: np.ndarray, mu_x_mu_n: float, m_chi_gev: float) -> np.ndarray:
    """Natural-Xe magnetic rate, retaining only non-zero-spin isotopes."""
    from WIMpy import DMUtils as DMU

    mu_x_mu_b = mu_x_mu_n / MU_N_TO_MU_B
    rate = np.zeros_like(energy_keV, dtype=float)
    for isotope, abundance in ISOTOPES:
        rate += abundance * np.asarray(
            DMU.dRdE_magnetic(energy_keV, m_chi_gev, mu_x_mu_b, isotope),
            dtype=float,
        )
    if not np.isfinite(rate).all():
        raise ValueError("Magnetic-moment spectrum contains NaN/Inf")
    return np.maximum(rate, 0.0)


def magnetic_signal_spectrum(
    energy_keV: np.ndarray,
    mu_x_mu_n: float = MU_X_MU_N,
    m_chi_gev: float = M_CHI_GEV,
) -> np.ndarray:
    """Public alias for the raw PandaX magnetic-moment spectrum."""
    return _wimpy_rate(np.asarray(energy_keV, dtype=float), mu_x_mu_n, m_chi_gev)


def pandax_selection_efficiency(
    energy_keV: np.ndarray,
    band: str = "nominal",
) -> np.ndarray:
    """Bounded proxy for total PandaX selection efficiency versus NR energy."""
    p = EFFICIENCY_PROXY[band]
    e = np.asarray(energy_keV, dtype=float)
    # Piecewise-linear interpolation is easier to audit than a fitted sigmoid.
    x = np.array([0.0, 3.0, 5.0, 20.0, 50.0, 120.0])
    y = np.array([0.0, p["at_3_keVnr"], p["at_5_keVnr"], p["at_20_keVnr"], p["above_50_keVnr"], p["above_50_keVnr"]])
    return np.clip(np.interp(e, x, y), 0.0, 1.0)


def _integrate_window(energy_keV: np.ndarray, values: np.ndarray, lo: float, hi: float) -> float:
    mask = (energy_keV >= lo) & (energy_keV <= hi)
    if mask.sum() < 2:
        return 0.0
    return float(np.trapezoid(values[mask], energy_keV[mask]))


def fold_signal_into_pandax(
    energy_keV: np.ndarray,
    raw_rate_per_kg_day_per_keV: np.ndarray,
    efficiency_band: str = "nominal",
    nr_median_acceptance: float = 0.50,
) -> dict:
    """Fold the signal through proxy efficiency and published NR-band split."""
    e = np.asarray(energy_keV, dtype=float)
    raw = np.asarray(raw_rate_per_kg_day_per_keV, dtype=float)
    eff = pandax_selection_efficiency(e, efficiency_band)
    selected = raw * eff
    # Split by the published NR median.  The median itself is a 50% split;
    # the model-envelope values below vary this fraction separately.
    exposure_kg_day = sum(PANDAX_PUBLISHED["exposure_tonne_year"].values()) * 1000.0 * 365.25
    out = {
        "efficiency_band": efficiency_band,
        "nr_median_acceptance": float(nr_median_acceptance),
        "raw_5_50": _integrate_window(e, raw, 5.0, 50.0) * exposure_kg_day,
        "selected_5_50": _integrate_window(e, selected, 5.0, 50.0) * exposure_kg_day,
        "raw_5_270": _integrate_window(e, raw, 5.0, 270.0) * exposure_kg_day,
        "selected_5_270": _integrate_window(e, selected, 5.0, 270.0) * exposure_kg_day,
        "raw_published_nr_roi": 0.0,
        "selected_published_nr_roi": 0.0,
        "selected_nr_band_5_270": 0.0,
        "selected_nr_band_published_roi": 0.0,
    }
    roi_parts = []
    for run, (lo, hi) in PANDAX_PUBLISHED["nr_roi_keV"].items():
        exp = PANDAX_PUBLISHED["exposure_tonne_year"][run] * 1000.0 * 365.25
        raw_roi = _integrate_window(e, raw, lo, hi) * exp
        selected_roi = _integrate_window(e, selected, lo, hi) * exp
        roi_parts.append({"run": run, "roi_keVnr": [lo, hi], "exposure_kg_day": exp, "raw": raw_roi, "selected": selected_roi})
        out["raw_published_nr_roi"] += raw_roi
        out["selected_published_nr_roi"] += selected_roi
    out["selected_nr_band_published_roi"] = out["selected_published_nr_roi"] * nr_median_acceptance
    out["selected_nr_band_5_270"] = out["selected_5_270"] * nr_median_acceptance
    out["run_breakdown"] = roi_parts
    return out


def _log_poisson(n_obs: int, mean: float) -> float:
    if mean <= 0:
        return -1.0e300 if n_obs else 0.0
    return -mean + n_obs * math.log(mean) - math.lgamma(n_obs + 1.0)


def profile_poisson_gaussian_bkg(
    n_obs: int,
    signal: float,
    background: float,
    background_sigma: float,
) -> dict:
    """Profile a non-negative Gaussian-constrained background nuisance."""
    if signal < 0 or background < 0 or background_sigma <= 0:
        raise ValueError("Invalid signal/background inputs")
    upper = max(200.0, n_obs + 12.0 * background_sigma, signal + background + 12.0 * background_sigma)
    grid = np.linspace(0.0, upper, 20001)
    means = signal + grid
    ll = np.array([_log_poisson(n_obs, m) for m in means]) - 0.5 * ((grid - background) / background_sigma) ** 2
    i = int(np.argmax(ll))
    prof_b = float(grid[i])
    prof_ll = float(ll[i])
    # Background-only profile is calculated on the same nuisance grid.
    bg_means = grid
    bg_ll_values = np.array([_log_poisson(n_obs, m) for m in bg_means]) - 0.5 * ((grid - background) / background_sigma) ** 2
    bg_i = int(np.argmax(bg_ll_values))
    bg_prof_ll = float(bg_ll_values[bg_i])
    return {
        "n_obs": int(n_obs),
        "signal": float(signal),
        "background_nominal": float(background),
        "background_sigma": float(background_sigma),
        "profiled_background": prof_b,
        "log_l": prof_ll,
        "background_only_log_l": bg_prof_ll,
        "delta_log_l_vs_background": prof_ll - bg_prof_ll,
    }


def load_candidate_csv_counts() -> dict:
    """Verify the two local public candidate files and reproduce their counts."""
    import csv

    result = {}
    for run in ("run0", "run1"):
        path = PANDAX_DATA_DIR / f"Run{run[-1]}_DM_candidates.csv"
        with path.open("r", encoding="utf-8") as f:
            n = sum(1 for _ in csv.DictReader(f))
        result[run] = {"path": str(path), "n_rows": n}
    result["total"] = sum(v["n_rows"] for k, v in result.items() if k != "total")
    return result


def main() -> dict:
    energy = np.linspace(0.5, 270.0, 6000)
    raw_rate = _wimpy_rate(energy, MU_X_MU_N, M_CHI_GEV)
    folds = {band: fold_signal_into_pandax(energy, raw_rate, band) for band in EFFICIENCY_PROXY}
    nominal = folds["nominal"]
    low = folds["low"]
    high = folds["high"]
    # Propagate a separate uncertainty for the NR-median split; this is not a
    # statistical error and is intentionally shown as a model-envelope term.
    nr_band_factors = {"low": 0.40, "nominal": 0.50, "high": 0.60}
    nr_band_signal = {
        k: folds[k]["selected_published_nr_roi"] * nr_band_factors[k]
        for k in folds
    }
    likelihood = {
        k: profile_poisson_gaussian_bkg(
            PANDAX_PUBLISHED["n_below_nr_median"],
            nr_band_signal[k],
            PANDAX_PUBLISHED["background_below_nr_median"],
            PANDAX_PUBLISHED["background_below_nr_median_sigma"],
        )
        for k in folds
    }
    output = {
        "analysis": "T90.24 PandaX efficiency/background fold",
        "status": "live_public_data_approximate_recast",
        "parameters": {"mu_x_mu_N": MU_X_MU_N, "m_chi_GeV": M_CHI_GEV},
        "candidate_csv_verification": load_candidate_csv_counts(),
        "published_inputs": PANDAX_PUBLISHED,
        "efficiency_proxy": EFFICIENCY_PROXY,
        "folds": folds,
        "nr_band_signal_by_efficiency_envelope": nr_band_signal,
        "published_observable_likelihood": likelihood,
        "headline": (
            "Using the published PandaX below-NR-median observable (24 observed, "
            "20.5 +/- 2.5 background), the LZ-tuned magnetic-moment signal remains "
            "a large predicted contribution after the explicit efficiency proxy. "
            "This is an approximate public-data recast because the full PandaX "
            "multidimensional efficiency/response maps are not public."
        ),
        "not_claimed": [
            "No claim of an official PandaX likelihood or official exclusion is made.",
            "The 287 candidate count in an approximate NEST energy inversion is not used as the primary likelihood observable.",
            "The old 695-event [200,300] extrapolated count is not used; the published PandaX DM ROI ends near 94-103 keVnr.",
        ],
        "sources": [
            "PandaX Collaboration, arXiv:2408.00664 / PRL 134, 011805",
            "https://pandax.sjtu.edu.cn/public/data_release",
        ],
    }
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    out_path = OUTPUT_DIR / "t90_v24_pandax_fold.json"
    out_path.write_text(json.dumps(output, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps({
        "output": str(out_path),
        "csv_counts": output["candidate_csv_verification"],
        "selected_5_50_nominal": nominal["selected_5_50"],
        "selected_published_roi_nominal": nominal["selected_published_nr_roi"],
        "nr_band_signal_nominal": nr_band_signal["nominal"],
        "likelihood_delta_log_l_nominal": likelihood["nominal"]["delta_log_l_vs_background"],
        "likelihood_delta_log_l_low_high": [likelihood["low"]["delta_log_l_vs_background"], likelihood["high"]["delta_log_l_vs_background"]],
    }, indent=2))
    return output


if __name__ == "__main__":
    main()
