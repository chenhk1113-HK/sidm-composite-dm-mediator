# T120.11.B/C — σ/v curve and excited state abundance (2026-09-19)

## What comment12.docx asked

Reviewer (comment12.docx 2026-09-19) raised 3 specific points:

1. **Mass scale consistency**: Confirm α_D=0.0015, m_A'=30 MeV, Δm=10 MeV
   reproduce target σ/m(v) for Cloud-9, SPARC, cluster
2. **Full σ/m(v) curve**: Show 3-30 km/s window with pseudo-Dirac dynamics
3. **Excited-state abundance**: Quantify χ_2 population today, BBN/CMB constraints

## Response

### Point 1: Mass scale consistency ✓

The pseudo-Dirac Yukawa component (with α_D=0.0015, m_A'=30 MeV, Δm=10 MeV)
gives σ/m in the range 0.03-0.5 cm²/g (see table below). This is comparable
to Phase 44's required σ_0 = 0.052 cm²/g. The BW peaks (which are NOT
affected by pseudo-Dirac) provide additional σ/m at v=29, 100, 178, 430, 768 km/s.

The full σ/m(v) is: σ(m) = σ_Yukawa_pseudo_Dirac(v) + Σ σ_BW_peaks(v)

| v (km/s) | σ_pseudo_Dirac | σ_total (+BW) | σ_eff (2C+grav) | Observation | Status |
|---|---|---|---|---|---|
| 3 | 0.44 | 0.44 | 0.04 | <0.8 | ✓ |
| 5 | 0.34 | 0.34 | 0.09 | <0.8 | ✓ |
| 7 | 0.29 | 0.29 | 0.07 | <0.8 | ✓ |
| 10 | 0.24 | 0.24 | 0.05 | <0.8 | ✓ |
| 15 | 0.20 | 0.20 | 0.03 | <0.8 | ✓ |
| **28** | **0.14** | **177.5** (BW peak) | **128** | **≥100** | **✓** |
| 100 | 0.08 | 0.46 | 0.19 | ∈[0.05, 0.5] | ✓ |
| 500 | 0.03 | 0.03 | 0.0002 | <1.0 | ✓ |

The pseudo-Dirac does NOT degrade Cloud-9 (the BW peak at v=29 dominates).

### Point 2: Full σ/m(v) curve in 3-30 km/s window ✓

Computed in `t120_11_hidden_u1_uv.py::zhang2016_self_scattering`. The
velocity dependence in the pseudo-Dirac model:

| v (km/s) | σ/m (cm²/g) | note |
|---|---|---|
| 3 | 0.44 | extreme UFD |
| 5 | 0.34 | UFD |
| 7 | 0.29 | |
| 10 | 0.24 | |
| 15 | 0.20 | classical dSph |
| 28 | 0.14 | Cloud-9 (but BW peak dominates) |

The σ/m(v) decreases with increasing v (slight 1/v dependence). All values
are below the dSph/UFD limit of 0.8 cm²/g, so the pseudo-Dirac Yukawa
component ALONE satisfies the low-v constraints. The two-component +
gravothermal selection then brings it down further to 0.03-0.16 cm²/g.

### Point 3: Excited-state abundance ✓

The χ_2 excited state can be populated thermally if kT > Δm. With Δm = 10 MeV:

| Era | T | Δm/T | n_χ2/n_χ1 |
|---|---|---|---|
| Early universe | 1 GeV | 0.01 | ~1 (in equilibrium) |
| BBN | 1 MeV | 10 | exp(-10) ~ 5×10⁻⁵ |
| Recombination | 0.26 eV | 4×10⁷ | ~0 |
| Today | 0.0001 eV | 10¹¹ | ~0 |

**Conclusion**: At all relevant epochs (BBN, recombination, today),
the χ_2 excited state is **exponentially suppressed**:
n_χ2/n_χ1 ≈ exp(-Δm/kT) ≈ 0

This means:
- No BBN constraint from χ_2 → χ_1 + γ_eff decays
- No CMB constraint from χ_2 injection
- No late-time down-scattering signals (which would otherwise evade our Δm kinematic protection)

The pseudo-Dirac excited-state fraction is **completely negligible** at
all cosmological epochs relevant for current observations.

## Hierarchy of claims (point 5 of comment12.docx)

The reviewer emphasized keeping the claim hierarchy explicit:

1. **T120.1–T120.7 (phenomenological)**: Multi-component DM + gravothermal
   core-collapse selection + Gaussian BW + flattened background slope
   → **resolves** the Cloud-9 vs UFD/dSph tension. **CORE RESULT**

2. **T120.9a (statistical)**: MCMC refit verifies the phenomenological
   parameters. ΔBIC = -170 (T120 WINS by Occam)

3. **T120.11 (UV completion)**: Hidden U(1) + pseudo-Dirac mass splitting
   makes the phenomenological model UV-complete AND evades direct
   detection. **Complementary** to (1), not the origin of multi-scale resolution.

## What's still imperfect

- Pseudo-Dirac Yukawa ALONE gives σ/m(v=15) = 0.20 cm²/g (passes 0.8 limit)
  but if we used ONLY this without two-component + gravothermal, we'd be at
  the edge of the limit. The two-component treatment gives extra safety margin.
- The pseudo-Dirac framework doesn't predict the BW peaks (those come from
  resonant structure, separate UV physics).
- The kinetic mixing ε is needed for direct-detection cross-section; origin
  of ε is open (string theory, anomaly cancellation, etc.)

## Files updated

- `v0.3-prelim/docs/PAPER_V1_DRAFT.md` §9.8.2: added "Important clarification"
  paragraph + §9.8.3 NEW hierarchy of claims
- `v0.3-prelim/docs/T120_11_JOINT_FIT_VERIFICATION.md` (THIS FILE)
- `v0.3-prelim/code/t120_11_hidden_u1_uv.py`: contains σ/v curve function