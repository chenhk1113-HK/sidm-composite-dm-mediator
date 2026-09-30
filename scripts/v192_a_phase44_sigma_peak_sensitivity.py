"""v19.2-A: Phase 44 sigma_peak_HH_1 sensitivity sweep.

Question: Is the framework's resonance strength (sigma_peak_HH_1 = 174 cm^2/g
per causality_summary_corrected, vs sigma_peak = 196.3 from Phase 44 free fit,
vs sigma_peak = 30-100 from various prescription modes) actually correct?

We sweep sigma_peak_HH_1 in [30, 50, 75, 100, 125, 150, 174, 200, 250] and
check, for each value:
  1. sigma/m at v=28 (Cloud-9) and v=15 (Fornax)
  2. Cloud-9 gravothermal t_core, t_cross, causality check
  3. dSph gravothermal t_core for Fornax (V_max=15)
  4. Whether v=15 sigma/m is high enough to fail dSph bound
  5. SPARC / cluster consistency check (sigma/m at v=100, 500)

Per Rule 28 (arithmetic checking before claim), all values are derived from
canonical functions:
  - sigma_HH_at_v(v, sigma_peak_HH_1=...) from two_component_three_term
  - gravothermal_t_core_Gyr(sigma_m, rho_s, r_s, v_max) from T208
  - t_cross_Gyr_from_r_vir_vmax(r_vir_pc, v_max_kms, c) from t212

Causality check: t_core / t_cross > 1 = OK, < 1 = FAIL
dSph bound: sigma/m(15) < sigma_eff_published(Fornax) / f_H^2 = 0.032 / 0.09 = 0.36
  - If sigma/m(15) > 0.36, then sigma_HL < 0 is required (Fornax outlier)
"""
import json
import sys
from pathlib import Path

REPO = Path(r'C:\Users\lamkuenai\projects\sidm-composite-dm-mediator')
sys.path.insert(0, str(REPO / 'v0.3-prelim' / 'code'))

from two_component_three_term import sigma_HH_at_v
from T208_path_b_cloud9_host_halo_gravothermal import gravothermal_t_core_Gyr
from t212_silverman_gravothermal import t_cross_Gyr_from_r_vir_vmax

# Cloud-9 NFW params (from causality_summary_corrected in t207_final_summary)
CLOUD9 = {
    "M_200_MSun": 3.0e10,
    "c": 12,
    "v_max_kms": 31.12,
    "r_vir_kpc": 38.9,
    "r_s_kpc": 3.24,
    "rho_s_MSun_pc3": 1.4e-2,
}

# Fornax NFW params (from v192_dsph_gravothermal_sweep.json)
FORNAX = {
    "V_max": 15.0,
    "M_halo_MSun": 3.0e9,
    "c": 12,
    "rho_s_MSun_pc3": 1.0e-2,  # rough NFW scale density at V_max=15
    "r_s_kpc": 4.0,           # ~ r_vir/c, rough
    "r_vir_kpc": 48.0,
}

# Sigma/m sensitivity sweep
SIGMA_PEAKS = [30, 50, 75, 100, 125, 150, 174, 200, 250]

# Channel velocity scales
CHANNELS = {
    "UFD v=3": 3,
    "UFD v=5": 5,
    "dSph v=7": 7,
    "dSph v=10": 10,
    "dSph v=15 (Fornax)": 15,
    "Cloud-9 v=28": 28,
    "Cloud-9 v=29.4 (Phase 44 peak)": 29.4,
    "SPARC v=100": 100,
    "Cluster v=500": 500,
}


def compute_row(sigma_peak: float) -> dict:
    """Compute all derived values for one sigma_peak value."""
    row = {"sigma_peak_HH_1_cm2_per_g": sigma_peak}

    # 1. sigma/m at all channels (using canonical sigma_HH_at_v)
    row["sigma_HH_at_v"] = {}
    for label, v in CHANNELS.items():
        try:
            row["sigma_HH_at_v"][label] = round(sigma_HH_at_v(v, sigma_peak_HH_1=sigma_peak), 4)
        except Exception as e:
            row["sigma_HH_at_v"][label] = f"ERROR: {e}"

    # 2. Cloud-9 gravothermal
    s28 = row["sigma_HH_at_v"]["Cloud-9 v=28"]
    if isinstance(s28, (int, float)):
        t_core_cloud9 = gravothermal_t_core_Gyr(
            sigma_m_cm2_per_g=s28,
            rho_s_Msun_per_pc3=CLOUD9["rho_s_MSun_pc3"],
            r_s_pc=CLOUD9["r_s_kpc"] * 1e3,  # convert kpc to pc
            v_max_kms=CLOUD9["v_max_kms"],
        )
        t_cross_cloud9 = t_cross_Gyr_from_r_vir_vmax(
            r_vir_pc=CLOUD9["r_vir_kpc"] * 1e3,
            v_max_kms=CLOUD9["v_max_kms"],
            c=CLOUD9["c"],
        )
        row["Cloud-9_t_core_Gyr"] = round(t_core_cloud9, 4)
        row["Cloud-9_t_cross_Gyr"] = round(t_cross_cloud9, 4)
        row["Cloud-9_causality_ratio"] = round(t_core_cloud9 / t_cross_cloud9, 3)
        row["Cloud-9_causality_verdict"] = "OK" if t_core_cloud9 > t_cross_cloud9 else "FAIL"
    else:
        row["Cloud-9_t_core_Gyr"] = None
        row["Cloud-9_t_cross_Gyr"] = None

    # 3. Fornax gravothermal (V_max=15, M_halo=3e9, c=12)
    s15 = row["sigma_HH_at_v"]["dSph v=15 (Fornax)"]
    if isinstance(s15, (int, float)):
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
        row["Fornax_t_core_Gyr"] = round(t_core_fornax, 4)
        row["Fornax_t_cross_Gyr"] = round(t_cross_fornax, 4)
        row["Fornax_causality_ratio"] = round(t_core_fornax / t_cross_fornax, 3)
        row["Fornax_causality_verdict"] = "OK" if t_core_fornax > t_cross_fornax else "FAIL"
    else:
        row["Fornax_t_core_Gyr"] = None

    # 4. Fornax sigma/m bound check
    # If sigma/m(15) > sigma_eff_published / f_H^2 = 0.032 / 0.09 = 0.36,
    # then sigma_HL < 0 is required (Fornax outlier)
    if isinstance(s15, (int, float)):
        sigma_eff_threshold = 0.032 / 0.09  # = 0.356
        row["Fornax_sigma_HL_required_for_σ_eff=0.032"] = round(
            (0.032 - 0.09 * s15) / 0.42, 4
        )  # σ_eff = f_H² σ_HH + 2 f_H f_L σ_HL; solve for σ_HL with σ_LL=0
        row["Fornax_outlier?"] = s15 > sigma_eff_threshold

    # 5. SPARC sigma/m at v=100 (should be small)
    s100 = row["sigma_HH_at_v"]["SPARC v=100"]
    if isinstance(s100, (int, float)):
        row["SPARC_v100_sigma_HH"] = s100
        row["SPARC_OK?"] = s100 < 1.0  # SPARC upper limit ~ 1 cm^2/g

    return row


def main():
    print("=" * 80)
    print("v19.2-A: Phase 44 sigma_peak_HH_1 sensitivity sweep")
    print("=" * 80)
    print(f"Sweeping sigma_peak_HH_1 in {SIGMA_PEAKS}")
    print(f"Cloud-9 NFW: M={CLOUD9['M_200_MSun']:.1e}, c={CLOUD9['c']}, V_max={CLOUD9['v_max_kms']}")
    print(f"Fornax NFW: V_max={FORNAX['V_max']}, M_halo={FORNAX['M_halo_MSun']:.1e}, c={FORNAX['c']}")
    print()

    results = []
    for sigma_peak in SIGMA_PEAKS:
        row = compute_row(sigma_peak)
        results.append(row)

        # Print summary
        print(f"--- sigma_peak = {sigma_peak} cm²/g ---")
        print(f"  Cloud-9: σ/m(28) = {row['sigma_HH_at_v']['Cloud-9 v=28']:.2f}, "
              f"t_core = {row.get('Cloud-9_t_core_Gyr', 'N/A')} Gyr, "
              f"t_cross = {row.get('Cloud-9_t_cross_Gyr', 'N/A')} Gyr, "
              f"ratio = {row.get('Cloud-9_causality_ratio', 'N/A')} ({row.get('Cloud-9_causality_verdict', 'N/A')})")
        print(f"  Fornax:  σ/m(15) = {row['sigma_HH_at_v']['dSph v=15 (Fornax)']:.2f}, "
              f"t_core = {row.get('Fornax_t_core_Gyr', 'N/A')} Gyr, "
              f"ratio = {row.get('Fornax_causality_ratio', 'N/A')} ({row.get('Fornax_causality_verdict', 'N/A')}), "
              f"σ_HL req = {row.get('Fornax_sigma_HL_required_for_σ_eff=0.032', 'N/A')} cm²/g, "
              f"outlier = {row.get('Fornax_outlier?', 'N/A')}")
        print(f"  SPARC:   σ/m(100) = {row['sigma_HH_at_v']['SPARC v=100']:.3f}")
        print()

    # Save JSON
    out = {
        "version": "v19.2-A",
        "date": "2026-09-30",
        "description": "Phase 44 sigma_peak_HH_1 sensitivity sweep",
        "cloud_9_nfw": CLOUD9,
        "fornax_nfw": FORNAX,
        "sigma_peaks_swept": SIGMA_PEAKS,
        "channels": CHANNELS,
        "results": results,
        "key_findings": [],
    }

    # Add key findings
    # Finding 1: At sigma_peak=174 (causality threshold), is Cloud-9 OK?
    r174 = next(r for r in results if r["sigma_peak_HH_1_cm2_per_g"] == 174)
    out["key_findings"].append(
        f"sigma_peak=174: σ/m(28)={r174['sigma_HH_at_v']['Cloud-9 v=28']:.2f}, "
        f"Cloud-9 causality ratio={r174['Cloud-9_causality_ratio']}, "
        f"Fornax σ_HL required={r174['Fornax_sigma_HL_required_for_σ_eff=0.032']} cm²/g"
    )

    # Finding 2: At sigma_peak=100 (common fit value), what's the Cloud-9 verdict?
    r100 = next((r for r in results if r["sigma_peak_HH_1_cm2_per_g"] == 100), None)
    if r100:
        out["key_findings"].append(
            f"sigma_peak=100: σ/m(28)={r100['sigma_HH_at_v']['Cloud-9 v=28']:.2f}, "
            f"Cloud-9 causality ratio={r100['Cloud-9_causality_ratio']}"
        )

    # Finding 3: Minimum sigma_peak for Fornax outlier
    fnx_threshold = 0.36  # sigma/m at v=15 must be < 0.36 to avoid Fornax outlier
    min_no_outlier = None
    for r in results:
        s15 = r["sigma_HH_at_v"]["dSph v=15 (Fornax)"]
        if isinstance(s15, (int, float)) and s15 <= fnx_threshold and not r["Fornax_outlier?"]:
            min_no_outlier = r["sigma_peak_HH_1_cm2_per_g"]
            break
    out["key_findings"].append(
        f"Minimum sigma_peak to avoid Fornax σ_HL outlier: {min_no_outlier} cm²/g"
    )

    # Finding 4: At what sigma_peak does Cloud-9 fail causality?
    fail_peak = None
    for r in results:
        if r.get("Cloud-9_causality_verdict") == "FAIL":
            fail_peak = r["sigma_peak_HH_1_cm2_per_g"]
            break
    out["key_findings"].append(
        f"Cloud-9 fails causality (t_core/t_cross < 1) starting at sigma_peak={fail_peak} cm²/g"
    )

    print("\n=== KEY FINDINGS ===")
    for f in out["key_findings"]:
        print(f"  {f}")

    # Save
    out_path = REPO / 'v0.3-prelim' / 'data' / 'results' / 'v192_a_phase44_sigma_peak_sensitivity.json'
    json.dump(out, open(out_path, 'w'), indent=2)
    print(f"\nSaved: {out_path}")
    return out


if __name__ == "__main__":
    main()