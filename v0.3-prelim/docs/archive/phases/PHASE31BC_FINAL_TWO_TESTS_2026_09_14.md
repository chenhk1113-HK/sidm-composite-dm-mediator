# Phase 31bc — Final Two Critical Review Tests (consider8.docx)

> **Status:** ✅ Shipped 2026-09-14 (branch `wip/cloud-9-relhic`)
> **Trigger:** User requested completion of all 5 remaining critical review tests
> **Predecessor:** Phase 31a (3 of 5 tests done; Test H CRITICAL FAILURE)

---

## TL;DR — Final two test results

| Test | Question | Verdict | Severity |
|---|---|---|---|
| **E** | UV completion (composite mesons, dipole, etc.) | ⚠️ **MULTIPLE_UV** | 2 of 4 scenarios work — narrower than expected |
| **G** | Stellar stream gaps (Pal 5, GD-1) | ✗ **TOO_FEW_GAPS** | Predicts 10-25× fewer gaps than observed |

**Final verdict (9/9 tests done): PARTIALLY_PLAUSIBLE — 2 critical failures**

The model has **two structural failures** that can't be fixed by parameter tuning:
1. **Test H**: Dwarf cores predicted 40-300× too large
2. **Test G**: Stellar stream gaps predicted 10-25× too few

Plus a **mixed** result on completion: 2 of 4 UV scenarios can produce the resonance, so the model isn't entirely unphysical — but the UV parameter space is constrained.

---

## Test E — UV completion scan

**Question**: Can ANY known dark-sector construction produce the required narrow resonance?

**Method**: Tested 4 UV scenarios for producing:
- E_R ~ 42 eV (resonance center)
- Γ_R / E_R ~ 0.013 (very narrow width)
- m_χ ~ 6 GeV (DM mass)

**Results**:

| UV Scenario | Verdict | Detail |
|---|---|---|
| **Composite dark mesons** | LOOSE | 730 parameter combinations work, e.g., α_D=0.07, Λ_D=8.3 GeV, m_ψ=1 GeV |
| **Secluded U(1)' + scalar** | NEEDS_TINY_COUPLING | Requires α_D ~ 6.6×10⁻⁸ (extreme fine-tuning) |
| **Magnetic dipole portal** | POSSIBLE | EFT scale Λ ~ 60 TeV (heavy but achievable) |
| **Dark atom bound states** | TOO_NARROW | Width predicted ~ 10⁻¹⁰ eV (way too narrow) |

**Aggregate: MULTIPLE_UV** — 2 of 4 scenarios can produce the resonance.

### Detailed scenarios

**Composite dark mesons (LOOSE, 730 matches)**:
- α_D × (Λ_D/1 GeV)³ × (1 GeV/m_ψ)² gives the resonance energy
- For target E_R = 42 eV: α_D ~ 0.07, Λ_D ~ 8.3 GeV, m_ψ ~ 1 GeV works
- This is **physically reasonable** — composite dark matter with these parameters is well-studied

**Magnetic dipole portal (POSSIBLE)**:
- Dipole operator: σ_v ~ α_D² × (m_χ/Λ)⁴
- Requires EFT scale Λ ~ 60 TeV (heavy)
- Magnetic dipole DM is a known scenario (e.g., Pospelov 2011)

**Secluded vector (NEEDS_TINY_COUPLING)**:
- t-channel pole gives resonance at E_R ~ m_φ²/(4m_χ)
- Width: Γ_R ~ α_D × m_φ
- For Γ_R / E_R ~ 0.013, need α_D ~ 6.6×10⁻⁸
- This is **extreme** but not impossible

**Dark atom (TOO_NARROW)**:
- Bound state width ~ α_D⁵ × m_eff ~ 10⁻¹⁰ eV
- Target Γ_R = 0.56 eV is 10⁹× too broad for bound-state model
- NOT a viable UV scenario

**Conclusion**: The model has **2 viable UV paths** (composite mesons + magnetic dipole). It's not as phenomenological as feared.

---

## Test G — Stellar stream gaps

**Question**: Does the model predict the right number of gaps in stellar streams?

**Method**:
- Compute σ/m at stream velocities (150-400 km/s)
- Map to subhalo cutoff mass M_cut
- Estimate gap density per unit length
- Compare to observed Pal 5 and GD-1 gaps

**Result**:

| v_stream (km/s) | σ/m (cm²/g) | M_cut (M_sun) | Predicted gaps/10 kpc |
|---|---|---|---|
| 150 | 0.017 | 2.9×10⁷ | 0.025 |
| 200 | 0.013 | 1.9×10⁷ | 0.025 |
| 250 | 0.010 | 1.3×10⁷ | 0.025 |
| 300 | 0.008 | 1.0×10⁷ | 0.025 |
| 400 | 0.006 | 6.6×10⁶ | 0.010 |

**Average: 0.022 gaps per 10 kpc**

**Observations** (Carlberg+ 2012, Erkal+ 2017):
- Pal 5: 0.2-0.5 gaps per 10 kpc
- GD-1: 5-15 gaps total in ~10 kpc stream

**Verdict: TOO_FEW_GAPS** — Model predicts **10-25× FEWER gaps than observed**

### Why?

The same Breit-Wigner resonance that solves Cloud-9 (σ/m(28) = 29) drops rapidly at v=200+ km/s. At these velocities, σ/m ~ 0.01 cm²/g — this **evaporates subhalos below 10⁷ M_sun**, but most stream-disrupting subhalos are in this range. The result: too few gaps.

### What's the right answer?

For streams to match observations, we'd need σ/m(v=200-400) ~ 0.1-1 cm²/g. But Phase 29 has σ/m(v=200) = 0.013. This is a fundamental architectural failure — **the model suppresses too much substructure for stream-gap observations**.

---

## Final aggregate verdict (9/9 tests complete)

| # | Test | Result | Severity |
|---|---|---|---|
| 1 | D: Fine-tuning | NATURAL (max 1.3) | ✓ None |
| 2 | A: Other low-v systems | PARTIAL (4/10) | ⚠️ Mild |
| 3 | F: Relic density | REASONABLE (η/η_B = 0.82) | ✓ None |
| 4 | B: SPARC Bayes | Δlog L = -0.48 | ⚠️ Modest |
| 5 | C: Subhalo real data | CONSISTENT | ✓ None |
| 6 | **H: Dwarf cores** | **OVERSHOOTS 40-300×** | ✗ **CRITICAL** |
| 7 | I: DD limits | Evades with ε ≤ 1.4e-13 | ✓ None (with asymmetric DM) |
| 8 | E: UV completion | MULTIPLE_UV (2/4) | ⚠️ Constrained |
| 9 | **G: Stream gaps** | **TOO_FEW_GAPS (10-25×)** | ✗ **CRITICAL** |

**Score**: 4 ✓ + 3 ⚠️ + 2 ✗ (out of 9)

**Final verdict: PARTIALLY_PLAUSIBLE — has 2 critical structural failures**

---

## What this means for the model

### Working
- ✓ Satisfies Cloud-9 (the primary target)
- ✓ Phenomenologically robust (no extreme fine-tuning)
- ✓ Asymmetric DM compatible (relic density, DD limits)
- ✓ Consistent with strong-lensing data
- ⚠️ UV completable (2 scenarios work)

### Failing
- ✗ **Dwarf cores overshoot by 40-300×** — same resonance that fixes Cloud-9 breaks dwarfs
- ✗ **Stream gaps too few by 10-25×** — same architecture suppresses too much substructure

### What kind of fix is needed?

Both failures have the **same root cause**: the resonance at v=28 km/s is too broad (Γ_R / E_R ~ 0.013), causing σ/m to be too high at v=10-20 km/s (dwarfs) and too low at v=200-400 km/s (streams).

**Possible fixes**:
1. **Sharper velocity cutoff** (e.g., step function instead of Breit-Wigner)
2. **Multiple resonances** (narrow peaks at multiple velocities)
3. **Velocity-dependent coupling** (coupling itself decreases at low v)
4. **Hybrid model** (resonance + additional constant σ/m component)

None of these is a minor patch — they require new physics beyond simple Breit-Wigner.

---

## Updated honest framing (final)

**Old (Phase 29)**: "FULL SOLUTION: 23/23 channels PASS"

**Intermediate (Phase 30)**: "Phenomenological effective model under asymmetric DM, pending UV completion"

**New (Phase 31a-c)**: **"Cloud-9 solver that breaks at dwarf cores and stellar streams"**

The model is **not a viable dark matter solution** in its current form. It:
- Solves one problem (Cloud-9)
- Creates two new problems (dwarf cores, stream gaps)
- Has viable UV completion paths (composite mesons or magnetic dipole)

### Recommended next steps

1. **Retire the resonant model** as the project's primary DM solution
2. **Investigate sharper resonance architectures** (step function, multi-resonance)
3. **Consider multi-component SIDM** (resonance for Cloud-9 + standard SIDM for dwarfs)
4. **Or accept Cloud-9 as a separate puzzle** that needs its own explanation

---

## Files shipped

- `code/phase31b_E_uv_completion.py` (~400 lines)
- `code/phase31c_G_stream_gaps.py` (~230 lines)
- `data/results/phase31b_E_uv_completion.json`
- `data/results/phase31c_G_stream_gaps.json`
- `tests/test_phase31bc_remaining_tests.py` — 5/5 PASS
- `docs/PHASE31BC_FINAL_TWO_TESTS_2026_09_14.md`

**97/97 tests pass** across the post-Phase 10 sweep (23 phases, 29 sub-tasks).

---

## Bottom line (layman)

The resonant dark matter model **worked for Cloud-9 but failed for two other important tests**: dwarf galaxy cores and stellar stream gaps. The same resonance that solved Cloud-9 is too broad — it overshoots at dwarf scales and undershoots at stream scales.

**The model isn't the answer.** It's a Cloud-9 solver that creates two new problems.

The project now has a clear next step: **find a sharper resonance or a different architecture** that can satisfy Cloud-9 without breaking dwarfs or streams. Or accept that Cloud-9 needs its own explanation separate from SIDM.