# Referee-Objection Responses (Phase 3.3)

**Date:** 2026-09-27
**Per:** devplan1.docx Phase 3.3 — prepared responses to likely objections

---

## O1. "This is not a model, it's a fit."

**Correct.** The paper is explicitly framed as a constraint map + no-go catalogue, not a unified
particle-physics derivation. See §1 (Introduction), §9.11 (Path F1 verdict split), and
`PAPER_STANDING_NUMBERS.md §2` (per-prescription channel counts). The headline is "4 of 8 channels
under physically motivated f_H" — not "8 of 8 self-consistent."

The paper's contribution is the constraint map itself: which σ/m(v) shapes are ruled out by
which channels, which require composite UV, and which require N-body f_H derivation to
resolve.

## O2. "The five no-gos are strawmen."

**No.** Each no-go is a published construction evaluated against current data:

| No-go | Construction | Source |
|---|---|---|
| LZ direct detection | Magnetic dipole DM, hidden U(1) + 10 MeV pseudo-Dirac | T163 KK tower + LZ 2024 |
| Kinematic forbiddance | GeV-scale inelastic DM | T182 single-resonance rewrite |
| Unitarity violation | p-wave resonance (Chu+ 2019) | T179 partial-wave analysis |
| Flat velocity dependence | One-mediator UV systematic (general) | T184/T191 α_D ∈ [0.01, 100] |

All four no-gos **independently** rule out their respective UV completions; **T175 confirms all 4
verdicts hold at T163 KK-tower best-fit parameters** (see `data/results/t175_nogo_retest_t163.json`).
The T184 fifth no-go is a general scaling argument rather than a specific UV construction.

## O3. "Cloud-9 is treated too softly."

**The Turini & Benítez-Llambay 2026 environmental systematics are explicit.** See §10.4d
(Cloud-9 as systematic upper bound) for the full discussion. The three systematic effects
identified (local environmental density, HI self-shielding, FAST beam-smearing) can shift the
σ/m ≥ 50 floor by factors of 2-3. **Cross-validation against Crater II and Antlia II kinematic
constraints (Zhang+ 2024 ApJL 968, L13) is documented.** The paper's framing is: Cloud-9 is
likely a real signal but the precise σ/m value is systematic-uncertain. The framework's
inability to satisfy Cloud-9 under physically motivated f_H is **not** claimed to refute the
framework — it is claimed to be consistent with the systematic uncertainty.

## O4. "Why no N-body for f_H?"

**Acknowledged limitation.** KiSS-SIDM is single-species and cannot produce f_H from
multi-species gravothermal evolution. Yang+ 2025 Fig. 2 provides f_H at 2800× larger σ/m than
our parameter regime; the regime extrapolation is the borrowed prescription mode. **First-principles
f_H is future work**, documented as a top priority in §11 (Conclusions) and excluded from the
paper's claims. The honest framing in §9.6 makes this explicit.

## O5. "The Bayes factor is weak."

**Honest reporting.** log B = 2.411 (Bayes B = 11.149) is "moderate evidence" on the Jeffreys
scale, downgraded from T177's log B = 3.06 with hand-picked σ_unc. **The BIC-corrected evidence
favors the constant σ/m null** (ΔBIC = +3.22 with 15 vs 1 parameters). Both metrics are reported
in §4 (Statistical Tests) of `PAPER_STANDING_NUMBERS.md`. The paper does not claim Bayes
dominance over the constant σ/m alternative.

## O6. "Where is the UV completion?"

**No unified UV completion is claimed.** Two-mediator (Drobczyk 2025) is presented as a viable
candidate for thermal relic density (Ωh² = 0.1187 at δ = 0.43%, g_h_SM = 0.00040) in §10.3. The
paper's identity is constraint map, not UV construction. **Five UV completion no-go theorems
explicitly rule out single-mediator UV at Phase 44 parameters.** Future UV work (T198 Drobczyk
composite UV, T199 partial-wave couplings) is post-submission follow-up.

## O7. "Cloud-9 t_core should be measured."

**Cannot be measured at tested N/resolution.** Tier 1+2 future-work pilot confirmed that parameter
tuning alone cannot extend T215 KiSS-SIDM runs beyond 70 Myr (full pilot summary at
`docs/T215VWXY_TIER12_PILOT_2026-09-27.md`). Higher N and/or Tier 3 code modifications
(subcycled time integration, freeze refinement after density threshold) are required — these
require ~100+ days of compute and are deferred. **§10.5b is explicit: methods contribution only,
no quantitative t_core reported.** The qualitative gravothermal direction (interior up
1.76-2.99×, outer down 0.34-0.63×) is reproducible in 5/5 fresh-session runs.

## O8. "Why is the headline 4 of 8 instead of 6 of 8?"

**Per Refinement 1 of devplan1.docx.** The "6 of 8" framing counts clear+marginal under borrowed
f_H (hand-picked placeholder, retracted v18.29) — it is misleading for 6 versions. The paper
honestly distinguishes:
- **4 of 8 clear_pass** under yang (physically motivated f_H) — the headline
- **6 of 8 clear+marginal** under borrowed — mentioned as upper-bound under retracted prescription
- **4 of 8 clear+marginal** under t202 (N-body f_H) — independent cross-check
- **8 of 8 clear_pass** under priored free fit — at the cost of SPARC log L = -2.03 (clear fail)

The "4 of 8" headline is the cleanest statement of what the framework establishes.

## O9. "What about the KK tower check?"

**Covered in §7 and §10.** T213 (KK tower + Silverman+ combined, 2026-09-26) confirms T163 KK
tower σ/m(V_max = 31.12 km/s) = **0.174 cm²/g**, which is **5.7× below** the Silverman+ 2026
gravothermal threshold of 1.0 cm²/g. The KK tower is in the Born regime where σ ∝ α²/m_med²
(no Sommerfeld enhancement at low v); velocity dependence is flat across 5-500 km/s (factor <
1.04). T163 KK tower alone **cannot bridge the Cloud-9 gap** — Path F1 three-term σ_eff
decomposition cannot either, because the σ_HL peak is at v_HL ≈ 100 km/s (SPARC scale), not
v = 31 km/s (Cloud-9 host V_max). **T175 confirms all 4 no-gos hold at T163 parameters.**

## O10. "The five no-gos are independent?"

**Yes.** T175 was run specifically to verify the no-go verdict independence. The four specific
UV no-gos (LZ, kinematic, unitarity, flat-velocity) are ruled out by **independent mechanisms**:
- LZ: direct detection cross-section vs LZ 2024 limit
- Kinematic: dispersion-supported flatness vs Crater II/Antlia II
- Unitarity: cross-section grows faster than 1/v² below threshold
- Flat velocity: α²/m² scaling produces σ(v) ≈ const, ruled out by UFD/dSph/Cloud-9 spread

T184 (one-mediator UV systematic) is a general scaling argument rather than a specific UV
construction. All five are **necessary** for the "no single-mediator UV" verdict.

---

## Submission-time response protocol

If a referee raises one of O1-O10 in their review:

1. **Quoted response** from this document, with §X.Y references to PAPER_V1_DRAFT.md
2. **Data file** pointed to (e.g., `data/results/t175_nogo_retest_t163.json`)
3. **Standing-numbers table** cross-check (`docs/PAPER_STANDING_NUMBERS.md`)
4. **Honest limit** acknowledged if applicable

If a new objection not covered here:

1. Pull the relevant data JSON
2. Add to this document with the standard response template
3. Cross-check against `PAPER_STANDING_NUMBERS.md`