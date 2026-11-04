# High-sigma Cloud-9 formation-timing recheck (2026-11-03)
# Question: with sigma/m near the canonical peak (~174 cm2/g), does the Cloud-9
# core become OPTICALLY THICK (mean free path < core radius) before/within the
# time the project's Yang+2024 eq-2.2 collapse-time chain claims? If yes, the
# LMFP-only formula is invalid at the claimed state (van den Bosch 2610.28890
# caveat) and required collapse time is underestimated.
# Pure recompute using the project's own module functions. ASCII only.

import sys, math, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'v0.3-prelim', 'code'))
import gravothermal_yang2024 as G

MSUNKPC3_TO_GCM3 = 1.9885e33 / (3.0857e21)**3   # 6.770e-31
KPC_CM = 3.0857e21

def sigma_canonical(v):
    return (G._SIGMA_0 * (G._V_REF / v) ** G._A_SLOPE
            + G._SIGMA_PEAK * math.exp(-((v - G._V_TARGET) ** 2) / (2 * G._SIGMA_1 ** 2)))

print("Canonical constants (scripts/constants.py via module):")
print(f"  SIGMA_0={G._SIGMA_0}, A_SLOPE={G._A_SLOPE}, V_REF={G._V_REF}")
print(f"  SIGMA_PEAK={G._SIGMA_PEAK}, V_TARGET={G._V_TARGET}, SIGMA_KMS(width)={G._SIGMA_1}")
for v in (15.0, 21.0, 28.0, 29.4, 36.0):
    print(f"  sigma({v}) = {sigma_canonical(v):.2f} cm2/g")

print()
# Cloud-9 per CLOUD9_REBASELINE.md: M=5e9, Vmax~31-36, r_s 1.4-1.85
cases = {
    "Cloud9-legacy(V31.12,rs1.4)": (5e9, 31.12, 1.4),
    "Cloud9-rebaseline(V36,rs1.85)": (5e9, 36.0, 1.854),
    "Fornax-control(V18,rs1.0)":    (1e9, 18.0, 1.0),
}

for name, (M, vmax, r_s0) in cases.items():
    rho_s0 = G.nfw_rho_s_from_vmax(vmax, r_s0)
    t_evol = G.evolution_time_gyr(M)
    print(f"== {name}: rho_s0={rho_s0:.3e} Msun/kpc3, t_evol={t_evol:.2f} Gyr")
    for label, s_eff in [("canonical(28)", sigma_canonical(28.0)),
                         ("peak174", 174.0),
                         ("Zhou-lower-50", 50.0),
                         ("dwarf-7", 7.0)]:
        t_c_lit  = G.collapse_time_SI_gyr(s_eff, rho_s0, r_s0)
        t_c_cal  = G.collapse_time_calibrated_gyr(s_eff, rho_s0, r_s0)
        t_c_leg  = G.collapse_time_gyr(s_eff, rho_s0, r_s0)
        tau_nat  = t_evol / t_c_cal   # uncapped natural tau with calibrated tc
        # Scan tau: r_c(tau), core density at r=r_c, mean free path
        tau_trans = None
        tau = 0.01
        # The eq. 2.3/2.4 fits go unphysical past tau ~ 1.3 (f_rs_over_rs0 and f_Vmax_over_Vmax0 turn
        # NEGATIVE at tau = 1.4), so scanning to tau = 20 used to print meaningless tau* values.
        # Scan only the range where the parametric model is physical. 2026-11-04.
        TAU_MAX_SCAN = G.TAU_FIT_RANGE_MAX
        while tau <= TAU_MAX_SCAN:
            rho_s = rho_s0 * G.f_rho_s_over_rho_s0(tau)
            r_c   = r_s0 * G.f_rc_over_rs0(tau)
            rho_core = G.rho_sidm(r_c, rho_s, r_s0 * G.f_rs_over_rs0(tau), r_c)
            lam_kpc = 1.0 / (rho_core * MSUNKPC3_TO_GCM3 * s_eff * KPC_CM) * KPC_CM  # cm->kpc handled
            # lambda in cm = 1/(rho_gcm3 * s_cm2g); in kpc = that / KPC_CM
            lam_kpc = 1.0 / (rho_core * MSUNKPC3_TO_GCM3 * s_eff) / KPC_CM
            if lam_kpc < r_c and tau_trans is None:
                tau_trans = tau
            tau += 0.01
        # state at tau=1 (claimed deep-collapse endpoint)
        rho_s1 = rho_s0 * G.f_rho_s_over_rho_s0(1.0)
        r_c1   = r_s0 * G.f_rc_over_rs0(1.0)
        rho_c1 = G.rho_sidm(r_c1, rho_s1, r_s0 * G.f_rs_over_rs0(1.0), r_c1)
        lam1   = 1.0 / (rho_c1 * MSUNKPC3_TO_GCM3 * s_eff) / KPC_CM
        print(f"  s_eff={s_eff:7.1f}: t_c lit={t_c_lit:8.2f} cal={t_c_cal:8.2f} leg={t_c_leg:8.2f} Gyr"
              f" | tau_natural={tau_nat:6.2f}")
        print(f"      at tau=1: r_c={r_c1:.4f} kpc, rho_core={rho_c1:.2e}, lambda={lam1:.4f} kpc"
              f" -> {'OPTICALLY THICK (lambda<r_c)' if lam1 < r_c1 else 'optically thin'}")
        if tau_trans is not None:
            print(f"      optical-thickness onset: tau*={tau_trans:.2f}"
                  f" -> t*={tau_trans*t_c_cal:.1f} Gyr (cal) / {tau_trans*t_c_lit:.1f} Gyr (lit);"
                  f" within t_evol={t_evol:.1f} Gyr? {'YES' if tau_trans*t_c_cal < t_evol or tau_trans*t_c_lit < t_evol else 'no'}")
        else:
            print(f"      never optically thick within the physical fit range (tau <= "
                  f"{G.TAU_FIT_RANGE_MAX})")
    print()
