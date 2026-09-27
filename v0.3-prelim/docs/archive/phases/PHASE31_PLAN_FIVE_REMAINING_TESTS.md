# Plan — Phase 31: Five Remaining Critical Review Tests

> **Status:** 📋 Plan ready (2026-09-14)
> **Trigger:** User requested plan for the 5 remaining tests from consider8.docx
> **Predecessor:** Phase 30 (4 of 9 tests done; verdict PLAUSIBLE w/ caveats)

---

## Goal

Execute the 5 deferred tests from consider8.docx that were not run in Phase 30.
After Phase 30, the verdict is "PLAUSIBLE w/ caveats" — these 5 tests will either
strengthen or weaken that verdict.

| Test | Reviewer's question | Status | Feasibility |
|---|---|---|---|
| **C** | Subhalo mass function (real Euclid/HST data) | ✅ READY | High — T88.E2 infra exists |
| **E** | UV completion (composite dark mesons, dark atoms) | ✅ READY | High — T105 infra exists |
| **G** | Stellar stream gaps (Pal 5, GD-1, Orphan) | ⚠️ PARTIAL | Medium — T95 has data, need subhalo prediction |
| **H** | Cluster vs dwarf core-size evolution | ✅ READY | High — T95 v02 has core-size infra |
| **I** | Direct-detection / beam-dump consistency | ✅ READY | High — T62/T76 has DD infra |

---

## Test C — Subhalo mass function (real Euclid data)

**Question**: Does the real Euclid Q1 strong-lensing cluster count (14 grade-A in 63.1 deg²) match the resonant SIDM prediction?

**Method**:
- Use existing `euclid_q1_subhalo_real_data.py` (T88.E2) for Poisson count likelihood
- Compute σ/m at v ~ 500-1000 km/s (cluster velocities) for Phase 29 resonant posterior median
- Compute SIDM suppression from Robertson+ 2019 BAHAMAS-SIDM
- Compare predicted N_lenses vs observed 14 grade-A clusters

**Existing infrastructure**:
- `code/euclid_q1_subhalo_real_data.py` (has Poisson likelihood, suppression function)
- `data/results/phase29_full_resonant_joint_fit.json` (posterior median)
- `code/t90_v50_resonant_sidm.py` (σ/m at any velocity)

**Expected output**: 
- n_predicted (resonant): ~ 14 × (1 - suppression)
- log L_resonant vs log L_CDM
- verdict: CONSISTENT / TENSION / EXCLUDED

**Effort**: ~30 min (script is mostly assembly + 1 evaluation)

---

## Test E — UV completion (composite dark mesons, dark atoms)

**Question**: Can any known dark-sector construction produce a Breit-Wigner-like feature with Γ_R/E_R ~ 0.013 peaked at ~42 eV in the CM frame of two ~6 GeV particles?

**Method**:
- Use existing `t105_uv_consistency.py` infrastructure for parameter scan
- For composite dark mesons: δ_M ~ α_D × Λ_D³ / m_ψ² (analogous to pion-rho splitting)
- For secluded vector + scalar: t-channel pole gives Breit-Wigner form
- Scan (Λ_D, m_ψ, α_D) to find any combination that gives:
  - Mass splitting δ_M ~ 40 eV (not 300 keV as in T105)
  - Width Γ_R ~ 0.5 eV (much narrower than typical hadronic widths)
  - DM mass m_chi ~ 6 GeV

**Existing infrastructure**:
- `code/t105_uv_consistency.py` (has UV parameter scan framework)
- Could extend to include Breit-Wigner resonance as additional UV signature

**Expected output**:
- Number of (Λ_D, m_ψ, α_D) combinations that give the right resonance
- Honest verdict: NO_KNOWN_UV / POSSIBLE_UV / NATURAL_UV

**Effort**: ~1-2 hours (UV parameter scan with new resonance target)

**Honest expectation**: Narrow resonances in dark sectors are typically Γ/E ~ 0.1-1 (hadronic), not 0.013. So verdict is likely NO_KNOWN_UV.

---

## Test G — Stellar stream gaps (Pal 5, GD-1, Orphan)

**Question**: Do predicted subhalo encounters match the observed gap statistics in stellar streams?

**Method**:
- The resonant model predicts σ/m at v ~ 200-400 km/s (stream velocity dispersion)
- Stream gaps are sensitive to subhalo mass function, which depends on σ/m at these velocities
- Phase 29 σ/m(200) = 0.013, σ/m(300) = 0.005 (very low!)
- Compare to existing stream gap analyses (T95 v25 has real galstreams data)

**Existing infrastructure**:
- `code/t95_v25_multi_stream_real_galstreams.py` (galstreams v1.2 catalog data)
- Phase 29 posterior median σ/m values

**Challenge**: The actual stream gap likelihood is not yet implemented in the repo. Would need to:
1. Use published gap constraints (Carlberg+ 2012, Erkal+ 2016 for GD-1)
2. Map σ/m to subhalo mass function suppression
3. Compare predicted gap density to observed

**Effort**: ~3-4 hours (significant new forward model needed)

**Decision**: DEFER if no quick published gap statistic available, or implement simplified version.

**Alternative quick test**: Check if Phase 29 σ/m(200) = 0.013 is consistent with observed stream survival. Streams at v ~ 200 km/s with σ/m ~ 0.013 should have **minimal** subhalo disruption. Real streams have some gaps → moderate σ/m expected. So verdict likely **predicts too few gaps**.

---

## Test H — Cluster vs dwarf core-size evolution

**Question**: Does the predicted core size in dwarfs match observed, and does it match cluster predictions?

**Method**:
- The resonant model predicts σ/m(v) varies dramatically:
  - v=28 km/s (dwarf): σ/m = 29 (huge, predicts large cores)
  - v=100 km/s (galactic): σ/m = 0.035 (small cores)
  - v=1000 km/s (cluster): σ/m = 0.0006 (negligible, CDM-like)
- Use T95 v02 core size predictor: r_c = sqrt(σ_T × ρ_s × r_s² / m_chi)
- For dwarf galaxies (v_0 ~ 30 km/s): predict r_c ~ several kpc
- For clusters (v_0 ~ 1000 km/s): predict r_c ~ 0 (CDM-like)
- Compare to observed dwarf cores (e.g., Fornax, Sculptor: r_c ~ 0.5-1 kpc) and cluster cores (CDM-like)

**Existing infrastructure**:
- `code/t95_v02_option2_core_size.py` (NFW + SIDM core size prediction)

**Expected output**:
- Predicted r_c for dwarf (Fornax-like): r_c ~ 1-5 kpc (resonance peak)
- Predicted r_c for cluster: r_c ~ 0 (no SIDM effect at cluster velocities)
- Comparison to observations

**Verdict likely**: PARTIAL — model predicts LARGER dwarf cores than observed (overshoot due to σ/m=29 at v=28)

**Effort**: ~30 min (script assembly)

---

## Test I — Direct-detection / beam-dump consistency

**Question**: Does m_chi = 6 GeV + 8 MeV mediator + small ε make concrete DD/beam-dump predictions, and are they consistent with existing limits?

**Method**:
- Resonant SIDM doesn't directly predict DD cross-section (no σ_SI from Breit-Wigner form)
- Use **kinetic mixing** ε (assumed small, σ_SI << 10⁻⁴⁶) to check DD limits
- For beam dumps (LDMX, NA64, etc.): mediator can be produced if ε is large enough
- Currently Phase 29 has asymmetric DM, so annihilation is suppressed → only DD + beam dumps constrain

**Existing infrastructure**:
- `code/t62_lz_direct_detection.py` (LZ sensitivity)
- `code/t76_reframe_direct_detection.py` (DD limits)

**Expected output**:
- σ_SI prediction from resonant SIDM (with kinetic mixing ε as free parameter)
- Compared to LZ, XENONnT, PandaX limits
- Beam-dump reach for ε in [10⁻⁵, 10⁻³]

**Verdict likely**: CONSISTENT (σ_SI << 10⁻⁴⁶) — model evades current DD limits

**Effort**: ~1 hour

---

## Sequencing

**Phase 31a (this phase, fast):** Tests C, H, I — all have existing infrastructure, ~1 hour total
- Test C: subhalo real data (30 min)
- Test H: core size (30 min)
- Test I: DD consistency (30 min)

**Phase 31b (medium term, 1-2 hours):** Test E — UV completion scan
- Extend T105 to include resonance target

**Phase 31c (deferred):** Test G — stream gaps need new forward model, defer unless requested

---

## What this delivers

After Phase 31a-c, the verdict becomes:

**If all 5 tests come back reasonable:** Verdict stays **PLAUSIBLE** — model survives scrutiny from 9/9 tests.

**If 2-3 tests fail:** Verdict becomes **PARTIALLY_PLAUSIBLE** — model has 2-3 structural weaknesses beyond the already-documented SPARC tension.

**If 4-5 tests fail:** Verdict becomes **NOT_PLAUSIBLE** — model is too phenomenological, needs major rework.

Most likely outcome: **PARTIALLY_PLAUSIBLE** with specific failures in:
- Test E (UV completion likely NO_KNOWN_UV for Γ/E = 0.013)
- Test G (stream gaps likely predict too few gaps due to σ/m(200) = 0.013)
- Tests C, H, I likely pass

---

## User's role

- **Approve Phase 31a** (the fast 3-test scan, ~1 hour)
- **Decide on Phase 31b** (UV scan, 1-2 hours, likely gives "no known UV" verdict)
- **Decide on Phase 31c** (stream gaps, 3-4 hours, new forward model)
- **Or specify different priorities**

---

## File deliverables

- `code/phase31a_subhalo_real_data.py`
- `code/phase31a_core_size.py`
- `code/phase31a_direct_detection.py`
- `code/phase31b_uv_completion.py` (optional)
- `code/phase31c_stream_gaps.py` (optional)
- `tests/test_phase31_*.py`
- `docs/PHASE31_FIVE_TESTS_2026_09_14.md`

---

## Recommendation

Run Phase 31a (1 hour, 3 tests) first. Then decide whether to run Phase 31b (UV) and Phase 31c (streams) based on results.
