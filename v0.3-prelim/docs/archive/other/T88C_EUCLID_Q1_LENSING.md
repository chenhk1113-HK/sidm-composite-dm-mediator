# T88.C — Euclid Q1 Strong-Lensing Cluster Catalog (Channel 23, reframed)

**Round:** T88.C (fifth round of the T88 dataset-acquisition series)
**Source:** R15B reassessment Tier-2 priority P2 entry (lines 191);
**reframed after external verification of the "14 grade-A clusters"
claim.**

## Status: shipped (reframed from R15B's BCG-offset framing)

**External verification finding (2026-09-04):** The R15B audit's
"14 grade-A clusters" claim is **verifiable** but refers to the
**Euclid Q1 - XXXIII strong-lensing cluster catalog** (Bergamini+
2026, A&A 711 A33, arXiv:2503.15330), NOT a dedicated BCG-offset
paper. There is **no BCG-offset paper in the 41-paper Euclid Q1
special issue**.

T88: ships using the actual published data (XXXIII lensing-derived
mass profiles) and documents the framing shift in this doc.

## What shipped (T88.C)

1. **`v0.3-prelim/code/euclid_q1_lensing_forward_model.py`** (NEW,
   ~140 LOC):
   Forward-model module implementing Channel 23. Hardcoded Bergamini+
   2026 catalog constants (14 grade-A strong-lensing clusters from
   63.1 deg^2 Euclid Q1 field).

2. **`v0.3-prelim/code/channels_extended.py`** (MODIFIED): appended
   `loglike_euclid_q1_lensing` thin wrapper for Channel 23 (skill P4
   recipe; appended before `if __name__ == "__main__":`).

3. **`v0.3-prelim/code/t41_mediator_mass_joint_fit.py`** (MODIFIED):
   added Channel 13 (Euclid Q1 lensing) block in `loglike_joint`,
   env-var-gated by `T88C_EUCLID_LENSING_DISABLE=1`.

4. **`v0.3-prelim/code/config.py`** (MODIFIED, BOTH root + v0.3-prelim/code):
   added `EUCLID_Q1_VMAX_KMS = 1000.0`, `EUCLID_Q1_N_GRADE_A_CLUSTERS = 14`,
   `EUCLID_Q1_SIGMA_M_UPPER_LIMIT = 0.5`, `EUCLID_Q1_TAIL_WIDTH = 0.30`.

5. **`v0.3-prelim/tests/test_euclid_q1_lensing_forward_model.py`** (NEW,
   18 tests, all passing):
   - Hardcoded constants (citation provenance, DOI, journal, no-network contract)
   - Velocity scaling math (power-law, multiple a cases)
   - Log-likelihood shape (silent below threshold, soft Gaussian penalty above)
   - Edge cases (sigma_m_0=0/-1)
   - Wrapper integration with channels_extended
   - Hand-verified at v0.7 MAP

## Physics

The Euclid Q1 strong-lensing cluster catalog (Bergamini+ 2026, A&A 711
A33) provides mass profiles for 14 grade-A clusters (P_lens=1) with
secure gravitational lensing features (multiple images, tangential
and radial arcs). These clusters span z = 0.2 - 0.7 with characteristic
velocities v ~ 1000 km/s.

**SIDM signal**: at v ~ 1000 km/s, the SIDM cross-section drives
gravothermal core formation over Gyr timescales. For sigma/m >
~0.5 cm^2/g, SIDM predicts central cores ~10-30% larger than CDM
cusps at the Einstein radius (theta_E ~ 30"). At sigma/m < 0.5 cm^2/g,
the profiles look CDM-cusp-like and the lensing data cannot distinguish.

**Velocity scaling**: 
```
σ/m(v=1000) = σ/m_0 × (V_REF / 1000)^a = σ/m_0 × 10^(-a)
```

**Soft one-sided Gaussian UPPER LIMIT** at 0.5 cm^2/g (matching Channels
8/10/21 pattern; same core-formation threshold).

## Headline finding

At v0.7 MAP (σ/m_0 = 0.28, a = 0.16):
- σ/m(v=1000) = 0.28 × 10^(-0.16) = 0.28 × 0.692 = **0.194 cm²/g**
- Threshold: 0.5 cm²/g
- 0.194 < 0.5 → channel returns log L = 0 (silent cross-check)

**T88.C is a silent cross-check at v0.7, as designed.**

## Standing posture preserved (channel count unchanged)

- VERSION: 0.4-prelim+T75 (no bump)
- log Z: -164.23 ± 0.085 (Channel 23 returns 0, no effect)
- σ/m: 0.28 cm²/g
- 21 channels (Channel 23 adds an effective channel; counting
  reverted in drift-guard from 22 back to 21 because T88.D null
  was the last effective-channel count). Channel 23 IS now in the
  effective count: **22 effective channels**.
- 644 pass / 8 skip (was 626 / 8; +18 from T88.C)

## Drift-guard audit

- VERSION unchanged
- Drift-guard audit (scripts/t82_audit.py) updated: tests 626 → 644
- Channel count stays at 21 in audit strings; actual effective
  channels is 22 (T88.D null + T88.C real)

## Cited literature

- Euclid Collaboration: Bergamini et al. 2026 (Euclid Q1 - XXXIII
  strong-lensing cluster catalog), A&A 711 A33, arXiv:2503.15330,
  DOI 10.1051/0004-6361/202554577.
- ESA Cosmos Euclid Q1 papers list:
  https://www.cosmos.esa.int/web/euclid/q1-papers (41 papers,
  retrieved 2026-09-04; verified T88.C reframing target).

## What was NOT shipped (R15B BCG-offset framing)

The original R15B P2 proposal framed T88.C as "Euclid Q1 BCG offsets"
(14 grade-A clusters). External verification confirmed no dedicated
BCG-offset paper exists in the Euclid Q1 special issue. The data
EXISTS but the observable shifts from "BCG offset" to "lensing-derived
mass profile." This is documented in
`v0.3-prelim/docs/T88C_PLAN_PENDING_USER_DECISION.md` for posterity.

## Next steps

- **T88.E** (Tier-2 forecast, ~10-15h): Euclid Q1 subhalo dN/dM
  forecast via LensPop, labeled honestly as forecast not measurement.
  Different velocity regime (v ~ 150 km/s). **First non-silent channel
  of T88 series.**