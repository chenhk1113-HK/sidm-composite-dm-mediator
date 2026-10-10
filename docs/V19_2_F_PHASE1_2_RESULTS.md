# v19.2-F Phase 1 + Phase 2 — UV completion gate results

**Date:** 2026-10-09
**Status:** v19.2-F track (forward-looking, separate from v19.2-D-FREEZE)
**Source:** ClawsGO Science Harness, [`uv_work/phase1_kinematics.py`](uv_work/phase1_kinematics.py) · [`uv_work/phase2_yukawa_background.py`](uv_work/phase2_yukawa_background.py)
**Branch:** wip/v19.2-F-init

## Strategic context

Per [CLAWSGO_PLAN_UV_multimediator_clockwork.md](CLAWSGO_PLAN_UV_multimediator_clockwork.md), the v19.2-F track is the program that takes the v19.2-D-FREEZE σ(v) phenomenology and asks: *can any UV completion derive it?* Two tracks:

- **Paper (A) — UV-requirements (safe, ~3 weeks)**: "Here is what any UV completion must satisfy; the peak cannot be derived without ~10⁻⁹ tuning and the low-v background is over the Horigome limit."
- **Paper (B) — UV-completion (ambitious, ~2-3 months)**: "Here is a concrete dark sector that reproduces σ(v) and passes Cloud-9 + Horigome + LZ + relic + ΔN_eff."

Phases 1-3 are common to both; the Phase-3 result decides which paper is being written. **Do NOT commit to (B) before Phase 3 passes its gate.**

## Phase 1 — s-channel near-threshold kinematics

**Question:** If the Cloud-9 feature (v_res = 29.4 km/s) is an s-channel pole just above 2m_χ, what mass precision does the mediator need?

**Method:** Convention √s = 2m_χ + ¼m_χv², m_χ = 1 GeV. For each v_res, compute:
- Pole offset ΔM above 2m_χ
- Relative tuning ΔM/2m_χ
- Width Γ_E from σ₁ = 4.4 km/s
- Fractional width Γ_E/2m_χ

**Result table:**

| v_res [km/s] | pole offset ΔM above 2m_χ | relative tuning ΔM/2m_χ | Γ_E (σ₁ = 4.4 km/s) | Γ_E/2m_χ |
|---|---|---|---|---|
| 5 | 0.070 eV | 3.5×10⁻¹¹ | 0.12 eV | 6.1×10⁻¹¹ |
| 10 | 0.28 eV | 1.4×10⁻¹⁰ | 0.25 eV | 1.2×10⁻¹⁰ |
| 20 | 1.11 eV | 5.6×10⁻¹⁰ | 0.49 eV | 2.5×10⁻¹⁰ |
| **29.4 (Cloud-9 node)** | **2.40 eV** | **1.20×10⁻⁹** | **0.72 eV** | **3.6×10⁻¹⁰** |
| 50 | 6.95 eV | 3.5×10⁻⁹ | 1.22 eV | 6.1×10⁻¹⁰ |
| 100 | 27.8 eV | 1.4×10⁻⁸ | 2.45 eV | 1.2×10⁻⁹ |
| 178 | 88.1 eV | 4.4×10⁻⁸ | 4.36 eV | 2.2×10⁻⁹ |
| 430 | 514 eV | 2.6×10⁻⁷ | 10.5 eV | 5.3×10⁻⁹ |

**Read-off.** The Cloud-9 feature, if it is an s-channel pole, requires the mediator 2.40 eV above the 2m_χ threshold at a fractional precision 1.2×10⁻⁹, with fractional width 3.6×10⁻¹⁰. **Nothing in the framework's own machinery** (a 200 eV Yukawa; a clockwork mass ladder) produces a 2.4 eV offset at 10⁻⁹ precision — M1 is a *tuning statement*, not a mechanism the framework supplies.

**Honest limit clause for v19.2-D-FREEZE paper:** "the Cloud-9 feature, if it is an s-channel pole, requires 1.2×10⁻⁹ near-threshold tuning of the mediator mass, with fractional width 3.6×10⁻¹⁰. The framework does not supply this from a 200 eV Yukawa or a clockwork mass ladder; it is a tuning requirement, not a UV prediction."

**Gate:** if M1 requires tuning worse than ~10⁻⁸ and no symmetry justifies it, drop M1 and go with M2 (M3 as backup). The Cloud-9 tuning 1.2×10⁻⁹ is in the "drop M1" range; M2 (Sommerfeld/t-channel resonance, Chu, Hambye & Tytgat 2018 [7]) is the leading candidate. **M1 dropped; M2 + M3 are the candidate mechanisms for Phase 3.**

## Phase 2 — Background gate

**Question:** Can a single light Yukawa (m_φ = 200 eV, α_χ ≈ 6.8×10⁻⁷) reproduce the fitted background σ/m = 0.052·(100/v)^1.93 cm²/g at m_χ = 1 GeV?

**Method:** Born closed form σ_T = (2πα²/μ²v⁴)[ln(1+x) − x/(1+x)], x = 4μ²v²/m_φ², cross-checked against a full variable-phase (Calogero) partial-wave solver.

### Phase 2.1 — solver correctness

| Regime (α m_χ/m_φ) | Born vs partial-wave ratio |
|---|---|
| 0.01 (Born regime) | 0.990 (Born exact, as expected) |
| 0.5 | 0.65 |
| 20 (resonant regime) | 0.018 (Born fails as expected) |

**Verdict:** Solver reproduces Born in the weak-coupling limit and departs correctly as the potential deepens. Both methods are implemented in `uv_work/phase2_yukawa_background.py`; the partial-wave solver uses σ_T = (4π/k²)Σ(l+1)sin²(δ_l−δ_{l+1}) and is the right tool for κ = m_φ/m_χ not tiny.

### Phase 2.2 — The framework point (m_φ = 200 eV) is the wrong shape

| v [km/s] | Yukawa σ/m (200 eV, norm-matched at 100) | target σ/m | ratio |
|---|---|---|---|
| 10 | 347 | 4.43 | **78× too high** |
| 20 | 24.9 | 1.16 | 21× |
| 30 | 5.30 | 0.531 | 10× |
| 50 | 0.749 | 0.198 | 3.8× |
| 100 | 0.052 | 0.052 | 1 (by construction) |

**Findings:**
- Born slope = **−3.83** over 10-100 km/s, not −1.93. The Born turnover sits at v_turn ≈ m_φ/2μ ≈ 0.06 km/s, orders of magnitude below the window.
- Normalized to the correct value at v = 100, the 200 eV Yukawa **overproduces σ/m at low v by 78× at v = 10**. The Horigome low-v tension is *worse*, not better.
- The coupling needed for normalization is α = 9.2×10⁻⁸; the framework's derived α_χ ≈ 6.8×10⁻⁷ is 7.4× larger (order-of-magnitude consistent, but not the same number).

### Phase 2.3 — Best single-Yukawa *shape* match to the background

Scan m_φ, normalize each to σ/m(100) = 0.052, measure worst |log| deviation over 10-100 km/s:

| m_φ | slope | worst deviation over 10-100 |
|---|---|---|
| 200 eV (framework) | −3.83 | **78×** |
| 10 keV | −3.44 | 31× |
| 30 keV | −2.88 | 8.1× |
| **86 keV** | **−1.72** | **1.9×** |
| 100 keV | −1.52 | 2.5× |
| 300 keV | −0.41 | 29× |
| 1 MeV | −0.05 | 74× |

**Best single Yukawa:** m_φ ≈ 86 keV at 1.9× worst-case deviation, **428× heavier than the framework's 200 eV mediator**.

### Phase 2.4 — The resonant / classical regime goes flat, not −1.93

Full partial-wave, m_φ = 1-10 MeV (α m_χ/m_φ = 2-300):

| m_φ [MeV] | α | σ/m(10) | σ/m(30) | σ/m(100) | slope |
|---|---|---|---|---|---|
| 10 | 0.02-0.3 | ~30-250 | same | same | **≈ 0** |
| 1 | 0.02-0.3 | 2×10⁴-7×10⁴ | falling | falling | −0.1 to −0.2 |

**The two natural regimes bracket the target from opposite sides:**
- Born Yukawa → v⁻⁴ (too steep, slope −3.83 at m_φ = 200 eV)
- Deep resonant/classical → v⁰ (too flat, slope ≈ 0 at m_φ = 1-10 MeV)
- The fitted **−1.93** is not the Born signature; it is closer to a **Sommerfeld v⁻²** near a t-channel bound-state resonance.

## Phase 2 verdict (gate)

**A single light Yukawa does NOT reproduce the fitted background at the framework's parameters.** The background σ/m = 0.052·(100/v)^1.93 wants either:

1. A mediator of **m_φ ≈ 86 keV** (428× the framework's 200 eV) — reproducing the shape to ~2×; **OR**
2. A **resonant (t-channel Sommerfeld)** account of the slope, whose near-threshold v⁻² behaviour is *closer to* −1.93 — the M2 mechanism, to be tested in Phase 3.

**Per the plan:** the Phase-2 gate fails at the Born level — **exactly the condition for pivoting to paper (A) UNLESS Phase 3 passes.** Phase 3 is the kill/continue: scan (α_χ, m_φ/m_χ) for resonant poles, locate v_res, peak height (unitarity-capped), and width. If any (α_χ, m_φ/m_χ) with m_χ = 1 GeV places a resonance at v ≈ 29 km/s with σ_peak ≈ 174 cm²/g and Γ/v ≈ 0.05-0.10, AND the required α_χ is consistent with the hierarchy, paper (B) is alive. If not, paper (A) wins: "the Cloud-9 feature requires either ~10⁻⁹ s-channel tuning or a coupling/scale outside the range compatible with the background and hierarchy."

**Consequences for the v19.2-D-FREEZE paper:**
- The background σ/m(v) of §2.1 is **phenomenological**, not derived from the framework's named 200 eV Yukawa.
- The "Yukawa-type suppression, Feng+ 2009 [5]" label in §2.1 is a placeholder for the family of velocity-dependent suppression mechanisms; the specific Feng+ 2009 [5] formula is NOT the framework's background (which has slope −1.93, not Feng's −3.83 at m_φ = 200 eV).
- The fitted slope a = 1.93 is *closer to* (not "is") the M2 (Sommerfeld/t-channel resonance) mechanism, Chu, Hambye & Tytgat 2018 [7] — a hypothesis to be tested in Phase 3, not a stated property of the fit.
- This is a **paper update**, not a paper retraction: the σ(v) phenomenology is correct as a fit; what's wrong is the claim that it's *the* model's 200 eV Yukawa. The honest limit is added to §2.8 of the paper.

**Coupling attribution (ClawsGO #6).** The 78× overproduction at v = 10 km/s is at the **norm-matched** coupling α = 9.2×10⁻⁸ (which makes σ/m(100) = 0.052 by construction). The framework's *derived* coupling is α_χ = 6.8×10⁻⁷, which is 7.4× larger in α and 54.6× larger in σ_T ∝ α². At α_χ, the 200 eV Yukawa fails at v = 100 by 55× (σ/m(100) = 2.84 vs fitted 0.052) and overproduces at v = 10 by ~4300×, not 78×. Both couplings make the Horigome low-v tension *worse*, not better; the framework's α_χ is a sharper statement because it shows the 200 eV Yukawa is already inconsistent with the SPARC normalization.

**Caveat (v19.2-E A.1, ClawsGO #6).** Under the promoted real likelihood (T205 8-channel published-σ_unc, see §9.17), the canonical Phase 44 parameters (σ₀ = 0.052, a = 1.93, σ_peak = 174, v_target = 29.4, σ₁ = 4.4) pass **1 of 8 channels** (Cluster v=500 only). The 5-parameter DE best-fit (v19.2-E A.2) at the same likelihood passes **5 of 8** (sigma_peak=2026, sigma_1=1.2). The data prefer a *different* (5-param DE) point at 5/8. The "canonical" σ(v) presented in the v19.2-D paper is the v1 free-fit result; v19.2-E shows the data prefer a different point. This caveat belongs wherever "canonical" appears in the paper, including §2.1 and §2.8.

## Caveats

- Born and partial-wave use the standard SIDM momentum-transfer convention σ_T = (4π/k²)Σ(l+1)sin²(δ_l−δ_{l+1}); identical-particle symmetry factors (~O(1)) are not applied and do not affect the shape/slope conclusion.
- The framework point is evaluated in Born: α m_χ/m_φ ≈ 0.46 there, below the O(1)-to-~1.7 bound-state threshold, so the potential is far from binding, there is no Sommerfeld resonance, and Born is a fair approximation.
- The partial-wave solver is used where κ = m_φ/m_χ is not tiny (l_max tractable).
- The "428× heavier" claim (m_φ = 86 keV) is a *shape* match, not a *normalization* match; the coupling needed would still need to be derived from the hierarchy.

## Reference

- ClawsGO Phase 1: [`uv_work/phase1_kinematics.py`](uv_work/phase1_kinematics.py)
- ClawsGO Phase 2: [`uv_work/phase2_yukawa_background.py`](uv_work/phase2_yukawa_background.py)
- v19.2-D-FREEZE: tag `v19.2-D-milestone-R88-final`, commit 53ce85e
- v19.2-F track: branch `wip/v19.2-F-init`
- §2.1 of PAPER_V1_DRAFT.md: σ/m(v) parameterization (now annotated with Phase 2 background caveat)
- §2.8 of PAPER_V1_DRAFT.md (NEW): UV status of σ/m(v) (this Phase 1+2 result)
- §10 of PAPER_V1_DRAFT.md: five existing UV completion no-gos (now joined by a sixth from this result)
