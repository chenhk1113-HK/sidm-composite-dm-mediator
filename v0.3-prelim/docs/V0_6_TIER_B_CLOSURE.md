# Tier B closure — what shipped vs what's still deferred

> **Date**: 2026-08-28 (T71.5 closure)
> **Scope**: V0_6_ROADMAP items #12 (Drobczyk quantitative), #16 (LZ WS2024), #17 (KiSS-SIDM UFD fidelity)
> **Pre-flight outcome**: 1 of 3 items was stale (already shipped); 1 was a real 3-5 day research task done in 1 session; 1 has a hard wall-time limitation that requires a separate focused session.

This document is the closure note for the Tier B scope, parallel to the R16 reviewer-audit doc addendum.

---

## Tier B #16 — LZ WS2024 full posterior shapes: **ALREADY SHIPPED (stale roadmap item)**

**Roadmap claim** (T70.6): "Wire in LZ WS2024 / Fermi-LAT full posterior shapes — ~2 weeks, deferred to v0.6+."

**Reality check (2026-08-28)**:

The real LZ WS2024 posterior is **already in production** in the T41 production chain since R12 (2026-08-17). Evidence:

1. **`v0.3-prelim/code/t30_lz_real_posterior.py`** (262 lines) ingests the actual LZ WS2024 SI cross-section limits from **HEPData record 155182** (arXiv:2410.17036, PRL 135, 011802). 26 mass points, interpolated likelihood function `loglike_lz_real()`.

2. **T41 production chain uses the real LZ likelihood** at `v0.3-prelim/code/t41_mediator_mass_joint_fit.py:247`:
   ```python
   ll_lz = loglike_lz_real(m_chi_GeV, sigma_DM_n)
   ```
   No env var, no flag — it's the default. Every T41 v0.6 result since 2026-08-17 (T70.5+ through T71.4) uses the real WS2024 posterior.

3. **Comparison run on disk**: `v0.3-prelim/data/results/t30_lz_real_posterior.json` documents the placeholder-vs-real delta (real is more constraining than the legacy 9-point Gaussian placeholder by ~Δlog Z = 9207 in the 2D LZ-only fit).

**Verdict**: Tier B #16 is **stale** — same pattern as R15's "(Nc, Nf) scaffolded only" claim and R16's "channel experimental" claim. The roadmap item was written before T30 + R12 wired the real WS2024 data into production. The "v0.6+" deferral was an oversight; the work was already done.

**Action taken**: Marked V0_6_ROADMAP #16 as ✅ Shipped T71.5 (already shipped via T30, 2026-08-17; this is a documentation correction, not new work).

---

## Tier B #12 — Drobczyk 2025 quantitative σ/m(v) curve matching: **SHIPPED (T71.5, today)**

**Roadmap claim** (T70.6): "Quantitative σ/m(v) curve matching — ~1 week, deferred to v0.6+."

**Reality check (2026-08-28)**: T68 had Drobczyk's benchmark numbers hardcoded but no actual chi² test. T68b closes the gap.

**New file**: `v0.3-prelim/code/t68b_quantitative_cross_validation.py` (290 lines, compiles clean).

**Method**:
- Reads T41 v0.6 hier-sparc MAP (sigma/m_0 = 0.065 cm²/g, a = 0.114) as our point estimate
- Computes our σ/m(v) at Drobczyk's 3 published velocity points (v = 10, 30, 1000 km/s)
- Runs a chi² test with assumed per-point uncertainty of 0.2 dex (Drobczyk doesn't publish error bars; 0.2 dex ≈ factor-of-1.6 is conservative)

**Result** (`v0.3-prelim/data/results/t68b_quantitative_cross_validation.json`):
- chi² = **213.62** on 1 dof → **STRONG TENSION** (the two models disagree within even a wide 0.2 dex uncertainty)
- Per-point breakdown:
  | Velocity | Our σ/m | Drobczyk σ/m | Factor | log₁₀ gap |
  |---|---|---|---|---|
  | v=10 km/s (dwarf) | 0.085 cm²/g | 0.96 cm²/g | 0.09× | -1.06 dex |
  | v=30 km/s (MW sat) | 0.075 cm²/g | 0.11 cm²/g | 0.68× | -0.17 dex |
  | v=1000 km/s (cluster) | 0.050 cm²/g | 9.5e-5 cm²/g | **526×** | **+2.72 dex** |
- **Cluster scale is the worst disagreement** — our model overpredicts σ/m at cluster v by factor 526.
- To match Drobczyk's dwarf value (0.96 cm²/g at v=10), we'd need σ/m_0 = 0.74 cm²/g (vs our MAP 0.065 — 11× higher).

**Honest framing (in the JSON's "honest_framing" field)**:
> "Our T41 MAP σ/m_0 = 0.065 cm²/g is significantly LOWER than Drobczyk's dwarf prediction (0.96). The ~1.2 dex gap at the dwarf scale reflects a real quantitative disagreement between the two models: Drobczyk's two-mediator model with resonant freeze-out naturally produces HIGHER σ/m at low v; our single-mediator dark-ρ model produces LOWER σ/m at low v. Both models are valid frameworks with different physics; we do NOT conclude one is 'right' and the other 'wrong'. A future hierarchical model comparison would need both models fit to the SAME data with the SAME likelihood machinery."

**Caveats** (also in the JSON):
- Drobczyk doesn't publish per-point error bars; 0.2 dex is conservative
- Our MAP is a point estimate; full posterior uncertainty would widen the comparison
- The two models use different coupling parameterizations (y_χ Yukawa vs g_χ gauge coupling); a direct chi² comparison is approximate

**Action taken**: V0_6_ROADMAP #12 marked ✅ Shipped T71.5. Real research output, even if the conclusion is "the models disagree, here's exactly how much".

---

## Tier B #17 — KiSS-SIDM UFD fidelity upgrade: **PARTIAL — wall-time limited**

**Roadmap claim** (T70.6): "Application of cluster-scale bounds to UFDs is a known approximation; proper treatment is multi-week."

**Reality check (2026-08-28)**:

The KiSS-SIDM Julia bridge (`v0.3-prelim/code/kiss_sidm_julia_bridge.py`) is set up correctly, but has a **hard wall-time bottleneck** at the UFD scale:

1. **T38 (dwarf KiSS-SIDM, 2026-08-22) ALREADY FAILED** at N=5e4 with `TimeoutExpired: Command 'julia' timed out after 3600 seconds` (the bridge's hardcoded 3600s timeout). The KiSS-SIDM Julia DSMC code is intractable at UFD scale within 1 hour per run.

2. **T27 (multiresolution KiSS-SIDM, 2026-08-21)** showed that the **canonical halo (M_halo = 10⁹ M_☉) is fully converged** at N=1e4 and N=1e5 (identical r_core/r_s = 0.1024). But the convergence study was done for the canonical halo, NOT for UFD halos.

3. **T38 hypothesis** (was): "dwarf regime requires N ≥ 1e5". The T38a test at N=5e4 hit the 3600s timeout before testing N=1e5. To go further would require either (a) the original Gurian & May 2025 paper's N=2e6 (their reported convergence threshold, requiring ~30 min on a laptop in their C/Python code), OR (b) rewriting the KiSS-SIDM DSMC in a faster language (C/Rust).

4. **Yang+ 2023 UFD benchmark data**: not in the repo. Would need to be downloaded (no automated download path; AGENTS.md rule 17 = no new deps without approval).

**Why this can't ship in one session**: A N=1e5 or N=2e6 KiSS-SIDM dwarf run requires either (a) ≥1 hour wall-time per config (and the bridge's 3600s timeout is already saturated), or (b) code refactoring. Both are beyond a single-session budget. Per the parallel-execution-decision skill's 600s subagent timeout rule and the AGENTS.md rule 23 silent-failure hook: don't kick off a KiSS-SIDM UFD run that we expect to fail and then "wait and see".

**Honest framing (this closure note)**:
- The canonical-halo KiSS-SIDM pipeline is **production-grade** (T21, T22, T23, T27 converged at N=1e4-1e5).
- The dwarf/UFD KiSS-SIDM pipeline is **intractable** at our computational budget (T38a timeout, N=5e4 → 1 hour no result).
- A real UFD-fidelity upgrade requires either (a) a separate dedicated compute session (~weeks of wall-time on a cluster), or (b) rewriting KiSS-SIDM in a faster language, or (c) using the paper's original C/Python implementation instead of our Python reimplementation (which would require external dep install + AGENTS.md rule 17 approval).

**Action taken**: V0_6_ROADMAP #17 marked **Deferred (wall-time limited)** with a multi-line rationale. NO new code shipped for #17 in T71.5. The closure note (this document) is the deliverable.

---

## Summary table

| Tier B item | Roadmap claim | Pre-flight finding | T71.5 action | Status |
|---|---|---|---|---|
| #12 Drobczyk quantitative | "~1 week" | T68 had hardcoded benchmarks; no chi² test | t68b written + run; chi²=213 on 1 dof | ✅ Shipped T71.5 |
| #16 LZ WS2024 posteriors | "~2 weeks" | Already in T41 production via t30 since R12 | Roadmap doc correction; no new code | ✅ Shipped T71.5 (stale → already shipped via T30) |
| #17 KiSS-SIDM UFD fidelity | "Multi-week" | T38a failed at N=5e4 (1-hour timeout); canonical converged but UFD intractable at our compute budget | Honest closure note (this doc); V0_6_ROADMAP #17 deferred with rationale | ⚠️ Deferred (wall-time limited) |

**Net Tier B outcome**: 2 of 3 items resolved (1 real new work, 1 stale-claim correction). 1 item honestly documented as deferred with multi-line rationale. No fake "shipped" claims.

## What's still on Tier C/D for v0.6

Per V0_6_ROADMAP, items #10 (Boltzmann relic), #18 (form-factor ansatz), #11 (external review), #19 (lattice KSFR ratios) remain deferred. Each is multi-week or out-of-band.

The next realistic v0.6 milestone is "Tier B closure" (T71.5, this commit). After that, the v0.6 roadmap has 4 deferred items, each requiring either dedicated compute (Boltzmann / lattice) or external action (review / KSFR data).
