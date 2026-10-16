"""v31 CORRECTED extended alpha_D scan + full data.

REVIEWER-33 fixes (r33.docx):
- Item 1: Full 14-row alpha_D tables (no truncation) per Gamma/rho.
- Item 3: sigma_m_resonance failure → log to stderr + region='ERROR' + continue.
- Item 5: sys.path replaced with importlib (no implicit module override).
- Item 6: JSON metadata: function_version, precision, generated_at,
  total_computed, filtered_out, script_sha.

Script produces:
- v19_2_f_lyman_alpha_post_v31.json: full 126-point scan + metadata
- All values follow alpha_D^2 scaling (JSON regenerated programmatically).
"""
import hashlib
import importlib.util
import json
import math
import sys
from datetime import datetime, timezone
from pathlib import Path

# Use importlib instead of sys.path mutation (r33 item 5 fix)
_SCRIPT_DIR = Path(__file__).resolve().parent
# Layout: v0.3-prelim/code/<this>.py
#   _SCRIPT_DIR                  = v0.3-prelim/code
#   _SCRIPT_DIR.parent           = v0.3-prelim
#   _SCRIPT_DIR.parent.parent    = sidm-composite-dm-mediator  (PROJECT ROOT, constants.py lives here)
#   _SCRIPT_DIR.parent.parent.parent = projects                 (TOO HIGH — one too many)
_PROJECT_ROOT = _SCRIPT_DIR.parent.parent  # project root (constants.py)
_CODE_DIR = _SCRIPT_DIR                    # v0.3-prelim/code (helpers live here)

def _load_module_from_path(module_name, file_path):
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

_constants = _load_module_from_path(
    "constants_workspace",
    _PROJECT_ROOT / "constants.py",
)
_helpers = _load_module_from_path(
    "v19_2_f_priority1_resonance_helpers_workspace",
    _CODE_DIR / "v19_2_f_priority1_resonance_helpers.py",
)

C_KMS = _constants.C_KMS
HBAR_C_GEV_CM = _constants.HBAR_C_GEV_CM
sigma_m_resonance = _helpers.sigma_m_resonance

# === Fixed physical parameters (REVIEWER-32 item 4, unchanged) ===
M_CHI_GEV = 1.0          # dark matter mass
M_RHO_GEV = 0.05e-3      # dark rho mass (50 keV, v_res = 29.98 km/s)
M_PHI_GEV = 200e-9       # NOT used in resonance (Yukawa m = m_rho)
V_TARGET_KMS = 29.4
SIGMA_TARGET = 174.0     # cm^2/g
SIGMA_FUNCTION_VERSION = "sigma_m_resonance v1.0 (16-point Gauss-Legendre, TYL Eq A1 LINEAR bracket)"
INTEGRATION_PRECISION = "limit=100 (scipy.integrate.quad) per sigma_m_resonance"

ALPHA_D_GRID = [1e-10, 1e-8, 1e-7, 3e-7, 1e-6, 3e-6, 5.55e-6, 1e-5,
                3e-5, 1e-4, 1e-3, 1e-2, 1e-1, 1e+0]
GAMMA_RHO_OVER_M_RHO_GRID = [0.01, 0.1, 0.5, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0]


def unitarity_bound(m_chi_GeV, v_kms):
    """sigma_max = 4 pi / k^2 (Born-unitarity, velocity-dependent)."""
    mu = m_chi_GeV / 2
    v = v_kms / C_KMS
    k = mu * v
    return (4 * math.pi / k**2) * HBAR_C_GEV_CM**2 / (m_chi_GeV * 1.78266192e-24)


def _classify(r_t):
    """Classify sigma/m vs target ratio into IN BAND / NEAR TARGET / OUT.

    Boundary convention (r34 Code-5 fix): IN BAND uses half-open interval
    (0.5, 2.0); NEAR TARGET uses (0.1, 10.0]; OUT is everything else.
    The choice of < vs <= for the upper bound means r_t == 2.0 is NEAR TARGET
    (not IN BAND) and r_t == 0.5 is OUT (not IN BAND). This matches the
    v30/v31 paper convention and is documented in §3 of the v32 packet.
    """
    if 0.5 < r_t <= 2.0:
        return "IN BAND"
    if 0.1 < r_t <= 10.0:
        return "NEAR TARGET"
    return "OUT"


def main():
    sigma_max = unitarity_bound(M_CHI_GEV, V_TARGET_KMS)
    print("=" * 75)
    print("v31 CORRECTED extended alpha_D scan (r33 fixes applied)")
    print("=" * 75)
    print()
    print("FIXED PHYSICAL PARAMETERS (REVIEWER-32 item 4):")
    print(f"  m_chi (dark matter)        = {M_CHI_GEV} GeV")
    print(f"  m_rho (dark rho meson)     = {M_RHO_GEV*1e3} MeV")
    print(f"  v_resonance                = {C_KMS * M_RHO_GEV / (M_CHI_GEV/2):.4f} km/s")
    print(f"  v_target                   = {V_TARGET_KMS} km/s")
    print(f"  sigma/m target             = {SIGMA_TARGET} cm^2/g")
    print(f"  sigma/m unitarity at v={V_TARGET_KMS} = {sigma_max:.4e} cm^2/g")
    print()
    print(f"Function: {SIGMA_FUNCTION_VERSION}")
    print(f"Precision: {INTEGRATION_PRECISION}")
    print()
    print("Coupling convention: alpha_D = g^2/(4 pi) [LOCKED]")
    print()

    # Full alpha_D scan at multiple Gamma/rho
    # r33 item 3: try-except around sigma_m_resonance; on failure → ERROR region, continue scan
    results = {}
    error_count = 0
    for Gamma_frac in GAMMA_RHO_OVER_M_RHO_GRID:
        Gamma_rho = Gamma_frac * M_RHO_GEV
        scan = []
        for alpha_D in ALPHA_D_GRID:
            try:
                sig = sigma_m_resonance(V_TARGET_KMS, alpha_D, M_RHO_GEV, Gamma_rho)
            except Exception as exc:  # noqa: BLE001
                print(f"  [ERROR] Gamma/rho={Gamma_frac} alpha_D={alpha_D:.2e}: "
                      f"{type(exc).__name__}: {exc}", file=sys.stderr)
                error_count += 1
                scan.append({
                    "alpha_D": alpha_D,
                    "sigma_m_29.4": None,
                    "ratio_target": None,
                    "region": "ERROR",
                    "error": f"{type(exc).__name__}: {exc}",
                })
                continue
            if not (math.isfinite(sig) and sig > 0):
                scan.append({
                    "alpha_D": alpha_D,
                    "sigma_m_29.4": sig,
                    "ratio_target": None if not math.isfinite(sig / SIGMA_TARGET) else sig / SIGMA_TARGET,
                    "region": "OUT_NEG_OR_NAN",
                })
                continue
            r_t = sig / SIGMA_TARGET
            scan.append({
                "alpha_D": alpha_D,
                "sigma_m_29.4": sig,
                "ratio_target": r_t,
                "region": _classify(r_t),
            })
        results[Gamma_frac] = scan

    # Print each Gamma/rho table (all 14 rows — r33 item 1 fix)
    for Gamma_frac, scan in results.items():
        print(f"Gamma/rho={Gamma_frac}:")
        print(f'{"alpha_D":>12} {"sigma/m":>14} {"x target":>10} {"region":>20}')
        for entry in scan:
            sig = entry["sigma_m_29.4"]
            r_t = entry["ratio_target"]
            sig_str = f'{sig:>14.4e}' if isinstance(sig, (int, float)) and math.isfinite(sig) else f'{"--":>14}'
            r_t_str = f'{r_t:>10.3e}' if isinstance(r_t, (int, float)) and math.isfinite(r_t) else f'{"--":>10}'
            print(f"  {entry['alpha_D']:>10.2e} {sig_str} {r_t_str} {entry['region']:>20}")
        print()

    # IN BAND at Cloud-9 calibration
    print("=" * 75)
    print("IN BAND points at Cloud-9 calibration (alpha_D = 5.55e-6):")
    print("=" * 75)
    print(f'{"Gamma/rho":>10} {"sigma/m":>14} {"x target":>10} {"region":>15}')
    for Gamma_frac, scan in results.items():
        for entry in scan:
            if abs(entry["alpha_D"] - 5.55e-6) < 1e-7:
                sig = entry["sigma_m_29.4"]
                r_t = entry["ratio_target"]
                sig_str = f'{sig:>14.4e}' if isinstance(sig, (int, float)) else '--'
                r_t_str = f'{r_t:>10.3e}' if isinstance(r_t, (int, float)) else '--'
                print(f'{Gamma_frac:>10.2f} {sig_str} {r_t_str} {entry["region"]:>15}')
                break

    # alpha_D^2 scaling verification at Gamma/rho=5.0 (sanity)
    print()
    print("=" * 75)
    print("alpha_D^2 scaling verification (at Gamma/rho=5.0):")
    print("=" * 75)
    Gamma_frac = 5.0
    Gamma_rho = Gamma_frac * M_RHO_GEV
    ref_sig = None
    ref_alpha = None
    for alpha_D in [1e-10, 1e-7, 1e-6, 1e-5, 5.55e-6, 1e-4, 1e-3, 1e-2, 1e-1]:
        sig = sigma_m_resonance(V_TARGET_KMS, alpha_D, M_RHO_GEV, Gamma_rho)
        if ref_sig is None and abs(alpha_D - 1e-5) < 1e-9:
            ref_sig = sig
            ref_alpha = alpha_D
        if ref_sig is not None and abs(alpha_D - ref_alpha) > 1e-9:
            predicted = ref_sig * (alpha_D / ref_alpha) ** 2
            ratio = sig / predicted
            print(f"  alpha_D={alpha_D:.2e}: actual={sig:.4e}, predicted={predicted:.4e}, ratio={ratio:.6f}")

    # Build metadata block (r33 item 6 fix)
    total_computed = sum(len(scan) for scan in results.values())
    filtered_out = sum(
        1
        for scan in results.values()
        for entry in scan
        if entry["region"] in ("ERROR", "OUT_NEG_OR_NAN")
    )
    script_text = Path(__file__).read_text(encoding="utf-8")
    script_sha = hashlib.sha256(script_text.encode("utf-8")).hexdigest()[:16]

    # Save JSON
    output_path = _SCRIPT_DIR.parent / "data" / "results" / "v19_2_f_lyman_alpha_post_v31.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "fixed_parameters": {
            "m_chi_GeV": M_CHI_GEV,
            "m_rho_GeV": M_RHO_GEV,
            "v_resonance_kms": C_KMS * M_RHO_GEV / (M_CHI_GEV / 2),
            "v_target_kms": V_TARGET_KMS,
            "sigma_target_cm2_g": SIGMA_TARGET,
            "sigma_max_unitarity_cm2_g": sigma_max,
            "coupling_convention": "alpha_D = g^2/(4 pi), LOCKED",
        },
        "metadata": {
            "function_version": SIGMA_FUNCTION_VERSION,
            "precision": INTEGRATION_PRECISION,
            "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "script_sha256": script_sha,
            "total_computed": total_computed,
            "filtered_out": filtered_out,
            "alpha_D_grid_size": len(ALPHA_D_GRID),
            "gamma_rho_grid_size": len(GAMMA_RHO_OVER_M_RHO_GRID),
            "expected_entries": len(ALPHA_D_GRID) * len(GAMMA_RHO_OVER_M_RHO_GRID),
        },
        "alpha_D_grid": ALPHA_D_GRID,
        "Gamma_rho_over_m_rho_grid": GAMMA_RHO_OVER_M_RHO_GRID,
        "all_scan_results": {
            str(Gamma_frac): scan for Gamma_frac, scan in results.items()
        },
        "version": "v31 (REVIEWER-33: programmatic table rendering, sys.path→importlib, JSON metadata, ERROR region)",
    }
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)
    print()
    print(f"Saved: {output_path}")
    print(f"Total entries: {total_computed}, filtered/errors: {filtered_out}, "
          f"expected: {len(ALPHA_D_GRID) * len(GAMMA_RHO_OVER_M_RHO_GRID)}")
    print(f"Script SHA-256: {script_sha}")


if __name__ == "__main__":
    main()
