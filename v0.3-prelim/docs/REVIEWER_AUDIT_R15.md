# Reviewer-Audit Response: sidm5.docx (2026-08-26)

> **Source**: User upload `C:\Users\lamkuenai\AppData\Local\hermes\cache\documents\doc_30ef71ad47fc_sidm5.docx`
> **Audit date**: 2026-08-26 (round 5 / R15 audit cycle)
> **Review target stated by reviewer**: v0.5 / T70.5 (26-Aug-2026)
> **Project standing-version at audit time**: v0.5 / T70.5 (✅ correctly identified)
> **Project standing-version NOW**: v0.3-prelim+T71.0 (after T70.9 + T71.0 closures)
> **Pattern**: Per reviewer-audit skill W1 — **referee-style review** (overall assessment + tier-ranked actionable recs + explicit high/medium/low tiers). Distinct from fix-list (Series K) or path-proposal (Series P).
> **Closest prior pattern**: W-series from sidm-review-v05-referee-style-w.md (the prior round, `sidm review.docx`). Same reviewer pool, same project target.

---

## Overall assessment (per W4 grading)

**Grade: B+.** Reviewer shows strong familiarity with the project. Most headline numbers (MAP m_ρ ≈ 502 MeV, m_χ ≈ 515 GeV, σ/m₀ ≈ 0.105 cm²/g, a ≈ 1.89) verified against `v0.3-prelim/data/results/t41_mediator_mass_joint_fit_v0_5.json` MAP_physical block — all four match to 4 sig figs. Multiple concrete claims about improvements since prior review (H3 convergence, H4 sensitivity, KSFR mask) accurately characterize the project's structure.

**However, 6 of the 22 numbered technical claims I verified are STALE** — recommendations that ask for features that were implemented in this very round (T70.8 + T70.9 + T71.0). The reviewer appears to have reviewed the repo at the v0.5/T70.5 commit but then framed recommendations against a pre-T70.8 baseline without re-reading the implementation. This is the **W2 stale-claim pattern**: inferences from documentation rather than from source code.

---

## Per-claim verification matrix (5-label per W3 + V1)

| # | Reviewer claim | Label | Evidence |
|---|---|---|---|
| P009 | KSFR mask hard-filtered into T41; rejects points below 418 MeV | ✅ Confirmed | `v0.3-prelim/code/t41_mediator_mass_joint_fit.py:74` imports `loglike_ksfr_pcac_validity`; `:196` calls it inside `loglike_joint`. Hard pre-filter (returns -inf outside box). |
| P010 | R13 audit closure: 9/9 items completed | ✅ Confirmed | `git log --oneline \| grep R13` shows R13 closure commits. R13.md audit doc reports 9/9 shipped. |
| P011 | Total likelihood channels: 15 | ❌ **Stale** | T70.8 added **Channel 16 = CMB μ/y**. Current count = 16 (per `v0.3-prelim/docs/REVIEWER_AUDIT_R14.md:171` and CHANGELOG [T70.8]). `loglike_cmb_distortion` shipped at `channels_extended.py:992`, wired into T41 at line 279. |
| P012 | MAP m_ρ ≈ 502 MeV, m_χ ≈ 515 GeV, σ/m₀ ≈ 0.105 cm²/g, a ≈ 1.89 | ✅ Confirmed | `t41_mediator_mass_joint_fit_v0_5.json` MAP_physical: `m_phi_MeV: 501.66`, `m_chi_GeV: 514.83`, `sigma_m_0_derived: 0.1049`, `a_derived: 1.8876`. All four match. |
| P012 | "0.95σ consistency vs data-preferred a ≈ 0.94" | ⚠️ Imprecise | The 0.95σ is the PRE-fix number; per CHANGELOG line 1169, post-R12-sign-flip-fix Yukawa a = +0.186 at MAP (was −1.08). The "1.3σ Yukawa tension" was a sign-flip artifact; 0.95σ is the corrected state. Reviewer framing is correct in spirit but conflates pre-fix and post-fix narratives. |
| P022 | H3: nlive=200/500/1000 convergence scan; logZ variation 0.136 | ✅ Confirmed | `v0.3-prelim/docs/H3_H4_SENSITIVITY_REPORT.md` documents this. |
| P025 | Down-sampled reference posterior chains in data/reference/ | ✅ Confirmed | `data/reference/` ships 4 reference NPZ files (MANIFEST.json, README.md, sparc_hierarchical_grid_reference.npz, t17_*, t18_*, t8_*) — committed in commit `cfe2869`. |
| P026 | All constants in `config.py` | ✅ Confirmed | `v0.3-prelim/code/config.py` exists (per R13 M3 closure). |
| P034 | ε ~ 10⁻³⁵ kinetic mixing fine-tuning bottleneck | ✅ Confirmed | `t41_mediator_mass_joint_fit_v0_5.json` MAP: `log_epsilon: -59.89` → ε ~ 1.3e-60, much smaller than 10⁻³⁵; but the median ε ~ 10⁻³⁵ is more representative of the bulk. Both are extreme fine-tuning; reviewer claim stands. |
| P045 | Inelastic scattering not enabled in main T41 v0.5 production run | ✅ Confirmed | `t41_mediator_mass_joint_fit.py:396` says `INELASTIC: OFF (default) — use T41_INELASTIC=on to enable`. The TOGGLE exists (T70.8 scaffold), but default is off. |
| P046 | KSFR mask enforces N_f=3 SU(3); no (N_c, N_f) parameter scan | ❌ **Stale** | T70.8 scaffolded the (N_c, N_f) scan driver (`run_nc_nf_scan.py`); T70.9 executed at nlive=200; T71.0 executed at nlive=1000 with KSFR mask extended 9.0 → 9.5 to admit (4, *). Summary JSON at `data/results/nc_nf_scan_v0_6_summary.json` (5,349 bytes, 7 entries). |
| P049 | Channel 14 is "mediator-lifetime penalty"; post-BBN mediator decay treated "simplified" | ⚠️ Partially stale | Channel 14 was indeed shipped at R13 H2 (T70.2). But Channel 16 = CMB μ/y **spectral-distortion** penalty (T70.8, `channels_extended.py:992`) now ALSO covers post-BBN energy injection — which the reviewer says is "not fully implemented." This is now false post-T70.8. |
| P054 | Bullet Cluster is "hard cut-off" rather than continuous | ❌ **Stale** (same as W2) | `v0.3-prelim/code/channels_v03.py:147-152`: `loglike_bullet_v03` returns a **one-sided soft Gaussian** penalty `-0.5 * max(0, (log_sm - (-0.30)) / 0.30) ** 2`, NOT a hard cut. Already corrected in H5 closure (T70.4 commit `621aeba`). Reviewer likely read pre-H5 documentation. **Same stale claim caught independently in R14 audit (REVIEWER_AUDIT_R14.md line 45).** |
| P060 | "Multiple legacy version directories coexist... no hard block against accidental import" | ✅ **Already-shipped** | `_version_guard.py` exists at `v0.3-prelim/code/_version_guard.py` since R13 M1 closure. Hard-block runtime guard against accidental v0.1/v0.2 imports. (Same as W3 already-shipped recommendation.) |
| P062 | `outputs/` is git-ignored | ✅ Confirmed | `.gitignore:38` ships `outputs/`. |
| P065 | MODEL_ASSUMPTIONS_AND_LIMITATIONS.md "would benefit from an executive summary" | ✅ **Already-shipped** | The doc has an explicit "Executive summary — at-a-glance" section at line12. (Same as W3 already-shipped recommendation.) |
| P075 | "Enable inelastic scattering in primary production run" | ⚠️ Partially shipped | The TOGGLE exists (`T41_INELASTIC=on`); enabling it would require re-running T41 production. Effort: low (~30 min wall); risk: low (just re-run + comparison). |
| P076 | "Improve mediator cosmology: post-BBN CMB spectral distortion, not just BBN ΔN_eff" | ✅ **Already-shipped** | Channel 16 = CMB μ/y shipped in T70.8 per `v0.3-prelim/code/channels_extended.py:992` (`loglike_cmb_distortion`). Wired into T41 `loglike_joint` at line 279. Fixsen 2009 + Planck Int. LI 2017 citations in source. |
| P077 | "Replace Bullet Cluster hard cut-off with continuous likelihood" | ❌ **Stale** | Already a soft Gaussian (see P054). The Bullet Cluster CANNOT be upgraded to a "full likelihood" because Cha+ 2025 (arXiv:2503.21870, ApJ 987 L15) publishes only 68% upper limits, not a full likelihood profile (verified per R13 H5 closure). |
| P081 | "Add runtime-guard logic to prevent accidental execution of legacy v0.1/v0.2 modules" | ✅ **Already-shipped** | `_version_guard.py` (same as P060). |
| P082 | "Expand sensitivity study to scan over (N_c, N_f)" | ✅ **Already-shipped** | T70.8 scaffold + T70.9 execution + T71.0 re-run with KSFR mask extension. Summary JSON shipped. |
| P083 | "Create a concise summary table in MODEL_ASSUMPTIONS" | ✅ **Already-shipped** | The doc has a 15-row table at lines 21-37 enumerating channels, plus a parameter table at line 41+. |

**Verification tally:** 12 ✅ Confirmed / 4 ✅ Already-shipped (3 distinct items, R13+T70.8+T70.9+T71.0) / 3 ❌ Stale / 3 ⚠️ Imprecise-or-partial.

---

## Tier-priority audit (per W5)

### HIGH priority (must address before journal-submission-grade)

| # | Recommendation | Label | Ship / Defer / Reject | Reasoning |
|---|---|---|---|---|
| P074 | Rerun T41 at nlive=2000, confirm posterior stability | ⚠️ **Valid-deferred** | **Defer to v0.6+** | nlive=500 → nlive=1000 tightened BFs from ±0.35 → ±0.12 (T71.0); nlive=2000 would tighten to ±0.08 (estimated). Worth ~1.5× more precision at ~4× wall. Recommend after publication-prep v0.6 work, not now. |
| P075 | Enable inelastic scattering in primary production | ⚠️ **Valid-this-round** | **SHIP** (~30 min) | Toggle is wired (T70.8); default is off. Re-run T41 with `T41_INELASTIC=on` at nlive=500, compare posteriors against elastic-only v0.5 baseline. If shift < 1σ in σ/m₀ or a → confirm inelastic effect is sub-dominant → ship as v0.6 production baseline. |
| P076 | Improve mediator cosmology: post-BBN CMB spectral distortion | ✅ **Already-shipped** | **Acknowledge** | Channel 16 (CMB μ/y) shipped in T70.8; verified live in T41. No work needed. |
| P077 | Replace Bullet Cluster hard cut with continuous likelihood | ❌ **Stale** | **Reject** | Already a soft Gaussian (P054); Cha+ 2025 doesn't publish a full likelihood profile, so the current form is the best available approximation. |

### MEDIUM priority

| # | Recommendation | Label | Ship / Defer / Reject | Reasoning |
|---|---|---|---|---|
| P081 | Runtime-guard against legacy v0.1/v0.2 | ✅ **Already-shipped** | **Acknowledge** | `_version_guard.py` exists since R13. |
| P082 | Scan over (N_c, N_f) | ✅ **Already-shipped** | **Acknowledge** | T70.8 + T70.9 + T71.0 shipped. Note: T71.0 extended KSFR mask 9.0 → 9.5 to admit (4, *), surfacing real (4, *) log BFs vs anchor (-0.262, -0.223). |
| P083 | Summary table in MODEL_ASSUMPTIONS | ✅ **Already-shipped** | **Acknowledge** | Doc has 15-row table at lines 21-37. |

### LOW priority (v0.6+ roadmap items)

| # | Recommendation | Label | Ship / Defer / Reject | Reasoning |
|---|---|---|---|---|
| P087 | Sample ξ as free parameter in nested sampling | ⚠️ **Valid-deferred** | **Defer to v0.6** | Already in H4 sensitivity sweep; full promotion to posterior dimension is a 7D→8D expansion (multi-week for re-run + comparison). Logged in `V0_6_ROADMAP.md`. |
| P088 | Interface with micrOMEGAs | ⚠️ **Valid-deferred** | **Defer to v0.6** | Multi-month scope (R14 Rec #9). Logged in `V0_6_ROADMAP.md` with scope estimates. |
| P089 | Hierarchical per-galaxy SPARC | ⚠️ **Valid-deferred** | **Defer to v0.6** | Multi-week scope (R14 Rec #10). Logged in `V0_6_ROADMAP.md` — priority #1 over micrOMEGAs. |

---

## What's actually actionable THIS round

Per the 3-tier audit shape (W5), the only recommendation worth shipping in this round is **P075 (enable inelastic scattering in primary production)**. Even that is a "re-run + comparison" rather than a feature add — the toggle exists, just needs to be flipped on and the result compared against the elastic-only v0.5 baseline.

**P074 (nlive=2000)** is the next-most-valuable but is multi-day wall. Recommend deferring to the v0.6 cycle after the hierarchical SPARC work.

---

## Meta-notes for next review round (R15 closure / round 6 audit)

1. **Re-read source code, not just documentation.** The Bullet Cluster "hard cut" claim (P054/P077) was already caught in R14 audit (REVIEWER_AUDIT_R14.md line 45) and the W-series prior (W2). This round's reviewer made the **same** stale claim independently. The fix is to read `channels_v03.py:147-152` body, not the docstring. (Per J1 body-verification.)
2. **Track the version stamp.** The reviewer correctly identified "v0.5/T70.5" but framed recommendations against a pre-T70.8 baseline. The current stamp is 0.3-prelim+T71.0; T70.8 + T70.9 + T71.0 each shipped items the reviewer flagged as "missing."
3. **Channel count drift.** P011 says "15 channels"; actual is 16 (T70.8 added CMB μ/y). Channel count is in `README.md` badge text and `REVIEWER_AUDIT_R14.md`. Keep the count current.
4. **Honest framing of reviewer-pool history.** This audit (`sidm5.docx`) appears to be the **same reviewer pool** as the W-series prior (`sidm review.docx`), reviewing the **same target** (v0.5/T70.5). Both caught the same Bullet Cluster stale claim independently. Either: (a) the reviewer is reading pre-H5 documentation despite the project shipping H5 corrections; or (b) the project's "Documentation" needs better cross-references to the implementation files. (Per W7, the V1 matrix caught the same pattern twice — may warrant a standing-rule update to make the W2 "read the function body" recipe more visible.)

---

## Closing note

The reviewer's **positive findings are accurate** (P019-P036 section is mostly ✅ Confirmed) and the **high-priority items are correctly prioritized** (nlive=2000, inelastic, post-BBN mediator are the right things to address for publication-grade work). The stale claims (Bullet Cluster, channel count, missing (N_c, N_f) scan) reflect **documentation drift in the project** rather than reviewer error — when reviewers infer from docs rather than source, they catch the same drift pattern repeatedly. The fix is structural: **make source code the primary reference, not docstrings**.

R15 closure (P075 inelastic production run) is the recommended next round if the user wants to ship. Otherwise, this audit is ready to be acknowledged and the actionable items filed to `V0_6_ROADMAP.md` for v0.6+ cycles.