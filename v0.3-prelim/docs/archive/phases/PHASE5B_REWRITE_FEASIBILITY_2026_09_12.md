# Channel-Likelihood Rewrite Feasibility (2026-09-12)

**Question:** Is it feasible to rebuild the channel likelihoods to be mediator-class-agnostic (so Phase 5 can properly discriminate power-law vs Yukawa vs scalar vs composite)?

**Answer:** **Yes, but it is a 2-4 week engineering project, not a 1-2 week phase as originally estimated.** The complexity is concentrated in the SPARC grid rebuild.

---

## What needs to change

The existing project likelihoods have the **power-law form baked into multiple places**. To make them mediator-class-agnostic, these need to be parameterized:

### 1. SPARC (the hardest)

**Current state:**
- Pre-computed grid `sparc_hierarchical_grid.npz` (175 galaxies × 50 σ/m × 30 a)
- Built by `v0.3-prelim/code/precompute_sparc_hierarchical.py`
- Per-galaxy likelihood uses **line 148:**
 ```python
 sigma_m_eff = sigma_m * (V_max_kms / RC_SIDM_VMAX_REF) ** a
 ```
- This is exactly the power-law form `σ/m(v) = σ/m_0 × (v/v_ref)^(-a)`

**What needs to change:**
1. Modify `precompute_sparc_hierarchical.py` line 148 to accept a generic `sigma_m_form(sigma_m_0, a, V_max_kms, **extra)` function
2. Add a parameter `mediator_class` to the script that picks one of the 4 forms
3. **Regenerate the grid 4 times** — once per mediator class. Each grid takes ~5-10 minutes (per galaxy, marginalizing over ρ_c with Dutton-Maccio 2014 prior)
4. Modify `loglike_sparc_hierarchical()` to accept a `mediator_class` parameter and load the appropriate grid

**Estimated cost:**
- Code changes: 1-2 days
- Grid regeneration: 4 × 5-10 min = **20-40 min** (mostly wall-clock time)
- Testing: 1-2 days
- **Total: 4-5 days**

### 2. dSph (Channel 2) + UFD (Channel 3) — easier

**Current state:**
- `loglike_dsph_v03(sigma_m_0, a)` uses `sigma_m_at_v(sigma_m_0, a, V_DSPH)` directly
- `loglike_ufd_v03(sigma_m_0, a)` uses `sigma_m_at_v(sigma_m_0, a, V_UFD)` directly
- Single function call each — easy to parameterize

**What needs to change:**
1. Add `mediator_class` parameter (default "power_law")
2. Add lookup dictionary mapping class → σ/m(v) function
3. Modify the call site from `sigma_m_at_v(...)` to `MEDIATOR_FORMS[mediator_class](...)`

**Estimated cost:**
- Code changes: 0.5-1 day
- Testing: 0.5-1 day
- **Total: 1-2 days**

### 3. Extended channels (Ch4-Ch7, Ch9, Ch10) — moderate

**Current state:**
- `channels_extended.py` has 5 likelihoods (`loglike_dm_free_udg`, etc.)
- All use the inline form `log_sm_at_v = np.log10(sigma_m_0) + coefficient * a`
- This is the linearization of the power-law form at specific velocities

**What needs to change:**
1. Add `mediator_class` parameter to each function
2. Replace the inline `np.log10(sigma_m_0) + coefficient * a` with `np.log10(MEDIATOR_FORMS[mediator_class](sigma_m_0, a, V_RELEVANT))`

**Estimated cost:**
- Code changes: 1-2 days
- Testing: 0.5-1 day
- **Total: 1.5-3 days**

### 4. LZ + Fermi — does NOT need changes

**Current state:**
- LZ and Fermi depend on ε and α (kinetic mixing, dark photon parameters)
- They don't depend on the mediator class form (because the form is already dark-photon, with σ/m_0 derived from particle physics)
- For Phase 5, the ε and α are held fixed at the v0.3-prelim MAP

**What needs to change:** Nothing.

---

## Total estimated cost

| Component | Cost (days) |
|---|---|---|
| SPARC grid rebuild | 4-5 |
| dSph + UFD parameterization | 1-2 |
| Extended channels | 1.5-3 |
| Integration testing | 1-2 |
| Documentation + commit | 0.5-1 |
| **Total** | **8-13 days (~2-3 weeks)** |

**Honest estimate: 2-3 weeks**, NOT 1-2 weeks as the roadmap originally stated.

---

## Key risks and uncertainties

### Risk 1: SPARC grid takes longer than expected

The SPARC grid has 175 galaxies × 50 σ/m × 30 a = 262,500 evaluations. Each evaluation marginalizes over ρ_c using the Dutton-Maccio 2014 prior. The 5-10 min estimate assumes:
- Per-galaxy evaluation: ~1 ms (assumes scipy optimization converges fast)
- ρ_c marginalization: ~5-10x slowdown

If the marginalization is slower (e.g., 50ms per evaluation), the total wall time is 50 × 5 min = **4 hours per grid × 4 grids = 16 hours**. That's a full day of compute, not a single morning.

**Mitigation:** Run the 4 grids in parallel (4 cores), reducing total wall time to ~4 hours.

### Risk 2: SPARC likelihood is dominant

The SPARC channel dominates the joint log_Z (log_Z ~ -240,000 vs dSph ~ -1). If SPARC's power-law form is the source of the Phase 5 kill, then:
- Even with the rewrite, SPARC's per-galaxy likelihood might prefer the power-law form by a small amount
- This is actually the **expected behavior** — the kill criterion might still trigger, but now for physics reasons (SPARC prefers power-law) rather than structural reasons

**Mitigation:** Phase 5 result with the rewrite will give the **physics-grounded answer** instead of a structural limitation.

### Risk 3: Other channels (Ch4-Ch7, Ch9, Ch10) may have hidden power-law assumptions

The `coefficient * a` inlines in `channels_extended.py` are derived from specific velocity mappings. If a mediator class gives a σ/m(v) that doesn't fit a linear log-σ/m vs a at the relevant velocity, the inline calculation will silently break.

**Mitigation:** Add unit tests that compare `MEDIATOR_FORMS[mediator_class](sigma_m_0, a, v)` vs the inline `np.log10(sigma_m_0) + coefficient * a` at the relevant (v, coefficient) pairs.

---

## Recommended approach

**Two options:**

### Option A: Full rewrite (2-3 weeks)

1. Parameterize all channels to accept `mediator_class`
2. Rebuild SPARC grid 4 times (parallel)
3. Run Phase 5 with mediator-class discrimination
4. Get a **physics-grounded Bayes factor** between power-law, Yukawa, scalar, composite

**Pros:** Phase 5 actually discriminates mediator classes (per AGENTS.md rule 11)
**Cons:** 2-3 weeks; can't be combined with the publishable finding paper (Option B)

### Option B: Publishable finding paper FIRST (1-2 weeks), then rewrite

1. Draft the paper with the current finding (Phase 4 + Phase 5 result)
2. The paper claims: "Yukawa is over-strong; power-law fits best; mediator class is unconstrained"
3. After paper submission, do the rewrite as Phase 5b
4. Phase 5b results go into the paper revision if favorable, or as a follow-up paper

**Pros:** Get the publishable artifact now; the rewrite becomes the "improved Phase 5" for the paper revision
**Cons:** Two separate artifacts instead of one unified paper

---

## Strategic decision

**My recommendation: Option B** (paper first, rewrite as Phase 5b).

**Reasoning:**
1. The Phase 4 + Phase 5 finding is **publishable as-is** without the rewrite
2. The rewrite adds 2-3 weeks of engineering work that may not change the headline (power-law still fits best, probably)
3. If the rewrite DOES change the headline (e.g., Yukawa is now slightly favored), we get an even stronger paper
4. If the rewrite doesn't change the headline, we still have the paper, and the rewrite was wasted
5. **Sequencing: paper → rewrite → paper revision** is the standard scientific workflow

**Alternative:** If you want to do the rewrite first to get a definitive answer, that's Option A.

---

## What's left to ship Phase 5b (the rewrite)

If you choose Option A:

1. **Refactor `sigma_m_at_v`** to be one of several `MEDIATOR_FORMS[*]` functions
2. **Parameterize `loglike_dsph_v03` and `loglike_ufd_v03`** to accept `mediator_class` (1-2 days)
3. **Parameterize the 5 extended-channel likelihoods** in `channels_extended.py` (1.5-3 days)
4. **Modify `precompute_sparc_hierarchical.py`** to accept `mediator_class` and regenerate 4 grids (1-2 days code + ~4 hours wall time)
5. **Modify `loglike_sparc_hierarchical`** to load the correct grid based on `mediator_class` (0.5 day)
6. **Add integration tests** for all channels × 4 mediator classes (1-2 days)
7. **Run Phase 5 with the rewrite** (1 day)
8. **Update Phase 5 doc with the new finding** (0.5 day)
9. **Commit + push** (0.25 day)

**Total: 8-13 days (~2-3 weeks)**

---

## Next steps

**Question:** Do you want Option A (full rewrite, 2-3 weeks) or Option B (paper first, then rewrite)?

If Option B (recommended), I can ship:
- The publishable paper skeleton (Option 2 from earlier) with Phase 4 + Phase 5 findings
- The Phase 5b rewrite deferred to a follow-up commit

If Option A, I'll start with the SPARC grid rebuild (the most impactful single change).