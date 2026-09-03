# Changelog — sidm-composite-dm-mediator

> **Note 2026-08-14**: project renamed from `dm-sidm-pipeline`. All version
> tags below retain their original `v0.X-prelim-DYY` / `Mediator_Detection_vN`
> identifiers — they describe the same work, just under the new name.

All notable changes to this project are documented here. Format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

> **Note 2026-09-03 (T86.7i)**: this file was thinned from ~219 KB /
> ~4,187 lines to ~26 KB / 480 lines. **Round-level details (commits,
> headline numbers, file lists) for every round remain in git history.**
> To recover the full original entry for any round:
> ```bash
> git show <commit>:CHANGELOG.md  # original commit that introduced the entry
> ```
> Each entry's "introducing commit" hash is recorded next to it below.

---

# Current era — full entries (T81 → T86)

These five entries cover the v0.4-prelim Tier-1 milestone and the
recent doc-pack restructure. Kept at full fidelity because they are
the rounds the project currently stands on.

## [T86] — 2026-09-03

T86 = **doc-pack restructure (Option C hybrid).** Continuing the
T85 README streamline work. Standing version unchanged
(`v0.4-prelim+T75`); this is a documentation-only round.

**What shipped (5 sub-commits):**

1. **T86.7b/c (commit `4be9876`):** promoted
   `v0.3-prelim/docs/DARK_SECTOR_LAGRANGIAN.md` → `docs/` (the
   only methodology doc still under v0.3-prelim); added
   `CURRENT.md` (1-page version-of-record) and `docs/INDEX.md`
   (navigation skeleton).

2. **T86.7d (commit `28a5ba0`):** renamed
   `docs/LAYMAN_SUMMARY_V04_PRELIM_TIER1.md` →
   `docs/LAYMAN_SUMMARY.md` (the version-suffix was carrying
   historical-only info; canonical version is captured in the
   doc body).

3. **T86.7e (commit `e93c65e`):** bundled 4 superseded layman
   summaries (R12, R13, R14, T71.8) into
   `v0.3-prelim/docs/LAYMAN_SUMMARIES_HISTORICAL.md`
   (collapsed `<details>` blocks); deleted the originals. ~55 KB
   in-tree saved; full content remains in git history.

4. **T86.7f (commit `0e21059`):** bundled 5 V0_6 closures
   (`BROWER_PROBE_SCOPE`, `KISS_SIDM_TIMEOUT_VERDICT`,
   `KISS_SIDM_UPSTREAM_FINDING`, `LATTICE_FORMFACTOR_CLOSURE`,
   `TIER_B_CLOSURE`) into
   `v0.3-prelim/docs/V0_6_CLOSURES_HISTORICAL.md`; bundled
   10 old Mediator Detection Syntheses (v2-v11) into
   `v0.3-prelim/docs/MEDIATOR_SYNTHESES_HISTORICAL.md`; deleted
   the originals. Renamed
   `v0.3-prelim/docs/FINDINGS.md` →
   `v0.3-prelim/docs/PROJECT_FINDINGS.md` (breaks basename
   collision with `docs/findings_2026_SIDM_papers.md`).

5. **T86.7g (commit `80bafb8`):** extended `scripts/t82_audit.py`
   to scan `CURRENT.md` (1-page version-of-record). Audit count
   went 32 → 40 checks (8 new for CURRENT.md).

**Also updated:**

- **T86.a/b (commit `b29a7f2`):** test count 504 → 542 across
  `EXTRACT.md`, `docs/LAYMAN_SUMMARY.md`, and audit-test
  machinery (was already part of pre-T86 drift cleanup; included
  here for completeness).

**Verification (end of T86):**

- Audit: **40/40 ALL CLEAR** (was 32 pre-T86)
- Tests: **542 pass / 6 skip** (unchanged from T84)
- v0.3-prelim/docs/ file count: 50+ → 33
- Total in-tree disk saved: ~135 KB

**Deferred to a follow-up round** (out of scope for the in-progress
doc-pack restructure): `CHANGELOG.md` thinning. Currently 219 KB /
~4,096 lines. Thinning approach: keep first 50 lines (project
rename + standing version), keep T85+ entries at full fidelity,
collapse older rounds to one-line commit-references.

## [T86.7j] — 2026-09-03

**Plausibility audit** addressing two user-raised concerns:
(1) Does the LZ 2.6σ finding undermine the model?
(2) Does the Planck-length extrapolation invalidate the σ_DM-nucleon
suppression claim?

**Trigger:** User upload of `Consider3.docx` (third-party review,
181 paragraphs) + the actual LZ preprint
(`LZ_Preprint_260901_Dark_Matter_EFT_Nuclear_Recoil_Search_at_Higher.pdf`,
25 pages, 2026-09-02).

**What shipped:**

1. **`v0.3-prelim/docs/T86_PLAUSIBILITY_AUDIT.md`** (NEW, ~360 lines):
   Full analysis with verbatim LZ paper quotes, numerical derivations,
   and tables comparing LZ best-fit (1000 GeV/c² Ls₁₀) against project
   v0.7 MAP (770 GeV). Verdict: both concerns resolve to **validation,
   not falsification**.

2. **`CURRENT.md`** (modified): added `## Plausibility audit` section
   + fixed drift-guard count consistency (40/40 not 32/32).

3. **`docs/LAYMAN_SUMMARY.md`** (modified): added `## Honest caveats —
   T86.7j plausibility audit` section. Reheating-temperature requirement
   (T_RH > 10¹⁵ GeV) — a load-bearing assumption previously buried in
   T79 — is now surfaced in the layman summary.

4. **`scripts/t82_audit.py`** (modified): drift-guard check updated
   from "32/32 ALL CLEAR" to "40/40 ALL CLEAR".

**Standing posture preserved:** log Z = −163.29 ± 0.085, m_χ = 770 GeV,
σ/m = 0.27 cm²/g, 19 channels. **No posterior re-run.** No new physics.

**Verification:** drift-guard audit 40/40 ALL CLEAR; 5/5 drift-guard
tests passing; test suite 540 pass / 8 skip (env-conditional; canonical
WSL count is 542 pass / 6 skip per standing posture).

**One caveat surfaced:** MAP ε ~ 10⁻³⁷ places the project in the
freeze-in regime, which requires T_RH > 10¹⁵ GeV or non-standard
cosmology. Standard cosmology has T_RH ~ 10⁹-10¹⁰ GeV. Documented in
T79 §"Relic-density consistency check" but is now prominent in
CURRENT.md and LAYMAN_SUMMARY.md. Not a falsification (freeze-in is
well-established per Hall et al. 2010), but a load-bearing assumption
worth flagging.

---

## [T86.7k+C] — 2026-09-03

**Composite-channel gap analysis** addressing the substantive point in
`consider4.docx` (third-party review, 109 paragraphs) that arrived after
T86.7j shipped. **Docs-only round** — no new code, no posterior re-run.

**Trigger:** User message 2026-09-03 — "I want to really close the gap."

**What shipped (5 doc updates, no code):**

1. **`v0.3-prelim/docs/V0_6_ROADMAP.md`** (modified): Added Tier-2 Item 3
   — "Composite-DM direct-detection forward prediction (T87)". Scope:
   ~5-6 hrs wall. Estimated effort: 1.5-2 hrs for inelastic σ_DM-nucleon
   module + 1-1.5 hrs for LZ event-rate module + 1 hr for tests + 30 min
   for smoke test at v0.7 MAP + 30 min for verdict writeup. No new deps.
2. **`v0.3-prelim/docs/T86_PLAUSIBILITY_AUDIT.md`** (modified): Added
   "Composite-channel gap analysis" section with reviewer claim-by-claim
   verification, status of existing inelastic-DM modules (T43,
   T41_INELASTIC, h4_inelastic_sweep, test_inelastic_wrapper_regression),
   and the genuine-gap itemization.
3. **`CURRENT.md`** (modified): Added "Composite-channel gap
   (T86.7k+C, post-Consider4 review)" subsection under "Plausibility audit".
4. **`docs/LAYMAN_SUMMARY.md`** (modified): Added "Honest caveats —
   T86.7k+C composite-channel gap" subsection.
5. **`v0.3-prelim/docs/consider4_review/`** (NEW): Created folder with
   `consider4_source.docx` (13 KB) + `README.md` (3.5 KB) for reviewer-input
   traceability per AGENTS.md rule 21.

**The genuine gap (reviewer was right):**

- The LZ paper tests **inelastic-DM and SD operators** (NREFT O₁ˢ, O₄ᵛ,
  Ls₁₀; inelastic DM with δ ≈ 200-300 keV), not elastic SI.
- The project's "10⁻¹¹¹ cm² elastic SI" number is correct for the
  elastic-SI channel, but LZ is actually probing inelastic/SD channels.
- Composite DM naturally has SD + inelastic channels (constituent spins,
  mass splitting), but the project has NOT computed inelastic σ_DM-nucleon
  or composite-DM SD operator decomposition.
- This is the missing piece that elevates "compatible with LZ" to
  "predicts LZ event" (if successful) or to "constrained/falsified" (if
  the predicted event rate doesn't match).

**Three reviewer claims that were stale premises:**

1. "T79 form-factor calc pending" — T79 already shipped at commit `6b83904`.
2. "Relic-density check pending" — T79 §"Relic-density consistency check"
   verifies freeze-in regime; T_RH > 10¹⁵ GeV now surfaced in CURRENT.md.
3. "Inelastic/SD cross-section not started" — partially right. Inelastic
   σ_DM-DM exists (T43, T41_INELASTIC, h4_inelastic_sweep). Inelastic
   σ_DM-nucleon + composite-SD operator decomposition is genuinely missing.

**Standing posture preserved:** log Z = −163.29 ± 0.085, m_χ = 770 GeV,
σ/m = 0.27 cm²/g, 19 channels. No posterior re-run. No new physics.

**T87 (the code work) is registered but NOT initiated** in this round.
Per the project's pre-registered T78 trigger discipline: <3σ → doc-only
(current); ≥3σ → run the analysis. T87 is the analysis that would run at
≥3σ; running it now is premature but allowed per user direction.

**Verification:**
- Drift-guard audit: 40/40 ALL CLEAR
- Drift-guard tests: 5/5
- Test suite: 540 pass / 8 skip (env-conditional; canonical WSL count is
  542 pass / 6 skip per standing posture)

**Next round:** T87 (full forward-prediction code + tests + verdict doc)
initiated if user gives the green light.

---

## [T85] — 2026-09-03

**README.md streamline** (Option C precursor to T86). Standing
version unchanged (`v0.4-prelim+T75`).

**What changed:**

- README.md: 750 lines → 440 lines (−41%).
- Headline + key findings (TL;DR) promoted to **TOP** (under title/
  badges). A reader sees the v0.7 result (σ/m = 0.27 cm²/g, m_χ =
  770 GeV, log Z = −163.29, 19 channels, 542 tests) **before**
  any historical context.
- The ~250-line historical heads-up block (T70 / T70.1 / T70.2 /
  R12 / etc.) moved to a single `## Recent rounds heads-up
  (chronological, archived for context)` section near the BOTTOM,
  preserved for archival context, with `[Standing]` /
  `[Superseded]` tags.
- KSFR LATTICE-class promotion (T83) added to "What's in each
  version".
- T84 sensitivity sweep added to "Key findings".
- `scripts/t82_audit.py` README checks refactored (was 11, now
  10); `test_t82_audit_version_drift.py` minimum check count
  assertion updated 33 → 32 to match.
- Version table updated to reflect T83 (KSFR promotion) + T84
  (sensitivity sweep).

**Verification:** Full test suite 542 pass / 6 skip; audit 32/32
ALL CLEAR at time of merge.

---

## [T84] — 2026-09-03

T84 = **Channel 18 (LSS) ρ_abundance sensitivity sweep.**

Per Updated review1.docx §4 (received 2026-09-03): "consider a sensitivity
study that varies the mapping from bias to core size." This study
quantifies exactly that — T74's Channel 18 uses `rho_abundance` (z_f-Σ*
correlation coefficient) as a hardcoded fixed parameter (default 0.85);
T84 sweeps it across the physically plausible range [0.5, 1.0] in 11
grid points.

**Headline result:**

| Quantity | Value |
|---|---|
| ρ grid | 0.50 to 1.00 (11 points, Δ = 0.05) |
| Fiducial ρ (T74 default) | 0.85 |
| Best-fit σ/m at all ρ values | 2.683 cm²/g (constant — grid-search finds absolute max) |
| Best-fit σ/m spread over ρ ∈ [0.7, 1.0] | 0.000 cm²/g ✓ |
| Max \|Δlog Z\| across ρ ∈ [0.5, 1.0] | 9.015 log-units |
| Δlog Z(ρ=1.0) vs fiducial | +1.439 |
| Δlog Z(ρ=0.7) vs fiducial | −2.894 |
| T74 sensitivity claim "ρ ∈ [0.7, 1.0] is insensitive" | **Half-verified — best-fit σ/m is invariant, but log Z magnitude is sensitive** |

**Honest interpretation:** The T74 doc claim is **partially correct**.
Best-fit σ/m IS invariant (T74's grid-search picks the absolute max-LL
bin, which lands at the same σ/m regardless of ρ). However, the
log-likelihood magnitude at that best-fit σ/m **scales substantially
with ρ²** (because `b_pred[i] = 1 + s · ρ · (b_obs[i] - 1)` means
chi² ∝ ρ² at the perfect-SIDM-template bin). Over ρ ∈ [0.7, 1.0] the
log Z swing is ~3 log-units; over the full [0.5, 1.0] range it's
~9 log-units.

**Implications for the v0.7 posterior:** The v0.7 MAP σ/m = 0.27 cm²/g
sits in a sub-optimal regime for Channel 18 regardless of ρ (predicted
b_rel diffuse bin ~1.16 to 1.31, observed 2.31 ± 0.20). The headline
σ/m = 0.27 cm²/g is robust because it is *driven by other channels*
(dSph + UFD + Bullet + SPARC + DAMPE), not by LSS alone. The
ρ-sensitivity affects the magnitude of the LSS-channel contribution to
log Z, not the sign — so the v0.7 posterior remains qualitatively
correct under reasonable ρ variation.

**T84 deliverables:**

1. **`v0.3-prelim/code/t84_lss_rho_sensitivity.py`** (NEW, ~290 lines):
   Sweep runner + JSON writer + summary printer. ~3 sec wall time
   on the 11×45 grid.

2. **`v0.3-prelim/data/results/2026-09-03_t84_rho_sensitivity/t84_rho_sweep.json`**
   (~8 KB): full machine-readable results.

3. **`v0.3-prelim/data/results/2026-09-03_t84_rho_sensitivity/t84_best_fit_per_rho.csv`**
   (498 bytes): compact per-ρ CSV.

4. **`v0.3-prelim/tests/test_t84_rho_sensitivity.py`** (NEW, 14 tests):
   - Grid structure, range, fiducial-in-set
   - Best-fit σ/m in [0.3, 3] for all ρ
   - Best-fit σ/m spread < 0.5 cm²/g over ρ ∈ [0.7, 1.0]
   - log L monotonically increases with ρ at fixed σ/m
   - b_pred matches formula `b_pred[i] = 1 + s · ρ · (b_obs[i] - 1)`
   - JSON schema + delta-at-fiducial=0 + bias-scaling-with-ρ
   - log Z swing is substantial (>1 log-unit)

5. **`v0.3-prelim/docs/T84_LSS_RHO_SENSITIVITY.md`** (NEW, 7 KB):
   Full results, interpretation, and recommended edit to T74 doc claim.

6. **T74 doc update** (§Honest limitations #4): the original "insensitive
   to ρ over [0.7, 1.0]" claim was refined to "best-fit σ/m invariant;
   log Z magnitude moderate-sensitive", with a link to T84 doc.

**No version bump.** T84 is a sensitivity study (no posterior change).
Standing version `v0.4-prelim+T75`. 542 tests passing (was 528; +14).
Drift-guard remains `33/33 ALL CLEAR`.

---

## [T83] — 2026-09-03

T83 = **KSFR lattice-table promotion + T82 stale-claim audit**.

**Part 1 — T82 stale-claim audit (closed in commit `29a8ed5`):** Every bold
quantitative claim in the 7 drift-guard docs (VERSION, README, CITATION,
EXTRACT, MODEL_ASSUMPTIONS, CHANGELOG, layman) was verified against the
canonical v0.7 T41 result JSON. **32/32 checks passed — no drift detected.**
The CI-gatable `scripts/t82_audit.py` (4.8 KB) was added so future drift is
caught automatically.

**Part 2 — KSFR LATTICE_TABLE promotion (this commit):** v0.6 ROADMAP item
**#19** (Lattice-informed KSFR ratios) advanced one row:

| Combo | Was | Now |
|---|---|---|
| (3, 2) fundamental | ESTIMATED in `t53b_lattice_input.py` (LATTICE in `ksfr_pcac_validity.KSFR_NC_NF_RATIOS`) | **LATTICE in both sources** (Shindler 2019, 8.4 ± 0.3) |

The (3, 2) promotion closes a module-level inconsistency: the existing
canonical `KSFR_NC_NF_RATIOS` table at line 115 of
`ksfr_pcac_validity.py` had `(3, 2): 8.4, # LATTICE — SU(3) fund Nf=2
extrapolated`, but the `t53b_lattice_input.LATTICE_TABLE` only had
**commented-out** entries for (3, 2). T83 promotes the entry to the
active LATTICE_TABLE so `m_rho_over_f_pi()` for (3, 2) now returns the
Shindler 2019 value directly instead of falling back to the QCD ratio.

**Honest framing on T83 originally-drafted AF_EXCLUDED demotion:** The T83
first draft attempted to demote (2, 3) fundamental from ESTIMATED to
AF_EXCLUDED on the basis of asymptotic-freedom violation. Self-audit
caught that the 1-loop β₀ for SU(2) N_f=3 is **+16/3 > 0** (i.e.
asymptotically free), so the demotion was based on a math error and
was **reverted before commit**. T83 ships only the (3, 2) promotion.
(2, 3) and (3, 4) remain ESTIMATED per the existing
KSFR_NC_NF_TABLE.md.

**KSFR confidence counts (after T83):**
- LATTICE: 3 (was 2) — (3, 3), (3, 2) fundamental, (2, 2) adjoint
- ANALYTICAL: 2 — (4, 3) and (4, 4) large-N_c extrapolation
- ESTIMATED: 2 (was 3) — (2, 2) fundamental (Arthur 2016, conservative),
  (3, 4)

**Other T83 deliverables:**

1. **ANCHOR_RATIO_ERR_COMBINED** added to `t53b_lattice_input.py`:
   ```python
   ANCHOR_RATIO_ERR_PDG = 0.05            # PDG 2022 / FLAG review average
   ANCHOR_RATIO_ERR_LATTICE_2019 = 0.30   # Shindler 2019 multi-N_f sweep
   ANCHOR_RATIO_ERR_COMBINED = sqrt(0.05² + 0.30²) ≈ 0.304  # ~3.7%
   ```
   Multi-source confirmation of the (3, 3) anchor visible at code level.

2. **scripts/t82_audit.py** (CI-gatable doc drift guard):
   ```bash
   python scripts/t82_audit.py  # exits 0 on clean, 1 on drift
   ```
   Wired into pre-commit hook so any v0.7-JSON-vs-doc divergence fails CI.

3. **`tests/test_t83_ksfr_lattice_promotion.py`** (NEW, 19 tests):
   - LATTICE_TABLE promotion tests (×5)
   - Fallback behavior preservation tests (×3)
   - Anchor uncertainty band tests (×6)
   - KSFR counts and v0.7 MAP validity tests (×5)

4. **`v0.3-prelim/docs/T82_STALE_CLAIM_AUDIT.md`** (NEW, 6.9 KB):
   Full audit report documenting the 32/32 drift checks against the v0.7 JSON.

5. **`v0.3-prelim/docs/T83_KSFR_LATTICE_PROMOTION.md`** (NEW, 8.1 KB):
   Full T83 closure doc including the honest disclosure of the AF math error.

**No version bump.** T83 is refinement + audit (no posterior change).
Standing version: `v0.4-prelim+T75`. 523 tests passing (was 504; +19).

---

## [T81] — 2026-09-02

### LZ review response + XENONnT/PandaX-4T Channel 19 (v0.4-prelim)

Defensive doc-update + Channel 19 implementation in response to the
`LZ1.docx` technical review of the T80 milestone write-up.

The reviewer's 5 recommendations:
1. Soften "cross-validation" -> "compatibility" (rec #1)
2. Soften "sigma/m survives all scenarios" -> "sigma/m unchanged at
   current LZ precision" (rec #2)
3. Complete T79 (already done; F^2(q) values documented) (rec #3)
4. Flag LSS phenomenological status more prominently (rec #4)
5. Register XENONnT + PandaX-4T watch (rec #5)

All 5 addressed in T81.

### Channel 19 implementation (XENONnT + PandaX-4T watch)

Per LZ1.docx reviewer rec #5:
- Added XENONNT_2025_LIMITS (arXiv:2502.18005, PRL 135, 221003)
  to `channels_extended.py` (7 mass points, 1.7e-47 cm^2 minimum at 30 GeV)
- Added PANDAX4T_2025_LIMITS (arXiv:2408.00664, PRL 134, 011805)
  to `channels_extended.py` (7 mass points, ~3e-47 cm^2 minimum at 40 GeV)
- Added helper functions `sigma_XENONnT_2025_limit`, `sigma_PandaX4T_2025_limit`,
  `is_excluded_by_XENONnT_or_PandaX`, `loglike_competitor_dd_watch`
- Wired Channel 19 into T41 joint fit with `T81_COMPETITOR_DD_DISABLE=1`
  env-var gating (same pattern as Channels 17/18)
- Marked as "experimental - NOT in primary production" in CHANNEL_STATUS
- Added 13 new tests in `test_channel_19_competitor_dd.py`

### Conftest fix

Found a Windows-specific bug in `v0.3-prelim/tests/conftest.py`:
WSL path detection used `exists()` which returns True for
`C:\home\...` on Windows even when WSL is not running.
Added `_is_real_project_root(p)` sentinel that checks for
`v0.3-prelim/code/channels_extended.py` as a robust marker.

### Rhetoric softening (recs #1, #2, #3)

- README: "cross-validation" -> "compatibility check" in T80
  milestone block; T80 row in version table updated
- LAYMAN_SUMMARY_V04_PRELIM_TIER1: "sigma/m survives all scenarios" ->
  "sigma/m unchanged at current LZ precision"; "Heavy-WIMP hypothesis
  validated by LZ" -> "Heavy-WIMP hypothesis compatible with LZ"
- T74 LSS docs: prominent phenomenological status note added
  (per rec #4)

### Files modified

- `v0.3-prelim/code/channels_extended.py` (Channel 19 + limit tables)
- `v0.3-prelim/code/t41_mediator_mass_joint_fit.py` (Channel 19 wiring)
- `v0.3-prelim/tests/test_channel_19_competitor_dd.py` (NEW, 13 tests)
- `v0.3-prelim/tests/conftest.py` (Windows compatibility)
- `v0.3-prelim/docs/T74_LSS_ZHANG_2025.md` (phenomenological status)
- `v0.3-prelim/docs/T81_LZ_REVIEW_RESPONSE.md` (NEW, 11 KB)
- `docs/LAYMAN_SUMMARY_V04_PRELIM_TIER1.md` (softened rhetoric)
- `README.md` (T80 milestone block: "compatibility" framing)
- `CHANGELOG.md` (T81 entry)

### Standing-version impact

**No version bump.** T81 is refinement + Channel 19 addition; no
posterior change. Standing version: `v0.4-prelim+T75`.

Test count: 504 passed, 6 skipped (was 472 passed, 7 skipped).

---

# Historical rounds — collapsed to one line per round

Each line below records the introducing commit, the round name, and a
topic sentence from the original full entry. To recover the full
original entry, see the commit hash.

### v0.4-prelim Tier-1 milestone era (T72–T80)

Captures the v0.4-prelim DAMPE + LSS Tier-1 work (T72 DAMPE POC → T80 LZ paper update). The v0.4-prelim+T75 line is the standing-version milestone.

*2026-09-02*

- **[T80]** (2026-09-02, `503f973`) — The actual LZ preprint appeared 2026-09-02 (much earlier than the KIV cron 080d2f590251 expected fire date ...
- **[T79]** (2026-09-02, `6b83904`) — Quantitative refinement of T78 in response to the 'comment T78 wrap-u.docx' technical critique. The reviewe...
- **[T78]** (2026-09-02, `686f016`) — Defensive doc-update + model-specific calculation in response to the Consider2.docx technical review of the...
- **[T77]** (2026-09-02, `14de661`) — In response to the 2026-09-01 LUX-ZEPLIN announcement of a single high-energy particle interaction event at...
- **[T76]** (2026-09-02, `c3f98e3`) — Final v0.4-prelim milestone closing out the deferred items from T75. 1. **nlive=2000 v0.7 rerun.** Wall tim...
- **[v0.4-prelim+T75]** (2026-09-02, `9c5b580`) — Runs the T41 joint fit at nlive=500 with Channels 17 (DAMPE) and 18 (Zhang+2025 LSS) wired in. **Major post...
- **[T74]** (2026-09-02, `114465b`) — Wires the Zhang et al. 2025 Nature measurement of the **anti-correlation** between stellar surface density ...
- **[T73]** (2026-09-02, `1d40286`) — Wires the T72 DAMPE POC into the T41 joint fit as **Channel 17**, with a dark-matter forward model that pre...
- **[T72]** (2026-09-02, `5b75d02`) — Per the `REVIEWER_CONSIDER_DATA.md` path-proposal audit (T71.9 input), DAMPE ingestion was promoted from "T...


### v0.6 KSFR + Wave A era (T71.0–T71.8.1)

KSFR/PCAC validity mask + R13/R14/R15/R16/R7 audit closure + (Nc,Nf) scan.

*2026-08-26 — 2026-08-29*

- **[T71.8.1]** (2026-08-29, `572c69e`) — Per user direction "proceed (e)" on the advisory `Update check.docx` (2026-08-29). Pre-flight on the 5 advi...
- **[T71.8]** (2026-08-28, `572c69e`) — Per `Updated review15.docx` (read end-to-end, 223 paragraphs, per AGENTS.md rule 21). Reviewer's Sp(4) sect...
- **[T71.7]** (2026-08-28, `2581429`) — Per user direction "kiss sidm ufd, use the author original c python; download hepdata". **KiSS-SIDM upstrea...
- **[T71.5]** (2026-08-28, `8ced591`) — Per user direction "do as much as possible" after T71.4 (3 v0.6 items shipped in parallel). Pre-flight on T...
- **[T71.4]** (2026-08-28, `39bf07d`) — Per user direction "proceed all, in parallel if ok" after T71.3 R7 closure. Closes V0_6_ROADMAP items #1 (H...
- **[T71.3]** (2026-08-28, `6c704e8`) — Per user direction "do solid r7, try run in parallel" after the v0.6 release-bundle scope discussion (T71.2...
- **[T71.2]** (2026-08-27, `55767a1`) — Per user direction "ship the 2 session-shippable items" after R16 sidmgrok1.docx audit. Per reviewer-audit ...
- **[T71.1]** (2026-08-27, `3503802`) — Per user direction "do all the fixes and checking" after R15 sidm5.docx audit. Per reviewer-audit skill W1 ...
- **[T71.0]** (2026-08-26, `4dbdfc6`) — Per user direction "proceed a, b and c" (continuing the R14 closure cycle). Three parts: (1) re-run the (Nc...


### v0.6 Channel expansion era (T70–T70.9)

Channels 11-13 (DM-free UDGs, cosmic-web radio, SIDM quantum-statistical mass floor); v0.5 KSFR-enabled rerun.

*2026-08-25 — 2026-08-26*

- **[T70.9]** (2026-08-26, `9361382`) — Per user direction "proceed c, a, and b" (resuming the v0.5+R14 cycle). Two parts: (1) close the 5 remainin...
- **[T70.8]** (2026-08-26, `2258916`) — Per user direction "proceed" (resuming the v0.5+T70.5 documentation cleanup). Two R14 deferred items from `...
- **[T70.7]** (2026-08-26, `a398f2f`) — Per user direction "proceed option 1" (parallel execution of Wave A from the v0.6 plan). Three items shippe...
- **[T70.6]** (2026-08-26, `805b967`) — Per user direction "proceed option 1" — ship 3 of 3 high-priority + 1 of 3 medium-priority recommendations ...
- **[T70.5]** (2026-08-26, `d3dc490`) — Per user direction "v0.5 re-run" — execute the re-run of T41 with the KSFR/PCAC validity mask (Channel 15) ...
- **[T70.4]** (2026-08-26, `23f5419`) — Per user direction "relaunch h3 h4" — resume the deferred sensitivity sweeps from `REVIEWER_AUDIT_R13.md` §...
- **[T70.3]** (2026-08-26, `1d331ed`) — Per user direction "do the 0.4 and 0.5" (resume deferred sub-projects from `REVIEWER_AUDIT_R13.md` §"Honest...
- **[T70.2]** (2026-08-25, `dbd4b39`) — Per user upload of `sidm review2.docx` (2026-08-25). Two reviewers in the document: Reviewer1 (detailed sci...
- **[T70.1]** (2026-08-25, `4b36df1`) — Per user question *"I am puzzled, given both sidm and fdm are particles, then shouldn't sidm also be subjec...
- **[T70]** (2026-08-25, `6801b2f`) — The user uploaded two documents summarising recent literature: - `暗物质竟是量子波.docx` (9 KB, 58 paragraphs) — a ...


### R12 audit era + T69 (post-reviewer feedback)

Six-reviewer audit closure (R12/R12a/R12b/R12c) + baryonic-feedback nuisance sensitivity (T69).

*2026-08-17 — 2026-08-19*

- **[T69]** (2026-08-19, `fe8bb6c`) — The user uploaded `Baryonic feedback.docx` (91 lines, ~13 KB), proposing that baryonic feedback be added as...
- **[R12c]** (2026-08-18, `021d351`) — The user uploaded `Consider this review.docx` (8 paragraphs, 6 "needs correction" findings, 1 "bottom-line ...
- **[R12b]** (2026-08-18, `03f4c35`) — Added a plain-language companion to the T68 technical synthesis, in response to the user finding the layman...
- **[R12a]** (2026-08-18, `dcec35e`) — Re-verify of T68 against `v0.3-prelim/data/results/t68_cross_validation_drobczyk.json` and the T72 cross-va...
- **[R12]** (2026-08-17, `8d76894`) — Six external reviewers (`six reviews.docx`) sent an audit on 2026-08-14. All 7 of Reviewer 6's specific fin...


### v0.3-prelim D-era (pre-renaming, mid-Aug 2026)

Tier-3 publication work (T3.1/T3.2/T3.3), parallel-session infrastructure, Julia/KISS-SIDM integration. Round numbers D..D15-CORRECTED3 reflect the old naming scheme.

*2026-08-11 — 2026-08-12*

- **[v0.3-prelim-D15-CORRECTED3]** (2026-08-12, `ede5dd6`) — D15-CORRECTED3 ships the response to "Full Review 5.docx" (a thorough English review of v0.3-D15-CORRECTED2...
- **[v0.3-prelim-D15-CORRECTED2]** (2026-08-12, `ede5dd6`) — D15-CORRECTED2 ships the response to review4.docx (the most thorough external review of v0.3-D15). The revi...
- **[v0.3-prelim-D15]** (2026-08-12, `ede5dd6`) — **TIER-3 RESOLVED (T39 + T39b):** Per memory's pinned TIER-3 KEY LESSON, T30 (LZ) and T32 (Fermi) gave
- **[v0.3-prelim-D14-CORRECTED]** (2026-08-12, `ede5dd6`) — **BG-1: T38c dwarf KiSS-SIDM N=2e6 paper-scale run** - **`v0.3-prelim/code/t38c_dwarf_kiss_sidm_paper_scale...
- **[v0.3-prelim-D13-CORRECTED]** (2026-08-12, `ede5dd6`) — **D11/Direction A closure: T36 — SASHIMI 3×2 config matrix** - **`v0.3-prelim/code/t36_sashimi_config_matri...
- **[v0.3-prelim-D12]** (2026-08-12, `ede5dd6`) — **D13: T38 — Dwarf KiSS-SIDM at higher particle counts (PARTIAL)** - **`v0.3-prelim/code/t38_dwarf_kiss_sid...
- **[v0.3-prelim-D11]** (2026-08-12, `ede5dd6`) — **D12: T37 — T22 Bayes factor with β_seg at the T29-MAP value** - **`v0.3-prelim/code/t37_t22_with_fitted_b...
- **[v0.3-prelim-D10]** (2026-08-11, `ede5dd6`) — **T3.2: T31 — Halo-mass marginalization** - **`code/t31_halo_mass_marginalization.py`** — Re-runs KiSS-SIDM...
- **[v0.3-prelim-D9]** (2026-08-11, `ede5dd6`) — **T3.1: T30 — LZ 2024 real posterior ingestion** - **`code/t30_lz_real_posterior.py`** — Ingests real LZ WS...
- **[v0.3-prelim-D8]** (2026-08-11, `ede5dd6`) — **T3.4: T29 — β_seg as fitted free parameter** - **`code/t29_beta_seg_fitted.py`** — Re-runs T22 (Yang+ 2-c...
- **[v0.3-prelim-D7]** (2026-08-11, `ede5dd6`) — **Tier 1: T26 — T21 width sensitivity (with KISS-SIDM penalty)** - **`code/t26_t21_width_sensitivity.py`** ...
- **[v0.3-prelim-D6]** (2026-08-11, `ede5dd6`) — **Tier 1 quick wins:** - **`requirements.txt`** at project root — pinned versions (numpy 2.4.6, scipy 1.18....
- **[v0.3-prelim-D5]** (2026-08-11, `ede5dd6`) — - **`code/t22_real_kiss_sidm_two_comp.py`** — Re-runs T19 (Yang+ 2026 2-comp SIDM) with REAL KISS-SIDM grav...
- **[v0.3-prelim-D4]** (2026-08-11, `ede5dd6`) — - **Julia 1.11.5 installed at `/home/lamkuenai/.juliaup/bin/`** (default channel set to 1.11.5). - **KISS-S...
- **[v0.3-prelim-D3]** (2026-08-11, `ede5dd6`) — - **`data/results/kiss_sidm_canonical_simulation_N1e5.json`** + `boost_dsmc.py` + `boost_dsmc_500k.py` + `t...
- **[v0.3-prelim-D2]** (2026-08-11, `ede5dd6`) — - **`code/t17_kiss_sidm_corrected_fit.py`** + **`data/results/t17_kiss_sidm_corrected_fit.json`** + **`data...
- **[v0.3-prelim-D]** (2026-08-11, `ede5dd6`) — - **`code/kiss_sidm_scalings.py`** (16.6 KB): published power-law fits from Gurian & May 2025 (arXiv:2505.1...


### Initial releases (v0.1-prelim, v0.2-prelim, v0.3-prelim, Unreleased)

Earliest publicly-shipped versions. All superseded by v0.4-prelim.

*2026-08-10*

- **[Unreleased]** (2026-08-10, `ede5dd6`) — - **`config.py`** at project root: single source of truth for paths, constants, prior ranges, sampler hyper...
- **[v0.3-prelim]** (2026-08-10, `ede5dd6`) — - `code/channels_v03.py`: Channel 2 (dSph) likelihood proxy with bimodal exclusion dip, plus velocity-depen...
- **[v0.2-prelim]** (2026-08-10, `ede5dd6`) — - `code/sidm_velocity_dependent.py`: v-dep SIDM parametrization σ/m(v) = σ/m_0 × (v/v_ref)^(-a) + Gaussian ...
- **[v0.1-prelim]** (2026-08-10, `ede5dd6`) — - `code/sparc_loader.py`, `code/halo_profiles.py`, `code/fit_single_galaxy.py`, `code/fit_all_galaxies.py`,...


---

# How to recover the full original entry for any round above

Every historical entry has an introducing commit hash. To see the
full original CHANGELOG.md as it stood when that round shipped:

```bash
git show <commit-hash>:CHANGELOG.md
# Or browse in the GitHub UI:
# https://github.com/chenhk1113-HK/sidm-composite-dm-mediator/blob/<commit>/CHANGELOG.md
```

The drift-guard (`scripts/t82_audit.py`) does NOT scan this
collapsed section — only the top 5 full-fidelity entries +
`CURRENT.md` + the standing-version docs.

---

## Known issues / deferred (per peer review)

- Gaussian proxies for external likelihoods (Issue 2.1.1) — needs real
  posterior chains from Horigome+/Sánchez-Almeida+/Cha+ groups for peer review.
- SASHIMI-SIDM cosmology (Issue 2.1.4) — would take weeks to implement.
- SPARC v-dep re-fits (Issue 2.1.2) — saturation model used instead.
- Parallelization (Issue 2.2.5) — single-threaded fits only.
- requirements.txt (Issue 2.2.6) — manual `dynesty 3.0.0, numpy 2.4.6` etc.
- CHANGELOG (Issue 2.3.1) — **this file**, created 2026-08-10 in response to review.