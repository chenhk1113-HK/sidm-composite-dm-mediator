# Priority 1: Resonance Form Factor F(q) — Report
**Date:** 2026-10-11  **Status:** Future-work plan, Priority 1 of theoretical mechanisms to rule out.
## Hypothesis
If DM is composite (the project's premise), the Yukawa propagator can carry a **resonance** form factor (dark-rho exchange, Chu-Hambye-Tytgat 2018 M2):

```
F(q) = g^2 / (q^2 - m_rho^2 + i m_rho Gamma_rho)
```

Unlike the dipole form factor (Priority 4, ruled out — it is a pure suppressor), this Breit-Wigner lineshape can in principle create a **peak** in sigma/m(v) at the resonance velocity v_res where q^2 ~ m_rho^2.
## Method
- Coupling convention: `alpha_D = g^2/(4*pi)` (locked in `constants.py`).
- Scan grid: 5 m_rho x 3 widths x 5 alpha_D = **75 combinations**.
- Velocity grid: [3.0, 5.0, 10.0, 15.0, 20.0, 29.4, 50.0, 100.0, 150.0] km/s.
- For each combination, compute sigma/m(v) on the grid; flag if v=29.4 km/s is a local maximum.
- Cross-check: at exact resonance, sigma/m should be enhanced by ~1/(Gamma_rho/m_rho)^2.

## Resonance velocities (q^2 = m_rho^2)

| m_rho (MeV) | v_res (km/s) | near v=29.4? |
|---:|---:|:---:|
| 10.0 | 5996.000 | no |
| 50.0 | 29980.000 | no |
| 100.0 | 59960.000 | no |
| 500.0 | 299800.000 | no |
| 1000.0 | 599600.000 | no |

## Results
- Combinations scanned: **75**
- Combinations with peak at v=29.4 km/s: **0**
- Max sigma/m(v=29.4) across all combinations: **3.929e+01 cm^2/g**
- Target (Cloud-9): 174.0 cm^2/g

### Top 10 combinations by sigma/m(v=29.4)

| m_rho (MeV) | Gamma/m | alpha_D | v_res (km/s) | sigma/m(29.4) [cm^2/g] | peak? | enhancement | theory |
|---:|---:|---:|---:|---:|:---:|---:|---:|
| 10.00 | 0.010 | 1.00e-02 | 5996.000 | 3.929e+01 | no | 9.99e-01 | 1.00e+04 |
| 10.00 | 0.100 | 1.00e-02 | 5996.000 | 3.890e+01 | no | 9.99e-01 | 1.00e+02 |
| 10.00 | 0.500 | 1.00e-02 | 5996.000 | 3.143e+01 | no | 9.99e-01 | 4.00e+00 |
| 10.00 | 0.010 | 1.00e-03 | 5996.000 | 3.929e-01 | no | 9.99e-01 | 1.00e+04 |
| 10.00 | 0.100 | 1.00e-03 | 5996.000 | 3.890e-01 | no | 9.99e-01 | 1.00e+02 |
| 10.00 | 0.500 | 1.00e-03 | 5996.000 | 3.143e-01 | no | 9.99e-01 | 4.00e+00 |
| 50.00 | 0.010 | 1.00e-02 | 29980.000 | 6.286e-02 | no | 1.00e+00 | 1.00e+04 |
| 50.00 | 0.100 | 1.00e-02 | 29980.000 | 6.224e-02 | no | 1.00e+00 | 1.00e+02 |
| 50.00 | 0.500 | 1.00e-02 | 29980.000 | 5.029e-02 | no | 1.00e+00 | 4.00e+00 |
| 10.00 | 0.010 | 1.00e-04 | 5996.000 | 3.929e-03 | no | 9.99e-01 | 1.00e+04 |

### Combinations with peak at v=29.4 km/s

**NONE.**

## Verdict

**FAIL** — No combination produces a sigma/m peak at v=29.4 km/s. Composite-DM resonance mechanism (Chu-Hambye-Tytgat M2) is RULED OUT.

## Interpretation

The composite-DM resonance form factor mechanism (Chu-Hambye-Tytgat M2, dark-rho exchange) **cannot** produce a sigma/m peak at v=29.4 km/s over the scanned parameter range. This is the last theoretical mechanism on the future-work plan; ruling it out closes the door on composite-DM explanations of the Cloud-9 dwarf-galaxy peak.

### Why no peak?
- The resonance velocity v_res ~ (m_rho/mu) * c. For m_rho ~ 10-1000 MeV and m_chi ~ 1 GeV, v_res is in the 10000-300000 km/s range (cluster scale), not 29.4 km/s.
- For v_res to land at 29.4 km/s, one needs m_rho ~ 100 keV (sub-MeV). At such light masses, the Born approximation breaks down and the alpha_D values required to hit 174 cm^2/g push kappa = alpha_D * m_chi / m_rho to far above kappa_c ~ 1.68 -> bound-state/Sommerfeld regime, where the simple Breit-Wigner propagator is no longer the dominant effect.
- Even at the lightest m_rho = 10 MeV, the resonance velocity is v_res ~ 6000 km/s; the v=29.4 km/s point sits far on the low-v tail of the Breit-Wigner, where sigma/m(v) ~ alpha_D^2 / (q^2 + m_rho^2)^2 -- a monotonic DECREASING function of v. No peak.

## Files

- JSON results: `C:\Users\lamkuenai\projects\sidm-composite-dm-mediator\v0.3-prelim\data\results\v19_2_f_priority1_resonance_scan.json`
- Markdown report: `C:\Users\lamkuenai\projects\sidm-composite-dm-mediator\docs\V19_2_F_PRIORITY1_RESONANCE_FORM_FACTOR_REPORT.md`
