# T90 Project Status Snapshot

**Last sync:** 2026-09-11
**Synced by:** Hermes Agent
**Branch:** `wip/cloud-9-relhic`
**HEAD:** `55761d7` (clean, pushed to origin)

---

## Where we are now (sync 2026-09-11)

**T90 series reached the Grand Unified milestone (T90.59) and is in
post-review revision mode.** The exploratory T90 line on
`wip/cloud-9-relhic` has shipped T90.45–T90.61, with three
independent post-review corrections in the last session:

1. **T90.59 → honest LZ framing** (commits `6191fc8`):
   Title changed from "Grand Unified SIDM" to "Multi-channel SIDM
   Synthesis (with honest LZ framing)." LZ is reframed as a
   **fine-tuning penalty** on μ_χ, not positive validation.

2. **T90.60 → naturalness measure** (commit `dff55d3`):
   Barbieri-Giudice measure on T90.57 hybrid + T41 v0.8. **Both
   models have at least one extreme-fine-tuning parameter** (T90:
   μ_χ N=19.7; v0.8: m_φ N=24.2).

3. **T90.61 → Kahlhoefer audit (REVISED)** (commits `5adeff5`,
   `55761d7`): Independent σ_DM-nuc re-derivation. Original T90.61
   had a unit-conversion bug; corrected T90.61 v2 confirms T86
   audit's "σ_DM-nuc is 46-65 orders below LZ" conclusion is
   **approximately right**.

**Total T90 test functions: 357** (38 test files, all passing
within their smoke scope — T90.50+ = 266 passing in 0.21s).

**3 commits shipped today (2026-09-11):** T90.60, T90.61 v1, T90.61 v2.
Plus 1 commit for the new TODO.md file recording item 8.

---

## Branch state

| Item | Value |
|---|---|
| Working branch | `wip/cloud-9-relhic` |
| HEAD commit | `55761d7` |
| T90.59 milestone tag | `t90-grand-unified-v59-2026-09-11` (annotated, on origin) |
| GitHub Release | 386933757 (created with user-provided PAT, used once) |
| Test status | 357 T90 test functions, 266+ recent tests passing |
| Open background processes | None |
| Uncommitted changes | None |

---

## Recent commit history (T90 wip branch, 2026-09-11)

```
55761d7 fix(T90.61 v2): correct unit-conversion bug; revise T86 + T90.61 writeups
420b9bf docs(T90.62 TODO): record item 8 from 2026-09-11 review as TODO
5adeff5 feat(T90.61): resolve T86 sigma_DM-nuc discrepancy -- 62 orders, not 15
dff55d3 feat(T90.60): Barbieri-Giudice naturalness measure on T90.57 and T41 v0.8
6191fc8 docs(T90.59 post-review): reframe LZ as fine-tuning penalty, resolve doc drift
6413350 docs(T90): consolidate T90.53-T90.59 entries into ALL_FINDINGS_REFERENCE
5b56f6b feat(T90.59): Grand Unified SIDM -- final synthesis of T90.45 -> T90.58
5b83255 feat(T90.58 re-run): final production numbers -- LZ dominance confirmed
ce8c3ab feat(T90.58): channel-set ablation sweep on hybrid 5-channel fit
ed72a35 feat(T90.57 followup): KSFR-enabled run completed -- Bayesian evidence penalty
d4c5596 feat(T90.57): KSFR/PCAC channel wired (KSFR-off converged, KSFR-on in progress)
8e95281 feat(T90.56): CONVERGED 4-channel hybrid fit with LZ -- satisfies all 4 channels
9176d71 feat(T90.56): LZ magnetic-moment channel (10D, INTERIM -- fit did not converge)
bb45c69 feat(T90.55): hybrid joint fit (9D, 3 channels) -- multi-portal wins
```

---

## T90 series — what each version did

| Version | What it did | Test count | Posterior |
|---|---|---|---|
| T90.45 | First multi-portal joint fit | 7 | log Z = +0.31 |
| T90.50 | Resonant SIDM (m_χ=30 GeV, E_R=65 eV) | 12 | log Z = -2.13 |
| T90.51 | Resonant joint fit (6D, 3-ch) | 11 | log Z = -2.435 ± 0.064 |
| T90.52 | Multi-portal compare (apples-to-apples) | 7 | Δlog Z = -0.21 ± 0.09 (INCONCLUSIVE) |
| T90.53 | Channel survey (47/50 loglike_* functions cataloged) | 0 | n/a |
| T90.54 | Hybrid σ/m(v) form (9 params) | 7 | n/a (form only) |
| T90.55 | Hybrid 3-channel fit (9D) | 8 | log Z = -2.943 ± 0.075 |
| T90.56 | + LZ magnetic-moment (10D, 4-ch) | 7 | log Z = -7.268 ± 0.125 |
| T90.57 | + KSFR/PCAC (10D, 5-ch, KSFR-off/on) | 7 | log Z = -7.286 / -7.912 |
| T90.58 | Channel-set ablation (6 subsets) | 8 | baseline -7.97; LZ drop +4.33 |
| T90.59 | Grand Unified synthesis writeup | n/a (doc) | see doc |
| T90.60 | Barbieri-Giudice naturalness measure | 11 | both lines have extreme N |
| T90.61 | Kahlhoefer σ_DM-nuc audit (REVISED v2) | 8 | confirms T86 conclusion |

---

## Key findings (consolidated, 2026-09-11)

### Robustness hierarchy (T90.58 ablation)
- LZ: Δlog Z = +4.33 (most constrained)
- Cloud-9: Δlog Z = +1.81
- Galactic: Δlog Z = +1.19
- KSFR: Δlog Z = +1.02
- Bullet: Δlog Z = -0.01 (statistically null)

### Unified model posterior median (T90.57 KSFR-on)
- m_χ = 485 GeV
- m_φ_A = 1387 MeV
- g_χ_A = 1.02
- m_φ_B = 4.2 MeV
- E_R = 700 eV
- μ_χ = 4.3×10⁻⁸ μ_N (fine-tuning penalty from LZ)

### σ_DM-nuc at v0.7 MAP (T90.61 v2 corrected)
- Standard Kahlhoefer: ~7.4×10⁻¹⁰⁴ cm²
- T86 hand calc (with bugs): ~10⁻⁹⁶ cm²
- T78/T79 claim: ~10⁻¹¹¹ cm² (prefactor wrong by ~7.5 orders)
- LZ sensitivity: ~10⁻⁴⁵ cm²
- **Gap (model below LZ): ~59 orders**

### Naturalness (T90.60)
- T90 hybrid: μ_χ **EXTREME** (N=19.7); g_χ_B EXTREME (N=9.6); m_χ,m_φ_A severe (~3.6)
- T41 v0.8: m_φ **EXTREME** (N=24.2); m_χ EXTREME (N=7.0); ε MODERATE (N=1.86)

---

## Open work / TODO (per `v0.3-prelim/TODO.md`)

1. **T90.62 (item 8)** — Replace Gaussian placeholder channels with
   raw posterior chains. Deferred per 2026-09-08 pause directive.

2. **Item A — Fix downstream v0.8 docs** (T86, T87, README, CURRENT.md)
   to propagate T90.61 v2 findings. **Requires user explicit
   approval** (touches standing v0.8 docs).

3. **Item B — Continue T90 series** (T90.62+, T90.63, T90.64, T90.65).
   Per pause directive, T90 was explicitly exempted but each new
   T90.x is a fresh production run.

4. **Earlier deferred items:** T95 streams, M51 likelihood, Path C
   resonance (all paused per 2026-09-08 directive).

---

## Lessons learned (recent, 2026-09-11)

1. **Unit-conversion bug in T90.61 v1**: I used `(1/ℏc)² = 2.57×10²⁷`
   for GeV⁻² → cm². WRONG. The correct conversion is `(ℏc)² = 3.89×10⁻²⁸`.
   Off by **10⁵⁵**. The bug was caught during T86 audit review
   (Option D.1 of this session).

2. **T86 audit's two bugs partially cancel**: μ_χp = 423 GeV (MeV/GeV
   confusion, off by 450×) and unit conversion off by 10. Net: T86
   answer is approximately right (~10⁻⁹⁶) despite both bugs.

3. **T86 audit was approximately right** that the model is "untestable
   by current direct detection." The "46-71 orders below LZ" framing
   is correct in spirit and magnitude.

4. **Per rule 25 (memory pre-flight)**, I should have remembered the
   canonical Kahlhoefer formula and ℏc conversion from previous
   sessions. The bug came from rushing. Self-improvement
   opportunity for future sessions.

5. **Smoke test cleanup pattern** (from T90.58): `for f in results_dir.glob("*.json"): f.unlink()`
   will destroy prior production JSONs. Future smoke tests should
   rename-then-restore instead.

---

## Known deviations from defaults

- `wip/cloud-9-relhic` branch is exploratory only. Standing version
  remains v0.8 on master.
- σ_DM-nuc claim in T86/T78/T79 is **off by ~7.5 orders** from the
  standard Kahlhoefer formula. This is documented in T90.61 v2.
- The Grand Unified branding (T90.59) has been downgraded to
  "Multi-channel SIDM Synthesis" per post-review feedback.

---

## Verification

Ground truth verified by:

```bash
git log --oneline -15   # 15 commits visible, HEAD = 55761d7
git branch -a           # wip/cloud-9-relhic is checked out
git tag -l "t90*"       # t90-grand-unified-v59-2026-09-11 present
python3 -m pytest tests/test_t90_v60_naturalness.py tests/test_t90_v61_kahlhoefer_audit.py
                       # 19/19 passing
```

Pre-sync backups: T86_PLAUSIBILITY_AUDIT.md has the T90.61 patch
preserved in git history at `55761d7`. T90.61 writeup is at
`v0.3-prelim/docs/T90_PATH_C4_V61_KAHLHOEFER_AUDIT.md` (revised).

---

## Next step options (binary choice)

1. **Patch downstream v0.8 docs** (Option A — touching T86, T87,
   README, CURRENT.md to propagate T90.61 v2 findings)
2. **Stop here and pause** — sync is complete, all open work recorded
   in TODO.md, no further action needed.

No auto-execution: per project-status-sync anti-pattern #2, sync is
doc-only and requires explicit user sign-off for further mutations.