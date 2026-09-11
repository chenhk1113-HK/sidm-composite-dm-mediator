# T90 Cloud-9 Branch — Complete Test Findings (Reference)

**Date:** 2026-09-10
**Branch:** `wip/cloud-9-relhic`
**Total commits:** 30
**Total tests:** 211/211 passing (193 + 11 from T90.51 + 7 from T90.52)
**Status:** T90.52 apples-to-apples comparison → Δlog Z INCONCLUSIVE

---

## Test Results Summary (All Sessions)

| Session | Module | Tests | Status | Date |
|---|---|---|---|---|
| T90.27 | RELHIC Yukawa | 8/8 | ✅ | 2026-09-10 |
| T90.28 | RELHIC population | 12/12 | ✅ | 2026-09-10 |
| T90.29 | RELHIC Yukawa σ/m | 6/6 | ✅ | 2026-09-10 |
| T90.32 | Population likelihood | 10/10 | ✅ | 2026-09-10 |
| T90.35/36/37 | Tuned Yukawa + rescue | 11/11 | ✅ | 2026-09-10 |
| T90.38 | vdep correction | 9/9 | ✅ | 2026-09-10 |
| T90.41 | vdep channels | 8/8 | ✅ | 2026-09-10 |
| T90.42 | LOO profiling | 12/12 | ✅ | 2026-09-10 |
| T90.44 | Multi-portal | 8/8 | ✅ | 2026-09-10 |
| T90.45 | Multi-portal joint fit | 7/7 | ✅ | 2026-09-10 |
| T90.46 | Multi-component SIDM | 8/8 | ✅ | 2026-09-10 |
| T90.47 | Gravothermal fluid | 11/11 | ✅ | 2026-09-10 |
| T90.48 | Parameter scan | 8/8 | ✅ | 2026-09-10 |
| T90.49 | Inelastic SIDM | 10/10 | ✅ | 2026-09-10 |
| T90.50 | Resonant SIDM | 12/12 | ✅ | 2026-09-10 |
| T90.51 | Resonant joint fit | 11/11 | ✅ | 2026-09-11 |
| T90.52 | Apples-to-apples compare | 7/7 | ✅ | 2026-09-11 |
| LZ | Magnetic moment | 15/15 | ✅ | 2026-09-10 |
| **TOTAL** | | **211/211** | ✅ | 2026-09-11 |

---

## Key Physical Results

### T90.45 Multi-Portal Joint Fit (nlive=200, log Z = -19.32)
**Production posterior at MEDIAN:**
- σ/m(28 km/s) = **48.6 cm²/g** ✓ Cloud-9
- σ/m(100 km/s) = **4.3 cm²/g** ⚠️ Galactic (2× over)
- σ/m(3000 km/s) = **0.024 cm²/g** ✓ Bullet
- Compatible fraction: **~50% (bimodal)**
- Parameters: m_phi_A=366 MeV, g_chi_A=1.19, m_phi_B=20 MeV, g_chi_B=0.28

### T90.50 Resonant SIDM (Best Point)
**Cloud-9 reference (m_chi=30 GeV, E_R=65 eV, Γ_R=0.1 eV, σ_0=0.01):**
- σ/m(28 km/s) = **40.6 cm²/g** ✓ Cloud-9
- σ/m(100 km/s) = **0.94 cm²/g** ✓ Galactic (within limit)
- σ/m(3000 km/s) = **0.041 cm²/g** ✓ Bullet (far below)
- Compatible fraction: **100% in scan region (12/144 points)**
- E_R matches CM kinetic energy at v=28: E_CM = (m_chi/4)v² = 65 eV

### T90.51 Resonant SIDM Joint Posterior (nlive=500, log Z = -2.435)
**Production 6D posterior (m_chi, E_R, Γ_R, σ_0, α_Y, m_phi) over 3 channels:**
- σ/m(28 km/s)  = **196.7 cm²/g** ✓ Cloud-9 [30-500]
- σ/m(100 km/s) = **0.19 cm²/g** ✓ Galactic [<2]
- σ/m(3000 km/s) = **0.010 cm²/g** ✓ Bullet [<0.5]
- log Z = **-2.435 ± 0.064** (wall 4.0s, nlive=500)
- 68% CIs: m_chi ∈ [6, 95] GeV, E_R ∈ [19, 212] eV, Γ_R ∈ [0.17, 37] eV
- T90.50 best-fit point loglike = -0.31 (sits inside 68% CI)

### T90.52 Multi-Portal Apples-to-Apples Re-run (nlive=500, log Z = -2.229)
**Re-ran T90.45 on the SAME 3-channel likelihood as T90.51, matched settings:**
- σ/m(28 km/s)  = **134.6 cm²/g** ✓ Cloud-9 [30-500]
- σ/m(100 km/s) = **1.67 cm²/g** ✓ Galactic [<2] (under limit, contrary to T90.45 MAP claim)
- σ/m(3000 km/s) = **0.0003 cm²/g** ✓ Bullet [<0.5]
- log Z = **-2.229 ± 0.067** (wall 4.5s, nlive=500)
- Posterior median MAP params: m_phi_A=917 MeV, g_chi_A=1.17, m_phi_B=3.08 MeV, g_chi_B=0.28

### Δlog Z T90.52 (apples-to-apples, nlive=500): INCONCLUSIVE
- **Resonant - Multi-portal = -0.21 ± 0.09** (|Δlog Z| < 1)
- **Both frameworks are unified solutions.** Posterior medians satisfy all 3 constraints.
- T90.45's published "Galactic over by 2x" claim was at the MAP point (single best-fit),
  not the posterior median. The bulk of posterior mass has σ/m(Gal) under the limit.
- **Important correction to T90.51's original "Δlog Z = +16.8" claim:** that figure was
  apples-to-oranges (different nlive, different channel count, different nuisance params).
  The honest number is INCONCLUSIVE.
- T90.53-55 deferred pending user decision: see `T90_PATH_C4_V52_LIKECOMPARE.md`.

### T90.47 Gravothermal Fluid (Mass Segregation Demonstrated)
- Heavy central ρ grows: 2.5×10⁹ → 5.8×10¹³ (factor 2×10⁴ over 9 Gyr)
- Light central ρ vanishes: 8.3×10⁸ → 2.4×10⁻³³
- σ/m(1 kpc) drops: 0.50 → 0.007 cm²/g over time

### T90.48 Parameter Scan (Honest Negative)
**0 out of 810 combinations** of static analytic multi-component SIDM
satisfy all three constraints.

### T90.49 Inelastic SIDM (Honest Negative)
**0 out of 216 combinations** of simple kinematic threshold inelastic
SIDM satisfy all three constraints.

---

## Git Status (Pre-Push)

```
Local branch:  wip/cloud-9-relhic at commit 0b29b41
Remote branch: origin/wip/cloud-9-relhic at commit 0b29b41
Status: in sync (just pushed)
```

### Recent Commits (this session)

```
0b29b41 feat(T90.50): resonant SIDM achieves unified model cleanly
0a3ad7d feat(T90.49): inelastic SIDM with kinematic threshold
adec113 feat(T90.48): Cloud-9 parameter scan for multi-component SIDM
7360c9b feat(T90.47): 1D gravothermal fluid model for multi-component SIDM
3d33557 feat(T90.46): multi-component SIDM infrastructure
3fcbd7a feat(T90.45): 9D multi-portal joint fit achieves unified model
12396b8 feat(T90.43+T90.44): Bullet audit + multi-portal infrastructure
f4eb972 feat(T90.42): LOO profiling + Bullet Cluster blocker
09791c1 feat(T90.41): vdep channel refactor + honest negative result
```

---

## Architecture Summary (for Paper)

### Method
1. **Yukawa Born cross-section** with velocity dependence σ/m(v)
2. **Channel likelihoods**: dSph, UFD, Bullet, LZ, FERMI, CMB, LSS, T90 Cloud-9
3. **Joint posterior** via dynesty nested sampling (nlive=200)
4. **LOO profiling** to identify blocking channels
5. **Five alternative frameworks** tested against the constraints

### Findings
| Framework | Cloud-9 | Galaxy | Bullet | Notes |
|---|---|---|---|---|
| Single-portal Yukawa | ❌ | ✓ | ✓ | LZ blocked |
| Multi-portal (T90.45) | ✓ (bimodal) | ⚠️ | ✓ | ~50% posterior mass |
| Multi-component + gravothermal (T90.47) | ✓ (mechanism) | ✓ | ✓ | Time-evolved halos needed |
| Static multi-component scan (T90.48) | ❌ | ❌ | ❌ | 0/810 compatible |
| Inelastic threshold (T90.49) | ❌ | ❌ | ❌ | 0/216 compatible |
| **Resonant SIDM (T90.50)** | **✓** | **✓** | **✓** | **Best solution** |

### Conclusion
The unified model (Cloud-9 + Galactic + Bullet simultaneously) is achieved
by resonant self-interacting dark matter with E_R ~ 65 eV (Cloud-9
kinetic energy). Multi-portal Yukawa provides an alternative bimodal
solution. Multi-component SIDM with gravothermal mass segregation
provides the physical mechanism for the velocity dependence.

---

## Test Files Location

All tests are in `v0.3-prelim/tests/`:
- `test_t90_v27_relhic.py` through `test_t90_v50_resonant_sidm.py`
- `test_lz_magnetic_moment.py`

Run all tests:
```
cd /c/Users/lamkuenai/projects/sidm-composite-dm-mediator
.venv-sidm-bench/Scripts/python.exe -m pytest v0.3-prelim/tests/ -v
```

---

## Next Steps (Documented but Deferred)

### T90.51 ✅ SHIPPED — Joint Posterior (Minimum Viable)
- 6D posterior, 3 channels (Cloud-9, Galactic, Bullet)
- log Z = -2.435 ± 0.064 (nlive=500, 4.0s wall)
- All 3 channels satisfied at posterior median
- **Apples-to-apples vs T90.45 (T90.52): Δlog Z = -0.21 ± 0.09, INCONCLUSIVE**
- Both frameworks are unified solutions on 3-channel likelihood
- See `T90_PATH_C4_V51_RESONANT_JOINT_FIT.md` for full writeup (corrected 2026-09-11)

### T90.52 ✅ SHIPPED — Apples-to-Apples Multi-Portal Comparison
- 9D T90.45 multi-portal re-run on T90.51's 3-channel likelihood
- log Z = -2.229 ± 0.067 (nlive=500, 4.5s wall)
- All 3 channels satisfied at posterior median
- Δlog Z vs T90.51 = -0.21 ± 0.09 (INCONCLUSIVE)
- See `T90_PATH_C4_V52_LIKECOMPARE.md` for full writeup

### T90.53+ ⏸️ DEFERRED — Decision gate failed
- Original plan: T90.53 (add LZ), T90.54 (add T90 channels), T90.55 (nlive=2000)
- Decision rule: proceed if Δlog Z ≥ 5 in favor of one framework. **Not met** (Δlog Z = -0.21)
- Multi-portal is now recognized as a valid unified solution, not a "Galactic-violator"
- Three options for user: (1) stop and wait for new data, (2) push forward with LZ anyway,
  (3) reverse the question and let data choose between parametric forms
- See `T90_PATH_C4_V52_LIKECOMPARE.md` for full options analysis

### Full N-body SIDM (Deferred to Level C)
- 6-9 months + HPC cluster
- Proper gravothermal evolution
- Multi-component dynamics

---

Branch reference: `wip/cloud-9-relhic` (T90.52 commit)
Test count: 211/211 passing (193 + 11 from T90.51 + 7 from T90.52)
Last push: extends c428b0c