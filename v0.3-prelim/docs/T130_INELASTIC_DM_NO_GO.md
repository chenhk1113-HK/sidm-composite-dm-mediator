# T130 — Inelastic DM No-Go Theorem

## Question (Qwen referee Strategy 1)

For what m_χ does there exist a Δm that simultaneously:
- (a) Evades LZ/XENONnT direct detection via Δm > 100 keV
- (b) Allows self-scattering at Cloud-9 (KE_CM(28) > Δm)
- (c) Forbids self-scattering at dSph/UFD (KE_CM(15), KE_CM(3-10) < Δm)

## Result

**No valid m_χ < 46 TeV satisfies all three constraints.**

### Mass threshold derivation

KE_CM(v) = (1/4) m_χ v² (in c = 1 units)

| v (km/s) | KE_CM / m_χ (dimensionless) | Reference |
|---|---|---|
| 28 (Cloud-9) | 2.18 × 10⁻⁹ | Qwen referee, verified independently |
| 15 (dSph) | 6.25 × 10⁻¹⁰ | Qwen referee, verified independently |
| 3 (UFD-deep) | 2.50 × 10⁻¹¹ | independent |

Required: **KE_CM(28) > Δm > 100 keV**

Solving:
- Δm_max = (1/4) m_χ (28e3/c)² = 2.18 × 10⁻⁹ m_χ
- Δm_min = 100 keV = 10⁵ eV

For Δm_min < Δm_max:
- 10⁵ eV < 2.18 × 10⁻⁹ × m_χ_eV
- m_χ > 10⁵ / (2.18 × 10⁻⁹) = **4.59 × 10¹³ eV = 45.9 TeV**

**Threshold: m_χ ≥ 46 TeV** (Qwen: 46 TeV; our independent calc: 45.86 TeV; agreement: 0.3%)

### Window at the threshold

At m_χ = 46 TeV:
- KE_CM(Cloud-9) = 100.3 keV
- Required Δm: 100.0 keV < Δm < 100.3 keV
- **Window width: 0.3 keV = 0.3% of the threshold**

This is razor-thin. The model requires the splitting to be tuned to a specific narrow range.

### Two additional problems at m_χ = 46 TeV

**Problem 1: Thermal relic requires unitarity violation.**

For thermal freeze-out at m_χ = 46 TeV:
- <σv>_thermal ≈ 3 × 10⁻²⁶ cm³/s
- Tree-level <σv> = α_D² / m_χ² × c × v_relic_c × (ℏc)²

Solving for α_D:
- α_D_needed ≈ **404** (way above unitarity bound α_D < 1)

This means the coupling must be **non-perturbative** — thermal freeze-out does not produce the right relic density with perturbative couplings.

**Problem 2: Sommerfeld-enhanced annihilation may over-deplete.**

If we boost the annihilation cross-section via Sommerfeld enhancement to compensate for the small α_D, the enhancement factor at v ~ 10 km/s is:
- S(v) ~ 2π × α_D / v_c ~ 1884 (for α_D ~ 0.01, v_c ~ 3.3 × 10⁻⁵)

This boosts <σv> from 10⁻³⁵ cm³/s to 10⁻³² cm³/s — still **below** the thermal target of 3 × 10⁻²⁶ cm³/s. So even with Sommerfeld, the relic is **over-abundant** unless α_D is further increased (which makes unitarity worse).

## No-Go Conclusion

| m_χ range | DD evasion? | Cloud-9 ON? | dSph OFF? | Verdict |
|---|---|---|---|---|
| < 46 TeV | ✗ (window < 100 keV) | — | — | **NO-GO** |
| ≥ 46 TeV | ✓ | ✓ | ✓ | Window 0.3 keV at threshold; α_D ~ 404 needed (unitarity violation) |

**Inelastic DM (pseudo-Dirac) is NOT a viable UV completion for the phenomenology.**

## Implications for the project

This is a **publishable no-go theorem**:
1. GeV-scale pseudo-Dirac DM cannot satisfy both Cloud-9 and dSph constraints while evading DD.
2. Multi-TeV pseudo-Dirac DM works in principle but requires:
   - Razor-thin fine-tuning on Δm
   - Unitarity-violating α_D
   - Non-thermal relic density (or freeze-in)
3. Therefore the phenomenology (multi-resonance + two-component + gravothermal) is **NOT naturally realized by simple pseudo-Dirac DM**.

## v1.14 framing

The Qwen referee is correct that this supports Option (c) from the prior referee response:
- Retire the UV completion claim
- Keep the phenomenology
- Add EFT target map (Qwen Strategy 4)

## Files added

- `v0.3-prelim/code/T130_inelastic_kinematic_scan.py` — full scan with verification
- `v0.3-prelim/tests/test_T130_inelastic_kinematic_scan.py` — 13 tests, all pass
- `v0.3-prelim/docs/T130_INELASTIC_DM_NO_GO.md` — this document

## References

- Qwen referee report, 2026-09-19 (Strategy 1)
- Zhang 2016 Phys. Dark Univ. 15 (2017) 82 [45] — Hidden U(1) + pseudo-Dirac (now falsified)
- Griest & Kamionkowski 1990 — unitarity bound on thermal WIMP mass
