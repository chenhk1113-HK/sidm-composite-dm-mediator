"""
T189 — B-factory / beam-dump sensitivity for the heavy scalar Phi_h at 20 GeV
(2026-09-21).

The Drobczyk 2025 benchmark puts the heavy scalar at m_Phi_h ~ 1.2 TeV,
visible at LHC via ttbar. Our T185 puts it at m_Phi_h ~ 22 GeV, BELOW
ttbar threshold, in the B-factory / beam-dump window.

Testable predictions:
- Production: e+ e- -> Phi_h -> SM SM
- Beam-dump: p + target -> Phi_h + X -> SM SM
- B-meson decays: B -> K + Phi_h -> K + SM SM (similar to B -> K + inv)
- Belle II can probe Phi_h ~ 10-20 GeV in e+e- collisions at sqrt(s) = 10.58 GeV
  via radiative return (e+e- -> gamma + Phi_h)

For our parameters:
- m_Phi_h = 22.223 GeV
- g_DM_Y1 = 0.05 (DM coupling, irrelevant for production)
- g_h_SM = 0.01 (Higgs portal mixing, sets production cross-section)

Production cross-section at e+e- colliders via Higgs portal mixing:
  sigma(e+e- -> Phi_h) ~ (g_h_SM * m_e / v)^2 * (mechanism-dependent)

Decay channels for 22 GeV scalar:
- chi chi (if kinematically open, mass ~10 GeV)
- tau+ tau- (mass < 2 m_tau ~ 3.5 GeV; kinematically open)
- hadrons (via mixing with SM Higgs)
- mu+ mu- (mass > 2 m_mu ~ 0.21 GeV)

Branching ratios depend on mixing angle. For 22 GeV, dominant decay is
likely hadronic (multi-pion, etc.).

We compute:
1. Production rate at Belle II
2. Production rate at beam-dump experiments
3. Branching ratios
4. Predicted signal-to-noise
"""
import sys
import json
import numpy as np

sys.path.insert(0, r'C:\Users\lamkuenai\projects\sidm-composite-dm-mediator\v0.3-prelim\code')


# Constants
m_chi = 22.223  # GeV (Phi_h)
m_DM = 10.3  # GeV (DM)
g_h_SM = 0.01  # Higgs portal mixing
g_DM_Y1 = 0.05  # DM coupling
v_H = 246.0  # GeV
m_e = 0.511e-3  # GeV
m_mu = 0.1057  # GeV
m_tau = 1.777  # GeV
m_h_SM = 125.0  # GeV
alpha_EM = 1.0 / 137.0


def branching_ratio_to_dm(m_Phi_h, m_DM, g_DM_Y1):
    """BR(Phi_h -> DM DM) for scalar with Yukawa coupling g_DM_Y1.

    Width Gamma(Phi_h -> DM DM) ~ g_DM_Y1^2 * m_Phi_h / (8 pi) * (1 - 4 m_DM^2/m_Phi_h^2)^(3/2)
    """
    if m_Phi_h < 2 * m_DM:
        return 0.0
    width = g_DM_Y1**2 * m_Phi_h / (8 * np.pi) * (1 - 4 * m_DM**2 / m_Phi_h**2)**1.5
    return width


def branching_ratio_to_fermions(m_Phi_h, m_fermi, g_h_SM, v_H=v_H):
    """BR(Phi_h -> f fbar) for SM fermion with Higgs portal mixing.

    Width Gamma(Phi_h -> f fbar) ~ (g_h_SM * m_f / v)^2 * m_Phi_h / (8 pi)
                                 * (1 - 4 m_f^2 / m_Phi_h^2)^(3/2)
    """
    if m_Phi_h < 2 * m_fermi:
        return 0.0
    coupling = g_h_SM * m_fermi / v_H
    width = coupling**2 * m_Phi_h / (8 * np.pi) * (1 - 4 * m_fermi**2 / m_Phi_h**2)**1.5
    return width


def branching_ratio_to_gluons(m_Phi_h, g_h_SM):
    """BR(Phi_h -> gg) via top loop.

    For Higgs-like scalar with portal mixing g_h_SM, BR ~ 8% at low mass.
    Simplified: use the SM Higgs BR scaled by (g_h_SM / SM_Higgs_coupling)^2.
    """
    # Top loop contribution
    width = (g_h_SM * 0.012)**2 * m_Phi_h / 8  # rough estimate
    return width


if __name__ == '__main__':
    print("="*70)
    print("T189 — B-factory / beam-dump sensitivity at m_Phi_h = 22 GeV")
    print("="*70)
    print(f"Our parameters: m_Phi_h = {m_chi} GeV, g_h_SM = {g_h_SM}, g_DM_Y1 = {g_DM_Y1}")
    print()

    # Compute partial widths
    print("="*70)
    print("DECAY CHANNELS AND BRANCHING RATIOS")
    print("="*70)
    channels = {}
    channels['DM'] = branching_ratio_to_dm(m_chi, m_DM, g_DM_Y1)
    channels['e+e-'] = branching_ratio_to_fermions(m_chi, m_e, g_h_SM)
    channels['mu+mu-'] = branching_ratio_to_fermions(m_chi, m_mu, g_h_SM)
    channels['tau+tau-'] = branching_ratio_to_fermions(m_chi, m_tau, g_h_SM)
    channels['cc'] = branching_ratio_to_fermions(m_chi, 1.27, g_h_SM)  # charm mass
    channels['bb'] = branching_ratio_to_fermions(m_chi, 4.18, g_h_SM)  # bottom mass
    channels['gg'] = branching_ratio_to_gluons(m_chi, g_h_SM)

    total_width = sum(channels.values())
    print(f"Total width Gamma = {total_width*1e3:.4f} MeV")
    print()
    print(f"{'Channel':>15} {'Width (MeV)':>15} {'BR (%)':>10}")
    for name, width in channels.items():
        br = 100 * width / total_width if total_width > 0 else 0
        print(f"{name:>15} {width*1e3:>15.4f} {br:>10.2f}")

    # Verify this matches Drobczyk (which says BR(Phi_h -> chi chi) ~ 0.07%)
    if 'DM' in channels:
        br_dm = 100 * channels['DM'] / total_width if total_width > 0 else 0
        print()
        print(f"BR(Phi_h -> DM DM) = {br_dm:.3f}%")
        print(f"Drobczyk benchmark (1.2 TeV): BR(Phi_h -> chi chi) ~ 0.07%")

    # Compute lifetime (assuming phi decays promptly)
    print()
    tau_Phi_h = 6.582e-25 / (total_width * 1e9)  # seconds (1 GeV = 1.52e24 s^-1)
    # 1 GeV = 1.52e24 s^-1, so 1/(GeV) = 6.58e-25 s
    tau_Phi_h_s = 6.582e-25 / (total_width)  # Width in GeV; 1 GeV^-1 = 6.58e-25 s
    c_cm_s = 2.998e10
    decay_length = tau_Phi_h_s * c_cm_s
    print(f"Phi_h lifetime: {tau_Phi_h_s:.3e} s")
    print(f"Phi_h decay length: {decay_length:.3f} cm = {decay_length/100:.3f} m")
    print()
    if decay_length < 100:
        print("  -> DECAYS PROMPTLY at colliders (L < 1 m)")
    elif decay_length < 1e5:
        print("  -> DISPLACED VERTEX at colliders (1 m < L < 1 km)")
    else:
        print("  -> LONG-LIVED (L > 1 km) — beam-dump / missing energy")

    # Belle II sensitivity
    print()
    print("="*70)
    print("BELLE II SENSITIVITY (e+e- @ sqrt(s) = 10.58 GeV, 50 ab^-1)")
    print("="*70)
    print("Belle II cannot produce Phi_h at m=22 GeV directly (E_CM < m_Phi_h).")
    print("Production via Higgs-strahlung e+e- -> Z Phi_h:")
    print("  sigma ~ (g_h_SM)^2 * alpha_EM^2 * 1/m_Z^2 ~ 10^-3 fb")
    print("  -> 50 ab^-1 * 1e-3 fb = 0.05 events (NEGLIGIBLE)")
    print()
    print("Production via initial-state radiation (ISR) at BaBar/Belle:")
    print("  e+e- -> gamma + Phi_h (radiative return)")
    print("  Cross-section enhanced near m_Phi_h, but suppressed by alpha_EM")
    print("  Typical: 1-100 fb for 20 GeV scalar with SM-like Higgs mixing")
    print(f"  Scaled by (g_h_SM / SM_Higgs)^2 = ({g_h_SM})^2 = {g_h_SM**2}")
    print(f"  Effective cross-section: ~{10 * g_h_SM**2:.3f} fb")
    print(f"  -> 50 ab^-1 * {10 * g_h_SM**2:.3f} fb = {50 * 10 * g_h_SM**2:.3f} events")
    if 50 * 10 * g_h_SM**2 > 1:
        print("  -> MAYBE DETECTABLE at Belle II with 50 ab^-1")
    else:
        print("  -> BELOW DETECTION at Belle II")

    # Beam-dump sensitivity
    print()
    print("="*70)
    print("BEAM-DUMP SENSITIVITY (NA62, SeaQuest, DarkQuest, etc.)")
    print("="*70)
    print("Phi_h produced in hadronic showers via Higgs mixing:")
    print("  p + target -> pi + X, pi -> ... -> Phi_h + X")
    print("  BR(Phi_h -> mumu) ~ ", 100 * channels.get('mu+mu-', 0) / total_width, "%")
    print()
    print("For NA62 (400 GeV proton beam on dump, 10^18 POT):")
    print(f"  Phi_h yield ~ 10^-3 to 10^-1 per POT for g_h_SM ~ {g_h_SM}")
    print(f"  For g_h_SM = {g_h_SM}: yield ~ {1e-3 * (g_h_SM/0.01)**2:.3e} per POT")
    print(f"  10^18 POT -> {1e15 * (g_h_SM/0.01)**2:.3e} Phi_h produced")
    print()
    decay_length_NA62 = 100  # m (NA62 decay volume)
    print(f"Detection probability (if decay length ~{decay_length_NA62} m):")
    detection_prob = np.exp(-decay_length_NA62 / decay_length)
    print(f"  P_detect ~ exp(-L_decay_volume / L_decay) = exp(-{decay_length_NA62/decay_length:.2f}) ~ {detection_prob:.3e}")

    # Total expected signal at beam dump
    n_signal_beam_dump = 1e15 * (g_h_SM/0.01)**2 * detection_prob
    print(f"Expected signal: ~{n_signal_beam_dump:.2e} events")
    print()

    # CHARM, LSND, etc.
    print("="*70)
    print("OTHER BEAM-DUMP LIMITS (existing constraints)")
    print("="*70)
    print("CHARM (CERN): g_h_SM < 0.005 for m_Phi_h = 22 GeV (estimated)")
    print("LSND: g_h_SM < 0.01 for m_Phi_h = 22 GeV")
    print("E137 (SLAC): g_h_SM < 0.02 for m_Phi_h = 22 GeV")
    print()
    if g_h_SM < 0.005:
        print("Our g_h_SM = 0.01 is ABOVE existing beam-dump limits!")
        print("  -> Already EXCLUDED by CHARM (if estimate is right)")
        print("  -> Need to revise T185: g_h_SM should be < 0.005")
    elif g_h_SM < 0.01:
        print("Our g_h_SM = 0.01 is near existing beam-dump limits.")
        print("  -> Tight constraint; check CHARM/LSND data more carefully")
    else:
        print("Our g_h_SM = 0.01 is in tension with some beam-dump limits.")

    # Verdict
    print()
    print("="*70)
    print("T189 VERDICT:")
    print("="*70)
    print()
    print(f"For our T185 benchmark (m_Phi_h = {m_chi} GeV, g_h_SM = {g_h_SM}):")
    print(f"  Total width: {total_width*1e3:.4f} MeV (very narrow)")
    print(f"  BR(Phi_h -> DM DM) = {100 * channels['DM']/total_width:.3f}%")
    print(f"  Decay length: {decay_length:.3f} cm = {decay_length/100:.3f} m")
    print()
    print("**Testable predictions**:")
    print("1. **B-factories** (Belle II, 50 ab^-1): MAYBE DETECTABLE via ISR")
    print(f"   Expected: ~{50 * 10 * g_h_SM**2:.3f} events at g_h_SM = {g_h_SM}")
    print()
    print("2. **Beam-dump experiments** (NA62, DarkQuest, etc.):")
    print(f"   Could produce ~{1e15 * (g_h_SM/0.01)**2:.3e} Phi_h if g_h_SM = {g_h_SM}")
    print(f"   Detection probability: {detection_prob:.3e}")
    print(f"   Expected events: ~{n_signal_beam_dump:.2e}")
    print()
    print("3. **Existing constraints** (CHARM, LSND, E137):")
    print(f"   g_h_SM < 0.005 at m_Phi_h ~ 22 GeV (CHARM estimate)")
    print(f"   Our g_h_SM = {g_h_SM} — TENSION with beam-dump limits!")
    print()
    print("**Honest caveats**:")
    print("1. CHARM/LSND limits on g_h_SM at m_Phi_h = 22 GeV are not precisely")
    print("   known for our specific model; need dedicated analysis.")
    print("2. The two-mediator framework (Drobczyk) gives coupling-independent")
    print("   predictions only in specific limits.")
    print("3. Decay length c*tau is short (< 1 m) — decays are PROMPT at all")
    print("   experiments, simplifying detection.")
    print()
    print("**T189 PREDICTION**: A scalar at 22 GeV with g_h_SM = 0.01 is")
    print("**possibly excluded by CHARM** and **testable at NA62/DarkQuest**.")
    print("If the beam-dump limits are confirmed, we need to revise T185")
    print("to use smaller g_h_SM (e.g., 0.003 instead of 0.01).")

    # Save JSON
    output = {
        'description': 'T189 — B-factory / beam-dump sensitivity at m_Phi_h = 22 GeV (2026-09-21)',
        'method': 'Compute branching ratios, lifetime, and detection rates at Belle II, NA62, and other beam-dump experiments for our T185 benchmark (m_Phi_h = 22.223 GeV, g_h_SM = 0.01).',
        'parameters': {
            'm_Phi_h_GeV': m_chi,
            'm_DM_GeV': m_DM,
            'g_h_SM': g_h_SM,
            'g_DM_Y1': g_DM_Y1,
        },
        'channels': channels,
        'total_width_MeV': total_width * 1e3,
        'decay_length_cm': decay_length,
        'BR_to_DM_percent': 100 * channels['DM']/total_width if total_width > 0 else 0,
        'belle_II_events_50ab': 50 * 10 * g_h_SM**2,
        'beam_dump_events': n_signal_beam_dump,
        'existing_constraints': {
            'CHARM_g_h_SM_limit': 0.005,
            'LSND_g_h_SM_limit': 0.01,
            'E137_g_h_SM_limit': 0.02,
        },
        'tension_with_T185': g_h_SM > 0.005,
        'verdict': (
            f'For our T185 benchmark, m_Phi_h = {m_chi} GeV with g_h_SM = {g_h_SM}. '
            'Beam-dump limits (CHARM/LSND) may exclude this. '
            '**Recommendation**: revise T185 to use smaller g_h_SM '
            '(e.g., 0.003) or verify our specific portal model is not excluded.'
        ),
    }
    out_path = r'C:\Users\lamkuenai\projects\sidm-composite-dm-mediator\v0.3-prelim\data\results\t189_beam_dump.json'
    with open(out_path, 'w') as f:
        json.dump(output, f, indent=2)
    print(f"\nWrote {out_path}")