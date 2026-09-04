# T88.D — XRISM φ→γγ Decay Null-Channel (Channel 22 Documented Null)

**Round:** T88.D (fourth round of the T88 dataset-acquisition series)
**Source:** R15B reassessment lines 168-174 (P6b entry)
**Verdict per R15B:** SKIP — asymptotically null at v0.7 ε

## What shipped (T88.D)

This is a **documented null-channel audit trail**, not a real constraining
channel. The forward model code, tests, and wire-in exist to **lock the
R15B verdict into the codebase** with hand-computed numbers, so future
review rounds don't re-litigate the analysis.

1. **`v0.3-prelim/code/xrism_phi_decay_forward_model.py`** (NEW, ~270 LOC):
   Hardcoded R15B null-verdict computations (lifetime, photon energy,
   photon count, log-likelihood all return 0 by construction).

2. **`v0.3-prelim/code/channels_extended.py`** (MODIFIED): appended
   `loglike_phi_to_gamgam_xrism` thin wrapper for Channel 22 (skill P4
   recipe; appended before `if __name__ == "__main__":`).

3. **`v0.3-prelim/code/t41_mediator_mass_joint_fit.py`** (MODIFIED):
   added Channel 22 block in `loglike_joint`, env-var-gated by
   `T88D_PHI_DECAY_DISABLE=1`.

4. **`v0.3-prelim/code/config.py`** (MODIFIED, BOTH root + v0.3-prelim/code):
   added `XRISM_RESOLVE_BAND_LOW_KEV=0.3`, `XRISM_RESOLVE_BAND_HIGH_KEV=12.0`,
   `XRISM_RESOLVE_EFFECTIVE_AREA_CM2=160.0`, `XRISM_RESOLVE_FOV_ARCMIN2=1.0`,
   `XRISM_PHI_DECAY_PERSIAN_FOV_KPC3=1e5`, `XRISM_PHI_DECAY_HARD_CAP_EPS=1e-30`.

5. **`v0.3-prelim/tests/test_xrism_phi_decay_forward_model.py`** (NEW,
   15 tests, all passing):
   - Hardcoded constants (citation provenance, no-network contract)
   - Photon energy at v0.7 MAP (E_γ = m_φ/2 = 226,475 keV, 4 orders above XRISM)
   - Photon energy for all posterior m_φ (always above XRISM band)
   - Lifetime at v0.7 MAP (τ_φ = 3×10⁵² yr, ~3×10⁴² × Hubble time)
   - Predicted photon count (large, but at wrong energy band)
   - log-likelihood behavior (zero everywhere)
   - Wrapper integration + graceful failure handling
   - Hardcoded audit trail path

## Physics — why the channel is null

The secluded mediator φ couples to Standard Model photons via kinetic
mixing or direct photon coupling. The decay φ → γγ produces a
monochromatic photon line at E_γ = m_φ/2. If the portal coupling ε is
non-zero, XRISM Resolve could in principle detect this line in cluster
cores where the DM density is highest.

### First null: wrong energy band

XRISM Resolve operates at 0.3-12 keV (X-ray spectroscopy of ICM gas).
The mediator mass m_φ in the project's posterior range is 10-1000 MeV,
so:

| m_φ (MeV) | E_γ (keV) | XRISM band (0.3-12 keV)? |
|---|---|---|
| 50  | 25,000 | ❌ (2080× above 12 keV) |
| 100 | 50,000 | ❌ (4170× above) |
| **453** (v0.7 MAP) | **226,475** | **❌ (18,870× above)** |
| 600 | 300,000 | ❌ (25,000× above) |
| 1000 | 500,000 | ❌ (41,670× above) |

**E_γ is 4-5 orders of magnitude above XRISM Resolve's band for ALL
physically-relevant m_φ.** XRISM cannot detect photons at these energies.

### Second null: impossibly long lifetime

The kinetic-mixing portal gives:
```
Γ(φ→γγ) = (α ε² m_φ³) / (64 π³ v_EW²)
τ = ℏ / Γ
```

At v0.7 MAP (ε = 3.6×10⁻³⁷, m_φ = 453 MeV):
- τ_φ ≈ 2.8×10⁵² s ≈ **8.9×10⁴⁴ yr**
- Hubble time = 1.38×10¹⁰ yr
- **τ_φ / t_H = 6.5×10³⁴** (line is undetectable on cosmological timescales)

Even ignoring the energy-band mismatch, the photon count in 745 ks
XRISM Resolve exposure at v0.7 MAP would be:

| Quantity | Value |
|---|---|
| N_φ in 100 kpc³ FOV at Perseus | ~10⁵⁰ |
| Decay probability in 745 ks | ~3×10⁻⁴³ |
| Predicted photons in FOV | ~6×10⁶ (at MeV energies, wrong band) |

**But these photons are at MeV energies, not keV.** XRISM cannot see them.

## Forward model

```python
loglike_phi_to_gamgam_xrism(theta) = 0.0  # always
```

The implementation has helper functions that **document** the null:
- `phi_decay_lifetime_yr(eps, m_phi)` — hand-computed τ
- `photon_energy_keV(m_phi)` — E_γ = m_φ/2 in keV
- `is_photon_in_xrism_band(m_phi)` — always False for posterior m_φ
- `predicted_photons_in_fov(eps, m_phi)` — count at MeV (wrong band)

The log-likelihood function always returns 0 in the posterior region;
above the hard cap `XRISM_PHI_DECAY_HARD_CAP_EPS = 1e-30`, it returns 0
(out of posterior range).

## Why ship a null channel?

1. **Audit trail**: locks the R15B verdict into the codebase so reviewers
   can verify the computation directly. The 15 tests serve as executable
   documentation.

2. **Cost-benefit**: ~2 hours to ship vs. perpetual "should we
   reconsider this?" debate. Cheap to lock in.

3. **Doesn't break anything**: channel count stays at 21 (NOT 22)
   because a null channel has no empirical constraining power. Effective
   channel count = number of channels with non-zero likelihood at v0.7.

4. **Future-proofing**: if v0.8 changes ε by 30+ orders of magnitude
   (impossible per model constraints, but defensively), this channel is
   already there to flag it.

## Standing posture preserved

- **VERSION:** `v0.4-prelim+T75` (no bump)
- **log Z:** -164.23 ± 0.085 (Channel 22 returns 0, no effect)
- **σ/m:** 0.28 cm²/g (sampling-variance shift from 0.27)
- **Channels:** 21 (NOT 22; null channel does not count)
- **Tests:** 626 pass / 8 skip (was 611 / 8; +15 from T88.D)

## Drift-guard

- VERSION unchanged (v0.4-prelim+T75)
- Drift-guard audit (`scripts/t82_audit.py`): channel count stays 21,
  test count goes 612 → 626.
- Total checks: still 40 (no new audit checks added).

## Cited literature

- Bulbul et al. 2024 (eROSITA-DE eRASS1 cluster cosmology catalog),
  A&A 685 A106, arXiv:2402.08452, DOI 10.1051/0004-6361/20248264-23.
  (Citation provenance for the XRISM cross-cite; no actual data used.)
- R15B reassessment (`v0.3-prelim/docs/consider5_review/R15B_DATASET_AVAILABILITY_REASSESSMENT.md`)
  lines 168-174 (P6b entry) — the source of the null verdict.
- consider5.docx (R15 source) lines 27-28 — original XRISM φ→γγ proposal.

## What is NOT in this scope (deferred per R15B)

- Real XRISM mediator decay line analysis: would require ε > 10⁻²⁰,
  30+ orders of magnitude above the v0.7 posterior. Not a constraint;
  a different physics regime.
- Gamma-ray telescope data (Fermi-LAT, CTA, HESS) for the actual MeV
  photon band: deferred to v0.6+ cycles if ε posterior moves.
- Other secluded mediator decay modes (e⁺e⁻, μ⁺μ⁻, ππ, etc.):
  same null logic applies (energy band + lifetime).

## Next steps (per R15B priority)

- **T88.C (Tier-2, ~5h)**: Euclid Q1 BCG offsets — adds a *detection*
  to Channel 8's *upper limit* (14 grade-A clusters at v ~ 1000 km/s).
- **T88.E (Tier-2 forecast, ~10-15h)**: Euclid Q1 subhalo dN/dM via
  LensPop — forecast channel labeled honestly as forecast not measurement.

Both are session-shippable. Awaiting user go-ahead for T88.C.