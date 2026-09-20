# T95.8 (Option C) — Multi-Stream Analysis with Published Gap Data

**Status:** Option C SHIPPED — **GD-1 DOMINATES the tension**
**Date:** 2026-09-07
**Branch:** `wip/tier3-magnetic-moment-LZ`
**Companion script:** `v0.3-prelim/code/t95_v24_multi_stream_analysis.py`
**Output:** `v0.3-prelim/outputs/t95/multi_stream_analysis.json`

---

## TL;DR

Combining published gap measurements from **5 stellar streams**
(GD-1, Pal 5, Orphan-Chenab, ATLAS, Styx), the T95 tension is
**almost entirely from GD-1**:
- GD-1: log L = **-12.04** (out of -12.17 total)
- Other 4 streams: log L = -0.13 (essentially consistent)
- **GD-1 contributes 99% of the negative loglik**

This means:
1. The T95 tension is essentially a **single-stream tension** (GD-1)
2. Adding more streams doesn't help much until GD-1 is resolved
3. **The Zhang+ 2025 GD-1 interpretation is the key bottleneck**

For the master Yukawa, the T95 tension with multi-stream data is
log L = -12.17 (very strong). The two-component SIDM gives -13.98
(worse). The mixture gives -17.61 (worst). **Master is the best
fit**, but only marginally.

---

## Method

### Step 1: Per-stream constraints

Compiled from published literature:

| Stream | v (km/s) | σ/m lower | σ/m upper | Reference |
|---|---|---|---|---|
| GD-1 | 10 | 30 | 100 | Zhang+ 2025 |
| Pal 5 | 30 | 0.5 | 2.0 | Carlberg 2012, Bonaca 2020 |
| Orphan-Chenab | 70 | 0.1 | 1.0 | Koposov 2019, Shipp 2021 |
| ATLAS | 90 | 0.05 | 0.5 | Shipp 2018 |
| Styx | 40 | 0.2 | 2.0 | Necib 2019 |

### Step 2: Multi-stream likelihood

Soft-box likelihood with 0.3 dex soft edges:
```
log L = 0          if σ/m in [lower, upper]
log L = -0.5 * dev^2 if σ/m outside (where dev = (log_edge - log_pred) / 0.3)
```

Combined loglik = sum over all 5 streams.

### Step 3: Comparison of models

For each stream velocity v, compute σ/m under three models:
1. **Master Yukawa** (T89 calibration)
2. **Mixture of LZ interpretations** (Option D, 47% MM + 47% HIG)
3. **Two-component SIDM** (Option A, naive mass-weighted)

---

## Results

### Master Yukawa per-stream breakdown

| Stream | σ/m predicted | [lower, upper] | loglik | % of total tension |
|---|---|---|---|---|
| GD-1 | 1.01 | [30, 100] | **-12.04** | **99.0%** |
| Pal 5 | 0.85 | [0.5, 2.0] | 0.00 | 0% |
| Orphan-Chenab | 0.74 | [0.1, 1.0] | 0.00 | 0% |
| ATLAS | 0.71 | [0.05, 0.5] | -0.13 | 1% |
| Styx | 0.81 | [0.2, 2.0] | 0.00 | 0% |
| **Combined** | | | **-12.17** | |

### Combined loglik for each model

| Model | Combined loglik |
|---|---|
| Master Yukawa | **-12.17** (best fit) |
| Mixture (Option D) | -17.61 |
| Two-component (Option A, naive) | -13.98 |

**Master Yukawa is best**, but only by a small margin (Δlog L = 1.8 over two-component). The mixture is significantly worse (-5.4 log L penalty) because it cuts σ/m at all velocities.

---

## Key Findings

### 1. The T95 tension is essentially GD-1

Adding Pal 5, Orphan-Chenab, ATLAS, and Styx only changes the
combined loglik by -0.13 (1% of the total tension). The Zhang+ 2025
GD-1 constraint alone captures **99%** of the tension.

This means multi-stream analysis doesn't help unless we resolve
GD-1 specifically.

### 2. The Zhang+ 2025 interpretation is critical

The GD-1 tension comes from a specific interpretation:
- The gap at φ₁ ~ -20° was caused by a dark subhalo
- The subhalo mass is 10^5-10^8 M_sun
- The σ/m required is in [30, 100] cm²/g

If any of these assumptions are wrong, the tension changes:
- **Gap is from baryonic perturber**: no σ/m constraint needed
- **Gap is from progenitor's own dynamics**: no subhalo needed
- **Subhalo mass different**: σ/m constraint changes
- **Stream age different**: number of expected gaps changes

### 3. Two-component SIDM is slightly worse than master

The two-component SIDM (Option A, naive) gives log L = -13.98, which
is ~1.8 log L worse than master. This is because:
- At low v (dwarf scale), the two-component σ/m is **higher** than master
- At GD-1's v=10, two-component gives 6.15 vs master's 1.01
- This is closer to Zhang+ 2025 [30, 100] but still too low
- AND it's worse at other streams (Pal 5, Orphan-Chenab, etc.)

### 4. Mixture makes things worse

The mixture (Option D) reduces σ/m at all velocities (factor 2
reduction). This:
- Slightly improves GD-1 (closer to [30, 100] lower bound... no wait, it's lower than that too)
- Worsens other streams (now below their lower bounds)
- Net effect: log L = -17.61, worse than master

---

## What this tells us

### The bottleneck is GD-1, not the multi-stream framework

For T95 tension resolution:
- **GD-1 must be resolved first** — either by better understanding
  the gap origin or by relaxing the σ/m interpretation
- Adding more streams doesn't help until GD-1 is resolved
- Gaia DR4 may bring new constraints (more streams identified,
  tighter measurements of known streams)

### Possible ways to resolve GD-1

1. **Alternative gap origin**: If the GD-1 gap is from a baryonic
   perturber (globular cluster, gas cloud), the SIDM constraint
   doesn't apply.
2. **Relaxed progenitor model**: Different progenitor mass/orbit
   changes the gap count vs σ/m relationship
3. **Dark matter alternative**: SIDM isn't the only DM model that
   predicts subhalos. Fuzzy DM, primordial black holes, etc.
4. **Stream-systematic accounting**: Bonaca+ 2025 review emphasizes
   that "no stream features have been unambiguously associated
   with a perturbation mechanism"

---

## Files

- `v0.3-prelim/code/t95_v24_multi_stream_analysis.py` (12.4 KB)
- `v0.3-prelim/tests/test_t95_v24_multi_stream_analysis.py` (4.5 KB, 13/13 pass)
- `v0.3-prelim/outputs/t95/multi_stream_analysis.json`

---

## Caveats

1. **Stream constraints compiled from literature**: The σ/m ranges
   are approximate; published values vary depending on assumptions
2. **Soft-box likelihood edges**: 0.3 dex is approximate; actual
   constraints are tighter in some places
3. **Baryonic perturbers NOT subtracted**: Could bias the σ/m constraint
5. **Gap identification systematics NOT modeled**: Some "gaps" may be artifacts
6. **Progenitor uncertainties NOT propagated**: Different progenitors
   change the gap count vs σ/m relationship

---

## References

1. Zhang+ 2025, ApJL 978, L23 (GD-1 gap, σ/m constraint)
2. Carlberg 2012, Bonaca 2020 (Pal 5 gaps)
3. Koposov 2019, Shipp 2021 (Orphan-Chenab morphology)
4. Shipp 2018 (ATLAS stream)
5. Necib 2019 (Styx stream)
6. Bonaca+ 2025, arXiv:2405.19410 (review of stream systematics)

---

## What's next

Per user directive: "proceed option d, then b, a and c."

All 4 options (D, B, A, C) have been executed. **Summary**:
- **Option D**: Partial success (cluster tension reduced by 2×, dwarf unchanged)
- **Option B**: Negative result (re-calibration worsens T95 by 3×)
- **Option A**: Negative result (basic gravothermal insufficient, t_gc ~10^14-10^17 Gyr)
- **Option C**: Diagnostic (GD-1 dominates 99% of tension)

The **T95 tension is fundamentally about the GD-1 gap interpretation**,
not about the SIDM model details. Resolving GD-1 (e.g., via Gaia DR4
in Dec 2026 or alternative gap-origin studies) is the key next step.

---

## TIME LOG

```
2026-09-07 sidm-composite-dm-mediator T95.8 Option C (multi-stream)
  ESTIMATE: 1-2 weeks of agent compute (per pattern)
  ACTUAL:   ~30 minutes of agent compute
  RATIO:    ~0.01x (massively over-estimated)
  NOTE:     SUCCESSFUL diagnostic. Confirmed that GD-1 dominates
            99% of the T95 tension. Multi-stream framework is in
            place for future use when more streams have detailed
            gap measurements. Best model is master (-12.17 log L),
            followed by two-component (-13.98), then mixture (-17.61).
```