# Future Work Plan — SIDM Composite DM Mediator v19.2-E (Next Paper)

**Compiled:** R88(56) follow-up, commit 429f0c3
**Purpose:** Explicit roadmap for the next paper (v19.2-E)
**Status:** Current paper (v19.2-D, R88(56)) submission-ready as Direction C
**Scope:** Six prioritized paths with concrete deliverables, kill criteria, and resource estimates

---

## 0. Context

The current paper (v19.2-D, R88(56)) establishes a constraint map + no-go catalogue with three first-class results:
1. §2.6a: Cloud-9 vs dSph tension at v=28↔15
2. §9.17a: Lei/Wang vs Sameie+ 2020 tension at v=150
3. §9.17b: Structural trade-off theorem (Phase G10)

These three results are robust. They survive:
- A physically-motivated segregation model (Phase G9: drop factor 0.94-1.01×, kill criterion NOT met)
- A first-principles SIDM2c parameterization (Phase G10: trade-off theorem)

The current paper's contribution is the structural map. The next paper (v19.2-E) would pursue one or more of the six forward paths below.

---

## 1. Priority 1 — Direction D: Observational Refinement

**Timeline:** 0 additional computation (monitoring only)
**Resource:** 0 FTE
**Reversibility:** Maximum (just wait for new data)
**Risk:** Low

### 1.1 Specific actions

1. **Monitor Sameie+ 2020 follow-up publications**
   - Track arXiv submissions citing Sameie+ 2020 (subhalo mass function in MW-mass hosts)
   - Watch for revisions with explicit f_H(r) treatment in the Jeans/lensing modeling
   - If a revision shifts σ_eff(150) by factor ~2, the v=150 no-go dissolves

2. **Monitor Lei/Wang follow-up publications**
   - Track arXiv submissions citing Lei+ 2026 / Wang+ 2026 (inner DM fraction in massive galaxies)
   - Watch for revisions with explicit f_H(r) treatment
   - If either shifts σ_eff(150) by factor ~2, the v=150 no-go dissolves

3. **Systematic comparison of modeling assumptions**
   - Document the modeling assumptions in Sameie+ 2020 (lensing + satellite kinematics + baryonic feedback)
   - Document the modeling assumptions in Lei/Wang (Jeans modeling + stellar kinematics + gas dynamics)
   - Identify which is more sensitive to the f_H(r) assumption
   - Determine which observation should be trusted more

### 1.2 Deliverables

- **D-1:** Quarterly update to `FINDINGS_FOR_FUTURE_DELIBERATION.md` documenting new observational results
- **D-2:** Short paper draft (~10 pages) titled "Observational status of the v=150 tension" if either observation updates
- **D-3:** If no-go dissolves: short paper demonstrating the dissolution + re-running all channels with new σ_eff(150)

### 1.3 Kill criteria

- None — this is monitoring, not a test. Continue indefinitely.

---

## 2. Priority 2 — Path 3: Cosmological Merger Histories (Phase G2 Cosmological)

**Timeline:** 3-4 months
**Resource:** 1 FTE + access to IllustrisTNG / EAGLE / FIRE public data
**Reversibility:** Medium (can abandon midway)
**Risk:** Medium-high (depends on simulation coverage)

### 2.1 Motivation

Phase G2 (R88(49)) currently uses hand-classified merger histories (quiescent/active/mixed). Replacing these with empirical merger trees from cosmological simulations could supply the missing phase diversity.

The structural trade-off theorem (Phase G10) says single-species σ_m(v) with any physically-derived f_H(r) cannot satisfy all channels. Path 3 tests whether **phase diversity from real merger histories** changes this — if different halos end up at different τ, the trade-off may not bind uniformly.

### 2.2 Implementation steps

**Step 1 (2 weeks): Halo identification**
- Identify host halos for Cloud-9, Fornax, Sculptor, Draco in IllustrisTNG-300 (or TNG-100)
- Identify RELHIC-like candidates (isolated, low-mass, baryon-poor)
- Catalog halo IDs and snapshot numbers

**Step 2 (3 weeks): Merger tree extraction**
- Use `subfind` or consistent-trees code to extract full merger histories
- Track: mass assembly history, pericenter passages, tidal events, redshift of last major merger
- For each constrained halo: full merger history from z=0 to z=2

**Step 3 (3 weeks): Gravothermal phase calculation**
- For each halo at each epoch, compute gravothermal phase τ = t/t_c
- Use Phase G1 Yang+ 2024 calibration with proper σ_eff at each epoch
- Track τ evolution through cosmic time

**Step 4 (3 weeks): Coupled σ_m(v) + f_H(r) + τ**
- Combine: σ_m(v) from Phase G7/G8, f_H(r) from Phase G10 SIDM2c, τ from cosmological merger
- Test if empirical τ distribution produces observed core-collapse / non-collapse diversity
- Check if Cloud-9, Fornax, Sculptor, Draco end up at different τ regimes

**Step 5 (2 weeks): Re-run all channels**
- Phase G4 pipeline with new τ distribution
- Phase G7 channel stress test with empirical f_H(r, τ)
- Check if v=150 tension dissolves for SOME halos (centrals at low τ) but not others (subhalos at high τ)

### 2.3 Deliverables

- **P3-1:** Phase G2 cosmological module (~500 lines)
- **P3-2:** New paper (v19.2-E) titled "Cosmological phase diversity in SIDM halos" (~30 pages)
- **P3-3:** Updated `FINDINGS_FOR_FUTURE_DELIBERATION.md` with cosmological phase results

### 2.4 Success / Failure criteria (R88(58) sharpened)

**Success:** Empirical merger histories produce τ values that differ by ≥ factor 2 across the constrained halos (Cloud-9 vs Fornax vs Sculptor vs Draco), allowing phase diversity to break the trade-off theorem. Specifically: at least one halo must be at τ < 0.5 and another at τ > 1.0, with the spread distributed across the full sample.

**Failure:** All constrained halos end up at τ < 0.5 or τ > 2.0 (uniform phase), meaning merger history doesn't supply the missing diversity. The trade-off theorem stands.

**Ambiguous:** τ spread is factor 1.5-2.0 — marginal; requires follow-up with larger sample.

**Data availability kill:** If IllustrisTNG-300 has < 10 RELHIC-like halos with full merger histories, the sample size is too small for statistical conclusions. In this case, Path 3 terminates with "data inadequate" verdict.

### 2.6 Why this matters

Path 3 is the **only untested forward path**. All others (Direction A, Direction B) have been tested and found to have inherent limitations (Phase G9, Phase G10). If Path 3 doesn't work either, the structural trade-off theorem is genuinely binding, and the framework is at its fundamental limit.

### 2.6 Why this matters

Path 3 is the **only untested forward path**. All others (Direction A, Direction B) have been tested and found to have inherent limitations (Phase G9, Phase G10). If Path 3 doesn't work either, the structural trade-off theorem is genuinely binding, and the framework is at its fundamental limit.

---

## 3. Priority 3 — Direction B: Multi-Species UV Completion

**Timeline:** 1-2 months + uncertain payoff
**Resource:** 1 FTE + UV physics expertise
**Reversibility:** Low (UV construction is irreversible)
**Risk:** High

### 3.1 Motivation

Direction B is the **only path that breaks the trade-off theorem by construction**. A multi-species model with environment-dependent cross-sections could, in principle, satisfy Sameie+ 2020 (subhalos) and Lei/Wang (centrals) simultaneously without killing Cloud-9/SPARC.

### 3.2 Implementation requirements

**Requirement 1: Fresh Lagrangian**
- Two or more dark species (e.g., heavy + light, with mass ratio > 10)
- Mediator(s) producing different σ(v) shapes for each species
- Symmetry structure (U(1), SU(2), etc.) that allows species-specific couplings

**Requirement 2: Environment-dependent cross-sections**
- Central galaxies: heavy + light both present, σ_central(v)
- Satellite galaxies / subhalos: heavy preferentially lost via tidal stripping, σ_sub(v) ≈ σ_light(v)
- This is the key feature: different σ(v) in different environments

**Requirement 3: Re-derive all scaling relations**
- σ_m(v) for central halos (used by Lei/Wang, Cloud-9, SPARC)
- σ_m(v) for subhalos (used by Sameie+ 2020)
- Gravothermal evolution for both populations
- LZ direct-detection cross-section (must remain < 9.4×10⁻⁴⁸ cm²)

### 3.3 Implementation steps

**Step 1 (3 weeks): UV construction**
- Define Lagrangian with two dark species + mediator
- Compute σ(v) for each species
- Identify natural environment-dependence mechanism

**Step 2 (3 weeks): Channel-by-channel test**
- Apply new σ_m(v) to all 10 channels
- Verify Cloud-9, SPARC, Lei/Wang still pass (centrals)
- Verify Sameie+ 2020 now passes (subhalos with light-only σ)
- Verify LZ still satisfied

**Step 3 (2 weeks): Re-derive structural trade-off**
- Does the new σ_m(v) break the trade-off theorem?
- If yes: paper-worthy result
- If no: Direction B also fails

### 3.4 Deliverables

- **B-1:** Multi-species UV Lagrangian and σ(v) derivation
- **B-2:** New paper (v19.2-E) titled "Multi-species SIDM with environment-dependent cross-sections" (~30 pages)
- **B-3:** Updated findings document with new structural no-gos (or dissolution thereof)

### 3.5 Success / Failure criteria (R88(58) sharpened)

**Success:** A concrete Lagrangian with two dark species and mediator(s) produces σ_central(v) and σ_sub(v) that satisfy all 10 channels simultaneously, including both Sameie+ 2020 (v=150) and Lei/Wang (v=150). The model must also preserve LZ bound (σ_SI < 9.4×10⁻⁴⁸ cm²) and have a consistent UV completion (no symmetry breaking violations, no Lorentz invariance violations).

**Failure:** Any two-species model that satisfies Sameie+ 2020 also kills Cloud-9/SPARC/Lei-Wang (the trade-off theorem generalizes to multi-species). Document the failure mode.

**Ambiguous:** A model satisfies some channels but not all — requires further tuning. Document which channels pass and which fail, and identify the bottleneck.

**Decision gate:** Only pursue Direction B if Path 3 fails. If Path 3 produces phase diversity, Direction B is deferred (not needed). This is the R88(58) sequencing recommendation.

This is a high-risk path. The trade-off theorem says single-species σ_m(v) is fundamentally limited; multi-species is the only escape. But constructing a consistent UV model is hard, and the result may simply be that no such model exists at the relevant parameter point.

---

## 4. Priority 4 — Open Questions from §16.5

**Timeline:** Variable (each is bounded)
**Resource:** 1 FTE partial
**Reversibility:** Maximum (pure investigation)
**Risk:** Low

### 4.0 Prioritization (R88(58))

The four open questions are NOT equal priority. Suggested ordering:

1. **Q3 (Sameie+ 2020 vs Lei/Wang reliability)** — directly informs Direction D; if one observation is unreliable, the v=150 no-go dissolves. **Highest priority.**
2. **Q1 (why Phase G7 f_H(r) works)** — could reveal a loophole in the trade-off theorem. **High priority.**
3. **Q4 (multi-component UV feasibility)** — overlaps with Direction B; pursue only if Direction B is started. **Medium priority.**
4. **Q2 (intermediate-radius observables)** — speculative; useful as background for Direction D and Path 3. **Lowest priority.**

### 4.1 Four bounded investigations

**Q1 — Why does Phase G7 phenomenological f_H(r) work as well as it does?**
- The trade-off theorem says it shouldn't (heavy should be too concentrated at center for SIDM2c)
- But empirically, Phase G7 f_H(r) makes Cloud-9/SPARC/Lei-Wang all consistent
- Investigate: what property of Phase G7 f_H(r) makes it more permissive than SIDM2c?
- Method: Compare Phase G7 f_H(r) to SIDM2c at intermediate radii (r ~ 0.5-2 r_s); identify which channels are insensitive to the difference
- Deliverable: Short note (~10 pages) documenting the comparison

**Q2 — Are there observables at intermediate radii?**
- Current channels probe σ_eff at r_obs ~ 0.5 r_s (Cloud-9) and r_obs ~ 1.5 r_s (SPARC, Lei/Wang)
- The trade-off binds most strongly at r_obs ~ 1-2 r_s
- Survey: stellar streams (GD-1, Pal 5), strong lensing at intermediate radii, gas kinematics
- Method: Identify which intermediate-radius observables have published σ_eff constraints
- Deliverable: Survey paper (~20 pages) listing all intermediate-radius probes

**Q3 — Is Sameie+ 2020 or Lei/Wang more reliable?**
- Direction D hinges on which observation the field should trust more
- Compare: modeling assumptions, systematic uncertainties, statistical methodology
- Method: Reproduce both analyses with explicit f_H(r) treatment; compare residuals
- Deliverable: Comparative analysis paper (~15 pages)

**Q4 — Can a multi-component UV model break the trade-off theorem?**
- Same as Priority 3 but with smaller scope
- Investigate: minimum UV requirements to break the theorem
- Method: Derive necessary conditions; check if any published UV model satisfies them
- Deliverable: Short note (~10 pages) on UV feasibility

### 4.2 Deliverables

- **Q-1 to Q-4:** Four short notes, each ~10-20 pages
- Each can be published independently as standalone papers or combined

### 4.3 Kill criteria

- Each investigation has natural termination (no more interesting questions to ask)
- No external kill criterion; pure exploration

---

## 5. Priority 5 — Convert Approximate Passes to Actual Ones (Defensibility)

**Timeline:** 1-2 months each
**Resource:** 1 FTE
**Reversibility:** Maximum (improvement, not replacement)
**Risk:** Low

### 5.1 Two defensibility improvements

**D1 — SASHIMI re-run for Horigome+ 2025**
- Current Horigome PASS is approximate (uses σ_eff(r_obs) < 0.8 ceiling as proxy)
- Real check needs SASHIMI likelihood with full σ(v,θ) dependence
- Convert approximate PASS into actual one
- Timeline: 1-2 months
- Impact: Submission-grade defensibility for the dSph channel

**D2 — SPARC re-fit at σ_eff ≈ 0.19**
- Current SPARC: σ_eff = 0.091 vs target ~0.19 (factor 2 below)
- Use full per-galaxy likelihood (Jia-style re-implementation from scratch)
- Test if framework can hit SPARC exactly
- Risk: tight SPARC fit may break Cloud-9 / Horigome balance
- Timeline: 1 month

### 5.2 Deliverables

- **D-1:** SASHIMI likelihood re-run + paper supplement
- **D-2:** SPARC per-galaxy likelihood + paper supplement

### 5.3 Success / Failure criteria (R88(58) sharpened)

**D1 — SASHIMI re-run:**
- Success: Likelihood confirms σ_eff(r_obs) < 0.8 at ≥ 95% CL using the framework's σ(v,θ) form. Converts approximate PASS to actual PASS.
- Failure: Likelihood rejects σ_eff(r_obs) < 0.8 at > 5% CL. The Horigome PASS becomes FAIL. Honest disclosure required.
- Ambiguous: Likelihood is inconclusive (e.g., depends on prior choice). Document the dependence.

**D2 — SPARC re-fit:**
- Success: σ_eff(100) within factor 2 of 0.19 with no more than 10% degradation in Cloud-9 / Horigome fit quality. Establishes SPARC as robust PASS.
- Failure: Either (a) σ_eff(100) outside factor 2 of 0.19, or (b) achieving σ_eff(100) ≈ 0.19 requires breaking Cloud-9 / Horigome balance by >10%. SPARC becomes FAIL or MARGINAL. Trade-off must be disclosed.

### 5.4 Kill criteria

- D-1: If SASHIMI likelihood rejects framework's σ(v,θ), the Horigome PASS becomes FAIL. Honest disclosure required.
- D-2: If SPARC re-fit requires breaking Cloud-9 / Horigome balance, the SPARC PASS becomes FAIL. Trade-off must be disclosed.

---

## 6. Priority 6 — KiSS-SIDM Patches Upstream

**Timeline:** Days (writing the PR)
**Resource:** 0.1 FTE
**Reversibility:** Maximum (PR can be revised)
**Risk:** Minimal

### 6.1 Specific actions

Submit T215 patches to KiSS-SIDM as a PR:
- FP protection (avoid floating-point exceptions in collision kernel)
- Assertion disable (allow production runs without debug assertions)
- min_particles increase (avoid spurious particle clumps)

### 6.2 Deliverables

- **K-1:** KiSS-SIDM GitHub PR with T215 patches
- **K-2:** Brief methods note documenting the numerical fixes (~5 pages)

### 6.3 Kill criteria

- None — methods contribution, always valuable

---

## 7. Recommended Sequence and Dependencies (R88(58) refined)

### 7.1 Sequencing (with decision gate)

Path 3 and Direction B are **NOT parallel paths** — they're sequential with a decision gate. If Path 3 succeeds, Direction B is unnecessary.

```
1. Direction D (monitoring, ongoing) ──────────────────────────┐
                                                              │
2. Path 3 (cosmological merger histories, 3-4 months)         │
                                                              │
   Decision gate (after Path 3 completes):                     │
   ├── Success (τ diversity ≥ factor 2)                       │
   │   → Ship v19.2-E with phase-diversity paper              │
   │   → Direction B DEFERRED (not needed)                    │
   ├── Failure (uniform τ)                                   ─┤
   │   → Direction B becomes MANDATORY                       │
   │   → Path 3 negative result documented as paper         │
   └── Ambiguous (τ spread 1.5-2.0)                          │
       → Refine Path 3 with more halos                       │
       → Defer Direction B decision                          │
                                                              │
3. Direction B (multi-species UV, 1-2 months) — ONLY IF Path 3 fails ─┘
4. Open questions (opportunistic, can run in parallel)
5. Defensibility improvements (can run in parallel with Path 3)
6. KiSS-SIDM PR (can run anytime, days)
```

### 7.2 Parallel execution

- **Path 3** and **Direction D** can run in parallel (Path 3 is compute; Direction D is monitoring)
- **Defensibility improvements** (Priority 5) can run in parallel with Path 3
- **Open questions** can run in parallel with anything
- **Direction B** is **sequential after Path 3**, not parallel
- **KiSS-SIDM PR** is independent, can run anytime

### 7.3 Deliverables table

| Order | Path | Timeline | Dependencies | Deliverable |
|-------|------|----------|--------------|-------------|
| 1 | Direction D | 0 comp | None | Quarterly updates to findings |
| 2 | Path 3 (cosmological) | 3-4 mo | None | v19.2-E paper, 30 pages |
| 3 | Direction B (multi-species) | 1-2 mo | **After Path 3 fails** | v19.2-E paper, 30 pages |
| 4 | Open questions (Q1-Q4) | variable | None | 4 short notes |
| 5 | SASHIMI + SPARC | 1-2 mo ea | None | Paper supplements |
| 6 | KiSS-SIDM PR | days | None | Methods contribution |

---

## 8. Resource Estimates

| Path | FTE-months | Disk | Compute |
|------|------------|------|---------|
| Direction D | 0.1 | 0 | 0 |
| Path 3 | 4 | 500 GB (IllustrisTNG snapshots) | 1000 CPU-hr (merger tree extraction) |
| Direction B | 2 | 50 GB | 100 CPU-hr (parameter scans) |
| Open questions | 2 | 10 GB | 200 CPU-hr |
| Defensibility | 3 | 100 GB | 500 CPU-hr |
| KiSS-SIDM | 0.1 | 0 | 0 |

**Total for full program:** ~10 FTE-months, 650 GB disk, 1800 CPU-hr

**Minimum viable program (Path 3 + Direction D + Defensibility):** ~7 FTE-months

---

## 9. Go/No-Go Decision Tree (R88(58))

```
Path 3 result?
├── Success (τ diversity ≥ factor 2)
│   → Ship v19.2-E with phase-diversity paper (~30 pages)
│   → Title: "Cosmological phase diversity in SIDM halos:
│            a test of the structural trade-off theorem"
│   → Direction B DEFERRED (not needed)
│   → Open questions shift focus (Q1 becomes less critical)
│
├── Failure (uniform τ)
│   → Direction B becomes MANDATORY
│   → Path 3 negative result documented as paper (~25 pages)
│   → Title: "Phase uniformity in cosmological merger histories:
│            the structural trade-off theorem as fundamental limit"
│   → Direction B starts immediately after
│
└── Ambiguous (τ spread 1.5-2.0)
    → Refine Path 3 with more halos (1-2 months additional)
    → Defer Direction B decision
    → Ship "Path 3 inconclusive" note (~15 pages)
```

## 10. Minimum Publishable Unit (MPU)

If the full program can't be funded, the smallest publishable contribution is:

**MPU = Path 3 result + Direction D update + SASHIMI re-run**

This produces one paper (~30 pages) titled **"Cosmological phase diversity in SIDM halos: a test of the structural trade-off theorem"** regardless of whether Path 3 succeeds or fails.

- If Path 3 succeeds: positive result + SASHIMI confirmation + observational status
- If Path 3 fails: negative result + SASHIMI confirmation + observational status
- If Path 3 ambiguous: inconclusive result + SASHIMI + observational status

**All three outcomes are publishable.** The MPU is the fallback if Path 3 + Direction B + full defensibility program isn't funded.

## 11. Negative Result Framing for Path 3

The plan currently frames Path 3 as a search for a resolution. But a negative result is also publishable and scientifically valuable.

**Negative result paper (Path 3 fails):**

> "We tested whether cosmological merger histories supply the phase diversity needed to resolve the v=150 no-go. Across 5-10 RELHIC-like halos in IllustrisTNG-300, all constrained halos ended up at gravothermal phase τ < 0.5 or τ > 2.0 (uniform distribution). Merger history does not produce the phase diversity required to break the structural trade-off theorem. The trade-off therefore stands as the fundamental limit of single-species SIDM with the Phase 44 parameter point."

This is a **stronger scientific claim** than "we tried and it didn't work." It establishes the trade-off theorem as the boundary of what single-species SIDM can achieve.

## 12. Bottom Line

The current paper (v19.2-D, R88(56)) is **submission-ready as Direction C**. The future-work plan above represents the explicit roadmap for v19.2-E.

**The single most important future path is Path 3 (cosmological merger histories)** — it's the only untested forward direction, and it tests whether empirical phase diversity can break the structural trade-off theorem.

**The cheapest future path is Direction D** (observation monitoring) — zero computation, fully reversible, may dissolve v=150 no-go.

**The most fundamental future path is Direction B** (multi-species UV) — only way to break the trade-off by construction, but **only pursued if Path 3 fails** (R88(58) sequencing). High risk and uncertain payoff.

**The defensibility improvements (Priority 5) and methods contributions (Priority 6) are valuable but don't address the structural tensions** — they're hygiene improvements, not resolution attempts.

**Recommendation:** Start Path 3 in parallel with Direction D monitoring. After 3-4 months, apply the go/no-go decision tree:

- If Path 3 succeeds: ship v19.2-E with phase-diversity paper; Direction B deferred
- If Path 3 fails: ship negative result paper; Direction B becomes mandatory
- If Path 3 ambiguous: refine with more halos; defer Direction B decision

The MPU (Path 3 + Direction D + SASHIMI) is the fallback if full program isn't funded.

**The framework has reached its natural conclusion for the current paper. The next paper is genuinely forward-looking research, with explicit decision gates and publishable outcomes regardless of result.**
