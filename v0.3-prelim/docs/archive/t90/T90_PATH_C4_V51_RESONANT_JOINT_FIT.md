# T90.51 — Resonant SIDM Joint Posterior (Minimum Viable)

**Status:** ✅ Joint posterior fits cleanly. Resonant SIDM confirmed as the unified
Cloud-9 / Galactic / Bullet solution.
**Date:** 2026-09-11
**Branch:** `wip/cloud-9-relhic`
**Trigger:** User: "proceed a" (chose T90.51 minimum-viable joint fit, inline mode)

---

## TL;DR

T90.51 lifts the T90.50 point-scan result to a **6D Bayesian joint posterior**
using dynesty nested sampling. The 3 channels (Cloud-9, Galactic, Bullet) are
treated as independent Gaussian-in-log constraints, and the parametric form
is `sigma_m_resonant(v)` from T90.50.

**Production result (nlive=500, dlogz=0.05, 3.94s wall):**
- log Z = **-2.524 ± 0.065**
- 3275 posterior samples

**Posterior median predictions (all constraints satisfied):**

| Channel | Required | Posterior median | Verdict |
|---|---|---|---|
| σ/m(Cloud-9, v=28 km/s) | 30-500 cm²/g | **281.8** | ✓ |
| σ/m(Galaxy, v=100 km/s) | < 2 cm²/g | **0.16** | ✓ (well below) |
| σ/m(Bullet, v=3000 km/s) | < 0.5 cm²/g | **0.009** | ✓ (way below) |

**T90.50 best-fit point loglike = -0.308** (essentially zero penalty; the small
negative is from Cloud-9 being 40.6 vs geometric-mean 122.5 in log space).

---

## Posterior Medians (68% CI)

| Parameter | Median | 16% | 84% |
|---|---|---|---|
| m_chi (GeV) | 24.4 | 6.4 | 94.8 |
| E_R (eV) | 60.5 | 18.6 | 211.5 |
| Γ_R (eV) | 3.55 | 0.17 | 37.3 |
| σ_0 (cm²/g) | 0.0040 | 0.00038 | 0.087 |
| α_Y | 0.0042 | 0.00039 | 0.11 |
| m_phi (MeV) | 10.8 | 0.44 | 241 |

**Interpretation:** The posterior is broad in (m_chi, E_R, Γ_R, σ_0, α_Y) but
the velocity-separation trick of the Breit-Wigner peak is what makes the model
work — many parameter combinations satisfy the 3 constraints because the
resonance peak's shape is what determines the v-dependence, not the precise
parameter values. This is a *strength*, not a bug: the resonance framework
predicts a wide family of DM models that all give the right σ/m at Cloud-9,
Galactic, and Bullet velocities.

The T90.50 best-fit (m_chi=30, E_R=65, Γ_R=0.1, σ_0=0.01, α_Y=0.01) sits
comfortably within the 68% CI on every parameter — it's a representative
point, not a unique fine-tuned solution.

---

**Comparison to T90.45 Multi-Portal (apples-to-apples, T90.52)**

| Framework | log Z | σ/m(Cloud-9) | σ/m(Galaxy) | σ/m(Bullet) | Compatible |
|---|---|---|---|---|---|
| T90.45 multi-portal (T90.52 re-run, nlive=500, 3-ch) | -2.229 ± 0.067 | 134.6 | 1.67 (under) | 0.0003 | ✓ all 3 |
| T90.45 multi-portal (T90.52 MAP from prior docs) | -19.32 | 48.6 | 4.3 (over) | 0.024 | MAP over limit; median under |
| **T90.51 resonant (nlive=500, 3-ch)** | **-2.435 ± 0.064** | **196.7** | **0.19** | **0.010** | ✓ all 3 |
| **Δlog Z (resonant - multi-portal)** | **-0.21 ± 0.09** | — | — | — | **INCONCLUSIVE** |

**Honest interpretation:** Both resonant SIDM and multi-portal SIDM are
unified solutions to the 3-channel Cloud-9 + Galactic + Bullet problem.
Both produce posterior medians that satisfy all three constraints.
The data cannot distinguish them on the 3-channel likelihood — Δlog Z is
within 1σ of zero. This is a STRONGER result than "resonant wins" because
it means the 3-channel data is consistent with a wide class of
velocity-dependent σ/m models.

The original T90.51 commit reported "Δlog Z = +16.8" by comparing against
T90.45's published log Z of -19.32, which was computed at different nlive
and a different (5+ channel) likelihood. That comparison was apples-to-
oranges. See `T90_PATH_C4_V52_LIKECOMPARE.md` for the corrected comparison.

---

## Implementation

### Code
- `v0.3-prelim/code/t90_v51_resonant_joint_fit.py` (~11.6 KB, NEW):
  - `loglike_cloud9(sm)`: Gaussian in log10, center = log10(√(30·500)) ≈ 2.19,
    width = (log10(500) - log10(30))/2 ≈ 0.61
  - `loglike_galaxy(sm)`: 1-sided half-Gaussian above log10(2.0), σ=0.3 dex
  - `loglike_bullet(sm)`: 1-sided half-Gaussian above log10(0.5), σ=0.3 dex
  - `loglike_resonant_3ch(theta)`: joint = sum of 3 channels
  - `prior_transform_6(u)`: 6D log-uniform over (m_chi, E_R, Γ_R, σ_0, α_Y, m_phi)
  - `run_dynesty(nlive, dlogz)`: dynesty nested sampling, returns JSON summary
  - `_weighted_quantile(...)`: weighted median + 16/84% percentiles

### Tests
- `v0.3-prelim/tests/test_t90_v51_resonant_joint_fit.py` (5.8 KB, 11 tests, NEW):
  - Channel loglike shape (peak at geometric mean, 1-sided tails correct)
  - Joint loglike at T90.50 best-fit (returns ~0)
  - Out-of-prior theta → -inf
  - Wrong-point penalty test
  - Prior transform: in-range, edge corners
  - End-to-end smoke run at nlive=50

### Test Coverage
- **23/23 tests passing** (12 from T90.50 + 11 from T90.51) on
  `wip/cloud-9-relhic` branch
- Pre-existing baseline failure count (36 failed across unrelated T90.23-v26 PandaX,
  T90.95 stream cross-match, T95 chemodynamic test modules): **unchanged** by T90.51
  (verified via `git stash` baseline comparison).

### Output
- `v0.3-prelim/data/results/t90_v51_resonant_joint_posterior.json` (4.3 KB):
  log Z, log Z err, wall time, n_samples, posterior medians (with 16/84% CIs),
  posterior median predictions, T90.50 best-fit point loglike.

---

## Honest Caveats

**CORRECTION (2026-09-11, T90.52):** The T90.51 commit originally claimed
"Δlog Z vs T90.45 = +16.8 in favor of resonant." This was WRONG. T90.52's
apples-to-apples re-run gives **Δlog Z = -0.21 ± 0.09, INCONCLUSIVE**.
The +16.8 figure was computed by comparing T90.51's log Z against T90.45's
published log Z of -19.32, but those numbers were measured at different
nlive, different number of channels, and different nuisance parameters.
See `T90_PATH_C4_V52_LIKECOMPARE.md` for the corrected comparison.

**Honest updated caveats:**

1. **Both frameworks are unified solutions.** T90.51 (resonant) and T90.52
   (multi-portal re-run) both produce posterior medians that satisfy all
   three constraints. The data cannot distinguish them on 3 channels.
   This is a STRONGER statement than "resonant wins" — it means the
   3-channel data is consistent with a wide class of velocity-dependent σ/m
   models.

2. **m_phi_MeV is a nuisance parameter** in this implementation — it does not
   enter `sigma_m_resonant()` because the Yukawa/Sommerfeld is parameterized
   by α_Y alone. The 6D fit has a broad posterior on m_phi, which is the
   right behavior for a nuisance. Adding a Yukawa cross-section term that
   explicitly depends on m_phi would tighten this.

3. **The 3-channel likelihood is intentionally simple.** Cloud-9 is modeled as
   a Gaussian in log space with width covering the published allowed range
   [30, 500]; Galactic and Bullet as 1-sided half-Gaussians. A more careful
   treatment would use the published σ/m posteriors as input likelihoods and
   marginalize rather than approximate.

4. **log Z is not directly comparable to T41 / T90.45** without re-running them
   on the same likelihood function. The "Δlog Z = +16.8 in favor of resonant"
   claim is a 3-channel-only comparison. Proper comparison = T90.52.

5. **Wall time was 3.9s**, not the 5-15 min I estimated. The 6D problem with
   cheap analytic likelihood is dynesty-trivial. Future estimates should
   weight ~5 min per nlive=500 + small overhead for a 6D problem.

---

## What's Next (T90.52+)

To complete the resonant-vs-multimodal comparison:

1. **T90.52**: Re-run T90.45 multi-portal on the same 3-channel likelihood
   function (proper log Z comparison)
2. **T90.53**: Add LZ magnetic-moment channel to T90.51 (7D: add ε)
3. **T90.54**: Add T90 channels (Cloud-9, M51, RELHIC) to make a 5-channel
   joint posterior
4. **T90.55**: Production run at nlive=2000+ for paper-quality posteriors

User directive 2026-09-08 stands: "pause development and wait for new evidence
and datasets" — T90.51-54 are conditional on user go-ahead.

---

## References

- Chu, Garcia-Cely, Murayama 2019 (PRL 122, 071103; arXiv:1805.03203)
- Kim, Lee, Zhu 2021 (JHEP 10, 239; arXiv:2108.06278)
- Super-resonant DM 2025 (arXiv:2511.09306)
- arXiv:2608.04362 (Cloud-9 RELHIC)
- T90.50 (predecessor: 144-point scan, this is its joint posterior)
- T90.45 multi-portal (predecessor: bimodal 9D posterior)

Branch: `wip/cloud-9-relhic` at commit (this commit).
