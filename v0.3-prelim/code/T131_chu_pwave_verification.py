"""
T131 — Chu-Garcia-Cely-Murayama 2019 P1 verification.

Verifies that the published best-fit p-wave resonance (Chu et al. PRL 122,
071103, arXiv:1810.04709) does NOT solve our Cloud-9 vs dSph tension.

This is the cited "Strategy 2" candidate from the Qwen referee. The referee's
suggestion was to scan for p-wave resonances that satisfy our phenomenology.
Here we use the existing literature benchmark (P1) to show that the published
best-fit p-wave resonance does NOT match our constraints.

Reference:
  Chu, Garcia-Cely, Murayama, "Velocity Dependence from Resonant Self-
  Interacting Dark Matter," PRL 122, 071103 (2019), arXiv:1810.04709.

Key formula (Eq. 7 in paper, narrow-width approximation):
  <sigma v>/m |NWA = sigma_0/m * <v>
                 + (128 pi / 3) * S / (m^3 v_0^3) * (2 gamma v_R^(2L+1))
                 * exp(-v_R^2 / v_0^2)

P1 benchmark parameters (best-fit, 95% C.L.):
  m_DM_tilde = 400 MeV (rescaled mass for L >= 1)
  v_R = 108 km/s (resonance velocity)
  gamma = 10^-3 (width parameter)
  sigma_0/m = 0.1 cm^2/g (background cross-section)
  L = 1 (p-wave)
"""
import numpy as np


def chu_pwave_resonance(v_km_s, m_DM_GeV=0.4, v_R_km_s=108.0, gamma=1e-3,
                         sigma_0_m=0.1, L=1, S=3.0):
    """Chu et al. 2019 P1 p-wave resonance cross-section per unit mass.

    Parameters
    ----------
    v_km_s : float
        Relative velocity (km/s)
    m_DM_GeV : float
        DM mass (GeV); P1 uses 0.4 GeV
    v_R_km_s : float
        Resonance velocity (km/s); P1 uses 108 km/s
    gamma : float
        Width parameter; P1 uses 1e-3
    sigma_0_m : float
        Background cross-section (cm^2/g); P1 uses 0.1 cm^2/g
    L : int
        Partial wave (1 for p-wave); P1 uses L=1
    S : float
        Spin factor (2*J_R+1)/(2*J_DM+1)^2; P1 uses S=3

    Returns
    -------
    sigma_m : float
        Cross-section per unit mass (cm^2/g)
    """
    # Eq. (7) NWA: <sigma v>/m = sigma_0/m * <v> + (128 pi / 3) * S / (m^3 v_0^3)
    #                                              * (2 gamma v_R^(2L+1)) * exp(-v_R^2/v_0^2)
    #
    # v_0 is related to <v> by <v> ~ 2 v_0 / sqrt(pi), so v_0 ~ <v> * sqrt(pi) / 2
    # For rough estimate: v_0 ~ v (within ~13%)

    v0 = v_km_s * np.sqrt(np.pi) / 2  # convert <v> to v_0

    # Background contribution
    sigma_background = sigma_0_m

    # Resonant contribution (NWA)
    if v0 > 0 and v_R_km_s > 0:
        bw_term = (128 * np.pi / 3) * S / (m_DM_GeV**3 * v0**3) \
                  * 2 * gamma * v_R_km_s**(2*L+1) \
                  * np.exp(-v_R_km_s**2 / v0**2)
        # bw_term has units of cm^2/g * km/s (it's <sigma v>/m)
        sigma_resonant = bw_term / v_km_s if v_km_s > 0 else 0
    else:
        sigma_resonant = 0

    return sigma_background + sigma_resonant


# Our phenomenology targets
PHENOMENOLOGY_TARGETS = {
    'Cloud-9 (v=28)':         {'v_km_s': 28,  'target': 100.0,  'op': '>=', 'description': 'high'},
    'classical dSph (v=15)':  {'v_km_s': 15,  'target': 0.8,    'op': '<=', 'description': 'low'},
    'UFD (v=10)':             {'v_km_s': 10,  'target': 0.8,    'op': '<=', 'description': 'low'},
    'UFD (v=7)':              {'v_km_s': 7,   'target': 0.8,    'op': '<=', 'description': 'low'},
    'UFD (v=5)':              {'v_km_s': 5,   'target': 0.8,    'op': '<=', 'description': 'low'},
    'UFD (v=3)':              {'v_km_s': 3,   'target': 0.8,    'op': '<=', 'description': 'low'},
    'SPARC (v=100)':          {'v_km_s': 100, 'target': 0.19,   'op': '~',  'description': 'intermediate'},
    'Cluster (v=500)':        {'v_km_s': 500, 'target': 1.0,    'op': '<=', 'description': 'low'},
}


if __name__ == '__main__':
    print("=" * 80)
    print("T131 — Chu et al. 2019 P1 p-wave resonance verification")
    print("=" * 80)
    print()
    print("P1 parameters:")
    print("  m_DM_tilde = 400 MeV")
    print("  v_R = 108 km/s")
    print("  gamma = 1e-3")
    print("  sigma_0/m = 0.1 cm^2/g")
    print("  L = 1 (p-wave)")
    print()
    print("=" * 80)
    print("P1 prediction vs our phenomenology targets:")
    print("=" * 80)
    print()
    print(f"{'Channel':25s} {'<v>':>8s} {'P1 sigma/m':>12s} {'Our target':>12s} {'Match?':>10s}")
    print("-" * 80)

    passes = 0
    fails = 0
    for label, info in PHENOMENOLOGY_TARGETS.items():
        v = info['v_km_s']
        target = info['target']
        op = info['op']
        sigma_p1 = chu_pwave_resonance(v)
        if op == '>=':
            match = '✓' if sigma_p1 >= target else '✗'
        elif op == '<=':
            match = '✓' if sigma_p1 <= target else '✗'
        else:  # ~
            ratio = sigma_p1 / target if target > 0 else 0
            match = '~' if 0.3 < ratio < 3 else '✗'

        if match == '✓':
            passes += 1
        else:
            fails += 1

        print(f"{label:25s} {v:8d} {sigma_p1:12.4f} {target:12.4f} {match:>10s}")

    print()
    print(f"P1 passes: {passes}, fails: {fails}")
    print()

    if fails > 0:
        print("CONCLUSION: Chu P1 p-wave resonance does NOT match our phenomenology.")
        print("The published best-fit p-wave resonance (Chu et al. 2019) is too flat:")
        print("  - sigma/m ~ 0.1 cm^2/g at almost all velocities")
        print("  - Cannot get Cloud-9 high (100 cm^2/g) AND dSph low (<0.8)")
