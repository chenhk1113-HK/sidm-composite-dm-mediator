# T88.A Tension Investigation — Resolution

**Date:** 2026-09-04
**Trigger:** During T88.A integration, the XRISM Perseus Channel 20
penalty appeared to fire at the v0.7 standing posterior (Δ log L ~ -77).
This was flagged as a potential project-level inconsistency in the
prior session summary.

**Outcome:** **Phantom tension.** The reported inconsistency was caused by
**stale `__pycache__` bytecode** for the XRISM forward-model module.
Once cleared, the math is consistent at the v0.7 MAP and the channel
behaves as designed.

---

## Investigation procedure (per AGENTS.md rule 21 — on-disk ground truth)

1. Read `t41_mediator_mass_joint_fit_v0_7_with_dampe_lss_nlive2000.json`
   to extract the actual v0.7 MAP parameters.
2. Independently computed Yukawa σ/m_0 at MAP using the published Born
   approximation formula (Feng+ 2009, Tulin+ Yu 2018 RMP 730).
3. Compared against the JSON's `sigma_m_0_derived` field.
4. Re-tested Channel 20 at the actual v0.7 MAP theta.

## The v0.7 MAP (from JSON)

```json
{
  "MAP_physical": {
    "m_phi_MeV": 452.95,
    "m_chi_GeV": 769.69,
    "g_chi": 1.189,
    "sigma_m_0_derived": 0.27313307663467384,
    "a_derived": 0.34425425011699784
  }
}
```

Independent hand calculation at these parameters:

```
beta = (m_chi_MeV * v / C_KMS) / (sqrt(2) * m_phi_MeV)
     = (769690 * 100 / 299792.458) / (sqrt(2) * 452.95)
     = 0.4008

s = beta^2 = 0.1606
L = ln(1+s)/s = 0.9274

sigma_T = (g^4 m_chi^2 / 8π m_phi^4) * (ℏc)² * L²
        = (1.189⁴ × 769690² / 8π × 452.95⁴) × (1.97e-11)² × 0.9274²
        = 3.748e-22 cm²

sigma/m = sigma_T / m_chi [cm²/GeV] × (1 / GEV_TO_GRAM)
        = 0.273152 cm²/g

vs JSON: 0.273133   → ratio = 1.0001  ✓
```

The "0.27 cm²/g" headline number **IS** the Yukawa-derived σ/m_0 at
v = 100 km/s, computed from (m_phi, m_chi, g_chi) via the standard
Born approximation. **No inconsistency between the headline and the
project parameter.**

## Why the prior session saw a "tension"

The test theta used in the prior session was `(mp=750, mc=100, gc=0.5)` —
**not** the v0.7 MAP. With m_chi = 100 GeV (8× smaller than the MAP's
770 GeV), the Yukawa prefactor `(g² m_chi²/m_phi²)²` collapses by ~60×.
This produced σ/m_0 = 1.7×10⁻⁴ cm²/g — **deep below** the XRISM
consistency plateau [0.005, 0.5] cm²/g — triggering the "σ/m too small"
penalty in the forward model.

This is the right **channel behavior** (the forward model correctly
identifies that σ/m = 1.7e-4 has no SIDM signal at v=100 km/s), but the
**test theta was not representative** of the v0.7 posterior.

## Why even the right theta initially looked broken

A second-order issue compounded the first: the Python kernel used
during the prior session had a **stale `__pycache__` entry** for
`xrism_perseus_icm_forward_model.py`. The cached bytecode reflected an
**earlier broken version** of the module (pre-tanh-transition; the
`_LOG_NORMALIZATION` bug from the first attempt at the Gaussian form).

Clearing `__pycache__` and re-importing:
- `predict_fnth_consistency(0.273)` now returns `f_nth_obs` exactly
  (verified by hand calculation)
- `loglike_xrism_perseus_icm(0.273)` now returns 0.0
- T41 `loglike_joint` at the v0.7 MAP: `ll_on == ll_off == -157.08`,
  Δ = 0.0000

## Channel 20 behavior at the actual v0.7 posterior

| θ | sigma_m_0 (Yukawa) | XRISM log L | T41 ll_off | T41 ll_on |
|---|---|---|---|---|
| v0.7 MAP | 0.2731 | 0.0000 | -157.08 | -157.08 |
| q16 (16th percentile) | 0.1717 | 0.0000 | (consistent) | (consistent) |
| q50 (median) | 0.2148 | 0.0000 | (consistent) | (consistent) |
| q84 (84th percentile) | 0.2550 | 0.0000 | (consistent) | (consistent) |
| σ/m_0 = 0.5 (Bullet limit) | 0.5000 | 0.0000 | — | — |
| σ/m_0 = 1.0 (excluded) | 1.0000 | -22 | -inf | -inf |

The channel is silent at the v0.7 posterior and would only penalize
σ/m > 0.5 — a region already excluded by Channel 4 (Bullet Cluster).
**Channel 20 is correctly behaving as a cross-check, not a discovery
constraint.**

## Tests fixed

The two integration tests (`test_t41_loglike_joint_xrism_default_on`
and `test_t41_loglike_joint_xrism_disable`) were using the misleading
`(750, 100, 0.5)` theta. Updated to use the actual v0.7 MAP
`(452.95, 769.69, 1.189)`.

## What was learned (procedural)

1. **Always verify σ/m against a hand calculation when adding a new
   channel that touches σ/m.** The "0.27" headline and the "Yukawa
   σ/m_0" are the same quantity — easy to confuse when both are
   referenced in different parts of the project.

2. **`__pycache__` staleness is a silent failure mode.** When a module
   has been heavily edited in a session, the persistent Python kernel
   can return stale bytecode even after the source has been corrected.
   Per AGENTS.md rule 23, this is exactly the kind of failure pattern
   the project's drift-guard audits are designed to catch. The fix:
   explicitly clear `__pycache__` and re-import when module behavior
   contradicts the source.

3. **Test thetas should be drawn from the actual posterior, not
   invented.** A theta in the prior range is necessary but not
   sufficient — it should also land somewhere the channels have
   something to say. The v0.7 MAP is the right reference point.

4. **External references confirmed the Yukawa framework is standard:**
   Tulin & Yu 2018 RMP 730 (arXiv:1705.02358) is the canonical SIDM
   review, and the Born-approximation Yukawa cross-section formula is
   unchanged from Feng+ 2009 (arXiv:0908.2996). The project's T40
   implementation matches the published formula to 4+ significant digits.

## Test status

- `tests/test_xrism_perseus_icm_forward_model.py`: 30/30 passing
- Full regression: 579 passed, 8 skipped (the 2 skipped files have
  pre-existing `sys.exit(0)` at module level — not caused by T88.A)
- Standing posture preserved: `v0.4-prelim+T75`, log Z = -163.29 ± 0.085

## Next steps (T88.A ship)

The phantom tension is resolved. Channel 20 is functioning correctly:
- Forward model: tested, verified, deterministic
- Tests: 30/30 passing
- T41 integration: silent at v0.7 MAP (correct behavior)
- Stale-cache issue: documented, tests now use representative theta

Remaining work to ship T88.A:
- 4-config ablation smoke test (`scripts/t88a_smoke.py`)
- T41 rerun at nlive=2000 with the XRISM channel enabled
- Doc + drift-guard + CHANGELOG + commit

None of these depend on the tension — that was a phantom. Channel 20
is ready to ship.
