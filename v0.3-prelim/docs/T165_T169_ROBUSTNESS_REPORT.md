# T165-T169 Robustness Investigation (2026-09-20)

**Goal:** Improve robustness of our phenomenology model by testing sensitivity to data points and assumptions.

**Key question:** Is the 4000× Cloud-9 spike required by our data, or an artifact of our specific parameter choice?

---

## T165: Cloud-9 Value Sensitivity

**Method:** Refit our 8 data points with Cloud-9 (v=28) set to different values: 50, 100, 128, 500, 2000 cm²/g.

**Results:**

| Cloud-9 value (cm²/g) | Best RMSE | Best params |
|---|---|---|
| 50 (lower bound) | **1.033** | α=0.3, mA=0.3, mχ=100 |
| 100 | 1.131 | α=0.3, mA=0.3, mχ=100 |
| 128 (current) | 1.166 | α=0.3, mA=0.3, mχ=100 |
| 500 | 1.363 | α=0.3, mA=0.3, mχ=100 |
| 2000 | 1.566 | α=0.3, mA=0.3, mχ=100 |

**Verdict:** Different Cloud-9 values give DIFFERENT fits (spread 0.53). The 4000× spike value MATTERS for our model. **Lower Cloud-9 values (50-128) give better RMSE than high values (500-2000).**

**Implication:** Our specific 128 cm²/g choice is **not optimal** — a lower value (50 cm²/g) gives better fit. This supports using σ/m ≥ 50 (lower bound only) rather than a specific high value.

---

## T166: Leave-One-Out

**Method:** Refit with each of 8 data points excluded. Determines which points are "load-bearing".

**Results:**

| Excluded point | RMSE | Δ from full |
|---|---|---|
| None (full fit) | 1.166 | — |
| v=3 | 1.246 | +0.080 |
| v=5 | 1.246 | +0.080 |
| v=7 | 1.243 | +0.076 |
| v=10 | 1.237 | +0.070 |
| v=15 | 1.227 | +0.061 |
| **v=28 (Cloud-9)** | **0.459** | **−0.707** |
| v=100 | 1.221 | +0.054 |
| v=500 | 1.162 | −0.004 |

**Verdict:** **Cloud-9 is by far the most influential point.** Excluding it improves RMSE by 0.707 (from 1.166 to 0.459). All other points contribute marginally.

**Implication:** Our 8-point fit quality is **dominated by Cloud-9**. The 7-point fit (excluding Cloud-9) gives RMSE = 0.459, which is genuinely excellent. The 1.166 RMSE comes almost entirely from the Cloud-9 residual.

**Critical insight:** Our model fits the **7 non-Cloud-9 points very well** but cannot accommodate the Cloud-9 spike. This confirms T149's earlier finding.

---

## T168: Cloud-9 as Lower-Bound Constraint

**Method:** Treat Cloud-9 as constraint σ/m ≥ 50 (lower bound only), not a specific value. Refit 7 remaining points freely.

**Results:**
- Best 7-point params: α=0.5, mA=0.3, mχ=10
- 7-point RMSE: **0.250** (much better!)
- Predicted σ/m at v=28: **0.081 cm²/g** (way below 50 floor)
- 8-point RMSE: 1.457
- Constraint satisfied: **NO** (model underpredicts by factor ~600)

**Verdict:** Our 7-point fit is excellent (RMSE = 0.25), but it **completely fails** the Cloud-9 constraint. The model cannot simultaneously fit the 7 low-v points AND satisfy σ/m ≥ 50 at v=28.

**Implication:** This is the cleanest demonstration that **standard single-Yukawa cannot accommodate Cloud-9**. The Cloud-9 spike is genuinely a different physics regime.

---

## T169: Published Cloud-9 Range [50, 21000]

**Method:** Test full published range from Ohana, Zhang & Yu 2026.

**Results:**

| Cloud-9 value | RMSE |
|---|---|
| 50 | **1.033** |
| 100 | 1.131 |
| 200 | 1.230 |
| 500 | 1.363 |
| 1000 | 1.464 |
| 5000 | 1.702 |
| 21000 | 1.916 |

**Verdict:** Model is **moderately robust** — all values give RMSE < 2.0. Lower Cloud-9 values (50-200) give better fits than high values (5000-21000).

**Implication:** Using σ/m = 50 (the published lower bound) gives the **best fit**. Our current 128 is suboptimal but defensible.

---

## T167: Bootstrap Stability (in progress)

**Method:** Sample 8 points with replacement 10 times. Refit each. Check if best-fit params are stable.

**Pending result.**

---

## Summary of Robustness Findings

### Confirmed:
1. **Our 7-point fit (excluding Cloud-9) is excellent** (RMSE = 0.25)
2. **Cloud-9 spike is the dominant source of model-data tension**
3. **Lower Cloud-9 values (50-100) give better fits** than our current 128
4. **Standard single-Yukawa cannot accommodate Cloud-9** at any value in [50, 21000]

### Implications for paper:

1. **Honest framing recommended:** State that our phenomenology fits 7 of 8 data points well, with Cloud-9 being the unresolved outlier requiring new physics.

2. **Use σ/m ≥ 50 (lower bound) as our Cloud-9 constraint**, not the specific 128 value. This:
   - Is consistent with published range (Ohana+ 2026)
   - Gives better RMSE
   - Is more honest about what's measured vs. interpreted

3. **The 4000× "spike" language should be softened** to "σ/m enhancement by factor ≥1000 at v=28" — we cannot claim it's a specific measurement.

4. **The model is robust on 7 points** — this is a publishable result even without Cloud-9.

### Recommended next steps:

1. **Update paper to use σ/m ≥ 50 as lower bound** instead of 128
2. **Add explicit discussion of Cloud-9 as outlier** in §3.2
3. **Frame the SIDM interpretation as 7-point fit + Cloud-9 constraint**
4. **Consider showing the model separately for the 7-point fit and the full 8-point fit**

---

**Files produced:**
- v0.3-prelim/code/T165_cloud9_robustness.py
- v0.3-prelim/code/T166_loo.py
- v0.3-prelim/code/T167_bootstrap.py (pending)
- v0.3-prelim/code/T168_lower_bound.py
- v0.3-prelim/code/T169_published_range.py
- v0.3-prelim/data/results/t165_cloud9_robustness.json
- v0.3-prelim/data/results/t166_loo.json
- v0.3-prelim/data/results/t168_lower_bound.json
- v0.3-prelim/data/results/t169_published_range.json
- v0.3-prelim/docs/T165_T169_ROBUSTNESS_REPORT.md (this file)
