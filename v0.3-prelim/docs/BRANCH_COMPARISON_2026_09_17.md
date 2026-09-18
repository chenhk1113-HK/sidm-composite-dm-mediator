# Branch Comparison — `wip/cloud-9-relhic` vs `wip/tier3-sequential-T90-magnetic`

**Date:** 2026-09-17
**Author:** MiniMax-M3 (with input from `qwen2.docx` reviewer, 2026-09-17)
**Purpose:** Document the differences between the two WIP branches so reviewers don't conflate them.

---

## TL;DR

These two branches do **completely different physics** for **completely different audiences**, even though both are about dark matter. They share some keywords (SIDM, dm_chi, m_φ) and they share some infrastructure (Python venv, data/results/ JSONs), but the **scientific questions, methodology, and conclusions** are distinct.

| Branch | Question | Methodology | Headline result |
|---|---|---|---|
| `wip/cloud-9-relhic` | Can a multi-resonance SIDM model satisfy Cloud-9 + SPARC + JVAS simultaneously? | 4 Breit-Wigner peaks + Yukawa background; 5 UV embeddings (clockwork, Secluded U(1), power-law, integer, dark-SU(N_c)); free + UV-prior joint fits | Phase 44: +8.10 log-units; 5 honest limitations |
| `wip/tier3-sequential-T90-magnetic` | Can a Composite Inelastic DM model satisfy galactic SIDM constraints AND the LZ 248 keV event simultaneously? | Composite DM (Alves-Behbahani-Schuster-Wacker 2010); 7D / 8D dynesty nested sampling; T90 merge rule with strict Bayesian evidence thresholds | Door B marginally preferred (ΔlogZ = +0.51) but below +2 threshold; Door C closed (-10.7); Door D closed (-5.7); 0.08% UV surviving |

---

## Side-by-side comparison

### What is the dark matter?

| Branch | DM model | Mediator | Velocity dependence |
|---|---|---|---|
| `wip/cloud-9-relhic` | Implicit DM (no specific UV identity); σ/m(v) parameterized as Yukawa + 4 Breit-Wigner resonances | 4 mass-degenerate mediators in the dark sector; masses set by ladder constraint | Strongly v-dependent: σ/m has 4 narrow velocity windows with σ/m enhanced |
| `wip/tier3-sequential-T90-magnetic` | Composite dark pions (Alves-Behbahani-Schuster-Wacker 2010 framework) | Elementary dark photon A' with kinetic mixing ε to SM photon | Velocity-independent σ/m + inelastic mass splitting δ ~ 100-300 keV for the LZ portal |

### What channels does it test?

| Branch | Channels | Velocity scale | Energy scale |
|---|---|---|---|
| `wip/cloud-9-relhic` | Cloud-9, SPARC, JVAS | v ≈ 15-200 km/s | kinematic |
| `wip/tier3-sequential-T90-magnetic` | galactic SIDM, LZ 248 keV event, DIAMX combined LXeTPC | v ≈ 100 km/s | recoil ~100 keV |

### What's the headline number?

| Branch | Headline result | Sign of result |
|---|---|---|
| `wip/cloud-9-relhic` | +8.10 log-units (Phase 44 free joint fit); +7.93 (Phase 53 v2 with clockwork UV prior) | **Positive** — multi-resonance architecture satisfies Cloud-9 + SPARC + JVAS |
| `wip/tier3-sequential-T90-magnetic` | ΔlogZ = +0.51 for 8D (v0.7 + LZ + DIAMX) over 6D v0.7 baseline | **Marginal** — Door B mathematically viable but not significantly preferred by data |

### What's the verdict?

| Branch | Verdict | Publishable? |
|---|---|---|
| `wip/cloud-9-relhic` | Multi-resonance architecture is consistent with 3 channels, has 5 UV embeddings at MINIMAL fine-tuning, 5 honest limitations documented in Paper v1.8 §8.4 | **Yes**, as mixed-verdict paper (PRD / JCAP / JHEP) |
| `wip/tier3-sequential-T90-magnetic` | Composite Inelastic DM with both portals is **fine-tuned** (0.08% UV surviving), in **15σ tension** between LZ-only and DIAMX-combined fits, marginally preferred (ΔlogZ = +0.51) | **Yes**, as exclusion-limits paper (the qwen2 recommendation) |

---

## Why do they share keywords but do different things?

Both branches deal with SIDM (self-interacting dark matter) and both use Bayesian nested sampling (dynesty). But the **research questions are orthogonal**:

- **`wip/cloud-9-relhic`** is about reconciling **multi-scale** SIDM observations (different velocity scales probe different σ/m strengths). The 4-resonance architecture addresses this by introducing narrow velocity windows. The "Doors" concept doesn't exist on this branch.

- **`wip/tier3-sequential-T90-magnetic`** is about reconciling **astrophysical SIDM** with **terrestrial direct detection anomalies** (the LZ 248 keV event). The "Doors" concept (A/B/C/D = baseline kinetic mixing / inelastic scattering / magnetic moment / multi-component DM) is the central methodology of this branch.

If you're reviewing qwen2.docx and it says "the branch opens Door B with ΔlogZ = +0.51" — that's referring to tier3, NOT cloud-9. If it says "the branch has a +8.10 log-unit gain from Phase 44" — that's referring to cloud-9, NOT tier3.

---

## Common infrastructure

Both branches share:

- **Python venv**: `.venv-sidm-bench/Scripts/python.exe` (Windows) or WSL `/home/lamkuenai/.venv/bin/python`
- **Result JSONs**: `v0.3-prelim/data/results/*.json`
- **Test infrastructure**: `v0.3-prelim/tests/`
- **Drift-guard scripts**: `scripts/t82_audit.py`
- **Paper source**: `v0.3-prelim/docs/PAPER_V1_DRAFT.md` (markdown-only during drafting)

But the **code in `v0.3-prelim/code/`** is different:

- `wip/cloud-9-relhic` has: `phase32_cloud9_*`, `phase33d_*`, `phase41_*`, `phase44_*`, `phase47_*`, `phase51_*`, `phase52_*`, `phase53_*`, `phase54_*`, `t90_v70_multi_resonant_darkqcd.py`, `channels_v03.py`
- `wip/tier3-sequential-T90-magnetic` has: `t103_lz_only_fit.*`, `t105_uv_consistency.*`, `t106_multi_experiment_joint.*`, `t108_full_8d_dynesty.*`, `t110_full_7d_dynesty.*`, `t111_multicomponent_dm.*`, `t112_highres_8d_dynesty.*`, `t113_event_rate_forecasts.*`, `t114_xe124_dec_systematic.*`, `t115_sequential_confirmation.*`, `t116_sequential_t90_value.*`, `t87_composite_inelastic_nucleon.py`

The **only code file they share is `channels_v03.py`** (the σ/m(v) parameterization), and even that's used differently on each branch.

---

## Reviewer confusion (qwen2.docx, 2026-09-17)

The qwen2 reviewer uploaded a critical review that:

- **Correctly identified** the multi-channel SIDM focus of the project
- **Incorrectly labeled** the branch as `wip/cloud-9-relhic` when actually reviewing `wip/tier3-sequential-T90-magnetic`
- **Correctly described** the Doors framework (A/B/C/D), T103, T105, T106, T108, T110, T111, Alves-Behbahani-Schuster-Wacker 2010, DIAMX combined analysis, 15σ tension, ΔlogZ = +0.51 — all of these are on tier3
- **Incorrectly implied** these features existed on cloud-9 — they don't

This branch-comparison doc is created in response to this confusion. Future reviewers should refer to this document when reviewing either branch.

---

## Recommendation: read both branches as separate papers

The reviewer (qwen2) recommended **publishing the T105 + T106 exclusion limits as a negative-result paper**. This is a good recommendation for **tier3**, not for cloud-9. The two branches should be considered for **separate papers**:

| Branch | Recommended paper |
|---|---|
| `wip/cloud-9-relhic` | "Multi-Resonance SIDM: Joint Multi-Channel Constraints and UV-Prior Re-Evaluation" — mixed-verdict paper at PRD / JCAP / JHEP |
| `wip/tier3-sequential-T90-magnetic` | "Composite Inelastic Dark Matter: Combined Astrophysical + LXeTPC Constraints and the 15σ Mass Tension" — exclusion-limits paper |

Both papers can use the **same Markdown source-of-truth workflow** (per the 2026-09-17 user decision on .md-only drafting). The reviewer pattern from `qwen2.docx` (open Doors, get honest negative results, publish the limits) is exactly the right approach for tier3.

---

## File inventory

| Branch | Paper draft | Test report | Roadmap |
|---|---|---|---|
| `wip/cloud-9-relhic` | `v0.3-prelim/docs/PAPER_V1_DRAFT.md` (v1.8) | `v0.3-prelim/docs/SELF_CHECK_REPORT_2026_09_17_v2.md` | `v0.3-prelim/docs/POST_PAPER_ROADMAP_2026_09_17.md` |
| `wip/tier3-sequential-T90-magnetic` | (no paper draft yet) | (no self-check report yet) | (no roadmap yet) |

The tier3 branch has the **scientific content** (T103-T116 results) ready but does NOT yet have:
- A consolidated paper draft
- A self-check test report
- A post-paper roadmap

These should be created if/when tier3 is promoted to paper status.

---

## Action recommendation

For the current session, the **`wip/cloud-9-relhic` branch is the active work** (Paper v1.8). The **`wip/tier3-sequential-T90-magnetic` branch is paused** at commit `7ff95a6` ("docs(branch split): Sequential branch; pause development").

If the user wants to:
1. **Promote tier3 to paper status**: create a paper draft + self-check + roadmap on that branch
2. **Merge tier3 changes into master**: requires careful review since the methodology is fundamentally different
3. **Archive tier3**: keep the branch for reference but stop development

The user can choose based on their priorities. For now, this document exists to prevent reviewer confusion between the two branches.