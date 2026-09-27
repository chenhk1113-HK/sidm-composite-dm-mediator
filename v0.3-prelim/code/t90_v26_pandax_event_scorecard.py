"""T90.26: event-level PandaX public-data scorecard.

This is deliberately not a claim of identifying dark-matter events. It maps
public candidate records to approximate ER energy and reports how they rank
against a simple NR-like band. It also computes the magnetic signal's expected
rate in the same public observable using the extracted PandaX efficiency curve.
The output separates: observed records, model expectation, and a descriptive
score only.
"""
from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

import numpy as np

_PROJECT_ROOT = Path(__file__).resolve().parents[1]
CODE_DIR = _PROJECT_ROOT / "code"
if str(CODE_DIR) not in sys.path:
    sys.path.insert(0, str(CODE_DIR))

from t90_v24_pandax_fold import MU_X_MU_N, M_CHI_GEV, _integrate_window, _wimpy_rate  # noqa: E402
from t90_v25_pandax_efficiency_background_fold import public_efficiency  # noqa: E402

DATA_DIR = _PROJECT_ROOT / "data" / "external_data" / "pandax_4t"
OUTPUT_DIR = _PROJECT_ROOT / "outputs" / "t90"
RUNS = {
    "run0": {"g1": 0.0997, "g2b": 4.12, "field": 92.8, "exposure_ty": 0.54, "roi": [4.0, 94.0]},
    "run1": {"g1": 0.0907, "g2b": 5.029, "field": 84.4, "exposure_ty": 1.00, "roi": [3.0, 103.0]},
}


def nr_ee_keV(energy_nr: np.ndarray, field: float) -> np.ndarray:
    mf0 = 0.0480 * field ** (-0.0533) * (2.8611 / 2.90) ** 0.30
    mf1 = 1.0 - 1.0 / (1.0 + (energy_nr / 0.3) ** 2)
    n_e = energy_nr * mf1 / (mf0 * np.sqrt(energy_nr + 12.6))
    n_ph = (11.0 * energy_nr ** 1.1 - n_e) * mf1
    return 0.0137 * (n_ph + n_e)


def map_candidate_record(qs1: float, qs2b: float, run: str) -> dict:
    p = RUNS[run]
    eee = 0.0137 * (qs1 / p["g1"] + qs2b / p["g2b"])
    grid_er = np.linspace(0.01, 150.0, 30000)
    grid_ee = nr_ee_keV(grid_er, p["field"])
    er = float(np.interp(eee, grid_ee, grid_er, left=np.nan, right=np.nan))
    # Descriptive NR-like score: below the approximate NR-median line used by
    # the public plot script. It is not a classification probability.
    lg = float(np.log10(qs2b / qs1))
    nr_median = float(-0.05 + np.log10(max(qs1, 0.5)))
    return {"qS1": qs1, "qS2B": qs2b, "Eee_keV": eee, "E_R_approx_keVnr": er, "log10_S2B_over_S1": lg, "nr_median_proxy": nr_median, "below_nr_median_proxy": bool(lg < nr_median)}


def load_events() -> dict:
    out = {}
    for run, p in RUNS.items():
        path = DATA_DIR / f"Run{run[-1]}_DM_candidates.csv"
        events = []
        with path.open(encoding="utf-8") as f:
            for row in csv.DictReader(f):
                events.append(map_candidate_record(float(row["qS1"]), float(row["qS2B"]), run))
        out[run] = events
    return out


def signal_prediction() -> dict:
    energy = np.linspace(0.5, 150.0, 6000)
    raw = _wimpy_rate(energy, MU_X_MU_N, M_CHI_GEV)
    eff = public_efficiency(energy)
    result = {}
    for run, p in RUNS.items():
        exp = p["exposure_ty"] * 1000.0 * 365.25
        lo, hi = p["roi"]
        selected = _integrate_window(energy, raw * eff, lo, hi) * exp
        result[run] = {"roi_keVnr": p["roi"], "selected_signal": float(selected), "selected_signal_below_nr_median_proxy": float(selected * 0.5)}
    result["combined"] = {k: float(sum(v[k] for r, v in result.items() if r != "combined")) for k in ("selected_signal", "selected_signal_below_nr_median_proxy")}
    return result


def main() -> dict:
    events = load_events()
    observed = {}
    for run, rows in events.items():
        observed[run] = {
            "n_records": len(rows),
            "n_below_nr_median_proxy": sum(r["below_nr_median_proxy"] for r in rows),
            "n_approx_3_to_50_keVnr": sum(3.0 <= r["E_R_approx_keVnr"] <= 50.0 for r in rows),
            "n_approx_published_roi": sum(RUNS[run]["roi"][0] <= r["E_R_approx_keVnr"] <= RUNS[run]["roi"][1] for r in rows),
            "energy_percentiles_keVnr": np.nanpercentile([r["E_R_approx_keVnr"] for r in rows], [5, 50, 95]).tolist(),
        }
    observed["combined"] = {k: sum(v[k] for r, v in observed.items() if r != "combined") for k in ("n_records", "n_below_nr_median_proxy", "n_approx_3_to_50_keVnr", "n_approx_published_roi")}
    output = {
        "analysis": "T90.26 PandaX event-level public scorecard",
        "status": "descriptive_event_mapping_not_event_identification",
        "observed": observed,
        "events": events,
        "model": {"mu_x_mu_N": MU_X_MU_N, "m_chi_GeV": M_CHI_GEV, "prediction": signal_prediction()},
        "interpretation": [
            "No individual event is labeled as dark matter.",
            "The below-NR-median flag is a descriptive proxy, not PandaX's official likelihood classification.",
            "The model prediction is an expected ensemble mean, not a list of records to match one-to-one.",
            "Exact identification requires the full PandaX S1/S2 signal templates and nuisance model, which are not public.",
        ],
        "sources": ["PandaX public candidate bundle", "PandaX Collaboration arXiv:2408.00664 / PRL 134, 011805"],
    }
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    path = OUTPUT_DIR / "t90_v26_pandax_event_scorecard.json"
    path.write_text(json.dumps(output, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps({"output": str(path), "observed": observed, "model": output["model"]}, indent=2))
    return output


if __name__ == "__main__":
    main()
