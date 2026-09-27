# T90.53–54 — Grand Unified SIDM Channel Survey + Hybrid σ/m(v) Form

**Status:** ✅ Hybrid σ/m(v) built and verified to reduce to T90.50 + T90.45 special cases.
**Date:** 2026-09-11
**Branch:** `wip/cloud-9-relhic`
**Trigger:** User: "drop t95, focus on building unified t90 first"
**Plan:** Option B (Grand Unified SIDM), T90.53-54 checkpoint first.

---

## TL;DR

Built the **hybrid parametric σ/m(v) form** that contains BOTH T90.50
(resonant) and T90.45 (multi-portal) as special cases:

  σ/m(v) = σ/m_portal_A(v) + σ/m_portal_B(v) + σ/m_resonant(v)

This is the core parametric form for Option B. It has 9 free parameters:

  θ = (m_chi, m_phi_A, g_A, m_phi_B, g_B, E_R, Γ_R, σ_0, α_Y)

**Verification:**
- Hybrid σ/m matches T90.50 exactly when portal couplings are off (`g_A = g_B = 0`)
- Hybrid σ/m matches T90.44 multi-portal exactly when resonance is off
  (`E_R → ∞, σ_0 = 0`)
- Random scan over prior: 2.4% of hybrid combinations satisfy all 3 channels
  (Cloud-9 + Galactic + Bullet). Lower than T90.50's 100% because the two
  mechanisms add constructively at low v.

**Next session:** T90.55 — wire the hybrid into a 9D dynesty joint fit on
the 3 channels. Then T90.56 — add LZ magnetic-moment. Then T90.57 — full
production + channel-set robustness sweep.

---

## T90.53 Channel Survey

Scanned all 50 `loglike_*` functions in the project. Classified each by
parametric form expected:

| Category | Count | Notes |
|---|---|---|
| Power-law (σ_m_0, a) | 20 | Standard T41 form; needs wrapper for hybrid |
| Parametric (m_chi, m_phi, g_chi, ε) | 12 | Compatible with hybrid form |
| Single-sigma (one σ_m value) | 9 | Trivial to wrap |
| Theta-wrapper (full posterior) | 9 | Wrap the whole theta |
| **Total** | **50** | |

Status breakdown:
- 47 usable
- 2 silent (documented-null audit channels: XRISM φ→γγ, ΔN_eff)
- 1 stub (Alpheus degeneracy placeholder)

**T95 streams deliberately excluded** (per user directive): they provide
σ/m predictions under a master-Yukawa parametric form, not published
observational constraints. Cannot be used as a Bayesian channel until
external σ/m observations are available (Gaia DR4 Dec 2026).

**Future channel candidates for T90.56+:**
- LZ magnetic-moment: `loglike_lz_magnetic_moment(m_chi_GeV, mu_x)`
- KSFR/PCAC validity: `loglike_ksfr_pcac_validity(theta)`
- These exist and are usable; just need to wire into the hybrid θ vector

Channel manifest: `v0.3-prelim/data/results/t90_v53_channel_manifest.json`

---

## T90.54 Hybrid σ/m(v)

### Implementation

`v0.3-prelim/code/t90_v54_hybrid_sigma_m.py` (~7.9 KB, NEW):

- `sigma_m_hybrid(v_kms, theta)` — returns dict with portal / resonant / total
- `hybrid_at_3_velocities(theta)` — convenience for the 3 canonical velocities
- `evaluate_hybrid_point(theta)` — adds channel-OK booleans + count
- `prior_transform_9(u)` — 9D unit cube → physical (mixed log/linear)
- `unpack_theta(theta_log)` — for the joint fit pipeline

### Reduction tests (the key correctness checks)

```python
# Pure resonance (g_A = g_B = 0): hybrid == T90.50
theta = (30.0, 1e6, 0.0, 1e6, 0.0, 65.0, 0.1, 0.01, 0.01)
sigma_m_hybrid(28.0, theta) == sigma_m_resonant(28.0, 30, 65, 0.1, 0.01, 0.01)  ✓

# Pure portals (E_R → ∞, σ_0 = 0): hybrid == T90.44 multi-portal
theta = (30.0, 700.0, 1.5, 5.0, 0.20, 1e10, 1e10, 0.0, 0.01)
sigma_m_hybrid(100.0, theta) ≈ sigma_m_multi_portal(100.0, ...)  ✓
```

### Random scan over prior (n=2000)

| n_channels_satisfied | Count | % |
|---|---|---|
| 3/3 (all constraints satisfied) | 48 | 2.4% |
| 2/3 (one constraint violated) | 596 | 29.8% |
| 1/3 (two constraints violated) | 825 | 41.2% |
| 0/3 (all constraints violated) | 531 | 26.6% |

**Interpretation:** The hybrid's 3-channel satisfaction rate is LOWER than
T90.50's (100% in 12/144-point scan) and T90.52 multi-portal's (also near
100% in the joint posterior median). The reason: when both mechanisms are
present, they ADD constructively at low v, so the Galactic σ/m easily
exceeds the <2 limit.

This is actually a useful result: **the hybrid model is harder to fit than
either special case**. The data has to find a parameter combination where
the portal contribution is small at v=100 km/s AND the resonance doesn't
over-amplify at v=100 km/s. The fact that 2.4% of random points do satisfy
all 3 means such combinations exist; the question is whether dynesty can
find them efficiently and whether the log Z is competitive with the
single-mechanism models.

### Tests

- `v0.3-prelim/tests/test_t90_v54_hybrid_sigma_m.py` (4.8 KB, 7 tests, NEW)
- **37/37 total tests passing** on T90.50 + T90.51 + T90.52 + T90.54

---

## What's deferred (next session)

Per the checkpoint agreement: T90.53-54 stops here. Next session picks up:

1. **T90.55** — Joint fit of hybrid 9D σ/m(v) on 3 channels (Cloud-9 + Galactic + Bullet). dynesty at nlive=500. Compute log Z hybrid, compare to T90.51 (-2.435) and T90.52 (-2.229).

2. **T90.56** — Add LZ magnetic-moment channel. Wire `loglike_lz_magnetic_moment` into the hybrid likelihood. This requires the ε kinetic-mixing parameter — which means promoting to 10D.

3. **T90.57** — Production nlive=2000 + channel-set robustness sweep (drop each channel in turn, see which results are robust).

4. **T90.58** — Report: "the unified model satisfies N out of M channels; here are the satisfied channels and the violated ones."

---

## Honest caveats

1. **Hybrid combines mechanisms ADDITIVELY.** This is the simplest combination;
   in reality a Breit-Wigner resonance and a Yukawa portal could interfere
   (coherent sum with phase), but the Born approximation we use here is
   standard in the SIDM literature.

2. **The hybrid is more parameter-rich than either special case.** 9 free
   parameters vs 6 (resonant) or 9 (multi-portal). The Bayes factor
   comparison will penalize the extra parameters via the Occam factor. If
   log Z_hybrid ≈ log Z_special_case, the special case is preferred. If
   log Z_hybrid >> log Z_special_case, the data prefers the hybrid.

3. **The 2.4% satisfaction rate is for the uninformative prior.** dynesty
   nested sampling will concentrate in the high-likelihood region, so the
   posterior mass at "3/3 satisfied" should be much higher than 2.4%.

4. **No LZ/KSFR yet.** These are the most likely channels to break the
   degeneracy between frameworks (LZ constrains multi-portal's Portal A
   kinetic mixing; KSFR constrains the resonance E_R via PCAC validity).
   Adding them is T90.56.

5. **T95 streams dropped per user directive.** Will revisit when Gaia DR4
   data arrives (Dec 2026) or when published σ/m observations become
   available for individual streams.

---

## References

- T90.50 (resonant SIDM, Breit-Wigner + Sommerfeld)
- T90.44 (multi-portal infrastructure)
- T90.40 Yukawa cross-section (`t40_yukawa_sigma_m.py`)
- T90.51 (3-channel likelihood wrapper)
- T90.52 (apples-to-apples comparison framework)
- arXiv:1805.03203 (Chu, Garcia-Cely, Murayama 2019)
- arXiv:2608.04362 (Cloud-9 RELHIC)

Branch: `wip/cloud-9-relhic` (T90.54 commit).
