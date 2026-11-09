# V19.2-F — Y24 / profile-family recheck of the Cloud-9 c-M tension claim

**Date:** 2026-11-09. **Trigger:** the profile-family caveat added to `PAPER_V1_DRAFT.md` §5
(citing Despali+ 2026 AIDA-TNG profiles paper [48]) was a live objection to the paper's
headline, so the headline was rechecked rather than left with a caveat attached.

**Reproduce:** `C:/Python314/python.exe v0.3-prelim/code/v19_2_f_y24_profile_family_recheck.py`
(every number below is printed by that script or quoted from a KB-extracted paper text).

---

## 1. Claim under test

From `PAPER_V1_DRAFT.md` §5 (headline block, unchanged by this recheck):

- CDM interpretation of Cloud-9 requires **c_200 ~7 sigma below the concentration-mass median**.
- Best-fit SIDM interpretation (sigma/m = 483 cm^2/g, **c_200 = 4.0**) gives **3.2 sigma below the median**.

Both numbers descend from Ohana+ 2026, who fit Cloud-9 with an **NFW** halo; the sigma counts
use a **0.16 dex** scatter (DK14 convention, chain verified in the v19.2-B round).

## 2. What [48] actually says (verbatim, AIDA-TNG profiles paper, A&A 708, A47)

From `docs/papers/verified/_extracted_text_20261109/2512.15869.txt`:

- **Y24 definition** (§2, eq 2): the parametric SIDM profile of Gilman+ 2021 and Yang+ 2024 —
  NFW outside the core, flat core of size r_c inside, beta = 4; the core radius enters through
  "the constraint r_c <= r_Y"; "the Y24 profile at r -> 0 ... reduces to the NFW profile".
  Concentrations are computed "using r_Y".
- **Einasto fits are biased low** (§4.2): SIDM1/vSIDM Einasto concentrations "remain
  systematically lower than CDM in all masses. This is a direct consequence of the inner core,
  whose presence is not fully absorbed by the Einasto scale radius."
- **Y24 fits are not** (§4.2, Fig 4 right panel): "Here, the inferred concentrations for both
  SIDM models closely match the CDM relation. This arises naturally from the fact that
  r_c <= r_Y ..."
- **The c-M relation itself is declared insufficient** (§4.2): "The concentration-mass relation
  is thus an incomplete description for SIDM profiles. A more precise parametrisation can be
  obtained by combining the concentration-mass relation with the mass dependence of the core
  size" — their eq (3): `y(SIDM1) = 0.37 - 0.5x + 0.0026x^2`, `y(vSIDM) = 0.16 - 0.11x`,
  with `x = log M_200c`, `y = log(r_c/r_200c)`.
- **DMO SIDM intrinsic concentrations are unchanged** (§7): the core does not shift the true
  concentration of the halo relative to CDM.
- **Regime** (§3, Fig 6): their SIDM1 model has sigma/m = 1 cm^2/g; the profile panels are for
  haloes in the mass range log M_200c = [12, 13].

## 3. Leg A — the paper's own sigma bookkeeping is not internally consistent

Solving the draft's own pair (c_200 = 4.0 at 3.16 sigma, 0.16 dex) gives an implied
**median c_200 = 12.81** at Cloud-9's mass. Under that single convention:

| c_200 | draft reports | recomputed at median 12.81, 0.16 dex | median the draft's number implies |
|---|---|---|---|
| 4.0 | 3.16 sigma (§2.7) | **+3.16 sigma** | 12.81 |
| 6.0 | 0.32 sigma (§2.6c/d, Elbert+ saturated) | **+2.06 sigma** | 6.75 |
| 26.4 | -1.42 sigma (retracted v40.39, Yang+ Eq 5 extrapolation) | **-1.96 sigma** | 15.65 |

Three different medians (6.75, 12.81, 15.65) are in use inside one analysis. Consequences:

1. The headline reduction "3.2 sigma -> 0.3 sigma" is **not reproducible** from any single
   median + scatter convention. Under the convention the paper itself uses for the 3.16 sigma
   number, the Elbert+ saturated prediction c_200 = 6.0 sits **2.06 sigma** below the median,
   not 0.32 sigma.
2. §5 (c_200 = 4.0, 3.2 sigma) and §2.6c/d (c_200 = 6.0, 0.32-1.31 sigma) are **different
   quantities** presented as the same result: 4.0 is Ohana+'s fitted value, 6.0 is the
   framework's saturated c-τ prediction.

**This is defect D9** (see §7). It is arithmetic, not interpretation.

## 4. Leg B — a Y24 fit for Cloud-9 is not available with what exists

Two independent walls, both hard:

**(i) The published Y24 parametrisation does not reach Cloud-9's state.** The framework's own
Y24 implementation (`v0.3-prelim/code/gravothermal_yang2024.py`, from [43] eq 2.3) has
`TAU_FIT_RANGE_MAX = 1.3`. The factors `f_rs(tau) = r_s/r_s,0` are physical only inside that
window:

| tau | f_rs | in range | c_200 = c_0 / f_rs (c_0 = 12) |
|---|---|---|---|
| 1.0 | 0.4547 | yes | 26.4 |
| 1.3 | 0.0956 | yes | 125.5 |
| 16.3 (framework's Cloud-9 tau, f_H = 0.297) | -1702 | **no** | unphysical (r_s <= 0) |
| 46.3 / 185.3 | -4.0e4 / -2.6e6 | **no** | unphysical |

The framework places Cloud-9 at tau = 16-185 (§2.6c table), i.e. **12-140x beyond the range
where the Y24 evolution factors are physical**. Note also: `f_rs(tau=1)` reproduces exactly
**26.4**, the retracted v40.39 "Yang+ Eq 5 extrapolation" concentration — that number was the
Y24 fit factor evaluated at tau = 1 and then used at tau = 16. The retraction was right, and
this is the mechanical reason.

**(ii) [48]'s own numbers do not extrapolate to Cloud-9's regime.** Their sigma/m = 1 cm^2/g at
log M = 12-13; Cloud-9 is 5e9 Msun (log M = 9.70) at sigma/m = 50-483 cm^2/g. Forcing eq (3)
down to Cloud-9's mass, with r_200 = 35.3 kpc (rho_crit = 136 Msun/kpc^3, H0 = 70; cross-checked
against r_200(1e12) = 206 kpc x (5e9/1e12)^(1/3)):

- SIDM1: log(r_c/r_200c) = -4.23 -> r_c = 0.006% of r_200 = **0.002 kpc**
- vSIDM: log(r_c/r_200c) = -0.91 -> r_c = 12.4% of r_200 = **4.4 kpc**
- the framework's own Cloud-9 core floors (§2.6d) are 30% and 50% of r_200 = **10.6 and 17.6 kpc**

A 5,000x discrepancy in core size confirms the extrapolation is invalid, not merely imprecise.

## 5. Leg C — what the profile family does to the claim

Direction, from [48] §4.2 and from the Y24 factors above, agrees:

- Fitting a cored halo with NFW or Einasto **underestimates** the recovered concentration
  ("not fully absorbed by the Einasto scale radius").
- Fitting the same halo with Y24 returns concentrations that **closely match the CDM relation**
  — and inside its valid range the Y24 family *raises* concentration (12 -> 26 at tau = 1).

So the 3.2 sigma deficit is, in part, **a property of the NFW fit that measured it**, not a
pure measurement of the halo. Two readings follow, and the paper currently implies neither:

- **Favourable reading:** if a Cloud-9 halo were fitted with the family designed for cored
  halos, its fitted concentration would move toward the median, so the SIDM repair would be
  *larger* than 3.2 sigma suggests — potentially near 0 sigma.
- **Deflationary reading:** if a SIDM halo's Y24-fitted concentration already "closely matches
  the CDM relation" [48 §4.2], then a SIDM halo needs no special explanation for its
  concentration, and the framework's "SIDM relieves the c-M tension" argument loses most of
  its discriminating power — the same paper that supplies the published precedent for the
  argument (Yang+Yu+An 2020 [53], CDM needs c_200 = 4 in DF2) also says the observed offset is
  family-dependent.

**Verdict on the headline:** the 7 sigma -> 3.2 sigma pair **survives as a statement about
NFW-family fits of Ohana+'s data**, and must be labelled as such. It **cannot be upgraded to a
profile-marginalised result** with what is available (no N-body SIDM halo of Cloud-9's mass and
cross-section exists in this project, and the published Y24 parametrisation does not cover its
tau). It should not be presented as model discrimination until either is fixed.

## 6. What would actually settle it

1. An N-body SIDM halo at M_200 ~ 5e9 Msun with sigma/m ~ 174 cm^2/g (or the velocity-dependent
   form), fitted **three ways** — NFW, Einasto, Y24 — with c_200 and its scatter reported per
   family. That single experiment decides whether 3.2 sigma is physics or fit artifact.
2. Re-deriving the framework's c-M tensions with **one** stated median + scatter (D9).
3. If Y24 is to be used beyond tau = 1, a parametrisation that is physical at tau > 1 — [43]'s
   eq 2.3 is not one.

## 7. Defects created by this recheck (recorded in `docs/V19_2_F_REFERENCE_DATA_REGISTRY.md`)

- **D9 — sigma bookkeeping inconsistency.** Three implied medians (6.75 / 12.81 / 15.65) in the
  c-M tension statements; "3.2 sigma -> 0.32 sigma" not reproducible. Fix requires recomputing
  §2.6c/d and §5 with one convention; changes a headline number, so it is left for a decision.
- **D10 — phantom citation in code.** `v0.3-prelim/code/v19_2_f_loop1_segue1_veff_check.py`
  attributes its M2 vector-portal model (m_rho = 0.05 meV, Gamma_rho/m_rho = 1) to
  "Chu, Hambye, Tytgat 2018 (M2 model, arXiv:1712.02521)". **arXiv:1712.02521 is
  "An integrated single- and two-photon non-diffracting light-sheet microscope",
  Rev. Sci. Instrum. 89, 043701 (2018)** — an optics paper, authors Lau/Chiu/Zhao/Zhao/Loy/Du.
  A Crossref author query for Chu+Hambye+Tytgat over 2017-06 to 2019-06 returns **no** such
  three-author 2018 paper. The M2 mechanism the paper cites elsewhere is
  Chu, Garcia-Cely & Murayama 2019 [7]/[28]; the vector-portal unstable-mediator construction is
  Chu, Hambye & Tytgat 2012 [29] (JCAP 05 (2012) 034, arXiv:1112.0493 — verified).
- **D11 — stale citation slots at one body site.** §"150 prefactor" line read
  "Balberg+ 2002 [7], Koda+ 2011 [23], Pollack+ 2015 [48]", but [7] = Chu+ 2019, [23] = Yu 2026,
  and [48] is now Despali+ 2026; Koda and Pollack had no entries at all. Corrected to
  Balberg+ 2002 [18], Koda & Shapiro 2011 [55], Pollack+ 2015 [56], both newly verified
  (MNRAS 415, 1125-1137 (2011); ApJ 804, 131 (2015)).

## 8. Side finding (not adjudicated) — rho_crit unit constants

The recheck's r_200 cross-check exposed an inconsistency in the project's own constants:
`phase36_concentration_dependent_collapse.py` (140 Msun/kpc^3), `T208_path_b...` (138.1) and
`v19_2_e_b_per_halo_gravothermal.py` (141) are mutually consistent and match 136 Msun/kpc^3 at
H0 = 70. But `t90_v27_relhic_hydrostatic.py:93` declares `RHO_CRIT = 1.3398e-7 # M_sun/kpc^3`
(10^9 too small as labelled) and `t16_kiss_sidm_vs_fluid.py:77` declares `rho_crit = 1.4e8
# M_sun/kpc^3` (10^6 too large as labelled, its own comment says "order of magnitude").
Flagged, not fixed — the scripts may be internally consistent in some other unit; each needs its
own audit before any number derived from them is cited.

## 9. Sources used

- Despali+ 2026 AIDA-TNG profiles paper, A&A 708, A47, arXiv:2512.15869v2 — KB extract
  `docs/papers/verified/_extracted_text_20261109/2512.15869.txt` (§2, §3, §4.2, §7).
- Yang, Nadler, Yu & Zhong 2024 [43] as implemented in `gravothermal_yang2024.py` (eq 2.3 factors,
  `TAU_FIT_RANGE_MAX = 1.3`).
- Crossref (venues/DOIs), InspHEP (AIDA-TNG arXiv IDs), arXiv API (paper identity checks).
- `v0.3-prelim/code/v19_2_f_y24_profile_family_recheck.py` — all arithmetic above.
