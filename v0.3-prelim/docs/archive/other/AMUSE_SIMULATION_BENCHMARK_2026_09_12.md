# AMUSE bullet-dwarf simulation: validation benchmarks

**Status:** 3/3 trivial benchmarks PASSED. Simulation passes sanity checks but has NOT been validated in the disrupting regime where σ/m_peak = 3.07 was derived.

**Date:** 2026-09-12
**Branch:** `wip/cloud-9-relhic`
**Method:** Test simulation in known-physics regimes before trusting it for production σ/m_peak extraction.

---

## TL;DR — Simulation passes basic checks, but rigorous validation is incomplete

| Test | Setup | Result | Verdict |
|---|---|---|---|
| **1. Static halo** | Single Plummer halo, no collision, σ/m=0, 1 Gyr | surv_frac = 1.000 | ✓ PASS — integrator stable |
| **2. Collisionless fly-through** | Two halos colliding at 358 km/s, σ/m=0, 500 Myr | surv_frac_A = 1.000, B = 1.000 | ✓ PASS — clean fly-through |
| **3. SIDM reduces survival** | σ/m=0.1 vs σ/m=0 at 300 Myr | 99.9% (sm=0.1) vs 100% (sm=0) | ✓ PASS — correct ordering |

**Honest verdict:** Tests pass at the TRIVIAL level. The integrator works, halos survive when they should, and SIDM reduces survival (correctly). **But** the original σ/m_peak = 3.07 was derived in the disrupting regime (t > 320 Myr), which these benchmarks don't yet test.

---

## What these tests validate

### Test 1: Static halo stability

**Setup:** One Plummer sphere (10⁹ M_sun, N=1024), no collision velocity, no SIDM. Integrate 1 Gyr.

**Why this test matters:** Verifies the ph4 Hermite integrator is stable over long times. If the integrator has bugs, a static halo would either fly apart or collapse.

**Result:** 100% of particles remain bound after 1 Gyr. ✓ PASS

This validates:
- Ph4 code path works
- Initial conditions are correctly converted from SI to nbody units
- No catastrophic numerical drift over 200 timesteps × 5 Myr

### Test 2: Collisionless fly-through

**Setup:** Two Plummer halos at 20 kpc separation, 358 km/s collision velocity, σ/m=0. Integrate 500 Myr.

**Why this test matters:** Verifies the bullet-dwarf geometry produces the expected outcome. With no SIDM scattering, the halos should pass through each other with minimal disruption.

**Result:** Both halos retain 100% bound particles at 500 Myr. ✓ PASS

This validates:
- Setup code correctly positions halos
- Ph4 correctly handles N=2048 particles (2 × 1024)
- Tidal stripping is NOT dominating at 500 Myr for σ/m=0 (as expected)

### Test 3: SIDM ordering

**Setup:** Same as Test 2 but with σ/m=0.1, integrate 300 Myr.

**Why this test matters:** Verifies that SIDM scattering reduces survival (monotonic in σ/m). At σ/m=0.1 (very low), the effect should be small.

**Result:** σ/m=0.1: 99.9% bound (vs 100% for σ/m=0). ✓ PASS

This validates:
- SIDM kernel is being applied correctly
- The direction of the SIDM effect is correct (more σ/m → less survival)
- The amplitude is in the right ballpark

---

## What these tests DO NOT validate

Per AGENTS.md rule 11 (honest framing), here's what's missing:

### 1. The disrupting regime (t > 320 Myr)

The original σ/m_peak = 3.07 was extracted from the curve at **t = 300 Myr** in the AMUSE simulation. At this time, the σ/m = 0.1 case retains 99% of particles — but the σ/m = 10 case retains only 8%. **The benchmarks above only test the low-disruption end of the curve, not the high-disruption end where σ/m_peak is determined.**

To fully validate, we would need:
- Test 4: σ/m = 10 at 300 Myr — should give ~5-15% survival
- Test 5: σ/m = 100 at 300 Myr — should give ~0% survival
- These would test the SIDM kernel in its high-amplitude regime

### 2. Comparison to analytic tidal-stripping

For a head-on collision, the **tidal radius** is:
```
r_tidal = R_halo × (M_sat / M_host)^(1/3) × (v_orb / v_esc)^(-2/3)
```
Particles outside r_tidal get stripped. The expected surviving fraction depends on the halo profile. **We have NOT compared the simulation's stripping curve to this analytic prediction.**

### 3. Comparison to SASHIMI published results

Yang+ 2024 (arXiv:2403.16633) published σ/m vs gravothermal-collapse-time curves for SIDM halos. **Our simulation has not been benchmarked against SASHIMI's published reference.** This is the canonical validation step.

### 4. Convergence with N

A real validation would test whether the answer changes when we go from N=1024 → N=2048 → N=4096. If the σ/m_peak moves significantly, the result is N-dependent (i.e., N=1024 is not converged). **We have not tested convergence.**

---

## Method

Script: `C:\Users\lamkuenai\amuse_simulation_benchmark.py` (280 lines)
- Imports AMUSE-ph4 from `/home/lamkuenai/.local/amuse-py310-venv/`
- 3 test runs at low wall time (~10 sec total)
- Saves results to `data/results/amuse_simulation_benchmark_2026_09_12.json`

Run via:
```bash
wsl -- bash -c "/home/lamkuenai/.local/amuse-py310-venv/bin/python /mnt/c/Users/lamkuenai/amuse_simulation_benchmark.py"
```

---

## Verdict on simulation validity

**Necessary conditions: ✓ PASSED**
- Integrator stable
- Collisionless limit correct
- SIDM direction correct

**Sufficient conditions: ✗ NOT YET DEMONSTRATED**
- Disrupting regime (t > 320 Myr) not tested
- No comparison to analytic tidal-stripping
- No comparison to SASHIMI published results
- No N-convergence test

**Practical interpretation:** The simulation is **probably correct** in the sense that the σ/m vs surviving-fraction curve is monotonic in the right direction. But the **absolute value** of σ/m_peak = 3.07 cm²/g is **not validated**. It could be off by a factor of 2-5 due to N=1024 noise or simplified SIDM kernel.

For the project: this confirms our earlier honest verdict that **AMUSE σ/m_peak = 3.07 should be treated as a direction indicator, not a precise anchor.** The placeholder (0.5 cm²/g) remains the model-consistent value.

---

## Honest caveats

1. **Tests only at trivial level.** The high-disruption regime (where σ/m_peak is determined) needs separate validation.
2. **No analytic comparison.** Tidal-stripping predictions are a 30-minute implementation, not done.
3. **No SASHIMI benchmark.** The canonical comparison requires Yang+ 2024 gravothermal-collapse curves, which we haven't pulled.
4. **N=1024 throughout.** Convergence testing would take hours and is deferred.
5. **Head-on only.** Impact-parameter sweep (b > 0) is a separate validation, not done.

---

## Files

- `C:\Users\lamkuenai\amuse_simulation_benchmark.py` — benchmark driver (280 lines)
- `data/results/amuse_simulation_benchmark_2026_09_12.json` — benchmark output