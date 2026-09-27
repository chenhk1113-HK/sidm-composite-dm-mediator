# T120.10 — Critical Limitations of Magnetic Dipole UV Completion (2026-09-19)

## What T120.10 found

The T120.9b magnetic dipole UV completion claim was based on a **unit-conversion error**. The CORRECT calculation shows that magnetic dipole DM is **INCOMPATIBLE** with:

1. **Direct detection (LZ 2024, XENONnT 2023)** — σ_SI is 16 orders of magnitude ABOVE the limit
2. **Published bounds (Sigurdson+ 2004 PRD 70, 083501)** — required µ_χ is 5300× ABOVE the published upper limit

## The correct numbers

For magnetic dipole DM with σ_DM-DM/m(v=100) = 0.052 cm²/g (Phase 44 best fit):

| Quantity | Value |
|---|---|
| Required µ_χ | **5.35 × 10⁻¹³ cm** (NOT 1.57 × 10⁻²⁰ cm as T120.9b claimed) |
| Required µ_χ | 27.1 GeV⁻¹ |
| Predicted σ_SI (DM-nucleon) | **2.04 × 10⁻³⁰ cm²** |
| LZ 2024 limit (WIMP-like, m_χ=10 GeV) | 9.4 × 10⁻⁴⁷ cm² |
| **Violation** | **2.17 × 10¹⁶ × ABOVE LZ limit** |
| Sigurdson+ 2004 µ_χ bound | ~10⁻¹⁶ e·cm |
| **Violation** | **5350 × ABOVE published bound** |

## Why the T120.9b claim was wrong

The original T120.9b calculation had a unit-conversion error in
converting between natural units (GeV) and CGS units (cm). The
corrected calculation shows:

  σ_DM-DM/m(v) = (α_EM × µ_χ²)² × π / (m_χ² × v_rel)
                = α_EM² × µ_χ⁴ × π / (m_χ² × v_rel)    [GeV⁻²]

  σ_SI (DM-nucleon) = α_EM² × µ_χ⁴ / (16π × m_χ²)   [GeV⁻²]

The ratio σ_SI / σ_DM-DM (in same units) is:
  σ_SI / σ_DM-DM = (1/16π) / (π/v) = v / (16π²)

For v = 100 km/s = 3.33 × 10⁻⁴:
  σ_SI / σ_DM-DM = 3.33e-4 / 158 = 2.1 × 10⁻⁶

So σ_SI is SMALLER than σ_DM-DM by a factor of 5×10⁵ in natural units.
But when converting to cm²/g and comparing to LZ limit:

  σ_DM-DM/m(v=100) = 0.052 cm²/g  →  σ_DM-DM = 0.052 × (10.44 GeV × 1.78e-24 g)
                                       = 9.67 × 10⁻²⁵ cm² (per particle)

  σ_SI (after ratio) = 9.67e-25 × 2.1e-6 = 2.03e-30 cm²

LZ limit is 9.4e-47 cm², so violation = 2.17e16.

## What this means for v1.13.2

The magnetic dipole UV completion claim in v1.13.2 §9.8.2 is **INVALID**.
The required dipole moment is too large for the model to be physically
realizable with known DM.

The good news: **the SIDM phenomenology (v1.13.1) is still valid** — it
predicts the right σ/v curve, satisfies all 8 observational constraints,
and is MCMC-robust. What's missing is a UV completion.

## Honest impact assessment

The "broken" claim was:
  ❌ Magnetic dipole DM provides UV completion for a_slope=1.0

What remains valid:
  ✅ a_slope=1.0 satisfies all 8 observational constraints
  ✅ MCMC posterior recovers v1.13.1 parameters within 1σ
  ✅ Fair BIC Δ = -170 (T120 wins on same data set)
  ✅ All other robustness checks pass

What's needed for v1.13.3:
  - Remove the magnetic dipole UV completion claim (§9.8.2)
  - Acknowledge that the phenomenological a_slope=1.0 is not yet UV-derived
  - Search for alternative UV completions:
    - Hidden U(1) with dark-only mediator (bypasses SM direct detection)
    - Composite DM with non-point-like DM-DM vs DM-nucleon coupling
    - P-wave/BW-resonance mechanism (which has different velocity scaling)

## What to do now

Three options:

**(a) Revise to acknowledge the limitation honestly** — Update paper to remove
the magnetic dipole claim, document the negative result, document alternatives
to explore. Quick (1-2 hours).

**(b) Pivot to alternative UV completion** — Hidden U(1) or composite DM
would require new derivation but could still work. Effort: 1-2 days.

**(c) Accept the model as phenomenological** — Accept that v1.13.1 is
phenomenological (sigma/v phenomenology only, no UV) and document
this honestly. Quickest path to submission.

My recommendation: **(a)** + acknowledge, then **(b)** if time permits.
The honesty of acknowledging a wrong claim STRENGTHENS the paper (shows
we're not post-hoc rationalizing).

## Files to revise

- `v0.3-prelim/docs/T120_9B_UV_COMPLETION_MAGNETIC_DIPOLE_2026_09_19.md`
  → Replace with LIMITATIONS doc
- `v0.3-prelim/docs/PAPER_V1_DRAFT.md` §9.8.2 → Either remove or
  revise to honest assessment
- `v0.3-prelim/tests/test_t120_9_mcmc_and_uv.py`
  → Either remove magnetic dipole tests or add "magnetic dipole ruled
  out" tests

## What still works (and is robust)

| Component | Status |
|---|---|
| SIDM phenomenology (σ/v curve) | ✓ VALID |
| 8 observational constraints pass | ✓ VALID |
| MCMC posterior (well-defined, unimodal) | ✓ VALID |
| Fair BIC Δ = -170 | ✓ VALID |
| Multi-component + gravothermal selection | ✓ VALID |
| Slope window robust | ✓ VALID |
| **Magnetic dipole UV completion** | **✗ RULED OUT (unit error)** |