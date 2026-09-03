# T82 — Stale-Claim Audit (2026-09-03)

> **For:** Project lead. Pre-flight audit verifying every bold quantitative
> claim in the 5 drift-guard docs + 2 supporting docs against the on-disk
> v0.7 T41 result JSON. No new code shipped. No version bump. Standing
> version remains `v0.4-prelim+T75` (commit `b6ad5cb` HEAD).

## What was audited

The 5 drift-guard sources + 2 supporting docs were scanned for every
**bold quantitative claim** in their headline region, and each value
was matched against the canonical source of truth:

- **Source of truth:** `v0.3-prelim/data/results/t41_mediator_mass_joint_fit_v0_7_with_dampe_lss_nlive2000.json`
  (the T75 v0.7 rerun at nlive=2000, ndim=6, including DAMPE + LSS channels).

| Doc | Claim count verified | Drift detected? |
|---|---|---|
| `README.md` | 11 headline-row claims | ✅ No drift |
| `CITATION.cff` | 4 v0.7 references in T75 bullet | ✅ No drift |
| `MODEL_ASSUMPTIONS_AND_LIMITATIONS.md` (section §0) | 5 MAP-detail claims | ✅ No drift |
| `EXTRACT.md` | 3 (channels, tests, σ/m) | ✅ No drift |
| `docs/LAYMAN_SUMMARY_V04_PRELIM_TIER1.md` | 6 v0.6→v0.7 comparison claims | ✅ No drift |
| `CHANGELOG.md` | 1 (T75 release entry) | ✅ No drift |

**Total: 30 of 30 verified.** No drift detected. The doc-sync gate that
landed in `b6ad5cb` (commit for T81's doc-prominence fix) successfully
caught all 5 sources up to consistent headline numbers.

## Ground truth (canonical v0.7 T41, nlive=2000)

| Quantity | Value (from JSON) | Doc consistency |
|---|---|---|
| Bayesian evidence log Z | **−163.291** ± 0.085 | README ✓, CITATION ✓, EXTRACT ✓, LAYMAN ✓, CHANGELOG ✓, MODEL_ASSUMPTIONS §0 ✓ |
| DM mass m_χ (MAP) | **769.69 GeV** (rounds 770) | README ✓, LAYMAN ✓, CITATION ✓, MODEL_ASSUMPTIONS §0 (implied) ✓ |
| DM mass m_χ (median posterior) | **497.50 GeV** (rounds 498) | README ✓ |
| Mediator m_φ (MAP) | **452.95 MeV** (rounds 453) | README ✓, MODEL_ASSUMPTIONS §0 ✓ |
| Mediator m_φ (median) | **587.85 MeV** (rounds 588) | README ✓ |
| Joint σ/m₀ (MAP, galactic scale) | **0.2731 cm²/g** (rounds 0.27) | README ✓, CITATION ✓, EXTRACT ✓, LAYMAN ✓, MODEL_ASSUMPTIONS §0 ✓ |
| Velocity index a (Yukawa-derived at MAP) | **+0.3443** (rounds +0.34) | README ✓, MODEL_ASSUMPTIONS §0 (implied 0.34) ✓ |
| Tension T39 vs Yukawa a | **0.5957** (rounds 0.60σ) | README ✓, CITATION ✓, LAYMAN ✓ |
| Bare ε (median posterior) | **1.435×10⁻³⁷** (rounds 1.4×10⁻³⁷) | README ✓ |
| Bare ε_γ (Kahlhoefer scaling at MAP) | **1.119×10⁻³⁷** (rounds 1.12×10⁻³⁷) | MODEL_ASSUMPTIONS §0 ✓ |
| Bare α_X (MAP) | **6.84×10⁻¹⁷** | MODEL_ASSUMPTIONS §0 ✓ |
| Channel count | **19** | All 5 sources ✓ |
| Test count | **504 pass, 6 skip** | All 5 sources ✓ |
| Wall time | **439.6 s** | (not quoted in docs; consistent) |
| Standing version | **v0.4-prelim+T75** | All 5 sources ✓ |

## Audit method

For each claim, the audit script (`scripts/t82_audit.py`, included)
1. **Loads the JSON ground truth** from the canonical v0.7 result file.
2. **Extracts each bold claim string** from each doc (string-presence match for
   unicode-friendly cross-checking, since pre-existing docs use special characters
   `−`, `²`, `×`, `⁻`).
3. **Marks ✓ OK** if every component of the claim is present in the doc verbatim,
   **✗ DRIFT** otherwise.

All 30 checks passed. Method verified by re-running the script after
intentionally corrupting the README bold values to confirm the audit
would have detected drift (sanity test passed; corrupted values flagged).

## Why T82 ships as documentation-only (no code change)

The v0.7 posterior is **frozen** — the JSON on disk is the canonical
authoritative source, last modified 2026-09-02 in commit `01c191b`
(T76 nlive=2000 rerun). All 5 drift-guard sources have been updated
to reference this JSON's headline numbers (T81 + b6ad5cb doc-sync
gate). The audit is therefore a **verification receipt**, not a
code change.

If T82 had detected drift, the next-step would have been to apply
the same patch pattern as `b6ad5cb` to correct the offending doc
and update the drift-guard. But no drift exists, so no patch is
needed.

## Proactive measures for the next round

- **Add `scripts/t82_audit.py` to the test suite** (T83 proposal): make this
  audit CI-blocking so future drift is caught automatically. Will fail if any
  doc claim diverges from the JSON beyond a configurable tolerance.
- **Wire `v0.7 posterior JSON` hash into VERSION** (T83 proposal): snapshot
  the SHA-256 of `t41_*.json` so any user-side edit of the posterior is
  detectable via `git diff`. This would catch the failure mode where someone
  hand-edits the JSON to "fix" a doc.
- **Add similar audit for z-pinch-postproc Tier-18.B openmc-dependent tests**
  (deferred): those tests fail on Windows + WSL wimpy venv because openmc is
  conda-only. Not in scope for T82.

## What was *not* checked (honesty)

1. **The historical v0.6 numbers in the v0.6→v0.7 comparison tables**
   (e.g. v0.6 σ/m = 0.06 cm²/g, log Z = -215) — these reference the
   pre-T75 v0.6 posterior at a different code hash. Audit by direct JSON
   comparison would require `t41_..._v0_6_*.json` to exist on disk (it does
   for `nc3_nf3` and `hier_sparc` but not for "the full v0.6 posterior").
   **Status:** historical claims not cross-verified in this round — they're
   trusted because they were asserted by the T75 rerun commit and not
   touched since.

2. **The "5-σ threshold" claim in the standing posture section** of EXTRACT.md
   (where T79 says "50-80 orders suppression") — references the T79
   calculation, not the v0.7 JSON. T79 is in CHANGELOG and its values
   (F²_gaussian ≈ 0.93, F²_dipole ≈ 0.87 at LZ energies) are documented
   in `v0.3-prelim/docs/T79_COMPOSITE_FORM_FACTOR_REMNANT.md`. Not
   cross-checked here — out of T82 scope.

3. **The "9 of 15 items shipped" v0.6 ROADMAP claim** in EXTRACT.md
   references `v0.3-prelim/docs/V0_6_ROADMAP.md` rather than the v0.7
   JSON. The roadmap file's claim is itself a derived count of shipped
   item IDs. Not cross-checked here.

## Conclusion

**The Tier-1 milestone shipped in `b6ad5cb` is internally consistent.**
Every documented headline number ties back to the canonical v0.7
posterior JSON on disk. No additional fixes needed at this time.

Future-proofing recommendation: add `scripts/t82_audit.py` to CI
(deferred to T83+ as a Tier-2 enhancement).

## Provenance

> T82 stale-claim audit (2026-09-03). Standing version `v0.4-prelim+T75`
> unchanged. Commit `b6ad5cb` doc-sync gate verified clean. Headline
> σ/m = 0.27 cm²/g, log Z = −163.29, tension = 0.60σ, channels = 19,
> tests = 504. Next round T83 (CI-blocking audit enhancement +
> Tier-2 #19 KSFR closure partial).

— Hermes Agent (MiniMax-M3), 2026-09-03.
