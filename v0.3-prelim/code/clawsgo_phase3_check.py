#!/usr/bin/env python3
"""
Phase-3 check — does a low-velocity Sommerfeld/t-channel resonance exist in the
region the project's own Phase-3 scan did NOT cover?

The project's Phase-3 scan used m_A'/m_chi in [0.01, 2.0]  (m_A' in [10 MeV, 2 GeV])
and concluded "gate FAILS".  Its own WHY paragraph says a resonance at v = 29.4 km/s
needs m_A' <~ 50 keV -- i.e. 200x BELOW the lowest scanned mass.  The framework's
named mediator (200 eV) is also outside the scan.

Here we run the validated variable-phase partial-wave solver over the UNSCANNED
region  m_A' in [1 keV, 100 keV], and ask directly: for some (alpha_D, m_A'), is
there a peak in sigma/m(v) at v ~ 29.4 km/s?

Units: natural (hbar=c=1), masses/energies in GeV, v in units of c.
"""
import numpy as np
from scipy.integrate import solve_ivp
from scipy.special import spherical_jn, spherical_yn

M_CHI = 1.0
MU = M_CHI / 2.0
V_KMS = 299792.458
HBARC = 1.973269804e-14
GEV_TO_G = 1.78266192e-24
CM2_PER_GEV2 = HBARC**2


def sigma_m_cm2_g(sigT):
    return sigT * CM2_PER_GEV2 / (M_CHI * GEV_TO_G)


def _lmax_for(k, m_phi, cap=400):
    return min(int(np.ceil(4.0 * k / m_phi)) + 6, cap)


def sigma_T_partialwave(alpha, m_phi, v, n_r=6000):
    """sigma_T via variable-phase (Calogero); returns nan if l_max unmanageable."""
    k = MU * v
    l_max = _lmax_for(k, m_phi)
    if l_max >= 400:                      # free-function overflow regime
        return np.nan
    ls = np.arange(l_max + 1)
    r_max = max(8.0 / m_phi, 8.0 / k)
    r0 = min(0.02 / m_phi, 0.05 / k)
    r = np.linspace(r0, r_max, n_r)

    def rhs(rr, d):
        V = -alpha * np.exp(-m_phi * rr) / rr
        x = k * rr
        F = x * spherical_jn(ls, x)
        G = -x * spherical_yn(ls, x)
        return -(2.0 * MU / k) * V * (np.cos(d) * F - np.sin(d) * G)**2

    sol = solve_ivp(rhs, [r[0], r[-1]], np.zeros(l_max + 1), t_eval=r,
                    rtol=1e-9, atol=1e-12, method="RK45")
    if not sol.success:
        return np.nan
    d = np.append(sol.y[:, -1], 0.0)
    l = np.arange(len(d) - 1)
    return (4.0 * np.pi / k**2) * np.sum((l + 1) * np.sin(d[:-1] - d[1:])**2)


def resonance_map(m_phi, alphas, vs):
    """Return sigma/m(v) grid and, per alpha, the v of the peak in the window."""
    out = {}
    for a in alphas:
        sm = np.array([sigma_m_cm2_g(sigma_T_partialwave(a, m_phi, v / V_KMS))
                       for v in vs])
        if np.all(np.isnan(sm)):
            out[a] = (np.nan, np.nan, sm)
            continue
        ipk = np.nanargmax(sm)
        out[a] = (vs[ipk], sm[ipk], sm)
    return out


def main():
    print("Phase-3 check: resonance scan in the UNSCANNED region m_A' in [1, 100] keV")
    print(f"m_chi = {M_CHI} GeV, mu = {MU} GeV.  Target v_res = 29.4 km/s.\n")
    vs = np.array([5, 10, 20, 29.4, 60, 200.0])
    alphas = [1e-4, 3e-3, 1e-2, 0.1]

    for m_keV in [10.0, 50.0]:
        m_phi = m_keV * 1e-6      # keV -> GeV
        # parameter that controls resonance structure
        print(f"### m_A' = {m_keV:g} keV   (kappa = m_A'/m_chi = {m_phi:.2e})")
        print("| alpha_D | alpha*m_chi/m_A' | v_peak [km/s] | sigma/m(v_peak) | sigma/m(v=29.4) |")
        print("|---|---|---|---|---|")
        for a in alphas:
            res = resonance_map(m_phi, [a], vs)[a]
            vpk, spk, sm = res
            sm29 = sm[np.argmin(np.abs(vs - 29.4))]
            ratio = a / m_phi
            print(f"| {a:.0e} | {ratio:.3g} | {vpk:.4g} | {spk:.4g} | {sm29:.4g} |")
        print()


if __name__ == "__main__":
    main()
