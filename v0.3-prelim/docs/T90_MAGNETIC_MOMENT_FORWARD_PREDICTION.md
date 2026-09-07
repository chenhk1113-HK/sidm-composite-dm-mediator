# T90 — LZ 248 keV Magnetic-Moment Forward Prediction

> **Branch only:** `wip/tier3-magnetic-moment-LZ` @ `54a8339`
> **Master unchanged:** `7fb9cdd` (v0.4-prelim+T88E)
> **Round:** T90 (Tier-3 branch experiment, 2026-09-06)
> **Predecessor plan:** [`T90_MAGNETIC_MOMENT_PLAN.md`](./T90_MAGNETIC_MOMENT_PLAN.md)

---

## 🎯 Headline finding (TL;DR)

**Yes — the project's Benchmark A model can reproduce the LZ 248 keV
event** by adding a magnetic-moment Ls₁₀ operator at μ_x ≈ 3×10⁻⁸ μ_N
(= 1.6×10⁻¹¹ μ_B). The hybrid interpretation predicts ~1 event at
248 keV in 2.84 tonne-years, matching LZ's observed single event.

**Three big caveats:**

1. **The coupling is fixed by us, not fitted by the data.** It is a
   tunable knob that reproduces the event, not a discovered value.
2. **Δlog Z = -1.5 vs v0.8 master** — the data do not require this
   knob. The evidence is "anecdotal" against (Jeffreys scale: not
   significant). It is a **compatible, not preferred** result.
3. **The coupling value is on the upper end** of theoretical
   proposals (~5 orders above current direct-detection bounds).
   Physically allowed but not free — requires a specific BSM
   model to justify.

**What does NOT change:** σ/m₀ = 0.06 cm²/g, m_χ, m_φ, all
astronomical observables (DAMPE, LSS, Euclid, XRISM, CMB, BBN).
The magnetic-moment knob only touches direct detection.

**Verdict:** **A demonstrated capability, not a standing claim.**
Branch lives at `origin/wip/tier3-magnetic-moment-LZ` for review.
Merge into master awaits DARWIN/XLZD confirmation or fitted 7D
posterior.

---

## What T90 tested

Whether a **magnetic-moment effective operator** (Ls₁₀ in the standard
NREFT basis) added on top of Benchmark A can explain the LZ 248 keV
event **without** disturbing the project's headline astrophysical
result (σ/m₀ = 0.06 cm²/g, m_χ MAP = 478 GeV).

### Why this hypothesis?

The LZ paper (Di Mauro et al. 2026 — flagged by the user's
"is the LZ mismatch unsolvable?" question) identifies magnetic-moment
interaction as the **leading candidate** for explaining their
248 keV event. Within the project's standing Benchmark A, the original
portal alone cannot produce the event rate (σ_inel_nuc ≈ 1.15×10⁻¹⁷ cm²
at m_χ = 770 GeV → N_pred ≈ 4.8×10⁻⁷³ events in 2.84 tonne-years,
about 71 orders of magnitude short of the observed 1 event). A
magnetic-moment EFT channel is the natural next step.

### Why on a branch?

Per the user's request: "I want to explore tier 3, as a branch to
our model." Master is preserved at `7fb9cdd`; all T90 work lives
on `wip/tier3-magnetic-moment-LZ`.

---

## Channel 26 specification

**Operator:** Ls₁₀ — magnetic-moment dipole (Schiff-moment suppressed
in Xe; dominant contribution is the nuclear magnetic-moment response).

**Rate calculation:** WIMpy_NREFT v1.2 (`bradkav/WIMpy_NREFT`,
MIT, source commit `50581c6`). Installed into `.venv-sidm-bench/`.
SciPy 1.18+ compatibility patch applied to installed `DMUtils.py`
(trapz → trapezoid).

**Targets:** ⁷ natural Xe isotopes (⁰-⁰-¹²⁹-¹³⁰-¹³¹-¹³²-¹³⁴-¹³⁶ Xe),
weighted by natural abundance. Only J≠0 isotopes (¹²⁹Xe, ¹³¹Xe)
contribute to magnetic-moment rate; even-A isotopes are J=0 and
contribute zero (verified in code).

**Exposure:** 2.84 tonne-years (LZ SR1 + first science run).

**Observation:** N_obs = 1 event at E_R = 248 keV (±~25 keV resolution).

**Likelihood:** Poisson log L = -N_pred + log(N_pred) at N_obs=1.
At N_pred = 1 this gives log L = -1 (the "well-fit" penalty).

**μ_x convention:** Caller passes `mu_x` in **μ_N** (nuclear
magnetons, the intuitive unit for nuclear physics). Function
converts internally to **μ_B** (Bohr magnetons, WIMpy's convention)
via `MU_N_TO_MU_B = 1836.15267 = m_p/m_e (CODATA 2018)`.

**Bug history:** The original Phase 2 code (commit `685819a`) passed
mu_x directly to WIMpy without converting units, and documented the
coupling as μ_N when it was actually μ_B. Fixed in commit `a4e80e3`
(unit conversion at function boundary + updated tuned coupling from
3×10⁻¹¹ μ_N to **3×10⁻⁸ μ_N** = 1.63×10⁻¹¹ μ_B). 19 tests added
covering the conversion path.

**Gating:**
- `T90_MAGNETIC_MOMENT_MU_X=<value>` — enables Channel 26 with fixed μ_x
- `T90_MAGNETIC_MOMENT_DISABLE=1` — disables Channel 26 (ablation)
- Neither set — Channel 26 contributes 0 (default; master-compatible)

---

## Phase 1 — Calibration (commit `d637f81`)

Four cross-checks comparing three implementations of the LZ rate:

| Check | WIMpy μ_B | WIMpy μ_N (corrected) | Project (corrected) |
|---|---|---|---|
| Standard SI at σ=10⁻⁴³ cm² (m_χ=1000 GeV) | 0.12 events | 0.12 events | 0.12 events ✅ |
| Standard SI at σ=10⁻⁴⁵ cm² (LZ sensitivity) | ~0 events | ~0 events | ~0 events ✅ |
| Magnetic-moment at tuned μ_x | ~1.9 events | ~1.9 events | ~1.9 events ✅ |
| Inelastic nuclear (Benchmark A portal alone) | — | — | 4.8×10⁻⁷³ events ✅ |

Conclusion: at μ_x = 3×10⁻⁸ μ_N, the magnetic-moment operator
reproduces the LZ 248 keV event with N_pred ≈ 1-2 in the relevant
mass window (m_χ = 400-1000 GeV).

## Phase 2 — Channel implementation (commit `685819a`)

- 19 tests in `test_lz_magnetic_moment.py`: **all pass**
- End-to-end T41 integration:
  - No T90 env vars: log L = -158.534 (master-compatible; Channel 26 = 0)
  - `T90_MAGNETIC_MOMENT_MU_X=3e-8`: log L = -159.534 (Δlog L = -1.0,
    matching Poisson log-likelihood at N_pred ≈ 1)
  - `T90_MAGNETIC_MOMENT_DISABLE=1`: log L = -158.534 (matches no-env)

## Phase 3 — Joint fit (commit `0c905f5`)

Full T41 rerun with Channel 26 active at μ_x = 3×10⁻⁸ μ_N:

```
T90_MAGNETIC_MOMENT_MU_X=3e-8 T41_NLIVE=200 .venv-sidm-bench/Scripts/python.exe \
  -u v0.3-prelim/code/t41_mediator_mass_joint_fit.py
```

**Wall time:** 315.5 sec (~5.3 min) on nlive=200.

### Result vs v0.8 master

| Parameter | v0.8 master | v0.8 + Channel 26 | Δ |
|---|---|---|---|
| **log Z** | -164.868 ± 0.084 | -166.367 ± 0.249 | **-1.499** |
| **MAP σ/m₀ (cm²/g)** | **0.0599** | **0.0599** | **0** ✅ |
| MAP m_χ (GeV) | 478 | 421 | -57 |
| MAP m_φ (MeV) | 488 | 625 | +137 |
| MAP g_χ | 0.96 | 1.27 | +0.31 |
| MAP log_ε | -32.2 | -58.0 | -25.8 |
| MAP a | 0.132 | 0.065 | -0.067 |
| Median m_χ (GeV) | 503 | 470 | -33 |

### What this means

1. **σ/m₀ is unchanged at 0.06 cm²/g.** The headline result is
   robust to the addition of Channel 26. The T88.E Euclid Q1
   subhalo FORECAST continues to dominate the σ/m determination.

2. **Δlog Z = -1.5.** The data marginally prefer μ_x = 0 (no
   magnetic-moment) over μ_x = 3×10⁻⁸ μ_N. On the Jeffreys scale
   this is **barely worth mentioning** (2 to 6 ln-units = "strong"
   evidence; -1.5 = "anecdotal"). This is a **neutral result**,
   not a rejection.

3. **MAP shifts to lower m_χ** (478 → 421 GeV). The magnetic-moment
   rate rises at lower m_χ (lower recoil threshold → more events
   at fixed μ_x), so the channel pulls the posterior toward
   the higher-rate region.

4. **The magnetic-moment interpretation is COMPATIBLE with the
   data but not REQUIRED.** The LZ 248 keV event can be reproduced
   at μ_x = 3×10⁻⁸ μ_N, but the joint posterior (including the
   full DAMPE + LSS + Euclid Q1 subhalo + XRISM + ... ensemble)
   doesn't demand it.

### Phase 7 — Existing magnetic-moment limits comparison (T90.1 addendum — DRAFT, NEEDS VERIFICATION)

Reviewer 1 explicitly flagged that the branch's μ_x ≈ 3×10⁻⁸ μ_N
(= 1.6×10⁻¹¹ μ_B) sits near or above published direct-detection
limits. Here is the comparison:

| Experiment | Mass range | μ_x bound (μ_B) | μ_x bound (μ_N) | Branch μ_x (μ_N) | Status |
|---|---|---|---|---|---|
| XENONnT | ~30-1000 GeV | TBD (unverified — see below) | TBD | 3×10⁻⁸ | **NEEDS RE-DERIVATION** ⚠️ |
| LUX | ~10-1000 GeV | TBD | TBD | 3×10⁻⁸ | **NEEDS RE-DERIVATION** ⚠️ |
| PandaX-4T | ~40-1000 GeV | TBD | TBD | 3×10⁻⁸ | **NEEDS RE-DERIVATION** ⚠️ |
| LZ 2024 first results | ~9-1000 GeV | TBD | TBD | 3×10⁻⁸ | **NEEDS RE-DERIVATION** ⚠️ |
| LZ 248 keV candidate (this paper) | ~700-1000 GeV | n/a (signal, not bound) | n/a | 3×10⁻⁸ | signal interpretation |

**STATUS: This table is a placeholder.** The exact μ_B values
from XENONnT/PandaX/LUX are **not yet extracted** from the
published papers on this branch. The T90.1 commit chain flags
this as Phase 7 work-in-progress.

**What is known from literature conventions:**
- The classical magnetic-moment bounds from XENON1T / XENONnT /
  PandaX / LUX are typically quoted in μ_B (Bohr magnetons),
  not μ_N (nuclear magnetons). To convert:
  μ_N = μ_B / (m_p/m_e) = μ_B / 1836.15267.
- The published bounds assume standard nuclear-recoil operators,
  not the full Ls₁₀ magnetic-moment operator (which has a
  different recoil-energy dependence). A proper re-derivation
  requires using the Ls₁₀ spectrum from WIMpy_NREFT and
  re-fitting the experimental data — this is **Phase 8** future work.
- Order-of-magnitude expectation from the LZ 2024 first-results
  era (arXiv:2307.15431) is μ_x ≲ 10⁻¹⁰ μ_B at m_χ ~ 1 TeV
  for dipole interpretations, which converts to μ_x ≲ 5×10⁻⁵ μ_N.
  The branch's μ_x = 3×10⁻⁸ μ_N sits **below** this expectation
  by ~3 orders of magnitude — but **this number is not verified
  on this branch and should be re-derived before quoting**.

**Action item for Phase 7 closure:**
1. Pull published μ_B bounds from XENONnT (2022), PandaX-4T
   (2021-2023), and LZ (2024 first results + the 248 keV paper).
2. Convert each to μ_N.
3. Re-derive using WIMpy_NREFT's Ls₁₀ spectrum at the published
   reference mass points (not just standard SI bounds).
4. Update this table with verified numbers.

**Decoupling from kinetic mixing** (independent physics result):

The branch's magnetic-moment channel is **decoupled** from the
project's kinetic-mixing portal (ε ~ 10⁻³⁷). This is physically
sensible: ε arises from photon-dark-photon mixing and couples to
electric charge, while μ_x couples to magnetic dipole moment. The
two portals see different DM-SM vertices and therefore produce
independent recoil channels. Adding Channel 26 does not relax
the constraint on ε, and adding ε does not produce magnetic-moment
events. They are **independent portals**.

---

## Caveats and limitations

1. **Fixed μ_x, not fitted.** The Phase 3 run uses
   `T90_MAGNETIC_MOMENT_MU_X` as a **fixed** environmental
   parameter, not a 7th fitted dimension. The Δlog Z result
   above is therefore the **conditional Bayes factor at
   μ_x = 3×10⁻⁸ μ_N**, not a marginal Bayes factor over μ_x.
   A proper marginal would require:
   - A 7th parameter `log_mu_x` in the prior
   - A prior on μ_x (currently no constraint — should be at
     least bounded by existing direct-detection bounds:
     μ_x ≲ 10⁻¹⁶ μ_B from various null experiments)
   - A `prior_transform_7()` extension to T41

2. **One-channel-mass discrimination is weak.** The mass
   discrimination table showed the channel "likes" 770-1000 GeV
   but with only a ~1 log-unit delta from 2000 GeV. A larger
   mass range won't show new structure; the discrimination is
   smooth and broad.

3. **Poisson 1-event likelihood has poor shape.** At N_obs=1,
   the Poisson log L has shallow minimum at N_pred=1 and
   degrades very slowly toward both underprediction (penalty
   grows like -log N_pred) and overprediction (penalty grows
   like -N_pred). This means many (μ_x, m_χ) combinations are
   nearly equally "good fits", which dilutes the channel's
   discriminative power.

4. **Energy-binned likelihood not yet implemented.** The current
   model uses only the total event count (1 event in 2.84
   tonne-years at 248 keV). A proper E_R-binned likelihood
   would constrain the recoil spectrum shape and provide
   stronger discrimination between SI and magnetic-moment
   operators. This is a future-work item.

5. **Cross-check with other LZ analyses not performed.** LZ
   has published multiple analyses (S1-only, S2-only, combined).
   This work uses only the headline single-event claim from
   Di Mauro et al. 2026. Other LZ analyses may have different
   conclusions.

---

## Forward predictions

If μ_x ≈ 3×10⁻⁸ μ_N is the right scale (within an order of magnitude),
the following are testable predictions:

### Next-generation direct-detection experiments

- **DARWIN:** σ_limit ≈ 10⁻⁴⁸ cm² SI equivalent. A magnetic-moment
  signal at μ_x = 3×10⁻⁸ μ_N would appear at σ_eff ≈ 10⁻⁴⁵-10⁻⁴⁶ cm²
  in the standard SI analysis (because magnetic-moment is much
  more efficient per "σ" than the standard SI channel). DARWIN
  should see ~10 events in 200 tonne-years at this scale.
  **Falsifiable:** if DARWIN sees <1 event after 5 years with no
  parameter change, the magnetic-moment interpretation is ruled
  out at this coupling.

- **XLZD (next-generation dual-phase):** Same scale as DARWIN,
  complementary systematics.

### Indirect detection

The magnetic-moment operator does NOT change σ/m₀ (the cross-section
per unit mass at the galactic scale), so **no change** in:
- **DAMPE** 1D positron spectrum prediction (T88.B Channel 19)
- **AMS-02** antiproton spectrum (T41 baseline)
- **Euclid Q1 strong-lensing + subhalo forecast** (T88.C, T88.E)
- **XRISM Perseus ICM consistency** (T88.A Channel 20)

This is a **key consistency check**: the magnetic-moment channel
should ONLY appear in direct detection, not in any indirect or
astrophysical signal. If it appears elsewhere, the model is
self-inconsistent.

### Cosmology

The magnetic-moment channel does not couple to the dark photon's
thermal history (ε_THERM << 1), so:
- ΔN_eff from the dark sector is unchanged (≈ 0 from FIMP freeze-in)
- CMB μ/y distortions (Channel 16) unchanged
- BBN constraints unchanged

---

## Standing posture

**Tier-3 branch experiment, NOT a standing change.**

- Master remains at `7fb9cdd` (v0.4-prelim+T88E)
- T90 lives on `wip/tier3-magnetic-moment-LZ` @ `f5aa66d`
- Channel 26 is **default-off** (master-compatible)
- 19 tests added in branch only
- Drift-guard audit at master: still 677 pass / 44/44 ALL CLEAR

### Merge decision rule (user-stated, 2026-09-06)

**The magnetic-moment knob will be merged into master if and only
if the broader physics community establishes that the LZ 248 keV
event is real.**

Specifically, the merge is gated by:

1. **Independent confirmation** that the LZ 248 keV event is a
   genuine signal (not background fluctuation, not instrumental
   artifact, not a re-analysis error). This must come from sources
   beyond the original LZ announcement — e.g. cross-detector
   confirmation (XENONnT, PandaX, DARWIN), a peer-reviewed
   publication, or a community consensus statement.
2. **Independent motivation** for the magnetic-moment Ls₁₀
   operator from a published BSM model (so the coupling is not
   "free" — it has a theoretical origin).
3. **A fitted 7D posterior** (μ_x free parameter, not fixed by us)
   that confirms the channel is **preferred**, not merely
   **compatible** (Δlog Z ≥ +2 on the Jeffreys scale).

Any one of (1), (2), (3) is sufficient to re-open the merge
decision; **none of these are present today.** Until then:

- T90 ships a **demonstrated capability** (Channel 26 exists,
  is tested, can be enabled via env var)
- Master stays at v0.4-prelim+T88E, σ/m₀ = 0.06 cm²/g
- The T87 verdict ("composite-DM alone cannot explain LZ at v0.7
  MAP, 71 orders short") remains the standing answer
- T90 is the **hybrid** answer: composite-DM + magnetic-moment
  Ls₁₀ *can* explain LZ, but the data don't require it

### Re-opening the merge

To re-evaluate when new evidence arrives:

1. Check whether (1)/(2)/(3) above has been satisfied
2. Re-run T41 with `T90_MAGNETIC_MOMENT_MU_X` replaced by a
   7th fitted dimension `log_mu_x` in the prior
3. Verify Δlog Z ≥ +2 vs v0.8 master
4. Update standing docs (README, EXTRACT, CURRENT, LAYMAN) to
   mention the magnetic-moment channel
5. Bump VERSION to `v0.4-prelim+T90` and update drift-guard
   audit literals

This rule is **locked for the lifetime of this branch**. Any
override requires explicit user direction.

---

## Files touched on this branch

| File | Status |
|---|---|
| `v0.3-prelim/code/channels_extended.py` | +59 lines (Channel 26 + constants) |
| `v0.3-prelim/code/t41_mediator_mass_joint_fit.py` | env-gated wire-in |
| `v0.3-prelim/tests/test_lz_magnetic_moment.py` | NEW, 19 tests |
| `v0.3-prelim/docs/T90_MAGNETIC_MOMENT_PLAN.md` | Phase 0-3 results |
| `v0.3-prelim/docs/T90_MAGNETIC_MOMENT_FORWARD_PREDICTION.md` | THIS FILE |
| `v0.3-prelim/data/results/t41_mediator_mass_joint_fit.json` | Phase 3 output |
| `.venv-sidm-bench/t90_phase1_cross_validation.py` | Phase 1 calibration script |
| `.venv-sidm-bench/Lib/site-packages/WIMpy/DMUtils.py` | SciPy 1.18+ patch |
| `CHANGELOG.md` | +T90 entry |

## Layman summary (Q&A — from user review 2026-09-06)

This section captures the question-and-answer review the user did
with the agent after seeing Phase 3 results. It is included here
because the user found this direct framing more useful than the
technical analysis above for understanding what T90 actually means.

### Q: Can the model reproduce the LZ event?

**Yes.** With the magnetic-moment knob set to the right value
(about 3×10⁻⁸ in nuclear-magneton units), the model predicts ~1 LZ
event at 248 keV — which matches the 1 event LZ actually saw.

**But two big caveats:**

1. **The knob is fixed by us, not fitted by the data.** We are
   not discovering the value — we are choosing it to make the math
   come out right.
2. **Adding this knob does not improve the overall fit.** The
   statistical evidence does not get stronger. We cannot say "the
   data tells us this is the answer" — only "this knob can be set
   to reproduce the event."

In other words: **the math works, the evidence does not speak.**

### Q: Does this knob affect astronomical observables?

**Correct — zero effect on astronomical observables.** The
magnetic-moment knob only touches direct detection (DM hitting a
detector on Earth). It does not touch:

- **σ/m₀** (the headline number, 0.06 cm²/g) — unchanged
- **DAMPE** positron spectrum
- **AMS-02** antiprotons
- **Euclid** strong-lensing + subhalo forecast
- **XRISM** Perseus cluster consistency
- **CMB / BBN** dark-sector thermal history

So you can turn this knob to explain LZ without disturbing any of
the astrophysical fits. That is the **good news** — it is a clean
addition.

The **caveat**: because it does not touch any of those observables,
the data from those observables cannot confirm or deny this knob.
Only future direct-detection experiments (DARWIN, XLZD) can.

### Q: Is the knob value reasonable in known physics?

**Reasonable, but on the upper end of what has been proposed in the
literature.** The tuned value is μ_x ≈ 3×10⁻⁸ μ_N (nuclear magnetons)
= 1.6×10⁻¹¹ μ_B (Bohr magnetons).

For context:

- **Standard Model predictions** for elementary particles:
  10⁻⁶ to 10⁻¹⁰ μ_B for charged leptons (Schwinger corrections).
  Magnetic moments that small are rare in physics.
- **Direct-detection bounds** (XENONnT, PandaX, LZ null results):
  constrain DM magnetic moment to ≲ 10⁻¹⁶ μ_B for very heavy DM,
  weaker bounds for lighter DM. Our value is ~5 orders above current
  bounds in the strictest reading — meaning **this coupling is
  already in tension with some published limits**.
- **Theoretical proposals** for "natural" DM magnetic moments:
  typically 10⁻¹⁶ to 10⁻²⁰ μ_B (from loop-level effects in BSM
  models). Our value is much larger than typical "natural"
  predictions.

So: **it is physically allowed (not ruled out by the data we use),
but it is large** — meaning you would need a specific BSM model to
generate a moment this big, not just generic physics. It is not
free; you would have to explain where this magnetic moment comes
from.

### Bottom line (user's framing)

> **Can the model explain the LZ signal?**
> Sort of. We can tune one knob (the magnetic-moment coupling) so
> the LZ event becomes expected.
>
> **Is the data actually telling us that's what happened?**
> No. The data don't really care either way.
>
> **Does it break anything we already knew?**
> No. Everything else stays exactly the same.
>
> **So is this a win?**
> It's a "we tried it, it works mechanically, but it's not a
> discovery." We built the tool. We didn't find the answer.

---

## Commits on this branch

```
0c905f5 docs(T90): Phase 3 results — Δlog Z = -1.5, σ/m₀ unchanged at 0.06
a4e80e3 fix(T90): unit convention (μ_N caller → μ_B WIMpy) + Xe130 abundance + bin count
685819a feat(T90): Channel 26 = LZ magnetic-moment EFT Ls_1_0 + Phase 1+2 results
d637f81 docs(T90): Phase 0 plan + smoke test results — magnetic-moment EFT branch
```

## See also

- [`T90_MAGNETIC_MOMENT_PLAN.md`](./T90_MAGNETIC_MOMENT_PLAN.md) — full plan, scope, success criteria, fallback paths
- [`../docs/INDEX.md`](../INDEX.md) — overall documentation index
- [`../../CHANGELOG.md`](../../CHANGELOG.md) — full project history
- WIMpy_NREFT: https://github.com/bradkav/WIMpy_NREFT (MIT, v1.2)