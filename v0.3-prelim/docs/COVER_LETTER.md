# Cover Letter — v19.0 submission (Phase 3.2)

**To:** Editor, JCAP (primary) / PRD (fallback)
**From:** K. Lam, sidm-composite-dm-mediator project
**Date:** 2026-09-27
**Subject:** Multi-component velocity-dependent SIDM constraint map + KiSS-SIDM numerics — submission draft

---

## Paragraph 1 — What the paper is

We present a velocity-dependent multi-component self-interacting dark matter (SIDM) framework that
maps the parameter space of allowed σ/m(v) across **eight independent observational channels**
spanning four orders of magnitude in velocity (UFD v ≈ 3 km/s to cluster v ≈ 500 km/s). The work
documents **five independent UV completion no-go theorems** (magnetic dipole DM, hidden U(1),
GeV-scale inelastic DM, p-wave resonance, one-mediator UV systematic) and demonstrates that
Path F1 — a three-term σ_eff = f_H² σ_HH + 2 f_H f_L σ_HL + f_L² σ_LL decomposition — is
structurally sufficient to reach SPARC's σ/m ≈ 0.193 via the σ_HL cross-section term.
Additionally, we contribute a **methods section on KiSS-SIDM v0.0.1 numerics** documenting three
numerical bug fixes and a reproducibility recipe that reduced endpoint-timing variance by 28×.

## Paragraph 2 — What the paper is NOT

This paper is **explicitly framed as a constraint map and no-go catalogue, not a unified
particle-physics derivation.** We do not provide a quantitative Cloud-9 t_core measurement —
KiSS-SIDM's adaptive grid resolution is exhausted at the simulated 30-70 Myr window. We do not
claim first-principles f_H from N-body (Yang+ Fig. 2 is borrowed at 2800× larger σ/m).
The Cloud-9 σ/m ≥ 50 floor is treated as a systematic upper bound (per Turini &
Benítez-Llambay 2026 environmental systematics), not a hard physical requirement. The Cloud-9
vs dSph tension is **unresolved** at Phase 44 parameters. Path F1 is **resolved only under
borrowed f_H**; under Yang+ 2025-derived f_H it is marginal, under T202 N-body f_H it is not
resolved, and under the priored free fit it fails SPARC at log L = -2.03 (z ≈ 2.0).

## Paragraph 3 — Why JCAP

JCAP is the right venue because the field needs **honest boundary maps** rather than incremental
unification claims. Negative results (five no-go theorems, parameter-regime refutations, N-body
disagreements) and methods contributions (KiSS-SIDM bug fixes) fit the journal's scope. The
paper's structural fix — Path F1 — provides a concrete framework for the velocity-dependent
multi-component SIDM community to anchor σ_eff decomposition against. The 8-channel coverage
under pinned prescriptions (4 of 8 under yang, 6 of 8 under borrowed, with the clear/marginal
split made explicit) is a citable map for future SIDM surveys (LSST/Rubin UFDs, Euclid strong
lensing, JDEM/SKA-era dSph follow-up).

---

## Submission checklist

- [x] Abstract ≤250 words, leads with "4 of 8 channels under physically motivated f_H"
- [x] Path F1 verdict split in §3.7 (moved from §9.11 per devplan Refinement 2)
- [x] §10.5b methods-only lead-in (per devplan Refinement 3)
- [x] §9.12 host-halo gravothermal closed at Phase 44
- [x] §10.4d Cloud-9 as systematic upper bound (Turini & Benítez-Llambay + Zhang+ Crater II)
- [x] 4 figures generated (Fig 1 sigma_m_v, Fig 2 Path F1 verdict, Fig 3 channel pass rate, Fig 4 T215 memory cap)
- [x] Standing-numbers table (24 numbers, zero drift)
- [x] audit_claims.py passes 24/24 + 7/7 regex
- [x] pytest test_paper_claims.py passes 12/12
- [x] SUPERSEDED T215 docs archived to docs/archive/t215/

## Referee-objection responses

(Prepared per devplan Phase 3.3 — see `docs/REFEREE_RESPONSES.md`)

## Sign-off

This paper represents ~6 months of methodology development across 6 rounds of internal review
plus 10 rounds of T215 numerics investigation. We believe it makes the SIDM literature
stronger by being explicit about what is established, what is borrowed, and what remains
unresolved — and we invite the community to use the standing-numbers table and KiSS-SIDM
patches as starting points for their own work.

— K. Lam, on behalf of the project team (Hermes-assisted)