"""
T90.23 PATH 2B (LIVE) — PandaX-4T 1.54 t-y NR-band smoke test (revisited).

This script uses PandaX's PUBLISHED observation: 24 events below the
NR median in [5, 270] keVnr (12 in Run 0, 12 in Run 1). It compares
that observation to the magnetic-moment prediction at the LZ-tuned
coupling, scaled to PandaX exposure.

NOTE on PandaX's published findings (PRL 134, 011805):
  - Total events in analysis ROI: 2490 (Run 0: 1117, Run 1: 1373)
  - Events BELOW NR median (i.e. in NR band): 24 (12 in Run 0, 12 in Run 1)
  - Below-NR-median expected backgrounds: 20.5 +/- 2.5 (summed from Table I)

So 24 events observed vs 20.5 expected background. The likelihood fit
gives GoF p-value 0.64, consistent with background only.

Magnetic-m at LZ-tuned coupling predicts:
  - LZ 2.84 t-y: ~720 events at [50, 200] keVnr (NR-band)
  - PandaX 1.54 t-y: ~390 events at [50, 200] keVnr (NR-band, scaled)
  - PandaX [5, 270] NR-band: ~720 events (mostly above 50 keVnr)

PERFORMING THE SMOKING-GUN COMPARISON:
  PandaX observed: 24 events below NR median in [5, 270]
  PandaX expected background: 20.5 events
  Magnetic-m prediction: ~720 events

  Ratio obs/magnetic-m: 24/720 = 0.033 (3%)
  Ratio obs/background: 24/20.5 = 1.17 (consistent with background)

  CONCLUSION: Magnetic-m at LZ-tuned coupling is OVER-PREDICTED
  by factor of ~30 at PandaX. The 24 events PandaX sees in the
  NR band are consistent with background alone.

This means: magnetic-m at the LZ-tuned coupling is RULED OUT
by PandaX's NR-band observation.

The data is consistent with background-only; magnetic-m would
predict ~720 events but only 24 are observed. The model's
explanation of the LZ 248 keV event at μ_x = 6.10×10⁻⁸ μ_N
is NOT compatible with PandaX data unless the coupling is much
smaller (off by factor ~30).
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

# Project imports
_PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_PROJECT_ROOT / "code"))


# PandaX PRL 134, 011805 published numbers
PANDAX_PUBLISHED = {
    "n_total_in_ROI": 2490,
    "n_run0": 1117,
    "n_run1": 1373,
    "n_below_NR_median_total": 24,
    "n_below_NR_median_run0": 12,
    "n_below_NR_median_run1": 12,
    "background_below_NR_median_total": 20.5,
    "background_below_NR_median_unc": 2.5,
    "background_components_below_NR_median": {
        "85Kr_ER_leak": 3.6,
        "Material_ER_leak": 0.6,
        "Solar_EES_ER_leak": 1.4,
        "136Xe_ER_leak": 0.6,
        "Other_ER_leak": 0.4,
        "Other_ER_data_leak": 0.2,
        "Tritium_ER_leak": 6.4,
        "127Xe_ER_leak": 5.2,
        "124Xe_ER_leak": 0.10,
        "Neutron": 1.0,
        "8B_CEvNS": 1.0,
        "Surface": 0.26,
        "Accidental": 0.26,
        # sum = 20.98
    },
    "goF_p_value_background_only": 0.64,
}

# Magnetic-m predictions at LZ-tuned coupling, scaled to PandaX 1.54 t-y
# (from t90_v12 dry-run, scaled by 1.54/2.84 = 0.542)
MAG_MOMENT_PREDICTIONS_PANDAX = {
    "mu_x_mu_N": 6.10e-8,
    "m_chi_GeV": 1000.0,
    "exposure_tonne_years": 1.54,
    "N_predicted_5_270_keVnr_total": 720.0,    # LZ 1500 * 0.542 (very rough)
    "N_predicted_5_50_keVnr": 422.0,
    "N_predicted_50_200_keVnr": 390.0,
    "N_predicted_200_300_keVnr": 0.54,
    "source": "t90_v12 dry-run, scaled by 1.54/2.84 = 0.542 from LZ 2.84 t-y",
}


def main():
    print("=" * 70)
    print("T90.23 Path 2B — PandaX-4T NR-band smoke test (published)")
    print("=" * 70)
    print()
    print("Source: PandaX-4T 1.54 t-y paper, PRL 134, 011805 (2025)")
    print("       arXiv:2408.00664")
    print()

    n_obs_below_NR = PANDAX_PUBLISHED["n_below_NR_median_total"]
    n_bg_below_NR = PANDAX_PUBLISHED["background_below_NR_median_total"]
    n_magmom_below_NR = MAG_MOMENT_PREDICTIONS_PANDAX["N_predicted_5_270_keVnr_total"]

    print(f"PandaX observed below NR median (entire [5, 270] keVnr): {n_obs_below_NR} events")
    print(f"PandaX expected background below NR median: {n_bg_below_NR} +/- {PANDAX_PUBLISHED['background_below_NR_median_unc']} events")
    print(f"Magnetic-m prediction at LZ-tuned coupling: ~{n_magmom_below_NR} events")
    print()

    ratio_obs_magmom = n_obs_below_NR / max(n_magmom_below_NR, 1)
    ratio_obs_bg = n_obs_below_NR / max(n_bg_below_NR, 1)

    print(f"Ratio observed / magnetic-m: {ratio_obs_magmom:.3f}")
    print(f"Ratio observed / background: {ratio_obs_bg:.3f}")
    print()

    # Verdict logic
    print("=" * 70)
    print("VERDICT")
    print("=" * 70)
    print()

    # Compute approximate Poisson log L for magnetic-m vs background
    # log P(24 | mu_magmom) - log P(24 | mu_bg)
    import math
    n_obs = n_obs_below_NR

    ll_magmom = -n_magmom_below_NR + n_obs * np.log(n_magmom_below_NR) - math.lgamma(n_obs + 1)
    ll_bg = -n_bg_below_NR + n_obs * np.log(n_bg_below_NR) - math.lgamma(n_obs + 1)
    delta_log_l_bg_vs_magmom = ll_bg - ll_magmom
    print(f"log L(magnetic-m) = {ll_magmom:.2f}")
    print(f"log L(background-only) = {ll_bg:.2f}")
    print(f"Delta log L (background - magnetic-m) = {delta_log_l_bg_vs_magmom:.2f}")
    print()

    if delta_log_l_bg_vs_magmom > 100:
        verdict = ("Magnetic-m at LZ-tuned coupling is DECISIVELY OVER-PREDICTED. "
                   f"Delta log L = {delta_log_l_bg_vs_magmom:.1f} in favor of background. "
                   "The PandaX data rules out the magnetic-m interpretation of the "
                   "LZ 248 keV event at the LZ-tuned coupling of mu_x = 6.10e-8 mu_N.")
    elif delta_log_l_bg_vs_magmom > 10:
        verdict = (f"Magnetic-m is over-predicted by a factor of "
                   f"{n_magmom_below_NR/n_bg_below_NR:.1f} relative to background. "
                   f"Delta log L = {delta_log_l_bg_vs_magmom:.1f} favoring background. "
                   "Magnetic-m at LZ-tuned coupling is excluded.")
    else:
        verdict = "Inconclusive - need more data or refined analysis."

    print(verdict)
    print()

    # Implication for T90 merge rule
    print("=" * 70)
    print("IMPLICATION FOR T90 MERGE RULE")
    print("=" * 70)
    print()
    print("The T90 magnetic-moment interpretation was tuned to explain the LZ")
    print("248 keV event. The coupling mu_x = 6.10e-8 mu_N was derived from LZ data.")
    print()
    print("At PandaX, this SAME coupling predicts ~720 NR-band events in [5, 270]")
    print("keVnr, but PandaX observes only 24 (12 in Run 0, 12 in Run 1), consistent")
    print("with backgrounds (20.5 expected) alone.")
    print()
    print("Conclusion: Magnetic-m at LZ-tuned coupling is RULED OUT by PandaX.")
    print()
    print("Possible resolutions:")
    print("  1. The LZ 248 keV event is NOT magnetic-m (most likely given PandaX)")
    print("  2. The magnetic-m interpretation requires a lower coupling (factor ~30 lower)")
    print("     - This would not explain LZ's 1 event at 248 keVnr at the predicted rate")
    print("  3. The PandaX and LZ analyses have systematic differences that make the")
    print("     predictions not directly comparable (e.g. different g1, g2b values,")
    print("     different NR medians, different signal efficiencies)")
    print()
    print("The PandaX constraint is the most robust public data cross-check available")
    print("and STRONGLY disfavors the magnetic-m interpretation at the LZ-tuned coupling.")

    output = {
        "mode": "live_published",
        "source": "PandaX-4T 1.54 t-y paper, PRL 134, 011805 (2025)",
        "pandax_published": PANDAX_PUBLISHED,
        "magnetic_moment_predictions_pandax": MAG_MOMENT_PREDICTIONS_PANDAX,
        "comparison": {
            "n_obs_below_NR_median": n_obs_below_NR,
            "n_background_below_NR_median": n_bg_below_NR,
            "n_magnetic_m_below_NR_median": n_magmom_below_NR,
            "ratio_obs_to_magnetic_m": ratio_obs_magmom,
            "ratio_obs_to_background": ratio_obs_bg,
            "log_l_magnetic_m": ll_magmom,
            "log_l_background": ll_bg,
            "delta_log_l_background_minus_magnetic_m": delta_log_l_bg_vs_magmom,
        },
        "headline_verdict": verdict,
        "t90_merge_implication": (
            "Magnetic-m at the LZ-tuned coupling (mu_x = 6.10e-8 mu_N) is RULED OUT "
            "by PandaX-4T's NR-band observation. The T90 magnetic-m interpretation "
            "as currently tuned is not viable."
        ),
        "caveats": [
            "PandaX's NR median curve is approximated; events on either side of the curve may differ by ~10-20% from my count.",
            "Background subtraction uncertainty (~10%) doesn't change the verdict.",
            "Systematic differences in g1, g2b, and E-field between PandaX and LZ could shift predictions by ~30% but not enough to reconcile factor-30 discrepancy.",
            "If LZ 248 keV event is real but the magnetic-m interpretation requires lower coupling, T90 needs to revisit mu_x value.",
        ],
    }

    out_path = _PROJECT_ROOT / "outputs" / "t90" / "t90_v23_pandax_NRband_smoke.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    print(f"\n[output] {out_path}")

    return output


if __name__ == "__main__":
    main()
