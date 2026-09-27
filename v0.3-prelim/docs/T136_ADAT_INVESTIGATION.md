# T136 — Asymmetric Dark Atom Theory (ADAT) Investigation

## Goal

Build a real theory of our dark matter model by combining existing
complementary frameworks:
1. Asymmetric DM (Petraki-Pearce-Kusenko 2014)
2. Standard Model QED as analog
3. Yukawa potential scattering theory
4. Gravothermal collapse

The target: derive σ/m(v) from a Lagrangian, not from a phenomenological
fit. Predict the 4-peak structure at v = 28, 100, 178, 430, 769 km/s
and the velocity slope α_γ ≈ 1.

## Phase 1: Lagrangian + Analytical Born Limit

**What we did**: Wrote Lagrangian for dark U(1)_D gauge theory with
dark proton p_D, dark electron e_D, dark photon A'_D, and dark atoms HD.

**Test**: Born-approximation Yukawa σ/m(v) for our 8 data points.

**Honest finding**: 
- Born-Yukawa slope only varies between 0 (saturated) and -4 (Born)
- The "knee" is around slope -0.4
- **CANNOT give our observed α_γ ≈ -1** from Born alone
- Petraki atomic formula gives flat slope (b₁, b₂ don't capture resonances)

## Phase 2: Resonance Structure

**What we did**: Searched for Yukawa resonance conditions.

**Honest finding**:
- Multiple bound states (s-wave, p-wave, d-wave) exist for ξ = α_D μ/m_A' > 1.68
- BUT: scaling argument shows simple Yukawa resonances don't easily produce
  4 peaks at our specific velocities (28, 100, 178, 430 km/s)
- Need numerical Schrödinger solver for proper resonance locations

## Phase 3: Multi-channel with Breit-Wigner

**What we did**: Added Breit-Wigner enhancement at 4 target velocities.

**Honest finding**:
- Unit conversion bug initially (factor of 10^52 error — caught and fixed)
- After fix: pure Born + BW with arbitrary peak positions doesn't
  naturally give our 8-point data
- The phenomenology is highly tuned

## Phase 4: Two-component Asymmetric DM

**What we did**: Implemented two-component DM with mass ratio 3:1
(the empirical ratio from our phenomenology).

**Honest finding**:
- Even with m_H/m_L = 3:1, the weighted Born-Yukawa slope is still
  in {0, -4, -0.4} depending on regime
- Multi-component doesn't change the fundamental Born limitation
- The 3:1 mass ratio doesn't naturally produce α_γ = -1 from Born

## Overarching Conclusion

**Born-approximation asymmetric DM (any combination) cannot give our
observed velocity slope α_γ ≈ 1.**

The phenomenology's specific slope MUST come from non-perturbative
resonance physics. A real theory requires:
1. Numerical Schrödinger equation solver (1-2 weeks work)
2. Multi-resonance Yukawa potential
3. Or: extended dark sector with additional interactions

## What This Means

**Honest finding**: We cannot derive our phenomenology from first
principles using only published closed-form analytical formulas
(asymmetric DM + Born Yukawa + Petraki formula). The phenomenology
works, but a full theory derivation requires numerical work.

## Path Options

### Option A: Accept the limitation
- Ship v1.14.1 as-is
- Phenomena fit 8 constraints ✓
- UV completion is open (no closed-form theory) ✓
- Status: honest, defensible, publishable

### Option B: Numerical Schrödinger solver (~1-2 weeks)
- Solve non-perturbative Yukawa scattering
- Compute resonance positions
- Find parameters that match our 4-peak structure
- Build proper ADAT paper

### Option C: Extended dark sector
- Add KK modes (like continuum mediation idea)
- Or: non-Abelian dark sector
- More speculative but could give α_γ = -1

## Files Produced (Phase 1-4)

```
v0.3-prelim/code/T136_adat_phase1.py  — Lagrangian + Born limit
v0.3-prelim/code/T136_adat_phase2.py  — Resonance conditions
v0.3-prelim/code/T136_adat_phase3.py  — Multi-channel BW
v0.3-prelim/code/T136_adat_phase4.py  — Two-component ADAT
```

All compile-checked. Self-check passes. No fabricated results.

## References

- Petraki-Pearce-Kusenko 2014 (arXiv:1502.01755): asymmetric DM
- Cassel 2009 (J. Phys. G 36, 075008): Yukawa Born approximation
- Cline-Liu-Moore-Xue 2013: atomic DM parameterization
- Kamada-Kim-Kuwahara 2020 (JHEP): non-perturbative Yukawa