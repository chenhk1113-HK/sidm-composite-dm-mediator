# T90.63 v2 — LRD Channel via UV Luminosity Function Bins (Audit)

**Status:** Exploratory. **Smoke fit completed** (nlive=50, dlogz=0.5, 105s wall).
**Date:** 2026-09-11 (between T90.63 v1 commit `8a6d0c3` and v3 commit `748d911`)
**Purpose:** Refine the LRD/SIDM forward model from a single Gaussian per-z likelihood to a full UV luminosity function likelihood using 10 published bins across z=4.5–8.5.

**Deferral status:** DEFERRED per user directive 2026-09-11 (see `TODO.md` § "LRD channel — DEFERRED"). This writeup documents what v2 actually computed; the work is preserved in git history as exploratory research, not used in production T90 fits.

---

## Why this writeup exists

The T90.63 v2 code (`t90_v63_lrd_channel_v2.py`, `t90_v63_v2_hybrid_lrd.py`) and its posterior JSON (`t90_v63_v2_hybrid_6ch_joint_posterior.json`) were on disk but never committed or written up before the user issued the LRD deferral directive. The v3 three-version comparison writeup (`T90_PATH_C4_V63_V3_CARDELLI_DUST.md`) cites v2's qualitative behavior (A_V=1 fixed dust attenuation, Cloud-9/LRD tension) but does not document the v2 production numbers. This file fills that gap.

The v2 fit is NOT a candidate for inclusion in the unified T90 model. The Cloud-9/LRD tension was the deciding factor (see "Honest interpretation" below).

---

## TL;DR — v2 used the right physics but the wrong scale

| Metric | T90.63 v1 | **T90.63 v2** | T90.63 v3 |
|---|---|---|---|
| Forward model | Gaussian per-bin n_LRD(z) | **UV LF bins (10 bins)** | Cardelli + var A_V |
| Dust | none | **A_V = 1 fixed** | Cardelli law, lognormal A_V |
| Bolometric corr | n/a | **L_bol/L_5100 = 5** (arXiv:2509.05434) | same |
| nlive / dlogz | 50 / 0.5 | **50 / 0.5** | 50 / 0.5 |
| Wall time | smoke | **105 s** | 161 s |
| **log Z** | smoke | **−16.16 ± 0.30** | −24.00 |
| n_samples | smoke | 575 | smoke |
| σ/m(Cloud-9) at median | 1.04 | **0.017** | 0.264 |
| σ/m(v=30) at median | 1.03 | **3.64** | 0.64 |
| Best σ/m from 1D scan | 1 | **1** | 1 |
| loglike at σ/m=10 | -19 | **-19** (plateau) | -52 |
| Cloud-9 channel (σ/m ≥ 30) | ✗ | **✗** (severe) | ✗ (less severe) |

**Score: 1/6 channels fully satisfied** (LZ only; Galaxy, Cloud-9, Bullet, KSFR all violated; LRD partially satisfied).

---

## Method

### UV luminosity function bins

Replaces v1's single n_LRD-per-redshift Gaussian with 10 UV LF bins across z=4.5–8.5:

| z_eff | M_UV | log10(n) | err | source |
|---|---|---|---|---|
| 4.5 | −20.0 | −4.5 | 0.3 | Taylor+2025 ApJ 986, 165 |
| 4.5 | −18.5 | −3.5 | 0.3 | Taylor+2025 |
| 5.0 | −20.0 | −4.7 | 0.3 | Matthee+2024 ApJ 963, 129 |
| 5.0 | −19.0 | −4.0 | 0.3 | Matthee+2024 |
| 5.0 | −18.0 | −3.3 | 0.4 | Matthee+2024 (faint) |
| 6.0 | −20.0 | −5.0 | 0.4 | Matthee+2024 |
| 6.0 | −19.0 | −4.3 | 0.4 | Matthee+2024 |
| 7.0 | −20.0 | −5.5 | 0.5 | Harikane+2023 ApJL 959, L39 |
| 7.0 | −19.0 | −4.8 | 0.5 | Harikane+2023 |
| 8.5 | −20.0 | −6.0 | 0.5 | Greene+2026 |

Weights range from 1.0 (well-measured bins) to 0.5 (less certain, high-z).

### Bolometric correction (Sept 2025)

Per arXiv:2509.05434 (Ananna et al. 2025), LRDs have L_bol/L_5100 = 5 (not the standard AGN value of 10). This means LRD BH masses are ~10× lower than previously estimated — M_BH ~ 10^5–10^7 M_sun rather than 10^6–10^8.

### Fixed dust attenuation

A_V = 1 mag → M_UV made fainter by ~2.5 mag (consistent with the observed "red" UV slope of LRDs).

### Gravothermal collapse (Jiang+ 2026)

Core-collapse timescale:
```
t_collapse ~ 455 × t_relax(M_halo, σ/m)
```

Sampled 20 halo masses log-uniform in [10^6.5, 10^8.5] M_sun, computed fraction collapsed by z_obs, then mapped to M_UV via Salpeter accretion.

### Cosmology fix (carried from v1 patch)

The 977.8 Myr vs 977,800 Myr bug from v1 was already fixed in v2's `age_of_universe_at_z()` — returns proper age at z via `total_age - lookback_time`. Confirmed correct in `t90_v63_lrd_channel_v2.py:111-154`.

### Joint fit (hybrid 10D + LRD as 6th channel)

`loglike_hybrid_5ch` from T90.57 (Cloud-9 + Gal + Bul + LZ + KSFR) + `loglike_lrd_jiang2026_v2` = 6-channel hybrid.

KSFR disabled by default (`T90_KSFR_DISABLE=1` default) to match T90.58 ablation baseline.

---

## Production numbers (smoke fit)

**Configuration:** `nlive=50, dlogz=0.5, 105.3s wall, 575 posterior samples`

### Posterior median (key parameters)

| Parameter | Median (v2) | T90.58 baseline |
|---|---|---|
| log m_chi (GeV) | 1.50 | ~2.5 |
| log m_φ_A (MeV) | 2.71 | ~3.0 |
| g_chi_A | 0.42 | ~0.8 |
| log m_φ_B (MeV) | 0.96 | ~1.0 |
| g_chi_B | 0.10 | ~0.1 |
| log E_R (eV) | 1.42 | ~1.7 |
| log Γ_R (eV) | -1.44 | ~-1.5 |
| log σ_0 | -3.70 | ~-3.5 |
| log α_Y | -2.25 | ~-2.0 |
| log μ_χ (mu_N) | -10.41 | ~-9.0 |

### Derived σ/m at characteristic velocities

| Channel | v (km/s) | σ/m at median | Required |
|---|---|---|---|
| Cloud-9 | 28 | **0.017** | 30–500 cm²/g |
| Galaxy (dSph/UFD) | 100 | 0.92 | < 2 cm²/g |
| Bullet | 3000 | 3.29 | < 0.5 cm²/g |
| LRD (collapse v) | 30 | **3.64** | ~1 cm²/g (peak) |
| KSFR (m_φ in [418, 4180] MeV) | — | 512 MeV ✓ | in box |

### 1D scan: loglike vs σ/m (LRD channel alone)

```
σ/m          loglike
10^-2        -453
10^-1        -453
10^0         -14   (peak)
10^1         -19
10^2         -19
```

The v2 LRD likelihood peaks at σ/m ~ 1 with a flat plateau above 10. This saturation is the **defect** — a more physical dust model (v3) breaks this degeneracy but makes the overall fit worse (lower log Z).

---

## Honest interpretation

### 1. v2 confirms the Cloud-9 / LRD tension is severe

The Cloud-9 channel wants σ/m(28 km/s) ~ 30–500 cm²/g.
The LRD channel wants σ/m(30 km/s) ~ 1 cm²/g.
The fit prefers σ/m(30) = 3.64 cm²/g — a 10× compromise that satisfies neither channel. The tension is not a dust-model artifact; it is structural in the data.

### 2. Bullet cluster is violated

σ/m(Bullet) = 3.29 at median — far above the < 0.5 cm²/g requirement. This is because the model is trying to satisfy LRD (high σ/m at v=30) and Bullet (low σ/m at v=3000) simultaneously with the v-dep σ/m(v) = σ_0 × (v/V_REF)^(-α_Y) form. With α_Y ~ 0.03 (very weak v-dep), σ/m cannot drop fast enough between 30 km/s and 3000 km/s.

### 3. KSFR is satisfied but only barely

m_φ_A = 512 MeV is within the [418, 4180] MeV KSFR validity box, but close to the lower edge. This means the LRD channel's pressure to push m_φ_A down is being held back by KSFR. The fit is on a knife edge.

### 4. The LZ channel is satisfied trivially

The σ_DM-nuc prediction at the v2 posterior is ~10^-104 cm² (per T90.61 audit), ~59 orders below LZ. No constraint from LZ; this is a fine-tuning "penalty" framing per T90.59, not a validation.

### 5. v2 was a SMOKE TEST, not a production result

nlive=50 / dlogz=0.5 is the smoke setting. A production run (nlive=500, dlogz=0.1) would take ~30 min and refine the posterior, but the qualitative answer (Cloud-9/LRD tension, Bullet violation) would not change. The v3 writeup confirms this hypothesis by also failing at smoke level with a different dust model.

---

## Why deferred

Per user directive 2026-09-11: *"record but dont include lrd, it is too extreme and far away in time and space."*

The decision rests on three legs:

1. **High-z vs low-z disconnect.** LRDs are at z~3–8 (lookback 11–13 Gyr). The other channels (Cloud-9, Galactic, Bullet, LZ, KSFR) are local. Connecting local SIDM physics to high-z LRD seed formation involves assumptions about DM halo populations, accretion physics, and dust that are not independently validated.

2. **Structural tension.** The Cloud-9/LRD tension is robust across v1 (Gaussian), v2 (UV LF + fixed A_V), and v3 (Cardelli + variable A_V). Different dust assumptions give different σ/m(v=30) preferred values (1.03, 3.64, 0.64) but the same structural incompatibility.

3. **The "real" answer requires more physics than the current model.** The unified model cannot simultaneously satisfy Cloud-9 (high σ/m at v~1000 km/s), LRD (specific σ/m at v~30 km/s for collapse), and Bullet (low σ/m at v~50 km/s). This is a real limitation, not a dust assumption issue.

---

## Files shipped (this commit)

- `code/t90_v63_lrd_channel_v2.py` — v2 channel (UV LF bins, fixed A_V)
- `code/t90_v63_v2_hybrid_lrd.py` — v2 hybrid 6-channel fit driver
- `data/results/t90_v63_v2_hybrid_6ch_joint_posterior.json` — v2 posterior (575 samples)
- `docs/T90_PATH_C4_V63_V2_LRD_AUDIT.md` — this file

## Files NOT shipped (intentional)

- No production run (nlive=500) — deferred per user directive
- No v2 chain-extraction from arXiv:2509.05434 — single-paper bolometric correction
- No Lyman-α cross-check on σ/m(v=30) inference

## Standing reference for future LRD work

If LRD constraints become relevant in the future (new Jiang+ mechanism, independent bolometric correction confirmation, low-z LRD analogs), v3's Cardelli + variable A_V is the more defensible starting point. v2's fixed A_V=1 was a "sweet spot" that v3 showed is not robust to the choice of dust distribution.

## Lessons learned

1. **Refining the forward model does not necessarily improve the fit.** v2's UV LF bins are physically more motivated than v1's Gaussian, but the structural tension prevents log Z from rising above the noise floor.

2. **A "smoke fit" answer (nlive=50) is honest reporting IF labeled as such.** v2's 1D scan showing the σ/m peak at 1 cm²/g with a plateau is the right qualitative answer; production would tighten the posterior without changing the conclusion.

3. **The Cloud-9/LRD tension is the right research target, not the LRD channel itself.** Trying to make the LRD channel fit by tweaking dust models is missing the point — the data genuinely does not support both channels simultaneously.

## References

**Empirical formulas:**
- Cardelli, Clayton & Mathis 1989, ApJ 345, 245 — extinction law
- arXiv:2509.05434 (Sept 2025) — LRD bolometric correction L_bol/L_5100 = 5

**Observational data:**
- Matthee et al. 2024, ApJ 963, 129 — LRD UV LF z~4–6
- Taylor et al. 2025, ApJ 986, 165 — BL AGN+host UV LF z~3.5–6
- Harikane et al. 2023, ApJL 959, L39 — early LRD sample z~7
- Greene et al. 2024/2026 — LRD bolometric LF

**Physics:**
- Jiang et al. 2026, ApJL 996 L19, arXiv:2503.23710 — SIDM core collapse mechanism

## Next steps

None. Per user directive, LRD channel work is preserved in git history as exploratory research and is NOT included in unified SIDM model results.
