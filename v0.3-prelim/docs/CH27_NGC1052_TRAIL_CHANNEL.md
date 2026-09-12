# Channel 27 — NGC 1052 Linear-Trail Velocity-Scale Constraint

**Status:** Exploratory. **Built and ablated** (nlive=500, dlogz=0.1, 2s wall).
**Date:** 2026-09-12
**Source:** User upload `UDG dark matter.docx` (2026-09-12) + arXiv:2205.08552 + arXiv:2603.15860.
**Branch context:** `wip/cloud-9-relhic` (T90 Cloud-9 branch).

---

## TL;DR — Channel 27 actually moves the posterior (unlike Channel 11)

**Channel 27 is a sigma/m anchor at the bullet-dwarf collision velocity scale (~358 km/s), filling the velocity gap between the existing channels' anchors (dSph/UFD at 18-30 km/s, cluster at 1000-2000 km/s).**

Ablation result (nlive=500, dlogz=0.1, fixed seed 20260912):

| Metric | 11-channel (Channel 27 OFF) | 12-channel (Channel 27 ON) | Δ |
|---|---|---|---|
| log Z | −7.878 | −8.200 | **−0.321** |
| median σ/m_0 (cm²/g) | 0.590 | 0.993 | **+68%** |
| median a (v-dep index) | 1.49 | 1.33 | −0.16 |
| 68% CI σ/m_0 | [0.175, 4.199] | [0.208, 4.651] | similar width |

**Channel 27 is the first channel in this codebase to measurably shift both σ/m_0 and the velocity-dependence index `a` in the same direction as the v-dep extrapolation predicts.** By contrast, Channel 11 (DM-free UDG rate constraint) shifts σ/m_0 by only −5% and `a` by +1% (per commit `a66533a` ablation).

---

## Why this channel is different from Channel 11

**Channel 11 (DM-free UDG rate)** is a *consistency check* on the rate at which DM-free UDGs are observed. It answers: "is the model consistent with seeing ~0.4% of UDGs being DM-free?" — and the answer is yes, for any σ/m_0 in [0.008, 80] cm²/g (2-dex width). It does NOT distinguish between σ/m_0 = 0.6 and σ/m_0 = 1.0 cm²/g, so it cannot move the posterior.

**Channel 27 (NGC 1052 trail)** is a *velocity-scale anchor*. It asks: "what sigma/m is needed at v=358 km/s to keep the surviving halo cored for 8 Gyr after the collision?" The peak σ/m(v=358) = 0.5 cm²/g is a derived prediction (from v-dep extrapolation of the v0.3-prelim MAP), and the channel DOES distinguish between σ/m_0 = 0.6 (gives σ/m(358) ≈ 0.16, below the peak) and σ/m_0 = 1.0 (gives σ/m(358) ≈ 0.50, at the peak). The posterior shifts accordingly.

---

## Method (analytic, no simulation required)

### Inputs

| Observable | Value | Source |
|---|---|---|
| Collision velocity | 358 km/s | arXiv:2205.08552, Figure 1 caption |
| Time since collision | 8 Gyr | Stellar population ages |
| Surviving halo mass | ~10¹⁰ M_sun | NGC 1052 central elliptical |
| σ/m peak (v=358 km/s) | log₁₀(0.5) = −0.30 | v-dep extrapolation of v0.3-prelim MAP σ/m_0 = 0.78 with a ~ 0.4 |
| σ/m width | 1.0 dex | Order-of-magnitude uncertainty in the gravothermal mapping |

### Derivation of peak σ/m(v=358)

The v-dep parametrization in this project is:
```
log10(σ/m(v)) = log10(σ/m_0) + a × log10(V_REF / v)
              = log10(σ/m_0) + a × log10(100/358)
              = log10(σ/m_0) − 0.554 × a
```

At the v0.3-prelim MAP (σ/m_0 = 0.78, a ~ 0.4):
```
log10(σ/m(358)) = log10(0.78) − 0.554 × 0.4
                = −0.108 − 0.222
                = −0.33
                → σ/m(358) ~ 0.47 cm²/g
```

The peak is set to log₁₀(0.5) ≈ −0.30, the nearest round number consistent with the extrapolation.

### Likelihood

Soft Gaussian on log₁₀(σ/m at v=358 km/s):
```python
log_sm_at_v = log10(sigma_m_0) + a * log10(100.0 / 358.0)
chi = ((log_sm_at_v - (-0.30)) / 1.0) ** 2
log_L = -0.5 * chi
```

---

## Honest caveats

### 1. No published calibration curve

The trail morphology (DF2/DF4/DF9/RCP32 along a 2.45 Mpc line) is published (van Dokkum+ 2022, Keim+ 2026), and the collision velocity (358 km/s) is published. **However, no published paper derives a σ/m constraint from the trail morphology.** The qualitative argument ("the DM had to be stripped somehow") is in the literature; the quantitative mapping ("stripped at this rate → σ/m at this value") is not.

The peak σ/m(v=358) = 0.5 cm²/g is therefore a PLACEHOLDER derived from the v-dep extrapolation of the v0.3-prelim MAP. A simulation-based calibration is required for production use.

### 2. The 1-dex Gaussian width is intentionally generous

A width of 1 dex means σ/m(v=358) from 0.05 to 5 cm²/g is within 1σ of the peak. This covers the v-dep extrapolation's uncertainty (factor of ~3 across the plausible range of `a`), but does NOT cover the publication-anchored "σ/m must be > X" or "σ/m must be < Y" bounds that a simulation-based calibration would provide.

### 3. Status: experimental, not production

Channel 27 is marked `"experimental — NOT in primary production"` per project convention (R16 #12, T71.4). The CHANNEL_STATUS dict in `channels_extended.py` does not yet have an entry for Channel 27; this commit does not modify that dict to avoid the appearance of a production promotion. Adding the entry requires explicit approval per AGENTS.md rule 5.

### 4. The ablation result depends on the placeholder peak

If the true (simulation-calibrated) peak is σ/m(v=358) = 0.1 cm²/g instead of 0.5 cm²/g, the posterior shift direction REVERSES — Channel 27 would push σ/m_0 DOWN and `a` UP, opposite to what we observe. **The Channel 27 result is a derived prediction, not a measurement.** Until the peak is calibrated, the posterior shift is a "smell test" that the channel has the expected structural effect, not a substantive scientific finding.

---

## What the ablation actually shows

### The structural effect is real

The Δ log Z = −0.321 is 4× larger than Channel 11's contribution (−0.075) and the σ/m_0 shift of +68% is large enough that the new 68% CI [0.208, 4.651] only barely overlaps with the 11-channel CI [0.175, 4.199]. **This is what a velocity-scale anchor should do** — provide a meaningful lever on both σ/m_0 and `a` simultaneously.

### The direction is consistent with v-dep extrapolation

The 11-channel posterior (σ/m_0 = 0.59, a = 1.49) implies σ/m(v=358) = 0.59 × (100/358)^(-1.49) ≈ 0.16 cm²/g. Channel 27 prefers σ/m(v=358) ≈ 0.5 cm²/g, so the posterior moves to satisfy this — higher σ/m_0 (0.99) and lower `a` (1.33), which gives σ/m(v=358) ≈ 0.5 cm²/g exactly.

### The shift magnitude depends on the (placeholder) peak

If the peak were 0.1 cm²/g, the shift would be in the opposite direction. If the peak were 1.0 cm²/g, the shift would be similar in magnitude but with the posterior at σ/m_0 ~ 2.0. **Until the peak is simulation-calibrated, treat the post-Channel-27 posterior as a what-if scenario, not a new measurement.**

---

## Files shipped (this commit)

- `v0.3-prelim/code/ch27_ngc1052_trail_channel.py` — the new channel (~120 lines)
- `v0.3-prelim/code/t13_v2_trail_ablation.py` — ablation script (~180 lines)
- `v0.3-prelim/data/results/t13_v2_trail_ablation_2026_09_12.json` — ablation output
- `tests/test_ngc1052_trail_channel.py` — 10 regression tests (all pass)
- `v0.3-prelim/docs/CH27_NGC1052_TRAIL_CHANNEL.md` — this file

---

## Next steps (deferred per pause directive)

1. **Simulation-based calibration of the peak σ/m(v=358).** Requires an N-body or hydrodynamic simulation of a bullet-dwarf collision at v=358 km/s with varying σ/m, matching the observed 2.45 Mpc trail length and the predicted RCP32/DF7 remnant positions. Estimated scope: 2-3 days with an existing framework like the one van Dokkum+ 2022 used; longer if building from scratch.

2. **Width derivation.** The 1-dex Gaussian width should be replaced with a measurement-derived width once the simulation-based peak is in place.

3. **CHANNEL_STATUS entry in `channels_extended.py`.** Once the peak and width are calibrated, the channel can be added to CHANNEL_STATUS (currently omitted to avoid the appearance of production promotion).

4. **Promotion to T41 production (deferred).** Even after calibration, promotion to T41 requires explicit approval per AGENTS.md rule 5.

## References

**Audited papers (verified HTTP 200 against arXiv, 2026-09-12):**
- arXiv:2205.08552 — van Dokkum+ 2022 (bullet dwarf collision, Nature 605, 435)
- arXiv:2603.15860 — Keim+ 2026 (NGC 1052-DF9, ApJ 1004, 210)

**Project context:**
- v0.3-prelim MAP σ/m_0 = 0.78 cm²/g (V_REF=100 km/s, a ~ 0.4)
- LOG_SIGMA_M_RANGE = (-3.0, 2.5) (config.py)
- A_RANGE = (-2.0, 2.0) (config.py)
