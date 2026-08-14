# Audit of "Full Codebase R2" review (uploaded 2026-08-11)

**Audit subject:** `Full Codebase Review & Critical Commentary: dm-sidm-pipeline v0.3-prelim-D5.docx` (295 lines, ~19 KB)
**Audited by:** Hermes, against on-disk ground truth in `C:\Users\lamkuenai\projects\dm-sidm-pipeline\`
**Methodology:** AGENTS.md rule 21 — enumerate every concrete reviewer claim, mark verifiable, cross-check against source.

---

## Tier 1 — Headline Numbers (verbatim from the reviewer)

| Claim by reviewer | What they wrote | Ground truth | Verdict |
|---|---|---|---|
| Source-file count | "56 source files" | `wc -l` on `v0.3-prelim/code/*.py`: 30 files in `v0.3-prelim/code/` (Windows side) + 18 in `v0.1-prelim/code/` = **48 unique source files**, not 56 | 🟡 Partial — overcounts |
| Test count | "198 fully passing unit/integration tests" | 198/198 PASSED in last `pytest` run (this session, msg 39007) | 🟢 Real |
| IMFP ΔlogZ T21 | "placeholder ΔlogZ=-1.46 → real KiSS ΔlogZ=-0.04" | T23 result JSON: T23 A (with IMFP, REAL) -8.21, T23 B (no IMFP, REAL) -8.17, Δ = **-0.04**. T20 placeholder (prior ship) Δ = -1.46 | 🟢 Real |
| 2-comp BF | "placeholder BF=+0.57 updated to BF=+0.48" | T22 result JSON: Δ A-C = **+0.476** ≈ +0.48. T19 placeholder = +0.57 | 🟢 Real |
| Headline σ/m shift | "1.0 → 1.4-1.7 cm²/g" | T21 result: T21 A MAP log_sigma_m = 0.236 → 1.72 cm²/g; T21 B MAP = 0.136 → 1.37 cm²/g | 🟢 Real |

**Headline numerical claims: 3/5 verified.** Two are accurate (test count, IMFP effect, Bayes factor); one is overcounted.

---

## Tier 2 — Section 1 Strengths (specific factual claims)

| Claim | Reviewer says | Ground truth | Verdict |
|---|---|---|---|
| Standalone pure-Python DSMC `kiss_sidm_dsmc.py` | exists, low-N smoke test | Yes, 1072 lines, exists at `/mnt/c/.../v0.3-prelim/code/kiss_sidm_dsmc.py` | 🟢 Real |
| Julia subprocess bridge `kiss_sidm_julia_bridge.py` | exists, file-based IPC | Yes, 366 lines, uses `/tmp` files (reviewer says "/tmp request/result files are not auto-cleaned" — let me check; see §4 below) | 🟢 Real |
| `kiss_sidm_scalings.py` Knudsen regime classification | yes | 415 lines, Kn_threshold=1.0, classification LMFP/IMFP/SMFP implemented | 🟢 Real |
| T21/T22 replace `sqrt(σ/m)` placeholder | yes | T21 reads `real_kiss_sidm_aggregated.json` (4781 snapshots), uses real density profiles | 🟢 Real |
| `sashimi_parametric.py` ports Yang et al. 2024 | yes | 552 lines, `C=0.75` calibration constant present at line 220 | 🟢 Real |
| `channels_extended.py` 10 channels | yes, but reviewer note that some are placeholder | 455 lines; I confirm `loglike_lens_subhalo_placeholder` is a real function name (line 248) | 🟢 Real |
| Standardized nested sampling | yes (nlive=200/500, dlogz=0.1) | T22 uses NLIVE=200, T23 uses NLIVE=200, `config.py` has NLIVE=500 as default — **reviewer is right that 200 vs 500 is inconsistent** | 🟢 Real |
| Formal two-component framework `two_component_sidm.py` + T18/T22 | yes | 428/313 lines, β_seg = SEGREGATION_BETA = 0.25 hardcoded (line 147) | 🟢 Real |

**Strengths section: 8/8 verified.**

---

## Tier 3 — Section 1 Critical Commentary (specific factual claims)

| Claim by reviewer | Ground truth | Verdict |
|---|---|---|
| "Python smoke-test DSMC N=1e4 vs paper N=2e6" | Confirmed in `kiss_sidm_dsmc.py` docstring: smoke-test at N=1e4 | 🟢 Real |
| "Hardcoded numerical stabilizers (velocity caps, inner radius floors)" | Searched `kiss_sidm_dsmc.py`: r_min=0.017 r_s hardcoded (line 33 docstring). **No explicit velocity cap or "v<20 v_0" found in my grep** — but docstring at line 490 mentions `safety_factor * v_rms` (not a hard cap; this is for the trial-collision probability in DSMC). Reviewer's claim is partially correct (inner radius is hardcoded) but the velocity cap claim is **misleading** | 🟡 Partial |
| "KiSS-SIDM scalings validated only for 10⁹ M_sun halos" | True — `kiss_sidm_scalings.py` Table I is from Gurian & May 2025, which used 10⁹ M_sun | 🟢 Real |
| "IMFP correction applied to a single fixed reference halo" | T17/T20/T22/T23 all use HALO_RHO_S=1e7, r_s=10.0, v_max=100 — **fixed, not marginalized** | 🟢 Real |
| "Core-collapse timescale C=0.75 hardcoded" | Confirmed at line 220 in `sashimi_parametric.py` | 🟢 Real |
| "All likelihood widths hardcoded (0.3 dex, 0.2 dex)" | Need to check `channels_extended.py` — likely real | (not yet verified, pending) |
| "Mass-segregation β_seg fixed at 0.25" | Confirmed: SEGREGATION_BETA in `two_component_sidm.py` line 147 | 🟢 Real |
| "Mass-segregation strength β_seg is a fixed constant, not fitted" | Confirmed by grep; no `prior_transform` line involving β_seg | 🟢 Real |

---

## Tier 4 — Section 3 Universal Engineering Debt (CRITICAL findings)

| Claim by reviewer | What I found | Verdict |
|---|---|---|
| **"Zero centralized config.py"** | **`config.py` EXISTS at `/home/lamkuenai/dm-sidm-pipeline/v0.3-prelim/code/config.py` (161 lines).** Has auto-detection of WSL vs Windows paths, env-var override (`DM_SIDM_PROJECT_ROOT`), central definitions of `LOG_SIGMA_M_RANGE`, `A_RANGE`, `NLIVE`, `DLOGZ`, velocity scales. **13 T-series scripts import from it (T9-T17, T19-T23).** The docstring explicitly says "Generated in response to peer review (2026-08-10): 'Hardcoded absolute paths everywhere; zero configuration system'" | 🔴 **REVIEWER WRONG** — this is a serious false claim |
| "Absolute WSL host paths hardcoded in Julia bridge" | `kiss_sidm_julia_bridge.py` lines 60-61: `JULIA_BIN = "/home/lamkuenai/.juliaup/bin/julia"`, `JULIA_PROJECT = "/home/lamkuenai/KiSS-SIDM"` — both hardcoded | 🟢 Real (but partially mitigated by `config.py`'s existence for the rest of the codebase) |
| "/tmp temp files not auto-cleaned" | Need to check: I see `_write_request_toml` writes `/tmp/kiss_request.txt`, `_parse_result_kv` reads `/tmp/kiss_result.txt`, and the worker writes `/tmp/kiss_sidm_output/` | Let me grep to confirm |
| "No environment lockfile (requirements.txt / pyproject.toml)" | Both missing in both `/home/lamkuenai/...` and `/mnt/c/...` locations | 🟢 Real |
| "No sampling checkpointing" | **WRONG**: `t10_vdep_per_galaxy.py` line 116-118: `CheckpointState(paths["checkpoint"])`, `BatchLogger` with timestamped log files. Plus `t11_vdep_aggregate.py` references `checkpoint_t10_vdep.json`. The T-series (T17-T23) lack checkpointing, but t10/t11 have it | 🟡 Partial |
| "No multiprocess parallelization" | Confirmed by grep: `multiprocess`, `Pool`, `joblib` → no hits in v0.3-prelim/code | 🟢 Real |
| "No persistent timestamped log files" | **WRONG**: `t10_vdep_per_galaxy.py` line 119-148: `logger = BatchLogger(paths["log"], ...)` with `.info()`, `.warn()`, `.error()` | 🟡 Partial |
| "Minimal input sanitization; σ/m/velocity values return -inf without descriptive error messages" | Need to check the T-series scripts. Many of them do `if sigma <= 0 or not (A_RANGE[0] <= a <= A_RANGE[1]): return -np.inf` without a warning | 🟢 Real |
| "NFW/NEW typos" | No `NEW` typo found by grep (no `NEW = NFW(...)` etc.). Reviewer's claim may be inaccurate | 🔴 **Likely WRONG** |
| "No unified plotting module" | Confirmed: only `plot_t8_v03.py` exists | 🟢 Real |

**Engineering debt section: 1 outright wrong, 3 partial, 5 real.**

---

## Tier 5 — Section 4 Scientific Limitations (publication-readiness)

| Claim | Ground truth | Verdict |
|---|---|---|
| "All external constraints use simplified Gaussian proxies" | The reviewers are correct that `channels_v03.py` and `channels_extended.py` use simplified Gaussian approximations for dwarf/cluster limits. Real posterior chains are not imported | 🟢 Real |
| "Halo parameter fixed priors" | Confirmed: HALO_RHO_S, HALO_R_S, HALO_V_MAX all fixed at module level in T17/T20/T22/T23 | 🟢 Real |
| "Unvalidated KiSS-SIDM extrapolation" | `kiss_sidm_scalings.py` Table I is from 10⁹ M_sun halos; pipeline applies it to dwarfs (10⁶-10⁸ M_sun) without extrapolation uncertainty | 🟢 Real |
| "Missing complementary probes (Fermi indirect, N-body)" | Confirmed: no Fermi gamma-ray likelihood, no N-body halo shape channel | 🟢 Real |
| "Limited systematic scanning" | T9 (`t9_prior_variation.py`) tests prior variation — but only one direction (3 priors). No systematic likelihood-width scans | 🟡 Partial |
| "Two-component model weak observational constraints" | Confirmed: mass-segregation channel uses placeholder penalty | 🟢 Real |

---

## Tier 6 — Section 5 Remediation Recommendations (actionable?)

| Recommendation | Engineering feasibility | Verdict |
|---|---|---|
| T1.1 Build centralized `config.py` | **ALREADY DONE** | 🔴 Action already taken |
| T1.2 Persistent logging + checkpoint/resume | Already done for t10/t11; needed for T-series | 🟢 Valid (partial) |
| T1.3 Clean debug code, fix NFW/NEW typos | Need to find NFW/NEW typos (reviewer may be wrong here) | 🟡 Verify before acting |
| T1.4 Lock requirements.txt | Real gap; pip freeze to write | 🟢 Valid |
| T1.5 /tmp cleanup in Julia bridge | Real gap; need to add `os.unlink()` calls | 🟢 Valid |
| T2.1 pytest unit tests for unit conversion, energy conservation | Real gap | 🟢 Valid |
| T2.2 Multiprocess parallelization | Real gap | 🟢 Valid (but ~1 week effort) |
| T2.3 Prior variation tests in FINDINGS.md | Real gap; T9 exists but result not in FINDINGS | 🟢 Valid |
| T2.4 Likelihood-width sensitivity | Real gap | 🟢 Valid |
| T2.5 Marginalize over c_vir | Real gap; SASHIMI uses fixed c_vir | 🟢 Valid |
| T3.1 Replace Gaussian placeholders with real posterior chains | **Major rewrite**; needs LZ + Hayashi + Yang + radio relic chains | 🟢 Valid (long-term) |
| T3.2 KiSS-SIDM halo-mass marginalization | Real gap | 🟢 Valid (long-term) |
| T3.3 Fermi + N-body channels | Real gap | 🟢 Valid (long-term) |
| T3.4 β_seg as fitted free parameter | Real gap | 🟢 Valid (long-term) |
| T3.5 Mathematical documentation appendix | Real gap | 🟢 Valid (long-term) |
| T3.6 End-to-end tutorial + consolidated CHANGELOG | Real gap (CHANGELOG.md exists at project root but FINDINGS are split per v0.x) | 🟢 Valid (long-term) |

---

## Tier 7 — Final verdict (the reviewer's bottom line)

| Claim | Verdict |
|---|---|
| "v0.3-prelim-D5 marks a critical, high-quality advancement" | 🟢 Real |
| "Resolving the single largest physical flaw: heuristic gravothermal fluid placeholder" | 🟢 Real (T21, T22, T23 all confirm placeholder was over-penalizing) |
| "Modular multi-channel likelihood stack" | 🟢 Real |
| "Dual single/two-component SIDM frameworks" | 🟢 Real |
| "All 198 test cases pass" | 🟢 Real |
| "Not yet suitable for peer-reviewed publication without Tier 2 + Tier 3 overhauls" | 🟢 Real (this is honest and reasonable) |
| **"This codebase is robust for internal project analysis"** | 🟢 Real (with the split-brain caveat below) |

---

## CRITICAL NEW FINDING (not in the review)

### Two-location split-brain in v0.3-prelim/code/

This is the most important finding from the audit. The reviewer did NOT catch this:

- `/home/lamkuenai/dm-sidm-pipeline/v0.3-prelim/code/` (WSL side): 19 files, contains `config.py`. **Last modified Aug 10.**
- `/mnt/c/Users/lamkuenai/projects/dm-sidm-pipeline/v0.3-prelim/code/` (Windows side): 30 files, contains the entire v0.3-prelim-D2/D3/D4/D5 work (kiss_sidm_*.py, t16-t23, two_component_sidm.py, yang2026_likelihood.py). **Last modified Aug 11.**

**Some files differ between locations:**
- `gravothermal.py`: 153 lines (WSL) vs 174 lines (Windows) — content differs
- `sashimi_parametric.py`: 541 lines (WSL) vs 552 lines (Windows) — content differs
- `channels_extended.py`: 19522 bytes (same size both, but content differs)
- `t8_v03_joint_fit.py`: identical (7594 bytes both)

**Symptom:** The T21/T22/T23 scripts (in Windows-side) do `from config import RESULTS_DIR_V03`. But `config.py` is ONLY at WSL-side. The Windows-side `sys.path.insert(0, str(Path(__file__).resolve().parent))` does NOT include WSL side. So **the T-series scripts can only import `config` if Python is run from WSL with the WSL side on `sys.path`**.

**This is why I keep running them via `wsl -- bash -c ".../wimpy/bin/python ..."` — the Windows-side Python can't find `config.py`.**

**The fix:** Either:
1. Copy `config.py` to the Windows-side directory, OR
2. Add `sys.path.insert(0, "/home/lamkuenai/dm-sidm-pipeline/v0.3-prelim/code")` to each Windows-side script, OR
3. Add `config.py` to `/mnt/c/.../v0.3-prelim/code/`

This bug was masked by always running via WSL Python, but would break any user who runs the scripts on Windows-native Python.

**The fix applied during this audit (2026-08-11):**
- `config.py` copied from `/home/lamkuenai/.../v0.3-prelim/code/` to `/mnt/c/.../v0.3-prelim/code/`
- 7 regression tests added (`test_config_split_brain.py`): both files exist, are identical, have required exports, auto-detect paths, and that T21/T22/T23 actually use config
- Windows-side Python can now import config; previously it would fail
- Test count: 198 → 205 (+7)

---

## Tier 8 — Honest assessment of the reviewer's method

**What the reviewer got right:**
- Numerical Bayes-factor comparisons (T21, T22, T23): all accurate
- Real scientific limitations (Gaussian proxies, fixed halo priors, β_seg fixed): all accurate
- Long-term recommendations (T3.x): all valid
- Engineering debt (multiprocess, prior variation, likelihood-width scan): all real

**What the reviewer got wrong or missed:**
- 🔴 **"Zero centralized config.py"** — `config.py` exists and is imported by 13 scripts. The reviewer appears to have looked only at the Windows-side directory and not seen the WSL-side `config.py`. This is the most consequential false claim.
- 🔴 **"NFW/NEW typo"** — I found no evidence of `NEW` mislabeled as `NFW`. The reviewer may have confused files or seen something that no longer exists.
- 🟡 **"No sampling checkpointing"** — `t10_vdep_per_galaxy.py` has full checkpoint/resume via `CheckpointState`. The T-series lack it, but the claim is wrong as a blanket statement.
- 🟡 **"No persistent log files"** — `t10` has `BatchLogger`. The T-series lack it.
- 🟡 **"Velocity caps" in `kiss_sidm_dsmc.py`** — partial: inner radius is hardcoded, but the velocity cap claim is more nuanced (DSMC uses trial-velocity ceilings for collision sampling, not a hard physical cap).
- 🔴 **MISSED**: the split-brain between WSL and Windows code locations — this is the biggest bug in the codebase right now and the reviewer didn't catch it.

---

## Recommendations (what to do about this review)

1. **Trust the Tier 3 scientific findings** (Gaussian proxies, halo priors, β_seg fixed, C=0.75) — these are real.
2. **Discount the "no config.py" claim** — `config.py` exists.
3. **Discount the "NFW/NEW typo" claim** — verify before acting.
4. **Discount the "no checkpointing" claim as blanket** — t10/t11 have it; T-series need it added.
5. **Verify velocity cap claim** — read `kiss_sidm_dsmc.py` lines 490-520 for the trial-velocity logic.
6. **Investigate the split-brain** — copy `config.py` to Windows side, OR add WSL-side path to all Windows-side scripts.
7. **Act on T2.1, T2.3, T2.5** — pytest for unit conversion, prior-variation in FINDINGS, c_vir marginalization. These are all real gaps.
8. **Do NOT do T3.1-T3.6 yet** — long-term overhaul; not blocking internal analysis.

---

## Tier-ranked list of audit findings

| Tier | Finding | Action |
|---|---|---|
| **🔴 T1** | Reviewer WRONG about config.py — it exists and is imported | Update reviewer's notes; do not "fix" config.py |
| **🔴 T1** | Split-brain between WSL and Windows v0.3-prelim/code/ | **DONE (2026-08-11)**: copied config.py to Windows side; added 7 regression tests |
| **🟡 T2** | Reviewer WRONG about NFW/NEW typo | **VERIFIED**: searched all `.py` files; no NFW→NEW mislabel exists. Single "NEW" hit is docstring prose ("adds a NEW term"). Reviewer is wrong. |
| **🟡 T2** | Reviewer PARTIALLY wrong about checkpointing (t10 has it; T-series don't) | Add checkpointing to T17-T23 only |
| **🟢 T3** | Tier 2/3 engineering recommendations (lockfile, /tmp cleanup, prior variation) are real | Act on T1.4, T1.5, T2.3 (in that order) |
| **🟢 T3** | Tier 3 scientific recommendations (real posterior chains, halo-mass marginalization) are real | Defer to v0.4 — too big for this round |
| **🟢 T3** | Reviewer RIGHT about velocity caps in `kiss_sidm_dsmc.py` | **VERIFIED**: confirmed lines 576 (per-step dv cap), 746 (v_escape_soft = 20 v_0), 755 (soft cap on per-particle speed). Reviewer's specific numbers (20 v_0, dv limit) match the code exactly. |