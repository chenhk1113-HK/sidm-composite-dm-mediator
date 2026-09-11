# T90.59 Branch-Line Context (cross-reference for README/T90/MATHEMATICS doc drift)

**Date:** 2026-09-11
**Purpose:** Resolve the "doc drift" surfaced by external reviewers of the T90.59 release — the README at repo root, CURRENT.md, MATHEMATICS.md, and the T90_PATH_C4_* docs describe different parameterizations. This document explains why and cross-references them.

---

## The three evolution lines in the repo

| Line | Branch | Headline claim | Parameterization | DM observables | Direct-detection observables |
|---|---|---|---|---|---|
| **v0.4-prelim+T88E** (standing) | `main` (or whatever holds T41 v0.8) | T41 joint fit, log Z = −164.87, m_χ=770 GeV, σ/m₀=0.06 cm²/g, MAP a=0.13 | Single Yukawa mediator (m_φ ~ 453 MeV), velocity-dependent σ_DM-DM | σ_DM-DM (g_χ, m_φ, α_Y) | σ_DM-nucleon via Kahlhoefer formula, ε ~ 10⁻³⁷ sampled |
| **T90 Cloud-9** (wip branch) | `wip/cloud-9-relhic` | T90.59 hybrid, m_χ=485 GeV, two-portal+resonance | Two-portal (m_φ_A ~ 1.4 GeV, m_φ_B ~ 4 MeV) + Breit-Wigner resonance (E_R ~ 700 eV) + Sommerfeld | σ/m(v) at 3 velocities (28, 100, 3000 km/s) | μ_χ (magnetic moment) ~ 4.3×10⁻⁸ μ_N sampled, ε pinned at log_ε = -50 |
| **Earlier T41 versions** | historical branches | Various v0.6, v0.7 numbers | Various | Various | Various |

---

## What each doc describes (and why they disagree)

### `README.md` (repo root)

- **Documents:** Standing v0.4-prelim+T88E line. Last refresh: T88.E (2026-09-02).
- **Headline numbers:** log Z = −164.87, MAP m_χ = 770 GeV, σ/m₀ = 0.06 cm²/g, MAP a = 0.13
- **Channels:** 22 (DAMPE + Zhang+ 2025 LSS + XENONnT/PandaX watch + XRISM Perseus + eROSITA + Euclid Q1 lensing + subhalo FORECAST + ΔN_eff, etc.)
- **Direct detection:** σ_DM-nuc ~10⁻¹¹¹ cm² at v0.7 MAP (Kahlhoefer point-particle formula); ε ~ 10⁻³⁷ fine-tuning flagged in T79

### `CURRENT.md` (repo root)

- **Documents:** 1-page version-of-record for standing v0.4-prelim+T88E
- **Same content as README** (just condensed)

### `MATHEMATICS.md` (in some folder)

- **Documents:** Math appendix for the standing v0.4-prelim+T88E line
- **Parameterization:** σ_DM-DM ∝ g_χ⁴ / m_φ⁴ × v^(-2a) (power-law velocity dependence)
- **This is the v0.7/v0.8 form, NOT the T90 hybrid**

### `T90_PATH_C4_*` docs (in `v0.3-prelim/docs/`)

- **Documents:** T90 Cloud-9 branch evolution (T90.27 → T90.59) on `wip/cloud-9-relhic`
- **Headline numbers:** log Z = -7.91 (T90.57), m_χ = 485 GeV, σ/m(28) = 94.9 cm²/g, σ/m(100) = 2.50 cm²/g, σ/m(3000) = 0.050 cm²/g, μ_χ = 4.3×10⁻⁸ μ_N
- **Parameterization:** Hybrid σ/m(v) = σ/m_portal_A(v) + σ/m_portal_B(v) + σ/m_resonant(v); two-portal + Breit-Wigner resonance
- **Direct detection:** μ_χ (magnetic moment) sampled; ε pinned at log_ε = -50

---

## Why the three descriptions disagree (and why this is intentional, not a T82 audit failure)

The T82 drift audit checks whether **doc claims match code claims within a single line**. The T82 audit does NOT check whether **different lines describe the same model** because they're allowed to be different lines.

The three docs describe **three different models on three different branches**:

1. **v0.8 (README/CURRENT):** T41 single-mediator Yukawa, velocity-dependent σ_DM-DM, Kahlhoefer σ_DM-nucleon
2. **v0.7 → v0.8 (MATHEMATICS):** Same v0.8 model, power-law velocity form
3. **T90.59 (T90_PATH_C4_*):** Hybrid two-portal+resonance, σ/m(v) at 3 velocities, magnetic-moment direct detection

Each line has its own:
- **Parameterization** (different priors, different nuisance structure)
- **Observables** (v0.8 measures σ_DM-DM; T90 measures σ/m at 3 velocities; v0.8 has σ_DM-nuc, T90 has μ_χ)
- **Direct-detection channel** (v0.8 uses ε; T90 uses μ_χ; the two are NOT equivalent — ε is a kinetic mixing, μ_χ is an anomalous magnetic moment)
- **Code paths** (v0.8 lives in `v0.3-prelim/code/t41_*`; T90 lives in `v0.3-prelim/code/t90_v*`)

**Honest re-read:** the T90 work is **exploratory** on a wip branch. It is **not** the standing version. The standing version is still v0.8 (per README and CURRENT.md). The T90.59 release is a **separate evolution experiment** that explores whether a different parameterization (hybrid two-portal+resonance, magnetic-moment DD) can also satisfy the σ/m constraints — and finds that yes, it can, with similar Bayesian evidence penalties as v0.8.

---

## What the external reviewers got right

Both reviewers (2026-09-11) flagged the doc drift as a major issue. **They are correct that the apparent disagreement creates confusion.** Their suggestions:

1. **Reconcile the 10⁻¹¹¹ vs 10⁻⁹⁶ σ_DM-nuc discrepancy against an independent Kahlhoefer-variant derivation** — applies to v0.8, NOT T90 (T90 doesn't compute σ_DM-nuc)
2. **State the relic-abundance production mechanism explicitly** — applies to v0.8 (T90 uses the v0.8 calibration)
3. **Re-frame the LZ channel: report the fine-tuning/naturalness cost separately from the Δlog Z** — applies to BOTH lines (v0.8 has ε ~ 10⁻³⁷; T90 has μ_χ ~ 4.3×10⁻⁸ μ_N pinned for unobservability)
4. **Replace Gaussian placeholder channels with raw posterior chains before any publication claim** — applies to both lines
6. **Quantify fine-tuning** — applies to both lines
5. **Resolve the README / T90 / MATHEMATICS model descriptions so the three agree on which model and which numbers are canonical** — this doc is the start of that resolution

## What the external reviewers got wrong

Both reviewers cite ε ~ 10⁻³⁷ as a T90 fine-tuning problem. **This is misattributed.** ε ~ 10⁻³⁷ is a v0.8 / T41 / T87 issue. In the T90 hybrid, ε is **pinned at log_ε = -50** (`t90_v57_hybrid_ksfr.py:16`) and the LZ constraint operates through μ_χ instead.

The T90 fine-tuning cost is on **μ_χ** (magnetic moment), not ε. μ_χ ~ 4.3×10⁻⁸ μ_N is fine-tuned to evade the LZ magnetic-moment bound (μ_χ ≲ 10⁻⁶ μ_N). This is still a fine-tuning cost — the model's μ_χ is engineered to be unobservable — but it's a different physical coupling than ε.

---

## Action items (post-review)

| Priority | Action | Status |
|---|---|---|
| 1 | Add this branch-context doc as a `T90_PATH_C4_V59_BRANCH_CONTEXT.md` sibling to the T90.59 writeup | ✅ This file |
| 2 | Add explicit "Branch line" header to T90.59 writeup noting it documents the wip/cloud-9-relhic line, not the standing v0.8 line | ✅ Done in this revision |
| 3 | Reframe the LZ Δlog Z in T90.59 as a fine-tuning penalty on μ_χ, not positive validation | ✅ Done in this revision |
| 4 | Add a 1-line note to README.md at repo root saying "see T90_PATH_C4_V59_BRANCH_CONTEXT.md for the wip/cloud-9-relhic T90 evolution line" | Not done (deferred — user decision) |
| 5 | Add a 1-line note to MATHEMATICS.md saying "this is the v0.4-prelim+T88E mathematical appendix; see T90_PATH_C4_V59 for the T90 hybrid form" | Not done (deferred — user decision) |
| 6 | Resolve the T86 σ_DM-nuc 15-order discrepancy | Not done (requires user input on which Kahlhoefer variant to trust) |
| 7 | Quantify fine-tuning on μ_χ (T90) and ε (v0.8) with a naturalness measure | Not done (deferred) |

---

## Honest conclusion

The T90.59 release is **a valid exploration of a different parameterization** that satisfies the same σ/m constraints as v0.8 with comparable Bayesian evidence. It is **not** an update to v0.8 — it's a parallel evolution experiment. The doc drift is **a consequence of having two parallel lines**, not a T82 audit failure.

The "Grand Unified" branding in the original T90.59 release title overclaims — see the post-review T90.59 writeup revision for the corrected framing. The "multi-channel SIDM" framing is more honest: the hybrid satisfies every constraint simultaneously *given the parameterization*, but the model is not uniquely determined, not validated by LZ (the LZ constraint is a fine-tuning penalty on μ_χ), and not the only possible solution.