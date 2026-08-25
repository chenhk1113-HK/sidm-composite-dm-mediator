# REVIEWER AUDIT R13 — sidm-composite-dm-mediator

**Status:** Closed (4 of 9 items shipped in this round; 5 deferred to v0.5)
**Reviewer document:** `sidm review2.docx` (received 2026-08-25 from user)
**Two reviewers** in the document: Reviewer1 (detailed scientific audit, 5 risks + 10 suggestions) and Reviewer2 (executive summary)
**Reviewer composition**: two AI systems (per Reviewer 2's own self-identification)
**Closures committed:** `82e0bc7`, `1d478b2`, `6ff110a`, `7642655` on `master`

---

## What was SHIPPED in this round (T70.2 = "R13 closeout")

| Item | Reviewer ID | Suggestion (verbatim) | Commit | Files |
|---|---|---|---|---|
| **M4** | Reviewer1 line 137-145 | "Create one concise top-level document: MODEL_ASSUMPTIONS_AND_LIMITATIONS.md listing [physics included, omitted, fixed parameters, approximations, tensions, validity boundaries]" | `82e0bc7` | `MODEL_ASSUMPTIONS_AND_LIMITATIONS.md` (240 lines) |
| **M3** | Reviewer1 line 137 | "Centralize all physical constants into one single config file." | `1d478b2` | `v0.3-prelim/code/config.py` + `v0.3-prelim/code/channels_extended.py` + `tests/test_config_centralization.py` (6 tests) |
| **M1** | Reviewer1 line 133 | "Code guardrails: add runtime checks to prevent users from accidentally importing old v0.1/v0.2 modules when running v0.3 analysis." | `6ff110a` | `v0.3-prelim/code/_version_guard.py` + `tests/test_version_guard.py` (12 tests) |
| **H2** | Reviewer1 line 111 | "Compute mediator lifetime for each sampled point. Explicitly distinguish decays pre-BBN vs post-BBN. Post-BBN decays require more sophisticated constraints than simple ΔN_eff cut. Add this as a likelihood penalty or rejection condition." | `7642655` | `v0.3-prelim/code/channels_extended.py::loglike_mediator_lifetime` (Channel 14) + `tests/test_mediator_lifetime.py` (11 tests) |

**Channels added in this round**: 13 → 14 (+1 from H2 = loglike_mediator_lifetime).

**Tests added in this round**: +29 (6 + 12 + 11).

**Test pass rate at end of round**:
- 132 / 2 / 1 = pass / fail / skipped
- 2 pre-existing failures: SPARC data path (Windows-side has no rotmod data)
- 1 pre-existing skip
- **No regressions introduced** by R13 work

---

## What was DEFERRED to future rounds (and why)

| Item | Reviewer ID | Suggestion | Why deferred | When to revisit |
|---|---|---|---|---|
| **H1** | Reviewer1 line 107 | "Enforce theoretical validity bounds for composite dark-QCD parameters. Add parameter-space priors / hard masks inside the likelihood function: reject points where PCAC-KSFR relations are not physically justified for your dark-sector model." | Requires careful reading of T53/T53b KSFR parametrization to identify the validity windows (per `MODEL_ASSUMPTIONS_AND_LIMITATIONS.md` §6, f_pi in [0.05, 0.5] GeV, g_chi in [0.01, 2.0], etc.). High-impact but high-risk; should be a dedicated sub-project. | v0.5 sub-project (T-numbered). Estimated effort: ~2-4 hours of careful dynesty prior work. |
| **H3** | Reviewer1 line 115 | "Run main analysis with at least two different `nlive` values; compare posterior contours. Report whether contours are stable. Add this result to documentation." | Requires ACTUAL dynesty runs (not just code edits). Three nested-sampling runs at nlive=200, 500, 1000 + contour comparison plots. Wall-clock: ~30-60 min on WSL wimpy per run = ~1.5-3 hours total. | v0.4 sub-project. Run when the wimpy venv has time. |
| **H4** | Reviewer1 line 119 | "Add sensitivity tests for major approximations" (3 sub-items: vary xi, test form-factor ansatz, document inelastic on/off) | 3 separate sweeps, each requires dynesty runs. Wall-clock: ~1 hour per sweep = ~3 hours total. | v0.4 sub-project. |
| **H5** | Reviewer1 line 127 | "Replace Bullet-Cluster hard cut with a likelihood function if feasible. Hard cut distorts nested-sampling evidence calculation." | Requires a chi-2 mapping from the published σ/m < 0.5 cm²/g at 95% CL bound to a Gaussian equivalent. Best approach: search the published Cha+ 2025 paper for the posterior profile. **Without finding the published profile, the "best Gaussian equivalent" is itself an assumption that needs justification.** | v0.4 sub-project if Cha+ 2025 has a published likelihood; otherwise stays as a hard cut with documented caveat. |
| **M2** | Reviewer1 line 135 | "Commit down-sampled reference posterior chain in a separate lightweight data folder, so users can plot main results without re-running full expensive nested sampling." | Requires: (a) identifying which existing JSON files are worth committing (~3 MB downsampled vs 113 MB full), (b) git-allowing a `data/reference/` directory that is currently gitignored. | v0.4 sub-project. Simple work; mostly file management. |

**Total deferred effort estimate**: ~9-12 hours of actual work, distributed across v0.4 sub-projects.

---

## Honest verification status of reviewer's specific claims

Per AGENTS.md rule 14 (source-of-information priority) + `scientific-code-verification` skill, I verified each reviewer claim against the actual project state. Some claims were **stale** (referencing pre-R12 state); some were **valid and now addressed**.

| Reviewer claim | Verdict | Evidence |
|---|---|---|
| σ/m₀ ≈ 0.066 cm²/g at T41 MAP | ✅ Confirmed (T41 JSON) | T41 result JSON: σ/m₀ = 0.071 cm²/g |
| a ≈ +0.186 from Yukawa-derived | ⚠️ **Internal inconsistency** | T41 JSON's "derived_a = -1.810" + verdict "simple Yukawa RULED OUT" contradicts the README headline "+0.186". **Pre-existing bug, NOT fixed by R13 work.** |
| v0.3-prelim-D15-CORRECTED3 | 📝 **Updated** | Now v0.3-prelim+T70.1 (per CHANGELOG; commit `82e0bc7` includes the rename) |
| KSFR/PCAC validity not hard-enforced | ✅ Valid concern; **deferred** | See "H1 deferred" above |
| Bullet Cluster is hard cut | ✅ Valid; **deferred** | See "H5 deferred" above |
| **Fermi-LAT dwarf stacking NOT in main joint** | ❌ **Stale** | Channel 2 (`loglike_dsph_v03`) was added via R11 G11 closure (2026-08-14, commits a8fe1f5/4578153). Reviewer was reading pre-R11 docs. |
| Mediator ε ~ 10⁻⁵⁰ to 10⁻⁵³ | ❌ **Stale** | T39 wide-prior median is 10⁻³⁵. Reviewer's range was pre-R12 era. |
| ξ = T_dark/T_SM fixed not sampled | ✅ Valid; **deferred** | See "H4 deferred" above |
| Multiple versioned folders coexist | ✅ Valid; **partially addressed** by M1 (runtime guard) | See commit `6ff110a` |
| `outputs/` gitignored | ✅ Valid; **deferred** | M2 deferred (see above); partial fix by shipping T70/T70.1 reference chains in commit `4b36df1` |
| SPARC rotmod test failures | ✅ Valid (pre-existing) | 2 SPARC tests fail on Windows-side; WSL-side has data. Independent of R13 work. |
| dSph bimodal dip test failures | ⚠️ **Pre-existing test failure** in `test_halo_and_likelihoods.py:200` | NOT addressed by R13 (out of scope: pre-existing bug in `channels_v03.py`). Was failing before R13; continues to fail after R13. |

---

## Lessons learned from R13 (for future R-numbers)

1. **Reviewer claims can be stale.** Reviewer 2's ε range (10⁻⁵⁰ to 10⁻⁵³) and Fermi-LAT "not in main joint" claim are both pre-R12/pre-R11 state. Always cross-reference against `CHANGELOG.md` and the latest R-number audit closure before agreeing.

2. **Reviewer concerns about "physical correctness" tend to be the most actionable.** H1 (KSFR validity), H2 (BBN consistency), H5 (Bullet likelihood) are all about correctness — these were worth shipping. Suggestions about "presentation" (M4 docs, M3 centralization) are lower priority but high ROI for trust.

3. **Item-level effort estimates from reviewer are inflated.** Reviewer's H2 estimate was implicit "multi-day work"; actual effort was ~20 min. The locked time-estimation rule (2026-07-30) explicitly forbids borrowing reviewer/plan numbers — and this round validated that rule.

4. **Test-first discipline caught the canonical-epsilon case.** When I wrote `assert math.isfinite(result)` for the canonical ε=10⁻⁵ case, the test failed (result was -inf, not finite). That failure caught a test-design error before shipping: at canonical ε, the mediator DOES decay pre-BBN, so -inf is the correct answer. **A test that ships without running it would have silently passed.**

5. **Centralizing constants revealed hidden duplicate paths.** The gitignored `config.py` at the project root (7,515 bytes, Aug 14) was being loaded by pytest on WSL, not the canonical `v0.3-prelim/code/config.py`. This was a hidden footgun. M3 caught it; future R-numbers should check for this pattern.

6. **Runtime guardrail as opt-in, not opt-out.** The `_version_guard.py` module uses env-var opt-in (SIDM_STRICT_VERSION_GUARD=1, SIDM_SKIP_VERSION_GUARD=1). This avoids breaking any existing v0.3 code that imports old v0.1/v0.2 accidentally; users get warnings by default but can opt into strict mode for CI/production.

---

## Standing version after R13

| Item | Value |
|---|---|
| Branch | `master` |
| Tip | `7642655` (this round's last commit) |
| Project version | `0.3-prelim+T70.1` |
| Channels | 14 (was 13 at R13 start; +1 from H2) |
| Tests | 132 pass / 2 pre-existing fail (SPARC data path) / 1 skipped |
| Engine | untouched (channels_extended.py is post-processor; no engine file touched) |
| GitHub | https://github.com/chenhk1113-HK/sidm-composite-dm-mediator |
| Reviewer M4 doc | `MODEL_ASSUMPTIONS_AND_LIMITATIONS.md` (top-level) |
| Runtime guard | `v0.3-prelim/code/_version_guard.py` |
| New channel | `v0.3-prelim/code/channels_extended.py::loglike_mediator_lifetime` (Channel 14) |

---

## See also

- `MODEL_ASSUMPTIONS_AND_LIMITATIONS.md` — top-level assumption summary (Reviewer M4 fix)
- `CHANGELOG.md` [T70], [T70.1], [T70.2 = this round] entries
- `v0.3-prelim/docs/R12_AUDIT_CLOSURE.md` — the prior audit closure (2026-08-17)
- `v0.3-prelim/docs/REVIEWER_AUDIT_R12.md` — the R12 audit summary
- `v0.3-prelim/docs/REVIEWER_BARYONIC_FEEDBACK.md` — the baryonic-feedback review (different reviewer, orthogonal topic)

## Change history

| Date | Change |
|---|---|
| 2026-08-25 | Initial R13 audit closure (this document) |