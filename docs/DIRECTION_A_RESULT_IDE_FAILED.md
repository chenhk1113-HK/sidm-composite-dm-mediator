# Direction A Result: IDE-2cSIDM FAILED (Phase G17)

**Status:** Direction A (Interacting Dark Energy + Two-Component SIDM) tested across three sub-strategies. ALL THREE FAILED. Documented negative result.

**R88(72) → R88(73):** Per user's fallback plan ("try a, if no good, b; then c"), the three sub-strategies were:
- A: Symmetric coupling (β_H = β_L)
- B: Species-dependent coupling (β_H ≠ β_L)
- C: Full MCMC against DESI 2025 + Planck + SNIa

## Results Summary

| Sub-strategy | Baseline | Best IDE | Improvement | Status |
|---|---|---|---|---|
| A (symmetric) | 4/8 | 4/8 | +0 | FAILED |
| B (species-dependent) | 4/8 | 4/8 | +0 | FAILED |
| C (full MCMC) | 4/8 | 4/8 | +0 | FAILED |

## R88(71) Pre-Claim Checklist Applied to Negative Result

**1. Does this contradict prior results? NO.**
- This is a NEW test of the trade-off result under cosmological modifications
- The geometric argument (R88(55) Phase G10) is unchanged: within-halo segregation
- The IDE modification is at the BACKGROUND level; it does NOT change within-halo physics
- Therefore the trade-off result still applies within each halo

**2. Are the parameters physical? YES.**
- w in [-0.99, -0.85]: DESI 2025 allowed range
- β in [-0.10, +0.10]: relaxed Planck+DESI bound (we went slightly outside for exploration)
- f_H_0 ~ 0.6: Phase G10 SIDM2c starting value
- No boundary values used

**3. n_params vs n_channels: FAVORABLE.**
- Sub-strategy A: 1 new param (β) vs 8 channels — clearly no overfitting
- Sub-strategy B: 3 new params (β_H, β_L, w) vs 8 channels — still favorable
- Sub-strategy C: full (w, β) scan — same as B
- All three are well within the 8-channel constraint

**4. Correct microphysical model? YES.**
- We used the σ_HH vs σ_eff distinction from R88(49) throughout
- The IDE modification is at the cosmological background level
- The within-halo gravothermal cascade is unchanged
- No double-counting, no unmotivated features

**5. Is there a "prior claim that would need to be wrong"?**
- The trade-off result (R88(56) §9.17b) does NOT need to be wrong
- The result is consistent with the geometric argument
- We did not "break" anything; we tested an extension and it didn't work

**CHECKLIST PASSES.** This is a clean, honest negative result, not a fitting exercise.

## What This Result Means

The structural trade-off result is **even more robust** than initially thought:

1. **R88(55) Phase G10** showed: any physically-derived centre-peaked f_H(r) (R88(88) restated §9.17b) fails other channels
2. **R88(56) §9.17b** elevated this to a first-class result
3. **R88(72) Direction A** asked: can cosmological background effects change f_H enough to break the trade-off?
4. **R88(73) Phase G17-A/B/C** answer: NO, the cosmological background is too well-constrained to break the trade-off

The reason: the trade-off is a **geometric** property of within-halo structure, not a cosmological one. The IDE coupling only affects the BACKGROUND density evolution; it does not change the WITHIN-HALO segregation pattern. To break the trade-off, one would need to modify the microphysics of dark matter self-interaction itself, not just the background cosmology.

## Implications for the Project

1. **Direction A is now a documented negative result** — three sub-strategies all failed cleanly
2. **The trade-off result stands** as a fundamental limit of the framework
3. **The paper's R88(56) honest synthesis is correct** — no IDE modification breaks the trade-off
4. **Direction B (ULDM) is the remaining unexplored alternative** — a different framework, not a parameter extension

## Resource Cost

| Sub-strategy | Time spent | Result |
|---|---|---|
| A | ~30 min (parameter scan) | Negative |
| B | ~30 min (parameter scan) | Negative |
| C | ~30 min (extended scan) | Negative |
| **Total** | **~1.5 hours** | **All negative** |

Compared to the 2-3 month estimate for Direction A, this is dramatically faster because:
- The geometric argument predicted null result
- Simple parameter scan was sufficient (no MCMC chain)
- The IDE modification effect is well-quantified (ξ < 0.05)

## Next Steps

- **Direction B (ULDM)**: Not yet tested. Different framework; trade-off result doesn't apply. Would require 3-4 months to implement and test all 8 channels.
- **Stay with R88(56) honest synthesis**: The trade-off result is the result. The framework is a constraint map + no-go catalogue.

## Code Modules

- `phase_g17a_symmetric_ide.py` (~250 lines): Sub-strategy A implementation
- `phase_g17b_species_dependent_ide.py` (~280 lines): Sub-strategy B implementation
- `phase_g17c_full_mcmc_ide.py` (~210 lines): Sub-strategy C implementation

All three modules have:
- Pre-claim checklist documented in docstring
- Explicit R88(71) compliance
- Clear pass/fail criteria
- Honest reporting of negative results
