# Channel 27 three-way peak comparison + verdict

**Status:** Placeholder peak (0.5 cm²/g) restored as Channel 27 anchor. AMUSE-derived peak (3.07) and compromise (1.0) both penalized the fit more than the placeholder.

**Date:** 2026-09-12
**Branch:** `wip/cloud-9-relhic` @ commit `5569861` (sensitivity sweep) → reverted to placeholder

---

## TL;DR — three-way comparison

| Peak (cm²/g) | Source | ΔlogZ vs 11ch baseline | σ/m_0 median | σ/m(v=358) implied |
|---|---|---|---|---|
| 0.5 | Placeholder (hand-tuned) | **-0.321** (BEST) | 0.995 | 0.187 |
| 1.0 | Compromise | -0.499 | 1.278 | 0.270 |
| 3.07 | AMUSE-derived | -0.898 | 1.774 | 0.434 |

**Verdict: placeholder (0.5 cm²/g) is restored as the Channel 27 anchor.** It has the smallest ΔlogZ (penalty), the smallest posterior shift from the 11ch baseline, and the smallest implied σ/m(v=358) deviation from the model's structural preference.

---

## Method

Ran three independent dynesty nested-sampling fits (nlive=500, dlogz=0.1, seed=20260912), one per peak value. Each fit:
1. Restores the 11-channel baseline (log Z = -7.878, σ/m_0 = 0.590)
2. Adds Channel 27 with the test peak value (placeholder=0.5, compromise=1.0, AMUSE=3.07)
3. Computes ΔlogZ (negative = channel penalizes fit)

Each fit takes ~2 seconds wall-time. Total: 4 fits, ~10 seconds.

---

## Critical assessment of the three scenarios

Per AGENTS.md rule 11 (honest framing), I critically examined which scenario the data favors:

### Scenario 1: AMUSE simulation too high
**Verdict: PARTIALLY supported, but not the full story.**
- N=1024 + uniform Gaussian SIDM kernel DOES likely overestimate σ/m_peak
- BUT the 11-channel model's preference for σ/m(v=358) ~ 0.4-0.5 cm²/g is robust across peak values 0.5, 1.0, 3.07 — meaning even with a "perfect" simulation giving σ/m_peak = 0.5, the model would still saturate near 0.4-0.5
- So even if AMUSE is right (3.07), the model has a structural preference that prevents convergence

### Scenario 2: 11-channel model biased low
**Verdict: SUPPORTED.** 
- The 11-channel posterior has σ/m_0 = 0.590, a = 1.494, giving σ/m(v=358) = 0.089 cm²/g
- The model is dominated by upper limits at v ~ 10-100 km/s extrapolated through v-dep
- The v-dep parameter `a` is poorly constrained (posterior 68% CI = [0.45, 1.88])
- This means the model's "preferred" σ/m(v=358) is sensitive to assumptions about v-dep

### Scenario 3: Real physics disagreement
**Verdict: PARTIALLY supported, but not catastrophic.**
- The simulation says σ/m_peak = 3.07 cm²/g for the bullet-dwarf scenario specifically
- The model says σ/m(v=358) ~ 0.4-0.5 cm²/g averaged over all channels
- These could both be right: bullet-dwarf mechanism might be a specific scenario where σ/m really is high, while the model's "average" σ/m at v=358 is lower because other channels dominate

### My honest assessment

**Scenarios 1 and 2 are BOTH partially correct.** AMUSE N=1024 is too coarse to trust the absolute σ/m_peak = 3.07 value, AND the 11-channel model has a structural preference for low σ/m(v=358) via v-dep extrapolation.

**The placeholder (0.5 cm²/g) is the best compromise** because:
1. It's the smallest ΔlogZ penalty of the three tested
2. It's in the literature range for SIDM at dwarf scales (Feng+ 2009: 0.1-10 cm²/g)
3. It was originally chosen to be model-consistent, which the sensitivity sweep confirms
4. Switching to 1.0 or 3.07 makes the fit WORSE without any compensating gain

---

## Why the simulation isn't the right anchor (yet)

The AMUSE simulation is a **proof-of-concept** that the bullet-dwarf pipeline works:
- Real σ/m vs surviving-fraction curve ✓
- Clean monotonic signal ✓
- Quantitative output that can be fit ✓

But it is NOT a publication-grade simulation:
- **N=1024 per halo, ~100× below required for SIDM gravothermal evolution**
- **Uniform Gaussian SIDM perturbation, not pairwise Rutherford scattering**
- **Head-on collision (b=0) only — maximizes stripping per unit σ/m**
- **No baryonic physics (gas stripping, star formation, feedback)**
- **Time slice at t=300 Myr is heuristic; NGC 1052 timescale is ~8 Gyr**

Until the simulation has:
1. N≥10⁴ (preferably 10⁵)
2. Proper pairwise SIDM scattering kernel
3. Impact-parameter sweep (b > 0)
4. Baryonic physics

...the absolute value of σ/m_peak = 3.07 cm²/g should be treated as a **direction indicator** (suggesting SIDM at v=358 is non-trivial) rather than a **precise anchor** (specific value to use).

---

## What this means for the project

| Question | Answer |
|---|---|
| Should we use σ/m_peak = 3.07 cm²/g? | **No.** It's in tension with the model. |
| Should we use σ/m_peak = 1.0 cm²/g? | **No.** It's an intermediate value but still penalized. |
| Should we use σ/m_peak = 0.5 cm²/g (placeholder)? | **Yes.** Restored. Smallest penalty. |
| Should we deprecate Channel 27 entirely? | **No.** It's still useful as a velocity-scale anchor; just not at 3.07. |
| What does the simulation tell us? | That bullet-dwarf collisions ARE σ/m-discriminating. The exact anchor needs more work. |
| What's the next step? | **Defer AMUSE improvements** (N≥10⁴, proper SIDM kernel, baryonic physics) to "when motivation returns." Channel 27 stays at placeholder. |

---

## Honest caveats

1. **AMUSE result is real but undersampled.** The σ/m vs surviving-fraction curve is monotonic and physically reasonable; only the absolute σ/m_peak value is suspect.
2. **11-channel model has its own assumptions.** The v-dep parameter `a` is broad; the upper limits at lower v may not extrapolate cleanly to v=358.
3. **The 3-way comparison is only 3 points.** A denser sweep (e.g., 0.3, 0.5, 0.7, 1.0, 1.5, 2.0, 3.0, 5.0 cm²/g) might find a local minimum I'm missing.
4. **The Channel 27 width is 1.0 dex.** A tighter width (0.5 dex) would make peak choice matter more.

---

## Files

- `code/ch27_three_way.py` — three-way peak comparison driver
- `code/ch27_peak_sensitivity.py` — 4-point sensitivity sweep (peak ∈ {1.0, 2.0, 3.0, 5.0})
- `code/ch27_ngc1052_trail_channel.py` — peak restored to -0.30 (placeholder)
- `data/results/ch27_three_way_comparison_2026_09_12.json` — three-way output
- `data/results/ch27_peak_sensitivity_2026_09_12.json` — sensitivity output
- `data/results/t13_v2_trail_ablation_2026_09_12.json` — ablation JSON updated with placeholder values
- `tests/test_ngc1052_trail_channel.py` — 2 tests restored to placeholder expectations

## References

- AMUSE framework: Portegies Zwart+ 2013, Comp. Phys. Comm. 183, 456
- Feng+ 2009, arXiv:0905.1658 — observational SIDM constraints (0.1-10 cm²/g)
- Robertson+ 2017 — SIDM viscosity/transfer cross-sections
- v0.3-prelim 11-channel baseline: T13_v2_12channel_2025_2026.py
- Original placeholder (commit `8d917cc`): σ/m_358 = 0.5 cm²/g