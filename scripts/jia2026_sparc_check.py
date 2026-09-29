"""Layer 3 v19.0.3 -- REAL verification per rev192.docx Reviewer 1.

This script computes sigma_pred(v=100) from the paper's three-term Path F1
model using each prescription's fitted parameters, then compares to the
paper's reported per-channel log L values.

Per Reviewer 1 (rev192.docx): a real verification requires:
  1. Take the paper's three-term Path F1 model
  2. Compute sigma_pred(v=100) for each f_H prescription
  3. Compute log L = -0.5 * ((sigma_pred - 0.193) / sigma_unc)^2
  4. Compare computed log L to paper's reported values (-0.09, -0.24, -0.60, -2.03)

This script does exactly that. The fitted parameters come from
v0.3-prelim/data/results/t207_final_summary.json (canonical T207 fit result).

Source data path: the SPARC v=100 per-channel log L is the paper's primary
anchor; sigma_unc = 0.05 is from T205 published SPARC measurement convention.
The "borrowed" / "yang" / "t202" / "priored free fit" rows are taken directly
from the paper's section 9.11 verdict split table.

Honest framing:
  - sigma_HH uses Phase 44's energy-space Breit-Wigner (sigma_m_at_v from
    phase44_joint_fit), with sigma_peak_HH_1 overridden to the prescription's
    fitted value.
  - sigma_HL uses a Lorentzian Breit-Wigner in velocity space (T207 convention),
    with the prescription's fitted v_HL, sigma_peak_HL, sigma_0_HL.
  - sigma_LL is pure Yukawa background: sigma_0_LL * (v_ref/v)^a_slope.
  - width_HL = 50 km/s default from T207 (not fitted per prescription).
  - sigma_unc at v=100 = 0.05 cm^2/g from SPARC T205 published value.

If this script reproduces the paper's per-channel log L, the paper is verified.
If it doesn't, the paper has a parameter-convention gap that needs explanation.
"""
from __future__ import annotations

import json
from pathlib import Path
import sys

# Make sure the project code dir is on path so we can import the canonical
# sigma_m_at_v from phase44_joint_fit
REPO = Path(r"C:\Users\lamkuenai\projects\sidm-composite-dm-mediator")
sys.path.insert(0, str(REPO / "v0.3-prelim" / "code"))

# Import the canonical machinery
from phase44_joint_fit import sigma_m_at_v as p44_sigma_m_at_v  # noqa: E402
from two_component_three_term import (  # noqa: E402
    lorentzian_bw,
    _phase44_params,
    _build_phase44_resonances,
)


# ----- Three-term model helpers (mirror the canonical two_component_three_term.py) -----

def sigma_HH_at_v(v_kms, sigma_0, a_slope, sigma_peak_HH_1):
    """Heavy-heavy channel sigma/m(v).

    Uses Phase 44's energy-space Breit-Wigner with sigma_peak_HH_1 overridden.
    """
    p = _phase44_params()
    m_chi = p["m_chi"]
    sigma_peaks = list(p["sigma_peaks"])
    sigma_peaks[0] = sigma_peak_HH_1
    resonances = _build_phase44_resonances(
        override_sigma_0=sigma_0, override_a_slope=a_slope,
        override_sigma_peaks=sigma_peaks,
    )
    return p44_sigma_m_at_v(v_kms, m_chi, resonances, sigma_0, a_slope)


def sigma_HL_at_v(v_kms, sigma_0_HL, a_slope, sigma_peak_HL, v_HL, width_HL=50.0, v_ref=100.0):
    """Heavy-light channel sigma/m(v)."""
    bg = sigma_0_HL * (v_ref / v_kms) ** a_slope
    peak = sigma_peak_HL * lorentzian_bw(v_kms, v_HL, width_HL)
    return bg + peak


def sigma_LL_at_v(v_kms, sigma_0_LL, a_slope, v_ref=100.0):
    """Light-light channel sigma/m(v) (pure Yukawa)."""
    return sigma_0_LL * (v_ref / v_kms) ** a_slope


def sigma_eff_three_term(
    v_kms, f_H, sigma_0, a_slope, sigma_peak_HH_1,
    sigma_0_HL, sigma_peak_HL, v_HL, sigma_0_LL, width_HL=50.0,
):
    """Three-term mixture rule:
        sigma_eff(v) = f_H^2 * sigma_HH + 2 f_H f_L * sigma_HL + f_L^2 * sigma_LL
    """
    f_L = 1.0 - f_H
    s_HH = sigma_HH_at_v(v_kms, sigma_0, a_slope, sigma_peak_HH_1)
    s_HL = sigma_HL_at_v(v_kms, sigma_0_HL, a_slope, sigma_peak_HL, v_HL, width_HL)
    s_LL = sigma_LL_at_v(v_kms, sigma_0_LL, a_slope)
    return f_H**2 * s_HH + 2 * f_H * f_L * s_HL + f_L**2 * s_LL


# ----- Load T207 prescription-mode fits from canonical result JSON -----

t207_path = REPO / "v0.3-prelim" / "data" / "results" / "t207_final_summary.json"
t207_data = json.loads(t207_path.read_text(encoding="utf-8"))

# Also load priored free fit (T207c)
priored_path = REPO / "v0.3-prelim" / "data" / "results" / "t207c_priored_free_emcee.json"
priored_data = json.loads(priored_path.read_text(encoding="utf-8"))

# SPARC observational target
SPARC_TARGET = 0.193  # cm^2/g
SPARC_SIGMA_UNC = 0.05  # cm^2/g (T205 published convention)


def log_L_SPARC(sigma_pred):
    """Compute SPARC log L = -0.5 * ((sigma_pred - 0.193) / 0.05)^2"""
    return -0.5 * ((sigma_pred - SPARC_TARGET) / SPARC_SIGMA_UNC) ** 2


# Paper's reported section 9.11 values for comparison
paper_reported = {
    "borrowed": {
        "log_L_paper": -0.09,
        "verdict_paper": "RESOLVED",
        "f_H_in_paper": 0.85,
    },
    "yang": {
        "log_L_paper": -0.24,
        "verdict_paper": "MARGINAL",
        "f_H_in_paper": 0.79,
    },
    "t202": {
        "log_L_paper": -0.60,
        "verdict_paper": "NOT RESOLVED",
        "f_H_in_paper": 0.92,
    },
    "priored free fit": {
        "log_L_paper": -2.03,
        "verdict_paper": "CLEAR FAIL",
        "f_H_in_paper": 0.06,  # priored f_H_cc value
    },
}


def compute_from_params(params, f_H_int=None):
    """Compute sigma_pred and log L given a best_params dict.

    If f_H_int is None, use the intermediate convention f_H_int = 0.5*(f_H_cf+f_H_cc).
    """
    if f_H_int is None:
        f_H_int = 0.5 * (params["f_H_cf"] + params["f_H_cc"])
    sigma_pred = sigma_eff_three_term(
        v_kms=100.0,
        f_H=f_H_int,
        sigma_0=params["sigma_0"],
        a_slope=params["a_slope"],
        sigma_peak_HH_1=params["sigma_peak_HH_1"],
        sigma_0_HL=params["sigma_0_HL"],
        sigma_peak_HL=params["sigma_peak_HL"],
        v_HL=params["v_HL"],
        sigma_0_LL=params["sigma_0_LL"],
    )
    return sigma_pred, log_L_SPARC(sigma_pred), f_H_int


def compute_prescription(name, prescription_entry):
    """Compute sigma_pred(v=100) and log L for a T207 prescription fit.

    For SPARC v=100 (halo_class='intermediate'), f_H_int = 0.5*(f_H_cf + f_H_cc).
    For core_forming channels (Cloud-9), use f_H_cf.
    For core_collapsed channels (UFD, dSph, Cluster), use f_H_cc.
    See T207_three_term_fit.py CHANNELS table.
    """
    params = prescription_entry["best_params"]
    f_H_cf = params["f_H_cf"]
    f_H_cc = params["f_H_cc"]
    # SPARC v=100 uses intermediate halo_class
    f_H = 0.5 * (f_H_cf + f_H_cc)
    sigma_pred = sigma_eff_three_term(
        v_kms=100.0,
        f_H=f_H,
        sigma_0=params["sigma_0"],
        a_slope=params["a_slope"],
        sigma_peak_HH_1=params["sigma_peak_HH_1"],
        sigma_0_HL=params["sigma_0_HL"],
        sigma_peak_HL=params["sigma_peak_HL"],
        v_HL=params["v_HL"],
        sigma_0_LL=params["sigma_0_LL"],
    )
    log_L = log_L_SPARC(sigma_pred)
    return sigma_pred, log_L, f_H


def compute_prescription_paper_fH(name, prescription_entry, f_H_paper):
    """Compute sigma_pred using the paper-reported f_H instead of the fit's f_H."""
    params = prescription_entry["best_params"]
    sigma_pred = sigma_eff_three_term(
        v_kms=100.0,
        f_H=f_H_paper,
        sigma_0=params["sigma_0"],
        a_slope=params["a_slope"],
        sigma_peak_HH_1=params["sigma_peak_HH_1"],
        sigma_0_HL=params["sigma_0_HL"],
        sigma_peak_HL=params["sigma_peak_HL"],
        v_HL=params["v_HL"],
        sigma_0_LL=params["sigma_0_LL"],
    )
    return sigma_pred, log_L_SPARC(sigma_pred)


# Compute for each prescription mode
results = {
    "method": "Layer 3 v19.0.3 -- real sigma_pred verification per rev192.docx Reviewer 1",
    "date": "2026-09-29",
    "note": (
        "Computes sigma_pred(v=100) from paper's three-term Path F1 model using "
        "T207 prescription-mode fitted parameters, then computes log L and "
        "compares to paper's reported per-channel log L values."
    ),
    "paper_verification": {},
    "verification_summary": {},
}

deltas = []

for name, prescription_entry in t207_data["t207_de_prescription_modes"].items():
    sigma_pred, log_L, f_H_used = compute_prescription(name, prescription_entry)
    paper = paper_reported[name]
    paper_per_channel_log_L = prescription_entry["per_channel_log_L"]["SPARC v=100"]
    delta_log_L = log_L - paper["log_L_paper"]

    f_H_paper = paper["f_H_in_paper"]
    sigma_pred_paper_fH, log_L_paper_fH = compute_prescription_paper_fH(
        name, prescription_entry, f_H_paper
    )

    results["paper_verification"][name] = {
        "f_H_int_used_for_SPARC": float(f_H_used),
        "f_H_cf_params": float(prescription_entry["best_params"]["f_H_cf"]),
        "f_H_cc_params": float(prescription_entry["best_params"]["f_H_cc"]),
        "f_H_paper_reported": paper["f_H_in_paper"],
        "sigma_pred_at_v100": float(sigma_pred),
        "log_L_at_v100": float(log_L),
        "sigma_pred_at_v100_paper_fH": float(sigma_pred_paper_fH),
        "log_L_at_v100_paper_fH": float(log_L_paper_fH),
        "log_L_paper_section_9_11": paper["log_L_paper"],
        "log_L_paper_per_channel_json": paper_per_channel_log_L,
        "delta_log_L_vs_9_11": float(delta_log_L),
    }
    deltas.append(abs(delta_log_L))

# Now add the priored free fit (from T207c emcee posterior median)
priored_params = priored_data["posterior_medians"]
sigma_pred_priored, log_L_priored, f_H_used_priored = compute_from_params(priored_params)
paper_per_channel_log_L_priored = priored_data["per_channel_log_L_at_median"]["SPARC v=100"]
paper_priored = paper_reported["priored free fit"]
delta_log_L_priored = log_L_priored - paper_priored["log_L_paper"]
results["paper_verification"]["priored free fit"] = {
    "f_H_int_used_for_SPARC": float(f_H_used_priored),
    "f_H_cf_params": float(priored_params["f_H_cf"]),
    "f_H_cc_params": float(priored_params["f_H_cc"]),
    "f_H_paper_reported": paper_priored["f_H_in_paper"],
    "sigma_pred_at_v100": float(sigma_pred_priored),
    "log_L_at_v100": float(log_L_priored),
    "log_L_paper_section_9_11": paper_priored["log_L_paper"],
    "log_L_paper_per_channel_json": paper_per_channel_log_L_priored,
    "delta_log_L_vs_9_11": float(delta_log_L_priored),
}
deltas.append(abs(delta_log_L_priored))

# Summary
results["verification_summary"] = {
    "n_prescriptions_checked": len(deltas),
    "max_delta_log_L": float(max(deltas)),
    "mean_delta_log_L": float(sum(deltas) / len(deltas)),
    "verifies_paper": max(deltas) < 0.05,  # within 0.05 log-units
    "interpretation": (
        "If max_delta_log_L < 0.05, the script reproduces the paper's reported "
        "section 9.11 SPARC v=100 per-channel log L values within 0.05 log-units. "
        "This is a TRUE verification (per rev192.docx Reviewer 1). If max_delta "
        "exceeds 0.05, there is a parameter-convention gap (likely the width_HL "
        "default = 50 km/s vs a per-prescription fitted width)."
    ),
}

out = Path(
    r"C:\Users\lamkuenai\projects\sidm-composite-dm-mediator\v0.3-prelim\data\results\jia2026_sparc_subset.json"
)
out.parent.mkdir(parents=True, exist_ok=True)
with open(out, "w") as f:
    json.dump(results, f, indent=2)
print(f"Saved: {out}")
print()
print(f"{'Prescription':22s} {'f_H_int':>8s} {'sigma_pred':>12s} {'log_L':>8s} {'paper_9_11':>11s} {'delta':>8s}")
for name, r in results["paper_verification"].items():
    log_L_paper = r['log_L_paper_section_9_11']
    print(
        f"  {name:20s} {r['f_H_int_used_for_SPARC']:>8.3f} {r['sigma_pred_at_v100']:>12.4f} "
        f"{r['log_L_at_v100']:>8.3f} {log_L_paper:>11.3f} "
        f"{r['delta_log_L_vs_9_11']:>8.3f}"
    )
print()
print(f"Max delta: {results['verification_summary']['max_delta_log_L']:.3f}")
print(f"Verifies paper (delta < 0.05): {results['verification_summary']['verifies_paper']}")
print(f"Interpretation: {results['verification_summary']['interpretation'][:200]}")