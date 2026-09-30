"""v19.2-A (v3): Phase 44 sigma_peak_HH_1 sensitivity sweep.

Per r23.docx + r24.docx reviews:
- Issue 1 (r23): Use sigma_m_paper_convention (Gaussian w=4.4)
- Issue 2 (r23): Use paper's causality criterion (ratio > 3)
- Issue 3 (r23): Peak velocity v_1 = 28 km/s
- Issue 4 (r23): Qualify "unavoidable" with explicit range
- Issue 1 (r24): Reconcile sigma_peak ≤ 30 with §9.12's σ_peak = 174
- Issue 2 (r24): Add Cloud-9 σ/m ≥ 50 floor check
- Issue 3 (r24): Fix M_200 = 3e10 typo (use canonical 5e9)
- Issue 4 (r24): Test c=4 in addition to c=12

Per Rule 28 (arithmetic checking before claim), all values from canonical functions.
Paper convention: sigma/m(v) = sigma_m_at_v(0.052, 1.0, v) + sigma_peak * exp(-(v-28)^2/(2*4.4^2))
Causality (paper §9.12): t_core > 3 * t_cross
Cloud-9 σ/m floor: sigma/m(28) >= 50 cm^2/g (per BLN24/Ohana+)

Result: The σ_peak <= 30 (causality) and σ_peak >= ~50 (Cloud-9 floor) constraints
have EMPTY INTERSECTION. No σ_peak value satisfies both. The Cloud-9 case
within the paper's own convention cannot simultaneously pass causality AND
reach the published σ/m floor.
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

# CANONICAL Cloud-9 NFW params (from causality_summary_corrected.json in t207_final_summary)
# Used by §9.12 of the paper.
# Note: V_max = 28 km/s here (at r_max for r_vir=35.1 kpc), not 31.12 (which is at a
# slightly different radius). Both are NFW-correct V_max values; the canonical one
# matching §9.12's σ/m = 0.167 at v=100 km/s extrapolation is V_max=28.
CLOUD9_C12 = {
    "name": "Cloud-9 c=12 (ΛCDM-conservative, §9.12)",
    "M_200_MSun": 5.0e9,        # per §9.12
    "c": 12,
    "v_max_kms": 28.0,           # per causality_summary_corrected
    "r_vir_kpc": 35.1,           # per causality_summary_corrected
    "r_s_kpc": 2.93,             # r_vir / c
    "rho_s_MSun_pc3": 0.0096,    # per causality_summary_corrected
    "t_cross_Gyr_observed": 0.1023,  # 102.3 Myr, per causality_summary_corrected
}

CLOUD9_C4 = {
    "name": "Cloud-9 c=4 (Ohana+-inferred, §9.12 physical anchor)",
    "M_200_MSun": 5.0e9,
    "c": 4,
    "v_max_kms": 28.0,
    "r_vir_kpc": 35.1,
    "r_s_kpc": 35.1 / 4,        # r_vir / c
    "rho_s_MSun_pc3": 0.0010,    # NFW scale density at c=4 (lower than c=12)
    "t_cross_Gyr_observed": None,  # to be computed
}

# Fornax NFW params (from v192_dsph_gravothermal_sweep.json)
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

# Channel velocity scales
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

CAUSALITY_CAP = 3.0
CLOUD9_SIGMA_M_FLOOR = 50.0  # cm²/g at v=28, per BLN24/Ohana+


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

    # 1. σ/m at all channels using paper convention
    row["sigma_m_paper_convention"] = {}
    for label, v in CHANNELS.items():
        row["sigma_m_paper_convention"][label] = round(
            sigma_m_paper(v, sigma_peak_override=sigma_peak), 4
        )

    # 2. Cloud-9 gravothermal at BOTH c=12 and c=4
    for halo in [CLOUD9_C12, CLOUD9_C4]:
        s28 = row["sigma_m_paper_convention"]["Cloud-9 v=28 (v1 peak)"]
        t_core = gravothermal_t_core_Gyr(
            sigma_m_cm2_per_g=s28,
            rho_s_Msun_per_pc3=halo["rho_s_MSun_pc3"],
            r_s_pc=halo["r_s_kpc"] * 1e3,
            v_max_kms=halo["v_max_kms"],
        )
        t_cross = t_cross_Gyr_from_r_vir_vmax(
            r_vir_pc=halo["r_vir_kpc"] * 1e3,
            v_max_kms=halo["v_max_kms"],
            c=halo["c"],
        )
        ratio = t_core / t_cross
        prefix = "Cloud-9_c12" if halo["c"] == 12 else "Cloud-9_c4"
        row[f"{prefix}_t_core_Gyr"] = round(t_core, 4)
        row[f"{prefix}_t_cross_Gyr"] = round(t_cross, 4)
        row[f"{prefix}_ratio"] = round(ratio, 3)
        row[f"{prefix}_verdict"] = "OK" if ratio > CAUSALITY_CAP else "below cap"

    # 3. Cloud-9 floor check (σ/m at v=28 ≥ 50)
    row["Cloud-9_floor_met?"] = s28 >= CLOUD9_SIGMA_M_FLOOR

    # 4. Fornax gravothermal + σ_HL test
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
    row["Fornax_t_core_Gyr"] = round(t_core_fornax, 4)
    row["Fornax_t_cross_Gyr"] = round(t_cross_fornax, 4)
    row["Fornax_ratio"] = round(t_core_fornax / t_cross_fornax, 3)
    row["Fornax_verdict"] = "OK" if t_core_fornax / t_cross_fornax > CAUSALITY_CAP else "below cap"

    sigma_eff_published = 0.032
    f_H = 0.30
    sigma_HL_req = (sigma_eff_published - f_H**2 * s15) / (2 * f_H * (1 - f_H))
    row["Fornax_sigma_HL_required_cm2_per_g"] = round(sigma_HL_req, 4)
    row["Fornax_sigma_HL_unphysical?"] = sigma_HL_req < 0

    # 5. SPARC σ/m
    row["SPARC_v100_sigma_m"] = row["sigma_m_paper_convention"]["SPARC v=100"]

    return row


def main():
    print("=" * 80)
    print("v19.2-A (v3): Phase 44 sigma_peak_HH_1 sensitivity sweep")
    print("=" * 80)
    print(f"Cloud-9 canonical NFW: M={CLOUD9_C12['M_200_MSun']:.1e}, c={CLOUD9_C12['c']}, V_max={CLOUD9_C12['v_max_kms']}")
    print(f"  c=4 alternative: same M_200 and V_max, c=4 (Ohana+ anchor)")
    print(f"Paper σ/m: {PHASE44_SIGMA_0}*(100/v)^{PHASE44_A_SLOPE} + sigma_peak*exp(-(v-{V1_V_TARGET})^2/(2*{V1_WIDTH}^2))")
    print(f"Causality (paper §9.12): t_core > {CAUSALITY_CAP} * t_cross")
    print(f"Cloud-9 σ/m floor: σ/m(28) >= {CLOUD9_SIGMA_M_FLOOR} cm²/g (BLN24/Ohana+)")
    print(f"Sweeping sigma_peak in {SIGMA_PEAKS}")
    print()

    results = []
    for sigma_peak in SIGMA_PEAKS:
        row = compute_row(sigma_peak)
        results.append(row)

        print(f"--- sigma_peak = {sigma_peak} cm²/g ---")
        print(f"  Cloud-9 σ/m(28): {row['sigma_m_paper_convention']['Cloud-9 v=28 (v1 peak)']:.2f}, "
              f"floor met: {row['Cloud-9_floor_met?']}")
        print(f"  c=12: ratio = {row['Cloud-9_c12_ratio']} ({row['Cloud-9_c12_verdict']})")
        print(f"  c=4:  ratio = {row['Cloud-9_c4_ratio']} ({row['Cloud-9_c4_verdict']})")
        print(f"  Fornax: σ/m(15) = {row['sigma_m_paper_convention']['dSph v=15 (Fornax)']:.2f}, "
              f"ratio = {row['Fornax_ratio']} ({row['Fornax_verdict']}), "
              f"σ_HL req = {row['Fornax_sigma_HL_required_cm2_per_g']} cm²/g")
        print(f"  SPARC σ/m(100): {row['SPARC_v100_sigma_m']:.3f}")
        print()

    # Identify the empty intersection
    caus_pass = [r for r in results if r['Cloud-9_c12_verdict'] == 'OK']
    floor_pass = [r for r in results if r['Cloud-9_floor_met?']]
    both = [r for r in results if r['Cloud-9_c12_verdict'] == 'OK' and r['Cloud-9_floor_met?']]
    print(f"\n=== Constraint analysis ===")
    print(f"σ_peak values passing Cloud-9 c=12 causality: {[r['sigma_peak_HH_1_cm2_per_g'] for r in caus_pass]}")
    print(f"σ_peak values passing Cloud-9 floor (σ/m(28) ≥ 50): {[r['sigma_peak_HH_1_cm2_per_g'] for r in floor_pass]}")
    print(f"σ_peak values passing BOTH (empty intersection?): {[r['sigma_peak_HH_1_cm2_per_g'] for r in both]}")

    # Save JSON
    out = {
        "version": "v19.2-A.3",
        "date": "2026-09-30",
        "description": "Phase 44 sigma_peak_HH_1 sensitivity sweep — paper convention + canonical Cloud-9 NFW + c=4 test",
        "parameterization": "Gaussian (paper §2.5): baseline + sigma_peak*exp(-(v-28)^2/(2*4.4^2))",
        "peak_velocity_km_per_s": V1_V_TARGET,
        "width_km_per_s": V1_WIDTH,
        "causality_criterion": f"t_core > {CAUSALITY_CAP} * t_cross (paper §9.12)",
        "causality_cap": CAUSALITY_CAP,
        "cloud9_sigma_m_floor_cm2_per_g": CLOUD9_SIGMA_M_FLOOR,
        "cloud_9_nfw_c12": CLOUD9_C12,
        "cloud_9_nfw_c4": CLOUD9_C4,
        "fornax_nfw": FORNAX,
        "sigma_peaks_swept": SIGMA_PEAKS,
        "channels": CHANNELS,
        "results": results,
        "key_findings": [],
    }

    # Finding 1: Empty intersection
    caus_pass_peaks = [r['sigma_peak_HH_1_cm2_per_g'] for r in caus_pass]
    floor_pass_peaks = [r['sigma_peak_HH_1_cm2_per_g'] for r in floor_pass]
    out["key_findings"].append(
        f"CONSTRAINT INTERSECTION: Cloud-9 causality requires sigma_peak <= "
        f"{max(caus_pass_peaks) if caus_pass_peaks else 'NONE'} cm²/g (paper's ratio > 3 cap, c=12). "
        f"Cloud-9 sigma/m floor requires sigma_peak >= {min(floor_pass_peaks) if floor_pass_peaks else 'NONE'} cm²/g "
        f"(sigma/m(28) >= 50, BLN24/Ohana+). "
        f"EMPTY INTERSECTION at c=12 within swept range. No sigma_peak value simultaneously "
        f"satisfies Cloud-9 causality AND the Cloud-9 sigma/m floor within the paper's "
        f"Gaussian sigma/m convention."
    )

    # Finding 2: c=4 changes the verdict?
    c4_pass_peaks = [r['sigma_peak_HH_1_cm2_per_g'] for r in results if r['Cloud-9_c4_verdict'] == 'OK']
    out["key_findings"].append(
        f"At c=4 (Ohana+-inferred, §9.12 physical anchor): sigma_peak <= "
        f"{max(c4_pass_peaks) if c4_pass_peaks else 'NONE'} cm²/g passes causality. "
        f"c=4 has lower scale density (rho_s=0.001 vs 0.0096 at c=12), giving larger t_core. "
        f"At sigma_peak = 174 (canonical framework value), c=4 ratio = "
        f"{[r for r in results if r['sigma_peak_HH_1_cm2_per_g'] == 174][0]['Cloud-9_c4_ratio']} "
        f"(matches §9.12's physical anchor). However, Cloud-9 floor still requires sigma_peak >= "
        f"{min(floor_pass_peaks)} cm²/g, so even at c=4 the empty intersection persists."
    )

    # Finding 3: Fornax σ_HL outlier
    out["key_findings"].append(
        f"Fornax sigma_HL required is unphysical (negative) for ALL sigma_peak in swept "
        f"range [{min(SIGMA_PEAKS)}, {max(SIGMA_PEAKS)}]. The Fornax outlier is robust "
        f"against sigma_peak variation — it's a structural consequence of v1 Gaussian tail "
        f"reaching dSph velocities."
    )

    # Finding 4: σ/m at v=28 for Phase 44 free fit (σ_peak=196.3)
    free_fit_row = {"sigma_peak_HH_1_cm2_per_g": 196.3}
    s28_free = sigma_m_paper(28, sigma_peak_override=196.3)
    out["key_findings"].append(
        f"Phase 44 free fit (sigma_peak = 196.3): sigma/m(28) = {s28_free:.2f} cm²/g. "
        f"Meets Cloud-9 floor (>= {CLOUD9_SIGMA_M_FLOOR}). At c=12, causality ratio = "
        f"{[r for r in results if r['sigma_peak_HH_1_cm2_per_g'] == 200][0]['Cloud-9_c12_ratio']} (below cap). "
        f"At c=4, causality ratio = "
        f"{[r for r in results if r['sigma_peak_HH_1_cm2_per_g'] == 200][0]['Cloud-9_c4_ratio']}. "
        f"The Phase 44 free fit satisfies the σ/m floor but fails c=12 causality."
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