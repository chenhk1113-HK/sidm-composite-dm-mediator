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
- Scan grid: 10 m_rho x 3 widths x 5 alpha_D = **150 combinations**.
- Velocity grid: [3.0, 5.0, 10.0, 15.0, 20.0, 29.4, 50.0, 100.0, 150.0] km/s.
- For each combination, compute sigma/m(v) on the grid; flag if v=29.4 km/s is a local maximum.
- Cross-check: at exact resonance, sigma/m should be enhanced by ~1/(Gamma_rho/m_rho)^2.

## Resonance velocities (q^2 = m_rho^2)

| m_rho (MeV) | v_res (km/s) | near v=29.4? |
|---:|---:|:---:|
| 0.0 | 5.996 | no |
| 0.1 | 29.980 | YES |
| 0.1 | 59.960 | no |
| 0.5 | 299.800 | no |
| 1.0 | 599.600 | no |
| 10.0 | 5996.000 | no |
| 50.0 | 29980.000 | no |
| 100.0 | 59960.000 | no |
| 500.0 | 299800.000 | no |
| 1000.0 | 599600.000 | no |

## Results
- Combinations scanned: **150**
- Combinations with peak at v=29.4 km/s: **15**
- Max sigma/m(v=29.4) across all combinations: **1.227e+13 cm^2/g**
- Target (Cloud-9): 174.0 cm^2/g

### Top 10 combinations by sigma/m(v=29.4)

| m_rho (MeV) | Gamma/m | alpha_D | v_res (km/s) | sigma/m(29.4) [cm^2/g] | peak? | enhancement | theory |
|---:|---:|---:|---:|---:|:---:|---:|---:|
| 0.05 | 0.010 | 1.00e-02 | 29.980 | 1.227e+13 | YES | 1.59e+02 | 1.00e+04 |
| 0.05 | 0.100 | 1.00e-02 | 29.980 | 1.678e+12 | YES | 2.25e+01 | 1.00e+02 |
| 0.05 | 0.010 | 1.00e-03 | 29.980 | 1.227e+11 | YES | 1.59e+02 | 1.00e+04 |
| 0.05 | 0.500 | 1.00e-02 | 29.980 | 7.651e+10 | YES | 1.80e+00 | 4.00e+00 |
| 0.01 | 0.010 | 1.00e-02 | 5.996 | 2.700e+10 | no | 1.93e-04 | 1.00e+04 |
| 0.01 | 0.100 | 1.00e-02 | 5.996 | 2.700e+10 | no | 2.13e-04 | 1.00e+02 |
| 0.01 | 0.500 | 1.00e-02 | 5.996 | 2.698e+10 | no | 7.11e-04 | 4.00e+00 |
| 0.05 | 0.100 | 1.00e-03 | 29.980 | 1.678e+10 | YES | 2.25e+01 | 1.00e+02 |
| 0.10 | 0.010 | 1.00e-02 | 59.960 | 3.119e+09 | no | 2.23e-01 | 1.00e+04 |
| 0.10 | 0.100 | 1.00e-02 | 59.960 | 3.066e+09 | no | 2.42e-01 | 1.00e+02 |

### Combinations with peak at v=29.4 km/s

| m_rho (MeV) | Gamma/m | alpha_D | sigma/m(29.4) [cm^2/g] | ratio to 174 |
|---:|---:|---:|---:|---:|
| 0.05 | 0.010 | 1.00e-02 | 1.227e+13 | 70509629207.4365 |
| 0.05 | 0.100 | 1.00e-02 | 1.678e+12 | 9642164494.7476 |
| 0.05 | 0.010 | 1.00e-03 | 1.227e+11 | 705096292.0744 |
| 0.05 | 0.500 | 1.00e-02 | 7.651e+10 | 439733681.7642 |
| 0.05 | 0.100 | 1.00e-03 | 1.678e+10 | 96421644.9475 |
| 0.05 | 0.010 | 1.00e-04 | 1.227e+09 | 7050962.9207 |
| 0.05 | 0.500 | 1.00e-03 | 7.651e+08 | 4397336.8176 |
| 0.05 | 0.100 | 1.00e-04 | 1.678e+08 | 964216.4495 |
| 0.05 | 0.010 | 1.00e-05 | 1.227e+07 | 70509.6292 |
| 0.05 | 0.500 | 1.00e-04 | 7.651e+06 | 43973.3682 |
| 0.05 | 0.100 | 1.00e-05 | 1.678e+06 | 9642.1645 |
| 0.05 | 0.010 | 1.00e-06 | 1.227e+05 | 705.0963 |
| 0.05 | 0.500 | 1.00e-05 | 7.651e+04 | 439.7337 |
| 0.05 | 0.100 | 1.00e-06 | 1.678e+04 | 96.4216 |
| 0.05 | 0.500 | 1.00e-06 | 7.651e+02 | 4.3973 |

## Verdict

**PARTIAL** — 15 combination(s) produce a peak at v=29.4 km/s, but none reach sigma/m ~ 174 cm^2/g (max: 1.227e+13). Resonance mechanism is technically viable but cannot explain Cloud-9.

## Interpretation

Some combinations produce a peak at v=29.4 km/s, but none reach the Cloud-9 target sigma/m ~ 174 cm^2/g. The composite-DM resonance mechanism is technically viable but cannot explain the observed peak height.

## Files

- JSON results: `C:\Users\lamkuenai\projects\sidm-composite-dm-mediator\v0.3-prelim\data\results\v19_2_f_priority1_resonance_scan.json`
- Markdown report: `C:\Users\lamkuenai\projects\sidm-composite-dm-mediator\docs\V19_2_F_PRIORITY1_RESONANCE_FORM_FACTOR_REPORT.md`
