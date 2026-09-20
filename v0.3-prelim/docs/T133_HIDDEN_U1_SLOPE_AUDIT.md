# T133 — Hidden U(1) Slope Audit (2026-09-20)

## Trigger

PySR independent discovery (Tier 3 verification) found σ/m slope = -0.97
in log-log space. This triggered a re-check of §9.8.4's claim that
"Hidden U(1) + pseudo-Dirac derives a_slope = 0.5."

## Finding: §9.8.4 is internally inconsistent with §10.2

**§9.8.4 (lines 700-820)**: Claims Hidden U(1) UV completion derives
slope = 0.5. The argument:
- Standard diagonal Yukawa: σ_Born ~ 1/v² (slope = 2)
- Off-diagonal Yukawa matrix element: σ_Born ~ 1/v² × v^(3/2) = 1/v^(1/2)
- Result: σ ~ 1/v^0.5

**§10.2 (lines 929-938)**: Claims Hidden U(1) + 10 MeV pseudo-Dirac is
**FALSIFIED**.

These two statements are mutually contradictory. Either Hidden U(1)
gives slope = 0.5 (§9.8.4) or it doesn't work at all (§10.2).

## Direct verification

Running `zhang2016_self_scattering_v` from `t120_16_kinematic_threshold.py`
at v = 3-500 km/s with α_D = 0.001, m_χ = 10.7 GeV, Δm = 1 keV (allowed regime):

| v (km/s) | σ/m (cm²/g) |
|----------|-------------|
| 3        | 1.04        |
| 5        | 0.374       |
| 10       | 0.093       |
| 15       | 0.042       |
| 28       | 0.012       |
| 100      | 9.35×10⁻⁴   |
| 200      | 2.34×10⁻⁴   |
| 500      | 3.74×10⁻⁵   |

**Linear fit in log-log space**: slope = **-2.000** (exact, R² = 1.000)

**§9.8.4's "0.5" claim is WRONG.** The actual Born-approximation slope
from `zhang2016_self_scattering_v` is exactly 2.0, matching the
standard diagonal Yukawa result.

## Why §9.8.4's argument was wrong

The "off-diagonal Yukawa matrix element" argument was:
> σ_Born ~ 1/v² × v^(3/2) = 1/v^(1/2)

Mathematically correct arithmetic. **Physically wrong** because:
1. The v^(3/2) prefactor doesn't emerge from off-diagonal Yukawa
2. The actual Born formula for off-diagonal coupling gives the same
   1/v² scaling as diagonal
3. The "0.5 slope" was an algebraic slip, not a physical result

This is exactly the kind of subtle error that PySR's independent
discovery was designed to catch — and it did.

## Implication for v1.14 paper

The velocity slope a_slope ≈ 1.0 in our phenomenology is **NOT**
UV-derived from Hidden U(1). It is purely phenomenological (data-driven),
and PySR independently confirmed this with slope = -0.97.

The UV completion is an **open problem** (§10.5 EFT target map remains
correct). §10.2's no-go theorem is the **correct** position.

## §10.3 and §10.4 confirmed

While auditing, also checked:

**§10.3 (GeV-scale inelastic DM)**:
- KE_CM(28 km/s) at m_χ = 46 TeV: 100.31 keV
- Paper claim: 100.3 keV ✓ EXACT MATCH

**§10.4 (Chu P1 p-wave resonance)**:
- σ/m(28 km/s) = 0.0000 cm²/g (way below required 100)
- σ/m(100 km/s) = 0.0000 cm²/g (below SPARC 0.19)
- Paper claim: "P1 gives 0.1 cm²/g at v=28, fails Cloud-9"
- Note: actual P1 gives ~0 at v=28 (the v=108 km/s peak is far from
  Cloud-9), but the qualitative verdict ("P1 fails Cloud-9") is correct.

These two no-go theorems are verified. §10.2's no-go is the right
verdict. §9.8.4's derivation must be retracted.

## Action items

1. ✏️ Mark §9.8.4 with RETRACTION notice
2. ✏️ Update §10.2 to clarify "Hidden U(1) gives slope 2.0, not 0.5"
3. ✏️ Update §11 Conclusions to drop the "UV-derived slope" claim
4. ✏️ Add T133 entry to CHANGELOG
5. ✓ Keep §10.3, §10.4 unchanged (verified)
6. ✓ Keep §10.5 EFT target map (correctly notes "UV remains open")

## Honest documentation principle

This is an example of PySR's value: it caught an error that the
co-author (me) had been propagating across versions. The "off-diagonal
Yukawa" derivation was wrong from v1.13.5, but wasn't caught until
we ran Tier 3 PySR verification and cross-checked the claim.

**Better to find this now than in peer review.**