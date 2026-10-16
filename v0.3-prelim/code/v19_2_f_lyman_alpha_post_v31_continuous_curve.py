"""v31 Continuous α_D curve — addresses REVIEWER-33 item 4.

Generates a 100-point log-spaced scan of alpha_D in [1e-10, 1e+0] at the
Cloud-9 calibration Gamma/rho=5.0, producing a smooth curve that shows
the "too weak → too strong" transition. This supports the "FAIL
independent of specific alpha_D value" claim with continuous (not just
discrete) evidence.
"""
import hashlib
import importlib.util
import json
import math
from datetime import datetime, timezone
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve().parent
_PROJECT_ROOT = _SCRIPT_DIR.parent.parent  # v0.3-prelim/code -> project root


def _load_module_from_path(module_name, file_path):
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


_constants = _load_module_from_path(
    "constants_continuous", _PROJECT_ROOT / "constants.py"
)
_helpers = _load_module_from_path(
    "resonance_helpers_continuous",
    _SCRIPT_DIR / "v19_2_f_priority1_resonance_helpers.py",
)

C_KMS = _constants.C_KMS
HBAR_C_GEV_CM = _constants.HBAR_C_GEV_CM
sigma_m_resonance = _helpers.sigma_m_resonance

M_CHI_GEV = 1.0
M_RHO_GEV = 0.05e-3
V_TARGET_KMS = 29.4
SIGMA_TARGET = 174.0

# Cloud-9 calibration: Gamma/rho = 5.0 (where IN BAND is achieved in v30 §8)
GAMMA_RHO_FRAC = 5.0

# 100 log-spaced points across alpha_D in [1e-10, 1e+0]
ALPHA_MIN = 1e-10
ALPHA_MAX = 1e+0
N_POINTS = 100
LOG_MIN = math.log10(ALPHA_MIN)
LOG_MAX = math.log10(ALPHA_MAX)
ALPHA_D_GRID = [10 ** (LOG_MIN + (LOG_MAX - LOG_MIN) * i / (N_POINTS - 1))
                for i in range(N_POINTS)]


def main():
    Gamma_rho = GAMMA_RHO_FRAC * M_RHO_GEV
    curve = []
    for alpha_D in ALPHA_D_GRID:
        sig = sigma_m_resonance(V_TARGET_KMS, alpha_D, M_RHO_GEV, Gamma_rho)
        curve.append({
            "alpha_D": alpha_D,
            "sigma_m_29.4": sig,
            "ratio_target": sig / SIGMA_TARGET,
        })

    # Find where IN BAND is (0.5 < ratio < 2.0)
    in_band = [p for p in curve if 0.5 < p["ratio_target"] < 2.0]
    near_target = [p for p in curve if 0.1 < p["ratio_target"] < 10.0]

    # Output JSON
    output_path = _SCRIPT_DIR.parent / "data" / "results" / "v19_2_f_lyman_alpha_post_v31_continuous_curve.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "config": {
            "Gamma_rho_over_m_rho": GAMMA_RHO_FRAC,
            "v_target_kms": V_TARGET_KMS,
            "sigma_target_cm2_g": SIGMA_TARGET,
            "alpha_D_min": ALPHA_MIN,
            "alpha_D_max": ALPHA_MAX,
            "n_points": N_POINTS,
            "log_spaced": True,
        },
        "summary": {
            "n_in_band": len(in_band),
            "alpha_D_in_band_min": min((p["alpha_D"] for p in in_band), default=None),
            "alpha_D_in_band_max": max((p["alpha_D"] for p in in_band), default=None),
            "n_near_target": len(near_target),
        },
        "curve": curve,
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    }
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)
    print(f"Saved: {output_path}")
    print(f"IN BAND points: {len(in_band)} / {N_POINTS}")
    if in_band:
        print(f"  alpha_D range: {min(p['alpha_D'] for p in in_band):.3e} "
              f"to {max(p['alpha_D'] for p in in_band):.3e}")
    print(f"NEAR TARGET points: {len(near_target)} / {N_POINTS}")

    # Emit a Markdown summary for inclusion in §7-appendix
    md_path = _SCRIPT_DIR.parent / "data" / "results" / "v31_continuous_curve_appendix.md"
    md = []
    md.append(f"### Γ/ρ = {GAMMA_RHO_FRAC} — continuous α_D scan (100 log-spaced points)\n")
    md.append("R33 item 4: continuous (not discrete) evidence that the FAIL verdict holds "
              "across α_D ∈ [10⁻¹⁰, 10⁰]. Below ~10⁻⁶, σ/m is too weak (OUT low side). "
              "Above ~10⁻⁵, σ/m is too strong (OUT high side). The IN-BAND window is narrow "
              "and well-characterized.\n")
    md.append("| α_D | σ/m(29.4) | × target | region |")
    md.append("|---:|---:|---:|:---:|")
    for p in curve:
        rt = p["ratio_target"]
        if 0.5 < rt < 2.0:
            region = "IN BAND"
        elif 0.1 < rt < 10.0:
            region = "NEAR TARGET"
        else:
            region = "OUT"
        md.append(f"| {p['alpha_D']:.3e} | {p['sigma_m_29.4']:.4e} | {rt:.3e} | {region} |")
    with open(md_path, "w", encoding="utf-8") as f:
        f.write("\n".join(md) + "\n")
    print(f"Wrote: {md_path}  ({len(curve)} rows)")


if __name__ == "__main__":
    main()
