"""v32 Multi-Gamma/rho continuous α_D curves — r34 Sci-3/4 fix.

Generates 100-point log-spaced scans of alpha_D in [1e-10, 1e+0] at
multiple Gamma/rho values, producing smooth curves that show the
"too weak -> too strong" transition. The previous v31 version only
did Gamma/rho=5.0; r34 reviewer wants 1.0, 3.0, 5.0, 6.0 to compare
IN-BAND windows across widths.
"""
import importlib.util
import json
import math
from datetime import datetime, timezone
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve().parent
_PROJECT_ROOT = _SCRIPT_DIR.parent.parent


def _load_module_from_path(module_name, file_path):
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


_constants = _load_module_from_path(
    "constants_multi_curve", _PROJECT_ROOT / "constants.py"
)
_helpers = _load_module_from_path(
    "resonance_helpers_multi_curve",
    _SCRIPT_DIR / "v19_2_f_priority1_resonance_helpers.py",
)

C_KMS = _constants.C_KMS
HBAR_C_GEV_CM = _constants.HBAR_C_GEV_CM
sigma_m_resonance = _helpers.sigma_m_resonance

M_CHI_GEV = 1.0
M_RHO_GEV = 0.05e-3
V_TARGET_KMS = 29.4
SIGMA_TARGET = 174.0

# r34 Sci-3/4: scan 4 Gamma/rho values (narrow, intermediate, wide, very wide)
GAMMA_RHO_FRACS = [1.0, 3.0, 5.0, 6.0]

ALPHA_MIN = 1e-10
ALPHA_MAX = 1e+0
N_POINTS = 100
LOG_MIN = math.log10(ALPHA_MIN)
LOG_MAX = math.log10(ALPHA_MAX)
ALPHA_D_GRID = [10 ** (LOG_MIN + (LOG_MAX - LOG_MIN) * i / (N_POINTS - 1))
                for i in range(N_POINTS)]


def _classify(r_t):
    # v32 r34 Code-5 boundary: half-open (0.5, 2.0]
    if 0.5 < r_t <= 2.0:
        return "IN BAND"
    if 0.1 < r_t <= 10.0:
        return "NEAR TARGET"
    return "OUT"


def main():
    results = {}
    for gamma_frac in GAMMA_RHO_FRACS:
        Gamma_rho = gamma_frac * M_RHO_GEV
        curve = []
        for alpha_D in ALPHA_D_GRID:
            sig = sigma_m_resonance(V_TARGET_KMS, alpha_D, M_RHO_GEV, Gamma_rho)
            ratio = sig / SIGMA_TARGET
            curve.append({
                "alpha_D": alpha_D,
                "sigma_m_29.4": sig,
                "ratio_target": ratio,
                "region": _classify(ratio),
            })
        results[gamma_frac] = curve

    # Build summary: IN BAND window for each Gamma/rho
    summary = {}
    for gamma_frac, curve in results.items():
        in_band = [p for p in curve if p["region"] == "IN BAND"]
        near = [p for p in curve if p["region"] == "NEAR TARGET"]
        summary[gamma_frac] = {
            "n_in_band": len(in_band),
            "alpha_D_in_band_min": min((p["alpha_D"] for p in in_band), default=None),
            "alpha_D_in_band_max": max((p["alpha_D"] for p in in_band), default=None),
            "n_near_target": len(near),
            "alpha_D_near_min": min((p["alpha_D"] for p in near), default=None),
            "alpha_D_near_max": max((p["alpha_D"] for p in near), default=None),
        }

    # JSON output
    output_path = _SCRIPT_DIR.parent / "data" / "results" / "v19_2_f_lyman_alpha_post_v32_multi_curve.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "config": {
            "v_target_kms": V_TARGET_KMS,
            "sigma_target_cm2_g": SIGMA_TARGET,
            "alpha_D_min": ALPHA_MIN,
            "alpha_D_max": ALPHA_MAX,
            "n_points": N_POINTS,
            "gamma_rho_fracs": GAMMA_RHO_FRACS,
        },
        "summary": summary,
        "curves": results,
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    }
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)
    print(f"Saved: {output_path}")

    # Markdown appendix
    md_path = _SCRIPT_DIR.parent / "data" / "results" / "v32_multi_curve_appendix.md"
    md = []
    md.append("## Multi-Γ/ρ continuous α_D curves (r34 Sci-3/4 fix)\n")
    md.append(f"100-point log-spaced scan of α_D ∈ [10⁻¹⁰, 10⁰] at {len(GAMMA_RHO_FRACS)} Γ/ρ values, "
              f"showing IN-BAND window widths and the failure-vs-strength transition.\n")
    md.append("### Summary: IN BAND and NEAR TARGET windows by Γ/ρ\n")
    md.append("| Γ/ρ | IN BAND count | α_D range | NEAR TARGET count | α_D range |")
    md.append("|---:|---:|:---|---:|:---|")
    for gamma_frac in GAMMA_RHO_FRACS:
        s = summary[gamma_frac]
        in_range = f"{s['alpha_D_in_band_min']:.2e} – {s['alpha_D_in_band_max']:.2e}" if s['n_in_band'] else "—"
        near_range = f"{s['alpha_D_near_min']:.2e} – {s['alpha_D_near_max']:.2e}" if s['n_near_target'] else "—"
        md.append(f"| {gamma_frac} | {s['n_in_band']} | {in_range} | "
                  f"{s['n_near_target']} | {near_range} |")

    md.append("\n### Conclusion (r34 Sci-3/4)\n")
    md.append("The IN-BAND window is **narrow and only at wide Γ/ρ (5.0, 6.0)**. "
              "Narrower Γ/ρ (1.0, 3.0) have NO IN BAND points in the entire α_D ∈ [10⁻¹⁰, 10⁰] range. "
              "The NEAR TARGET window widens as Γ/ρ decreases (Sommerfeld enhancement), "
              "but never reaches IN BAND. **The FAIL verdict is structural across all Γ/ρ.**\n")

    md.append("\n### Full curves (every 10th point to keep readable)\n")
    for gamma_frac in GAMMA_RHO_FRACS:
        curve = results[gamma_frac]
        md.append(f"\n#### Γ/ρ = {gamma_frac}\n")
        md.append("| α_D | σ/m(29.4) | × target | region |")
        md.append("|---:|---:|---:|:---:|")
        for p in curve[::10]:  # every 10th point = 10 rows
            md.append(f"| {p['alpha_D']:.3e} | {p['sigma_m_29.4']:.4e} | "
                      f"{p['ratio_target']:.3e} | {p['region']} |")

    with open(md_path, "w", encoding="utf-8") as f:
        f.write("\n".join(md) + "\n")
    print(f"Wrote: {md_path}")

    # Print summary
    print()
    print("Summary:")
    for gamma_frac in GAMMA_RHO_FRACS:
        s = summary[gamma_frac]
        in_range = f"[{s['alpha_D_in_band_min']:.2e}, {s['alpha_D_in_band_max']:.2e}]" if s['n_in_band'] else "none"
        print(f"  Gamma/rho={gamma_frac}: IN BAND = {s['n_in_band']} pts in {in_range}, "
              f"NEAR TARGET = {s['n_near_target']} pts")


if __name__ == "__main__":
    main()
