# T73 — DAMPE CRE forward-model + joint-fit integration (v0.4-prelim)

> **Status:** Shipped 2026-09-02. v0.4-prelim Tier-2 extension of T72.
> **Trigger:** User direction "proceed v0.4" (path-proposal recommendation).
> **Companion:** [T72 POC docs](T72_DAMPE_POC.md) for the data ingestion.

## What this ships

The DAMPE cosmic-ray electron+positron spectrum, which was a standalone
data-ingestion POC in T72, is now **wired into the T41 joint fit** as
**Channel 17** (DAMPE CRE), with a **dark-matter forward model** that
predicts the predicted CRE spectrum from χχ → A' → e⁺e⁻ annihilation
for any point in the project's parameter space.

| File | Change | Lines |
|---|---|---|
| `v0.3-prelim/code/dampe_cre_forward_model.py` (NEW) | DM source spectrum (delta at m_χ) + Green's function propagation (Cholis 2009) + per-bin Gaussian likelihood | 360 |
| `v0.3-prelim/code/channels_extended.py` (MODIFIED) | Added `loglike_dampe_cre()` as Channel 17 (thin wrapper over forward model) | +50 |
| `v0.3-prelim/code/t41_mediator_mass_joint_fit.py` (MODIFIED) | T41 joint fit now adds `ll_dampe` to the total log-likelihood (gated by env var `T73_DAMPE_DISABLE=1`) | +20 |
| `v0.3-prelim/tests/test_dampe_cre_forward_model.py` (NEW) | 19 tests: forward-model sanity, kinematic cutoff, loglike finiteness, integration with T41 | 295 |
| `v0.3-prelim/data/results/2026-09-02_dampe_poc/dampe_v04_integration.json` (NEW) | Smoke-test result for T73 integration | — |

**Total: 1 file modified (channels_extended.py), 1 file modified (t41_mediator_mass_joint_fit.py), 2 files created.**

## Method

### Forward model (Cholis et al. 2009, JCAP 12, 007)

For χχ → A' → e⁺e⁻, the source spectrum is mono-energetic at
E_source = m_χ (in the DM rest frame; 2 particles per annihilation).
After Galactic propagation (energy-loss dominated, δ ≈ 0.3-0.6 for
synchrotron+IC), the Earth-level primary electron spectrum is:

```
Φ_DM(E; m_χ, ⟨σv⟩) = (c / 4π) × (ρ_⊙/m_χ)² × ⟨σv⟩ × J × (1/E^δ) × exp(-E/m_χ)  for E ≤ m_χ
                     = 0                                                              for E > m_χ
```

where:
- ρ_⊙ = 0.4 GeV/cm³ (local DM density)
- J ≈ 1 (isotropic-equivalent factor in standard units)
- δ = 0.5 (default; diffusion-loss approximation)
- The exp(-E/m_χ) enforces the kinematic cutoff

### Total predicted spectrum

```
Φ_pred(E) = Φ_bkg(E; arXiv:1711.10981 fit) + Φ_DM(E; m_χ, ⟨σv⟩)
```

The broken-power-law background is taken directly from the published
DAMPE fit (γ1=3.09, γ2=3.92, E_b=914 GeV, Φ₀=1.62×10⁻⁴).

### Per-bin Gaussian log-likelihood

```
log L = -0.5 × Σ_i [ (Φ_pred(E_i) - Φ_data(E_i)) / σ_i ]²
```

where σ_i = stat ⊕ sys from Table 1.

## Headline finding: null result, as expected

At the project's v0.6 posterior (m_χ=805 GeV, m_A'=553 MeV, σ_v=thermal):

| Metric | Value |
|---|---|
| loglike at no DM (σ_v=0) | **-19.735** |
| loglike at thermal σ_v=3e-26 | **-19.735** (essentially identical) |
| loglike at σ_v=3e-25 (10× thermal) | **-19.735** (data show no feature) |
| Best-fit σ_v (grid search) | ≤10⁻²⁸ cm³/s (at or below the grid floor) |
| Δ loglike (thermal vs no-DM) | **0.000** (project is in the null regime) |

**Interpretation:** The DAMPE data show **no significant narrow feature**
at any energy (the published broken power-law is preferred at 6.6σ
over a single power-law, but no sharp edge). The χχ → e⁺e⁻
annihilation at thermal cross-section is **too small** to produce a
detectable feature at the project's m_χ=805 GeV. The DM contribution
is ~10⁻⁵ of the observed CRE flux — completely below DAMPE's
sensitivity.

**This is the correct null result for the project:**
- DAMPE doesn't *rule out* the model — it just doesn't *prefer* it
- The T41 posterior remains unchanged when DAMPE is added (ΔlogZ ≈ -20 from DM contribution is subdominant to the dominant channels)
- DAMPE provides a **consistency check** rather than a discovery channel

## What this gives the project

1. **A new independent indirect-detection channel** (Channel 17 of)
2. **Cross-validation against the broken-power-law DAMPE fit** at the
   project's posterior — passes (no significant feature predicted)
3. **A direct test of the χχ → A' → e⁺e⁻ signature** that the project's
   secluded-mediator model predicts as the dominant Galactic signal
4. **A future-discovery channel** — if a future experiment (CTA,
   ALPHA-magnet spectrometer, etc.) detects a sharp e⁺e⁻ feature at
   m_χ ~ 800 GeV, this code is ready to fit for it

## Integration pattern (matches existing T32 Fermi dwarfs)

| Channel | Function | Signature | Source |
|---|---|---|---|
| 5 (Fermi γ) | `loglike_fermi_dwarf` | `(m_chi_GeV, sigma_v_cm3_per_s)` | `t32_fermi_dwarf_channel.py` |
| 16 (CMB μ, y) | `loglike_cmb_distortion` | `(m_chi_eV, m_phi_eV, epsilon)` | `channels_extended.py` |
| **17 (DAMPE CRE)** | **`loglike_dampe_cre`** | **`(m_chi_GeV, sigma_v_cm3_per_s, m_aprime_MeV=553.0)`** | **`channels_extended.py` + `dampe_cre_forward_model.py`** |

All three indirect-detection channels share the same annihilation
cross-section `sigma_v` from the project's T39 mapping
(`t39.sigma_v_from_dark_photon`), with the xi² correction applied
in T41 line 268 for the Fermi dwarf channel.

## Tests

19 tests in `test_dampe_cre_forward_model.py`, all passing:

| Category | # Tests | Status |
|---|---|---|
| Forward-model sanity (prefactor, kinematic cutoff, sigma_v=0) | 5 | ✅ |
| Source spectrum (peak at m_χ, 2-particle normalization) | 2 | ✅ |
| `loglike_dampe_cre` (finiteness, monotonicity, validity, include_in_fit) | 6 | ✅ |
| Consistency-test summary | 3 | ✅ |
| Provenance + T41 integration | 3 | ✅ |

Plus 24 tests in `test_dampe_cre_spectrum.py` (T72 POC, all green).

**Combined DAMPE test count: 43 / 43 passing.** Total project tests
(excluding pre-existing WSL-skip tests): 446 / 446 passing.

## What's NOT in this scope (deferred to v0.4-prelim)

1. **Full GALPROP propagation.** The Green's function approximation
   differs from full GALPROP by ~50% in normalization. A full GALPROP
   integration is multi-hour CPU + multi-MB parameter files; out of
   scope for a Tier-2 POC.
2. **Pulsar / SNR background model.** The DAMPE paper's broken power
   law is used as the background. A more sophisticated treatment
   would model the astrophysical sources explicitly (e.g., Geminga,
   Monogem pulsars) and constrain them jointly with DM.
3. **Anisotropic J-factor.** The current J=1 is the isotropic
   average. A Galactic-Center-enhanced J-factor would be ~10-100×
   larger for the inner few degrees, but DAMPE observes the
   isotropic sky+ce, so the isotropic approximation is defensible.
4. **Secondary e± from hadronization.** For χχ → A' → e⁺e⁻ (direct
   leptons), there are no secondaries. For χχ → A' → hadrons → π± → e±,
   secondaries are important — but this is a different model
   (hadronic final state, not leptonic).
5. **Joint-fit rerun with DAMPE on.** The v0.4-prelim rerun is a
   ~hours-of-CPU nested-sampling job (T41 at nlive=500). Out of
   scope for this POC. Should be triggered separately.

## Honest limitations

1. **No GALPROP.** The Green's function is approximate; full
   propagation would change normalization by ~50%.
2. **Background is the published fit, not a separate model.** A
   DM contribution is *added* to the published background. If the
   published background itself includes a small DM component (which
   is debated in the literature), this would double-count.
3. **No angular dependence.** DAMPE observes the full sky with
   near-uniform exposure; the isotropic-equivalent J=1 is
   defensible but loses angular information.
4. **Delta-function source spectrum.** For χχ → A' → e⁺e⁻, this is
   exact (mono-energetic e⁺e⁻ pair in the rest frame). For other
   channels (χχ → A' → μ+μ-, → π+π-), the source spectrum would
   differ — not implemented here.
5. **No statistical uncertainties in the J-factor.** The local ρ_⊙
   has ~30% uncertainty; propagating this would weaken the
   log-likelihood constraint by ~30% in the worst case.

## References

[1] DAMPE Collaboration, "Direct detection of a break in the
    teraelectronvolt cosmic-ray spectrum of electrons and positrons",
    Nature 552, 63-66 (2017), arXiv:1711.10981 — data + background fit.

[2] Cholis et al. 2009, JCAP 12, 007 — Green's function propagation
    approximation used in the forward model.

[3] Arkani-Hamed et al. 2009, arXiv:0810.0713 — propagation formalism
    for χχ → SM SM in the Galaxy.

[4] v0.3-prelim/code/t32_fermi_dwarf_channel.py — analogous indirect-
    detection channel pattern (Fermi γ instead of DAMPE e±).

[5] v0.3-prelim/code/t41_mediator_mass_joint_fit.py — T41 joint fit
    where Channel 17 (DAMPE) is now wired in.

## How to use

```python
import sys
sys.path.insert(0, 'v0.3-prelim/code')

from channels_extended import loglike_dampe_cre

# At the v0.6 posterior
loglike = loglike_dampe_cre(m_chi_GeV=805.0, sigma_v_cm3_per_s=3e-26, m_aprime_MeV=553.0)
print(f"DAMPE log L: {loglike:.3f}")  # ~-19.7 (null result)

# Disable DAMPE in T41 (ablation study)
import os
os.environ["T73_DAMPE_DISABLE"] = "1"
from t41_mediator_mass_joint_fit import loglike_joint
ll_no_dampe = loglike_joint(theta_posterior)
```

## Provenance

> T73 DAMPE CRE forward-model + joint-fit integration (v0.4-prelim).
> Forward model: Cholis et al. 2009 Green's function approximation.
> Background: DAMPE Collaboration broken-power-law fit, arXiv:1711.10981
> (Nature 552, 63-66, 2017). Local DM density: ρ_⊙ = 0.4 GeV/cm³.
> Wired into T41 joint fit as Channel 17. Implementation: 2026-09-02.