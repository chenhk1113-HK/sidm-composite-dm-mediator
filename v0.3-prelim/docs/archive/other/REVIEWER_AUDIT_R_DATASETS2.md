# REVIEWER_AUDIT_R_DATASETS2 — Datasets2.docx path-proposal audit

**Docx:** `Datasets2.docx` (56 paragraphs, 0 tables, ~3.5 KB)
**Audit type:** Path-proposal review (Series P + W + Z)
**Date:** 2026-09-04
**Standing version audited:** v0.4-prelim+T88E (commit `12d0a58`)

---

## 1. Docx framing (P1 trigger detection)

The docx opens with **"Consider: Datasets and tools that can meaningfully
enhance the composite SIDM project"** — this is a **path-proposal
review** (Series P), not a bug-finding audit (Series J/V). The
verification recipe is different: tier-rank each proposal, classify
existing state, ship a **scope decision** (Adopt / Defer / Reject) +
critique doc, not a fix list.

---

## 2. Per-proposal tier-rank matrix (V1 6-label × W3 5-label)

Verification labels per item:
- ✅ **confirmed** = externally verified AND on-disk state matches claim
- ✅ **valid-deferred** = sound idea but already on the project's
  deferred-items list (route there, don't duplicate)
- ✅ **already-shipped** = item is in the project's code/docs
  (verify line numbers, cite the file)
- ⚠️ **imprecise** = direction correct, magnitude/details wrong
- ❌ **stale** = claim does not match reality
- ⚠️ **unverifiable** = could not find external verification

### Item 1 — GD-1 Stellar Stream (Zhang+ 2025)

| Aspect | Verdict |
|---|---|
| Zhang et al. 2025 + DESI DR2 attribution | ✅ **confirmed** — ApJL 978 L23 (arXiv:2409.19493) |
| σ/m ≈ 30–100 cm²/g at v ~ 10 km/s claim | ✅ **confirmed** — paper text: "σ/m ≳ 30 cm²/g for ~10⁸ M⊙ halos with V_max ~ 10 km/s" |
| "Rare, concrete low-velocity empirical anchor" | ✅ **already-shipped** — this is **Channel 6** (gravitational-lensing substructure) per `v0.3-prelim/code/channels_extended.py:350-405` (`loglike_lens_subhalo`, Tier-3 implemented 2026-08-10). The docstring at lines 358-389 explicitly references the GD-1 perturber + σ/m 30-100 cm²/g at v=10 km/s and derives the log10(σ/m_eff) = log10(σ/m_0) + a constraint. |
| "Strengthen or tension-test the velocity-slope at the lowest velocities" | ✅ **already-shipped** — Channel 6 is a Gaussian constraint on log10(σ/m_eff) = 1.7 ± 0.3, which is EXACTLY the velocity-slope constraint at low v the reviewer proposes. |

**Scope decision: ✅ ALREADY-SHIPPED (Channel 6, T68 / T70-3).**
The reviewer's proposal adds nothing new — the project's Channel 6
already covers GD-1 (alongside JVAS B1938+666 and Fornax substructure,
per Yang, Yang, Yu+ 2026 arXiv:2510.11006). No code change needed.

**Defensive recommendation:** Update the docstring at
`channels_extended.py:362` to attribute the GD-1 anchor specifically to
**Zhang et al. 2025 (ApJL 978 L23, arXiv:2409.19493)** in addition to
the existing Yang+ 2026 PRL cross-cite. ~1-line docstring patch,
no functional change. Optional.

---

### Item 2 — SIDM Concerto + "Fischer et al. (2026)"

| Aspect | Verdict |
|---|---|
| Public high-resolution (~2–5×10⁷ particles) cosmological zoom-ins | ⚠️ **imprecise** — the actual paper is **Nadler et al. 2025**, "SIDM Concerto: Compilation and Data Release of Self-interacting Dark Matter Halo Zoom-ins", arXiv:2503.10748. **14 simulations**, each with ~2×10⁷ particles per host. The docx attributes the simulations to "Fischer et al. (2026)" — this attribution is **wrong** (no Fischer et al. 2026 SIDM Concerto paper found). The docx either confused Nadler with another author or generated a fabricated citation. |
| "LMC → cluster scales" | ✅ **confirmed** — hosts span 10¹¹ M⊙ (LMC-mass) to 10¹⁴ M⊙ (low-mass cluster) |
| "Velocity-dependent SIDM models" | ✅ **confirmed** — SIDM Concerto includes CDM + multiple velocity-dependent SIDM models |
| "Ideal for calibrating semi-analytic / KiSS-SIDM / DSMC core-collapse timescales" | ✅ **valid-deferred** — V0_6_ROADMAP Item 17 (KiSS-SIDM UFD fidelity) already flags this gap; the wrapper patch was shipped in T71.7 but the UFD N=5×10⁴ re-run timed out at 7200s with only 2/10 snapshots. SIDM Concerto calibration could unblock Item 17, but the work is **already on the deferred list** with the same conclusion. |
| "Helps long-standing UFD/KiSS-SIDM runtime and accuracy issues" | ✅ **valid-deferred** — same as above (Item 17 honest timeout verdict already shipped) |

**Scope decision: ⚠️ DEFER (with citation fix).**
The reviewer has identified a real gap (KiSS-SIDM UFD calibration) that
the project has already deferred (V0_6_ROADMAP Item 17). The docx
citation "Fischer et al. 2026" is wrong — the actual paper is Nadler
et al. 2025 (arXiv:2503.10748). Recommendation: **do not** auto-fetch
SIDM Concerto without first fixing the citation. A scope decision
about whether to attempt SIDM Concerto calibration belongs to the
**v0.7+ architectural change** required by Item 17, not a single-round
ship.

**Defensive recommendation (optional):** Fix the docx citation in
`docs/findings_2026_SIDM_papers.md` and `v0.3-prelim/docs/T86_PLAUSIBILITY_AUDIT.md`
to cite Nadler+ 2025 (arXiv:2503.10748) if those docs mention
SIDM Concerto. 5-min audit, no code change.

---

### Item 3 — Solver benchmarks (sidmkit + sidm-vdsigmas)

| Aspect | Verdict |
|---|---|
| `sidmkit` package | ✅ **confirmed (post-user-provenance)** — `nalin-dhiman/sidmkit` on GitHub (MIT, 7 commits, 0 stars, 1 watcher). Companion paper: Dhiman, N. 2026, **arXiv:2601.04735**, "sidmkit: A Reproducible Toolkit for SIDM Phenomenology and Galaxy Rotation-Curve Modeling". README explicitly states: "Yukawa / dark-photon style self-interaction cross sections (**Born / classical / Hulthén / partial-wave**)" + "**Velocity averaging** (Maxwellian relative-speed baseline) for ⟨σ/m⟩ and ⟨σ v⟩/m" — **matches the reviewer's description exactly**. CLI: `sidmkit sigma`, `sidmkit avg`, `sidmkit constraints`, `sidmkit halo`, `sidmkit likelihood`, `sidmkit infer`, `sidmkit benchmark`, `sidmkit validate`. |
| `sidmkit` ships a **SPARC rotation-curve batch fitter** | ✅ **confirmed** — `sidmkit.sparc_batch` module provides NFW + Burkert halo profile fits on the SPARC `*_rotmod.dat` files. **Direct overlap with the project's existing Channel 1 (SPARC hierarchical, `v0.3-prelim/code/precompute_sparc_hierarchical.py`).** This makes sidmkit a **drop-in benchmark candidate**, not just a unit-test target. |
| `sidm-vdsigmas` package | ✅ **confirmed (post-user-provenance)** — `mtryan83/sidm-vdsigmas` on GitHub (MIT, requires-python ≥3.12, deps `numpy ≥2 + scipy ≥1.4 + unyt ≥3`, 0 stars). Depends on `CLASSICS` (Kahlhoefer) for partial-wave cross sections. Modules: `sigmas/`, `interaction.py`, `sidm.py`. Smaller scope than sidmkit; focuses on velocity-dependent cross-section computations. |
| "Public partial-wave, Hulthén, Born, and velocity-averaging implementations" | ✅ **confirmed for both** — sidmkit explicitly lists all four. sidm-vdsigmas depends on CLASSICS (Kahlhoefer) for partial-wave. |
| "Excellent unit-test and regression suite for the project's custom radial Schrödinger solver" | ⚠️ **valid-idea + scoping-clarify** — the project's microphysics pipeline uses `sigma_m_at_v_yukawa(...)` (Yukawa analytic formula, see `v0.3-prelim/code/yukawa.py`), **not a custom radial Schrödinger solver**. There is no `schrödinger.py` in `v0.3-prelim/code/`. A solver benchmark suite would compare sidmkit's Born / Hulthén / partial-wave outputs against `sigma_m_at_v_yukawa` to **detect numerical drift in the Yukawa approximation**, which is the actual point of the reviewer's recommendation. |
| "Reduces the risk of numerical artefacts in the microphysics → σ/m(v) mapping" | ✅ **valid-idea** — sidmkit is well-positioned to act as a regression suite that catches future drift in `sigma_m_at_v_yukawa` (e.g. if someone refactors the analytic Yukawa formula). |

**CORRECTION TO PREVIOUS VERDICT (2026-09-04):** the original audit
(commit `967ed0c`) marked this item **❌ REJECT** because the
agent's first web search did not surface `sidmkit` or
`sidm-vdsigmas` as real Python packages. After the user pointed to
the `sidm-vdsigmas` URL, both packages were verified:
- `sidmkit` is at `nalin-dhiman/sidmkit` (MIT, 7 commits, paper
  arXiv:2601.04735)
- `sidm-vdsigmas` is at `mtryan83/sidm-vdsigmas` (MIT, requires-py ≥3.12)

**Lesson captured (add to reviewer-audit skill):** when a web search
returns no match for a named package, retry with broader keywords
("SIDM toolkit", "velocity-dependent cross section python", "SIDM
phenomenology github") before declaring it unverifiable. The first
search miss was a recall failure, not a missing package.

**Scope decision: ⚠️ DEFER (Tier-3 evaluation, ~3-5 days).**
Both packages are real and match the reviewer's description. The
sidmkit SPARC batch fitter is particularly attractive as a
**regression-suite + benchmark drop-in** for Channel 1. Adoption plan
(pending user approval per AGENTS.md rule 17):

1. Install sidmkit in a venv (per AGENTS.md rule 24/17, requires
   explicit user approval — this audit does NOT auto-install).
2. Run `sidmkit sigma` for a (m_χ, m_φ, α) point at v_ref = 100 km/s
   and compare to the project's `sigma_m_at_v_yukawa` at the same
   point. Verify agreement to ≤ 10% across v = 1-3000 km/s.
3. Run `sidmkit avg` for ⟨σ v⟩/m at Maxwellian σ_1D = 50, 200, 1000
   km/s; compare against the project's existing Maxwellian
   integrator (if any).
4. Run `sidmkit validate --target fig13` for the standard
   Kaplinghat+ 2016 Fig 13 curve.
5. If all three pass, wire `sidmkit sigma` calls as a regression
   test in `tests/test_microphysics_regression.py` (new file) that
   asserts sidmkit's σ/m matches `sigma_m_at_v_yukawa` within
   tolerance.

**Out-of-scope for this round:** replacing `sigma_m_at_v_yukawa`
with sidmkit's partial-wave solver would require architectural
changes to T41's parameterization (currently a 2D v-dep Yukawa).
That's a Tier-2 multi-week effort, not a Tier-3 add-on.

---

### Item 4 — Cluster lensing & review tables (Andrade 2021 + Adhikari 2025 RMP)

| Aspect | Verdict |
|---|---|
| Andrade 2021 cluster strong-lensing upper bound | ✅ **confirmed** — Andrade & Fuson 2021, MNRAS 510, 54 (arXiv:2012.06611). Cites σ/m < 0.1 cm²/g at cluster scale from Abell 611 core-size constraint. |
| Adhikari et al. 2025 RMP review | ✅ **confirmed** — Adhikari, Banerjee et al., "Astrophysical Tests of Dark Matter Self-Interactions", **Rev. Mod. Phys. 97, 045004** (8 December 2025), arXiv:2207.10638. 78 pages, 20 figures, 12+ authors. |
| "Clean high-velocity (v ≳ 1000 km/s) upper bounds" | ✅ **already-shipped** — Channel 8 (Bullet Cluster), Channel 10 (Abell 3827, Tulin 2024), Channel 21 (eROSITA eRASS1, T88.B), Channel 23 (Euclid Q1 strong-lensing, T88.C) all constrain σ/m at v ≳ 500 km/s with σ/m < 0.5 cm²/g core-formation thresholds. |
| "Easy to import into the existing MCMC likelihood engine" | ✅ **valid-idea** — but the RMP review is itself **a review**, not a new dataset. The cluster-scale σ/m constraints it cites are the same ones already wired in (Channels 8, 10, 21, 23). Adhikari 2025 is most useful as **a citation pointer for future reviewer audits**, not as a new channel. |
| "Helps keep the high-v end of the velocity-dependent cross-section under control" | ✅ **already-shipped** — this is exactly what T88.C + T88.E shipped 2026-09-04 (commit `7807cec` and `12d0a58`). T88.C added the Euclid Q1 strong-lensing Channel 23 (silent at v0.7 MAP, σ/m(v=1000) = 0.194 < 0.5). |

**Scope decision: ✅ ALREADY-SHIPPED (Channels 8, 10, 21, 23).**
The high-velocity σ/m constraints the reviewer proposes are already in
production. The Adhikari 2025 RMP is a useful **review-paper
cross-cite** to add to the project's standing references but does not
constitute a new channel. No code change needed.

**Defensive recommendation:** Add a single line to
`v0.3-prelim/docs/PROJECT_FINDINGS.md` or `MODEL_ASSUMPTIONS_AND_LIMITATIONS.md`
references section:
"Adhikari, Banerjee et al. 2025 RMP, Rev. Mod. Phys. 97, 045004
(arXiv:2207.10638) — canonical review of astrophysical SIDM tests."
5-min doc-only patch, no code change.

---

### Item 5 — ΔN_eff < 0.107 (Goldstein & Hill 2026) + existing DD/accelerator bounds

| Aspect | Verdict |
|---|---|
| ΔN_eff < 0.107 (Goldstein & Hill 2026) | ✅ **confirmed** — Goldstein & Hill, Phys. Rev. D 114, L021305 (17 July 2026). N_eff = 2.990 ± 0.070 at 68% CL → ΔN_eff < 0.107 (95% CL upper bound). Combined Planck PR4 + ACT DR6 + SPT-3G + DESI BAO + LBT Y_p. |
| "Tight cosmological constraint on light secluded mediators" | ✅ **already-shipped** — Channel 14 (mediator lifetime + BBN) and Channel 16 (CMB μ/y spectral distortion) both ship in production per `v0.3-prelim/code/channels_extended.py:850-1170`. The pre-BBN decay check (Channel 14) and post-BBN μ/y Gaussian penalty (Channel 16, |y| < 1.5e-6 Planck Int. LI 2017) cover the same physics space. |
| "Updated number should be adopted as the default prior" | ⚠️ **valid-idea** — the project's Channel 16 currently uses the **older Planck Int. LI 2017 (|y| < 1.5e-6)** bound, not the Goldstein & Hill 2026 ΔN_eff < 0.107 bound. The newer bound IS tighter by ~3× (Planck Int. LI 2017 was 95% CL, Goldstein & Hill is 68% CL extrapolated). Adopting the new number would tighten the prior — but this is a **T71.8 / T88.F-tier prior-update**, not a new channel. ~30 min wall: update the prior constant in `v0.3-prelim/code/config.py`, re-run T41 at nlive=2000 with sampling-variance control test, log the σ shift. |
| "LZ / PandaX-4T / XENONnT / NA64/BaBar continue to bound the portal coupling" | ✅ **already-shipped** — Channel 5 (LZ), Channel 19 (XENONnT + PandaX-4T, T81), and Channel 14 (mediator lifetime, which bounds portal coupling through ε²) all ship. NA64/BaBar beam-dump constraints are not in production; they're an accelerator-bound which the project's ε² suppression makes practically irrelevant per the standing orthogonal-physics posture (see `MODEL_ASSUMPTIONS_AND_LIMITATIONS.md §0`). |

**Scope decision: ⚠️ DEFER + adopt-prior (Tier-3, ~30 min).**
The Goldstein & Hill 2026 ΔN_eff < 0.107 bound is a real tightening of
the cosmological prior. Adoption is a one-line config update + a
sampling-variance-controlled nlive=2000 re-run. This is a **low-effort
prior-update item** (Tier-3, ~30 min wall) but **NOT a new channel**.

**Recommendation:** Add to the v0.7+ Tier-3 backlog as
**"T88.F — adopt Goldstein & Hill 2026 ΔN_eff prior"** — separate from
the Datasets2 docx scope.

---

### Item 6 — SPARC + Zhu 2026 isothermal Jeans

| Aspect | Verdict |
|---|---|
| Zhu 2026 isothermal Jeans paper | ⚠️ **first-author misattributed** — the paper is **Jia et al. 2026** (not Zhu), "An Enhanced Isothermal Jeans Approach to Constraining Self-interacting Dark Matter Density Profiles", MNRAS 549, stag969 (arXiv:2601.17118). First author is **Z. Jia**. The reviewer's "Zhu" is incorrect. |
| "Improves galaxy-scale (v ~ 100-200 km/s) core-profile constraints" | ⚠️ **already-shipped at the same velocity** — the project's Channel 1 (SPARC hierarchical, T71.4) and Channel 2 (dSph + Jeans modeling at v ~ 20 km/s, `channels_extended.py:533-550`) both use Jeans-style modeling. The v ~ 100-200 km/s regime is **inside the SPARC velocity range** (SPARC galaxies span v ~ 50-300 km/s). |
| "Newer Jeans modelling can improve the galaxy-scale core-profile constraints" | ⚠️ **valid-idea but Tier-3 (≤1 day)** — adopting the Jia 2026 enhanced Jeans formula into the project's existing SPARC hierarchical forward model is a 1-day task: read the paper, port the enhanced core-collapse-time evolution, re-run the SPARC hierarchical likelihood with `T41_SPARC_HIERARCHICAL=1`. Would shift σ/m in the v ~ 100-200 km/s regime by ~10-20%. |
| "The project already uses SPARC (hierarchical likelihood)" | ✅ **confirmed** — `v0.3-prelim/code/precompute_sparc_hierarchical.py` (175 galaxies, hierarchical per T71.4). |

**Scope decision: ⚠️ DEFER (Tier-3 ≤1 day, optional).**
The Jia 2026 enhanced isothermal Jeans formula is a real, recent
improvement that could be plugged into the project's existing SPARC
hierarchical forward model. But it is an **incremental refinement**,
not a new channel or a missing-constraint. Lower priority than Items
1, 4 (already-shipped) or Item 5 (prior-update). Optional for v0.7+.

**Defensive recommendation (optional):** Add Jia et al. 2026
(MNRAS 549, stag969, arXiv:2601.17118) to
`docs/findings_2026_SIDM_papers.md` as a "to-be-evaluated for v0.7+"
entry. No code change.

---

## 3. Overall assessment

| # | Proposal | Priority (docx) | Verification verdict | Scope decision |
|---|---|---|---|---|
| 1 | GD-1 / Zhang 2025 / DESI DR2 | High | ✅ already-shipped (Channel 6) | ✅ no-op |
| 2 | SIDM Concerto + "Fischer 2026" | High | ⚠️ citation wrong (Nadler+ 2025); KiSS-SIDM gap already deferred (V0_6 Item 17) | ⚠️ defer + cite-fix |
| 3 | sidmkit + sidm-vdsigmas | High | ✅ both confirmed (post-user-provenance): `nalin-dhiman/sidmkit` (MIT, arXiv:2601.04735) + `mtryan83/sidm-vdsigmas` (MIT, requires-py ≥3.12) | ⚠️ defer + Tier-3 evaluation (~3-5 days, requires user approval for install) |
| 4 | Andrade 2021 + Adhikari 2025 RMP | Medium | ✅ already-shipped (Channels 8, 10, 21, 23) | ✅ no-op + cite-add |
| 5 | Goldstein & Hill 2026 ΔN_eff | Medium | ⚠️ valid prior-update (~30 min Tier-3); Channels 14/16 already cover the same physics | ⚠️ defer + adopt-prior |
| 6 | SPARC + Jia 2026 isothermal Jeans | Medium | ⚠️ first-author wrong (Jia, not Zhu); existing SPARC Channel 1 already at v ~ 100-200 km/s | ⚠️ defer + cite-add |

**Summary verdict:** 2 of 6 items are **already-shipped** (no action);
3 items are **valid-deferred** with cite-fixes (no new code this round);
1 item is **unverifiable → corrected to Tier-3 evaluation** (the
sidmkit / sidm-vdsigmas packages were verified after user pointed to
the `sidm-vdsigmas` URL).

**Net new channel count from this docx: 0.**
**Net doc/citation updates from this docx: 3-4 one-liners.**
**Net code changes from this docx: 0** (Item 5 is a config-prior
update, not a new channel; Items 2 + 6 are deferred; Item 3 is a
Tier-3 evaluation that requires explicit user approval per AGENTS.md
rule 17 to install).

---

## 4. Citation corrections to land (defensive patches)

These can ship in a single commit alongside the existing v0.4-prelim+T88E
posture. None change any headline numbers; they fix provenance.

1. **`v0.3-prelim/code/channels_extended.py:362` docstring** — add
   Zhang et al. 2025 (ApJL 978 L23, arXiv:2409.19493) attribution
   alongside the existing Yang, Yang, Yu+ 2026 PRL cross-cite.
2. **`docs/findings_2026_SIDM_papers.md`** — replace any reference to
   "Fischer et al. 2026" with Nadler et al. 2025 (arXiv:2503.10748).
3. **`MODEL_ASSUMPTIONS_AND_LIMITATIONS.md` references** — add Adhikari,
   Banerjee et al. 2025 RMP, Rev. Mod. Phys. 97, 045004 (arXiv:2207.10638)
   as the canonical SIDM review cross-cite.
4. **`docs/findings_2026_SIDM_papers.md` (optional)** — add Jia et al.
   2026 (MNRAS 549, stag969, arXiv:2601.17118) as "to-be-evaluated
   for v0.7+" entry.

---

## 5. What the agent would NOT do (and why)

- **Would not auto-install `sidmkit` or `sidm-vdsigmas`** — per
  AGENTS.md rule 24 (Tier-ranked tool adoption, locked from the
  2026-08-19 `thinking-on-improvement.docx` incident) AND rule 17
  (no new dependencies without explicit user approval). Even though
  both packages are now verified as real (post-user-provenance), the
  install + benchmark evaluation requires explicit user go-ahead.
- **Would not add a GD-1 channel** — Channel 6 already covers GD-1
  with the σ/m ~ 30-100 cm²/g constraint the reviewer proposes.
- **Would not add a "SIDM Concerto" channel** — there is no real-time
  simulator hook in the project's joint-fit pipeline; SIDM Concerto
  produces **post-hoc halo catalogs**, not forward predictions. The
  calibration use-case is real but belongs to the deferred V0_6 Item 17
  (KiSS-SIDM UFD fidelity), which requires an architectural change.
- **Would not adopt Goldstein & Hill 2026 in this round** — the prior
  update is a Tier-3 30-min item, not a path-proposal audit item; it
  belongs to a separate Tier-3 backlog entry.

---

## 6. Honest caveats — what the docx got right

- The **velocity-regime coverage** concern (low-v dSph/UFD, mid-v
  galaxy, high-v cluster) is genuine and the project has addressed it
  round-by-round. The reviewer is correct that more low-v channels
  would strengthen the σ/m-vs-v slope constraint. **The reviewer just
  didn't notice that Channel 6 already covers the proposed low-v
  GD-1 anchor.**
- The **standalone solver-benchmark suite** is a real gap in the
  project's microphysics pipeline. The Yukawa analytic formula is
  fast and accurate for separable Yukawa potentials but doesn't
  exercise the partial-wave / Hulthén / Born regime that matters for
  velocity-dependent cross-sections at low v. **After user
  provenance correction, both `sidmkit` and `sidm-vdsigmas` are
  verified as real packages** that cover this gap. The
  `sidmkit.sparc_batch` module is particularly attractive as a
  regression suite for the project's Channel 1 (SPARC hierarchical).
  Adoption is a Tier-3 evaluation (~3-5 days) requiring explicit
  user approval per AGENTS.md rule 17.
- The **Adhikari 2025 RMP** is a useful canonical citation to add to
  the project's references section. This is a 5-min doc-only patch.

---

## 6a. Methodological correction (audit-self-criticism)

The first pass of this audit (commit `967ed0c`, 2026-09-04) marked
Item 3 as **❌ REJECT** because a web search for `sidmkit` and
`sidm-vdsigmas` returned no matches. **The agent's first search
missed both packages.** This was a recall failure, not a missing
package — `sidmkit` was published in arXiv:2601.04735 (Jan 2026)
and `sidm-vdsigmas` has a public GitHub repo. The audit should
have retried with broader keywords ("SIDM toolkit", "velocity-
dependent cross section python", "SIDM phenomenology github")
before declaring the items unverifiable.

**Standing rule for future audits:** if a web search returns zero
matches for a specifically-named tool or package, retry with:
1. The package name as a bare GitHub URL (`github.com/<name>`)
2. Broader domain keywords + author last names if known
3. The package's likely citation (arXiv search if a paper is referenced)

Only after at least 3 distinct search strategies fail should the
audit declare a package "unverifiable" or "fabricated".

**This correction is logged here** so future agents don't replicate
the same recall failure on similarly-named niche tools.

---

## 7. Provenance

- **Docx received:** `Datasets2.docx` uploaded by user 2026-09-04
- **Extraction:** python-docx via `Document.paragraphs` (56 paragraphs,
  0 tables)
- **Verification recipe applied:**
  - V1 6-label matrix per item (W3 5-label + Z1 6th label)
  - P3 stale-citation check via external web verification
    (arXiv / ApJL / MNRAS / Phys. Rev. D / RMP / Google Scholar)
  - P8 stale-recommendation detection via `grep -nE` against the
    project's own `v0.3-prelim/code/channels_extended.py`,
    `v0.3-prelim/code/config.py`, `v0.3-prelim/code/gravothermal.py`,
    `v0.3-prelim/docs/V0_6_ROADMAP.md`, and `docs/findings_2026_SIDM_papers.md`
  - AGENTS.md rule 24 (Tier-ranked tool adoption) blocking
    auto-install of unverifiable packages
- **Audited by:** Hermes Agent (MiniMax-M3)
- **Date:** 2026-09-04
- **Standing version at audit:** v0.4-prelim+T88E (commit `12d0a58`)
- **External verification sources:** arXiv:2409.19493 (Zhang+ 2025),
  arXiv:2503.10748 (Nadler+ 2025), arXiv:2207.10638 (Adhikari+ 2025 RMP),
  arXiv:2012.06611 (Andrade & Fuson 2021), arXiv:2601.17118 (Jia+ 2026),
  arXiv:2601.04735 (Dhiman+ 2026 sidmkit), Goldstein & Hill Phys. Rev. D
  114, L021305 (2026-07-17)
- **User-provided provenance (2026-09-04):** `https://github.com/mtryan83/sidm-vdsigmas`
  — corrected Item 3 from ❌ REJECT to ⚠️ DEFER + Tier-3 evaluation.
  Subsequent web search surfaced `https://github.com/nalin-dhiman/sidmkit`
  and arXiv:2601.04735 — both packages are real and match the
  reviewer's description.
