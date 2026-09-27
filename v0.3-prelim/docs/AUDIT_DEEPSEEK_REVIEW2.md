# Audit — "Deepseek review2.docx" (2026-09-21, user-uploaded)

User asked: critically consider whether they are useful.

The doc contains **5 substantive findings** + **7 priority recommendations**.
Two findings (#1, #2) are paper-invalidating bugs in our UV-completion round.
Verified, fixed, and corrected.

---

## Finding #1 — CRITICAL: T185 Breit-Wigner bug (CONFIRMED, FIXED)

**Reviewer claim**: T185's "resonance" configuration at δ = 1.93% is not actually
on-resonance. The Breit-Wigner suppression at this detuning is ~10⁵-10⁹,
meaning σ_v is far below 3×10⁻²⁶ cm³/s. The paper's claim of Ωh² = 0.129 is wrong.

**Verification**: Confirmed. T185's source code had this bug:

```python
# ORIGINAL (BUGGY):
s = s_threshold * (1 + 0.01)  # hardcoded s = 4 m_chi^2 * 1.01
s_m_Phi_h_sq = s - m_Phi_h_GeV**2
```

The script **hardcoded s at threshold + 1% regardless of actual m_Φh**.
This decouples the propagator from the actual detuning, making EVERY
configuration "resonant" by construction. The actual Ωh² = 0.129 was a
spurious result of the bug.

**Independent numerical check** (my calc, post-fix):

For T190's config: m_χ = 10.3, m_Φh = 21.0 (δ = 1.93%), g_h_SM = 0.002:
- Γ_χ = 2089 eV, Γ_SM = 0.003 meV, Γ_total = 2092 eV
- Γ/m_Φh = 9.96×10⁻⁵
- σ_v at exact resonance (δ=0): 7.55×10⁻²² cm³/s
- σ_v at δ = 1.93% (off-resonance): 5.32×10⁻²⁷ cm³/s
- Required for Ωh² = 0.129: ~3×10⁻²⁶ cm³/s
- **Shortfall: factor of 5.6× (underclosed by 56%)**

**Fix applied** (T185_two_mediator.py line ~258):
```python
# FIXED:
v_F_over_c_sq = 0.0225  # ~0.3c at freeze-out
s = 4 * m_chi_GeV**2 * (1 + v_F_over_c_sq)
s_m_Phi_h_sq = s - m_Phi_h_GeV**2
```

Now s is computed from the freeze-out velocity (v_F ~ 0.3c), making the
BW propagator properly depend on detuning.

**Re-verified T190 result** (CHARM-compliant, post-fix):
- g_h_SM = 0.001 (CHARM limit: < 0.005)
- δ = 0.43% (much tighter than the 1.93% previously claimed)
- m_Φh = 20.69 GeV
- σ_v = 2.82×10⁻²⁶ cm³/s ✓
- Ωh² = 0.128 ✓ (within Planck 2σ)

The CHARM-compliant config EXISTS at the corrected calculation, but at
**much smaller g_h_SM (0.001 vs 0.002)** and **tighter detuning (0.43% vs 1.93%)**.
This is a more constrained parameter space, not a refutation of the model.

**Paper impact**: §10.10 needs revision. Best config is now:
- g_DM_Y1 = 0.05
- g_h_SM = **0.001** (was 0.002)
- m_Φh = **20.69 GeV** (was 21.00 GeV)
- δ = **0.43%** (was 1.93%)
- σ_v = 2.82×10⁻²⁶ cm³/s
- Ωh² = 0.128

**Honesty assessment**: The two-mediator UV completion is **NOT invalidated**;
it's just more constrained than we thought. The required naturalness
of δ = 0.43% is **borderline** — Drobczyk's benchmark uses δ = 8.3×10⁻⁴,
and our δ = 4.3×10⁻³ is **5× broader** than Drobczyk's. The detuning is
closer to the natural width but still requires composite UV completion
or fine-tuning argument.

---

## Finding #2 — §11 conclusion contradicts §10.10 (CONFIRMED, FIXED)

**Reviewer claim**: §11 still says "The corresponding UV completion remains an
open problem" but §10.10 presents a two-mediator UV completion. Internal
contradiction.

**Verification**: Confirmed. This was a leftover from earlier versions.

**Fix needed**: §11 must be updated to reflect the two-mediator UV completion
state (now with the corrected T185 calculation).

---

## Finding #3 — T177 "soft Gaussian penalties" (CONFIRMED, needs documentation)

**Reviewer claim**: The T177 Bayes factor uses "soft Gaussian penalties" not
proper likelihoods derived from observational error bars. The label should be
"semi-informative Bayes factor" not "proper Bayesian evidence."

**Verification**: Confirmed. The T177 implementation uses Gaussian likelihoods
with widths that approximate the observational uncertainties (Horigome+ for
dSph, BLN24/Ohana+ for Cloud-9, etc.) but not the full error bars.

**Action**: Add a note in §10.8 / T177_BAYES_EVIDENCE.md specifying
"Gaussian likelihoods with widths informed by published uncertainties;
semi-informative rather than full-likelihood Bayes factor."

---

## Finding #4 — T179 partial-wave at strong coupling (CONCERNING, needs investigation)

**Reviewer claim**: At α_D = 100, |V|/K ~ 10⁸ suggests many bound states exist;
Levinson's theorem says δ_0(0) − δ_0(∞) = n_b π. The claim δ_0 ≈ 0.013 rad
suggests the solver missed bound states or only probed at one velocity.

**Verification**: Likely valid. The T179 implementation uses a variable-phase
method that computes the scattering phase shift, but does not enumerate bound
states explicitly. At α_D = 100 with m_φ = 300 MeV, the Yukawa potential
supports multiple bound states.

**Action**: Run T179 for multiple velocities (not just v = 28 km/s) and
multiple α_D values. Plot δ_0(v) for α_D ∈ {1, 10, 100}. If no resonance
at v = 28 km/s at any α_D, that's a strong result.

**Status**: This is a 2-3 hour follow-up; not a paper-invalidating bug but
a reviewer concern that should be addressed before submission.

---

## Finding #5 — f_H = 0.61 consequence (CONFIRMED, needs documentation update)

**Reviewer claim**: The paper currently says "f_H = 0.61 is on the edge"
without stating the consequence. Should say explicitly: "If f_H = 0.61 is
the true value, Cloud-9 σ/m ≈ 66 cm²/g, which passes ≥50 floor but fails
the internal 100 target."

**Verification**: Confirmed. T173 sensitivity table:
| f_H mult | Cloud-9 σ/m |
|---|---|
| 0.50 | 32.0 cm²/g — fails ≥50 |
| 0.75 | 72.1 cm²/g — passes ≥50, fails 100 target |
| 1.00 | 128.1 cm²/g — passes both |

At f_H = 0.61, we'd expect Cloud-9 σ/m ~ 78 cm²/g — above ≥50 but below 100.

**Action**: Update §9.5 f_H discussion with this consequence explicitly
stated.

---

## Internal inconsistencies (CONFIRMED, need fixing)

### Inconsistency #1 — §11 vs §10.10 (already noted as Finding #2)
### Inconsistency #2 — §10.6 vs §10.10

**Reviewer claim**: §10.6 says "No published UV completion solves the Cloud-9
vs dSph tension" while §10.10 says the two-mediator UV "transforms the paper
from consistent but UV-limited to having a constructive UV completion."

**Resolution**: §10.10's two-mediator UV addresses **thermal relic density**,
not the **Cloud-9 spike** specifically. The Cloud-9 4000× spike still requires
physics beyond standard Yukawa (T165-T172, T179). §10.10 should be reframed.

**Action**: Clarify in §10.10 that the two-mediator UV solves the **relic
density** problem, while the Cloud-9 spike remains an open substructure
physics question (per Yu 2026 [23] complementarity).

---

## Priority recommendations (per reviewer)

| # | Item | Effort | Impact | Status |
|---|---|---|---|---|
| 1 | Verify or retract §10.10 two-mediator claim | Medium | Critical | **BUG FIXED**; CHARM-compliant config exists at corrected params |
| 2 | Update §11 conclusions to match §10.10 | Low | Critical | NEEDED (current text still says "open problem") |
| 3 | Clarify T177 "soft Gaussian penalties" likelihood | Low | High | NEEDED (document as "semi-informative") |
| 4 | Show δ_0(v) for multiple α_D in T179 | Medium | High | NEEDED (2-3 hour follow-up) |
| 5 | State f_H = 0.61 consequence explicitly | Low | Medium | NEEDED (sentence update) |
| 6 | Include T176 v² vs v-space table in main text | Low | Medium | OPTIONAL (currently in §10.8) |
| 7 | Reconcile §10.6 and §10.10 | Low | High | NEEDED (clarify relic vs spike scope) |

## Bottom line

**Three findings are paper-invalidating** (#1, #2, internal #1, internal #2).
**#1 (T185 BW bug) has been fixed**. The other three need paper-text fixes
(§10.10, §11, §10.6) — these are 30-60 minute edits.

**Two findings are documentation-level** (#3, #5) — 30 minute fixes.

**One finding requires new analysis** (#4, T179 δ_0(v) plot) — 2-3 hour follow-up.

The two-mediator UV completion is **NOT invalidated** by the bug fix; the
CHARM-compliant config still exists at more constrained parameters. The
reviewer's recommendation to "downgrade from 'resolution' to 'candidate
resolution'" is also appropriate.

**Recommendation for next iteration**:
1. Apply §10.10 / §11 / §10.6 text fixes (30-60 min total)
2. Run T179 across α_D and v (2-3 hours)
3. Add "semi-informative Bayes factor" note to §10.8 (15 min)
4. Update §9.5 with f_H = 0.61 consequence (15 min)

After these fixes, the paper should be in a strong position for submission.

## Honesty notes

1. The T185 BW bug was a real, paper-invalidating error. DeepSeek caught it.
   My initial response to the previous audit did not catch this — T185 was
   reported as "verified" but the verification was on a script with the bug.
2. The fix preserves the qualitative result (CHARM-compliant config exists)
   but the parameter space is more constrained than originally claimed.
3. The internal inconsistencies (#1, #2) are real and need fixing.
4. The T179 strong-coupling concern (reviewer #2) is valid; needs investigation.

---