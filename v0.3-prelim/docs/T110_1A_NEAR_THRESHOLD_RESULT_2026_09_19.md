# T110.1A — Near-threshold RSIDM Parameter Mapping

**Date**: 2026-09-19
**Branch**: wip/RSIDM-near-threshold
**Sub-task**: T110.1A (literature + parameter mapping)
**Status**: NEGATIVE RESULT — near-threshold RSIDM cannot satisfy all 3 constraints

## Summary

Per Chu, Garcia-Cely, Murayama 2019 (PRL 122, 071103), Eq. 2:

```
sigma(v) = sigma_0 + 4*pi*S / (m_red * E(v)) * Gamma(v)^2/4 / [(E(v) - E(v_R))^2 + Gamma(v)^2/4]
```

where:
- E(v) = (1/2) m_red v^2 (kinetic energy in CM frame)
- v_R = resonance velocity (E(v_R) = delta * m_chi where delta = m_R/m_chi - 2)
- Gamma(v) = m_R * gamma * v^(2L+1) (L = 0 S-wave, L = 1 P-wave)
- S = (2J_R + 1) / (2J_DM + 1)^2

## Method

Implemented `v0.3-prelim/code/near_threshold_rsidm.py` with:
- Full Chu+ Eq. 2 implementation
- Both S-wave (L=0) and P-wave (L=1) support
- Parameter scan over (m_chi, delta, gamma)
- Constraint checking: Cloud-9 + dSph + SPARC

Verified numerical implementation against known best-fit values (S1, S2, P1 in Chu+ 2019).

## Critical Finding: UNitarity Barrier

For m_chi = 0.5 GeV at v = 28 km/s:
- Unitarity limit: sigma_max = 4*pi/k^2 where k = m_red * v / (2 hbar c) ≈ 1.18e-4 GeV^-1
- sigma_max ≈ 9e8 GeV^-2 ≈ 4e5 cm^2/g

**Any** resonance enhancement at v = 28 saturates this unitarity limit, giving sigma/m ≈ 4e5 cm^2/g — which is **4000x above the Cloud-9 requirement of 100 cm^2/g**.

## Parameter Scan Results

### S-wave (L=0) with gamma = 1e-5 (narrow BW):
- v_R = 28 km/s: sigma/m(v=28) = 2e7 (unitarity saturation)
- v_R = 28.5 km/s: sigma/m(v=28) = 0.002 (off-resonance by 0.5 km/s)
- **Sharp cliff: factor of 10^10 per 0.5 km/s away from v_R**

### P-wave (L=1) with gamma = 1e-3:
- v_R = 28 km/s: sigma/m(v=28) = 2e7 (unitarity)
- v_R = 28.5 km/s: sigma/m(v=28) = 0.002
- v_R = 29 km/s: sigma/m(v=29) = 2e7 (unitarity at v=29)
- **Same sharp cliff behavior**

### Below-threshold (delta < 0, bound state):
- sigma/m ~ 10^-9 to 10^-6 cm^2/g (way below Cloud-9)

## Why the Chu+ Approach Fails

Cloud-9 kinematic velocity is v = 28 km/s. For sigma/m ≈ 100 cm^2/g (not 4e5) at this velocity:

1. **Resonance at v_R = 28** → saturates unitarity → σ/m ≈ 4e5 (too high)
2. **Resonance at v_R = 28.5** → off-resonance by 0.5 km/s → σ/m ≈ 0.002 (too low)
3. **No smooth transition** — the BW factor is a delta-function in the narrow-width limit

The velocity width of the resonance is set by Gamma/v_R:
- For gamma = 1e-3 (P-wave), Gamma/v_R ≈ 1e-3 in natural units → width in v ≈ 0.03 km/s
- For gamma = 1e-5 (S-wave narrow), width in v ≈ 0.0003 km/s

The resonance is **2-3 orders of magnitude narrower** than the 1-2 km/s gap between Cloud-9 (v=28) and dSph (v=30).

## Implication for Path A

**Path A (Near-threshold RSIDM) cannot satisfy Cloud-9 + dSph simultaneously** because:
- Cloud-9 requires σ/m ≈ 100 at v = 28 km/s
- dSph requires σ/m < 0.2 at v = 30 km/s
- The Chu+ near-threshold resonance has velocity width ≪ 1 km/s
- Either the resonance is AT v = 28 (saturates unitarity) or OFF (σ → 0)

This is a **fundamental physics constraint**, not a parameter-tuning problem.

## Comparison with Phase 44 (current model)

| Aspect | Phase 44 broad BW | Chu+ near-threshold |
|---|---|---|
| Peak σ/m at v_peak | 197 cm²/g (Cloud-9 ✓) | 4e5 cm²/g (Cloud-9 ≫✓) |
| σ/m at v_peak ± 1 km/s | 30 cm²/g (still >0.2) | 0.002 cm²/g (dSph ✓) |
| σ/m at v_peak ± 2 km/s | 0.66 cm²/g (>0.2, dSph ✗) | << 10⁻⁶ cm²/g (dSph ✓✓) |
| Velocity width | ~10 km/s FWHM | ~0.03 km/s FWHM |

**The Chu+ resonance is too narrow.** Cloud-9 (v=28) and dSph (v=30) are 2 km/s apart, but the Chu+ resonance width is 0.03 km/s. So either Cloud-9 hits the unitarity wall OR dSph is fine but Cloud-9 is off-resonance.

Phase 44 has the OPPOSITE problem: broad enough to cover Cloud-9 but also leaks into dSph.

**Neither extreme works for the Cloud-9 + dSph combination.** The fundamental constraint is:
- Velocity gap (28 → 30 km/s) = 2 km/s ≈ 7% of v_Cloud-9
- Required suppression factor = 100/0.2 = 500
- Required velocity dependence: σ/σ' = (v'/v)^n with n such that (30/28)^n > 500
- Required n > log(500)/log(30/28) ≈ 56

So σ/m must fall like v^-56 or steeper between v=28 and v=30. **No known microphysical mechanism produces this.**

## Next Step: Path B (Inelastic SIDM)

Path A is closed. Pivoting to Path B (inelastic SIDM with mass splitting).

Inelastic SIDM opens a new channel above a threshold velocity:
- v_threshold = sqrt(2 * delta / m_chi)  (for mass splitting delta)
- Below v_threshold: only elastic scattering (suppressed)
- Above v_threshold: inelastic channel opens (enhanced)

If delta is tuned so v_threshold = 30 km/s, then:
- v < 30: elastic suppressed → σ/m small → dSph ✓
- v > 30: inelastic enhanced → σ/m large → Cloud-9 ✓

This **naturally inverts** the requirement: σ/m RISES at higher v instead of falls.

## Recommendation

**Path A is closed (negative result documented). Pivot to Path B (inelastic SIDM) on wip/inelastic-SIDM branch.**
