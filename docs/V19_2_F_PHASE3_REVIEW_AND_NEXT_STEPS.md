# v19.2-F Phase 3 — Post-ClawsGO Review & Next-Steps Plan

**Date:** 2026-10-11
**Status:** Phase 3 COMPLETE (all 11 ClawsGO comments addressed); entering improvement-roadmap phase
**Baseline:** commit 40555d9 on `wip/v19.2-F-init` + master (ff-merged); tag `v19.2-F-Phase3-CLEAN`
**Review document:** `SIDM复合暗物质介质项目_科学可信度改进评估报告.pdf` (v1, 2026-10-11)
**Benchmark script:** `yukawa_resonance_benchmark.py` (run, figure produced: `yukawa_resonance_fig.png`)

---

## 1. Current state (post-ClawsGO #11)

### Phase 3 gate verdict
**FAIL.** No (α_D, m_A') point with m_χ = 1 GeV places a resonance at v = 29.4 km/s with σ/m = 174 cm²/g as a PEAK. Paper (A) is the honest result. The peak stays phenomenological by necessity.

### EXTENDED scan result (commit 40555d9)
- Best point: α_D = 5.55×10⁻⁶, m_A'/m_χ = 1.26×10⁻⁴ (m_A' = 126 keV, Born regime), giving σ/m(v=29.4) = 170.0 cm²/g (ratio 0.977)
- BUT: σ/m is monotonically decreasing in [5, 100] km/s (peak at v=5 km/s = 314 cm²/g); v = 29.4 is NOT a peak
- σ/m(10) = 293.6, σ/m(100) = 16.24 — factor 66-312× off the fit at window edges
- Single-velocity coincidence, not a fit

### Framework's named Yukawa (α_χ = 6.8×10⁻⁷, m_A' = 200 eV, t40 Born, κ = 3.4 > 1.68 threshold)
- σ/m(10) = 0.391 cm²/g
- σ/m(29.4) = 0.354 cm²/g (factor 492× BELOW target 174)
- σ/m(100) = 0.156 cm²/g (factor 3× over fit 0.052)
- Born is OUTSIDE its domain (κ = 3.4); true Sommerfeld-resummed value is larger but unknown; Calogero returns NaN at 200 eV

### Coupling-convention normalization (after ClawsGO #10/#11)
- α_D ≡ g²/(4π) is the correct convention
- κ = α_D m_χ/m_A' is the correct dimensionless criterion
- Framework's "σ/m(100) = 2.84" was a hand-waved estimate (corresponds to α ≈ 4.3×6.8e-7)
- Locking this in `constants.py` would prevent future recurrence

---

## 2. Independent review report (PDF) — physics claims audited

The PDF report has 5 sections + appendix. Here is my honest assessment of each claim.

### 2.1 κ_c normalization (claim 1, blocker 1)**✓ correct**
The benchmark's shooting method gives κ_c = 1.69 at ρ_max = 250 (0.5% from analytic 1.6798). The claim "κ = α_D m_χ/m_A' is the correct dimensionless resonance criterion" matches my Phase-3 doc convention. The framework's κ = 3.4 > 1.68 conclusion is self-consistent under this normalization.

Caveat not flagged in the report: the 0.5% deviation from analytic comes from the boundary condition u'(0)=1 (free-particle) rather than the correct u(r) ~ r near r=0. This is a standard small correction, but a referee might ask.

### 2.2 Elastic pile-up vs finite-velocity peak (claim 2)**✓ physically correct, ⚠ illustrative not rigorous**
The `sigma_elastic` function (`amp * (v0/v)^1.1 / (1+(v/v0)^2)^0.15` with amp=1200, v0=4) is a **parameterised ansatz**, not a Calogero/partial-wave result. It gives σ/m(29.4) = 73.3 cm²/g by construction. The qualitative conclusion (elastic Yukawa piles up at low v, no intermediate peak) is consistent with my Phase-3 EXTENDED scan (100 Calogero points over m_A' ∈ [1 keV, 2 GeV]) and with the deeper physics (de Broglie wavelength vs Yukawa range).

**The report does NOT show that this elastic curve corresponds to ANY actual (α_D, m_A') point.** It's a shape illustration.

### 2.2 iDM resonance (claim 3)**✓ shape matches, ⚠ not first-principles**
`sigma_idm(v) = 174 * exp(-0.5((v-29.1)/18)^2)` produces a peak at v ≈ 29.1 km/s by construction. This shows that **IF** you posit an intermediate-velocity resonance mechanism, the shape CAN match the target. The report does NOT derive this resonance from first principles (no iDM UV Lagrangian, no kinetic-mixing parameter, no constraint intersection).

### 2.2 Conclusion: "must introduce richer UV structure"**⚠ stronger than my Phase-3 doc**
The report claims "必须引入有限速度共振（iDM 类）或复合形状因子等更丰富结构" (must introduce finite-velocity resonance or composite form factor). My Phase-3 doc says the M2 (Sommerfeld/t-channel) mechanism is still an **OPEN hypothesis** — not ruled out by the scan. **My Phase-3 doc is more honest:** the scan rules out single-Yukawa resonances at v=29.4 in the (α_D, m_A') range scanned, but does NOT claim that NO mechanism can produce a peak.

### 2.2 σ/m(100) convention issue**✓ correct**
The report correctly identifies that "三套 σ/m(100) 的约定分歧" (three σ/m(100) values) — 0.052 (norm-matched), 2.84 (framework's previous doc claim), 41.0 (my ClawsGO #10 arithmetic error). The prescription to lock α_D ≡ g²/4π in `constants.py` is correct and would prevent recurrence.

### 2.2 Numerical claim "73.3 cm²/g at v=29.4 km/s from elastic curve"
This is the elastic *ansatz* value (parameterised shape), not a partial-wave/observed value. Consistent with my Phase-3 finding that single-Yukawa σ/m is monotonically decreasing, so σ/m(29.4) < σ/m(5).

### Section 3 (improvement roadmap)**✓ all constructive**
The 9-item roadmap is reasonable, with high-value items at the top:
- Item 1 (bound-state ridge scan): directly upgrades "scan failed" to a falsifiable structural claim
- Item 2 (iDM / composite form factor): explores richer UV structures
- Item 3 (constraint intersection): necessary for the conclusion to be falsifiable
- Item 6 (lock coupling convention): directly addresses the σ/m(100) ambiguity

### Section 4 (reproducibility)**✓ good**
Benchmark is self-contained, runs in ~10 seconds, produces both numerical outputs and a figure. I verified the numbers reproduce exactly (run output matches the PDF table).

---

## 3. Net assessment of the report

The report is a credible, well-structured improvement roadmap with two useful numerical benchmarks (κ_c convergence + elastic vs finite-velocity shapes). Where it's stronger than my doc: it explicitly quantifies the κ = 3.4 claim via the shooting-method convergence test. Where my doc is stronger: it honestly notes the M2 mechanism is not excluded. The report is internally consistent and the prescriptions are actionable.

**One caveat the report doesn't flag:** the benchmark's "single-Yukawa pile-up" conclusion depends on the chosen elastic ansatz (`amp=1200, v0=4`), not on a first-principles (α_D, m_A') point. The report would be stronger if it showed: "for this (α_D, m_A') point, the partial-wave solve gives this curve." As-is, the elastic shape is illustrative of the qualitative physics (pile-up at low v) but not of any specific calculation.

---

## 4. Next-steps plan (priority-ordered)

### Priority 1 — Lock coupling convention in `constants.py` (ClawsGO #9/#10/#11 close-out)
**Deliverable:** A `constants.py` module (or update to `channels_v03.py`) that:
- Defines `alpha_D ≡ g²/(4π)` explicitly with a self-consistency assertion
- Defines `kappa = alpha_D * m_chi / m_A_prime` with the same assertion
- Has the threshold `kappa_c = 1.68` hard-coded with a reference
- Documents the convention used everywhere else (Phase-3 doc, PAPER_V1_DRAFT.md, t40_yukawa_sigma_m.py)
- Adds a unit test that checks the convention is applied consistently across all references

**Time:** 0.5 day. **Deliverable:** commit + `constants.py` + `test_convention.py`.

### Priority 2 — Bound-state ridge scan (report Item 1)
**Deliverable:** A script `v19_2_f_phase3_bound_state_ridge_scan.py` that:
- For each (α_D, m_A'), solves the s-wave Schrödinger equation for E₀ (using the validated shooting-method DOP853 integration, borrowed from the benchmark)
- Plots E₀ vs (α_D, m_A') as a "bound-state surface"
- Identifies where E₀ = 0 (the bound-state formation curve)
- Records the (α_D, m_A') points where the bound-state energy matches E_resonance ≈ ½ μ v_target² (so the resonance lands at v=29.4 km/s)
- Tests whether these points ALSO give σ/m(29.4) ≈ 174 cm²/g as a peak

**Why this matters:** converts "scan failed" to a **falsifiable structural claim** — "the cloud-9 feature requires α_D and m_A' to lie on a specific bound-state curve AND have the bound-state energy tuned to E_resonance, a 10⁻⁹ precision tuning (Phase-1 path)". This is what ClawsGO #8/#9 said was missing.

**Time:** 2-3 days. **Deliverable:** commit + script + plot of the bound-state surface + ridge location.

### Priority 3 — Constraint intersection map (report Item 3)
**Deliverable:** A plot "峰可达区 ∩ 未被排除区" (peak-reachable × not-excluded) for the M2 mechanism candidate, showing:
- BBN / CMB / SN1987A constraints on dark photon (m_A' in [1 keV, 100 MeV] decaying to e⁺e⁻ → excluded for visible decay, allowed for invisible)
- Lyman-α / subhalo survival: σ/m > 100 cm²/g at v = 30 km/s suppresses subhalos (the "too-big-to-fail" problem)
- Direct detection (XENONnT/LZ): kinetic mixing gives DM-electron scattering limits on ε
- The 200 eV Yukawa framework point: does it pass/fail each?

**Why this matters:** converts the Phase 4 deferral ("worth checking into 174@29.4") into a binary falsifiable map.

**Time:** 3-5 days (most is literature lookup, not coding).

### Priority 4 — Composite form factor F²(q) attempt (report Item 2, alternative)
**Deliverable:** A script `v19_2_f_phase3_composite_form_factor.py` that:
- Implements a simple composite form factor F(q) = 1/(1 + q²/Λ_D²) (or Gaussian F(q) = exp(-q²/Λ_D²))
- Replaces the point-like Yukawa with a composite propagator
- Tests whether σ/m(v) develops a peak at v=29.4 km/s for some Λ_D

**Why this matters:** the project premise IS "composite DM". Using a composite form factor is the most natural way to get intermediate-velocity structure from the project's own framework. If it works, this is the strongest possible peak-mechanism candidate.

**Time:** 1-2 days.

### Priority 5 — Solver benchmark suite (report Item 5, Item 7)
**Deliverable:** A `tests/test_solver_benchmarks.py` that:
- Reproduces Tulin-Yu 2018 Fig. 2 (Yukawa σ/m(v) for m_φ = 10, 50, 100 MeV)
- Reproduces Loeb-Weiner 2011 classical limit
- Reproduces Born limit (high-v Yukawa cross section)
- Cross-checks Calogero against these limits
- Makes the benchmark part of `pre-commit` so future code changes are auto-validated

**Why this matters:** ClawsGO #8 caught a unit bug (50× velocity conversion). Calogero is the project's only validated solver. Locking in regression tests prevents the same class of bug from recurring.

**Time:** 1-2 days.

### Priority 6 — NaN distribution report (report Item 8)
**Deliverable:** A summary table in the Phase-3 doc showing:
- Number of null (Calogero NaN) scan points per (α_D, m_A') region
- Whether the nulls cluster at "where the peak should be" or are scattered

**Why this matters:** validates that the scan wasn't suppressed in the critical region.

**Time:** 0.5 day.

---

## 5. Recommended order

| Step | Time | Rationale |
|---|---|---|
| 1. Lock coupling convention | 0.5 d | Prevents recurrence of the σ/m(100) confusion. Quick win. |
| 2. Bound-state ridge scan | 2-3 d | Report Item 1 — directly upgrades "FAIL" to a falsifiable structural claim. |
| 3. Solver benchmark suite | 1-2 d | Defensive — Tulin-Yu/Loeb-Weiner/Born regression tests. Cheap insurance. |
| 4. Composite form factor | 1-2 d | Natural project-premise extension. If it works, it's the killer result. |
| 5. NaN distribution report | 0.5 d | Documentation/audit. |
| 6. Constraint intersection map | 3-5 d | Most literature-heavy. Can be deferred to last. |

Total ~2-3 weeks to complete all 6 items.

---

## 6. Open questions for the user

Before I start coding, please confirm:

1. **Convention lock** — Do you want α_D ≡ g²/(4π) (the standard convention in this report and in Tulin-Yu 2018)? Or do you want to keep the alternative convention where the framework's "α_χ = 6.8e-7" is g² (no 4π)? The latter was the source of the σ/m(100) disagreement.

2. **Bound-state ridge scan** — Should this scan use the same Calogero+framework-t40 hybrid that was just dropped, OR a fully validated shooting-method solver (like the benchmark's DOP853)? The benchmark's approach is the most robust.

3. **Composite form factor** — Is the project's `Λ_D` (composite compositeness scale) set somewhere in the codebase? I haven't seen it. If it's a free parameter, what range should I scan?

4. **Constraint intersection map** — Should I include ONLY the framework's 200 eV Yukawa, OR also include the iDM-mechanism candidate and the bound-state ridge from Step 2?

5. **Time budget** — Do you want all 6 items, or a subset (Priority 1+2+5 first, then decide based on those results)?

---

## 7. Honest summary

The Phase-3 result is correct: **paper (A), FAIL, phenomenological peak**. The PDF report's contribution is to give a falsifiable upgrade path (Items 1, 3, 6) and remove ambiguity (Items 6, 7). My recommended next steps (Priorities 1-6) implement those upgrades in order of scientific value.

The single most important next step is the **bound-state ridge scan** (Priority 2): if a (α_D, m_A') point lands on the ridge AND gives a σ/m peak at v=29.4 km/s, this is the strongest possible result the project can ship. If no point lands on the ridge, the gate is closed forever and paper (A) is final. Either way, the answer is **falsifiable** in a way the current scan result is not.

Standing by for confirmation on items 1-5.