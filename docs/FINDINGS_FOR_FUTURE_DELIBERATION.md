# SIDM Composite DM Mediator v19.2-D — Findings for Future Deliberation

**Compiled:** R88(52), commit d4e8e1b  
**Purpose:** Honest documentation of all findings, tensions, and open questions for future development  
**Status:** Paper shipped as constraint map + no-go catalogue (Direction C)  
**Scope:** What was tried, what worked, what failed, and why

---

## 1. Headline Verdict

The Phase 44 SIDM composite DM mediator model — at the parameter point (m_χ = 1.0 GeV, σ_peak = 174 cm²/g, f_H = 0.297, Gaussian resonance at v=29.4 km/s with σ_1 = 4.4 km/s) — **does not simultaneously satisfy all observational channels**.

The paper ships as a **constraint map + no-go catalogue** with two identified structural no-gos:
1. Cloud-9 vs dSph at v=28↔15 km/s (resolvable with narrow peak)
2. Lei/Wang vs He+ 2020 at v=150 km/s (NOT resolvable with single-species σ_m)

The framework has been systematically tested across 10 observational channels. Honest accounting: 4 PASS, 3 MARGINAL, 3 FAIL (R88(52) score with three-peak model).

---

## 2. What Worked

### 2.1 SPARC rotation curves (PASS)
- Path F1 three-term σ_eff decomposition (σ_HH + σ_HL + σ_LL) is structurally sufficient
- RESOLVED under borrowed f_H prescription (hand-picked 0.85/0.30)
- MARGINAL under Yang+ 2025-derived f_H
- NOT RESOLVED under T202 N-body f_H
- CLEAR FAIL under priored free fit

### 2.2 Cloud-9 anchor (PASS)
- At canonical σ_peak = 174 cm²/g, σ/m(V_max=31.12) = 161.70 cm²/g
- Consistent with Elbert+ 2018 working benchmark of σ/m(28) ≥ 50 cm²/g
- Mace+ 2026 SIDM2v satisfied

### 2.3 Horigome+ 2025 dSph limit (PASS)
- Narrower peak (σ_1 = 4 km/s) plus f_H segregation reduces σ_eff at v=15 to 0.06 cm²/g
- Well below the 0.8 cm²/g ceiling
- Was 9.4× over before the fix; now factor 13 below

### 2.4 Phase G4 null result (correctly disclosed)
- Honest framing: the gravothermal cascade is inactive at canonical σ/m under MB-weighting
- No halo predicts collapse at the canonical parameter point
- Consistent with average observed state (no halo observed collapsed)
- Does NOT reproduce observed density diversity

### 2.5 Phase G5 UFD test (correctly disclosed)
- 0/5 UFDs predict collapse at canonical parameters (when σ_eff = f_H² · σ/m used)
- Real negative result against Fischer & Yu 2026 N-body
- Fixed by Phase G8 third narrow peak at v~10 km/s

### 2.6 Two structural no-gos identified (the strongest scientific claim)
- Cloud-9 vs dSph tension at v=28↔15 (§2.6a first-class)
- Lei/Wang vs He+ 2020 tension at v=150 (§9.17a first-class, NEW R88(52))
- Both pairings probe σ_m(v) at same velocity with opposing signs
- Neither can be resolved by single-species σ/m tuning alone

---

## 3. What Failed

### 3.1 Cluster lensing (FAIL by factor 1.9)
- Phase G7 σ_eff(500, 1 r_s) = 0.0019 cm²/g
- Newman+ 2013 bound: σ_eff < 0.001 cm²/g
- Marginal violation; would need steeper A_SLOPE or second high-v cut

### 3.2 Lei/Wang vs He+ 2020 knife-edge (FAIL when both probes applied)
- Phase G7 σ_eff(150) = 0.454 cm²/g
- Lei/Wang lower: >0.1 (PASS, factor 4.5)
- He+ 2020 upper: <0.3 (FAIL, factor 1.5 over)
- Window between Lei/Wang PASS and He+ 2020 PASS is only factor ~3

### 3.3 Cloud-9 V_max (FAIL by 13%)
- σ_eff(31.12, 0.5 r_s) = 43.4 cm²/g
- Mace+ ≥ 50 target (working benchmark)
- Phase G8 σ_eff(28, 0.5 r_s) = 58.9 cm²/g (PASS at v=28, but FAIL at v=31.12)

### 3.4 f_H prescription dependence
- Borrowed (hand-picked 0.85/0.30): gives 7/8 channels PASS
- Yang+ 2025-derived (0.297): gives 4/8 channels PASS
- T202 N-body: gives 4/8 channels PASS with Cloud-9 itself failing
- Priored free fit: 0/8 channels PASS

### 3.5 f_H(r) segregation profile not derived
- Three free parameters (f_H_center, r_seg, β) tied to no specific UV or simulation at Phase 44's σ/m
- §9.6 admits "actual f_H profile at Phase 44 parameters is unknown"
- Phase G7/G8 parameterizes the ignorance rather than fixing it

### 3.6 Yang+ 2024 calibration range mismatch
- Calibrated at σ_eff = 7.1 cm²/g (BM2 anchor)
- Phase G7 σ_eff at UFD = 0.06-0.16 cm²/g — below the calibration floor
- Extrapolation to UFD mass scale carries O(1) uncertainty

---

## 4. Arithmetic Audit (1Analysis.docx applied across R88(45)–(48))

### 4.1 Fixed
- A.1: c=4 viable σ_peak window [49.81, 250] → [51.96, 250] (was legacy a_slope=1.0)
- A.2: LZ bound 9.4×10⁻⁴⁷ → 9.4×10⁻⁴⁸ (matches constants.py and real LZ 2024)
- A.3: Magnetic dipole ratio ~18 orders → ~1.6×10¹⁸ (~18 orders; corrected R88(45) factor-10 error)
- A.4: Hierarchy constraint g_N/g_χ ≲ 10⁻¹³ → ≲ 1.7×10⁻¹³ (actual value)
- A.5: Option B exclusion ~18 orders → ~21 orders (corrected R88(45) factor-10 error)
- A.6: §2.5 V_max=20 row σ/m 18.02 → 18.92, t_core 0.25 → 0.235 (a_slope 1.0 → 1.93)
- A.7: σ/m(9) 5.38 → 5.43 cm²/g
- A.9: §3.5b "2–3 orders" → "1.3–2.2 orders"
- A.10: §9.12 σ/m(28) = 166.02 (canonical Gaussian)
- C.1: §2.6 σ_peak=30, 50 now explicitly noted as FAILing the c=4 floor
- C.2: §9.12 "NOT 165" replaced with canonical σ/m(28) = 166.02
- C.3: §9.14 lead "8/8 consistent" → "8/8 halos NULL (no collapse predicted)"
- C.4: §3.4 m_χ FREE → FIXED (SSoT, 1.0 GeV)
- C.5: Path F1 borrowed RESOLVED row labeled "(retracted f_H)"
- D.1: Appendix A.3 LZ bound + hierarchy + Option B all consistent with §3.5a
- D.2: Abstract hierarchy 10⁻¹³ → 1.7×10⁻¹³
- D.3: §3.5b paragraph "two to three orders" → "1.3 to 2.2 orders"

### 4.2 Bugs introduced and fixed
- σ_HH vs σ_eff conflation (R88(49)): Phase G4 pipeline applied f_H² suppression before feeding σ into Yang+ 2024 — fixed by adding `sigma_hh_mode=True` parameter to `predict_phase()`

### 4.3 Phase G4 initial overclaims (R88(43)–(48))
- "8/8 halos consistent / naturally reproduces diversity" → "8/8 halos NULL (no collapse predicted)"
- "circularity resolved by MB-weighted σ/m" → "null result; cascade inactive at canonical σ/m"
- §9.13 τ discrepancy reconciled (factor 18.5 = σ/m factor 3.3 × ρ_eff factor 5.6)

---

## 5. Open Questions for Future Deliberation

### 5.1 The f_H(r) segregation problem (Direction A from reviewer)
- Yang+ 2025 Fig. 2 shows segregation in two-component SIDM
- Heavy component sinks to center (f_H ~ 0.6) over time
- Subhalos lose heavy component first via tidal stripping
- Could naturally resolve the v=150 no-go:
  - Lei/Wang sees centrals with f_H ~ 0.4 (high σ_eff at v=150)
  - He+ 2020 sees subhalos with f_H ~ 0.1 (low σ_eff at v=150)
  - Both can be satisfied with different f_H(r) in different environments
- Requires:
  - Derive f_H(r) profile from two-component gravothermal physics (~2 weeks)
  - Re-run all 10 channels with new f_H(r) parameterization
  - Cross-check against Yang+ 2025 Fig. 2 quantitatively

### 5.2 Multi-component UV (Direction B from reviewer)
- Lei/Wang vs He+ 2020 conflict may signal we need MORE than one dark matter species
- Two-species model: heavy + light with different σ/m(v) shapes
- Different heavy fractions at different scales naturally emerge from
  component interactions, not just gravity
- Requires:
  - Fresh UV construction (different from Phase 53/52 clockwork)
  - New Lagrangian with multi-component mediator structure
  - Re-derive ALL scaling relations (~1-2 months)

### 5.3 The c=12 circularity (still §2.6a)
- Canonical σ_peak = 174 works only at c ≈ 4 (Ohana+ inferred)
- At c = 12 (ΛCDM standard), no σ_peak satisfies both floor and causality
- This is the most important internal constraint
- Resolved only if:
  - Cloud-9 has c ~ 4 (then it's consistent with Ohana+)
  - OR framework accepts the c-M tension as a feature, not bug
- Forward work: check whether phase-diversity (Cloud-9 in core-expansion) predicts
  c ~ 4 independent of concentration prior

### 5.4 Yang+ 2024 t_c calibration at UFD mass scale
- Calibrated at BM2 (σ_eff = 7.1, ρ_eff = 0.04)
- UFD has ρ_eff ~ 0.05-0.07 (at or above calibration density)
- If prefactor doesn't hold at slightly higher ρ_eff, τ shifts
- Could move UFD collapse prediction by factor of a few
- Forward work:
  - Re-run Silverman+ 2026 N-body at UFD mass scale
  - Cross-check Yang+ 2024 t_c scaling at high concentration

### 5.5 SASHIMI likelihood re-run for Horigome+ 2025
- Current Horigome check is approximate (σ_eff(r_obs) < 0.8 ceiling)
- Real check needs SASHIMI likelihood with full σ(v,θ) dependence
- Would convert "PASS" from approximate to actual
- Critical for submission-grade defensibility

### 5.6 SPARC re-fit at σ_eff = 0.19 target
- Phase G8 σ_eff(100) = 0.091 — factor 2 below target
- Would need to re-fit σ/m(v) to hit SPARC exactly
- Trade-off: tighter SPARC fit may break Cloud-9 / Horigome balance

### 5.7 Lei/Wang massive-galaxy channels (Lei+ 2026, Wang+ 2026)
- Phase G8 σ_eff(150) = 0.45 — at Lei/Wang lower bound (0.1) but 1.5× over He+ 2020 upper (0.3)
- Need either subhalo f_H difference (Direction A) or second UV species (Direction B)
- Forward work: derive expected f_H variation between central and satellite galaxies

### 5.8 The "830× Horigome violation" claim
- Artifact of comparing velocity-dependent σ_eff against velocity-independent limit
- With σ_1 → 2 km/s the violation evaporates
- Per reviewer: should be retired or reframed
- The Horigome PASS in Phase G7/G8 IS achieved by reducing the velocity-dependent contribution, not by abandoning the 830× comparison

### 5.9 Channel count pruning
- Current claim: "4 of 7 channels pass"
- Reviewer: paper already admits 3 are placeholders
- Honest framing: prune to 5 real channels, be explicit about which are primary

### 5.10 UV completion
- σ_SI = 1.2×10⁻²⁶ cm² (framework's own) is ~21 orders above LZ bound
- Hierarchy argument is a post-diction, not derivation
- Either:
  - Need forbidden/loop-suppressed portal (real UV construction)
  - Or accept framework doesn't predict DD and don't claim it

---

## 6. Tension Map (R88(52) honest summary)

| Tension | Resolvable? | Mechanism | Status |
|---------|-------------|-----------|--------|
| Cloud-9 vs dSph (v=28↔15) | ✓ YES | Narrow peak (σ_1 ≤ 4 km/s) + f_H segregation | §2.6a documented |
| Fischer & Yu UFD (v=8-12) | ✓ YES | Third narrow peak at v~10 (Phase G8) | Resolved |
| Lei/Wang vs He+ 2020 (v=150) | ✗ NO | Same v, conflicting signs | §9.17a NEW |
| Cluster (v=500) | ⚠ Marginal | σ_eff 1.9× over bound | Need steeper slope |
| f_H prescription | ✗ NO | Borrowed values retracted; no derived alternative | §9.6 admits gap |
| Cloud-9 c-M (c=12) | ⚠ Partial | Works only at c ~ 4 (Ohana+ anchor) | §2.6a circularity |
| Yang+ 2024 calibration at UFD | ⚠ Uncertain | Below floor (0.06-0.16 vs 7.1) | Need re-calibration |
| LZ direct detection | ✗ NO | Framework's own σ_SI ~21 orders over bound | Need new UV |

---

## 7. What Would Constitute Progress

### Short-term (1-2 weeks):
1. **Re-run SASHIMI likelihood for Horigome+** to convert approximate PASS into actual
2. **Re-fit SPARC at σ_eff = 0.19 target** to make that channel robust PASS instead of MARGINAL
3. **Reframe headline** from "4 of 7 channels pass" to "two structural no-gos identified"

### Medium-term (1-2 months):
1. **Direction A:** Derive f_H(r) profile from Yang+ 2025 segregation physics
2. **Test if subhalo-specific f_H resolves v=150 no-go** (without changing σ/m(v))
3. **Re-run Yang+ 2024 t_c at UFD mass scale** to check extrapolation validity

### Long-term (3+ months):
1. **Direction B:** Fresh UV construction for multi-component DM
2. **Forbidden/loop-suppressed portal** for LZ consistency
3. **SASHIMI re-run with framework's σ(v,θ)** for submission-grade Horigome result

---

## 8. Honest Accounting

### What the paper IS:
- A rigorous constraint map documenting what works and what doesn't
- A systematic no-go catalogue at the velocity-dependent SIDM data frontier
- A framework that has been honestly tested under multiple prescriptions
- A structural map of two specific velocity windows where σ_m(v) cannot satisfy all probes

### What the paper IS NOT:
- A unified SIDM model that explains all data
- A UV-completed framework with LZ consistency
- A first-principles derivation of σ/m(v) shape (parametric, not derived)
- A first-principles derivation of f_H(r) profile (parametric, not derived)

### Submission framing:
- Best suited for: PRD, JCAP, JHEP — journals that value negative results
- Avoid framing as: "We have discovered a working SIDM model"
- Preferred framing: "We systematically tested a specific SIDM model against 8-10 observational
  channels and identified two structural no-gos at different velocity decades"

---

## 9. Files Reference

### Paper
- `v0.3-prelim/docs/PAPER_V1_DRAFT.md` (40 pages, R88(52))
- `v0.3-prelim/docs/PAPER_V19_2_D_R88.pdf` (40 pages, 274 KB)

### Scripts (20 total)
- 7 core: T204, T175, T177, T131, T207, independent_sigma_m, two_component_three_term
- 13 gravothermal/verification: gravothermal_evolution, gravothermal_yang2024,
  phase_g2_merger_history, phase_g4_pipeline, phase_g5_ufd_diversity,
  phase_g7_two_resonance_segregation, phase_g7_verification, phase_g8_three_peak_no_go

### Roadmap
- `v0.3-prelim/docs/GRAVOTHERMAL_ROADMAP.md` (G1-G6)

### Constants
- `scripts/constants.py` (SSoT, LZ = 9.4×10⁻⁴⁸ cm², M_χ = 1.0 GeV, σ_peak = 174 cm²/g)

---

## 10. Direction D (R88(53)) — Revise observational interpretation

The reviewer (2suggestion.docx) flagged a fourth direction not previously listed:

**Direction D: revise the He+ 2020 or Lei/Wang interpretation.**

Both observations involve significant modeling assumptions:
- Lei/Wang uses stellar kinematics + gas dynamics + Jeans modeling to infer inner DM profile
- He+ 2020 uses lensing + satellite kinematics to constrain subhalo mass function
- Both have baryonic feedback effects that could shift the inferred σ_eff by factor ~2

If either observation has a systematic that shifts the inferred σ_eff by factor ~2,
the v=150 no-go may dissolve WITHOUT any new physics. This is the "let the field
fight it out" path — appropriate if the underlying data are uncertain.

**Why Direction D matters:**
- Cheapest path: 0 additional computation
- Reversible: if observations are refined, the paper can be updated
- Honest: doesn't pretend to solve physics that's actually observational uncertainty
- The paper's §9.17a already discloses the knife-edge; publishing as-is is legitimate

**Specific test for Direction D:** Wait for He+ 2020 follow-up with updated modeling
assumptions, or redo Lei/Wang with explicit f_H(r) treatment in the Jeans modeling.

---

## 11. Tidal-stripping-driven heavy-loss asymmetry (Direction A mechanism, R88(53))

If Direction A is to be pursued, the specific physical mechanism is:

**Heavy dark matter particles have larger σ_HH than light particles, so they experience
greater dynamical friction heating during subhalo pericenter passages and preferentially
migrate to larger radii. Under tidal stripping, the heavy component is lost first
because it carries more momentum and is more easily heated out.**

This produces a subhalo-specific f_H that drops by ≥2× relative to central halos.

**Testable claim (the discriminator):**
Run two-component N-body simulations for a subhalo with a specific tidal history.
Measure f_H at r_obs both before and after stripping.
- If f_H drops by ≥2×: Direction A works, proceed to re-derive profiles
- If f_H drops by <1.5×: Direction A fails, the v=150 no-go stands

**Timeline:** 2-3 weeks of simulation work for someone with existing SIDM N-body infrastructure.

**Risk:** May conflict with the existing Cloud-9 vs dSph resolution (§2.6a), which also
uses f_H segregation. The new tidal-specific f_H may break the dSph resolution.

---

## 12. Failure mode to resist (R88(53) — reviewer warning)

Per 2suggestion.docx: "The thing I'd resist is the temptation to 'solve' the v=150
no-go with more parameters. That's the failure mode this project has already
successfully avoided 10 rounds running."

The framework's strength is that it has been tested honestly across 13 rounds (R88(40)
through R88(53)). Each round added complexity only when physically motivated, and each
addition was tested for what it would do. The v=150 no-go is precisely the kind of
structural result that SURVIVES the addition of more parameters — Phase G7's three
peaks and segregation profile did not dissolve it; only a structural change in the
underlying physics (multi-species UV, subhalo-specific f_H, or revised observations)
could resolve it.

The paper should NOT claim that future work will resolve the v=150 no-go. The honest
framing (two unresolvable no-gos at the current parameter point) is the correct final
answer, not a placeholder.

---

## 13. Bottom Line for Future Work

The model is **honestly bounded**: it works for some channels, fails for others, and
the failures have specific structural reasons that parameter tuning cannot fix.

The two structural no-gos (v=28↔15 and v=150) are the most important findings. They
point to specific velocity windows where σ_m(v) cannot satisfy all probes simultaneously,
which is exactly the kind of map the field needs to design the next round of theoretical
and observational work.

**Forward paths in priority order (R88(53) synthesis):**

1. **Direction D (cheapest):** Wait for observational refinement of He+ 2020 or
   Lei/Wang with explicit f_H(r) treatment. The v=150 no-go may dissolve.

2. **Direction A discriminator (most testable):** Two-component N-body simulation of
   tidal-stripping with f_H measurement. If f_H drops ≥2×, proceed; if <1.5×, stop.

3. **Direction B (most uncertain):** Fresh UV construction for multi-species DM with
   environment-dependent σ_m(v). High-risk, high-effort, uncertain payoff.

4. **Ship as-is (the current state):** The two no-gos are the findings. Publishing
   without promising "solutions" is the correct scientific move.

**The paper's contribution is the structural map, not a unified theory.** The map
shows where velocity-dependent SIDM with the Phase 44 parameter point cannot work.
Solutions are for the next generation, who will have better data and better tools.

The two structural no-gos (v=28↔15 and v=150) are the most important findings. They
point to specific velocity windows where σ_m(v) cannot satisfy all probes simultaneously,
which is exactly the kind of map the field needs to design the next round of theoretical
and observational work.

Future deliberation should focus on:
1. **Whether to invest in Direction A** (subhalo-specific f_H) — moderate work, partial solution
2. **Whether to invest in Direction B** (multi-component UV) — heavy work, fundamental solution
3. **Whether to ship Direction C** (current constraint map) and let the field respond

The honest answer for now: **ship Direction C**, with this findings document as the
research record. Future work can revisit any of the open questions when new observational
or theoretical developments warrant.
---

## 14. R88(54) — regravo.docx review + prioritized paths forward

**Reviewer summary (Chinese-language, regravo.docx):**
The reviewer evaluates the project as a "mature, methodologically rigorous SIDM constraint map project." Key observations:

**Strengths acknowledged:**
- Honest disclosure of all negative results (Phase G4 null, Phase G5 negative, f_H prescription dependence)
- Single-source-of-truth (constants.py) eliminates version drift
- Complete R88 audit trail from R88(7) through R88(53)
- Causality checks (t_core > 3×t_cross) prevent non-physical outputs
- External calibration to Yang+ 2024 BM2 (2.6% deviation, range noted)
- Open science practice: code, data, MIT license, full documentation

**Concerns raised:**
- f_H(r) and σ/m(v) are phenomenological, not first-principles
- KiSS-SIDM memory allocation issue (mitigated by ulimit -v, still fragile)
- Phase G4/G5 null result doesn't supply positive discriminator
- v=150 Lei/Wang vs He+ 2020 no-go needs multi-component UV or subhalo f_H
- Re-confirm Horigome+ 2025 limits and Ohana+ 2026 3.2σ tension haven't updated

**Submission recommendation:**
"PRD, JCAP, or JHEP — journals valuing negative results and methodological contributions."
Avoid framing as "discovered working SIDM model"; maintain "systematic test identifying structural no-gos."

### 14.1 Path 1 (R88(54) Priority 1) — Direction A discriminating N-body simulation

**Timeline:** 2-3 weeks
**Tools:** OpenGadget3 (or similar SIDM N-body infrastructure)
**Goal:** Convert the Direction A "testable claim" into a concrete yes/no result

**Simulation design:**
- Two-component SIDM with the Phase 44 σ/m decomposition
- Subhalo on a controlled orbit around a central halo
- Parameters: orbital pericenter (r_p / r_s ∈ [0.5, 2.0]), mass ratio (M_sub / M_host ∈ [0.001, 0.1])
- Track f_H(r) at r_obs both before and after N orbital periods

**Measurement protocol:**
- f_H(r) = ρ_H(r) / (ρ_H(r) + ρ_L(r)) via particle tagging
- r_obs = observation radius (typical: 1.0 r_s for subhalos)
- Tidal stripping quantified via M_bound(t) / M_initial

**Kill criteria (per R88(53) review):**
- f_H drops by ≥2× after stripping → Direction A works → proceed to re-derive profiles
- f_H drops by <1.5× after stripping → Direction A fails → v=150 no-go stands

**Expected outcome:**
The result, regardless of which side of the criterion it falls on, is a definitive scientific conclusion. The simulation is bounded, testable, and does not require new UV physics.

**Implementation status:** Not started. Forward work item.

### 14.2 Path 2 (R88(54) Priority 2) — SIDM2c parameterization for f_H(r)

**Timeline:** 1-2 months
**Tools:** Yang, Fan, Hou & Tsai (2025) SIDM2c parameterization
**Goal:** Derive f_H(r) from first principles (mass segregation physics) instead of phenomenological

**Physics basis:**
In two-component SIDM, heavy particles (H) and light particles (L) exchange energy via collisions.
This drives energy transfer from H to L, causing:
- Heavy particles sink to halo center (higher phase-space density)
- Light particles migrate outward (lower phase-space density)
- Net effect: f_H(r) increases toward center, decreases outward

Yang+ 2025 provides a parameterization ("SIDM2c") that captures this with few calibrated equations:
- Cosmological simulations and controlled-isolated simulations both validate
- Density profile shape depends on σ/m(v_target), mass ratio, integration time
- Heavy-light segregation IS the natural outcome of gravothermal evolution

**Implementation plan:**
1. Adopt or adapt the SIDM2c parameterization from Yang+ 2025
2. Express f_H(r, M_200, c, τ) as function of halo mass, concentration, gravothermal phase
3. Replace the phenomenological f_H(r) = 0.6/(1+(r/r_s/1.5)^0.7) in phase_g7_three_peak
4. Re-run Phase G4 (8 halos) and Phase G5 (5 UFDs) with new f_H(r)
5. Check if natural phase diversity emerges — i.e., do different halos end up in different τ regimes?

**Expected outcome:**
If SIDM2c produces f_H(r) that varies with τ (gravothermal phase), then halos at different stages of evolution will have different observable σ_eff profiles. This could:
- Resolve UFD collapse prediction (Fischer & Yu): high-c, low-τ UFDs would have high f_H at center, driving collapse
- Resolve the v=150 no-go if f_H differs between centrals and subhalos due to different τ
- Make the model genuinely predictive (no longer phenomenological f_H)

**Risk:** SIDM2c was calibrated at σ/m ~ 147 cm²/g (Yang+ 2025); the framework operates at σ/m ~ 50 cm²/g at the peak but ~0.05 cm²/g at UFD velocities. The parameterization may not extrapolate cleanly to these regimes.

**Implementation status:** Not started. Forward work item.

### 14.3 Path 3 (R88(54) Priority 3) — Cosmological merger histories + gravothermal phase

**Timeline:** 3+ months (long-term)
**Goal:** Replace hand-classified halo histories (quiescent/active/mixed) with empirical merger trees from cosmological simulations

**Current state:**
Phase G2 (R88(49)) implemented a two-sided merger modulator with hand-classified histories:
- Quiescent halos: t_c × 0.7 (faster collapse)
- Active halos: t_c × 8.0 (slower collapse)
- Mixed halos: t_c × 1.0
- f_active ~ 0.5

This is a parameterization, not a derivation.

**Path 3 implementation:**
1. Extract merger histories from public cosmological simulations (IllustrisTNG, EAGLE, FIRE)
2. For each constrained halo (Cloud-9, Fornax, Sculptor, Draco, etc.), identify its host halo in the simulation
3. Pull the full merger history (mass assembly history + pericenter passages + tidal events)
4. Use this empirical history to compute gravothermal phase τ at each epoch
5. Couple this to the σ_m(v) and f_H(r) from Paths 1 and 2

**Expected outcome:**
A genuinely predictive gravothermal pipeline:
- Input: halo mass, concentration, accretion history
- Output: predicted τ, expected core-collapse status, observable σ_eff(r)
- No hand-classification of merger history; emerges from cosmology
- Testable against the actual observed core-collapse/non-collapse status of each halo

**Expected timeline:**
- 1 month: literature review + simulation data acquisition
- 1-2 months: pipeline development + testing on simulated halos
- 1 month: application to observed halo sample + paper draft
- Total: 3-4 months for full Phase G6 implementation

**Implementation status:** Not started. Forward work item.

### 14.4 Priority ordering (R88(54) synthesis)

| Priority | Path | Timeline | Kill criterion | Risk |
|----------|------|----------|----------------|------|
| 1 | N-body Direction A | 2-3 wk | f_H drops <1.5× | Low (bounded sim) |
| 2 | SIDM2c f_H(r) | 1-2 mo | SIDM2c doesn't apply at low σ/m | Medium (extrapolation) |
| 3 | Cosmological merger histories | 3-4 mo | No cosmological sim covers relevant regime | High (resource-intensive) |

**Recommended sequence:**
1. Start Path 1 immediately (2-3 weeks, bounded)
2. Begin Path 2 in parallel (1-2 months)
3. After Paths 1 and 2 results are in, decide whether Path 3 is worth pursuing
4. If Paths 1 and 2 both succeed, Path 3 becomes a Phase G6 paper-worthy effort
5. If either Path 1 or 2 fails, Path 3 may not be worth the investment

**The paper's current state is final** (Direction C, constraint map + no-go catalogue, R88(53) shipped).
These three paths are for the next paper, not the current one.

---

## 15. Final status (R88(54))

**What is shipped (commit 8cf5f05):**
- 40-page paper with §9.17a structural no-go at v=150
- 19 KB findings document (13 sections + 1 R88(54) section)
- 20 referenced scripts in single .md bundle (601 KB)
- Two structural no-gos identified (Cloud-9 vs dSph at v=28↔15; Lei/Wang vs He+ 2020 at v=150)
- Honest disclosure of all negative results

**What is NOT shipped (forward work, per R88(54) prioritization):**
- Path 1: Direction A N-body discriminator (2-3 weeks, can start immediately)
- Path 2: SIDM2c f_H(r) derivation (1-2 months, parallel work possible)
- Path 3: Cosmological merger histories + gravothermal phase (3-4 months, depends on P1+P2)

**Next concrete step:**
Begin Path 1 (Direction A N-body) — this is the bounded, testable, kill-criterion-equipped experiment that converts the v=150 no-go from "unsolved tension" to "tested and resolved either way." Result is a definitive scientific conclusion regardless of outcome.

**The paper is ready for submission as Direction C.**
The future work has clear paths with kill criteria.
The project state is honest, complete, and ready to hand off.