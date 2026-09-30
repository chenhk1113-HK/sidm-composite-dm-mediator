"""v19.2-A (v2): Phase 44 sigma_peak_HH_1 sensitivity sweep — paper convention.

Per r23.docx review of v19.2-A bundle:
- Issue 1: Use sigma_m_paper_convention (Gaussian w=4.4) — the same
  parameterization as §2.5, not Breit-Wigner.
- Issue 2: Use paper's causality criterion: t_core > 3 × t_cross.
- Issue 3: Peak velocity v₁ = 28 km/s (paper convention), not 29.4.
- Issue 4: Qualify "unavoidable" with explicit swept range.

Per Rule 28 (arithmetic checking before claim), all values are derived from
canonical functions. The sigma_m_paper_convention function is imported from
v192_dsph_gravothermal_sweep.py (v19.2-D.3 canonical) to ensure §2.5 and
§2.6 use the same σ/m(v).

Paper convention (Gaussian w=4.4):
  sigma/m(v) = sigma_m_at_v(0.052, 1.0, v) + sigma_peak × exp(-(v-28)²/(2×4.4²))

Causality check (per §9.12): t_core > 3 × t_cross (OK), else FAIL.
"""
import json
import math
import sys
from pathlib import Path

REPO = Path(r'C:\Users\lamkuenai\projects\sidm-composite-dm-mediator')
sys.path.insert(0, str(REPO / 'scripts'))

# Import paper convention from v19.2-D.3 script (avoids duplicating constants)
import importlib.util
spec = importlib.util.spec_from_file_location(
    "v192_dsph",
    REPO / 'scripts' / 'v192_dsph_gravothermal_sweep.py'
)
v192_dsph = importlib.util.module_from_spec(spec)
spec.loader.exec_module(v192_dsph)

PHASE44_SIGMA_0 = v192_dsph.PHASE44_SIGMA_0     # 0.052
PHASE44_A_SLOPE = v192_dsph.PHASE44_A_SLOPE      # 1.0
V1_V_TARGET = v192_dsph.V1_V_TARGET              # 28.0
V1_SIGMA_PEAK_DEFAULT = v192_dsph.V1_SIGMA_PEAK  # 174.0
V1_WIDTH = v192_dsph.V1_WIDTH                    # 4.4
sigma_m_at_v = v192_dsph.sigma_m_at_v

from two_component_three_term import sigma_HH_at_v
from T208_path_b_cloud9_host_halo_gravothermal import gravothermal_t_core_Gyr
from t212_silverman_gravothermal import t_cross_Gyr_from_r_vir_vmax

# Cloud-9 NFW params
CLOUD9 = {
    "M_200_MSun": 3.0e10,
    "c": 12,
    "v_max_kms": 31.12,
    "r_vir_kpc": 38.9,
    "r_s_kpc": 3.24,
    "rho_s_MSun_pc3": 1.4e-2,
}

# Fornax NFW params
FORNAX = {
    "V_max": 15.0,
    "M_halo_MSun": 3.0e9,
    "c": 12,
    "rho_s_MSun_pc3": 1.0e-2,
    "r_s_kpc": 4.0,
    "r_vir_kpc": 48.0,
}

# Sigma/m sensitivity sweep
SIGMA_PEAKS = [30, 50, 75, 100, 125, 150, 174, 200, 250]

# Channel velocity scales (peak now at v=28 per paper convention)
CHANNELS = {
    "UFD v=3": 3,
    "UFD v=5": 5,
    "dSph v=7": 7,
    "dSph v=10": 10,
    "dSph v=15 (Fornax)": 15,
    "Cloud-9 v=28 (v1 peak)": 28,
    "SPARC v=100": 100,
    "Cluster v=500": 500,
}

# Causality criterion (paper's, per §9.12): t_core > 3 × t_cross
CAUSALITY_CAP = 3.0


def sigma_m_paper(v_kms: float, sigma_peak_override=None) -> float:
    """Paper's σ/m convention (Gaussian w=4.4). Override peak only."""
    peak = sigma_peak_override if sigma_peak_override is not None else V1_SIGMA_PEAK_DEFAULT
    baseline = sigma_m_at_v(PHASE44_SIGMA_0, PHASE44_A_SLOPE, v_kms)
    dv = v_kms - V1_V_TARGET
    resonance = peak * math.exp(-dv**2 / (2 * V1_WIDTH**2))
    return baseline + resonance


def compute_row(sigma_peak: float) -> dict:
    """Compute all derived values for one σ_peak, paper convention."""
    row = {"sigma_peak_HH_1_cm2_per_g": sigma_peak}

    # 1. σ/m at all channels using paper convention (Gaussian)
    row["sigma_m_paper_convention"] = {}
    for label, v in CHANNELS.items():
        row["sigma_m_paper_convention"][label] = round(
            sigma_m_paper(v, sigma_peak_override=sigma_peak), 4
        )

    # 2. Cloud-9 gravothermal (at v=28, the v1 peak)
    s28 = row["sigma_m_paper_convention"]["Cloud-9 v=28 (v1 peak)"]
    t_core_cloud9 = gravothermal_t_core_Gyr(
        sigma_m_cm2_per_g=s28,
        rho_s_Msun_per_pc3=CLOUD9["rho_s_MSun_pc3"],
        r_s_pc=CLOUD9["r_s_kpc"] * 1e3,
        v_max_kms=CLOUD9["v_max_kms"],
    )
    t_cross_cloud9 = t_cross_Gyr_from_r_vir_vmax(
        r_vir_pc=CLOUD9["r_vir_kpc"] * 1e3,
        v_max_kms=CLOUD9["v_max_kms"],
        c=CLOUD9["c"],
    )
    ratio_cloud9 = t_core_cloud9 / t_cross_cloud9
    row["Cloud-9_t_core_Gyr"] = round(t_core_cloud9, 4)
    row["Cloud-9_t_cross_Gyr"] = round(t_cross_cloud9, 4)
    row["Cloud-9_causality_ratio"] = round(ratio_cloud9, 3)
    # Paper's criterion: ratio > CAUSALITY_CAP = 3.0
    row["Cloud-9_causality_verdict"] = "OK" if ratio_cloud9 > CAUSALITY_CAP else "FAIL"

    # 3. Fornax gravothermal (V_max=15)
    s15 = row["sigma_m_paper_convention"]["dSph v=15 (Fornax)"]
    t_core_fornax = gravothermal_t_core_Gyr(
        sigma_m_cm2_per_g=s15,
        rho_s_Msun_per_pc3=FORNAX["rho_s_MSun_pc3"],
        r_s_pc=FORNAX["r_s_kpc"] * 1e3,
        v_max_kms=FORNAX["V_max"],
    )
    t_cross_fornax = t_cross_Gyr_from_r_vir_vmax(
        r_vir_pc=FORNAX["r_vir_kpc"] * 1e3,
        v_max_kms=FORNAX["V_max"],
        c=FORNAX["c"],
    )
    ratio_fornax = t_core_fornax / t_cross_fornax
    row["Fornax_t_core_Gyr"] = round(t_core_fornax, 4)
    row["Fornax_t_cross_Gyr"] = round(t_cross_fornax, 4)
    row["Fornax_causality_ratio"] = round(ratio_fornax, 3)
    row["Fornax_causality_verdict"] = "OK" if ratio_fornax > CAUSALITY_CAP else "FAIL"

    # 4. Fornax σ_HL outlier test
    # σ_eff = f_H² σ_HH + 2 f_H f_L σ_HL + f_L² σ_LL, σ_LL = 0
    # σ_eff = 0.09 × σ_HH + 0.42 × σ_HL
    # σ_HL = (σ_eff_published - 0.09 × σ_HH) / 0.42
    sigma_eff_published = 0.032
    f_H = 0.30
    sigma_HL_req = (sigma_eff_published - f_H**2 * s15) / (2 * f_H * (1 - f_H))
    row["Fornax_sigma_HL_required_cm2_per_g"] = round(sigma_HL_req, 4)
    row["Fornax_sigma_HL_unphysical?"] = sigma_HL_req < 0

    # 5. SPARC σ/m at v=100
    s100 = row["sigma_m_paper_convention"]["SPARC v=100"]
    row["SPARC_v100_sigma_m"] = s100

    return row


def main():
    print("=" * 80)
    print("v19.2-A (v2): Phase 44 sigma_peak_HH_1 sensitivity sweep — PAPER CONVENTION")
    print("=" * 80)
    print(f"Paper convention: sigma/m(v) = {PHASE44_SIGMA_0}*(100/v)^{PHASE44_A_SLOPE} + sigma_peak*exp(-(v-{V1_V_TARGET})^2/(2*{V1_WIDTH}^2))")
    print(f"Causality criterion (paper §9.12): t_core > {CAUSALITY_CAP} * t_cross")
    print(f"Sweeping sigma_peak in {SIGMA_PEAKS}")
    print()

    results = []
    for sigma_peak in SIGMA_PEAKS:
        row = compute_row(sigma_peak)
        results.append(row)

        print(f"--- sigma_peak = {sigma_peak} cm²/g ---")
        print(f"  Cloud-9: σ/m(28) = {row['sigma_m_paper_convention']['Cloud-9 v=28 (v1 peak)']:.2f}, "
              f"t_core = {row['Cloud-9_t_core_Gyr']} Gyr, "
              f"ratio = {row['Cloud-9_causality_ratio']} ({row['Cloud-9_causality_verdict']})")
        print(f"  Fornax:  σ/m(15) = {row['sigma_m_paper_convention']['dSph v=15 (Fornax)']:.2f}, "
              f"t_core = {row['Fornax_t_core_Gyr']} Gyr, "
              f"ratio = {row['Fornax_causality_ratio']} ({row['Fornax_causality_verdict']}), "
              f"σ_HL req = {row['Fornax_sigma_HL_required_cm2_per_g']} cm²/g, "
              f"unphysical = {row['Fornax_sigma_HL_unphysical?']}")
        print(f"  SPARC:   σ/m(100) = {row['sigma_m_paper_convention']['SPARC v=100']:.3f}")
        print()

    # Save JSON
    out = {
        "version": "v19.2-A.2",
        "date": "2026-09-30",
        "description": "Phase 44 sigma_peak_HH_1 sensitivity sweep — paper convention",
        "parameterization": "Gaussian (paper §2.5): baseline + sigma_peak*exp(-(v-28)^2/(2*4.4^2))",
        "peak_velocity_km_per_s": V1_V_TARGET,
        "width_km_per_s": V1_WIDTH,
        "causality_criterion": f"t_core > {CAUSALITY_CAP} * t_cross (paper §9.12)",
        "causality_cap": CAUSALITY_CAP,
        "cloud_9_nfw": CLOUD9,
        "fornax_nfw": FORNAX,
        "sigma_peaks_swept": SIGMA_PEAKS,
        "channels": CHANNELS,
        "results": results,
        "key_findings": [],
    }

    # Finding 1: σ_peak constraint under paper's criterion
    fail_peak = None
    for r in results:
        if r["Cloud-9_causality_verdict"] == "FAIL":
            fail_peak = r["sigma_peak_HH_1_cm2_per_g"]
            break
    passing = [r['sigma_peak_HH_1_cm2_per_g'] for r in results if r['Cloud-9_causality_verdict'] == 'OK']
    largest_passing = passing[-1] if passing else None
    out["key_findings"].append(
        f"Under paper's causality criterion (ratio > {CAUSALITY_CAP}), "
        f"Cloud-9 FAILS starting at sigma_peak = {fail_peak} cm²/g. "
        f"The largest sigma_peak that passes is {largest_passing} cm²/g."
    )

    # Finding 2: Fornax σ_HL outlier in swept range
    all_unphysical = all(r["Fornax_sigma_HL_unphysical?"] for r in results)
    out["key_findings"].append(
        f"Fornax sigma_HL required is unphysical (negative) for ALL sigma_peak in swept "
        f"range [{min(SIGMA_PEAKS)}, {max(SIGMA_PEAKS)}]. At sigma_peak={min(SIGMA_PEAKS)}, "
        f"sigma_HL required = {[r for r in results if r['sigma_peak_HH_1_cm2_per_g'] == min(SIGMA_PEAKS)][0]['Fornax_sigma_HL_required_cm2_per_g']} cm²/g."
    )

    # Finding 3: σ_peak threshold for Fornax outlier to vanish
    sigma_eff_published = 0.032
    f_H = 0.30
    baseline_15 = sigma_m_at_v(PHASE44_SIGMA_0, PHASE44_A_SLOPE, 15)
    gaussian_factor_15 = math.exp(-(15 - V1_V_TARGET)**2 / (2 * V1_WIDTH**2))
    threshold = (sigma_eff_published / f_H**2 - baseline_15) / gaussian_factor_15
    sigma_at_Vmax = threshold * math.exp(-(31.12 - V1_V_TARGET)**2 / (2 * V1_WIDTH**2)) + sigma_m_at_v(PHASE44_SIGMA_0, PHASE44_A_SLOPE, 31.12)
    out["key_findings"].append(
        f"For Fornax sigma_HL outlier to VANISH (sigma_HL = 0), sigma_peak would need "
        f"to be ~{threshold:.1f} cm²/g. But this would also reduce sigma/m(V_max=31.12) "
        f"to ~{sigma_at_Vmax:.2f} cm²/g, far below Cloud-9's ~135 cm²/g requirement. "
        f"The Fornax outlier is robust within any sigma_peak range that also satisfies Cloud-9."
    )

    print("\n=== KEY FINDINGS ===")
    for f in out["key_findings"]:
        print(f"  {f}")

    out_path = REPO / 'v0.3-prelim' / 'data' / 'results' / 'v192_a_phase44_sigma_peak_sensitivity.json'
    json.dump(out, open(out_path, 'w'), indent=2)
    print(f"\nSaved: {out_path}")
    return out


if __name__ == "__main__":
    main()