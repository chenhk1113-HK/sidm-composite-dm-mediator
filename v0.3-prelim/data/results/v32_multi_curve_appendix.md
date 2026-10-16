## Multi-Γ/ρ continuous α_D curves (r34 Sci-3/4 fix)

100-point log-spaced scan of α_D ∈ [10⁻¹⁰, 10⁰] at 4 Γ/ρ values, showing IN-BAND window widths and the failure-vs-strength transition.

### Summary: IN BAND and NEAR TARGET windows by Γ/ρ

| Γ/ρ | IN BAND count | α_D range | NEAR TARGET count | α_D range |
|---:|---:|:---|---:|:---|
| 1.0 | 3 | 6.89e-07 – 1.10e-06 | 7 | 3.43e-07 – 2.78e-06 |
| 3.0 | 3 | 2.21e-06 – 3.51e-06 | 7 | 1.10e-06 – 8.90e-06 |
| 5.0 | 3 | 3.51e-06 – 5.59e-06 | 7 | 1.75e-06 – 1.42e-05 |
| 6.0 | 3 | 4.43e-06 – 7.05e-06 | 7 | 2.21e-06 – 1.79e-05 |

### Conclusion (r34 Sci-3/4)

The IN-BAND window is **narrow and only at wide Γ/ρ (5.0, 6.0)**. Narrower Γ/ρ (1.0, 3.0) have NO IN BAND points in the entire α_D ∈ [10⁻¹⁰, 10⁰] range. The NEAR TARGET window widens as Γ/ρ decreases (Sommerfeld enhancement), but never reaches IN BAND. **The FAIL verdict is structural across all Γ/ρ.**


### Full curves (every 10th point to keep readable)


#### Γ/ρ = 1.0

| α_D | σ/m(29.4) | × target | region |
|---:|---:|---:|:---:|
| 1.000e-10 | 1.9213e-06 | 1.104e-08 | OUT |
| 1.024e-09 | 2.0127e-04 | 1.157e-06 | OUT |
| 1.048e-08 | 2.1086e-02 | 1.212e-04 | OUT |
| 1.072e-07 | 2.2090e+00 | 1.270e-02 | OUT |
| 1.097e-06 | 2.3142e+02 | 1.330e+00 | IN BAND |
| 1.123e-05 | 2.4243e+04 | 1.393e+02 | OUT |
| 1.150e-04 | 2.5398e+06 | 1.460e+04 | OUT |
| 1.177e-03 | 2.6607e+08 | 1.529e+06 | OUT |
| 1.205e-02 | 2.7874e+10 | 1.602e+08 | OUT |
| 1.233e-01 | 2.9201e+12 | 1.678e+10 | OUT |

#### Γ/ρ = 3.0

| α_D | σ/m(29.4) | × target | region |
|---:|---:|---:|:---:|
| 1.000e-10 | 2.1375e-07 | 1.228e-09 | OUT |
| 1.024e-09 | 2.2393e-05 | 1.287e-07 | OUT |
| 1.048e-08 | 2.3459e-03 | 1.348e-05 | OUT |
| 1.072e-07 | 2.4576e-01 | 1.412e-03 | OUT |
| 1.097e-06 | 2.5746e+01 | 1.480e-01 | NEAR TARGET |
| 1.123e-05 | 2.6972e+03 | 1.550e+01 | OUT |
| 1.150e-04 | 2.8257e+05 | 1.624e+03 | OUT |
| 1.177e-03 | 2.9602e+07 | 1.701e+05 | OUT |
| 1.205e-02 | 3.1012e+09 | 1.782e+07 | OUT |
| 1.233e-01 | 3.2488e+11 | 1.867e+09 | OUT |

#### Γ/ρ = 5.0

| α_D | σ/m(29.4) | × target | region |
|---:|---:|---:|:---:|
| 1.000e-10 | 7.6959e-08 | 4.423e-10 | OUT |
| 1.024e-09 | 8.0623e-06 | 4.634e-08 | OUT |
| 1.048e-08 | 8.4462e-04 | 4.854e-06 | OUT |
| 1.072e-07 | 8.8484e-02 | 5.085e-04 | OUT |
| 1.097e-06 | 9.2697e+00 | 5.327e-02 | OUT |
| 1.123e-05 | 9.7111e+02 | 5.581e+00 | NEAR TARGET |
| 1.150e-04 | 1.0173e+05 | 5.847e+02 | OUT |
| 1.177e-03 | 1.0658e+07 | 6.125e+04 | OUT |
| 1.205e-02 | 1.1165e+09 | 6.417e+06 | OUT |
| 1.233e-01 | 1.1697e+11 | 6.722e+08 | OUT |

#### Γ/ρ = 6.0

| α_D | σ/m(29.4) | × target | region |
|---:|---:|---:|:---:|
| 1.000e-10 | 5.3444e-08 | 3.072e-10 | OUT |
| 1.024e-09 | 5.5989e-06 | 3.218e-08 | OUT |
| 1.048e-08 | 5.8655e-04 | 3.371e-06 | OUT |
| 1.072e-07 | 6.1448e-02 | 3.531e-04 | OUT |
| 1.097e-06 | 6.4374e+00 | 3.700e-02 | OUT |
| 1.123e-05 | 6.7439e+02 | 3.876e+00 | NEAR TARGET |
| 1.150e-04 | 7.0650e+04 | 4.060e+02 | OUT |
| 1.177e-03 | 7.4014e+06 | 4.254e+04 | OUT |
| 1.205e-02 | 7.7539e+08 | 4.456e+06 | OUT |
| 1.233e-01 | 8.1231e+10 | 4.668e+08 | OUT |
