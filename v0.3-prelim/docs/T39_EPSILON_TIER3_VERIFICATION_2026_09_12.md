# T39 Tier-3 ε marginalization — current state (2026-09-12)

**Status:** Shipped and verified. ε-α joint posterior concentrates at ε ~ 10^-54, α ~ 10^-28. The model "works" by marginalizing over (ε, α), but the publishable caveat is that the SIDM mediator must be invisible to the SM at direct-detection energies.

**Source data:** `v0.3-prelim/data/results/t39_tier3_epsilon_alpha_joint_fit.json`
**Wall time:** 1.45 s (fast fit)
**Last reviewed:** This doc (2026-09-12)

---

## What T39 does

T39 fits a 4-parameter joint posterior over **(σ/m_0, a, log_ε, log_α)** with priors:

| Parameter | Prior range | Physical meaning |
|---|---|---|
| log_σ/m_0 | [-3.0, 2.5] | σ/m at V_REF=100 km/s (cm^2/g) |
| a | [-2.0, 2.0] | velocity power-law index |
| log_ε | [-60, -1] | dark photon kinetic mixing |
| log_α | [-30, -1] | dark-sector Yukawa coupling |

This is the Tier-3 marginalization: include ε and α as free nuisance parameters, marginalize over them, recover the σ/m posterior.

## Headline result

**log Z = -2.94 ± 0.21** (4-parameter joint fit)

Compared to catastrophic exclusions:
- T30 (no marginalization): log Z = -9207 (catastrophically excluded)
- T32 (partial): log Z = -1578 (still catastrophic)
- T39 (full marginalization): log Z = -2.94 (consistent with data)

**Median σ/m_0 = 1.57 cm^2/g** (16th-50th-84th: 0.67, 1.57, 3.16)

**MAP at log_ε = -56.1, log_α = -28.0** — essentially zero coupling.

## The publishable caveat (from the JSON itself)

> "The posterior concentrates at ε ~ 10^-50, α ~ 10^-28 (essentially zero). The SIDM mediator is INVISIBLE to the Standard Model at direct-detection (LZ) and gamma-ray (Fermi) energies."

> "The publishable headline MUST foreground this IF: 'σ/m = 1.67 cm^2/g is consistent with multi-channel data IF the SIDM mediator decouples from SM.' This is the MINIMUM statement, not the maximum."

> "Future work: log-normal or hierarchical priors for (ε, α)."

## What this means for the LRD2.docx reviewer's concern

The reviewer (LRD2.docx, claim 6) said:

> "The ε ~10^-37 required for LZ evasion remains a naturalness catastrophe regardless of how many astrophysical channels are satisfied. Adding more astrophysical constraints does not make the particle physics more plausible."

**T39 is the project's response to this concern:**

1. **The model can satisfy LZ + astrophysical channels** by marginalizing over (ε, α) — log Z goes from -9207 to -2.94.
2. **The cost is naturalness**: the SIDM mediator must decouple from SM (ε ~ 10^-54, α ~ 10^-28).
3. **The reviewer is correct** that this is a naturalness catastrophe. The "fine-tuning" is moved from "ε is wrong" to "ε must be tuned to near-zero."
4. **The reviewer is wrong that adding astrophysical channels doesn't help** — they constrain σ/m shape, which lets the marginalization converge. Without good σ/m constraints, ε has to do more work.

## The honest verdict

Per AGENTS.md rule 11 (honesty over fluency), T39 demonstrates:

- **The phenomenological model works** — log Z is consistent with multi-channel data.
- **The particle-physics story does NOT work** — ε ~ 10^-54 is unnatural and needs a symmetry-based explanation (not yet provided).
- **The decoupling interpretation** is the project's standing posture, not a bug. It says: "this model is a phenomenology tool, not a particle-physics candidate, until ε naturalness is resolved."

## Verdict softened per R1 (Jeffreys scale)

Per Reviewer 1 (roadmap1.docx, paragraph 11): log_Z = -2.94 is **"weak evidence at best (Jeffreys scale: 'not worth more than a bare mention')"** when interpreted in absolute terms. The earlier verdict "TIER-3 RESOLVED" (in the JSON output) is overclaiming.

**Revised verdict (this doc):** **TIER-3 WEAKLY CONSISTENT** with multi-channel data. The marginalization succeeds (log_Z = -2.94 vs catastrophic T30/T32), but the absolute evidence is weak per Jeffreys scale. The "~600× improvement" framing is comparing to catastrophically-excluded baselines, not a positive result.

**Three honest framings of the same posterior:**

1. **Strongest claim:** "Tier-3 marginalization restores consistency with multi-channel data."
2. **Weakest claim:** "Tier-3 marginalization succeeds only if the mediator is decoupled from the Standard Model at the 10^-54 level — a naturalness catastrophe."
3. **Most honest claim:** "Both. The model is consistent with data ONLY if the SIDM mediator is invisible to the Standard Model. That conditional is the entire result, not a caveat."

The published paper would need to foreground framing #3, not #1.

## What T39 does NOT address

- **Why ε ~ 10^-54** — no symmetry mechanism proposed (e.g., technical naturalness from a discrete symmetry, accidental cancellation in UV completion, etc.)
- **Hierarchical or log-normal priors** — current flat priors in log_ε are agnostic but may be too generous
- **Connection to specific UV completions** — the model uses ε as a generic kinetic mixing; not tied to a specific hidden-sector model (e.g., Stueckelberg, Higgs portal, etc.)

## Comparison to T30 / T32

| Test | log Z | Status |
|---|---|---|
| T30 | -9207 | Catastrophic exclusion (no marginalization) |
| T32 | -1578 | Still catastrophic (partial marginalization) |
| **T39** | **-2.94** | **Consistent with data** (full marginalization) |
| T90.30/33/40/41 series | various | Includes 6-param joint fits with m_phi, m_chi, g_chi, ε, α, ξ |

The progression T30 → T32 → T39 demonstrates that the marginalization is **necessary** — without it, the model fails. With it, the model works but at the cost of ε naturalness.

## Why this doc exists

Per the LRD2.docx reviewer's claim 6 ("ε ~ 10^-37 naturalness catastrophe persists"), there was no existing documentation of T39. This doc captures:

1. **What T39 does** (4-param marginalization)
2. **What T39 found** (log Z = -2.94, ε ~ 10^-54)
3. **What the caveat is** (decoupling interpretation, no naturalness mechanism)
4. **What this addresses and doesn't address** (works phenomenologically, fails particle-physics-naturalness)

The project already had the data; the missing piece was the writeup. This doc fills that gap.

## References

- **Data:** `v0.3-prelim/data/results/t39_tier3_epsilon_alpha_joint_fit.json`
- **Data:** `v0.3-prelim/data/results/t39_prior_robustness.json` (prior sensitivity)
- **Data:** `v0.3-prelim/data/results/t39b_tier3_conditional_marginalization.json` (conditional version)
- **T39 code:** `v0.3-prelim/code/t39_tier3_epsilon_alpha_joint_fit.py`
- **T39 prior robustness:** `v0.3-prelim/code/t39_prior_robustness.py`
- **T39b conditional:** `v0.3-prelim/code/t39b_tier3_conditional_marginalization.py`
- **Drobczyk 2025** (arXiv:2506.22997): Independent validation of decoupled SIDM phenomenology
- **arXiv:2510.05216**: DAMA/LIBRA direct-detection tension (5.1σ EFT analysis)
- **AGENTS.md rule 11**: Honest framing — captured the naturalness catastrophe explicitly
- **LRD2.docx** claim 6: "ε ~10^-37 naturalness catastrophe" — verified, with the caveat that the project's Tier-3 fit moves it to ε ~ 10^-54 (worse, not better)