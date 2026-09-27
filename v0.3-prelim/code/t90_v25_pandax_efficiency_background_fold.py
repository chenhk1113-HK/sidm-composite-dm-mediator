"""T90.25: PandaX public efficiency + background-folded recast.

Uses PandaX's publicly released total NR efficiency TGraph ``eff_nr``
(obtained from the collaboration data-release page), the public Run-0/Run-1
candidate CSV row counts, and the published below-NR-median background model.
The signal is folded in the published Run-0/Run-1 NR ROIs separately.

This remains an approximate physics recast: the public graph is one-dimensional
and from the first-analysis response release; it is not PandaX's private
Run-0+Run-1 multidimensional S1/S2 response or event-by-event NR-median
acceptance map.
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import numpy as np

_PROJECT_ROOT = Path(__file__).resolve().parents[1]
CODE_DIR = _PROJECT_ROOT / "code"
DATA_DIR = _PROJECT_ROOT / "data" / "external_data" / "pandax_4t"
OUTPUT_DIR = _PROJECT_ROOT / "outputs" / "t90"
if str(CODE_DIR) not in sys.path:
    sys.path.insert(0, str(CODE_DIR))

from t90_v24_pandax_fold import (  # noqa: E402
    MU_X_MU_N,
    M_CHI_GEV,
    PANDAX_PUBLISHED,
    _integrate_window,
    _wimpy_rate,
    _log_poisson,
    profile_poisson_gaussian_bkg,
)
from t90_v25_pandax_public_response import load_efficiency_graph  # noqa: E402


def public_efficiency(energy_keV: np.ndarray) -> np.ndarray:
    """Interpolate the published PandaX ``eff_nr`` graph, zero outside range."""
    graph = load_efficiency_graph()
    x = np.asarray(graph["x_values"], dtype=float)
    y = np.asarray(graph["y_values"], dtype=float)
    e = np.asarray(energy_keV, dtype=float)
    return np.clip(np.interp(e, x, y, left=0.0, right=0.0), 0.0, 1.0)


def load_candidate_counts() -> dict:
    import csv

    counts = {}
    for run in ("run0", "run1"):
        path = DATA_DIR / f"Run{run[-1]}_DM_candidates.csv"
        with path.open(encoding="utf-8") as f:
            counts[run] = sum(1 for _ in csv.DictReader(f))
    counts["total"] = counts["run0"] + counts["run1"]
    return counts


def fold_by_run(energy_keV: np.ndarray, raw_rate: np.ndarray) -> dict:
    eff = public_efficiency(energy_keV)
    selected_rate = raw_rate * eff
    results = {}
    for run, (lo, hi) in PANDAX_PUBLISHED["nr_roi_keV"].items():
        exposure = PANDAX_PUBLISHED["exposure_tonne_year"][run] * 1000.0 * 365.25
        raw = _integrate_window(energy_keV, raw_rate, lo, hi) * exposure
        selected = _integrate_window(energy_keV, selected_rate, lo, hi) * exposure
        results[run] = {
            "roi_keVnr": [lo, hi],
            "exposure_kg_day": exposure,
            "raw_signal": raw,
            "efficiency_folded_signal": selected,
            "efficiency_weighted": selected / raw if raw else 0.0,
        }
    results["combined"] = {
        "raw_signal": sum(v["raw_signal"] for k, v in results.items() if k != "combined"),
        "efficiency_folded_signal": sum(v["efficiency_folded_signal"] for k, v in results.items() if k != "combined"),
    }
    return results


def main() -> dict:
    energy = np.linspace(0.5, 270.0, 6000)
    raw_rate = _wimpy_rate(energy, MU_X_MU_N, M_CHI_GEV)
    graph = load_efficiency_graph()
    fold = fold_by_run(energy, raw_rate)
    selected = fold["combined"]["efficiency_folded_signal"]

    # The published NR median is an S1/S2 boundary. Without the collaboration's
    # 2D signal response, report a transparent 40/50/60% acceptance envelope.
    nr_fraction = {"low": 0.40, "nominal": 0.50, "high": 0.60}
    signal_by_envelope = {k: selected * v for k, v in nr_fraction.items()}
    likelihood = {
        k: profile_poisson_gaussian_bkg(
            PANDAX_PUBLISHED["n_below_nr_median"], signal,
            PANDAX_PUBLISHED["background_below_nr_median"],
            PANDAX_PUBLISHED["background_below_nr_median_sigma"],
        )
        for k, signal in signal_by_envelope.items()
    }

    output = {
        "analysis": "T90.25 PandaX public efficiency and background fold",
        "status": "live_public_data_approximate_recast",
        "parameters": {"mu_x_mu_N": MU_X_MU_N, "m_chi_GeV": M_CHI_GEV},
        "candidate_counts": load_candidate_counts(),
        "efficiency_graph": {
            "source": graph["source"],
            "source_url": graph["source_url"],
            "graph_name": graph["graph_name"],
            "n_points": graph["n_points"],
            "x_units": graph["x_units"],
            "x_min": graph["x_min"], "x_max": graph["x_max"],
            "y_min": graph["y_min"], "y_max": graph["y_max"],
            "sample_points": [
                {"E_R_keVnr": e, "efficiency": float(public_efficiency(np.array([e]))[0])}
                for e in (3.0, 5.0, 10.0, 20.0, 50.0, 80.0, 94.0, 103.0)
            ],
        },
        "published_inputs": {
            "roi_keVnr": PANDAX_PUBLISHED["nr_roi_keV"],
            "n_below_nr_median": PANDAX_PUBLISHED["n_below_nr_median"],
            "background_below_nr_median": PANDAX_PUBLISHED["background_below_nr_median"],
            "background_sigma": PANDAX_PUBLISHED["background_below_nr_median_sigma"],
            "background_components": PANDAX_PUBLISHED["background_components_below_nr_median"],
        },
        "fold_by_run": fold,
        "nr_median_signal_envelope": signal_by_envelope,
        "likelihood": likelihood,
        "headline": (
            "The public PandaX eff_nr curve reduces the LZ-tuned magnetic signal "
            f"to {selected:.2f} selected events in the published Run-0/Run-1 NR ROI. "
            "Using a transparent 40-60% NR-median acceptance envelope gives "
            f"{signal_by_envelope['low']:.2f}-{signal_by_envelope['high']:.2f} signal "
            "events below the median, versus 24 observed and 20.5 +/- 2.5 background."
        ),
        "interpretation": (
            "This is evidence of tension at the level of the public approximate recast, "
            "but not a collaboration-grade exclusion: the exact Run-0+Run-1 2D signal "
            "response and NR-median acceptance map are not public."
        ),
        "not_used": [
            "The old exposure-scaled 422-event estimate.",
            "The old extrapolated 695-event [200,300] keVnr count.",
            "The approximate 287-event NEST-inverted count as the primary likelihood observable.",
        ],
        "sources": [
            "PandaX public response release: " + graph["source_url"],
            "PandaX Collaboration, arXiv:2408.00664 / PRL 134, 011805",
            "PandaX data release: https://pandax.sjtu.edu.cn/public/data_release",
        ],
    }
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    path = OUTPUT_DIR / "t90_v25_pandax_efficiency_background_fold.json"
    path.write_text(json.dumps(output, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps({
        "output": str(path), "candidate_counts": output["candidate_counts"],
        "graph_points": graph["n_points"], "selected_roi": selected,
        "nr_band_signal": signal_by_envelope,
        "delta_log_l": {k: v["delta_log_l_vs_background"] for k, v in likelihood.items()},
    }, indent=2))
    return output


if __name__ == "__main__":
    main()
