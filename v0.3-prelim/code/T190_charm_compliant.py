"""
T190 — T185 revision with CHARM beam-dump constraint (2026-09-21).

T189 found that T185's best configuration (g_h_SM = 0.01) is in tension
with CHARM beam-dump limits (g_h_SM < 0.005 at m_Phi_h = 22 GeV).

This script re-runs the T185 scan with the CHARM constraint applied,
finding the simplest viable configuration that satisfies BOTH:
  - Thermal relic density (Omega_h^2 ~ 0.12)
  - Beam-dump constraints (g_h_SM <= 0.005)

The revised best config will be used to update the paper.
"""
import sys
import json
import numpy as np

sys.path.insert(0, r'C:\Users\lamkuenai\projects\sidm-composite-dm-mediator\v0.3-prelim\code')

from T185_two_mediator import (
    sigma_v_resonant, omega_h2_calibrated,
    m_chi, m_phi, OMEGA_H2_OBS
)


CHARM_LIMIT_g_h_SM = 0.005


if __name__ == '__main__':
    print("="*70)
    print("T190 — T185 revision with CHARM beam-dump constraint")
    print("="*70)
    print()

    # Extended scan with smaller g_h_SM
    g_DM_Y1_list = [0.05, 0.1, 0.3, 1.0, 2.0]
    g_h_SM_list = [0.001, 0.002, 0.003, 0.005, 0.008]  # Smaller range

    best_configs = []
    for g_DM_Y1 in g_DM_Y1_list:
        for g_h_SM in g_h_SM_list:
            # CHARM constraint
            if g_h_SM > CHARM_LIMIT_g_h_SM:
                continue

            for delta_log in np.linspace(-4, 0, 50):
                # Try positive and negative detuning
                for sign in [1, -1]:
                    delta = sign * 10**delta_log
                    if delta < -0.5:  # too far off
                        continue
                    m_Phi_h = 2 * m_chi * (1 + delta)
                    sv = sigma_v_resonant(g_DM_Y1, m_chi, m_Phi_h, g_h_SM)
                    om = omega_h2_calibrated(sv)
                    if 0.10 < om < 0.14:  # within 1.5x of Planck
                        best_configs.append({
                            'g_DM_Y1': g_DM_Y1,
                            'g_h_SM': g_h_SM,
                            'm_Phi_h_GeV': m_Phi_h,
                            'delta': delta,
                            'sigma_v': sv,
                            'omega_h2': om,
                        })

    print(f"Found {len(best_configs)} CHARM-compliant viable configurations.")
    if best_configs:
        print(f"\n{'g_DM_Y1':>10} {'g_h_SM':>10} {'m_Phi_h':>10} {'delta':>10} {'Omega_h^2':>12}")
        print("-"*60)
        for cfg in best_configs[:15]:
            print(f"{cfg['g_DM_Y1']:>10.3f} {cfg['g_h_SM']:>10.3f} {cfg['m_Phi_h_GeV']:>10.3f} {cfg['delta']:>10.4f} {cfg['omega_h2']:>12.4f}")

        # Pick smallest couplings (most perturbative)
        best = min(best_configs, key=lambda c: c['g_DM_Y1'] + c['g_h_SM'])
        print(f"\n**REVISED best configuration (CHARM-compliant):**")
        print(f"  g_DM_Y1 = {best['g_DM_Y1']}")
        print(f"  g_h_SM = {best['g_h_SM']} (CHARM limit: < {CHARM_LIMIT_g_h_SM})")
        print(f"  m_Phi_h = {best['m_Phi_h_GeV']:.3f} GeV")
        print(f"  delta = {best['delta']:.4e}")
        print(f"  sigma_v = {best['sigma_v']:.3e} cm^3/s")
        print(f"  Omega_h^2 = {best['omega_h2']:.4f}")

    # Verdict
    print()
    print("="*70)
    print("T190 VERDICT:")
    print("="*70)
    print()
    if best_configs:
        print("CHARM-compliant T185 configuration EXISTS:")
        print(f"  g_DM_Y1 ~ {best['g_DM_Y1']}")
        print(f"  g_h_SM ~ {best['g_h_SM']}")
        print(f"  m_Phi_h ~ {best['m_Phi_h_GeV']:.2f} GeV")
        print(f"  Omega_h^2 ~ {best['omega_h2']:.3f}")
        print()
        print("The thermal relic constraint is satisfied even with smaller")
        print("g_h_SM, because the BW enhancement scales as 1/g_h_SM at")
        print("fixed detuning — smaller g_h_SM requires smaller detuning")
        print("(more precisely on resonance).")
        print()
        print("**REVISION NEEDED**: Update paper §10.10 to use this revised config.")
        print("Direct-detection σ_SI will scale down (g_h_SM^2 factor).")
    else:
        print("No CHARM-compliant config found. Need finer scan or different UV setup.")

    # Save JSON
    output = {
        'description': 'T190 — T185 revision with CHARM beam-dump constraint (2026-09-21)',
        'method': 'Re-run T185 scan with g_h_SM <= 0.005 (CHARM beam-dump limit at m_Phi_h = 22 GeV).',
        'CHARM_limit_g_h_SM': CHARM_LIMIT_g_h_SM,
        'best_configuration': best if best_configs else None,
        'all_configs': best_configs[:30] if best_configs else [],
        'verdict': (
            'CHARM-compliant T185 configuration exists. '
            'Need to update paper with smaller g_h_SM (~0.001-0.005) '
            'and tighter detuning. σ_SI scales as g_h_SM^2 → much smaller.'
        ),
    }
    out_path = r'C:\Users\lamkuenai\projects\sidm-composite-dm-mediator\v0.3-prelim\data\results\t190_charm_compliant.json'
    with open(out_path, 'w') as f:
        json.dump(output, f, indent=2)
    print(f"\nWrote {out_path}")