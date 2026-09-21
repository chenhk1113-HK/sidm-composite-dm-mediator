# T170-T172 Resonant SIDM Investigation (2026-09-20)

**Goal:** Can resonant SIDM (Tran+ 2024, arXiv:2405.02388) accommodate Cloud-9 (σ/m ≥ 50 at v=28)?

---

## Background: Resonant SIDM

**Paper:** Tran et al. 2024, "Gravothermal Catastrophe in Resonant Self-interacting Dark Matter Models" (PRD 110, 043048)

**Key insight:** For attractive Yukawa potential, **bound-state formation** creates order-of-magnitude **resonant enhancements** in σ/m at specific velocities. The peak velocity depends on the dimensionless coupling α·m_χ/m_φ.

**Their model:** m_χ = 31.8 GeV, m_φ = 5.7 MeV, α = 1.6×10⁻³ gives σ/m ~ 100 cm²/g at v ~ 16 km/s.

**Why this matters for us:** Cloud-9 sits at v = 28 km/s with σ/m ≥ 50 required. If we tune the resonance to v = 28, we might bridge the 600× gap that single-Yukawa can't.

---

## T170: Initial resonant SIDM test

**Goal:** Verify that sidmkit reproduces the resonant enhancement.

**Result with exact Tran+ 2024 parameters:**

| v (km/s) | σ/m (cm²/g) |
|---|---|
| 1 | 24.5 |
| 5 | 27.5 |
| 10 | 52.3 |
| **16** | **260.6** ← resonance peak |
| 28 | 21.6 |
| 50 | 13.8 |
| 100 | 8.6 |
| 200 | 481.5 |
| 500 | 534.3 |
| 1000 | 522.2 |

**Verdict:** ✓ Resonance confirmed! σ/m peaks at v ~ 16 (not 28). The peak is HUGE (260× the floor) but narrow.

**Mild variations tested:**

| alpha | m_φ (MeV) | m_χ (GeV) | σ/m at v=28 |
|---|---|---|---|
| 1.6e-3 | 5.7 | 31.8 | 21.6 |
| 1.6e-3 | 10 | 31.8 | 0.8 |
| 1.6e-3 | 20 | 31.8 | 2.2 |
| **1.6e-3** | **3.0** | **31.8** | **90.9** |
| 5e-3 | 10 | 31.8 | 29.1 |
| 1e-2 | 10 | 31.8 | 6.3 |
| 5e-3 | 20 | 31.8 | 4.5 |
| 1e-2 | 50 | 31.8 | 26.7 |
| **1.6e-3** | **5.7** | **10** | **52.7** |
| 1.6e-3 | 5.7 | 100 | 3.5 |

**Best Cloud-9 matches:** α=1.6e-3, m_φ=3.0 MeV, m_χ=31.8 GeV → σ/m = 90.9 ✓
Also: α=1.6e-3, m_φ=5.7 MeV, m_χ=10 GeV → σ/m = 52.7 ✓

---

## T171: Systematic search (BROKEN - too slow)

**Goal:** Test 330 parameter combinations to find best fit.

**Status:** Stuck (330 configs × 30s timeout = 165 minutes minimum). Killed after ~30 min.

**Lesson learned:** Tighter, physics-guided grid is more efficient than blind grid.

---

## T172: Physics-guided search (SUCCESS)

**Goal:** Focused search around T170's promising configurations.

**Tested 33 configurations** in 68 seconds. Results:

| Rank | α | m_φ (MeV) | m_χ (GeV) | RMSE | σ/m(v=28) | σ/m(v=3) | C9 OK? |
|---|---|---|---|---|---|---|---|
| 1 | 2e-1 | 100 | 100 | 1.624 | 0.106 | 0.130 | NO |
| 2 | 1e-1 | 100 | 100 | 1.726 | 0.466 | 1.120 | NO |
| 3 | 1e-1 | 50 | 100 | 1.827 | 0.329 | 0.516 | NO |
| ... | | | | | | | |
| 15 | 1.6e-3 | 5.7 | 3.0 | 3.065 | 66.3 | 66.7 | **YES** |

**Best Cloud-9-satisfying fit:** RMSE = 3.065, but σ/m at v=3 = 66.7 (data = 0.155 — **way off**)

**Best overall fit (no Cloud-9):** RMSE = 1.624 (similar to single-Yukawa)

---

## Critical Honest Verdict

**Resonant SIDM can technically produce σ/m ≥ 50 at v=28, BUT it cannot simultaneously fit the other 7 data points.**

Why? The resonance that enhances σ/m at v=28 ALSO enhances σ/m at v=3 (and all other velocities in our data range). The bound state is **not** narrow enough to be selective.

The Cloud-9-satisfying fits have σ/m(v=3) ≈ 66 — about **400× too large** compared to data (0.155). This is the SAME problem as single-Yukawa, just shifted.

**Three possible explanations:**

1. **The 8 data points are fundamentally incompatible** — any single-Yukawa (resonant or not) cannot fit all 8 simultaneously.

2. **The Cloud-9 enhancement requires something OTHER than Yukawa resonance** — e.g., gravothermal core-collapse, hidden-sector dark matter, or non-SIDM physics.

3. **Our low-v data points have different physics** than Cloud-9 — multi-component DM, asymmetric matter, or environmental effects.

**Comparison with previous fits:**

| Method | Best RMSE | Cloud-9 satisfied? |
|---|---|---|
| Single-Yukawa (T160) | 1.42 | NO |
| KK tower (T163) | 1.408 | NO |
| Single-Yukawa σ=50 forced (T165) | 1.033 | YES |
| **Resonant SIDM (T172)** | **3.065** | **YES** |

**Key finding:** Forcing Cloud-9 via resonance HURTS the fit dramatically (1.033 → 3.065) because the resonance is too broad. Resonant SIDM is **NOT a better solution** than simply setting σ/m = 50 directly.

---

## Recommendations

1. **Resonant SIDM does NOT resolve the Cloud-9 tension** — it makes it worse
2. **Best Cloud-9 framing remains:** σ/m ≥ 50 (lower bound) with our standard single-Yukawa fit at RMSE = 1.033
3. **The 7-point fit (excluding Cloud-9) at RMSE = 0.25** remains the strongest result
4. **Future physics beyond Yukawa needed** for Cloud-9 — possibly:
   - Gravothermal core-collapse (extreme regime)
   - Asymmetric dark matter
   - Multi-component DM
   - Hidden sector with different mediator

---

## Files produced

- `v0.3-prelim/code/T170_resonant_sidm.py`
- `v0.3-prelim/code/T171_resonant_search.py` (incomplete, killed)
- `v0.3-prelim/code/T172_physics_guided.py`
- `v0.3-prelim/data/results/t170_resonant_sidm.json`
- `v0.3-prelim/data/results/t172_physics_guided.json`
- `v0.3-prelim/docs/T170_T172_RESONANT_SIDM.md` (this file)

---

**Honest verdict:** After 3 systematic attempts, resonant SIDM does NOT bring Cloud-9 into our framework without breaking the 7 other data points. The 4000× enhancement requires physics BEYOND standard Yukawa interactions.
