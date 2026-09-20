# Plan — Phase 34: Combined response to BOTH papers in halo1.docx

> **Status:** 📋 Plan ready (2026-09-14)
> **Trigger:** User uploaded halo1.docx containing TWO arxiv papers
> **Papers**:
>   1. **arXiv:2603.19362** (Klemmer, Fischer, Boddy, Kaplinghat, Sagunski 2026) — SIDM subhalo evolution
>   2. **arXiv:2606.12909** — JVAS B1938+666 lensing perturber (SIDM core collapse explanation)

---

## Both papers in plain English

### Paper 1: arXiv:2603.19362 (already covered)

SIDM subhalo evolution with realistic N-body including SSHI (scattering-induced subhalo-halo interaction), tidal stripping, tidal heating, and gravothermal core collapse. Tests isotropic vs forward-dominated scattering.

**Key result**: SIDM subhalos have much larger diversity of central densities and density slopes than CDM. SSHI can suppress core collapse if cross section doesn't drop fast enough with velocity.

### Paper 2: arXiv:2606.12909 (NEW — JVAS B1938+666 lensing)

A ~10⁶ M⊙ perturber has been detected via gravitational imaging of the strong-lensing system JVAS B1938+666 at z=0.881. 40% of its mass is enclosed within 80 pc — extremely concentrated.

**Key result**: SIDM explains this naturally via **deep gravothermal core collapse**. The required parameters are:
- σ/m ~ **100 cm²/g** at v_max ~ 15 km/s
- Progenitor: ~10⁸ M⊙, concentration c ~ 50
- The collapsed halo develops a secondary dense core (point-like, ~3×10⁵ M⊙ within 10 pc) within an extended profile

**CDM alternative** requires:
- 10¹¹ M⊙ progenitor hosting 10⁵ M⊙ black hole
- Loses 5 orders of magnitude via tidal stripping
- Requires unrealistic orbital conditions (r_sub < 30 kpc)
- "Whether such a scenario can be realized in realistic cosmological environments remains an open question"

---

## Critical finding: TENSION with our model

Paper 2 requires **σ/m(v ~ 15 km/s) ~ 100 cm²/g** for core collapse.

Our model predictions:
- σ/m(v=28) = **100.7** (Cloud-9, narrow resonance) ✓
- σ/m(v=15) = **1.25** (velocity-dependent background, dwarfs) ✗ **80× too low**

**Implication**: Our model produces Cloud-9 (σ/m=100 at v=28) but **cannot produce core collapse at v=15 km/s** to explain lensing anomalies like JVAS B1938+666.

### Why this matters

If JVAS B1938+666 is the right interpretation, then **SIDM needs σ/m ~ 100 cm²/g at sub-dwarf velocities**. Our model gives σ/m ~ 1 cm²/g there. This is a **specific, falsifiable, discriminating test**.

### Can we retune?

The Cloud-9 resonance is at v=28 km/s. To also get σ/m=100 at v=15 km/s, we'd need:
- The R1 resonance wider (so the BW tail extends down to v=15)
- OR a separate resonance at v=15
- OR σ_0_dwarf much larger (which breaks dwarf constraints)

All three would create new tensions with dwarf core tests.

---

## Phase 34 plan (revised)

### Phase 34a — Lens-test with JVAS B1938+666 (1 hour)

Compute our model's prediction for the JVAS B1938+666 perturber:
- For a 10⁸ M⊙ progenitor with c=50, compute σ/m(v_max=15) from our model
- Compare to Paper 2's required σ/m ~ 100 cm²/g for core collapse
- Verdict: can our model produce JVAS-like perturbers?

Expected: **FAIL** — our σ/m(15) = 1.25 << 100. This would be a new **specific** failure that the model can't hide behind loose bands.

### Phase 34b — σ/m diversity analysis (30 min, lower priority)

Compute variance of σ/m across Phase 32b posterior vs Paper 1's "much larger diversity than CDM" claim.

### Phase 34c — Combined doc + verdict (15 min)

Update T90_MASTER_REFERENCE with:
- Both new papers
- New verdict: "FAILS JVAS B1938+666 lensing test — σ/m(15) too low"
- Honest recommendation: retune model OR accept it can't explain lensing anomalies

---

## Honest assessment

This is a **legitimate challenge** to the model. Paper 2 provides a TARGET σ/m(v=15) ~ 100 cm²/g that we don't reach. Our model fits Cloud-9 (a specific Milky Way satellite) but doesn't generalize to explain lensing anomalies.

The user has now given me 2 papers + 1 review doc, all pointing at the same thing: **the model works in narrow domains but fails broader tests**. Phase 34 should make this explicit.

---

## Bottom line

Phase 34 is now an **external falsification test** rather than a "compatibility check". The JVAS B1938+666 lensing test is more discriminating than the SPARC probe because:
- It requires σ/m at a specific velocity (v=15) to be 100 cm²/g
- Our model gives σ/m(15) = 1.25 there
- This is an 80× discrepancy, not a "loose band" issue

Recommend proceeding with **Phase 34a (JVAS B1938+666 test)** as the next step. It's a single, decisive, falsifiable test.