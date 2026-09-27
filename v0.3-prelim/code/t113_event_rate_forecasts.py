"""
T113 — Event-rate forecasts at Door-B MAP point for next-round experiments.

Implements reviewer suggestion §3(a) + §3(c) from
'Suggestions for taking Door B further' (2026-09-08):

  (a) Forecast expected number of events in LZ Run 4, PandaX-4T Run 3,
      XENONnT S2-only analyses at the Door-B MAP point.
  (c) Forecast the signal in argon (DarkSide-20k) — a different target
      nucleus changes the kinematics and can break degeneracies.

Inputs: T108 MAP point (m_chi=138 GeV, delta=98 keV, sigma_PortalB=1.43e-42 cm^2).
Outputs: predicted events in [200, 300] keV window for each experiment.

Forecasts use a simplified rate formula:
  N_events = (exposure * sigma * f_window) * (form_factor/m_chi_scaling)

Each experiment's predicted event rate is computed at the T108 MAP.
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import numpy as np

SCRIPT_DIR = Path(__file__).resolve().parent
V03_ROOT = SCRIPT_DIR.parent
sys.path.insert(0, str(SCRIPT_DIR))

# T108 MAP (from t108_full_8d_dynesty.json)
T108_MAP = {
    "m_chi_GeV": 138.0,
    "delta_keV": 98.0,
    "sigma_PortalB_cm2": 1.43e-42,
}

# Next-round experiment parameters (planned exposures)
EXPERIMENTS = {
    "LZ_Run4_2027_2028": {
        "exposure_tonne_year": 20.0,  # 5x current 2.84 tonne-year
        "target": "xenon",
        "analysis": "standard",
        "current_run": "LZ Run 3 (2024) 2.84 tonne-year",
    },
    "PandaX-4T_Run3_2026_2027": {
        "exposure_tonne_year": 3.7,  # current + projected
        "target": "xenon",
        "analysis": "with-124Xe-DEC-fix",
        "current_run": "PandaX-4T (2021) 0.63 tonne-year",
    },
    "XENONnT_S2only_2027": {
        "exposure_tonne_year": 8.0,  # current + projected
        "target": "xenon",
        "analysis": "S2-only (lower threshold)",
        "current_run": "XENONnT (2024) 1.16 tonne-year",
    },
    "DarkSide-20k_2028": {
        "exposure_tonne_year": 100.0,  # planned (argon, large exposure)
        "target": "argon",
        "analysis": "standard",
        "current_run": "DarkSide-50 (2018) 0.05 tonne-year",
    },
}


def predicted_events(exposure_tonne_year, sigma_cm2, m_chi_GeV, target="xenon", delta_keV=98.0):
    """Predict number of events in [200, 300] keV window.

    Simplified formula:
        N_pred = (exposure * sigma / sigma_ref) * (m_chi_ref / m_chi) * f_window * form_factor

    Where:
      - sigma_ref = 1e-45 cm^2 (calibration)
      - m_chi_ref = 100 GeV (calibration)
      - f_window = fraction of recoil spectrum in [200, 300] keV window
      - form_factor = 1 for xenon, 0.3 for argon (different nuclear form factor)
    """
    sigma_ref = 1e-45
    m_chi_ref = 100.0
    f_window = 0.05  # rough fraction in 100 keV window for inelastic at threshold
    if target == "xenon":
        form_factor = 1.0
    elif target == "argon":
        form_factor = 0.3  # smaller nucleus, weaker form factor
    else:
        form_factor = 1.0

    N_pred = exposure_tonne_year * (sigma_cm2 / sigma_ref) * (m_chi_ref / m_chi_GeV) * f_window * form_factor
    return N_pred


def annual_modulation_amplitude(N_pred):
    """Crude amplitude estimate for annual modulation.

    For elastic DM, amplitude ~ 0.07 * N_mean.
    For inelastic DM (delta > 0), amplitude is suppressed by delta/m_chi,
    but modulation phase shifts.

    Returns: amplitude in events (rough estimate).
    """
    # Inelastic suppression factor: ~0.3 for delta/m_chi ~ 1e-3
    suppression = 0.3
    return 0.07 * N_pred * suppression


def main():
    out_dir = V03_ROOT / "outputs" / "t95"
    out_dir.mkdir(parents=True, exist_ok=True)

    print("=" * 80)
    print("T113 — Event-rate forecasts at Door-B MAP")
    print("=" * 80)
    print()
    print(f"T108 MAP point: m_chi = {T108_MAP['m_chi_GeV']:.1f} GeV, "
          f"delta = {T108_MAP['delta_keV']:.1f} keV, "
          f"sigma_PortalB = {T108_MAP['sigma_PortalB_cm2']:.2e} cm²")
    print()

    forecasts = {}
    for exp_name, exp_params in EXPERIMENTS.items():
        N_pred = predicted_events(
            exposure_tonne_year=exp_params["exposure_tonne_year"],
            sigma_cm2=T108_MAP["sigma_PortalB_cm2"],
            m_chi_GeV=T108_MAP["m_chi_GeV"],
            target=exp_params["target"],
            delta_keV=T108_MAP["delta_keV"],
        )
        amp = annual_modulation_amplitude(N_pred)

        forecasts[exp_name] = {
            "exposure_tonne_year": exp_params["exposure_tonne_year"],
            "target": exp_params["target"],
            "analysis": exp_params["analysis"],
            "current_run": exp_params["current_run"],
            "N_pred_in_200_300_keV_window": float(N_pred),
            "annual_modulation_amplitude_events": float(amp),
            "T108_MAP_assumed": T108_MAP,
        }
        print(f"  {exp_name}:")
        print(f"    exposure: {exp_params['exposure_tonne_year']} tonne-year ({exp_params['target']})")
        print(f"    N_pred (200-300 keV window): {N_pred:.3f} events")
        print(f"    annual modulation amplitude: {amp:.3f} events")
        print()

    # Summary table
    print("=" * 70)
    print("SUMMARY: Door-B MAP event-rate forecasts")
    print("=" * 70)
    print(f"{'Experiment':<35} {'Exposure':<12} {'N_pred':<10} {'Amp':<8}")
    for exp_name, f in forecasts.items():
        print(f"{exp_name:<35} {f['exposure_tonne_year']:<12.1f} {f['N_pred_in_200_300_keV_window']:<10.3f} {f['annual_modulation_amplitude_events']:<8.3f}")

    out = {
        "test": "T113_event_rate_forecasts",
        "date": "2026-09-08",
        "description": (
            "T113 — event-rate forecasts at T108 MAP (m_chi=138 GeV, delta=98 keV, "
            "sigma_PortalB=1.43e-42 cm^2) for next-round experiments. Implements "
            "reviewer suggestions §3(a) and §3(c) from 'Suggestions for taking "
            "Door B further'."
        ),
        "reviewer_suggestions_addressed": ["§3(a) event-rate forecasts", "§3(c) DarkSide-20k forecast"],
        "T108_MAP_used": T108_MAP,
        "forecasts": forecasts,
        "caveats": [
            "Simplified rate formula; real experiments use binned Poisson on full recoil spectrum.",
            "Form-factor scaling is approximate (1.0 for xenon, 0.3 for argon).",
            "f_window = 0.05 is rough estimate for 100 keV window at inelastic threshold.",
            "Annual modulation amplitude is suppressed by delta/m_chi for inelastic DM.",
            "Real predictions require detector-specific response functions and efficiencies.",
            "Numbers are ORDER-OF-MAGNITUDE estimates, suitable for planning, not for publication.",
        ],
    }

    out_path = out_dir / "t113_event_rate_forecasts.json"
    with open(out_path, "w") as f:
        json.dump(out, f, indent=2)
    print(f"\nWrote: {out_path}")


if __name__ == "__main__":
    main()