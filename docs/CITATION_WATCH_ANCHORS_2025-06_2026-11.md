# Citation Watch — SIDM v=150 anchors (window 2025-06 → 2026-11)

Compiled 2026-11-03. Abstract-level review only. Sources: Semantic Scholar
`/paper/arXiv:<ID>/citations` (rate-limited on this shared IP; succeeded
intermittently) **union** OpenAlex `filter=cites:` (reliable substitute);
abstracts + dates from the arXiv API `id_list` endpoint.

## Anchors (verified)

| Tag | arXiv ID | Title | First author | Date | Project ref |
|---|---|---|---|---|---|
| [54c] Sameie+ 2020 | **1904.07872** (v2) | "Self-Interacting Dark Matter Subhalos in the Milky Way's Tides" (PRL 124, 141102) | Omid Sameie | 2019-04-16 | `SIDM_REFERENCE_INTEGRITY_v1.0`; KB `1904.07872_sameie_2020.md` |
| [55b] Lei+ 2026 | **2609.16740** | "Lower central dark matter densities in nearby galaxies than predicted by simulations" (Nature Astronomy, accepted) | Yu Lei | 2026-09-15 | `SIDM_REFERENCE_INTEGRITY_v1.0` |
| [55c] Wang+ 2026 | **2609.19132** | "Massive Galaxy Halos Contain Less Inner Dark Matter Than Predicted" | Yu-Chen Wang | 2026-09-16 | `SIDM_REFERENCE_INTEGRITY_v1.0` |

**⚠️ Anchor description mismatch (flagged):** the task brief describes the
Sameie anchor as *"The Mass Function of High-mass Substructures…"* derived from
**strong-lens flux-ratio anomalies**. The project's registry and arXiv do **not**
support that. `[54c]` = **1904.07872**, which is about **SIDM subhalo core
collapse in the MW tidal field** (Draco/Fornax) — not flux-ratio anomalies, and
not a paper titled "Mass Function of High-mass Substructures." No arXiv paper
with that exact title exists. Either the brief conflated the anchor with a
different (unknown) paper, or the project's `[54c]` is mis-cited. **The project's
own registry is authoritative: anchor = 1904.07872.**

## HEADLINE FINDING — is there any revision of the anchor numbers?

**NO.** Across every citing paper in 2025-06 → 2026-11 (abstract-level), **not one
revises the Sameie, Lei, or Wang numbers**, and **none moves the effective
self-scattering cross-section at ~150 km/s by anything like a factor of 2**.
The "v=150 tension" is **not dissolved** by any 2025-06→2026-11 publication. The
Lei/Wang deficit measurement and the Sameie subhalo-mass-function bound stand
unchanged. The single most substantive new development is a **theory** paper
(Yang & Fan) that *explains* the Lei/Wang deficit rather than revising it.

---

## Papers citing Sameie+ 2020 (arXiv:1904.07872) — 22 in window

Classification: **REVISE** = revises anchor method/numbers · **NEW** = new related
measurement/mechanism · **LOW** = passing/methodological/unrelated.

| # | Date | arXiv | Title (short) | Note |
|---|---|---|---|---|
| 1 | 2025-06-16 | 2412.13065 | COZMIC III — zoom-in SIDM + P(k) suppression | NEW sim suite; velocity-dependent SIDM, core collapse below ~1e9 M☉. No revision of the 150 km/s σ_eff. |
| 2 | 2025-06-23 | 2506.11845 | Chemo-dynamics of Sculptor II | NEW dwarf DM-halo density measurement (actions-based); dwarf-scale, not the 150 km/s MW regime. |
| 3 | 2025-08-01 | 2502.14964 | Universal analytic lensing model for SIDM halos | Methodological; extends gravothermal lensing potentials. No number revision. |
| 4 | 2025-08-08 | 2412.14621 | Diversity & universality: dwarf galaxies w/ SIDM | Idealized N-body stellar-response study. Related; no revision. |
| 5 | 2025-08-29 | 2410.18948 | Gravothermalizing into PBH / boson / cannibal stars | Cosmological early-universe regime. LOW. |
| 6 | 2025-09-10 | 2504.02928 | Core collapse in resonant SIDM across halo mass | NEW; resonance at **v ~ 5–50 km/s** (not 150). Relevant to velocity-dependence but no 150 km/s revision. |
| 7 | 2025-09-10 | 2504.02303 | Two-component SIDM mass segregation | NEW mechanism for halo structural diversity. Related. |
| 8 | 2025-09-13 | 2501.16602 | Central densities in FIRE-2 (CDM vs SIDM) | NEW measurement; baryon-vs-SIDM core discrimination. Dwarf scale. |
| 9 | 2025-09-16 | 2503.10748 | **SIDM Concerto** (14 zoom-ins) | **NEW, most on-topic for [54c]:** measures SIDM subhalo mass function **suppressed ≈50% vs CDM in MW/LMC/group hosts**. Updates the *basis* of the Sameie subhalo-mass-function claim but states **no** revised σ_eff(150) bound. Watch this one. |
| 10 | 2025-10-01 | 2507.09799 | Novel challenges tracking SIDM subhalos | Methodological (Symfind finder in SIDM). No revision. |
| 11 | 2025-10-01 | 2510.01491 | Strong-lensing perturber signatures in SIDM sims | NEW; Concerto halos vs observed low-mass perturbers. Lensing-inference relevant. |
| 12 | 2026-01-13 | 2510.17956 | Strong lensing to detect subhalos w/ steep profiles | Methodological; detectability depends strongly on inner slope β. Shifts lensing *systematics*, not the anchor numbers. |
| 13 | 2026-01-30 | 2601.23264 | MARVELously Dark — velocity-dependent SIDM | NEW sim; σ/m_max = 50 cm²/g at v_max = 35 km/s. Dwarf scale. |
| 14 | 2026-02-09 | 2508.21121 | Pion dark matter in θ vacuum | Model-building; sharp velocity-dependent σ. Theory-side of the 150 km/s resonance idea; no data revision. |
| 15 | 2026-02-27 | 2601.09403 | Collapse vs Disruption (ULDM halos) | Different DM model (ultralight). LOW. |
| 16 | 2026-03-01 | 2509.12317 | Dissipative DM I: Born limit | Theory (cross-sections). LOW for the anchor numbers. |
| 17 | 2026-03-31 | 2504.13004 | Calibrating SIDM gravothermal catastrophe | Methodological; calibrates heat-transfer β. Affects core-collapse modeling used in lensing constraints. |
| 18 | 2026-05-22 | 2605.24174 | Sensitivity of substructure lensing to core-collapse model | Methodological; core-collapse-timeline uncertainty in lensing predictions. Relevant systematic. |
| 19 | 2026-05-22 | 2605.24191 | Hubble astrometry in the 2030s | Instrument whitepaper. LOW. |
| 20 | 2026-09-01 | 2604.08647 | Bypassed core formation in MW-mass SIDM halos | NEW; MW–M31 past-pericenter, baryon-preconditioned immediate core collapse. MW-halo relevant. |
| 21 | 2026-09-14 | 2606.12909 | SIDM/CDM interpretations of JVAS B1938+666 | NEW lensing inference; 1e6 M☉ perturber explained by deep core collapse. |
| 22 | 2026-09-19 | 2609.22758 | Feeding the Void — SIDM BH seeding post-collapse | NEW; core-collapse BH seeding. Related. |

## Papers citing Lei+ 2026 (2609.16740) and/or Wang+ 2026 (2609.19132) — 1 in window

| Date | arXiv | Title | Note |
|---|---|---|---|
| 2026-09-24 | **2609.29114** | Mass-Dependent Dark Matter Deficit from Inelastic Scattering (Da-Neng Yang, Yi-Zhong Fan) | Cites **both** [55b] and [55c]. **NOT a revision** — a theoretical *explanation*: exothermic inelastic DM with vector+scalar mediators, s-wave suppressed at low v, p-wave enhanced at a few hundred km/s, injecting energy and lowering central DM densities (mass-dependent, matching the deficit). Explicitly frames the Lei/Wang "dark matter deficit" as real and seeks a mechanism. The only substantive same-window follow-up to the anchors. |

S2 citation counts at compile time: Wang 2609.19132 → 1; Lei 2609.16740 → 1 (same
paper). OpenAlex → 0 for both (indexing lag, papers are ~7 weeks old).

---

## Bottom line for the project

- The v=150 no-go is **not dissolved**: no citing paper revises either anchor
  number or shifts σ_eff(~150 km/s) by ~2×.
- **Sameie [54c] basis is being actively rebuilt** (SIDM Concerto 2503.10748 and
  the 2510.01491 / 2604.08647 / 2606.12909 lensing-and-simulation line), so the
  *supporting* subhalo-mass-function and lensing literature is churning — but
  none of it has yet replaced the 0.3 cm²/g upper bound the project uses.
- **Lei/Wang [55b,c] are confirmed, not challenged** — the one citer reproduces
  the deficit with a new DM model.
- **Action item:** re-check the `[54c]` citation itself — its topic ("MW tides
  core collapse") does not match the "subhalo mass function / flux-ratio
  anomalies" framing the project attaches to it; the 0.3 cm²/g @ v=150 bound is
  not visible in the anchor abstract and should be traced to its true source.
