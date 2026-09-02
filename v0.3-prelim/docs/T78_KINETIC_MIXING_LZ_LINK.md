# T78 — Kinetic-Mixing Link Between σ_DM-DM and σ_DM-nucleon (v0.4-prelim)

> **Status:** Shipped 2026-09-02. Defensive doc-update + model-specific
> calculation in response to the Consider2.docx technical review of
> the T77 update.
> **Trigger:** User upload of `Consider2.docx` raising the kinetic-
> mixing concern; user direction "proceed a plus b".
> **Companion:** [T77 LZ signal update](T77_LZ_2026_09_UPDATE.md),
> [MODEL_ASSUMPTIONS §0](../../MODEL_ASSUMPTIONS_AND_LIMITATIONS.md).

## What this ships

1. **Model-specific calculation** of σ_DM-nucleon at the v0.7 posterior
   using the Kahlhoefer et al. kinetic-mixing formula. Shows that the
   project's predicted σ_DM-nuc is suppressed by **~70 orders of
   magnitude** relative to LZ sensitivity — making the kinetic-mixing
   link **practically inert** even though it is theoretically real.
2. **Refined framing** of the orthogonal-physics posture: from
   "completely orthogonal" (T77, physically overstated) to
   "practically decoupled" (T78, defensible).
3. **Pre-registered ≥3σ re-run protocol** in T77: when LZ reaches ≥3σ
   and the paper appears, fold the new σ_DM-nucleon limit into the
   existing Channel 5 (T30 LZ mapping), NOT as a new channel.
4. **Updated standing docs:** MODEL_ASSUMPTIONS §0, EXTRACT.md, and
   the T77 layman summary — all consistent with the refined framing.

## The Consider2.docx critique

The reviewer's 4 main points:

1. **"σ_DM-DM ≠ σ_DM-nucleon → completely orthogonal" is overstated.**
   In a light-mediator SIDM model, the same mediator couples to both,
   so the observables are theoretically linked.
2. **The 10²³ ratio claim is model-dependent hand-waving.** The actual
   ratio depends on ε²_γ and m_φ⁻⁴, not a fixed number.
3. **At ≥3σ, the project should pre-register what "re-run T41" means:**
   add LZ as a new channel, or fold into Channel 5?
4. **Watch XENONnT/PandaX-4T cross-checks** (already in T77).

All four points are **physically correct**. The T78 update addresses
each one.

## The kinetic-mixing calculation

### Formula (Kahlhoefer et al., arXiv:2011.03079)

For a vector mediator φ coupled to ordinary matter via kinetic mixing:

```
σ_SI_Xp = 1.5×10⁻²⁴ cm² × ε²_γ × (α_X/10⁻²) × (m_φ/30 MeV)⁻⁴
```

where:
- ε_γ — kinetic mixing parameter (small dimensionless)
- α_X — dark-sector gauge coupling (dimensionless)
- m_φ — mediator mass (MeV)

### At the v0.7 MAP (nlive=2000)

| Quantity | MAP value | Median value | Source |
|---|---|---|---|
| ε_γ (kinetic mixing) | 1.12 × 10⁻³⁷ | 1.44 × 10⁻³⁷ | 10^(log_epsilon) |
| α_X (dark-sector coupling) | 6.84 × 10⁻¹⁷ | 3.48 × 10⁻¹⁶ | 10^(log_alpha) |
| m_φ (mediator mass) | 453 MeV | 588 MeV | posterior median |
| m_χ (DM mass) | 770 GeV | 498 GeV | posterior median |
| **Predicted σ_DM-nuc** | **2.47 × 10⁻¹¹⁷ cm²** | **7.30 × 10⁻¹¹⁷ cm²** | computed |
| **log₁₀(σ_DM-nuc)** | **-116.6** | **-116.1** | |
| LZ 2024 limit @ 770 GeV | ~1.5 × 10⁻⁴⁶ cm² | (reference) | channels_extended.py |
| **Suppression factor** | **~10⁻⁷¹** | **~10⁻⁷¹** | (predicted / LZ limit) |

### Verdict

At the project's v0.7 posterior (both MAP and median):
- Predicted σ_DM-nucleon is **~10⁻¹¹⁶ cm²**
- LZ sensitivity is **~10⁻⁴⁶ cm²**
- **Difference: ~70 orders of magnitude suppression**

This means: **even if LZ confirms the 2026-09-01 signal at 5σ** and
publishes a precise σ_DM-nucleon limit, **the project's posterior
cannot be constrained** by LZ direct-detection at any reasonable
discovery significance. The kinetic-mixing link exists physically, but
the project's ε_γ ~ 10⁻³⁷ is so suppressed that LZ cannot bite.

### Reproducibility

The full calculation is in `scripts/epsilon_lz_check.py`. To reproduce:

```bash
python scripts/epsilon_lz_check.py
```

This will print the table above and write
`v0.3-prelim/data/results/2026-09-02_t78_epsilon_lz_check.json` with
the full results.

## The refined framing

**Old framing (T77, physically overstated):**
> "σ_DM-DM and σ_DM-nucleon are completely orthogonal; the LZ signal
> cannot affect σ/m under any future scenario."

**New framing (T78, defensible):**
> "σ_DM-DM and σ_DM-nucleon are theoretically linked through kinetic
> mixing. The link is practically inert at the project's v0.7
> posterior (ε ~ 10⁻³⁷), where predicted σ_DM-nucleon is suppressed
> by ~70 orders of magnitude relative to LZ sensitivity. So even
> confirmation of the LZ signal at 5σ would not change σ/m."

**Why this is the right framing:**
- It **acknowledges** the theoretical link (per the reviewer's point).
- It **quantifies** the practical decoupling with a model-specific
  calculation (not a hand-wave).
- It **preserves the project's standing posture** (rejecting direct-
  detection as σ/m constraint) but for the right reason (model-
  specific suppression, not absolute orthogonality).

## The pre-registered ≥3σ re-run protocol

Per the reviewer's point #3, the project pre-registers what "re-run
T41 at nlive=2000" means when the LZ signal reaches ≥3σ:

**Step 1:** Update `LZ_2024_LIMITS` array in `channels_extended.py`
with the new LZ limit at the relevant m_χ values.

**Step 2:** Recompute `loglike_direct_detection_exclusion` Channel 5
using the new LZ limit at the v0.7 MAP m_χ (~ 770 GeV).

**Step 3:** Re-run T41 at nlive=2000 with the updated Channel 5.

**Why fold into Channel 5 (not new channel):** The new LZ limit
constrains the same observable (σ_DM-nucleon) as the existing Channel
5 — it's a **limit update**, not a new physics observable. Adding it
as a new channel would double-count the same observable.

**Practical impact:** Even at LZ's hypothetical 5σ confirmation, the
new σ_DM-nucleon limit would not change σ/m because the project's
predicted σ_DM-nuc is suppressed by ~70 orders of magnitude relative
to LZ sensitivity. So the "re-run T41" is a defensive integrity check,
not a headline-result update.

## Files

| File | Change |
|---|---|
| `MODEL_ASSUMPTIONS_AND_LIMITATIONS.md` (MODIFIED) | §0 rewritten with kinetic-mixing link + model-specific calculation |
| `EXTRACT.md` (MODIFIED) | Top-of-doc callout softened |
| `docs/LAYMAN_SUMMARY_T77_LZ_2026_09.md` (MODIFIED) | Removed 10²³ hand-wave; added kinetic-mixing section |
| `v0.3-prelim/docs/T77_LZ_2026_09_UPDATE.md` (MODIFIED) | Added pre-registered ≥3σ re-run protocol |
| `v0.3-prelim/docs/T78_KINETIC_MIXING_LZ_LINK.md` (NEW) | This file |
| `scripts/epsilon_lz_check.py` (NEW) | Reproducible calculation |
| `v0.3-prelim/data/results/2026-09-02_t78_epsilon_lz_check.json` (NEW) | Full results |
| `CHANGELOG.md` (MODIFIED) | T78 entry |

## Drift guard

| Source | Value |
|---|---|
| VERSION | `0.4-prelim+T75` (unchanged; T78 is refinement, not version bump) |
| README.md badge | `v0.4-prelim+T75` (unchanged) |
| CITATION.cff | `v0.4-prelim+T75` (unchanged) |
| CHANGELOG.md top | `v0.4-prelim+T75` (T78 entry added below) |
| EXTRACT.md | `v0.4-prelim+T75` (refined framing) |
| MODEL_ASSUMPTIONS.md | `v0.4-prelim+T75` (refined §0) |

All 6 drift-guard sources still agree on `v0.4-prelim+T75`.

## Honest limitations

1. **The Kahlhoefer formula assumes a specific mediator coupling
   structure** (kinetic mixing with the photon). Other models
   (Z-boson mass mixing, Higgs mixing, etc.) would have different
   formulas. The project uses the kinetic-mixing form as the
   baseline; other couplings could shift the suppression factor by
   orders of magnitude in either direction.
2. **The α_X dependence** assumes the dark-sector coupling is at the
   reference value (10⁻²). At the project's posterior, α_X ~ 10⁻¹⁶,
   which further suppresses σ_DM-nucleon. The full calculation
   includes this suppression (the formula has α_X / 10⁻² explicitly).
3. **The LZ limit at 770 GeV is interpolated** from the
   `LZ_2024_LIMITS` table. The actual LZ limit at exactly 770 GeV
   may differ slightly; the suppression factor (~70 orders of
   magnitude) is dominated by ε², so small variations in the LZ
   limit don't change the conclusion.
4. **The kinetic-mixing calculation assumes a vector mediator (A').**
   The project's composite-DM model has a different microphysics
   (composite-rho, secluded A'), but the kinetic-mixing structure
   is the same — the dark photon still mixes with the SM photon via
   ε_γ.

## Provenance

> T78 defensive doc-update + model-specific calculation in response
> to the Consider2.docx technical review of the T77 update. The
> reviewer's 4 main points were:
> (1) "completely orthogonal" is physically overstated,
> (2) the 10²³ ratio is hand-wavy,
> (3) pre-register the ≥3σ re-run protocol,
> (4) watch XENONnT/PandaX cross-checks.
>
> All four are addressed in T78. The key calculation: at v0.7 MAP
> (ε ~ 10⁻³⁷), predicted σ_DM-nucleon is ~10⁻¹¹⁷ cm², suppressed
> by ~70 orders of magnitude relative to LZ sensitivity. The link
> is theoretically real but practically inert.
>
> Standing posture preserved at v0.4-prelim+T75. Implementation:
> 2026-09-02.