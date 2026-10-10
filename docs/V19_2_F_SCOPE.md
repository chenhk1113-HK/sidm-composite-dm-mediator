# v19.2-F — UV completion track scope

**Date opened:** 2026-10-09
**Branch:** wip/v19.2-F-init
**Status:** Phase 1+2 complete, Phase 3 (resonance scan) is the kill/continue gate
**Source plan:** [CLAWSGO_PLAN_UV_multimediator_clockwork.md](CLAWSGO_PLAN_UV_multimediator_clockwork.md)

## Goal

Take the v19.2-D-FREEZE σ(v) phenomenology (multi-resonance + power-law background, σ₀ = 0.052, a = 1.93, v_target = 29.4 km/s, σ_peak = 174 cm²/g, σ₁ = 4.4 km/s) and ask: *can any UV completion derive it?* Two tracks depending on Phase 3:

- **Paper (A) — UV-requirements** (safe, ~3 weeks): "Here is what any UV completion must satisfy; the peak cannot be derived without ~10⁻⁹ tuning and the low-v background is over the Horigome limit."
- **Paper (B) — UV-completion** (ambitious, ~2-3 months): "Here is a concrete dark sector that reproduces σ(v) and passes Cloud-9 + Horigome + LZ + relic + ΔN_eff."

**Do NOT commit to (B) before Phase 3 passes its gate.** The v19.2-D paper is frozen; v19.2-F is a separate track that cites the v19.2-D phenomenology as input, not re-derived.

## Phase status

- **Phase 0 (freeze hygiene):** DONE (R88(82)-(88), tag v19.2-D-milestone-R88-final)
- **Phase 1 (kinematics table):** DONE — Cloud-9 s-channel pole requires **1.2×10⁻⁹** relative tuning, fractional width **3.6×10⁻¹⁰**. M1 dropped; M2 leading.
- **Phase 2 (background gate):** DONE — A single light Yukawa does NOT reproduce the fitted background at the framework's parameters. 200 eV Yukawa at m_φ = 200 eV has Born slope −3.83 (not −1.93). Normalized to σ/m(100) = 0.052 (α = 9.2×10⁻⁸, not the framework's α_χ = 6.8×10⁻⁷), it overproduces σ/m at low v by 78× at v = 10; at the framework's *own* α_χ = 6.8×10⁻⁷, it fails at v = 100 by 55× and overproduces at v = 10 by ~4300×. Either way the Horigome low-v tension is *worse*, not better. Best single-Yukawa shape match is m_φ ≈ 86 keV (428× the framework's 200 eV). Fitted slope a = 1.93 is *closer to* (not "is") a Sommerfeld v⁻² near a t-channel bound-state resonance (M2 mechanism) — a hypothesis to be tested in Phase 3, not a stated property of the fit.
- **Phase 3 (resonance scan):** PENDING — the kill/continue gate. With the Phase-2 potential, scan (α_χ, m_φ/m_χ) for resonant poles (l = 0, 1 partial waves). For each pole, record v_res, peak height (unitarity-capped), width. Question: does any (α_χ, m_φ/m_χ) with m_χ = 1 GeV place a resonance at v ≈ 29 km/s with σ_peak ≈ 174 cm²/g and Γ/v ≈ 0.05-0.10, AND is the required α_χ compatible with the value implied by the hierarchy? **Pass → paper (B). Fail → paper (A).**
- **Phase 4 (joint fit over full constraint set):** PENDING — only if Phase 3 passes
- **Phase 5 (clockwork for hierarchy only):** PENDING — 2 weeks, parallel to 3-4
- **Phase 6 (relic density and cosmology):** PENDING
- **Phase 7 (write-up):** PENDING

## Honest limit sentence (v19.2-D-FREEZE, §2.8)

> "The background σ/m = 0.052·(100/v)^1.93 is a *phenomenological* fit to the channels. Its UV derivation is an open question. A s-channel pole at v_res = 29.4 km/s requires 1.2×10⁻⁹ near-threshold tuning of the mediator mass (M1 mechanism, dropped per Phase-1 gate). A first-principles Yukawa background at m_φ = 200 eV has slope −3.83 (not the fitted −1.93). Normalized to σ/m(100) = 0.052, it overproduces σ/m at low v by 78× at v = 10 km/s; at the framework's own α_χ = 6.8×10⁻⁷, it fails at v = 100 by 55× and overproduces at v = 10 by ~4300×. The Horigome tension is *worse*, not better, under either coupling. The fitted slope a = 1.93 is *closer to* (not 'is') a Sommerfeld v⁻² near a t-channel bound-state resonance (M2 mechanism) — a hypothesis to be tested in Phase 3, not a stated property of the fit. The σ/m(v) phenomenology of v19.2-D remains the input; v19.2-F (Phase 3+) is the program that tests whether any two/three-mediator UV sector produces it."

**Caveat (v19.2-E A.1).** Under the promoted real likelihood (T205 8-channel published-σ_unc), the canonical Phase 44 parameters (σ₀ = 0.052, a = 1.93, σ_peak = 174, v_target = 29.4, σ₁ = 4.4) pass **1 of 8 channels** (Cluster v=500 only). The 5-parameter DE best-fit (v19.2-E A.2) passes **5 of 8** (sigma_peak=2026, sigma_1=1.2). The data prefer a *different* point at 5/8. The "canonical" σ(v) presented in the v19.2-D paper is the v1 free-fit result; v19.2-E shows the data prefer a different (5-param DE) point.

**Open requirement (NOT a no-go).** The Phase-2 gate establishes that *the framework's named single 200 eV Yukawa* is not the background — a statement about the paper's own mediator, not a UV completion no-go. The class is not ruled out while M2 (Sommerfeld/t-channel resonance) is open and Phase 3 is pending. This complements the five UV no-gos already in §10; it should be read as **the background is phenomenological; a first-principles derivation is open (v19.2-F Phase 3)**, not as a sixth no-go.

## What ships

- Paper (A) or (B) — TBD by Phase 3 result
- Two figures: coupling-plane resonance map (Phase 3); from-first-principles σ(v) vs the fitted curve (Phase 2, already in `uv_work/phase2_yukawa_background.py`)
- The kinematics table (Phase 1, already in `uv_work/phase1_kinematics.py`)

## Tools

- Plain Python/scipy (radial Schrödinger ODE, partial-wave sums, scans) — no GPU, no cluster needed for Phases 1-3, 5
- Phase 4 reuses the existing phase41/43 SPARC code
- Phase 6 may need a Boltzmann solver (or a calibrated analytic treatment)

## Effort

- ~3-4 weeks for paper (A)
- ~2-3 months for paper (B)
- AI-assisted wall time shorter; **R88(71) pre-claim checklist on every numerical claim** (it has caught real errors three times)

## Risks

1. **Near-threshold tuning (~10⁻⁹) is irreducible for M1** — likely, and itself the result (paper A).
2. **Low-v background over Horigome** may be unfixable within a Yukawa background — then the honest conclusion is that Cloud-9 + Horigome require a low-v cutoff, a specific, publishable demand.
3. **Inputs are phenomenological** — the whole exercise inherits the fitted σ(v); state this explicitly in the abstract.
4. **Scope creep** — the v19.2-D paper is frozen; this is a separate track.

## Reference

- v19.2-F Phase 1+2 results: `docs/V19_2_F_PHASE1_2_RESULTS.md`
- PAPER_V1_DRAFT.md §2.8 (added 2026-10-09): UV status of σ/m(v)
- v19.2-D-FREEZE: tag `v19.2-D-milestone-R88-final`, commit 53ce85e
- v19.2-E COMPLETE: tag `v19.2-E-D`, commit 169ee1f
