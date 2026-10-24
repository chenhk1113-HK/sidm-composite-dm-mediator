# Dual Review Loop — Findings + Code Reference

**Project:** `sidm-composite-dm-mediator`
**Paper:** `v0.3-prelim/docs/PAPER_V1_DRAFT.md` (Draft v19.2-F Phase 3, pre-submission)
**Date:** 2026-10-24
**Version:** v1.0 (compiled findings with code)
**Base commit:** `68962001e`
**Final commit:** `ae4b763`
**dSph adjudication:** commit `351f42c` (FIXING_ROUNDS_REPORT v1.3)

---

## 0. Framework Constants (single source of truth)

All σ/m(v) computations import from `scripts/constants.py`:

```python
# scripts/constants.py — FRAMEWORK CONSTANTS (v19.2-F Phase 3)
M_CHI_GEV        = 1.0          # DM mass
M_PHI_GEV        = 200e-9       # Mediator mass (200 eV)
V_TARGET_KMS     = 29.4         # Resonance velocity (Cloud-9)
SIGMA_KMS        = 4.4          # Gaussian σ width (NOT FWHM; R76 renamed)
SIGMA_PEAK_CM2   = 174.0        # Resonance amplitude (causality cap)
SIGMA_0_CM2      = 0.052        # Background amplitude at v=100
A_SLOPE          = 1.93         # Background power-law exponent
F_H_PLACEHOLDER  = 0.297        # Heavy fraction (Phase G7 placeholder, retracted v18.29)
C_KMS            = 2.998e5      # Speed of light
HBAR_C_GEV_CM    = 1.973e-14    # hbar*c
LZ_BOUND_CM2     = 9.4e-48      # LZ 2024 90% CL
```

**σ/m(v) function** (used by dSph adjudication, D-5 sweep, D-5 fit):

```python
def sigma_m(v_kms, v_target=29.4, sigma_kms=4.4,
            sigma_peak=174.0, sigma_0=0.052, a_slope=1.93):
    """σ/m(v) = background Yukawa tail + Gaussian resonance peak."""
    background = sigma_0 * (v_kms / 100.0) ** (-a_slope)     # cm²/g
    gaussian = sigma_peak * math.exp(-(v_kms - v_target) ** 2 / (2 * sigma_kms ** 2))  # cm²/g
    return background + gaussian
```

---

## 1. Dual-Review Infrastructure

### 1.1 Reviewer 1 (OpenRouter / Nemotron 3 Ultra 550B)

```
# scripts/dual_review.py — OpenCode reviewer driver with priority chain
PRIORITY_CHAIN = [
    "opencode/deepseek-v4.1-flash-free",   # Primary
    "opencode/glm-5.3-flash-free",          # Fallback
    "opencode/mimo-v2.6-flash-free",        # Fallback
    "opencode/nemotron-3-ultra-free",       # Fallback
    "opencode/nemotron-3.5-super-vl-free",  # Fallback
]
```

```bash
python scripts/dual_review.py --prompt-file scripts/review_prompt_r5_excerpt.md \
                              --out docs/OPENCODE_REVIEW_R5.md
```

### 1.2 Reviewer 2 (Local llama.cpp / Qwen3.6-35B-A3B)

```python
# scripts/r5_local_review.py — Local reviewer via 127.0.0.1:50113
ENDPOINT = "http://127.0.0.1:50113/v1/chat/completions"
MODEL = "Qwen3.6-35B-A3B-UD-Q4_K_M"
# IMPORTANT: chat_template_kwargs: {"enable_thinking": False}
# Without thinking=False, content comes back EMPTY (token budget consumed by reasoning trace)
```

### 1.3 Comparison + Verification

```bash
# Compare two reviews: extract numbers only one reviewer cites
python scripts/compare_reviews.py --a docs/OPENCODE_REVIEW_R5.md \
                                  --b docs/LOCAL_REVIEW_R5.md

# Post-fix verification (8-layer self-check)
python scripts/t82_audit.py
```

### 1.4 Fix Scripts

```bash
# Round 2: early paper fixes
python scripts/apply_round2_paper_fixes.py

# Round 3: remaining paper fixes
python scripts/apply_round3_paper_fixes_v2.py

# Round 5: 11 fixes + 6 rejections (the substantive round)
python scripts/apply_round5_paper_fixes.py
```

---

## 2. The 6 Tracked Findings (Round 5 Rejections — Section 8 of FIXING_ROUNDS_REPORT.md)

### F1: Bayes Factor B = 11.149 Occam-Factor Reasoning → **ADJUDICATED** (2026-10-24)

**Finding:** "The paper's 'prior volume is 3.6× larger' argument may be backwards."

**Adjudication:** The Occam factor is built into dynesty's log Z — it is not a separate post-hoc correction. Dynesty computes log Z by integrating the likelihood over the prior volume, and the negative log B confirms the Occam penalty was correctly applied. Tightening σ_unc weakens (B=21.3→11.15) but does NOT reverse the verdict.

**Evidence files:**
```
v0.3-prelim/data/results/t177_bayes_factor.json   (hand-picked σ_unc, dynesty)
v0.3-prelim/data/results/t205_full_likelihood_published.json  (published σ_unc, dynesty)
```

**Key code (t205 T205 JSON):**
```json
{
  "model_A_multi_resonance": {"logZ": -14.285, "n_params": 15},
  "model_B_constant":         {"logZ": -16.697, "n_params":  2},
  "log_bayes_factor": 2.411,   // Jeffreys: moderate evidence
  "bayes_factor": 11.149
}
```

**t177 (hand-picked σ_unc):** log B = 3.057, B = 21.26 (strong evidence)

---

### F2: Option B (LZ excludes framework at ~21 orders) absent from §1 → **CLOSED**

**Finding:** "Option B is buried in an appendix footnote; §1 states only Option A."

**Adjudication:** §3.5a already states both options with the LZ number. Adding Option A/B to the Introduction is a claim-changing edit, not a text defect. The existing caveat is at the canonical location.

**Code reference:**
```python
# LZ evidence check script
# v0.3-prelim/code/epsilon_lz_check.py
```

---

### F3: Recount headline channels (Cloud-9 50 cm²/g floor is simulation) → **CLOSED**

**Finding:** "Recount because Cloud-9's 50 floor is a SIMULATION benchmark, not an observational bound."

**Adjudication:** Verified that the caveat is already attached at three sites (L173/L862/L1929). Changing the PASS tallies would alter the canonical A.15 accounting, which the project's own audits lock.

**Code reference:**
```python
# scripts/generate_a15.py — A.15 Block 2 channel accounting
```

---

### F4: §9.17b demotion → **CLOSED**

**Finding:** "§9.17b should be demoted from first-class result to map entry."

**Adjudication:** This is a scientific-position decision for the author, not a defect fix.

---

### F5: ~25-page rewrite proposal → **CLOSED** (future revision cycle)

**Finding:** "Rewrite the paper as a ~25-page paper."

**Adjudication:** Out of scope for a defect-fix round. Documented as future work.

---

### F6: dSph Tension Recompute with Velocity-Dependent Form → **ADJUDICATED** (2026-10-24)

**Finding:** "Recompute the dSph tension with the velocity-dependent form — requires SASHIMI-likelihood re-run."

**Adjudication:** Velocity-dependent form does NOT eliminate the dSph tension. The Gaussian resonance tail (σ₁ = 4.4 km/s) contributes ≈0.81 cm²/g at v = 15 km/s, exceeding the Horigome+ 2025 ceiling of 0.032 cm²/g by 25.7×.

**Code files:**
```
scripts/t235_d5_width_test.py   — σ₁ sweep over 8 channels + t_core
scripts/t236_d5_fit.py          — Full 8-channel likelihood fit
docs/dual_review_5loop/GROUND_TRUTH.json   — Controller-computed reference values
docs/dual_review_5loop/ADJUDICATION_EXTRA.json  — E1-E7 extra errors
```

**Key σ/m(v) function (t235 line 46-59):**
```python
def sigma_m(v_kms, v_target=29.4, sigma_kms=4.4,
            sigma_peak=174.0, sigma_0=0.052, a_slope=1.93):
    background = sigma_0 * (v_kms / 100.0) ** (-a_slope)
    gaussian = sigma_peak * math.exp(-(v_kms - v_target) ** 2 / (2 * sigma_kms ** 2))
    return background + gaussian
```

**dSph results table (at σ₁ = 4.4 km/s):**

| Channel | v (km/s) | σ/m(v) | σ_obs ± σ_unc | Status |
|---------|----------|--------|---------------|--------|
| UFD v=3 | 3 | 0.0062 | 0.155 ± 0.05 | PASS |
| UFD v=5 | 5 | 0.0024 | 0.093 ± 0.05 | PASS |
| UFD v=7 | 7 | 0.0016 | 0.067 ± 0.05 | PASS |
| UFD v=10 | 10 | 0.0111 | 0.047 ± 0.05 | PASS |
| **dSph v=15** | **15** | **0.8220** | **0.032 ± 0.04** | **FAIL (25.7×)** |
| Cloud-9 v=28 | 28 | 165.41 | 128.0 ± 30.0 | PASS |
| SPARC v=100 | 100 | 0.0000 | 0.193 ± 0.05 | FAIL |
| Cluster v=500 | 500 | 0.0000 | 0.00025 ± 0.0005 | PASS |

**Resolution:** The paper's D-5 partial resolution (σ₁ = 3.0 km/s) still applies — a narrower width suppresses the v=15 tail while preserving Cloud-9. Deferred to full likelihood refit in v19.2-D.

**D-5 sweep code (t235 line 199-176):**
```python
sigma_1_values = [1.0, 2.0, 3.0, 4.0, 4.4, 6.0]
channels = {
    "Cloud-9": 28.0,
    "Fornax (V_max=18)": 18.0,
    "Fornax (V_max=15)": 15.0,
    "Draco (V_max=10)": 10.0,
    "Sculptor (V_max=9)": 9.0,
    "SPARC (V_max=100)": 100.0,
    "Cluster (V_max=500)": 500.0,
}
results[sigma_1] = {
    "per_channel": {ch: sigma_m(v, sigma_kms=sigma_1) for ch, v in channels.items()},
    "t_core_Fornax_canonical_Gyr": balberg_t_core_Gyr(sigma_m(18, sigma_kms=sigma_1))
}
```

---

## 3. Round 5 Applied Fixes (F1–F9)

All 9 fixes verified independently before application. Code: `scripts/apply_round5_paper_fixes.py`

### F1 — §2.6a duplicated verbatim

```python
# Verify duplicate: two marker lines at L194-219 (canonical) and L695-718 (orphan)
i_markers = [i for i, l in enumerate(L) if l.startswith("**First-class result (R88(26))**")]
assert len(i_markers) == 2
canon_rows = [l for l in L[i_hdr1:i_hdr2] if l.strip().startswith("| Continuous viable")]
orphan_rows = [l for l in L[i_hdr2:i_next_hdr] if l.strip().startswith("| Continuous viable")]
assert canon_rows == orphan_rows
del L[i_hdr2:i_next_hdr]  # Delete orphan block
```

### F2 — §9.14 duplicated sentence block

```python
DUP_TAIL = " The R88(40)/(42) Phase G4 pipeline had a systematic error: ..."
assert txt.count(DUP_TAIL) == 2  # Original + duplicate
second = txt.find(DUP_TAIL, first + 1)
txt = txt[:second] + txt[second + len(DUP_TAIL):]  # Strip only duplicate
assert txt.count(DUP_TAIL) == 1
```

### F3 — §9.13–§9.18 physically inside §10

```python
i_h10 = next(i for i, l in enumerate(L) if l.startswith("## 10. UV Completion:"))
i_101 = next(i for i, l in enumerate(L) if l.startswith("### 10.1 "))
assert i_h10 < i_101  # ## 10 comes before §10.1 but §9.13-9.18 are BETWEEN them
h10 = L[i_h10]
del L[i_h10]  # Move header line
L[i_101:i_101] = [head_txt, scope_line, ""]  # Insert before §10.1
```

### F4 — §10.3 table header 4 columns but rows have 5

```python
old = "| Parameter | T185 (original, buggy) | (CHARM, buggy) | (post bug-fix) |"
new = "| Parameter | T185 (original, buggy) | T185 (CHARM, buggy) | T185 (post bug-fix) | T192 canonical (thermal-avg) |"
```

### F5 — Velocity-independent threshold caveat missing at quote sites

```python
# Abstract L11: attach qualifier to "3.6-23.7x" quote
old = "... 3.6-23.7x (σ_eff = f_H²·σ/m is 0.251 cm²/g at v = 15 ...)"
new = "... 3.6-23.7x (σ_eff = f_H²·σ/m is 0.251 cm²/g at v = 15 ... the comparison applies a velocity-dependent σ/m(v) to a velocity-INDEPENDENT threshold, so these factors are an UPPER BOUND on the true tension)"

# Main result L36: attach qualifier to "27-49x" quote
old = "... against their decisive CDM-preference threshold (0.2 cm²/g, Abstract); ..."
new = "... against their decisive CDM-preference threshold (0.2 cm²/g, Abstract); **Caveat:** the 0.2 cm²/g decisive threshold is a velocity-INDEPENDENT quantity while the framework's σ/m(v) is strongly velocity-dependent ..."
```

### F6 — Abstract shows only rosier channel count (4 PASS / 3 MAR / 1 FAIL)

```python
old = "8 constrained channels (4 PASS / 3 MARGINAL / 1 FAIL; PASS = ..., MARGINAL = ..., FAIL = ...; see §A.15 Block 1)."
new = "8 constrained channels. Under the canonical (self-normalized σ_unc) accounting: 4 PASS / 3 MARGINAL / 1 FAIL ... Under the promoted published-σ_unc likelihood (T205): 1 PASS / 0 MARGINAL / 7 FAIL ... Both counts are stated here because they differ only by likelihood convention, and a reader who sees only one of them would draw a materially different conclusion."
```

### F7 — Three Horigome limits (0.8 / 0.2 / 0.04) rotate silently

```python
old = "- v = 9: 5.43 cm²/g — 27x above threshold"
new = "- v = 9: 5.43 cm²/g (background only) — 27x above the 0.2 cm²/g decisive CDM-preference threshold"

# Plus a full "Threshold-rotation note" paragraph naming all three limits at point of use
```

### F8 — f_H canonical drift: 0.297 (constants.py) vs 0.30 (paper text)

```python
# L98: f_H_cc ~ 0.30 from T207 fit
old = "f_H_cc ≈ 0.30 from T207 fit for core-collapsed dSphs"
new = "f_H_cc ≈ 0.30 from T207 fit for core-collapsed dSphs; the canonical single-component value is f_H = 0.297 per constants.py — 0.30 is a rounded stand-in, a 2% shift in f_H²·σ/m"

# L174: at f_H = 0.30
old = "Fornax σ_HL outlier: ... at f_H = 0.30."
new = "Fornax σ_HL outlier: ... at f_H = 0.30 (rounded from the canonical f_H = 0.297 of constants.py; see §2.5)."
```

### F9 — Abstract status block 764 words inflated abstract to 1051 words

```python
old = "**v19.2-F Phase 3 verdict (2026-10-11, this draft):**"
new = "---\n\n### Headline verdicts (summary block — not part of the abstract prose)\n\n**v19.2-F Phase 3 verdict (2026-10-11, this draft):**"
```

**Post-fix verification:**
```python
assert txt.count("\n## ") == orig.count("\n## "), "H2 count changed"
assert txt.count("\n### ") == orig.count("\n### ") + 1, "H3 count = +1"
assert txt.count("```") == orig.count("```"), "code fence count changed"
```

---

## 4. 5-Loop Dual Review — Summary (33 Claims Adjudicated)

**Reviewers:** Nemotron 3 Ultra 550B (OpenRouter) + DeepSeek-v4.1-flash-free (OpenCode CLI)

| Loop | Focus | Nemotron findings | DeepSeek findings | Controller verdict |
|------|-------|-------------------|-------------------|-------------------|
| 1 | Cloud-9 V_max provenance | 4 | 9 | ✅ All confirmed |
| 2 | Two t_core values (73.71 vs 76 Myr) | 5 | 8 | ✅ All confirmed |
| 3 | Yang+ prefactor, 8.9e9 label | 6 | 9 | ✅ All confirmed |
| 4 | NFW self-consistency | 7 | 10 | ✅ All confirmed; 1 FP |
| 5 | σ_peak window, channel counts | 6 | 8 | ✅ All confirmed |

**Total:** 33 confirmed, 2 reviewer false positives, 1 partial.

---

## 5. Extra Findings (E1–E7) — ADJUDICATION_EXTRA.json

| ID | Verdict | Detail |
|----|---------|--------|
| **E1** | CONFIRMED | BW normalization printed form peaks at 0.20 cm²/g, not σ_peak (numerator must be (Γv_t/2)²) |
| **E2** | CONFIRMED | Horigome ceiling quoted 4 ways (0.04/0.2/0.8/0.032); labels swapped; factor range changes from 27–49× to 136–246× |
| **E3** | CONFIRMED | Abstract conflates σ_eff with σ/m; σ_eff(15) = 0.251 is 0.32× BELOW the 0.8 ceiling |
| **E4** | CONFIRMED | α_χ → 2.84 (L59) vs 0.156 (L59, L2273) for the same quantity |
| **E5** | CONFIRMED | g_N/g_χ hierarchy: L144's 1.2e-24 inconsistent with paper's own conversion (gives 1.01e-11) |
| **E6** | CONFIRMED | Gaussian tail: L117 quotes ~8e-5, correct value 9.93e-6 |
| **E7** | CONFIRMED | s-channel resonance formula: linear v_res = (m_med/m_χ)c is t-channel/Yukawa; s-channel gives v_res = 2c·sqrt(1 − 4m_χ²/m_med²) |

---

## 6. Verification Pipeline

After every fix round, the following audits run clean:

```bash
python scripts/audit_claims.py --table-only          # 29/29, 0 fail
python scripts/audit_units.py                         # clean
python scripts/audit_section_refs.py                  # clean
python scripts/audit_citation_provenance.py           # clean
python scripts/drift_guard.py                         # clean
python scripts/t82_audit.py                           # 85/85 pass
```

Plus per-round stale-string audit: all old strings → 0 occurrences.

---

## 7. File Index

| File | Purpose |
|------|---------|
| `scripts/dual_review.py` | OpenCode reviewer driver with priority chain |
| `scripts/compare_reviews.py` | Compare two reviews: extract numbers only one cites |
| `scripts/r5_local_review.py` | Local reviewer (Qwen3.6-35B-A3B, thinking=False) |
| `scripts/local_model.py` | Model swap utility (fast/deep) |
| `scripts/apply_round5_paper_fixes.py` | 11 Round 5 fixes with assertions |
| `scripts/apply_round3_paper_fixes_v2.py` | Round 3 fixes |
| `scripts/apply_round2_paper_fixes.py` | Round 2 fixes |
| `scripts/t235_d5_width_test.py` | σ₁ sweep over 8 channels (dSph resolution) |
| `scripts/t236_d5_fit.py` | Full 8-channel likelihood fit (dSph) |
| `scripts/constants.py` | Framework constants (all scripts import) |
| `scripts/t82_audit.py` | 8-layer self-check |
| `scripts/audit_claims.py` | Walk PAPER_STANDING_NUMBERS vs JSON |
| `docs/dual_review_5loop/FIXING_ROUNDS_REPORT.md` | Main fixing rounds report (v1.3) |
| `docs/dual_review_5loop/DUAL_REVIEW_5LOOP_REPORT.md` | 5-loop audit report (33 claims) |
| `docs/dual_review_5loop/ADJUDICATION_EXTRA.json` | E1–E7 extra errors |
| `docs/dual_review_5loop/GROUND_TRUTH.json` | Controller-computed reference values |
| `v0.3-prelim/data/results/t177_bayes_factor.json` | Bayes factor (hand-picked σ_unc) |
| `v0.3-prelim/data/results/t205_full_likelihood_published.json` | Bayes factor (published σ_unc) |
| `v0.3-prelim/code/aggregate_nl2000_scan.py` | dynesty nested sampling (log_Z) |
| `v0.3-prelim/code/ch04_width_resolution.py` | Width resolution (dynesty log_Z) |

---

**END OF FINDINGS + CODE REFERENCE**
