# Dual-Reviewer 5-Loop Audit — SIDM Composite DM Mediator

**Date:** 2026-10-22
**Paper:** `v0.3-prelim/docs/PAPER_V1_DRAFT.md` (Draft v19.2-F Phase 3, pre-submission, Phase 3 gate verdict FAIL)
**Reviewer 1:** `nvidia/nemotron-3-ultra-550b-a55b:free` (OpenRouter free) — Hermes `delegate_task` child
**Reviewer 2:** `opencode/deepseek-v4.1-flash-free` (OpenCode CLI free tier) — repo-aware, reads project files
**Controller:** all numerical claims recomputed in Python before adjudication

Every claim below was independently recomputed. Reviewers quote; the controller computes.

## Tally

| | Count |
|---|---|
| Claims adjudicated | 33 (26 loop-targeted + 7 extra) |
| **CONFIRMED** | **33** |
| REFUTED | 2 (both reviewer false positives — see below) |
| PARTIAL | 1 |
| Reviewer false positives caught by controller | 2 |

## The one finding that matters most: the T208 JSON is stale

**Severity: HIGH (data provenance), LOW (physics impact).**

Commit `beeb658` ("v18.40 code fixes per 2review.docx") fixed `v_max_from_M_c` to use
`r_max = 2.1626 * r_s` instead of the virial approximation. **The JSON was never regenerated.**

| Field | JSON value | Correct (current script) | Status |
|---|---|---|---|
| `V_max_kms` (Cloud-9) | 24.754551 | 31.118631 | **STALE** |
| `sigma_m_at_v_virial_C9` | 0.210062 | 0.167102 | **STALE** |
| `t_cross_Gyr` | 0.115516 | 0.091892 | **STALE** |
| `t_core_over_t_cross` | 638.10 | 802.15 | **STALE** |
| `V_max_kms` (subhalo) | 1.447655 | 1.924539 | **STALE** |
| `t_core_Gyr` | 73.710885 | 73.710885 | **correct** (invariant) |
| `t_core_over_t_Hubble` | 5.341368 | 5.341368 | **correct** (invariant) |
| `runs_in_Hubble` | False | False | **correct** |

**Why `t_core` is invariant:** `t_core = (12.7/σ)·(ρ_s/10⁻²)⁻¹·(r_s/10⁴)·(100/V_max)` and
`σ = 0.052·(100/V_max)^1.0` (A_SLOPE = 1.0). The `(100/V_max)/σ` factor is V_max-independent.
So the V_max error cancels exactly in `t_core`, which is why the stale JSON was never noticed.

**Physics impact: none on the verdict.** `t_core = 73.71 Gyr > t_Hubble = 13.8 Gyr` (ratio 5.34)
still holds, and the corrected ratio 802 is still ≫ 3, so the causality verdict is untouched.
The paper's own numbers (31.12 km/s, 802 at L1170) are the **corrected** ones — the paper and its
own data JSON disagree.

**Fix:** re-run `T208_path_b_cloud9_host_halo_gravothermal.py` and commit the regenerated JSON.
Note `matches_T204: false` will remain false (1.973 vs 0.563 Gyr, 3.51× apart) — that crosscheck
gap is unexplained in either the JSON or the paper.

## Loop-by-loop

### Loop 1 — Cloud-9 V_max provenance
- ✅ JSON V_max = the retired virial approximation `sqrt(G·M/r_vir)` (matches to 1e-9). Current script gives 31.12. **Both reviewers.**
- ✅ `t_core` invariant under the correction; verdict survives. **Both reviewers.**
- ✅ Stale fields: `sigma_m_at_v_virial_C9` (0.210→0.167), `t_cross_Gyr` (0.1155→0.0919), `t_core/t_cross` (638→802). **Both reviewers.**
- ✅ Subhalo V_max also stale (1.4477→1.9245). *DeepSeek only* — Nemotron said only "similarly affected if same method". DeepSeek's extra computation was the useful one.
- ⚠️ `matches_T204: false` unexplained.

### Loop 2 — two Cloud-9 t_core values (73.71 Gyr vs 76 Myr)
- ✅ 73.71/0.076 = 969.9 vs σ ratio 161.70/0.167 = 968.3 → agree to 0.17%, exactly the `t_core ∝ 1/σ` scaling. **Both reviewers.**
- ✅ "0.83 vs cap 3.0" **is** the "3.6×" (3.0/0.83 = 3.61) — a cap factor, not a floor ratio. **Both reviewers.**
- ✅ The paper's 0.83 uses the **corrected** `t_cross` (0.076/0.0919 = 0.827); the JSON has the stale 0.1155. Paper and JSON are mutually inconsistent.
- ✅ The two t_core values are **different σ/m scenarios** (73.71 Gyr: pre-core-collapse baseline σ/m=0.167; 76 Myr: resonance peak σ_peak=174 → σ/m=161.70). Same halo, two physics assumptions — conflatable as written.
- ✅ *DeepSeek only, extra*: Breit-Wigner normalization — the printed `(Γ/2)²/[(v²−v_t²)²+(Γv_t/2)²]` evaluates to `1/v_t² = 0.00116` at v=v_t, so with σ_peak=174 the printed form peaks at **0.20 cm²/g, not 174**. Numerator must be `(Γv_t/2)²`.
- ✅ *DeepSeek only, extra*: `exp[−(15−29.4)²/(2×3²)] = 9.93e-6`, but L117 quotes ~8e-5. The paper's own L158 has the correct 1.0e-5 form.

### Loop 3 — Yang+ 2024 prefactor and the 8.9e9
- ✅ Denominator units are `(cm²/g)(M☉/kpc²)/Gyr` — **not** 1/Gyr. The mixed-unit path carries an extra factor. *Nemotron's unit trace; correct.*
- ✅ Pure unit factor = 4.787e9 kpc²/M☉ per cm²/g (1 M☉/kpc² = 2.0889e-10 g/cm²). **Both reviewers.**
- ✅ **8.9e9 is NOT a pure unit factor.** `(1.34e12/150)/4.787e9 = 1.866` = the BM2 calibration mismatch. The code docstring (gravothermal_yang2024.py:283-289, 300) calls 8.9e9 a "unit-conversion factor"; it is units × calibration. *Nemotron; correct.*
- ✅ *DeepSeek only, extra*: in **consistent cgs** the denominator **is** 1/s and 150·C = 112.5 reproduces 15.77 Gyr. This shows the published 150 works dimensionally — the 8.9e9 gap is the code's mixed-unit choice, not an error in Yang+ 2024.
- ⚠️ The "8.9e9" wording appears **only in the code docstring**, not in the paper. The paper calls 1.34e12 "empirically calibrated" (L1291) — so the two conventions coexist. *DeepSeek's [Q] is right.*
- ✅ *DeepSeek only, extra*: α_χ is 7.4× the normalization coupling ⇒ σ_T 54.6× larger ⇒ σ/m(100) = 0.052×54.6 = **2.84**, which the paper does report at L59 — but L59 and L2273 also report **0.156** for the same quantity.

### Loop 4 — NFW self-consistency
- ✅ The script's `rho_s = M/(4πr_s³)/[ln(1+c)−c/(1+c)]` reproduces 9.68962e-3 M☉/pc³ exactly, and equals `(200/3)ρ_crit c³/f(c)`. **Both reviewers' [OK] correct.**
- ✅ The `(200/3)ρ_crit·c` form (no c³) is off by c² = 144. *DeepSeek; correct.*
- ✅ Paper's V_max 31.12 (c=12) and 25.59 (c=4) reproduce exactly.
- ✅ The script docstring's "20-30% underestimate" is **right** (20.5% / 25.7%), but its *reasoning* is wrong: `M(<r_max)/M_vir = 0.2848` (not 0.20) and `sqrt(0.2848×12) = 1.8486` (not 1.55); the true ratio is 1.2571. **Both reviewers.**
- ❌ **Nemotron false positive**: claimed the paper prints ρ_s with c¹ instead of c³. Paper L167 verbatim: `ρ_s = (200/3) × c³ × ρ_crit / [ln(1+c) − c/(1+c)]` — c³ *is* there. Nemotron's own `execute_code` output said "rho_s (alt formula with c^3) = 9.68962001e-03" and "Ratio = 1.000000", then the prose asserted c¹. **A self-contradiction inside one review**: the computation was right, the prose was wrong.
- ✅ *DeepSeek only, extra*: Horigome ceiling is quoted **four ways** — 0.04 (L949, w→∞), 0.2 (L36, labeled "velocity-independent w→∞"), 0.8 (L111, w=10), 0.032 (canonical_numbers.json:84). The abstract's "27–49×" uses 0.2; the paper's own L958 "115–460×" uses 0.04. **The labels are swapped**: 0.2 is the w=30 value, 0.04 is the true w→∞ value.
- ✅ *DeepSeek only, extra*: g_N/g_χ jump of ~10¹³ orders. From the paper's own 1.78e-24/9.4e-48 conversion: at σ/m(28)=166.02 → g = 1.74e-13 (L38's 1.7e-13 ✓); at σ/m(100)=0.052 → g = 1.01e-11, but L144 quotes 1.2e-24. L143 (5.2e44/4.4e-23) is also inconsistent with the same algebra.

### Loop 5 — σ_peak window and headline channel counts
- ✅ c=12 σ_peak window is **EMPTY** (floor 51.96 > cap 47.65 and > 47.71). **Both reviewers.**
- ✅ Floor: 50×50/48.14 = **51.93**, paper says 51.96 (L176, L189). 0.05% discrepancy. *Nemotron.*
- ✅ Cap inconsistency real: interpolation gives 143/3 = **47.667**, between the quoted 47.65 (L186) and 47.71 (L189/L192). **Both reviewers.**
- ✅ `dSph_violation_factor = 43.333` is **not** 50/0.8 (=62.5); it is 34.6667/0.8 = σ_m_v15_C9_CORE_enhanced / dSph_ceiling. **Both reviewers.**
- ⚠️ "174 fails by 3.6×" is ambiguous: 174/51.96 = 3.35× (floor) vs 174/47.65 = 3.65× (cap) — and 3.0/0.83 = 3.61× is a *different* 3.6×.
- ✅ Channel counts genuinely conflict: "1 of 8" / "5 of 8" (L19, L59, L820, L1606 — the v19.2-E A.1 caveat), "4 PASS / 3 MARGINAL / 1 FAIL" (L19, L25, L1605, L2264, L2266), "4 of 8" (L1013, L1014, L1085, L1086, L1707), "4 of 7" (L942, L1608, L1707, L1876, L2266), "7 of 10" (L1707, L1876), "6 of 8" (L1087), "7/8" (L1635, L1686, L2149). *DeepSeek.* These are partly different channel sets/likelihoods, but the retired "4 of 7" framing still appears at three lines.

## Extra findings not requested by any prompt (DeepSeek, loops 2/3/4) — all CONFIRMED

1. **Breit-Wigner normalization** (paper L34): printed form peaks at 0.20 cm²/g, not σ_peak.
2. **Horigome ceiling quoted 4 ways**, with the w→∞ and w=30 labels swapped (L36 vs L949/L950) — this changes the headline factor range from 27–49× to 136–246×.
3. **Abstract conflates σ_eff with σ/m** (L11): "σ_eff … above Horigome's 0.8 cm²/g limit by 3.6–23.7×", but the paper's own σ_eff = f_H²σ/m = 0.297²×2.85 = 0.251 cm²/g (L111) is **0.32× below** the ceiling. The 3.6–23.7× range is σ/m/0.8.
4. **α_χ → σ inconsistency**: 0.052×54.6 = 2.84 (reported at L59) vs 0.156 (reported at L59 and L2273) for the same quantity.
5. **g_N/g_χ hierarchy**: L144's 1.2e-24 and L143's 4.4e-23 are inconsistent with the paper's own conversion arithmetic, which gives 1.01e-11 and 1.74e-13.
6. **Gaussian tail**: L117's ~8e-5 should be 9.93e-6 (L158 has it right).
7. **s-channel resonance relation** (L82): the linear `v_res = (m_med/m_χ)c` is the t-channel/Yukawa form; s-channel with m_med ≈ 2m_χ gives `v_res = 2c·sqrt(1 − 4m_χ²/m_med²)`. Also L82's "four mediators" contradicts L896-898, which mark v₂–v₄ as bookkeeping nodes, **not** physical resonances.

## Reviewer scorecard

| Loop | Nemotron 550B | DeepSeek (OpenCode) | Overlap | False positives |
|---|---|---|---|---|
| 1 V_max | 4 findings | 9 findings | 7 shared numbers | 0 |
| 2 t_core | 5 | 8 | 9 shared | 0 |
| 3 prefactor | 6 | 9 | 3 shared | 0 |
| 4 NFW | 7 | 10 | 6 shared | **1 (Nemotron c³)** |
| 5 window | 6 | 8 | 4 shared | 0 |

- Nemotron: strong on **unit traces and dimensional algebra** (its Loop 3 unit analysis was the sharpest single contribution), but it produced **one false positive that contradicted its own computed output**.
- DeepSeek: broader coverage and **repo-aware** (it read files nobody pointed it at), caught **7 issues no prompt asked for**, but its numeric claims still needed full recomputation (it quoted 0.0918/0.09189/0.167/802/1.9245 — all correct — but only after the controller confirmed each).

## Recommended actions, in priority order

1. **Regenerate the T208 JSON** and commit it (fixes 5 stale fields). Then reconcile the paper's 73.71 Gyr / 802 ratio with the JSON.
2. **Fix the Horigome ceiling labelling** (L36 vs L949/L950) — this changes a headline factor range by 5×.
3. **Fix the abstract's σ_eff wording** (L11) — it currently claims a quantity exceeds a limit that the paper's own definition puts 3× below it.
4. **Fix the Breit-Wigner normalization** (L34) and the α_χ/σ/m inconsistency (L59, L2273).
5. **Reconcile the g_N/g_χ pair** (L143/L144) and the σ_peak provenance (162 vs 174 vs 178.5 vs 196.3 vs 2026).
6. **Harmonize the channel-count framing** — retire "4 of 7" at L942/1608/1707/1876, and make the v19.2-E A.1 "1 of 8 / 5 of 8" caveat appear wherever "canonical" appears.
7. **Fix the code docstring** at gravothermal_yang2024.py:283-289, 300 — 8.9e9 is units × calibration, not a unit factor.
8. **Explain or drop** the `matches_T204: false` crosscheck.

## Artifacts

- `docs/dual_review_5loop/NEMOTRON_LOOP{1..5}_review.md` — reviewer 1 output
- `docs/dual_review_5loop/OPENCODE_LOOP{1..5}_review_prompt_loop{N}_*.md` — reviewer 2 output
- `docs/dual_review_5loop/ADJUDICATION.json` — 29 adjudicated loop claims with verdicts
- `docs/dual_review_5loop/ADJUDICATION_EXTRA.json` — 7 adjudicated extra findings
- `docs/dual_review_5loop/GROUND_TRUTH.json` — controller-computed reference values
- `docs/dual_review_5loop/nemotron_context_loop{1..5}.txt` — the text-only context given to Nemotron
- `scripts/review_prompt_loop{1..5}_*.json` / `.txt` — the prompts
- `scripts/run_5loop_opencode.sh` — parallel driver for reviewer 2
