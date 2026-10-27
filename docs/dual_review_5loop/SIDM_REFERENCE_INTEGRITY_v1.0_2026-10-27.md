# SIDM v19.2-F — Reference Integrity & KB Compliance Round

**Date:** 2026-10-27
**Branch:** `wip/v19.2-F-init`
**Commit:** `2915f73` (pushed)
**Scope:** the paper's 42 reference slots, and the project KB's rule that every cited paper must be on disk

---

## 1. Headline

**All 42 cited papers now have a local PDF and a `.md` summary.** The KB rule (§8 of the reference
registry) says *"NEVER cite a paper without local PDF + .md summary + registry entry."* At the start
of this round only **5 of 41** slots complied. Now **42 of 42** do.

Along the way the round found and fixed **eight citation defects** — two of them fabricated
outright — plus one more place where a paper was named in the body with no reference entry at all.

| | Before | After |
|---|---|---|
| Slots with a local PDF + summary | 5 (of 41) | **42 (of 42)** |
| Fabricated / mis-attributed citations | 2 undetected | **0** |
| Wrong page, year, or arXiv ID | not checked | **0** |
| Body-named papers with no reference slot | 3 | **0** |
| Slots whose claim could not be verified | 2 | **0** (removed) |

---

## 2. The rule that was being broken

The registry (§8, locked 2026-10-19) records a standing instruction:

> **"NEVER cite a paper without local PDF + .md summary + registry entry."**
> Per user directive *"I want you to do it auto, no need for my reminder"*

The earlier reference-resolution round had checked a *different* thing: that each citation is
**bibliographically real** — the author, title, journal, volume and page match the live publisher
record. That is necessary but not sufficient. The rule wants the paper **on disk**, so a reader (or
a future session) can open it and check the numbers.

The two checks are not substitutes. A citation can be perfectly real and still be unreadable.

---

## 3. The eight defects, all verified against the live record

### 3.1 The two that were fabricated

**[10]** was printed as *"S. Girmohanta, Y. Yasuoka, Phys. Rev. D 111, 035005 (2025)"*. The implied
DOI `10.1103/physrevd.111.035005` **resolves** — to *Li, Yang, Zhang & Zhu*, "Theoretical bounds on
dark Higgs mass in a self-interacting dark matter model with U(1)′". No Girmohanta–Yasuoka paper
exists in arXiv, Crossref, InspireHEP, Semantic Scholar or OpenAlex.

**[9]** was printed as *"Hong, Kuranchi & Perez 2020"*. The surname **Kuranchi** returns zero author
records in any physics index. The nearest real paper is Hong, **Kurup** & **Perelstein**, PRD 101,
095037 — a conformal *freeze-in production* paper, which cannot support a velocity-dependent
cross-section claim. The audit's own recorded venue (PRD 102, 075025) is *Protasov et al.*,
"Theoretical analysis of antineutron-nucleus data needed for antineutron mirrors" — unrelated to
dark matter.

Both were re-pointed to the verified **Girmohanta & Shrock** papers, and both **load-bearing body
sentences were rewritten**, not just relabelled:

- **L38** — "geometric mass-ladder constructions" → **"mass-dependent u-channel constructions"**.
  Verified against the arXiv full text of 2206.14395: the u-channel amplitude carries explicit
  `m_chi^4` terms, and the abstract states the authors compare results "with the inclusion of both
  t-channel and u-channel exchanges".
- **L90** — "Girmohanta-Yasuoka 2025" → **"Girmohanta & Shrock 2023"**.

### 3.2 Six found in this round

| Slot | What was wrong | The truth |
|---|---|---|
| **[16]** | Credited *"Vegetti, Czoske, Koopmans, Globular Clusters as the First High-Mass Star Clusters of Dwarf Galaxies, MNRAS 408, 430 (2010)"* | **Vegetti, Koopmans, Bolton, Treu & Gavazzi, "Detection of a dark substructure through gravitational imaging," MNRAS 408, 1969 (2010)**, arXiv:0910.0760. **Czoske is not an author.** The title is a different paper's. Page 430 is wrong. *The body use — the JVAS B1938+666 perturber — was already correct.* |
| **[14]** | AJ 152, **3 (2020)** | **"SPARC: Mass Models for 175 Disk Galaxies with Spitzer Photometry and Accurate Rotation Curves," AJ 152, 157 (2016)**, arXiv:1606.09251 |
| **[6]** | arXiv:**1308.0009** | arXiv:**1302.3898**. 1308.0009 is *Kipping, "Efficient, uninformative sampling of limb darkening"* — a different paper |
| **[15d]** | Year 2024 | **Res. Notes AAS 10, 247 (2026)**, arXiv:2608.20911 |
| **[42]** | *"Phys. Rev. D (2025)"* — no volume, no page, no arXiv ID | **PRD 112, 083502 (2025)**, arXiv:2504.02303, doi 10.1103/9952-qf5l |
| **[13]/[30]** | Year 2022 | **2021** — Yang & Yu, PRD 104, 103031 (2021), arXiv:2102.02375 |

---

## 4. The two slots that could not be verified, and were removed

**[11]** ("Yang & Yu 2023, single-breathing-mode mediator") and **[12]** ("Turner et al. 2021,
atomic-DM transitions") have **no matching paper** in arXiv, InspireHEP, Crossref, Semantic Scholar
or OpenAlex. Their DOIs resolve to unrelated papers; the nearest real atomic-DM papers (Kaplan+
JCAP 10 (2010) 021; Geller & Telem PRD 104, 035010) have no Turner author and the wrong date.

At the user's decision both were **removed** — and L90 was rewritten to drop the citations **and
the claims they supported**, keeping the verified [13] and [10] clauses:

> The closest existing work is the**Yang & Yu 2021**[13] core-collapse extension and the
> **Girmohanta & Shrock 2023 [10]** dark-photon model, which is structurally similar but uses a
> different UV-completion story.

Neither slot appeared anywhere else in the body.

---

## 5. Two papers named in the body with no reference entry at all

| Slot | Paper | Named in the body |
|---|---|---|
| **[18]** | S. Balberg, S. L. Shapiro, S. Inagaki, *"Self-Interacting Dark Matter Halos and the Gravothermal Catastrophe,"* ApJ 568, 475 (2002), arXiv:astro-ph/0110561 | **11 times** |
| **[19]** | M. S. Fischer, H.-B. Yu, *"The dark fate of ultra-faint dwarfs: Gravothermal collapse in action,"* arXiv:2603.04508 (2026) | **9 times** |

All 20 mentions now carry a slot number. The same defect class as the old "Yang+ 2024" case.

---

## 6. "Yang+ 2024" was two different papers — resolved site by site

Both were downloaded and read before classifying. **34 occurrences** were individually judged:

- **[43]** arXiv:**2305.16176**, *"A Parametric Model for Self-Interacting Dark Matter Halos"* —
  the paper the code implements. Confirmed from the PDF: eq. (2.1) density profile with β = 4;
  eq. (2.2) collapse time with the 150 prefactor and C = 0.75; eq. (2.3) parameter evolution;
  eq. (2.4) Vmax/Rmax; the BM2 calibration (t_c = 28.7 Gyr at σ_eff/m = 7.1 cm²/g); Cosmo-501
  from Table 1; Fig. 2; σ₀/m = 147.1 cm²/g with w = 24.33 km/s. **28 occurrences → [43].**
- **[17]** arXiv:**2305.05067**, *"A quantitative comparison between velocity dependent SIDM cross
  sections constrained by the gravothermal and isothermal models"* — the **velocity-dependent
  σ/m(v) fit** (double power law, Eq. 19-21) and the SPARC+BCG cross-section constraints.
  **1 occurrence → [17]**: the line introducing the canonical σ/m(v) form.

### The registry was wrong about 2305.16176

The registry's §1 entry marked it **"NOT TO DOWNLOAD"** — reasoning that it was "the same paper as
the v40.4 wrong-citation bug". That inference was wrong. The PDF was downloaded and read: it *is*
the paper `gravothermal_yang2024.py` implements, down to the eq. numbers, the C = 0.75 calibration
constant and the Cosmo-501 test. The v40.4 bug was a *different* mistake — a wrong arXiv ID
attached to a gravothermal-model claim — not evidence that this paper was irrelevant.

**The code's attribution was correct all along.** The registry marking has been superseded.

---

## 7. The KB now covers the whole bibliography

| | count |
|---|---|
| Cited slots | **42** |
| With a local PDF | **42** |
| With a `.md` summary | **42** |
| PDFs in `docs/papers/verified/` | 43 (one duplicate copy of 2305.05067) |

**New tooling, both idempotent:**
- `docs/papers/fetch_all_cited_papers.sh` — downloads the full bibliography. Two traps it handles:
  pre-2007 papers are served under `/pdf/astro-ph/<id>` (the bare form returns a JS-gated HTML
  page, not a PDF), and it asserts it landed in the project root, because an off-by-one in an
  earlier version wrote PDFs into a **sibling directory** while still printing `[ok]`.
- `scripts/make_kb_summaries.py` — writes the summaries. The **title and author list come from the
  paper's own verified reference entry**; the abstract and the key numbers are extracted from the
  local PDF with `pdftotext`. **Nothing is invented**: every number in a summary is re-derivable by
  re-running the extraction.

---

## 8. A note on a mistake I made

My first attempt at the "Yang+ 2024" tagging mislabelled the body/appendix split and **duplicated
the entire file** (1178 insertions, four `## References` sections). I caught it by checking
`git diff --stat` and the structural heading count, restored from git, and redid every edit using
line indices only. The lesson is recorded: after any bulk text edit, verify the diff size and the
count of structural landmarks before writing.

---

## 9. Zotero — revisited, verdict unchanged

**Tier 3: do not adopt.** The falsifiable claim behind that verdict — *"the gap is metadata
retrieval, not library management"* — was **tested and held**. This round is the test:

- **42 of 42** slots filled with a stdlib-only resolver and a 590-line script. No app, no account,
  no API key, no new MCP surface.
- The resolver and the manual verification caught **eight citation defects**, including two
  fabrications. A Zotero import would have taken **all eight silently**, because its import path
  trusts the metadata you hand it. The failure mode here was a wrong *attribution*, not a missing
  record — and a reference manager does not check attributions.
- Three structural arguments against Zotero are unaffected: it needs a desktop app plus a cloud
  account plus an API key; the KB's extracted-number content has no Zotero equivalent; and this
  host already carries nine MCP surfaces, most of them dormant.

**What would change the verdict:** a need for citation-graph functionality (who-cites-whom,
co-citation counts) — which neither Zotero nor this resolver does well, and which this project does
not currently have.

---

## 10. The full reference list (42 slots, all with a local PDF)

| Slot | Authors | Title | Venue |
|---|---|---|---|
| `1` | M. Kaplinghat, S. Tulin, H.-B. Yu | Dark Matter Halos as Particle Colliders: Un... | Phys. Rev. Lett. 116, 041302 (2016). arXiv:1508.0... |
| `1a` | A. Benítez-Llambay, R. Dutta, M. Fu... | Examining the Nature of the Starless Dark M... | Astrophys. J. 973, 61 (2024). arXiv:2406.18643. (... |
| `2` | K. A. Oman, J. F. Navarro, A. Fatta... | The unexpected diversity of dwarf galaxy ro... | Mon. Not. R. Astron. Soc. 452, 3650-3665 (2015). ... |
| `3` | M. Boylan-Kolchin, J. S. Bullock, M... | Too big to fail? The puzzling darkness of m... | Mon. Not. R. Astron. Soc.: Lett. 415, L40-L44 (20... |
| `4` | S. W. Randall, M. Markevitch, D. Cl... | Constraints on the Self-Interaction Cross S... | Astrophys. J. 679, 1173 (2008); doi:10.1086/58785... |
| `5` | J. L. Feng, M. Kaplinghat, H.-B. Yu | Sommerfeld Enhancements for Thermal Relic D... | Phys. Rev. D 82, 083525 (2010); arXiv:1005.4678. |
| `6` | S. Tulin, H.-B. Yu, K. M. Zurek | Resonant Dark Forces and Small-Scale Structure | Phys. Rev. Lett. 110, 111301 (2013); arXiv:1302.3... |
| `7` | X. Chu, C. Garcia-Cely, H. Murayama | Velocity Dependence from Resonant Self-Inte... | Phys. Rev. Lett. 122, 071103 (2019); arXiv:1810.0... |
| `8` | M. Duerr, K. Schmidt-Hoberg, S. Wild | Self-interacting dark matter with a stable ... | J. Cosmol. Astropart. Phys. 09 (2018) 033; arXiv:... |
| `9` | S. Girmohanta, R. Shrock | Cross Section Calculations in Theories of S... | Phys. Rev. D 106, 063013 (2022); arXiv:2206.14395. |
| `10` | S. Girmohanta, R. Shrock | Fitting a Self-Interacting Dark Matter Mode... | Phys. Rev. D 107, 063006 (2023); arXiv:2210.01132. |
| `13` | D. Yang, H.-B. Yu | Self-interacting dark matter and small-scal... | Phys. Rev. D 104, 103031 (2021); arXiv:2102.02375. |
| `14` | F. Lelli, S. S. McGaugh, J. M. Scho... | SPARC: Mass Models for 175 Disk Galaxies wi... | Astron. J. 152, 157 (2016); arXiv:1606.09251; doi... |
| `15a` | R. Zhou, M. Zhu, Y. Yang et al. | FAST Reveals New Evidence for M94 as a Merger | Astrophys. J. 952, 130 (2023); Erratum 2024; arXi... |
| `15b` | A. Benítez-Llambay, R. Dutta, M. Fu... | Examining the Nature of the Starless Dark M... | Astrophys. J. 973, 61 (2024). arXiv:2406.18643. (... |
| `15c` | G. S. Anand, A. Benítez-Llambay, R.... | The First RELHIC? Cloud-9 is a Starless Gas... | Astrophys. J. Lett. 993, L55 (2025); doi:10.3847/... |
| `15d` | I. Trujillo, I. Ruiz Cejudo, S. Gue... | Ultra-Deep Imaging of the Starless Galaxy C... | Res. Notes Am. Astron. Soc. 10, 247 (2026); doi:1... |
| `15e` | M. Ohana, X. Zhang, H.-B. Yu | Cold Dark Matter and Self-Interacting Dark ... | arXiv:2608.04362 (2026). |
| `18` | S. Balberg, S. L. Shapiro, S. Inagaki | Self-Interacting Dark Matter Halos and the ... | Astrophys. J. 568, 475 (2002); arXiv:astro-ph/011... |
| `19` | M. S. Fischer, H.-B. Yu | The dark fate of ultra-faint dwarfs: Gravot... | arXiv:2603.04508 (2026); doi:10.1051/0004-6361/20... |
| `17` | S. Yang, F. Jiang, A. Benson, Y.-M.... | A quantitative comparison between velocity ... | Mon. Not. R. Astron. Soc. 533, 4007 (2024); arXiv... |
| `16` | S. Vegetti, L. V. E. Koopmans, A. B... | Detection of a dark substructure through gr... | Mon. Not. R. Astron. Soc. 408, 1969 (2010); arXiv... |
| `23` | H.-B. Yu | Three Birds with One Stone: Core-Collapsed ... | PRL 136, 141001 (2026); arXiv:2510.11006. |
| `25` | P. van Dokkum, R. Abraham, A. J. Ro... | Extensive Globular Cluster Systems Associat... | Astrophys. J. Lett. 844, L11 (2017); arXiv:1705.0... |
| `26a` | M. Mateo | Dwarf Galaxies of the Local Group | Annu. Rev. Astron. Astrophys. 36, 435 (1998); arX... |
| `27` | S. Ando, K. Hayashi, S. Horigome, M... | Stringent Constraints on Self-Interacting D... | arXiv:2503.13650 (2025). |
| `28` | X. Chu, C. Garcia-Cely, H. Murayama | Velocity Dependence from Resonant Self-Inte... | Phys. Rev. Lett. 122, 071103 (2019); arXiv:1810.0... |
| `30` | D. Yang, H.-B. Yu | Self-interacting dark matter and small-scal... | Phys. Rev. D 104, 103031 (2021); arXiv:2102.02375... |
| `42` | D. Yang, Y.-L. S. Tsai, Y.-Z. Fan | Diversifying halo structures in two-compone... | Phys. Rev. D 112, 083502 (2025); arXiv:2504.02303... |
| `43` | D. Yang, E. O. Nadler, H.-B. Yu, Y.... | A parametric model for self-interacting dar... | J. Cosmol. Astropart. Phys. 02 (2024) 032; arXiv:... |
| `45` | Y. Zhang | Self-interacting dark matter without direct... | Phys. Dark Univ. 15, 82-89 (2017). arXiv:1611.03492. |
| `49` | A. Engelhardt, F. Munshi, A. H. G. ... | MARVELously Dark: The Density Profile Evolu... | arXiv:2601.23264 (2026). |
| `50` | D. S. Akerib et al. (LUX-ZEPLIN Col... | Search for Dark Matter Particle Interaction... | arXiv:2609.02823 (2026). |
| `50c` | D. Yang, Y.-Z. Fan, S. Hou, Y.-L. S... | Self-Interacting Dark Matter with Mass Segr... | Sci. Bull. 71, 1349 (2026); arXiv:2506.14898. |
| `50d` | M. Kaplinghat, S. Tulin, H.-B. Yu | Dark Matter Halos as Particle Colliders: Un... | Phys. Rev. Lett. 116, 041302 (2016). arXiv:1508.0... |
| `51` | E. O. Nadler, D. Kong, D. Yang, H.-... | SIDM Concerto: Compilation and Data Release... | Astrophys. J. 991, 69 (2025). arXiv:2503.10748. |
| `52` | Z. Jia, F. Jiang, S. Li, R. Li, J. ... | An enhanced isothermal jeans approach to co... | Mon. Not. R. Astron. Soc. 549, stag969 (2026). ar... |
| `54` | M. Silverman, A. Hussein, A. Arora,... | Mergers Matter: Gravothermal Collapse in Dw... | arXiv:2606.02566 (2026). |
| `54c` | O. Sameie, H.-B. Yu, L. V. Sales, M... | Self-Interacting Dark Matter Subhalos in th... | Phys. Rev. Lett. 124, 141102 (2020). arXiv:1904.0... |
| `55a` | O. D. Elbert, J. S. Bullock, S. Gar... | Core formation in dwarf haloes with self-in... | Mon. Not. R. Astron. Soc. 453, 29-37 (2015). arXi... |
| `55b` | Y. Lei, L. Zhu, M. Yang, G. Despali... | Lower Central Dark Matter Densities in Near... | arXiv:2609.16740 (2026). |
| `55c` | Y.-C. Wang, Y. Peng, X. Yang, L. C.... | Massive Galaxy Halos Contain Less Inner Dar... | arXiv:2609.19132 (2026). |

---

## 11. Open items

1. **CG-3, CG-6, CG-8, CG-12** — the coverage-gap register rows, carried over from earlier rounds.
2. **No deliverable yet for this round** — the report PDF, ZIP and Telegram delivery come last, after
   the reference work settles.
