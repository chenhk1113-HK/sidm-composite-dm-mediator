"""v33 Multi-Gamma/rho continuous alpha_D curves — REVIEWER-35 fix.

GENERATES: 9 Gamma/rho x 100 alpha_D = 900 points (full coverage of v31 discrete grid).
REPLACES: v32 multi-curve which only covered 4 of 9 Gamma/rho values.

Key finding: IN BAND exists at all 9 tested Gamma/rho values, but the alpha_D
range required shifts to lower values as Gamma/rho decreases. At the Cloud-9
specific alpha_D = 5.55e-6, only Gamma/rho = 5.0 and 6.0 are IN BAND. This
preserves the Cloud-9 verdict (Phase 3 FAIL) while correcting the v32
overgeneralization that "IN BAND only at Gamma/rho=5.0/6.0".
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
    "constants_v33", _PROJECT_ROOT / "constants.py"
)
_helpers = _load_module_from_path(
    "resonance_helpers_v33",
    _SCRIPT_DIR / "v19_2_f_priority1_resonance_helpers.py",
)

C_KMS = _constants.C_KMS
HBAR_C_GEV_CM = _constants.HBAR_C_GEV_CM
sigma_m_resonance = _helpers.sigma_m_resonance

M_CHI_GEV = 1.0
M_RHO_GEV = 0.05e-3
V_TARGET_KMS = 29.4
SIGMA_TARGET = 174.0

# v33 fix: full coverage of v31 discrete grid
GAMMA_RHO_FRACS = [0.01, 0.1, 0.5, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0]

ALPHA_MIN = 1e-10
ALPHA_MAX = 1e+0
N_POINTS = 100
LOG_MIN = math.log10(ALPHA_MIN)
LOG_MAX = math.log10(ALPHA_MAX)
ALPHA_D_GRID = [10 ** (LOG_MIN + (LOG_MAX - LOG_MIN) * i / (N_POINTS - 1))
                for i in range(N_POINTS)]


def _classify(r_t):
    # v32 boundary (r34 Code-5): half-open (0.5, 2.0]
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

    # Build summary
    summary = {}
    for gamma_frac, curve in results.items():
        in_band = [p for p in curve if p["region"] == "IN BAND"]
        near = [p for p in curve if p["region"] == "NEAR TARGET"]
        # Check if Cloud-9 alpha_D is in the IN BAND range
        cloud9_in_in_band = False
        cloud9_in_near = False
        if in_band:
            lo, hi = min(p["alpha_D"] for p in in_band), max(p["alpha_D"] for p in in_band)
            cloud9_in_in_band = lo <= 5.55e-6 <= hi
        if near:
            lo, hi = min(p["alpha_D"] for p in near), max(p["alpha_D"] for p in near)
            cloud9_in_near = lo <= 5.55e-6 <= hi
        summary[gamma_frac] = {
            "n_in_band": len(in_band),
            "alpha_D_in_band_min": min((p["alpha_D"] for p in in_band), default=None),
            "alpha_D_in_band_max": max((p["alpha_D"] for p in in_band), default=None),
            "n_near_target": len(near),
            "alpha_D_near_min": min((p["alpha_D"] for p in near), default=None),
            "alpha_D_near_max": max((p["alpha_D"] for p in near), default=None),
            "cloud9_in_in_band": cloud9_in_in_band,
            "cloud9_in_near_target": cloud9_in_near,
        }

    # JSON output
    output_path = _SCRIPT_DIR.parent / "data" / "results" / "v19_2_f_lyman_alpha_post_v33_full_multi_curve.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "config": {
            "v_target_kms": V_TARGET_KMS,
            "sigma_target_cm2_g": SIGMA_TARGET,
            "alpha_D_min": ALPHA_MIN,
            "alpha_D_max": ALPHA_MAX,
            "n_points": N_POINTS,
            "gamma_rho_fracs": GAMMA_RHO_FRACS,
            "total_points": len(GAMMA_RHO_FRACS) * N_POINTS,
        },
        "summary": summary,
        "curves": results,
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    }
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)
    print(f"Saved: {output_path}")

    # Markdown appendix
    md_path = _SCRIPT_DIR.parent / "data" / "results" / "v33_full_multi_curve_appendix.md"
    md = []
    md.append("## v33 Full multi-Γ/ρ continuous α_D curves (r35 Sci-2 fix)\n")
    md.append(f"9 Γ/ρ × 100 α_D = {len(GAMMA_RHO_FRACS) * N_POINTS} points. **Comprehensive coverage** "
              "of the v31 discrete grid (r35 Sci-2: previous v32 only covered 4 of 9 Γ/ρ).\n")
    md.append("### Summary: IN BAND windows and Cloud-9 inclusion\n")
    md.append("| Γ/ρ | IN BAND count | α_D IN BAND range | Cloud-9 in IN BAND? | NEAR TARGET α_D range |")
    md.append("|---:|---:|:---|:---:|:---|")
    for gamma_frac in GAMMA_RHO_FRACS:
        s = summary[gamma_frac]
        in_range = f"{s['alpha_D_in_band_min']:.2e} – {s['alpha_D_in_band_max']:.2e}" if s['n_in_band'] else "—"
        near_range = f"{s['alpha_D_near_min']:.2e} – {s['alpha_D_near_max']:.2e}" if s['n_near_target'] else "—"
        cloud9_str = "✓" if s['cloud9_in_in_band'] else "✗"
        md.append(f"| {gamma_frac} | {s['n_in_band']} | {in_range} | {cloud9_str} | {near_range} |")

    md.append("\n### Conclusion (r35 Sci-4 corrected)\n")
    md.append("At the **Cloud-9 α_D = 5.55e-6 specifically**, only Γ/ρ = 5.0 and 6.0 are IN BAND. "
              "All other Γ/ρ values have IN BAND windows at α_D values BELOW Cloud-9. "
              "**The Phase 3 FAIL verdict at the Cloud-9 calibration is preserved.** "
              "The corrected claim (weaker than v32's): "
              "*IN BAND exists at all 9 tested Γ/ρ values, but the α_D range required shifts to "
              "lower values as Γ/ρ decreases. The Cloud-9 calibration falls in the IN BAND "
              "window only for the two widest widths (Γ/ρ = 5.0 and 6.0).*\n")
    md.append("\nThis pattern is consistent with a Breit-Wigner resonance formula where the "
              "resonance width Γ_ρ sets the coupling strength scaling: at fixed α_D, "
              "narrower Γ_ρ gives stronger cross-sections (over-unity σ/m, OUT above target), "
              "wider Γ_ρ gives weaker cross-sections. The Cloud-9 α_D corresponds to the "
              "transition between these regimes for Γ/ρ ∈ {5, 6}.\n")
    md.append("\n### Full curves (every 10th point to keep readable)\n")
    for gamma_frac in GAMMA_RHO_FRACS:
        curve = results[gamma_frac]
        md.append(f"\n#### Γ/ρ = {gamma_frac}\n")
        md.append("| α_D | σ/m(29.4) | × target | region |")
        md.append("|---:|---:|---:|:---:|")
        for p in curve[::10]:
            md.append(f"| {p['alpha_D']:.3e} | {p['sigma_m_29.4']:.4e} | "
                      f"{p['ratio_target']:.3e} | {p['region']} |")

    with open(md_path, "w", encoding="utf-8") as f:
        f.write("\n".join(md) + "\n")
    print(f"Wrote: {md_path}")

    # Print summary table
    print()
    print("Summary (Cloud-9 alpha_D = 5.55e-6 in IN BAND window?):")
    for gamma_frac in GAMMA_RHO_FRACS:
        s = summary[gamma_frac]
        in_range = f"[{s['alpha_D_in_band_min']:.2e}, {s['alpha_D_in_band_max']:.2e}]" if s['n_in_band'] else "none"
        cloud9_str = "YES" if s['cloud9_in_in_band'] else "no"
        print(f"  Gamma/rho={gamma_frac}: IN BAND = {s['n_in_band']} pts in {in_range}, "
              f"Cloud-9 in: {cloud9_str}")


if __name__ == "__main__":
    main()
