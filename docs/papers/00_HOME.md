# v19.2-F Papers Vault (Obsidian-compatible)

This is a knowledge base for the v19.2-F project's paper references. It is organized as an Obsidian vault (markdown with bidirectional `[[wiki-links]]`). To use in Obsidian: open this directory as a vault.

**Location:** `C:\Users\lamkuenai\projects\sidm-composite-dm-mediator\docs\papers\`
**Last updated:** 2026-10-17
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

## Verified papers (full text downloaded + key values verified)

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

**Known gap:** ~19 cited slots still have no local PDF (out of option-2 scope). The shorthand
"Yang+ 2024" refers to TWO papers — [17] arXiv:2305.05067 and [43] arXiv:2305.16176; [43] is
marked NOT TO DOWNLOAD in the registry but is cited and implemented in code. See registry §7.9.

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
- v40.4: 2305.16176 (wrong) → 2305.05067 (correct) for Yang+ 2024 gravothermal
- v40.6: fabricated verbatim quote attributed to 2605.00093 (corrected in v40.11)
- v40.6: 2510.05682 with wrong A&A id (corrected in v40.11)
- v40.6: 2508.20179 with wrong v ~ 1000 km/s (corrected in v40.11)

## Cross-references
- See also: `docs/V19_2_F_REFERENCE_DATA_REGISTRY.md` (the canonical registry)
- See also: `constants.py` (locked values)
- See also: `scripts/constants.py` (σ/m formula parameters)
