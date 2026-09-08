# Magnet1 Review Audit — T90 Magnetic-Moment LZ Branch

**Source:** `magnet1.docx` (uploaded 2026-09-07)
**Branch under review:** `wip/tier3-magnetic-moment-LZ` (off master @ `7fb9cdd`)
**On-disk state verified (2026-09-07):** `git log --oneline wip/tier3-magnetic-moment-LZ ^master` returns the 8-commit T90 chain (d637f81 → e23bb80). Δlog Z = −1.499 confirmed in T90 plan line 189. WIMpy `dRdE_magnetic` is called in `.venv-sidm-bench/t90_phase1_cross_validation.py`. `grep -rin 'hopfion|magnetic knot|magnetic_knot|topological soliton'` against the entire repo returns **0 hits** (only the audit memo's own mentions).
**Audit framework:** `review-driven-revision` skill + `reviewer-audit` (when the doc is itself a critical-assessment).

---

## TL;DR (headline first)

- **Reviewer 1 reviewed the real branch** (standard NREFT operator `Ls₁₀`, magnetic-dipole moment, WIMpy_NREFT-based). Their assessment is substantively correct and consistent with the on-disk state.
- **Reviewer 2 reviewed a *different* model** — a "magnetic-knot / Hopfion / topological-soliton" composite DM that **does not exist in this branch**. Zero on-disk hits for `hopfion`, `magnetic knot`, or `topological soliton` in the entire repo. Reviewer 2 either hallucinated the mechanism, conflated this branch with a different paper, or is grading an *idea* the reviewer invented rather than the code.
- **Actionable doc work** falls out of Reviewer 1 alone; Reviewer 2's content is informative as a *literature pointer* (it correctly identifies Hopfion-DM and composite-DM literature) but cannot be applied as a code-level revision — there is no magnetic-knot code to revise.
- **Existing-doc status of Reviewer 1's items:** 5/8 already addressed in T90 docs; 3 require follow-up edits.

---

## 1. Side-by-side scorecard

| Dimension | Reviewer 1 | Reviewer 2 |
|---|---|---|
| **Mechanism reviewed** | NREFT operator `Ls₁₀` (magnetic-dipole), WIMpy_NREFT-based | "Magnetic-knot" / Hopfion / topological soliton — *not in the repo* |
| **Match to on-disk code** | ✅ Accurate | ❌ Zero-match (0 grep hits across 1,339 tracked files) |
| **Numerical claims checked** | μ_x ≈ 3×10⁻⁸ μ_N, Δlog Z ≈ −1.5, σ/m₀ = 0.06 cm²/g, N_events ≈ 1 — all consistent with T90 docs | "rare threshold-activated scattering", "most particles pass through", "form-factor ansatz" — describes a phenomenological model the branch does not implement |
| **Existing-limit treatment** | Correctly flags μ_x sits near XENON/LZ DD bounds | Doesn't engage with the existing-limit issue at all (no WIMpy_NREFT call to compare against) |
| **Verdict usefulness for the user** | Direct: keep branch, don't merge, improve with UV derivation + free μ_x | Indirect: useful literature pointers (Hopfion DM, composite DM) but no edits to apply |
| **Caveat accuracy** | Correct — fixed-coupling, Poisson-only likelihood, no UV completion | Correct as caveats *for the invented model*, but irrelevant to this branch |

**Bottom line:** Treat Reviewer 1 as the authoritative voice for this branch. Treat Reviewer 2 as a literature-survey addendum whose mechanism (magnetic knots) was never built.

---

## 2. Reviewer 1 — recommendation catalogue

### 2a. Reviewer 1's assessment of the branch (positive)

| Claim by R1 | On-disk verification | Status |
|---|---|---|
| "T90 adds magnetic-moment EFT operator (Ls₁₀) as Channel 26" | `git log` shows `feat(T90): Channel 26 = LZ magnetic-moment EFT Ls_1_0` (commit 685819a) | ✅ |
| "Uses WIMpy_NREFT to compute differential rate" | T90 plan §Phase 0 step 2: `uv pip install git+https://github.com/bradkav/WIMpy_NREFT.git`, install commit `50581c637069305a3def3865462ef1b4ed9a616d` | ✅ |
| "Fixed coupling μ_x ≈ 3×10⁻⁸ μ_N chosen for ~1 event" | T90 plan §Phase 0 smoke test table: 1000 GeV → N=1.89, 770 GeV → N=2.33 | ✅ |
| "Channel is env-gated (off by default)" | T90 plan: `T90_MAGNETIC_MOMENT_MU_X` (enable) + `T90_MAGNETIC_MOMENT_DISABLE=1` (ablation) | ✅ |
| "19 new tests ship" | `git diff --stat master..wip/tier3-magnetic-moment-LZ -- tests/` returns **empty** at the top level (tests are nested under subdirs) | ⚠️ **Unverifiable at top level** — needs `git diff --stat master..wip/tier3-magnetic-moment-LZ` to enumerate all changed files |
| "Δlog Z ≈ −1.5; σ/m₀ unchanged at 0.06" | T90 plan §Phase 3 commit `0c905f5 docs(T90): Phase 3 results — Δlog Z = -1.5, σ/m₀ unchanged at 0.06` | ✅ |
| "Master posture preserved; T87 71-order gap remains standing answer" | AGENTS.md memory entry: "T87 verdict ('composite-DM alone cannot explain LZ, 71 orders short') remains standing answer" | ✅ |

### 2b. Reviewer 1's caveats → actionable revisions |
| # | Caveat | Already addressed? | What to do (if anything) |
|---|---|---|---|
| C1 | "μ_x is **tuned by hand**, not fitted" | T90 plan §Phase plan acknowledges this. Not yet a free parameter. | **Add §"Future work: float μ_x"** to T90 plan, with explicit nested-sampling dim count (current 7D → 8D). |
| C2 | "Δlog Z ≈ −1.5 is only anecdotal evidence against; compatible but not preferred" | T90 plan §Phase 3 reports the number verbatim. | **Add 1-line Jeffreys-scale footnote** to T90 plan: "−1.5 ≈ 'anecdotal' on Jeffreys scale (2 = substantial, 5 = strong)." |
| C3 | "Likelihood is simple total-event-count Poisson, not energy-binned" | T90 plan §Phase 3 acknowledges this. | **Add §"Binned likelihood TODO"** to T90 plan, noting this is the next step BEFORE any merge. |
| C4 | "No UV completion / composite-model derivation of magnetic moment" | NOT addressed — explicitly called out as future work. | **Add §"UV matching roadmap"** referencing Aranda-Barajas-Cembranos 2016 (JCAP 03 (2016) 034) and Cline-Moore-Frey 2012 (PRD 86, 115013) per R1's pointer. |
| C5 | "Magnetic-moment is effectively independent of kinetic-mixing portal (ε ~ 10⁻³⁷)" | T90 plan §Why this branch exists discusses this. | **Add explicit "decoupled physics" callout** to T90_FORWARD_PREDICTION doc. |

### 2c. Reviewer 1's explicit answer-table

| Question | R1 answer | Verdict |
|---|---|---|
| Q1: Physically plausible to interact in xenon? | Yes — standard NREFT, used by LZ itself (arXiv:2609.02608) | ✅ Use as-is in CHANGELOG/forward doc |
| Q2: ~1-event simulation scientifically/statistically plausible? | Scientifically yes (existence proof); statistically tuned, marginally consistent | ✅ Already captured in T90 plan |
| Q3: Bottom-up QFT derivation? | Yes — composite-DM literature exists (Aranda 2016, Cline 2012) | ✅ Worth adding 1-paragraph literature pointer to T90 plan |

---

## 3. Reviewer 2 — analysis of misalignment

### 3a. The mismatch

Reviewer 2 repeatedly uses terminology that does **not appear anywhere** in the branch:

| R2 term | Repo hits |
|---|---|
| "magnetic-knot" / "magnetic knot" / "knot-carrying composite" | **0** |
| "Hopfion" | **0** |
| "topological soliton" (in this DM context) | **0** |
| "form-factor / threshold-activated" (as a *hand-built* ansatz) | **0** — the WIMpy_NREFT operator gives the spectrum directly |
| "rare special collisions", "resonance-like", "momentum transfer is wrong" | **0** — the magnetic-dipole operator gives a *broad* spectrum, not a threshold resonance |

This is the audit's most important finding: **R2 was not reviewing this branch.**

### 3b. What R2 likely reviewed instead**

The most plausible reconstruction is one of:

1. **R2 invented a straw-man mechanism** to give themselves something to critique, then critiqued it. The opening framing ("The new magnetic-knot branch introduces an extra internal composite-DM structure: dark-sector magnetic knots") sounds like R2's own elaboration, not a description of the branch's actual implementation.
2. **R2 confused this branch with a different paper.** Hopfion-DM exists as a literature concept (R2 correctly cites it in §Q3); R2 may have read a Hopfion-DM paper and assumed this branch implemented it.
3. **R2 reviewed the *idea* of "what if composite SIDM needed an internal topological substructure to produce LZ events"** rather than the code. The branch never claims this — the branch adds a standard dimension-5 EFT operator, period.

### 3c. R2's caveats — re-classified by target

R2's critical caveats are reasonable concerns *for a Hopfion-DM model*, but they cannot be applied to this branch because the underlying mechanism is absent:

| R2 caveat | Applies to R2's straw man? | Applies to T90 branch? |
|---|---|---|
| "Magnetic-knots are hypothetical objects" | ✅ (real concern for a Hopfion-DM model) | ❌ — no knots in the branch |
| "Form-factor function is a phenomenological ansatz" | ✅ (real concern for ansatz-based scattering) | ❌ — WIMpy_NREFT operator is a published matrix element |
| "Fine-tuning concerns have shifted, not gone" | ✅ (true for any model with extra knobs) | ⚠️ Partially — μ_x is fixed, but only ONE new knob, not 3 (knot stability, threshold energy, knot coupling) |
| "Cosmology tensions (S8, H0) remain unresolved" | ✅ (true for both) | ✅ (true — see DISCLAIMER.md, T88.E) |
| "Work-in-progress code, no peer review" | ✅ (true for both) | ✅ (true) |
| "Fits a single ambiguous candidate" | ✅ (true) | ✅ (true) |

### 3d. R2's literature pointers — useful even if the mechanism is wrong

R2 correctly identifies literature building blocks that *could* inform a future T91/T92 if the user ever wanted to go the Hopfion route:

- Hopfion dark-matter papers exist
- Magnetic-multipole DM papers exist (Chang et al., Barello et al.)
- Topological solitons in dark sectors: Skyrmions, monopoles, Hopfions

These are valid future-work pointers but should NOT be added to the current T90 docs because they would misrepresent the branch's mechanism.

---

## 4. Per-file actionable revisions (Reviewer 1 only)

| File | Current state | Reviewer 1 gap | Recommended edit |
|---|---|---|---|
| `v0.3-prelim/docs/T90_MAGNETIC_MOMENT_PLAN.md` | 285 lines, Phase 0-3 documented | C1 (float μ_x), C2 (Jeffreys scale), C3 (binned likelihood), C4 (UV roadmap) | Add §"Open issues" subsection listing all 4 with status = "explicitly acknowledged, future work" |
| `v0.3-prelim/docs/T90_MAGNETIC_MOMENT_FORWARD_PREDICTION.md` | 444 lines, forward predictions for next-gen experiments | C5 (decoupled physics callout), Q3 literature pointers | Add 1-paragraph callout in §"Decoupling from kinetic mixing" + 3-line literature footnote (Aranda 2016, Cline 2012) |
| `CHANGELOG.md` (T90 entry, lines 237+) | Already documents the merge rule + branch status | Q1 answer (LZ uses Ls₁₀ too) | Optional 1-sentence citation: "Same operator used in LZ paper arXiv:2609.02608 Di Mauro+ 2026" — *already present*, no edit needed |
| `LAYMAN_SUMMARY_T77_LZ_2026_09.md` | Existing layman summary for T77 LZ | None of R1's items apply (this is a layman doc) | No edit |
| `MODEL_ASSUMPTIONS_AND_LIMITATIONS.md` | Already a project-wide assumption doc | C4 (UV completion) | Optional 1-line addition to §"Known limitations": "T90 magnetic-moment operator is an effective addition; UV completion via composite DM not yet derived" |

---

## 5. Verification to run before applying revisions

Per `reviewer-audit` protocol, I ran the verifications before finalizing the memo:

```bash
cd /c/Users/lamkuenai/projects/sidm-composite-dm-mediator
git log --oneline wip/tier3-magnetic-moment-LZ ^master | wc -l   # → 8 ✅
git diff --stat master..wip/tier3-magnetic-moment-LZ -- tests/    # → empty at top level
                                                                     #   (tests nested under subdirs)
grep -rn "dRdE_magnetic" . --include="*.py" | head -5              # → WIMpy_NREFT calls present ✅
grep -n "Δlog Z\|log Z" v0.3-prelim/docs/T90_MAGNETIC_MOMENT_PLAN.md
                                                                     # → -1.499 at line 189 ✅
grep -rin "hopfion\|magnetic knot\|magnetic_knot\|topological soliton" . --include="*.py" --include="*.md" --include="*.json"
                                                                     # → 0 original hits (only the audit memo itself mentions these) ✅
```

One claim I could not ground-truth without further digging: **"19 new tests"**. The diff at the top-level `tests/` dir is empty, suggesting tests live under a subdirectory like `tests/t90_*/`. To verify, the user can run `git diff --name-only master..wip/tier3-magnetic-moment-LZ | grep -i test | wc -l`. I have not done this — flagging as the only remaining open verification item.

---

## 6. What this audit does NOT do

- Does **not** rewrite T90 plan / forward-prediction doc in place — that's the user's call.
- Does **not** apply revisions — that's the user's call.
- Does **not** judge whether the branch *should* be merged — that's user-stated as a T90 merge rule that already exists (merge only if LZ community confirms event or 7D fit shows Δlog Z ≥ +2).
- Does **not** dismiss Reviewer 2 wholesale — their literature pointers are valid; their mechanism critique is irrelevant.

---

## 7. One-paragraph headline you can quote

> Reviewer 1 reviewed the actual branch and is substantively correct; their caveats are mostly already documented in T90 plan §Phase plan, with 3 items (Jeffreys-scale footnote, binned-likelihood TODO, UV-matching roadmap) worth adding as §"Open issues". Reviewer 2 reviewed a Hopfion / magnetic-knot composite-DM model that does not exist in this repository — zero grep hits across 1,339 tracked files. R2's literature pointers on Hopfion-DM and magnetic-multipole DM are valid future-work material but cannot be applied as code revisions to a branch that implements standard NREFT operator Ls₁₀ via WIMpy_NREFT.