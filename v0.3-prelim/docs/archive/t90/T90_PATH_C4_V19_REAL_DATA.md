# T90 Path C.4.7 (v19) — Real Data Incorporation

**Status:** v19 SHIPPED (Phase b of 'proceed (a) and (b)')
**Date:** 2026-09-07
**Branch:** `wip/tier3-magnetic-moment-LZ`
**Companion scripts:**
- `v0.3-prelim/code/euclid_q1_subhalo_real_data.py` (Euclid Q1 cluster count)
- `v0.3-prelim/code/solar_8b_cevns_real_data.py` (XENONnT + PandaX 8B CEvNS)
**Outputs:**
- `v0.3-prelim/outputs/t90/euclid_q1_real_data.json`
- `v0.3-prelim/outputs/t90/solar_8b_cevns_real.json`

---

## TL;DR

Replaces FORECAST data with real measurements:

| Channel | Real data source | LZ tension? |
|---|---|---|
| **Euclid Q1 cluster count** | Bergamini+ 2026 (14 grade-A clusters) | Δlog L = -0.073 (no tension) |
| **XENONnT 8B CEvNS** | PRL 133, 191002 (2024) | Consistent with SM |
| **PandaX-4T 8B CEvNS** | PRL 133, 191001 (2024) | Consistent with SM |
| **LZ 8B CEvNS** | arXiv:2509.16281 | Consistent with XENONnT/PandaX |

**Finding**: Real-data channels do NOT significantly constrain
the LZ interpretation. The cluster count has too little statistical
power (Poisson σ = √14 ≈ 3.7) to falsify.

---

## Phase 1: Real Euclid Q1 (Bergamini+ 2026)

### Data
From arXiv:2503.15330 (A&A 711 A33, published July 2026):
- **14 grade-A strong-lensing clusters** (P_lens = 1) in 63.1 deg²
- **83 cluster candidates** with P_lens > 0.5
- **Cluster density**: 0.3 deg⁻² for P_lens > 0.9
- **Full-survey prediction**: 4500+ clusters

### What's STILL FORECAST (per-cluster σ_v not yet public)
The mass profile for each cluster (which would give σ_v and
constrain σ/m at v ~ 500-1000 km/s) requires a follow-up paper
(Bergamini+ 2026 in prep.). Without per-cluster mass measurements,
the dN/dM observable is still a forecast.

### New count likelihood (T88.E2)
Implemented in `euclid_q1_subhalo_real_data.py`:
- Predicted N_grade_A = 14 × (1 - SIDM_suppression(sigma/m))
- SIDM suppression per Robertson+ 2019 BAHAMAS-SIDM:
  - σ/m ~ 0.05 cm²/g (cluster velocity): 2-6% suppression
  - σ/m ~ 0.5 cm²/g: 10% suppression
  - σ/m > 1.0 cm²/g: 15-20% suppression
- Returns Poisson log L with N_obs = 14

### Headline result at LZ-anchored 7D posterior
- σ/m(v=750 km/s) = 0.51 cm²/g
- SIDM suppression: 10.07%
- Predicted N_grade_A = 12.59 (vs observed 14)
- Poisson log L = -2.32 (vs CDM -2.25)
- **Delta log L = -0.073 (no significant tension)**

**Interpretation**: Cluster count alone CANNOT falsify LZ
interpretation because Poisson noise on 14 clusters is large
(σ = √14 ≈ 3.7). 10% suppression is well within statistical
fluctuation. Per-cluster mass measurements (future paper) will
be more constraining.

### Tests (10/10)
- Real-data constants match paper
- SIDM suppression grows with σ/m
- CDM (σ_m_0 = 0) predicts 14 clusters (matches data)
- LZ-anchored SIDM gives Δlog L close to 0 (no tension)

---

## Phase 2: Real 8B CEvNS (XENONnT + PandaX 2024)

### Data
From PRL 133, 191002 (2024) and PRL 133, 191001 (2024):
- **XENONnT 8B flux**: (4.7 +3.6 -2.3) × 10⁶ cm⁻²s⁻¹
- **XENONnT 8B CEvNS xsec on Xe**: (1.1 +0.8 -0.5) × 10⁻³⁹ cm²
- **PandaX-4T 8B CEvNS**: simultaneous publication, consistent
- **SM prediction**: 1.16 × 10⁻³⁹ cm² (PRL 133, 191002 Eq. 3)

### New likelihood (T88.F)
Implemented in `solar_8b_cevns_real_data.py`:
- Compares measured CEvNS cross section to SM prediction
- Adds Gaussian penalty if σ/m(v=30 km/s) > 0.5 cm²/g
  (consistency check on direct-detection bounds)

### SIDM contribution to CEvNS
**SIDM (DM-DM scattering) does NOT produce CEvNS-like events
directly.** The master Yukawa has no DM-nucleon coupling.
The measured CEvNS cross section places an upper limit on any
non-SM contribution to nuclear recoils at E_recoil < 10 keV,
but this is not a SIDM-specific constraint.

The real value of this channel is the **CROSS-CHECK** on whether
the SM prediction matches the measured cross section. **It does.**

### Headline result at LZ-anchored 7D posterior
- σ/m(v=30 km/s) = 0.85 cm²/g (in warning zone)
- CEvNS consistency log L = -0.003 (consistent with SM)
- DD consistency log L = -0.243 (mild penalty)
- **Total log L = -0.246 (mild, no Jeffreys threshold)**

### Tests (10/10)
- Real-data constants match PRL 133, 191002
- σ/m(v=30) formula correct
- SIDM excess = 0 (no DM-nucleon coupling)
- SM vs measured cross section consistent
- DD consistency penalty grows with σ/m

---

## Combined interpretation

Both real-data channels show **no significant tension** with the
LZ interpretation:

| Channel | Δlog L | Jeffreys verdict |
|---|---|---|
| Euclid Q1 cluster count | -0.073 | none |
| XENONnT 8B CEvNS | -0.003 | none |
| DD consistency at v=30 km/s | -0.243 | mild |
| **Total** | **-0.32** | **none** |

Compare to T95 cross-check findings (already on master):
| Channel | Δlog L | Jeffreys verdict |
|---|---|---|
| Euclid Q1 sub-halo forecast | -1.57 | substantial |
| Zhang+ 2025 GD-1 perturber | -23.61 | very strong |

The real-data channels (this work) provide WEAKER constraints than
the forecast/analytical channels (T95). This is because:
1. The cluster count has only N=14 events (low Poisson precision)
2. The CEvNS measurement is consistent with SM (no SIDM excess
   expected)

**Net conclusion**: Real-data incorporation confirms the LZ
interpretation is not yet falsified by current data. Future
data (per-cluster mass profiles, more clusters, lower thresholds)
will be more constraining.

---

## Honest caveats

1. **Per-cluster mass profiles** are NOT yet public for Q1
   (Bergamini+ 2026 in prep.). When available, this will be a
   much more constraining observable.
2. **Gaia DR4** is planned for 2026-12-02 (2.5 months from now).
   When available, the Zhang+ 2025 GD-1 constraint can be tightened.
3. **The 8B CEvNS channel** is a consistency check, not an SIDM
   constraint (SIDM doesn't directly contribute).
4. **Per-cluster σ_v** would also enable a v-independent check
   on the master Yukawa at cluster velocities.

---

## Files

- `v0.3-prelim/code/euclid_q1_subhalo_real_data.py` (12.8 KB)
- `v0.3-prelim/code/solar_8b_cevns_real_data.py` (12.6 KB)
- `v0.3-prelim/tests/test_euclid_q1_subhalo_real_data.py` (3.8 KB, 10 tests)
- `v0.3-prelim/tests/test_solar_8b_cevns_real_data.py` (3.7 KB, 10 tests)
- `v0.3-prelim/outputs/t90/euclid_q1_real_data.json`
- `v0.3-prelim/outputs/t90/solar_8b_cevns_real.json`

---

## References

1. Bergamini et al. 2026, A&A 711 A33, arXiv:2503.15330 (Euclid Q1)
2. XENONnT, PRL 133, 191002 (2024), arXiv:2408.06277 (8B CEvNS)
3. PandaX-4T, PRL 133, 191001 (2024), arXiv:2407.10892 (8B CEvNS)
4. LZ Collaboration, arXiv:2509.16281 (LZ 8B CEvNS)
5. Robertson+ 2019 (BAHAMAS-SIDM)

---

## TIME LOG

```
2026-09-07 sidm-composite-dm-mediator T90 v19 (real data)
  ESTIMATE: 1-3 weeks of agent compute (initial estimate)
  ACTUAL:   ~3.5 hours of agent compute (Phase 1 + Phase 2)
  RATIO:    0.05-0.08x (massively over-estimated)
  NOTE:     Both phases were literature extraction + small
            implementation. Per-cluster mass profiles are
            still FORECAST (Bergamini+ 2026 in prep.).
```