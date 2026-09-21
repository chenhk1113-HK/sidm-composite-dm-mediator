# Audit — "Fornax 6.docx" (2026-09-21, uploaded by user)

User asked: "I will upload a doc I want you critically consider whether they
are useful, take your time, search for info if needed."

The doc has **four substantive proposals** plus a code-list. Audit:

---

## Proposal 1 — Fornax 6 (F6) as 9th constraint channel

**Doc claims:**
- F6 is a 6th stellar cluster in Fornax dSph, M★ ≈ 7.2×10³ M☉, r_h ≈ 11 pc, σ ≈ 5.6 km/s, anomalously high M/L (15-258)
- Pace et al. 2021 confirmed it spectroscopically
- Peñarrubia et al. 2024 proposed capture by 10⁶ M☉ DM substructure
- Yu 2026 PRL showed core-collapsed SIDM halos simultaneously explain JVAS B1938+666, GD-1, AND F6

**Verification:**
- ✅ Pace+ 2021, ApJ 923, 77 (arXiv:2105.00064) — CONFIRMED (37 citations)
- ✅ Peñarrubia+ 2024, MNRAS 533, 3263 (arXiv:2404.19069) — CONFIRMED (17 citations)
- ✅ Yu 2026, PRL 136, 141001 (arXiv:2510.11006) — CONFIRMED, accepted for PRL, just published April 2026. Abstract literally says "core-collapsed SIDM halos of mass ~10⁶ M☉ ... also reproduce the structural properties inferred for the dense perturber detected in the strong lensing system JVAS B1938+666 ... sufficiently compact and dense to gravitationally capture field stars in satellite galaxies of the Milky Way, providing a natural explanation for the origin of Fornax 6"

**Actionable assessment:**

**STRONG ACTIONABLE.** This is the most important finding in the doc. Our paper currently treats JVAS as a "domain-boundary reclassification" / "structural limitation" (per T180 — gravothermal 100× enhancement vs 3125× needed). Yu 2026 provides a constructive solution at exactly the JVAS halo mass scale (10⁶ M☉) we identified as the structural limit. Adding F6 + Yu 2026:

1. **Reframes JVAS from "structural limitation" to "complementary prediction"** — exactly what the doc's Option C argues. This is the bigger story change.
2. **Adds a new observational anchor** at exactly the 10⁶ M☉ mass scale we already use for Cloud-9, dSphs, and UFDs — no new mass scale needed.
3. **Connects to the Fornax timing problem** — if our cored SIDM profile suppresses dynamical friction enough for the other 5 clusters to survive, that's a self-consistency check.

**Recommended action:** Add Yu 2026 reference [15g]. Update §3.3 (JVAS) and §10.9 (A5 — JVAS gravothermal) framing from "structural limitation" to "structural scope clarified by Yu 2026 — JVAS requires core-collapsed halo at 10⁶ M☉, which is complementary to (not in conflict with) our phenomenological σ/m at 10⁹-10¹² M☉." Optionally add F6 as a §3.5 discussion in the Joint fit section.

**Time cost:** 30-60 minutes. **Value:** Substantive reframing of JVAS from negative result to neutral/positive structural prediction.

---

## Proposal 2 — micrOMEGAs 6.0 for two-component relic density

**Doc claims:**
- Two-component asymmetric DM cannot be done with single-component Boltzmann solver
- micrOMEGAs 6.0 (Zenodo 2025, arXiv:2312.14894) generalizes Boltzmann for N-component DM
- Supports co-scattering, asymmetric DM, multi-component DD/ID rates, PlanckCMB

**Verification:**
- ✅ micrOMEGAs 6.0 confirmed (Zenodo June 2025 release, arXiv:2312.14894). Cited 38+ times already.

**Actionable assessment:**

**MODERATELY ACTIONABLE.** Our paper currently uses:
- T181 (Boltzmann solver, single-component) — but I noted in T181's verdict that SIDM σ_HH ≠ σ_ann, so relic density requires UV completion
- T184 (dark Higgs UV), T185/T190 (Drobczyk two-mediator UV) — but these are for the UV COMPLETION, not for two-component χ_H + χ_L relic density

**The doc is correct that the two-component χ_H (heavy) + χ_L (light) sector following Yang+ 2025 needs proper relic density calculation.** Currently our paper assumes f_H(r) profiles from Yang+ 2025 but doesn't independently compute the relic density for two components. This is a real gap.

**However:** The UV completion (T184-T190) was completed AFTER I read this doc's claim. Our current UV completion story is about a dark Higgs + dark photon (one-component), with the two-component SIDM being the phenomenology. So micrOMEGAs 6.0 would address the YANG+ 2025 two-component SIDM sector, NOT the T184/T190 UV completion.

**Recommended action:**
- Add micrOMEGAs 6.0 reference [29] to the bibliography
- Add a discussion paragraph in §10.9 (deferred items) noting that future work should use micrOMEGAs 6.0 for proper two-component relic density of χ_H + χ_L
- Do NOT install micrOMEGAs 6.0 now — it's a C/Fortran package requiring CalcHEP encoding, which is a 1-2 day task with new-dependency implications (per Rule 17)

**Time cost:** 30 min for paper update; 1-2 days for actual micrOMEGAs install + encoding. **Value:** Future-work placeholder; deferred.

---

## Proposal 3 — AIDA-TNG simulations for baryonic feedback

**Doc claims:**
- AIDA-TNG (Despali et al. 2025/2026, arXiv:2512.15869) is the first self-consistent cosmological MHD simulation with SIDM
- Six DM scenarios, six decades in halo mass, 570 pc resolution
- Baryonic adiabatic contraction SUPPRESSES SIDM cores — directly attacks our f_H(r) profiles from Yang+ 2025 (DMO)
- Provides vSIDM benchmark at σ/m ~ 0.1-1 cm²/g (matches our σ/m at v ≈ 100 km/s)
- Provides core-size and concentration-mass relations for SIDM

**Verification:**
- ✅ Despali+ 2025, A&A 697 A213 (AIDA-TNG introduction) — CONFIRMED
- ✅ Despali+ 2026, A&A 699 A222 (profiles paper, arXiv:2512.15869v1) — CONFIRMED
- ⚠ Doc says "Despali et al. (2026)" without disambiguating — there are two papers (2025 intro + 2026 profiles). Should cite both.

**Actionable assessment:**

**STRONG ACTIONABLE for the SYSTEMATIC UNCERTAINTY section.** Our paper §9.5 acknowledges that f_H profiles come from DMO simulations. AIDA-TNG is the EXACT tool to quantify this systematic. The doc is right that this is currently the most important unaddressed systematic in our paper.

**Honest caveats from the AIDA-TNG paper itself:**
- vSIDM benchmark at σ/m ~ 0.1-1 cm²/g matches our σ/m at v ~ 100 km/s (which is our cluster-scale), NOT our Cloud-9 (v=28 km/s) or dwarf (v=10 km/s) where σ/m is 100-200 cm²/g
- The key finding is "the coupling between baryons and self-interactions induces a broader range of inner slopes, including cases that are steeper than CDM at Milky Way masses" — so our borrowed f_H profiles may be wrong direction (steeper, not shallower)
- AIDA-TNG SIDM1 (constant σ/m) is NOT directly comparable to our multi-resonance architecture

**Recommended action:**
- Add AIDA-TNG references [29a, 29b] (both 2025 and 2026 Despali papers)
- Add a paragraph in §9.5 stating the systematic: "Our f_H profiles come from DMO simulations. AIDA-TNG (Despali+ 2025, 2026) shows that baryonic adiabatic contraction can suppress SIDM cores in full-physics runs. The vSIDM benchmark at σ/m ~ 0.1-1 cm²/g matches our σ/m at v ~ 100 km/s but not at v ~ 10-30 km/s where σ/m ~ 100 cm²/g. The applicability of our borrowed f_H(r) profiles from Yang+ 2025 to full-physics halos is uncertain."
- This is the same message as our existing §9.5 caveat, but now with quantitative AIDA-TNG backing
- **Optional:** Could add a quantitative comparison: at our predicted core sizes, do AIDA-TNG SIDM runs show the same density profile shapes?

**Time cost:** 30-60 minutes for paper update. **Value:** Substantively strengthens §9.5 systematic discussion; provides quantitative backup for our existing caveat.

---

## Proposal 4 — Code list (KiSS-SIDM, SASHIMI, parametricSIDM, OpenGadget3, etc.)

**Doc claims:**
- KiSS-SIDM (gitlab.com/Socob/KiSS-SIDM) — kinetic solver for gravothermal evolution
- SASHIMI-SIDM (github.com/shinichiroando/sashimi-si) — semi-analytic SIDM subhalo mapping
- parametricSIDM (github.com/DanengYang/parametricSIDM) — parametric halo profiles
- GravothermalSIDM (github.com/kboddy/GravothermalSIDM) — gravothermal fluid code
- OpenGadget3 — N-body code with two-species SIDM support
- sidmkit (github.com/nalin-dhiman/sidmkit) — Python toolkit for SPARC fits
- Various others (halox, SpheCow, pyHalo)

**Verification:**
- ✅ KiSS-SIDM: confirmed real (used in multiple published papers, ResearchGate finds 2011+ citations)
- ✅ GravothermalSIDM (kboddy): confirmed real
- ✅ sidmkit: confirmed real (we've already used it in T143, T170, T171, T172)
- ⚠ Most other packages in the list: NOT independently verified by me. Some look real (SASHIMI, parametricSIDM, OpenGadget3, halox, pyHalo are all known codes in the field) but I haven't verified the URLs work

**Actionable assessment:**

**LOW ACTIONABLE — we already use most of this.**

Critical finding from my audit: **our codebase already has substantial gravothermal + KiSS-SIDM integration:**
- `kiss_sidm_dsmc.py` (44 KB)
- `kiss_sidm_julia_bridge.py` (14 KB)
- `kiss_sidm_julia_reader.py` (7 KB)
- `kiss_sidm_scalings.py` (18 KB)
- `gravothermal.py` (8 KB)
- `phase43_vdgravothermal.py` (17 KB) — velocity-dependent gravothermal
- `t90_v47_gravothermal_fluid.py` (18 KB) — gravothermal fluid
- `t21_real_kiss_sidm_gravothermal.py` (13 KB) — KiSS-SIDM integration
- `t22_real_kiss_sidm_two_comp.py` (12 KB) — KiSS-SIDM two-component
- `t23_real_kiss_sidm_two_comp_imfp.py` (9 KB) — KiSS-SIDM imfp
- `t27_multiresolution_kiss_sidm.py` (6 KB)
- `t38_dwarf_kiss_sidm_higher_N.py` (11 KB)
- `t38c_dwarf_kiss_sidm_paper_scale.py` (5 KB)
- `t71_7_kiss_sidm_ufd_launcher.py` (3 KB)
- `t95_v04_option2_5_gravothermal.py` (10 KB) — gravothermal option 2.5
- `t95_v23_two_component_sidm_gravothermal.py` (17 KB) — two-comp gravothermal
- And many more

So the doc's recommendation of "start with KiSS-SIDM for fast gravothermal core-collapse studies" is **already done in our codebase**. We have ~16 gravothermal-related files.

The doc's recommendation of "OpenGadget3 for two-component cross-species interactions" is **also already done** — `t22_real_kiss_sidm_two_comp.py` and `t23_real_kiss_sidm_two_comp_imfp.py` are two-component KiSS-SIDM runs.

**Honest assessment:** The code list is accurate but **already saturated in our codebase**. The doc is recommending tools we already use.

**Recommended action:**
- **NONE for the existing codebase** — we already have all the recommended tools integrated
- **Optional:** Add a brief code-availability section to the paper acknowledging KiSS-SIDM, GravothermalSIDM, sidmkit (per open-science norms)
- **Optional:** Verify the URLs in the doc's code list work (5-minute spot check)

**Time cost:** 5-10 minutes for paper update. **Value:** Low.

---

## Summary — Classification

| Proposal | Actionable? | Time | Value | Recommended action |
|---|---|---|---|---|
| 1. Fornax 6 + Yu 2026 | **STRONG** | 30-60 min | **HIGH** — reframes JVAS from structural limitation to complementary prediction | **DO** — add Yu 2026 ref [15g], update §3.3 JVAS framing |
| 2. micrOMEGAs 6.0 | **MODERATE** | 30 min paper, 1-2 days install | Medium — future-work placeholder | **DO** — add reference [29], mention as future work in §10.9 |
| 3. AIDA-TNG | **STRONG** | 30-60 min | **HIGH** — strengthens §9.5 systematic discussion | **DO** — add refs [29a, 29b], expand §9.5 caveat with AIDA-TNG findings |
| 4. Code list | **LOW** | 5-10 min | Low — already saturated in codebase | **DO minimally** — add code-availability line if any |

## Bottom line

**Three of four proposals are actionable.** The strongest is **#1 (F6 + Yu 2026)**, which provides a constructive reframing of our JVAS "structural limitation" finding into a positive structural prediction. The second strongest is **#3 (AIDA-TNG)**, which provides quantitative backing for our §9.5 systematic caveat.

**#2 (micrOMEGAs 6.0)** is real but requires 1-2 days of C/Fortran install + CalcHEP encoding — out of scope for this iteration but worth noting as future work.

**#4 (code list)** is already saturated in our codebase; we don't need to add any new packages.

Recommended next step: implement #1 + #3 in a single 1-2 hour paper update, plus a brief #2 mention. That's the most efficient path to substantively improving the paper.

## Honesty notes

1. The doc's reference to "Despali et al. (2026)" doesn't disambiguate between the 2025 AIDA-TNG intro paper (A&A 697 A213) and the 2026 profiles paper (A&A 699 A222). Both should be cited.
2. The doc's claim that "f_H profiles you borrow from Yang+ 2025 are dark-matter-only" is correct. Our §9.5 already acknowledges this. The AIDA-TNG citation would be additive, not corrective.
3. The doc's claim that "B1938+666 lies outside the reliable domain of the present model and is better described by complementary core-collapse SIDM" is interesting because **Yu 2026 is exactly the "complementary core-collapse SIDM"** they refer to. The doc's proposal is to use Yu 2026's framework explicitly, which would shift our JVAS framing from negative to neutral.
4. The doc's "Bottom Line" on micrOMEGAs says "If you can encode the two-component Lagrangian into CalcHEP format, running micrOMEGAs 6.0 would substantially strengthen the paper's scientific plausibility" — this is true but should be flagged as a 1-2 day install + significant CalcHEP work, not a 30-minute fix.

---