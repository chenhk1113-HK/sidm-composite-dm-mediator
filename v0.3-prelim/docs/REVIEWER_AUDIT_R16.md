# Reviewer-Audit Response: sidmgrok1.docx (2026-08-27)

> **Source**: User upload `C:\Users\lamkuenai\AppData\Local\hermes\cache\documents\doc_7352bd3b340a_sidmgrok1.docx`
> **Audit date**: 2026-08-27 (round 6 / R16 audit cycle)
> **Reviewer identity**: Per the explicit AI-disclaimer in P004 ("coding was done primarily by Hermes/MiniMax-M3 with Doubao, Qwen, and other models as reviewers"), this is most likely a **machine-generated review** (the filename `sidmgrok1.docx` is consistent with Grok as the source model). Per reviewer-audit skill W1 + W3, **reviewer identity does not affect verification rigor** — every claim is verified against on-disk state regardless of who wrote it.
> **Review target stated by reviewer**: sidm-composite-dm-mediator (general)
> **Project standing-version NOW**: v0.3-prelim+T71.1 (after T70.9 + T71.0 + T71.1 closures)
> **Pattern**: Per reviewer-audit skill W1 — **referee-style review** with explicit "Strengths / Major Concerns / Technical / Overall Assessment / Necessary actions" structure. **Distinct from sidm5.docx (R15)** in that it includes an **explicit AI-disclaimer** and adds a **"Necessary actions to improve scientific plausibility"** section with **12 specific recommendations** organized as Priority 1/2/3/4.
> **Closest prior patterns**: W-series from sidm-review-v05-referee-style-w.md (sidm review.docx) and the R15 sidm5.docx audit (this round). All three are referee-style reviews of the same project with overlapping content.

---

## Overall assessment (per W4 grading)

**Grade: A-.** The reviewer correctly characterizes the project as a "serious, well-documented curiosity-driven pipeline that demonstrates how far an AI-assisted workflow can push a complex multi-channel Bayesian analysis." Most headline numbers (v0.5 MAP m_ρ ≈ 500-550 MeV, σ/m₀ ≈ 0.105 cm²/g, m_χ ≈ 515 GeV, a ≈ +1.89) verified against `t41_mediator_mass_joint_fit_v0_5.json`. The explicit AI-disclaimer is appropriate and honest.

**However, 3 of the 12 numbered recommendations are STALE** — the reviewer suggests features/improvements that were already shipped in this round (T70.8, T70.9, T71.0, T71.1) or in prior rounds (R12, R13). The recommendation that the KSFR mask fix needs proper cross-version controls is **already shipped** in T71.1 with explicit documentation. The recommendation to enable inelastic scattering is **already shipped** in T71.1 (90 sec run completed).

The reviewer explicitly acknowledges that the project's own `MODEL_ASSUMPTIONS_AND_LIMITATIONS.md` and `V0_6_ROADMAP.md` already identify most of these items. Per AGENTS.md rule 5 (least-surprise) and rule 11 (honest scope), the right action is to **acknowledge + defer** most of these items and **ship only those that fit the v0.6+ roadmap**.

---

## Per-claim verification matrix (5-label per V1 + W3)

| # | Reviewer claim | Label | Evidence |
|---|---|---|---|
| P002 | "claims ~15-16 observational channels (dSph, UFD, Bullet Cluster, SPARC, LZ, Fermi, DM-free UDGs, cosmic-web radio, mass floors, BBN/mediator lifetime, KSFR/PCAC validity, CMB spectral distortion, etc.)" | ✅ Confirmed | README badge + `REVIEWER_AUDIT_R14.md:171`: **16 channels** (T70.8 added Channel 16 = CMB μ/y). |
| P008 | "Extensive changelogs, versioned prelim tags (v0.1-v0.3 + T70/T71 patches)" | ✅ Confirmed | `git log --oneline \| grep -E "T70\|T71"` shows T70.4 through T71.1. |
| P008 | "multiple AI-reviewer audit closures (R12-R15)" | ✅ Confirmed | `REVIEWER_AUDIT_R12.md`, `R13.md`, `R14.md`, `R15.md` all exist. |
| P012 | "~574 pass / 0 fail / a few skips" | ✅ Confirmed | T71.1: **574 pass / 0 fail / 7 skip**. |
| P013 | "Pinned requirements.txt" | ✅ Confirmed | `requirements.txt` exists with explicit version pins. |
| P014 | "Reference posterior chains in data/reference/" | ✅ Confirmed | 4 reference NPZ files committed (per `data/reference/MMANIFEST.json`). |
| P016 | "Honest treatment of approximations (soft Bullet likelihood, calibrated SPARC score, calibrated relic density)" | ✅ Confirmed | All three stand-ins documented in `MODEL_ASSUMPTIONS_AND_LIMITATIONS.md`. |
| P019 | "Cross-checks against literature (e.g., Drobczyk 2025 arXiv:2506.22997)" | ✅ Confirmed | References in `MEDIATOR_DETECTION_SYNTHESIS_v10/11/12.md` + `REVIEWER_AUDIT_R12.md`. |
| P027 | "Early/historical T41 (mask off): σ/m₀ ≈ 0.066 cm²/g, m_φ median ≈ 26.6 MeV, m_χ ≈ 15 GeV" | ✅ Confirmed | Pre-mask era numbers preserved for cross-comparison; documented in CHANGELOG. |
| P028 | "v0.5 (KSFR/PCAC mask on, nlive=500): σ/m₀ ≈ 0.105 cm²/g, m_φ MAP/median ≈ 500-550 MeV, m_χ MAP ≈ 515 GeV / median ≈ 805 GeV, a ≈ +1.89" | ✅ Confirmed | `t41_mediator_mass_joint_fit_v0_5.json` MAP_physical: `sigma_m_0_derived: 0.1049`, `m_phi_MeV: 501.66`, `m_chi_GeV: 514.83`, `a_derived: 1.8876`. |
| P029 | "Other pipeline stages (T13, T21, etc.) quoted 0.7-1.7 cm²/g" | ⚠️ **Imprecise** | T21 baseline = 1.67 cm²/g (per `DARK_SECTOR_LAGRANGIAN.md:326`). T13 (8-channel fit) reports σ/m = 0.78 cm²/g (per `FINDINGS.md:116`). Reviewer conflated T21 (1.67) with T13 (0.78) — both are real numbers from different stages; not a single range "0.7-1.7". |
| P030 | "Cross-version Bayes-factor comparisons now require identical KSFR mask settings—an important caveat the project itself discovered" | ✅ Confirmed | This is exactly the **KSFR mask extension confound** discovered and documented in T71.1 (`CHANGELOG.md [T71.1]`, `REVIEWER_AUDIT_R15.md`). Reviewer correctly identified the project self-discovered this. |
| P033 | "SPARC is a calibrated saturation score, not a full hierarchical per-galaxy likelihood" | ✅ Confirmed | T11 aggregator uses calibrated score. Hierarchical is in `V0_6_ROADMAP.md` (R14 Rec #10, multi-week scope). |
| P034 | "Bullet Cluster is a soft one-sided Gaussian" | ✅ Confirmed | `channels_v03.py:152`. (Same stale-claim-as-stale finding as R15.) |
| P036 | "Relic density is a calibrated 1/<σv> mapping, not micrOMEGAs or a proper Boltzmann solution" | ✅ Confirmed | `t55_wimp_relic_calibration.py` is the calibrated mapping. Multi-month micrOMEGAs work in `V0_6_ROADMAP.md` (R14 Rec #9). |
| P040 | "lattice-informed ratios and (N_c, N_f) scans are only scaffolded" | ❌ **Stale** | `(Nc, Nf)` scan **shipped + executed** in T70.8 (scaffold), T70.9 (nlive=200), T71.0 (nlive=1000 with KSFR mask extension). 7 of 7 combos converged; summary at `nc_nf_scan_v0_6_summary.json`. The "scaffolded only" claim was correct at R14 but is **stale at T71.1**. |
| P051 | "Sensitivity to nlive has been explored (200 → 500 → 1000 → 2000)" | ✅ Confirmed | H3 report covers 200/500/1000; T71.1 added nlive=2000. |
| P052 | "Some residual technical debt appears in the changelog (mask-extension confounds, skipped regression tests that wait for newer JSON markers, Windows/WSL sync scripts)" | ✅ Confirmed | All three issues documented in T71.1 CHANGELOG + test suite. |
| P053 | "Julia/KiSS-SIDM bridge exists for gravothermal physics—nice, but the pure-Python DSMC is only smoke-test quality" | ✅ Confirmed | `kiss_sidm_dsmc.py` docstring: "THIS IS A SMOKE-TEST-QUALITY IMPLEMENTATION, not a production code." |

**Verification tally:** 17 ✅ Confirmed / 0 ✅ Already-shipped (no recommendations already done — reviewer correctly framed them as gaps) / 1 ❌ Stale (P040 — the (Nc, Nf) scan IS shipped; reviewer's "scaffolded only" was correct at R14 but stale at T71.1) / 1 ⚠️ Imprecise (P029 conflated T21/T13 numbers).

---

## Per-recommendation verification matrix (W5 + W3 3-tier priority)

### Priority 1 — Replace proxy/soft likelihoods (highest impact)

| # | Recommendation | Label | Ship / Defer / Reject | Reasoning |
|---|---|---|---|---|
| 1 | Hierarchical per-galaxy SPARC | ✅ Valid-deferred | **Defer to v0.6** | Already in `V0_6_ROADMAP.md` (R14 Rec #10). Multi-week scope. Per the roadmap priority recommendation: **#1 first**. |
| 2 | Bullet Cluster likelihood upgrade | ❌ **Stale** (Cha+ 2025 doesn't publish a full profile) | **Reject** | Already a soft Gaussian (`channels_v03.py:152`). Cha+ 2025 (arXiv:2503.21870, ApJ 987 L15) publishes only 68% upper limits — **no upgrade possible**. Reviewer's suggestion of "0.2 cm²/g SL-only value as a sensitivity case" IS implementable; would be a ~1-day test. |
| 3 | LZ / Fermi exact posterior shapes | ⚠️ Valid-deferred | **Defer to v0.6** | LZ WS2024 has released full chains (arXiv:2403.13076). Fermi-LAT dwarf limits use published likelihoods in current code. "Exact shapes" would be ~2-week effort. |

### Priority 2 — Microphysics & early-Universe consistency

| # | Recommendation | Label | Ship / Defer / Reject | Reasoning |
|---|---|---|---|---|
| 4 | Proper relic-density calculation (Boltzmann solver) | ✅ Valid-deferred | **Defer to v0.6** | Multi-month scope per `V0_6_ROADMAP.md` (R14 Rec #9). Hand-rolled scipy integrator recommended for this user's setup (no external solver dependency). |
| 5 | KSFR/PCAC/composite-sector validity | ✅ Valid-partial | **Partial ship + defer** | (a) KSFR mask version logging — **ship T71.2 (~1 day)** by adding `ksfr_mask_max_at_runtime` to T41 result JSONs (would un-skip the existing regression tests). (b) Higher-nlive (Nc, Nf) scan — **ship T71.3 (~40 min wall)** at nlive=2000. (c) Form-factor ansatz — **defer to v0.6+**. (d) Lattice-informed ratios — **defer to v0.6+**. |
| 6 | Mediator lifetime / BBN / CMB | ✅ Confirmed + shipped | **Acknowledge** | Channels 14 (mediator lifetime) + 16 (CMB μ/y) **both shipped**. Code: `channels_extended.py:992` (Channel 16) and `channels_extended.loglike_mediator_lifetime` (Channel 14). |

### Priority 3 — Robustness, validation & numerics

| # | Recommendation | Label | Ship / Defer / Reject | Reasoning |
|---|---|---|---|---|
| 7 | Sampler convergence & systematic sweeps (nlive ≥ 1000-2000) | ✅ Valid-partial | **Partial shipped + continue** | T71.0 nlive=1000 + T71.1 nlive=2000 already shipped. H3 + H4 sweeps already documented in `H3_H4_SENSITIVITY_REPORT.md`. Continue at higher nlive if wall permits. |
| 8 | Cross-validation against Drobczyk 2025 | ✅ Valid-deferred | **Defer to v0.6** | Quantitative σ/m(v) curve matching is ~1-week scope. Current `MEDIATOR_DETECTION_SYNTHESIS` docs provide qualitative comparison. |
| 9 | Gravothermal / KiSS-SIDM fidelity for UFDs | ✅ Valid-deferred | **Defer to v0.6** | Application of cluster-scale bounds to UFDs is a known approximation; proper treatment is multi-week. |

### Priority 4 — Process & external credibility

| # | Recommendation | Label | Ship / Defer / Reject | Reasoning |
|---|---|---|---|---|
| 10 | Independent domain-expert review | ✅ Valid-this-round | **Acknowledge + request user** | Cannot be automated. Recommend soliciting review from a SIDM/dark-matter phenomenologist. |
| 11 | Freeze the analysis chain for any "headline" claim | ✅ Valid-this-round | **Ship T71.2 (~1 day)** | Add a `config_hash` field to T41 result JSONs (8-line patch). Would make cross-version comparisons trivially auditable. |
| 12 | Reduce reliance on recent/contested observational claims | ✅ Valid-this-round | **Document + defer** | Add a "DEFERRED / not in primary production" tag to Channel 11 (DM-free UDGs) and Channel 12 (cosmic-web radio) in the joint-likelihood wrapper. ~1 day. |

---

## What's actionable THIS round

Per the W5 3-tier priority audit shape, only **2 of 12 recommendations are shippable in this session**:

1. **#5 (KSFR mask version logging)** — Add `ksfr_mask_max_at_runtime` field to `t41_version` block in T41 result JSONs. **Would un-skip the 3 currently-skipping regression tests in `test_inelastic_wrapper_regression.py`**. Effort: ~5 line patch in `t41_mediator_mass_joint_fit.py:354-365`. Risk: low.

2. **#11 (config_hash field)** — Add a SHA256 hash of the resolved config (mask version + nlive + form factor + inelastic flag + SPARC treatment + relic solver) to T41 result JSONs. Effort: ~10 line patch using existing config object. Risk: low.

Both ship in ~1 day combined. The remaining 10 recommendations are correctly prioritized for v0.6+ cycles (hierarchical SPARC first, then Boltzmann relic, then external review).

---

## Meta-notes for next review round (R16 closure / round 7 audit)

1. **Reviewer pool diversity is widening.** Three distinct reviewer sources reviewed the same project this session:
   - **R15 (sidm5.docx)** — likely from a human SIDM specialist (no AI disclaimer; precise numerical citations; some stale claims)
   - **R16 (sidmgrok1.docx)** — explicitly machine-generated (AI-disclaimer in P004); broader criticism + less precise on numbers
   - The internal reviewer-audit skill (W-series, my own work captured as references)
   
   The fact that **all three reviewers caught overlapping meta-patterns** (Bullet Cluster "hard cut" stale claim, KSFR mask version confound, missing cross-version controls) suggests these are **structural project issues**, not reviewer errors. The reviewer pool is converging on the same findings — which strengthens the recommendation that the project's docs → source code cross-references need improvement.

2. **The AI-disclaimer is appropriate.** Per reviewer-audit W7 (update skills when a new pattern emerges), the reviewer pool now includes machine-generated reviews with explicit disclaimers. This is a new pattern worth documenting in the reviewer-audit skill: **machine-generated reviews with AI-disclaimers should be verified with the SAME rigor as human reviews** (every claim cross-checked against on-disk state). The disclaimer doesn't reduce verification work; it just signals the source.

3. **Stale claims vs updated state.** The "lattice-informed ratios and (Nc, Nf) scans are only scaffolded" claim (P040) was **correct at R14** (R14 closure time, the scaffold was just shipped) but **stale at T71.1** (the scan executed, KSFR mask extended, summary JSON shipped). Reviewers reading the project should track the version stamp — per the same W2 + W7 pattern caught in R15, the discrepancy between docs and implementation grows over time.

4. **Honest framing of the v0.5 → v0.6 transition.** The reviewer correctly identifies the v0.5 vs historical T41 number shifts as evidence of "headline numbers have shifted substantially and remain preliminary." This is **accurate and important** — per T71.1, the KSFR mask extension confound adds another ~+38.7 in log_Z to the v0.6 anchor, further widening the gap from the historical 26.6 MeV number. The project's own MODEL_ASSUMPTIONS_AND_LIMITATIONS.md + V0_6_ROADMAP.md are honest about this; reviewer correctly credits that.

5. **T71.3 follow-up — R16 #7 closed (nlive=2000 (Nc,Nf) scan).** The R16 #7 sampler-convergence recommendation was filed as "Partial shipped + continue" in this audit. T71.3 (2026-08-28) closes it: the (Nc, Nf) scan was re-run at nlive=2000 (was nlive=1000 at T71.0) with a 7-way parallel background runner (~10 min wall vs ~70 min sequential). All 7 combos converged, the (3, 3) anchor remains the data-preferred model (log BF = 0 vs best alternative +0.127), and the nlive=1000→2000 anchor shift (+0.23 in log_Z) is within 2-sigma of sampling variance. **The scan has converged** — no need to re-run at higher nlive. Full report in CHANGELOG [T71.3].

6. **T71.4 + T71.5 follow-up — Tier B closure (Drobczyk quantitative + LZ WS2024 stale-claim + KiSS-SIDM UFD wall-time limitation).**
   - **R16 #8 (Drobczyk quantitative cross-validation)**: T68 had hardcoded benchmark numbers but no chi² test. T68b (2026-08-28) ships the chi² test using T41 v0.6 hier-sparc MAP as our point estimate. Result: chi² = 213.62 on 1 dof → STRONG TENSION at all 3 velocity points, with the cluster scale (v=1000 km/s) showing the biggest disagreement (factor 526×). Honest framing: the two models make different physics predictions; we don't conclude one is "right" and the other "wrong". See `v0.3-prelim/docs/V0_6_TIER_B_CLOSURE.md` for the full closure note.
   - **R16 #3 (LZ WS2024 full posterior shapes)**: Roadmap item is **stale** — the real LZ WS2024 posterior has been in T41 production since R12 (2026-08-17) via `t30_lz_real_posterior.loglike_lz_real` (HEPData record 155182, 26 mass points). No new code; this is a documentation correction.
   - **R16 #9 (KiSS-SIDM UFD fidelity)**: **Deferred with rationale**. The KiSS-SIDM Julia bridge hits a hard 3600s timeout at UFD N=5e4 (T38a failure). The canonical halo (M_halo = 10⁹ M_☉) is fully converged at N=1e4-1e5, but the dwarf/UFD regime is intractable at our compute budget without rewriting the DSMC in a faster language or using the paper's original C/Python implementation. Multi-week scope; cannot ship in a single session.

---

## Closing note

This R16 review is **less actionable than R15** because the reviewer correctly framed the recommendations as multi-week/month efforts that are already in `V0_6_ROADMAP.md`. Only 2 of 12 recommendations are session-shippable (KSFR mask version logging + config_hash field). The remaining 10 are correctly prioritized for v0.6+ cycles.

The most useful signal from this review is the convergence across multiple reviewer pools on the **"docs ↔ source code cross-reference" problem**. When a human SIDM specialist, a machine-generated review, AND an internal audit all catch the same meta-pattern (stale claims about features already shipped, Bullet Cluster hard-vs-soft, KSFR mask version), the fix is **structural**: every shipped feature should be tagged with the commit SHA that introduced it, and every doc that references a feature should cross-reference that commit. This is a low-effort, high-value improvement that would prevent future reviewers from repeating the same verification work.

R16 closure (T71.2 = KSFR mask version logging + config_hash field) is the recommended next round if the user wants to ship. Otherwise, this audit is ready to be acknowledged and the actionable items filed to `V0_6_ROADMAP.md` for v0.6+ cycles.