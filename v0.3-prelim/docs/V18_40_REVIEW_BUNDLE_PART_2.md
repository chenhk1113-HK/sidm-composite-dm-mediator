# v18.40 Review Bundle — Part 2 of 4 (Investigation docs 1-3)

This part contains 3 investigation documents:
- File 2: T208 Path B Gravothermal Refuted (4.6 KB)
- File 3: T208/T209 Strategic Investigation Report (19.7 KB)
- File 4: T210 Cloud-9 Crater Gating Test (7.4 KB)

**Other parts:**
- Part 1: PAPER_V1_DRAFT.md (paper alone)
- Part 3: T211 + T212 docs
- Part 4: 6 code files (Python + Julia)

---

# File 2: T208 Path B Gravothermal Refuted

_Source path: `v0.3-prelim/docs/T208_PATH_B_GRAVOTHERMAL_REFUTED_2026-09-25.md`_

```
# T208 Path B — Gravothermal at Cloud-9 Host-Halo Mass Scale

**Date:** 2026-09-25
**Purpose:** Test whether gravothermal core-collapse at the Cloud-9 host-halo mass scale (M_200 = 5×10⁹ M_☉) can produce a σ/m(v=28 km/s) enhancement that satisfies the Cloud-9 floor (≥50 cm²/g) without violating the dSph ceiling (≤0.8 cm²/g at v=15 km/s).

**Method:** Balberg+ 2002 Eq. 22 (PRL 88, 101301) gravothermal t_core normalization, same as T204. Computes t_core(t_halo, c, σ/m, v_max) at Cloud-9 host-halo parameters and checks if t_core ≤ t_Hubble.

**Code:** `v0.3-prelim/code/T208_path_b_cloud9_host_halo_gravothermal.py` (110 lines, pure analytical).
**Result:** `v0.3-prelim/data/results/t208_path_b_cloud9_host_halo_gravothermal.json`.

## Results

### Cloud-9 host-halo parameters (cosmological NFW)
- M_halo = 5×10⁹ M_☉
- concentration c = 12
- r_vir ≈ 35.1 kpc (cosmological, 200 ρ_crit)
- r_s ≈ 2.92 kpc
- V_max ≈ 24.75 km/s
- ρ_s ≈ 9.69×10⁻³ M_☉/pc³

### σ/m at the Cloud-9 host-halo scale (Phase 44 baseline, a_slope = 1.0)
- σ/m(v=28, Cloud-9) = 0.186 cm²/g — **270× below the 50 cm²/g floor**
- σ/m(v=15, dSph) = 0.347 cm²/g — at the dSph ceiling

### Gravothermal at Cloud-9 host-halo (Phase 44 σ/m)
- **t_core = 73.7 Gyr** (using virial σ/m = 0.21 cm²/g)
- **t_Hubble = 13.8 Gyr**
- **t_core / t_Hubble = 5.3** — gravothermal phase DOES NOT run
- Causality OK: t_core / t_cross = 638 (well above 3.0 cap)

### σ/m required for gravothermal to run at Cloud-9 host halo
- σ/m ≥ **1.12 cm²/g** (virial) for t_core = Hubble
- Phase 44 needs **21.6× enhancement** to even start gravothermal

### Even if gravothermal ran: enhancement insufficient
- A 100× core-enhancement (typical for deep core-collapse) gives σ_eff(v=28) = 18.6 cm²/g
- Cloud-9 needs ≥ 50 cm²/g — **2.7× short even with deep core enhancement**

### σ/m violation of dSph at Yang+ 2025 high-σ regime
- At σ/m = 147 cm²/g (Yang+ 2025 high-σ): t_core = 105 Myr (runs fast)
- σ_eff(v=28) = 525 cm²/g (Cloud-9 PASSES — 10× above floor)
- σ_eff(v=15) = 980 cm²/g (dSph **VIOLATED by 1225×**)
- Cloud-9 vs dSph tension is STRUCTURAL, not gravothermal

## Verdict

**Path 2 (gravothermal unification) is REFUTED at Phase 44 σ/m.** The gravothermal phase does not run at the Cloud-9 host-halo mass scale (t_core = 73.7 Gyr ≫ t_Hubble = 13.8 Gyr). Furthermore, **no σ/m value resolves Cloud-9 vs dSph via gravothermal at this mass scale** — the tension is structural, not a missing gravothermal phase.

This **closes Path 2** as a route to unified-model status. The Cloud-9 spike (σ/m ≥ 50 cm²/g at v=28 km/s) and the dSph ceiling (≤ 0.8 cm²/g at v=15 km/s) cannot be reconciled by gravothermal enhancement at the host-halo mass scale.

## Implications for the paper

The Cloud-9 vs dSph tension remains **unresolved**. Per the Confirmed_v18 reviewer's note: this is the load-bearing structural issue. The paper's honest framing is preserved:
- Path F1 (T207, v18.38) fixes the SPARC structural limitation (heavy-channel-only σ_eff)
- Path 2 (T208, this report) refutes gravothermal as a Cloud-9 vs dSph resolution
- The Cloud-9 4000× spike is NOT derived from first principles
- The model remains a constraint map, not a unified derivation

## What does NOT change

- Standing paper verdict (6-7 of 8 channels, five no-go theorems) preserved
- Path F1 verdict split (borrowed RESOLVED, yang MARGINAL, t202 NOT RESOLVED, priored free fit CLEAR FAIL) preserved
- T204 substructure result at 10⁶ M☉ scale (Yu+ 2026 mechanism confirmed for SUBHALOS) preserved — gravothermal DOES run at subhalo scale, just not at host-halo scale
- §3.3b Yu+ 2026 PRL 136, 141001 stellar streams and stellar halo substructure preserved

## Next steps

Path 4 (first-principles f_H from KiSS-SIDM DSMC N-body) is still in progress per user directive "strategic budget, whatever it takes." Even though Path 2 is refuted, Path 4 produces a standalone first-principles anchor for f_H that removes the Yang+ 2025 Fig. 2 dependency. The result will be reported in v18.39 regardless of whether it unifies the model.

## Honest framing

This is a **negative result** — Path 2 (gravothermal unification) is refuted. Negative results are still publishable findings: the paper can state explicitly that gravothermal enhancement at the Cloud-9 host-halo mass scale is **insufficient to resolve the Cloud-9 vs dSph tension**, regardless of σ/m. This is stronger science than claiming a positive result that doesn't hold.
```

---

# File 3: T208/T209 Strategic Investigation Report

_Source path: `v0.3-prelim/docs/T208_T209_STRATEGIC_INVESTIGATION_REPORT_2026-09-25.md`_

```
# T208/T209 Strategic Investigation Report — Cloud-9 vs dSph Unification Routes

**Date:** 2026-09-25
**Branch:** `wip/cloud-9-relhic` @ `9e273f2` (v18.38 standing)
**Goal:** Push the SIDM composite-DM-mediator paper toward a **unified model** — a single framework that satisfies all 8 observational channels at once, derived from first principles.
**Scope:** This report covers Path 2 (gravothermal at Cloud-9 host-halo mass scale) and Path 4 (first-principles f_H from KiSS-SIDM N-body), plus the architectural discovery that gates Path 4.
**Reader:** K Lam — for review and direction.

---

## 1. Executive Summary

**Goal:** Test two routes toward unifying the Cloud-9 vs dSph tension at the host-halo mass scale.

**Result:**
- **Path 2 (gravothermal): REFUTED at all σ/m.** Cloud-9 vs dSph tension is STRUCTURAL, not a missing gravothermal phase. t_core at Cloud-9 host-halo (5×10⁹ M_☉) is 73.7 Gyr, 5.3× longer than Hubble. Even at Yang+ 2025 high-σ regime where gravothermal DOES run (t_core = 105 Myr), the dSph ceiling is violated by 1225×.
- **Path 4 (KiSS-SIDM N-body): BLOCKED by single-component architecture.** KiSS-SIDM v0.0.1 (Gurian/May 2025, PRL 135 221001, arXiv:2505.15903v2) handles ONE species only. Two-component N-body (heavy + light) requires either modifying KiSS-SIDM substantially (~2-5 days Julia work) or accepting a degraded single-component smoke test (~1-2 hour).

**Strategic implication for the unified-model ambition:** **The unified-model route via gravothermal at Cloud-9 host-halo is closed.** The Cloud-9 σ/m(v=28) ≥ 50 cm²/g spike and the dSph σ/m(v=15) ≤ 0.8 cm²/g ceiling cannot be reconciled by gravothermal enhancement at the host-halo mass scale, regardless of σ/m. This is a publishable negative result.

**Recommendation:** Ship v18.39 with Path B as a clean negative result, optionally with Option C (single-component KiSS-SIDM smoke test) for independent confirmation. Defer Option B (KiSS-SIDM modification) unless specific motivation emerges.

---

## 2. Background: what was tried and why

### 2.1 Standing paper verdict (v18.38 baseline)

The SIDM composite-DM-mediator paper currently stands at:
- 6-7 of 8 observational channels satisfied (Cloud-9, dSph, UFD, SPARC, Cluster, JVAS, GD-1, Fornax 6)
- Five UV-completion no-go theorems (magnetic dipole, Hidden U(1), GeV-scale inelastic, Chu+ p-wave, T184 dark Higgs)
- T206 retraction of v18.31 free-tied likelihood
- v18.32 T202 vs SPARC structural mismatch
- v18.34 structural wall: heavy-channel-only decomposition σ_eff = f_H² × σ_HH(v) **cannot match SPARC's σ/m ≈ 0.193 at v = 100 km/s** (max achievable σ_eff = 0.069)
- **v18.38 T207 Path F1: three-term σ_eff = f_H² σ_HH + 2 f_H f_L σ_HL + f_L² σ_LL decomposition** — fixed the SPARC structural wall
- Path F1 honest verdict per prescription:
  - borrowed: SPARC penalty −0.09 → **RESOLVED**
  - yang: SPARC penalty −0.24 → MARGINAL
  - t202: SPARC penalty −0.60 → NOT RESOLVED
  - priored free fit: SPARC penalty −2.03 (z ≈ 2.0) → **CLEAR FAIL**
- **Cloud-9 vs dSph tension: UNRESOLVED** since v18.32. Path F1 does not address it.

### 2.2 User goal statement (2026-09-25 Confirmed_v18 review session)

> "My goal is to push forward the project along the path that has the most robust and potential for enhancing plausibility for an unified model."

The user approved **Path 2 + Path 4 in parallel, strategic budget** (option "b"). The strategic budget is "whatever it takes" — but per AGENTS.md rule 11, we never fabricate results, and per rule 17, we ask before installing new toolchains or making non-trivial Julia modifications.

### 2.3 Why these routes specifically

The unified-model ambition requires:
1. **Cloud-9 σ/m ≥ 50 cm²/g at v = 28 km/s** satisfied
2. **dSph σ/m ≤ 0.8 cm²/g at v = 15 km/s** satisfied
3. **Both satisfied simultaneously with physically motivated f_H**

Two natural candidates for new physics that could achieve this:
- **Gravothermal core-collapse** (Balberg+ 2002 PRL 88, 101301): σ/m enhancement during the runaway collapse phase. Already invoked for subhalo scale (T204, Yu+ 2026 PRL 136, 141001 stellar halo substructure). Question: does it extend to host-halo scale?
- **First-principles f_H** from N-body: replaces Yang+ 2025 Fig. 2 (borrowed empirical input) with a self-derived profile. Removes one dependency, even if it doesn't unify directly.

---

## 3. Path 2 — Gravothermal at Cloud-9 host-halo mass scale

### 3.1 Method

**Code:** `v0.3-prelim/code/T208_path_b_cloud9_host_halo_gravothermal.py` (110 lines, pure analytical).
**Inputs:** Balberg+ 2002 Eq. 22 (PRL 88, 101301) gravothermal t_core normalization, same as T204. Cross-checked against T204's 10⁶ M☉ subhalo result.
**Output:** `v0.3-prelim/data/results/t208_path_b_cloud9_host_halo_gravothermal.json` and `v0.3-prelim/docs/T208_PATH_B_GRAVOTHERMAL_REFUTED_2026-09-25.md`.

### 3.2 Parameters

**Cloud-9 host-halo (cosmological NFW):**
- M_halo = 5×10⁹ M_☉
- concentration c = 12
- r_vir ≈ 35.1 kpc (200 ρ_crit convention)
- r_s ≈ 2.92 kpc
- V_max ≈ 24.75 km/s
- ρ_s ≈ 9.69×10⁻³ M_☉/pc³

**SIDM cross-section (Phase 44 baseline, a_slope = 1.0):**
- σ/m(v=28, Cloud-9) = 0.186 cm²/g
- σ/m(v=15, dSph) = 0.347 cm²/g

### 3.3 Result: gravothermal does NOT run at Cloud-9 host-halo

| Quantity | Value | Comparison |
|---|---|---|
| t_core at Phase 44 σ/m | **73.7 Gyr** | 5.3× longer than Hubble (13.8 Gyr) |
| t_core / t_cross | 638 | Well above 3.0 cap (causality OK) |
| σ/m required for t_core = Hubble | **1.12 cm²/g** | 21.6× above Phase 44 |
| σ_eff(v=28) with 100× core enhancement | 18.6 cm²/g | 2.7× below Cloud-9 floor |

**Even if the gravothermal phase DID run** (e.g., at artificially boosted σ/m = 1.12 cm²/g for t_core = Hubble), the enhancement would be insufficient to satisfy Cloud-9's 50 cm²/g floor.

### 3.4 Result: gravothermal DOES run at high σ/m, but breaks dSph

| Quantity | Value | Comparison |
|---|---|---|
| σ/m at Yang+ 2025 high-σ regime | 147 cm²/g | t_core = 105 Myr (runs fast) |
| σ_eff(v=28) after 100× core enhancement | 525 cm²/g | Cloud-9 PASSES (10× above floor) |
| σ_eff(v=15) after 100× core enhancement | 980 cm²/g | dSph **VIOLATED by 1225×** |

### 3.5 Verdict: STRUCTURAL

**No σ/m value resolves Cloud-9 vs dSph via gravothermal at the 5×10⁹ M_☉ host-halo mass scale.** The Cloud-9 vs dSph tension is a structural property of the velocity scales (v=28 vs v=15), not a missing gravothermal phase.

This is the **load-bearing negative result** of this session. The paper can state explicitly: "gravothermal enhancement at the Cloud-9 host-halo mass scale is insufficient to resolve the Cloud-9 vs dSph tension, regardless of σ/m."

### 3.6 What is preserved (not refuted)

- **T204 result at subhalo scale (10⁶ M_☉): gravothermal DOES run.** Yu+ 2026 PRL 136, 141001 stellar halo substructure (GD-1, JVAS, Fornax 6) is preserved. The negative result is specific to the host-halo mass scale (5×10⁹ M_☉), not a global statement about gravothermal.
- **T204 substructure channels (subhalos): independent of Cloud-9 host-halo physics.** Fornax 6 cluster, GD-1, JVAS streams remain validated as subhalo-scale phenomena.
- **Cloud-9 the dwarf galaxy** is hosted by a 5×10⁹ M_☉ halo (this is the standard interpretation). The negative result is about gravothermal at that specific halo mass.

---

## 4. Path 4 — First-principles f_H from KiSS-SIDM N-body

### 4.1 Original plan

**Goal:** Derive f_H(r) at the Cloud-9 host-halo mass scale from KiSS-SIDM DSMC N-body, replacing Yang+ 2025 Fig. 2 as the f_H input.

**Why this matters:** Even if it doesn't unify the model, removing the Yang+ Fig. 2 dependency would strengthen the paper as a self-contained phenomenological framework.

### 4.2 KiSS-SIDM install: 3 attempts, 1 success

**Attempt 1 (Julia 1.13, default):** `Pkg.instantiate()` failed — Manifest mismatch. Existing Manifest resolved for Julia 1.10.0 but PhysicalConstants/DifferentialEquations were added later.

**Attempt 2 (Julia 1.10.12):** `Pkg.resolve()` failed — DSMC v0.0.1 requires `Printf v1.11+` which is in the Julia 1.11 stdlib. Julia 1.10 has only `Printf v1.10.12`. Hard incompatibility.

**Attempt 3 (Julia 1.11.9):** `Pkg.resolve()` succeeded. `Pkg.instantiate()` succeeded — 348 transitive deps precompiled in 390 s (≈ 6.5 min wall). DSMC smoke test passed: `using DSMC` loads cleanly at `/home/lamkuenai/KiSS-SIDM/src/DSMC.jl`.

**Background jobs this round:**
- `proc_63aac43febeb` — Attempt 1 (Julia 1.13)
- `proc_ed44acc93e3c` — Attempt 3 (Julia 1.11.9, success)

### 4.3 Architectural discovery: KiSS-SIDM is single-component

After install succeeded, I checked the source for multi-species support:
- 1,828 lines of Julia source, grepped for `species`, `particle_type`, `component_idx`, `mass_per`, `tag` → **zero matches**
- 6 test directories, all single-species
- The arXiv paper (Gurian/May 2025 PRL 135 221001, arXiv:2505.15903v2) describes single-component DSMC only
- `n_phys_per_tracer` is a `QuantityM` (scalar), not a vector
- All collision algorithms (`collide_nb!`, `collide_nb_allow_repeat!`) operate on same-species pairs

**Confirmed:** KiSS-SIDM v0.0.1 is **definitively single-component**. The user's recollection of multi-component support was incorrect (after re-checking, user confirmed).

### 4.4 What single-component KiSS-SIDM can and cannot do

**CAN do:**
- Verify gravothermal collapse timescale at Cloud-9 host-halo scale (independent confirmation of Path B's analytical result)
- Show that KiSS-SIDM runs cleanly on this host (Julia 1.11.9, MKL backend, 348 deps working)
- Provide a gravothermal timescale cross-check using a different method than Balberg+ 2002

**CANNOT do:**
- Track heavy + light components separately
- Compute f_H(r) from first principles (only one species exists)
- Capture heavy-light (H-L) cross-section scattering (Path F1's σ_HL term)
- Model Yang+ 2026's two-component segregation physics

### 4.5 Three options for Path 4

#### Option A — Stop Path 4, ship v18.39 with Path B alone

**What it means:** Publish T208 as a clean negative result. Add a paper section saying "gravothermal cannot unify Cloud-9 vs dSph" and stop. Use Yang+ 2025 Fig. 2 as the f_H input (same as v18.37).

**Cost:** 1-2 hours wall (paper update + commit + push).

**Pros:**
- Honest publishable negative result
- No more compute, no Julia work
- Standing verdict preserved

**Cons:**
- Doesn't advance unified-model ambition
- Re-confirms v18.38 verdict rather than extending it

#### Option B — Modify KiSS-SIDM to support two species

**What it means:** Add a species tag to each particle (heavy vs light), modify collision algorithm to handle H-H, H-L, L-L scattering with different σ's, modify gravity for mass-weighted sums, modify snapshot output to record species labels. Substantial Julia coding.

**Cost:** 2-5 days focused Julia coding + testing.

**Pros:**
- Genuine two-component first-principles f_H derivation
- Removes Yang+ Fig. 2 dependency
- Real progress toward unified model

**Cons:**
- Substantial engineering investment
- **Likely outcome (per Path B):** even with two-component support, gravothermal doesn't run at Cloud-9 host-halo at Phase 44 σ/m, so f_H stays uniform (≈ 0.5). The marginal result is "Yang+ Fig. 2 is empirical, not derivable from gravothermal" — useful but not transformative.
- Per AGENTS.md rule 17, requires explicit user approval before committing to multi-day Julia work.

#### Option C — Single-component KiSS-SIDM smoke test at Cloud-9 host-halo scale

**What it means:** Run the KiSS-SIDM gravothermal collapse test case at M_halo = 5×10⁹ M_☉ (Cloud-9 scale). Independent confirmation that gravothermal does NOT run at this mass scale.

**Cost:** 1-2 hour KiSS-SIDM run.

**Pros:**
- Cheap independent confirmation of Path B
- Validates KiSS-SIDM runs cleanly on this host
- Useful background for any future multi-species extension

**Cons:**
- Single-component can't give f_H from first principles
- Result is "no, gravothermal doesn't run" — same verdict as Path B
- Doesn't advance unified model

---

## 5. Strategic assessment

### 5.1 What this session achieved for the paper

**Strong finding:** Path 2 is structurally refuted. The Cloud-9 vs dSph tension is not a missing gravothermal phase. This is a publishable negative result that strengthens the paper's epistemic honesty.

**Weak finding:** KiSS-SIDM is single-component, so Path 4 (two-component N-body) is blocked without substantial engineering investment.

### 5.2 What this session did NOT achieve

- **No advancement toward a unified model.** Both paths were long shots, but neither produced a positive result.
- **No first-principles f_H.** Yang+ 2025 Fig. 2 remains the empirical input.

### 5.3 What the unified-model ambition actually requires

Per Path B's negative result, **the unified-model route via gravothermal is closed.** The honest reality is that **the unified-model ambition requires new physics, not better measurements.** Candidate directions:

1. **Different microphysics** — not gravothermal, but some other enhancement mechanism at v=28 km/s
2. **Different astrophysics** — baryonic feedback modifies the inner halo (SIDM+baryons literature exists)
3. **Different observational interpretation** — Cloud-9 may not be a σ/m constraint at all (e.g., baryonic effect, supernova feedback, modified NFW profile)

None of these are on the current roadmap. Pursuing them would require either a substantial new literature survey or a deliberate broadening of the project scope.

### 5.4 My recommendation

**Option A (ship v18.39 with Path B alone):** Best paper-honesty return per unit time. ~1-2 hours wall.

**Option A + Option C (independent confirmation via KiSS-SIDM smoke test):** Best paper-honesty return per unit time, plus clean independent verification. ~2-3 hours wall.

**Option B (modify KiSS-SIDM):** Only worth doing if you specifically want to remove Yang+ Fig. 2 dependency. ~2-5 days Julia work, likely outcome is "first-principles f_H is uniform (≈ 0.5)" which doesn't unify the model but does strengthen the framework.

**None of the three options advances toward a unified model.** That requires either Option B's investment or a fundamentally different physics/astrophysics/observational direction.

---

## 6. Open questions for the next session

1. **Should we ship v18.39 with Path B as a clean negative result?** (Option A)
2. **Should we also run the KiSS-SIDM smoke test for independent confirmation?** (Option C)
3. **Is Option B (modify KiSS-SIDM) worth the 2-5 day investment?** (Strategic question — only you can answer)
4. **Is the unified-model ambition itself still the right goal?** Given Path B's negative result, is there a different physics route we should explore instead?

---

## 7. References

- **KiSS-SIDM paper:** Gurian & May 2025, "Core Collapse Beyond the Fluid Approximation: The Late Evolution of Self-Interacting Dark Matter Halos," PRL 135, 221001, arXiv:2505.15903v2.
- **Gravothermal theory:** Balberg, Shapiro & Inoue 2002, "Cold Dark Matter Halos with Self-Interaction: A Hamiltonian Approach," PRL 88, 101301.
- **Subhalo gravothermal:** Yang et al. 2025, "Two-component SIDM," PRD (Yang+ 2026 PRD reference cited in paper §3.2).
- **Substructure:** Yu et al. 2026, "Stellar streams and stellar halo substructure," PRL 136, 141001.
- **Path F1 paper integration:** v18.38 commit chain (`3b3d119` → `7e490f4` → `a3efc6a` → `58c9caf` → `39aafab`).
- **T208 Path B code:** `v0.3-prelim/code/T208_path_b_cloud9_host_halo_gravothermal.py`, results at `v0.3-prelim/data/results/t208_path_b_cloud9_host_halo_gravothermal.json`, writeup at `v0.3-prelim/docs/T208_PATH_B_GRAVOTHERMAL_REFUTED_2026-09-25.md`.
- **Background jobs this session:** `proc_63aac43febeb` (KiSS-SIDM install attempt 1, failed), `proc_ed44acc93e3c` (KiSS-SIDM install attempt 3, succeeded), `proc_3615b1263ae4` (Julia 1.11 install), `proc_255f8b03ce70` (KiSS-SIDM resolve+instantiate attempt 2, failed).

---

## 8. Honest framing

**Path B (gravothermal refutation) is the strongest finding.** It is a publishable negative result that the paper can cite in §10.4a to explicitly close off gravothermal as a Cloud-9 vs dSph resolution route. This is good science (we've shown what can't work, with two independent lines of evidence pending the KiSS-SIDM smoke test).

**Path 4 was always a long shot.** The multi-component block is unsurprising in hindsight — KiSS-SIDM is a single-species kinetic Boltzmann solver designed for the canonical gravothermal collapse case. Two-species support would be a substantial extension, not a configuration change.

**The unified-model ambition is the harder problem.** Both paths tried in this session failed to advance it. Path B established that gravothermal is structurally insufficient. Path 4 was blocked at the architectural level. A unified model requires either Option B's substantial engineering investment or a fundamentally different physics/astrophysics/observational direction.

**What the paper has achieved:** Standing v18.38 verdict (6-7 of 8 channels, five no-go theorems, Path F1 three-term σ_eff decomposition). v18.39 will add the gravothermal refutation as a clear epistemic boundary. The framework is honest, defensible, and structurally complete up to the Cloud-9 vs dSph tension, which is now demonstrably closed off via gravothermal — leaving the tension as an open astrophysical question rather than a missing gravothermal phase.

---

## 9. Suggested v18.39 paper outline

If Option A is approved:

**§9.12 (new) — Gravothermal at Cloud-9 host-halo scale: a structural refutation**

Add to paper after §9.11 (Path F1 verdict split):
- Compute t_core at M_halo = 5×10⁹ M_☉ using Balberg+ 2002 Eq. 22 normalization (same as §3.3b T204 substructure)
- Show t_core = 73.7 Gyr ≫ Hubble 13.8 Gyr
- Show σ/m required for t_core = Hubble = 1.12 cm²/g (21.6× above Phase 44)
- Show σ_eff(v=28) with 100× core enhancement = 18.6 cm²/g (still 2.7× below Cloud-9 floor)
- Show σ/m at Yang+ high-σ regime breaks dSph by 1225×
- **Verdict:** Cloud-9 vs dSph tension is structural, not a missing gravothermal phase.

**§10.4a (new) — Negative result: gravothermal does not unify Cloud-9 vs dSph**

Cross-reference §9.12. State explicitly: "gravothermal enhancement at the Cloud-9 host-halo mass scale is insufficient to resolve the Cloud-9 vs dSph tension, regardless of σ/m."

**§11 conclusions — update**

Add one paragraph summarizing §9.12 + §10.4a.

**CHANGELOG.md** — new `[T208-GravothermalRefuted-v18.39]` entry.

**CURRENT.md** — update standing version to v18.39, last refresh 2026-09-25.

**VERSION** — `+T208-GravothermalRefuted-v18.39` suffix.

**README.md** — update front-page badge, WIP-branch table.

If Option A + C is approved: add §9.13 with KiSS-SIDM single-component smoke-test result for independent confirmation.

If Option B is approved: defer v18.39 to ~2026-09-30 (after 2-5 days KiSS-SIDM modification).

---

## 10. Decision needed

Per AGENTS.md rule 5 ("Get explicit approval before ANY state-changing action with side effects on … external writes (git push), service/daemon state"), please confirm:

- **(a)** Ship v18.39 with Option A only — Path B as standalone finding. ~1-2 hours.
- **(b)** Ship v18.39 with Option A + Option C — Path B + KiSS-SIDM smoke test for independent confirmation. ~2-3 hours.
- **(c)** Defer v18.39, invest in Option B — modify KiSS-SIDM for two-component support. ~2-5 days.
- **(d)** Other — your direction.
```

---

# File 4: T210 Cloud-9 Crater Gating Test

_Source path: `v0.3-prelim/docs/T210_CLOUD9_CRATER_GATING_TEST_2026-09-25.md`_

```
# T210 Gating Test + Path A2 Sharp Resonance Scan — Cloud-9 / Crater II / Antlia II

**Date:** 2026-09-25
**Trigger:** Cloud-9alternate.docx memo proposing Crater II + Antlia II as kinematic (more robust) alternatives to Cloud-9's hydrostatic inference, and a sharp-resonance scan as Path A2.
**Code:** `v0.3-prelim/code/t210_gating_test_crater_antlia.py` + `t210_path_a2_sharp_resonance_scan.py` + `t210_quick_sigma_eff_decompose.py`
**Results:** `v0.3-prelim/data/results/t210_gating_test_crater_antlia.json` + `t210_path_a2_sharp_resonance_scan.json` + `t210_path_a2_summary.json`

## 1. Gating Test Outcome — B (model fails Crater II + Antlia II)

The current Path F1 three-term σ_eff decomposition, evaluated under the borrowed prescription (f_H_cf = 0.85, f_H_cc = 0.5, σ_peak_HH_1 = 84.4, σ_peak_HL = 0.318, v_HL = 98.2, σ_0_LL = 0.0006), fails Crater II and Antlia II across all V_max interpretations:

| Scenario | Crater II σ_eff | z vs 30 cm²/g | Antlia II σ_eff | z vs 30 cm²/g |
|---|---|---|---|---|
| A: V_max = σ_los | 0.253 | 2.97 (FAIL) | 0.228 | 2.98 (FAIL) |
| B: V_max = √3·σ_los | 0.231 | 2.98 (FAIL) | 0.252 | 2.97 (FAIL) |
| C: V_max ≈ 15 km/s | 0.345 | 2.97 (FAIL) | 0.345 | 2.97 (FAIL) |
| D: V_max ≈ 28 km/s | 10.716 | 1.93 (FAIL) | 10.716 | 1.93 (FAIL) |

**The memo's critical caveat is resolved:** σ_eff in the current model peaks at 10.7 cm²/g around v=28 and drops to 0.23 cm²/g at v=5. Neither Crater II's nor Antlia II's kinematic constraint (σ/m ≥ 30-60 cm²/g) is satisfied at any V_max.

**Cloud-9 reference (memo comparison):** σ_eff(28) = 10.7 cm²/g vs floor 128 cm²/g → z = 3.91 (FAIL). This is the Cloud-9 vs dSph tension restated.

**dSph reference (memo comparison):** σ_eff(15) = 0.345 cm²/g vs ceiling 0.8 cm²/g → z = -11.37 (PASS). dSph is satisfied.

## 2. Path A2 — Sharp Resonance Scan

Tested whether moving v_HL (the heavy-light Lorentzian peak position) down to v=25-35 km/s and shrinking width_HL to 5-50 km/s could satisfy Cloud-9 + dSph simultaneously.

**Result: ZERO configurations pass both Cloud-9 AND dSph** across the 7 × 6 = 42 grid (v_HL ∈ {25, 28, 30, 35, 50, 75, 100}, width_HL ∈ {5, 10, 15, 20, 30, 50}).

The best configurations cluster at:
- σ_eff(28) ≈ 31 cm²/g (vs 128 floor, z = 3.23)
- σ_eff(15) PASS (dSph)
- σ_eff(100) ≈ 0.02 cm²/g (vs SPARC 0.193 target, z = -3.45 → SPARC FAILS)

**Trade-off is fundamental:** moving v_HL down to 28 satisfies Cloud-9's neighborhood (at the expense of never reaching the floor), but BREAKS SPARC because the heavy-light term no longer contributes at v=100.

## 3. Decomposition — what's in σ_eff(28)

Diagnostic run `t210_quick_sigma_eff_decompose.py` shows that σ_eff(28) is dominated by **f_H² × σ_HH_1(v=28) ≈ 0.5² × 84.4 ≈ 21.1 cm²/g**, plus the σ_HL cross-term (small, ~1 cm²/g).

To reach σ_eff = 128 at v=28, σ_peak_HL would need to be ~500 cm²/g — **physically implausible** (and would break the dSph ceiling at v=15).

**This is the structural ceiling:** the framework's σ_HH_1 Lorentzian peak of 84.4 is the dominant contributor at v=28, and even it can only push σ_eff to ~31. The 4× gap (31 vs 128) is unreachable without new physics.

## 4. Implications for the paper

### What the paper needs to acknowledge

**The multi-probe reframing the memo proposed does not work under the current framework.** Crater II and Antlia II, when evaluated against Path F1, fail the same way Cloud-9 does. Adding them as additional channels only multiplies the failure mode.

### What the paper CAN say (honest framing)

1. **Cloud-9 vs dSph tension is structural under Path F1.** σ_eff(28) cannot reach 128 cm²/g because the framework's σ_HH_1 Lorentzian peak (84.4 cm²/g) caps the heavy-heavy contribution at f_H² × 84 ≈ 21 cm²/g, and σ_peak_HL cannot bridge the gap without exceeding physical bounds.

2. **Crater II and Antlia II confirm the tension, not relax it.** At any V_max interpretation, σ_eff under borrowed mode reaches at most 10.7 cm²/g at v=28, which is 3× below Crater II's 30 cm²/g floor (z = 1.93-2.97 across scenarios).

3. **The 4 UV-completion no-go theorems + Path F1's σ_eff ceiling form a complete constraint map.** The framework describes 6-7 of 8 channels under borrowed prescription, fails Cloud-9 / Crater II / Antlia II / free fit at SPARC, and cannot unify the high-σ/m probes (Cloud-9 + Crater II + Antlia II + LSB) with the low-σ/m probes (dSph + UFD + SPARC + Cluster).

### What the paper CANNOT say

- "Multi-probe reframing strengthens the framework." It doesn't — it adds more failures.
- "Sharp resonance at v=28 unifies the model." It doesn't — Cloud-9 floor is unreachable.
- "Crater II is more accommodating than Cloud-9." It isn't, under Path F1. Both fail by similar factors.

## 5. Honest assessment

This session confirmed what Path 2 (gravothermal refutation) and Path 4 (KiSS-SIDM single-component) suggested: **the current framework cannot unify the high-σ/m and low-σ/m probes.** Three independent tests (gravothermal enhancement, sharp-resonance scan, multi-probe gating) all converge on the same structural ceiling.

The remaining options are:
- **Option A (paper-level):** Document the constraint map honestly. Add §10.4b (this finding) alongside §10.4a (gravothermal refutation). v18.40 standing = "framework describes 6-7 of 8 channels, but Cloud-9 vs dSph tension is structural across all multi-probe variations tested."
- **Option B (physics-level):** New physics required. The memo's Path B3 candidates (velocity-dependent cross-section with non-monotonic structure, separate environments, baryonic coupling) are the only routes forward. Each requires its own literature survey and validation campaign.
- **Option C (presentation-level):** Re-cast Crater II and Antlia II as upper limits rather than floor constraints. If the SIDM inference for these systems carries systematic uncertainties (tidal stripping, environment), the paper can argue the 60 cm²/g requirement is itself uncertain. This is Path B2 from the memo.

## 6. Files added this round

- `v0.3-prelim/code/t210_gating_test_crater_antlia.py` — Crater II + Antlia II gating test
- `v0.3-prelim/code/t210_path_a2_sharp_resonance_scan.py` — (v_HL, width_HL) grid scan
- `v0.3-prelim/code/t210_quick_sigma_eff_decompose.py` — σ_eff(28) decomposition diagnostic
- `v0.3-prelim/data/results/t210_gating_test_crater_antlia.json` — gating test results
- `v0.3-prelim/data/results/t210_path_a2_sharp_resonance_scan.json` — full scan results
- `v0.3-prelim/data/results/t210_path_a2_summary.json` — summary + best configs
- `v0.3-prelim/docs/T210_CLOUD9_CRATER_GATING_TEST_2026-09-25.md` — this writeup

## 7. Decision needed

The memo's Day 1-2 work is complete. Day 3 (sharp resonance scan) is also complete and confirms the framework cannot unify the probes. Per the memo's Day 4 recommendation:

> "Based on the resonance scan, decide between (a) presenting the resonance as a candidate unification route, or (b) accepting that the framework is a constraint map, not a unified model."

**Recommendation: option (b).** The framework is a constraint map. v18.40 should add §10.4b (this finding) and explicitly mark the unified-model ambition as closed under the current framework. Any future unification requires new physics (Option B) or new observational interpretation (Option C).

Awaiting direction.
```

---

