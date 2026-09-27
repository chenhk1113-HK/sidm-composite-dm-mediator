# Phase 35 — 5-Resonance Architecture: JVAS-Resolved but Tension Surfaced

> **Status:** ✅ Shipped 2026-09-14 (branch `wip/cloud-9-relhic`)
> **Trigger:** User selected Option C: implement 5th resonance AND document honestly
> **Reference:** Paper 2 (arXiv:2606.12909) requires σ/m(15) ~ 100 for JVAS core collapse
> **Verdict:** **JVAS RESOLVED, but Fornax/Tri II BROKEN at same velocity (v=15)**

---

## What I did

1. Added a **5th resonance at v=15 km/s** with σ_peak = 100 cm²/g and width = 3%
   - This matches Paper 2's requirement for JVAS core collapse
   - The resonance is narrow enough to not contaminate Cloud-9 (v=28)

2. Tuned σ_0_dwarf = 0.20, a_slope = 0.5 (background)
   - Lower than Phase 32b's 0.195 + 0.7 to make SPARC band work
   - But still gives dwarfs in [0.5, 5] at v=10-12

3. Ran all critical tests → **8/11 PASS**

## What passed

✓ Segue 1 (v=10): σ/m = 3.32 (in [0.5, 5])
✓ Sculptor (v=12): σ/m = 2.81 (in [0.5, 5])
✓ **JVAS (v=15): σ/m = 102.07** (in [50, 200]) ← NEW, FIXES Paper 2
✓ Cloud-9 (v=28): σ/m = 100.93 (in [30, 500])
✓ SPARC (v=100): σ/m = 0.27 (in [0.05, 0.5])
✓ Stream low (v=250): σ/m = 0.067 (in [0.05, 1])
✓ Stream high (v=300): σ/m = 0.15 (in [0.05, 1])
✓ Cluster (v=1000): σ/m = 0.013 (in [0.01, 0.1])

## What failed

✗ Fornax (v=15): σ/m = 102 (target [0.5, 5]) ← BREAKS
✗ Tri II (v=15): σ/m = 102 (target [0.5, 5]) ← BREAKS
✗ Bullet (v=3000): σ/m = 0.0034 (target [0.005, 0.1]) — borderline

---

## The fundamental tension SURFACED

**Fornax and JVAS B1938+666-V both have v_max ~ 15 km/s** but require **opposite σ/m values**:

| Object | v (km/s) | Required σ/m | Reason |
|---|---|---|---|
| Fornax (isolated dwarf) | 15 | **1-5 cm²/g** | Dwarf rotation curves show cored profiles |
| JVAS perturber (lensing) | 15 | **~100 cm²/g** | Need deep core collapse for lensing mass |

With a **velocity-only** σ/m model (our framework), both can't be true at the same velocity. Adding a 5th resonance at v=15 satisfies JVAS but breaks Fornax.

This is a **real physical tension** — not something we can hide with band tuning.

### Possible resolutions

1. **Concentration-dependent collapse time** (Paper 2's actual mechanism)
   - Fornax: low concentration (c ~ 10), even with σ/m ~ 100, t_c > Hubble time → no collapse, looks like isolated dwarf
   - JVAS progenitor: high concentration (c ~ 50), t_c < Hubble time → core collapse
   - **Both can be true** if σ/m ~ 100 but only JVAS-concentration progenitors have time to collapse

2. **Environmental dependence** (Paper 1's mechanism)
   - Fornax is in isolation → σ_eff ~ σ
   - JVAS is in dense lens environment → SSHI modifies effective σ/m
   - **But Paper 1 says SSHI REDUCES σ/m at low v**, opposite of what we need

3. **CDM with black hole** (Paper 2's alternative)
   - JVAS is a 10¹¹ M_sun progenitor hosting 10⁵ M_sun black hole
   - Doesn't require SIDM σ/m at all
   - Paper 2 says this is "potentially difficult to realize" but possible

4. **Reinterpret JVAS observation**
   - Maybe the lens modeling is wrong
   - Maybe it's a different kind of object entirely

### What the model ACTUALLY says now

The 5-resonance architecture with R0 at v=15 cm²/g **mechanically satisfies** the JVAS test but **breaks the Fornax test at the same velocity**. The honest verdict:

> "The 5-resonance model can produce SIDM cross-section values consistent
> with JVAS B1938+666-V's core collapse requirement, but at the cost of
> Fornax/Tri II consistency at v=15 km/s. This is a fundamental tension
> that requires either concentration-dependent physics (not in our
> model) or alternative interpretations of JVAS."

---

## Updated status

| Test | σ/m | Status |
|---|---|---|
| Segue 1 (v=10) | 3.32 | ✓ |
| Sculptor (v=12) | 2.81 | ✓ |
| **JVAS (v=15)** | **102.07** | ✓ FIXED |
| **Fornax (v=15)** | **102.07** | ✗ BROKEN (was 1.2) |
| **Tri II (v=15)** | **102.07** | ✗ BROKEN (was 1.2) |
| Cloud-9 (v=28) | 100.93 | ✓ |
| SPARC (v=100) | 0.27 | ✓ |
| Stream (v=250) | 0.067 | ✓ |
| Stream (v=300) | 0.15 | ✓ |
| Cluster (v=1000) | 0.013 | ✓ |
| Bullet (v=3000) | 0.0034 | borderline ✗ |

8/11 PASS. Compared to Phase 32b's 9/11, the trade is:
- **Lost**: Fornax, Tri II (at v=15)
- **Gained**: JVAS (at v=15)

Net effect: similar pass rate, but we **traded one set of failures for another at the same velocity**.

---

## Why this is actually informative

This reveals that **Fornax and JVAS are fundamentally at odds** at v=15 km/s. The model can't satisfy both simultaneously with a velocity-only σ/m.

Three possible paths:

| Path | Implication |
|---|---|
| **A. Concentration-dependent collapse** | Need to add concentration physics (not in model) |
| **B. JVAS is CDM+black hole** | Need to accept SIDM doesn't explain JVAS |
| **C. Fornax is wrong about its cross-section** | Challenge observational constraint |

Path A is most likely correct (per Paper 2). Path B is the simplest. Path C is risky.

---

## What I would recommend next

Don't keep adding resonances. Instead:

1. **Add concentration-dependent physics** to the model
   - Compute t_c(c, σ/m) for each test system
   - A system only "core collapses" if t_c < Hubble time AND c > threshold
   - This is ~2-3 hours of work

2. **OR explicitly accept partial solution**
   - Document: "model explains Cloud-9 + SPARC + subhalos, but cannot
     simultaneously explain JVAS B1938+666 + Fornax dwarf rotation"
   - This is honest and avoids ad hoc fitting

3. **OR treat Fornax/Tri II as already-collapsed**
   - If Fornax already collapsed to a dense state, its σ/m might be ~100
   - But Fornax is observed to have a cored profile (not dense)
   - So this doesn't work

**My recommendation**: Try option 1 (concentration-dependent physics) — it's the most physically motivated and would resolve both tests simultaneously without additional free parameters.

---

## Files shipped

- `code/t90_v71_five_resonance_jvas.py` (~250 lines)
- `docs/PHASE35_FIVE_RESONANCE_JVAS_RESOLVED.md`

This phase demonstrates that the JVAS requirement is **not trivially fixable** — it forces a real conflict with dwarf observations at the same velocity. The honest path forward requires either more physics or accepting the tension.

Total tests: 135/135 still pass (existing tests unchanged).