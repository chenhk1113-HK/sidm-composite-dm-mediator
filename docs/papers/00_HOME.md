# v19.2-F Papers Vault (Obsidian-compatible)

This is a knowledge base for the v19.2-F project's paper references. It is organized as an Obsidian vault (markdown with bidirectional `[[wiki-links]]`). To use in Obsidian: open this directory as a vault.

**Location:** `C:\Users\lamkuenai\projects\sidm-composite-dm-mediator\docs\papers\`
**Last updated:** 2026-11-09 (intake from the user's "Useful papers.docx": 8 papers added, including the NFW 1996/1997 pair that the paper had never cited; citation defects recorded in registry §7.11). Prior: 2026-11-03 (Tier-2 sweep papers verified — full intake closed).
**Status:** Active, ongoing

---

## Map of Contents

- **[[INDEX]]** — master index of all papers
- **[[Concepts/Cloud-9 Galaxy]]** — Cloud-9 RELHIC overview
- **[[Concepts/SIDM Framework]]** — Self-Interacting Dark Matter model framework
- **[[Concepts/Coupling Convention]]** — α_D ≡ g²/(4π) convention
- **[[Concepts/Resonance Cross-Section]]** — σ/m formula details
- **[[Concepts/Gravothermal Collapse]]** — t_c formula details

---

## Verification levels (read this before trusting a `verified/` entry)

- **Full-text verified** — PDF downloaded and the specific values quoted by this repo cross-checked
  against the paper. These are the entries listed under "Verified papers (full text downloaded +
  key values verified)" below.
- **Abstract-level** — `Status:` line says `VERIFIED (arXiv metadata fetched …; title/authors/abstract
  from arXiv export API)`. On 2026-11-04, 22 summaries for previously uncited arXiv IDs were added at
  this level via `fetch_uncited_kb.sh`, plus 4 papers held in `to_verify/`. They are safe for
  **citation coverage** (title, authors, scope) and **not** yet safe for quoting a number from them.
  `scripts/check_fabrication.py` counts any `verified/` file as a verified ID, so the tool's label is
  coarser than this KB's own levels — do not read "0 unverified citations" as "all values checked".

## Verified papers (full text downloaded + key values verified)

**2026-11-09 — intake from the user's "Useful papers.docx"** (8 papers; registry §7.11). Read end-to-end from pypdf text extraction; every headline number below was spot-grepped against the extracted text before promotion.

- [[9611107 Navarro+FrenkWhite 1997]] — A Universal Density Profile from Hierarchical Clustering — ApJ 490, 493-508, DOI 10.1086/304888. **The profile the paper uses 49x with no citation** (defect D3). Source of eq. 1 and of c = r_200/r_s with rho_crit = 3H^2/8piG.
- [[9508025 Navarro+FrenkWhite 1996]] — The Structure of Cold Dark Matter Halos — ApJ 462, 563, DOI 10.1086/177173. **ABSTRACT-LEVEL ONLY: the 1995 scan's text layer is damaged** (digits split by stray slashes); bibliographic facts verified, numerical values not quotable.
- [[9703057 Burkert 1997]] — The structure of dark matter halos. Observation versus theory — review, no arXiv journal_ref. Background stand-in only; **Burkert 1995 (ApJ 447, DOI 10.1086/309560) has no arXiv record and still has no local PDF** (registry §7.5).
- [[2411.11945 Tran+ 2026]] — Novel density profile for isothermal cores; T25 = 4 rho_c [tanh(r/r_c)/(r/r_c)]^n [1+(r/r_s')^2]^((3-n)/2) — arXiv 2024, published PRD 113(6) March 2026; 8 authors; simulated at 21.94 and 31.98 cm^2/g. Profile-family caveat on every fitted-concentration claim.
- [[2512.15869 Despali+ 2026]] — AIDA-TNG: dark matter profiles and concentrations — A&A **708, A47**, DOI 10.1051/0004-6361/202558686 (the draft's audit file has the wrong venue: defect D1). SIDM1 = 1 cm^2/g constant; SIDM1/vSIDM Einasto concentrations systematically BELOW CDM at all masses; Y24 (Gilman+ 2021 / Yang+ 2024) is the SIDM-native fit.
- [[2002.02102 Yang+Yu+An 2020]] — SIDM origin of NGC1052-DF2/-DF4 — PRL 125, 111105. sigma/m = 3 and 5 cm^2/g; CDM needs c_200 = 4, i.e. **4 sigma below the c-M median**, and is "strongly disfavored"; SIDM raises the fitted concentration through core formation plus enhanced tidal mass loss. Closest published analogue of the Cloud-9 7 sigma -> 3 sigma argument.
- [[2403.11403 Zhang+Bi+Yin 2024]] — Tidal formation of NGC1052-DF2 by SIDM — **unrefereed** (no journal reference in arXiv or Crossref). Adopted band 0.3-10.2 cm^2/g, benchmark 5.0, maximum 13.0.
- [[2607.08818 Sarrato-Alós+ 2026]] — Dark matter density profiles of the Milky Way satellite population — accepted A&A, volume/page not yet registered. Inner slopes -1.5 at M_star ~ 10^5 Msun to 0/-0.4 at ~10^8; core formation begins above ~10^6 Msun; **unmodified NFW over-predicts cored central density by 2-3 sigma**.

**2026-10-27 — option-2 body-leaning set added** (14 papers; see registry §7.9). These are the
papers the PAPER BODY actually leans on, downloaded because §8's rule requires a local PDF +
`.md` summary for every citation. Re-download with `bash docs/papers/fetch_cited_papers.sh`.

- [[2510.11006 Yu 2026]] — core-collapsed SIDM halos unify lens/stream/satellite perturbers [23]
- [[1508.03339 Kaplinghat+ 2016]] — Dark Matter Halos as Particle Colliders [1]/[50d]
- [[1005.4678 Feng+ 2010]] — Sommerfeld Enhancements for Thermal Relic DM [5]
- [[1810.04709 Chu+ 2019]] — Velocity Dependence from Resonant SIDM [7]/[28]
- [[2406.18643 Benítez-Llambay+ 2024]] — Cloud-9 VLA [1a]/[15b]
- [[2206.14395 Girmohanta & Shrock 2022]] — Cross Section Calculations (t- and u-channel) [9]
- [[2210.01132 Girmohanta & Shrock 2023]] — dwarf-to-cluster fit [10]
- [[2609.16740 Lei+ 2026]] — lower central DM densities in nearby galaxies [55b]
- [[2609.19132 Wang+ 2026]] — massive galaxy halos have less inner DM [55c]
- [[2601.17118 Jia+ 2026]] — enhanced isothermal Jeans vs SPARC [52]
- [[1103.0007 Boylan-Kolchin+ 2011]] — Too big to fail? [3]
- [[1804.10385 Duerr+ 2018]] — stable vector mediator [8]
- [[2503.10748 Nadler+ 2025]] — SIDM Concerto [51]
- [[2601.23264 Engelhardt+ 2026]] — MARVELously Dark [49]

**2026-11-03 — new-data sweep Tier 1 added (read end-to-end; verdicts in [[NEW_DATA_SWEEP_2026-11-03]] §7):**

- [[2610.28890 van den Bosch & Tokayer 2026]] — revised SIDM core-collapse calibration (MNRAS accepted) — calibration caveat on the [43] t_c chain
- [[2610.31881 Tekverk+ 2026]] — strong-lensing perturber predictions (JCAP submitted) — corroborates Model III (147.1, 120); contests Model I at cluster scales only
- [[2610.40766 Gilman+ 2026]] — SIDM hints from lensing, particle letter (PRL submitted) — corroboration; no numeric collision with 174@29.4
- [[2609.35974 Gilman+ 2026]] — JWST survey V (PRD submitted) — population support 8:1-24:1 for core collapse

**2026-11-03 — new-data sweep Tier 2 added (read end-to-end; verdicts in each KB entry):**

- [[2510.02247 Nibauer+ 2025]] — GD-1 ABC subhalo inference — background (CDM-consistent subhalo picture; f_sub 0.05±0.08; WDM M_hm<10^8.6)
- [[2510.17956 Kollmann & Nierenberg 2025]] — lensed subhalo profiles — corroborates steep/compact subhalos (α≈2.1-2.2), no σ
- [[2512.01361 Liu & Li 2025]] — GD-1 vs fuzzy/WDM — background (m_WDM>6.2 keV, m_FDM>1.74e-20 eV; no contact with our model)
- [[2601.21432 Chaves-Montero+ 2026]] — GD-1 as early-universe probe — background (isocurvature A_S²<0.379; reinterpretation watch)
- [[2602.20889 Li+ 2026]] — 20 elliptical mass profiles — refinement: J0946+1006 main halo α=1.04±0.10 (Sunnenfeld 1.7 artifact); merger-heated c200 scatter
- [[2604.05237 Nierenberg+ 2026]] — JWST 61-cluster subhalo census — corroborates (weak): 10^8.2-10^8.6 M_sun subhalos observed, CDM-consistent
- [[2604.20958 Jarvis+ 2026]] — GD-1 heated-subhalo cocoon — corroborates (weak): σ_v 2.49→6.13 mas/yr reproduced in CDM
- [[2605.16200 Arora+ 2026]] — 15k Gaia velocity jumps — CONTESTS single-encounter reading (75% complex, 26% clean; GD-1 kicks all complex)
- [[2610.41842 Guillaume+ 2026]] — Sgr merger makes GD-1-like spurs — CONTESTS (spur rates 50/25/28% merger/bar/subhalo; morphology degenerate)
- [[2609.22581 Silva+ 2026]] — DESI Lyα sterile neutrinos — background (Neff<3.41, m_s^eff<0.061 eV; NOT a stream paper — reader misclassification corrected)
- [[2609.29114 Yang & Fan 2026]] — mass deficit from inelastic DM — background/competing explanation (Δ=18.1 keV, σ(300)/m≈0.95 at cluster v; different regime)
- [[2610.26877 Zhu+ 2026]] — DESI DR2 BAO SIDM1 — corroborates conditionally (lnB 5.57/8.72; σ/m<0.01 at v~1000; WATCH: pressures Model III tail ~0.03)
- [[2609.14535 Saifollahi+ 2026]] — Euclid DR1 Fornax-7 — corroborates potential (170 M_sun, 10.4 Gyr, 2.8 kpc from Fornax; no DM measurement)
- [[2606.10006 Crumrine+ 2026]] — mixed DM limits from MW satellites — background; external support for mediator baryon-coupling ceiling (NOT a WD paper — corrected)
- [[2606.21774 Euclid Q1 Starkman+ 2026]] — halo geometry from 13 extragalactic streams — corroborates new channel (q_proj 0.95±0.05; no σ yet)
- [[2609.11328 Besnard+ 2026]] — FDM mass from Euclid ERO globular clusters — background (m22<1.46 Fornax / <1.09 Perseus; NOT Sgr A* — corrected)
- [[2610.28745 Gurian+ 2026]] — cross-code gravothermal calibration — METHODOLOGY CAVEAT with 2610.28890: Knudsen Kn=1 LMFP/SMFP boundary; Yang 150C valid only LMFP C≳0.5; SMFP t∝σ²

Sweep intake is now CLOSED: all 21 candidates adjudicated (4 Tier-1 + 17 Tier-2).

The remaining items in `to_verify/` are pre-sweep historical papers (Adén 2009, Simon 2011, Tulin+ 2013, etc.) with their own pending status.

**2026-11-09 — intake from the user's "Useful papers.docx" (8 papers; citation defects in registry §7.11):**

- [[9611107 Navarro+FrenkWhite 1997]] — A Universal Density Profile from Hierarchical Clustering, ApJ 490, 493-508, DOI 10.1086/304888 — **the profile the paper uses 49× with no citation** (defect D3)
- [[9508025 Navarro+FrenkWhite 1996]] — The Structure of Cold Dark Matter Halos, ApJ 462, 563, DOI 10.1086/177173 — abstract-level only (1995 scan has a damaged text layer)
- [[2411.11945 Tran+ 2024/2026]] — Novel density profile for isothermal cores (T25), PRD 113(6) — profile-family caveat on any fitted-concentration claim
- [[2512.15869 Despali+ 2026]] — AIDA-TNG profiles & concentrations, A&A **708, A47** — SIDM1/vSIDM Einasto concentrations sit BELOW CDM at all masses; draft's audit file has the wrong venue (defect D1)
- [[2002.02102 Yang+Yu+An 2020]] — SIDM origin of NGC1052-DF2/-DF4, PRL 125, 111105 — CDM needs c_200 = 4 (4σ below the c-M median); SIDM repairs it. Closest published analogue of the Cloud-9 7σ→3σ argument
- [[2403.11403 Zhang+Bi+Yin 2024]] — tidal DF2 by SIDM, unrefereed — dwarf σ/m band 0.3-10.2, benchmark 5.0, max 13.0 cm^2/g
- [[2607.08818 Sarrato-Alós+ 2026]] — MW satellite density profiles, accepted A&A — unmodified NFW over-predicts cored dwarfs' central density by 2-3σ
- [[9703057 Burkert 1997]] — review, "Observation versus theory" — stand-in for reading; Burkert 1995 (ApJ 447, L25, DOI 10.1086/309560) has **no arXiv preprint** (KB exception, see §7.5)

**Known gap (CLOSED 2026-10-27):** option 1 has been run — `fetch_all_cited_papers.sh`
downloads the FULL 42-slot bibliography, so every cited paper now has a local PDF.
Re-download with `bash docs/papers/fetch_all_cited_papers.sh`.

**"Yang+ 2024" is TWO papers — RESOLVED site by site (2026-10-27):**
- **[17]** arXiv:2305.05067 — Yang, Jiang, Benson, Zhong, Mace, Du, Zeng, Peter & Fischer,
  MNRAS 533, 4007 (2024). The **velocity-dependent σ/m(v) fit** (Eq. 19-21) and the
  SPARC+BCG cross-section constraints.
- **[43]** arXiv:2305.16176 — Yang, Nadler, Yu & Zhong, JCAP 02 (2024) 032,
  "A Parametric Model for SIDM Halos". **VALIDATED** by reading the PDF: eq. (2.1)
  density profile (β=4), eq. (2.2) collapse time (150 prefactor, C=0.75), eq. (2.3)
  parameter evolution, eq. (2.4) Vmax/Rmax, the BM2 calibration (t_c = 28.7 Gyr at
  σ_eff/m = 7.1 cm²/g) and Cosmo-501 from Table 1. **The registry's earlier "NOT TO
  DOWNLOAD" marking of this paper was wrong** — see registry §7.10.

**Two papers named in the body with no reference entry — SLOTS NOW ADDED:** [18]
Balberg, Shapiro & Inagaki 2002 (astro-ph/0110561, named 11×) and [19] Fischer & Yu
2026 (arXiv:2603.04508, named 9×).

- [[2305.05067 Yang+ 2024 (Cloud-9)]] — gravothermal/isothermal σ/m comparison
- [[2207.13111 Gilman+ 2023]] — resonant SIDM strong-lensing constraint
- [[2508.20179 O'Donnell+ 2025]] — single cluster lensing+kinematics
- [[2510.05682 Sánchez Almeida+ 2025]] — UFD stellar cores SIDM constraints
- [[2605.00093 Jee, Park, Lee 2026]] — double radio relic cluster constraint

## To-verify papers (downloaded but full read pending)
- [[1712.02521 Chu+ 2018]] — M2 model
- [[1306.5010 Tulin, Yu, Zurek 2013]] — foundational SIDM review
- [[1705.02358 Tulin & Yu 2018]] — Phys. Rep. 730 review (the "Kaplinghat+ 2016" reference)
- [[1007.4198 Simon+ 2011]] — Segue 1 kinematics
- [[1808.06634 Read, Walker, Steger 2019]] — M_halo for Segue 1
- [[2508.20157 Anand+ 2025 (Cloud-9)]] — Cloud-9 RELHIC discovery
- [[2012.06611 Andrade+ 2022]] — cluster strong-lensing constraint

## To-verify papers (no arXiv preprint exists)
- [[Walker+ 2007 dSph]] — ApJL 667, L53 — but DOES NOT include Draco/UMi
- [[Walker+ 2016 Tucana II]] — ApJ 819, 53 — no arXiv
- [[Adén+ 2009 Hercules]] — ApJL 706, L150 — likely thesis-only

## Bug history (papers with corrected citations)
- 2026-11-09: `AUDIT_REFERENCES.md` had AIDA-TNG profiles as "A&A 699, A222 (2026)" — actual **A&A 708, A47** (2026-03-26); 699/A222 is a different paper ("Detecting low-mass haloes with strong gravitational lensing"). "Introducing the AIDA-TNG project" was listed as MNRAS 2024 — actual **A&A 697, A213** (2025). See registry §7.11 D1-D2.
- 2026-11-09: NFW 1997 DOI recorded as 10.1086/309191 and NFW 1996 as 10.1086/176418 — **both wrong, recalled from memory**; resolved to 10.1086/304888 and 10.1086/177173 via Crossref. See registry §7.11 D7.
- 2026-11-09: registry §7.5 claimed Burkert 1995 was "cited but no local PDF" — the draft cites no Burkert at all (registry D4).
- 2026-11-09: three arXiv links in the user's "Useful papers.docx" point at unrelated papers (astro-ph/9810021, astro-ph/0403457, astro-ph/9508181). See registry §7.11 D5.
- v40.4: 2305.16176 (wrong) → 2305.05067 (correct) for Yang+ 2024 gravothermal
- v40.6: fabricated verbatim quote attributed to 2605.00093 (corrected in v40.11)
- v40.6: 2510.05682 with wrong A&A id (corrected in v40.11)
- v40.6: 2508.20179 with wrong v ~ 1000 km/s (corrected in v40.11)

## Cross-references
- See also: `docs/V19_2_F_REFERENCE_DATA_REGISTRY.md` (the canonical registry)
- See also: `constants.py` (locked values)
- See also: `scripts/constants.py` (σ/m formula parameters)
