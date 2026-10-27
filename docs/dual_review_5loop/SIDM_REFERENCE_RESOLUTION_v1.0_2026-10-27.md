# SIDM v19.2-F — Reference Resolution Round

**Date:** 2026-10-27
**Branch:** `wip/v19.2-F-init`
**Commit:** `6336649` (pushed)
**Scope:** the 38 blank `[NEEDS CITATION]` slots in `v0.3-prelim/docs/PAPER_V1_DRAFT.md`

---

## 1. Headline

**39 of 41 reference slots now carry a publisher-verified entry.** Two entries that were
**fabricated** were found, re-pointed to real papers, and their two load-bearing body
sentences rewritten. Six further body-level attribution errors were found and corrected.
Two slots remain unresolved and are tracked as open items — deliberately **not** filled with
plausible-looking substitutes.

| | Before | After |
|---|---|---|
| Slots with a verified entry | 13 (of 41) | **39** (of 41) |
| Fabricated citations | 2 undetected | **0** |
| Body-level attribution errors | 6 undetected | **0** |
| Unresolved slots recorded as open items | 0 | 2 (`[11]`, `[12]`) |

---

## 2. The two fabricated citations

### [10] — attributed to a co-author who does not exist

The draft read: `[10] S. Girmohanta, Y. Yasuoka, Phys. Rev. D 111, 035005 (2025).`

- The implied DOI `10.1103/physrevd.111.035005` **resolves** — to *Li, Yang, Zhang & Zhu*,
  "Theoretical bounds on dark Higgs mass in a self-interacting dark matter model with U(1)'".
  A DOI that resolves is not a citation that is correct.
- No Girmohanta–Yasuoka co-authored paper exists in arXiv, Crossref, InspireHEP, Semantic
  Scholar or OpenAlex.
- **Now:** Girmohanta & Shrock, PRD 107, 063006 (2023), arXiv:2210.01132.

### [9] — an author who does not exist in any physics index

The draft read: `Hong, Kuranchi & Perez 2020` (PRD 102).

- The surname **Kuranchi** returns **zero** author records in arXiv, InspireHEP, Crossref,
  Semantic Scholar and OpenAlex.
- The real paper is Hong, **Kurup** & **Perelstein**, PRD 101, 095037 — a *conformal freeze-in
  production* paper, which cannot support a velocity-dependent-cross-section claim.
- The audit's recorded venue (PRD 102, 075025) is *Protasov et al.*, "Theoretical analysis of
  antineutron-nucleus data needed for antineutron mirrors" — unrelated to dark matter.
- **Now:** Girmohanta & Shrock, PRD 106, 063013 (2022), arXiv:2206.14395.

> **On the "Kuranchi = Shalini Kuranchi-Bendin" hypothesis** (raised during this round):
> she is a real researcher, and her work on fuzzy-dark-matter spherical collapse is real — but
> she has no author record in any physics index, and her work cannot support this claim. The
> hypothesis was tested against five independent indexes and ruled out.

---

## 3. Both load-bearing body sentences were rewritten

The citations were not merely relabelled; the claims were re-checked against the papers.

**L38** — the velocity-dependence mechanism list:

> before: `...or geometric mass-ladder constructions (Hong, Kuranchi & Perez 2020 [9]; Girmohanta & Yasuoka 2025 [10]).`
> after: `...or mass-dependent u-channel constructions (Girmohanta & Shrock 2022 [9]; Girmohanta & Shrock 2023 [10]).`

Verified against the arXiv full text of 2206.14395: the u-channel amplitude carries explicit
`m_chi^4` terms (Eq. 29, scalar mediator; Eq. 110, vector mediator), and the abstract
states the authors compare results "with the inclusion of both t-channel and u-channel
exchanges". "Mass-dependent u-channel" is therefore supported; "geometric mass-ladder" was
not supported by anything.

**L90** — the closest-existing-work comparison:

> before: `The Girmohanta-Yasuoka 2025 [10] dark-photon model is structurally similar but uses a different UV-completion story.`
> after: `The Girmohanta & Shrock 2023 [10] dark-photon model is structurally similar but uses a different UV-completion story.`

PRD 107, 063006 is the paper that *uses* the u-channel-inclusive cross sections over
v ~ 20 km/s to >~ 10^3 km/s, and it is the dark-photon (vector mediator) model the sentence
describes.

---

## 4. Six further body-level attribution errors found and fixed

These live in the **prose**, not the reference list — no reference-list tool can see them.

| Slot | The error | The truth | Fixed |
|---|---|---|---|
| `[5]` | venue PRL 104, 151301 | That DOI is *Halo-Shape and Relic-Density Exclusions of Sommerfeld-Enhanced DM* — a **different** FKY paper. The Yukawa-suppression source the body cites is FKY, PRD 82, 083525 (2010), arXiv:1005.4678 | ✓ |
| `[7]` | credited "Chu, Hambye & Tytgat 2018" | The paper cited is Chu, **Garcia-Cely & Murayama** 2019, PRL 122, 071103 | ✓ (2 body sites) |
| `[8]` | credited "Duerr et al. 2021" | Duerr, Schmidt-Hoberg & Wild, JCAP 09 (2018) 033 | ✓ |
| `[50c]` | credited "Mace, Yang, Zeng+ 2026" | arXiv:2506.14898 is **Yang, Fan, Hou & Tsai**, Sci. Bull. 71, 1349. The SIDM2v model itself is Mace+ 2025 (arXiv:2504.13004), which the body already states correctly elsewhere | ✓ |
| `[55a]` | 6th author "Boylan-Kolchin" | The real 6th author is **Annika H. G. Peter** | ✓ |
| `[13]`/`[30]` | year "Yang & Yu 2022" | **Yang & Yu 2021**, PRD 104, 103031 (2021), arXiv:2102.02375 | ✓ |

---

## 5. Duplicate slots — three pairs, cross-labelled

| Pair | Paper | Why both slots survive |
|---|---|---|
| `[1]` / `[50d]` | Kaplinghat, Tulin & Yu, PRL 116, 041302 | cited at different body sentences (L36, L807) |
| `[1a]` / `[15b]` | Benítez-Llambay+ 2024, ApJ 973, 61 | cited at different body sentences (L807, L845) |
| `[7]` / `[28]` | Chu, Garcia-Cely & Murayama, PRL 122, 071103 | cited at different body sentences (L38, L1737) |

Each entry now states which slot it duplicates, so a reader cannot mistake three pairs for
six papers. Merging them would require renumbering, which is a larger change than the
defect warrants.

---

## 6. The resolver: `scripts/resolve_references.py`

**Standard library only.** `urllib` + `xml.etree` + `json`. No pip install, no API key, no
account, no new MCP surface. It queries `export.arxiv.org` and `api.crossref.org`, and it
**refuses to invent** a candidate that fails the agreement check.

**Three gate bugs, each found by re-running the resolver against a record that had already
fooled it:**

| Bug | Record that fooled it | Gate now |
|---|---|---|
| A title match could override a venue mismatch | A *Physics World* news item titled "A map of dark matter" (vol 21, p 5) was RESOLVED for the ApJ 679 slot | A venue mismatch is **fatal** whenever the seed names a journal |
| An author mismatch did not block RESOLVED | "Turner 2021, Atomic Dark Matter" → Ryan, "Black Holes From Atomic Dark Matter" (title overlap 1.00, venue YES) | Missing expected surnames ⇒ **CONFLICT**, always |
| Surname+year counted as an identification | Slot "Wang 2026, no title" → an optical-fibre **traffic-sensing** paper with seven authors named Wang | A seed with neither title nor venue can only be CONFLICT |

Three further refinements: surname comparison is **diacritic-insensitive**
(`Garcia-Cely` = `García-Cély`, `Onorbe` = `Oñorbe`); the Crossref query carries
**author + journal + volume + page** rather than a bare title (the title-only query is what
returns the proceedings and the news item); and every verdict is recorded with its evidence
in `docs/papers/to_verify/resolved_reference_candidates.json`.

**A caveat worth stating:** the resolver needed three rounds of hardening. It is not
"obviously safer than a library manager" — it is *different*. The argument for it is that its
failure modes are **visible and auditable** rather than silent.

---

## 7. The two unresolved slots

| Slot | Cited as | Status |
|---|---|---|
| `[11]` | "Yang & Yu 2023, single-breathing-mode mediator with one resonance" | DOI `10.1103/PhysRevD.108.043040` does not resolve in Crossref; no Yang–Yu 2023 paper with this title found in arXiv, InspireHEP, Crossref, Semantic Scholar or OpenAlex |
| `[12]` | "Turner et al. 2021, atomic-DM transitions" | PRD 104, 013005 is *"Revisiting semileptonic decays of ..."*; the real atomic-DM paper is Kaplan, Krnjaic, Rehermann & Wells, JCAP 10 (2010) 021 — a different author set |

Both remain `[NEEDS CITATION]` and are recorded as open items with their evidence. They are
**not** filled with a topically-adjacent substitute, because that is the exact failure mode
that produced the two fabrications in the first place.

---

## 8. Verified reference list (39 of 41)

| Slot | Authors | Title | Venue |
|---|---|---|---|
| `[1]` |  | M. Kaplinghat, S. Tulin, H.-B. Yu, "Dark Ma... |  |
| `[1a]` |  | A. Benítez-Llambay, R. Dutta, M. Fumagalli,... |  |
| `[2]` |  | K. A. Oman, J. F. Navarro, A. Fattahi, C. S... |  |
| `[3]` |  | M. Boylan-Kolchin, J. S. Bullock, M. Kaplin... |  |
| `[4]` |  | S. W. Randall, M. Markevitch, D. Clowe, A. ... |  |
| `[5]` |  | J. L. Feng, M. Kaplinghat, H.-B. Yu, "Somme... |  |
| `[6]` |  | S. Tulin, H.-B. Yu, K. M. Zurek, "Resonant ... |  |
| `[7]` |  | X. Chu, C. Garcia-Cely, H. Murayama, "Veloc... |  |
| `[8]` |  | M. Duerr, K. Schmidt-Hoberg, S. Wild, "Self... |  |
| `[9]` |  | S. Girmohanta, R. Shrock, "Cross Section Ca... |  |
| `[10]` |  | S. Girmohanta, R. Shrock, "Fitting a Self-I... |  |
| `[11]` | **UNRESOLVED** | — |
| `[12]` | **UNRESOLVED** | — |
| `[13]` |  | D. Yang, H.-B. Yu, "Self-interacting dark m... |  |
| `[14]` |  | F. Lelli, S. S. McGaugh, J. M. Schombert, "... |  |
| `[15a]` |  | R. Zhou, M. Zhu, Y. Yang et al., "FAST Reve... |  |
| `[15b]` |  | A. Benítez-Llambay, R. Dutta, M. Fumagalli,... |  |
| `[15c]` |  | G. S. Anand, A. Benítez-Llambay, R. Beaton ... |  |
| `[15d]` |  | I. Trujillo, I. Ruiz Cejudo, S. Guerra Aren... |  |
| `[15e]` |  | M. Ohana, X. Zhang, H.-B. Yu, "Cold Dark Ma... |  |
| `[16]` |  | S. Vegetti, O. Czoske, L. V. E. Koopmans, "... |  |
| `[23]` |  | H.-B. Yu, "Three Birds with One Stone: Core... |  |
| `[25]` |  | P. van Dokkum, R. Abraham, A. J. Romanowsky... |  |
| `[26a]` |  | M. Mateo, "Dwarf Galaxies of the Local Grou... |  |
| `[27]` |  | S. Ando, K. Hayashi, S. Horigome, M. Ibe, S... |  |
| `[28]` |  | X. Chu, C. Garcia-Cely, H. Murayama, "Veloc... |  |
| `[30]` |  | D. Yang, H.-B. Yu, "Self-interacting dark m... |  |
| `[42]` |  | D. Yang, Y.-L. S. Tsai, Y.-Z. Fan, "Diversi... |  |
| `[43]` |  | D. Yang, E. O. Nadler, H.-B. Yu, Y.-M. Zhon... |  |
| `[45]` |  | Y. Zhang, "Self-interacting dark matter wit... |  |
| `[49]` |  | A. Engelhardt, F. Munshi, A. H. G. Peter, E... |  |
| `[50]` |  | D. S. Akerib et al. (LUX-ZEPLIN Collaborati... |  |
| `[50c]` |  | D. Yang, Y.-Z. Fan, S. Hou, Y.-L. S. Tsai, ... |  |
| `[50d]` |  | M. Kaplinghat, S. Tulin, H.-B. Yu, "Dark Ma... |  |
| `[51]` |  | E. O. Nadler, D. Kong, D. Yang, H.-B. Yu, "... |  |
| `[52]` |  | Z. Jia, F. Jiang, S. Li, R. Li, J. Wang, L.... |  |
| `[54]` |  | M. Silverman, A. Hussein, A. Arora, M. Lisa... |  |
| `[54c]` |  | O. Sameie, H.-B. Yu, L. V. Sales, M. Vogels... |  |
| `[55a]` |  | O. D. Elbert, J. S. Bullock, S. Garrison-Ki... |  |
| `[55b]` |  | Y. Lei, L. Zhu, M. Yang, G. Despali, Z. Zhe... |  |
| `[55c]` |  | Y.-C. Wang, Y. Peng, X. Yang, L. C. Ho, D. ... |  |

---

## 9. Zotero re-examined (the "revisit zoterotopic and discuss" item)

**Verdict: Tier 3 — do not adopt. Unchanged, but now empirically grounded rather than
rhetorical.**

The original evaluation rested on one falsifiable claim: *the gap is metadata retrieval,
not library management, and that is solvable with zero new dependencies.* This round tested
it. The claim holds:

- **39 of 41 slots filled** with stdlib-only code — no app, no account, no key, no MCP.
- The resolver caught **two fabricated citations and six body-attribution errors**. A Zotero
  import would have taken all eight silently, because its import path trusts the metadata
  you hand it. The failure mode here is a wrong *attribution*, not a missing record.
- Three of the strongest arguments against Zotero are structural and unaffected: it needs a
  desktop app + cloud account + API key; the KB's extracted-number content has no Zotero
  equivalent; and adding a 10th MCP surface to a host with 9 dormant ones compounds an
  existing inventory problem.

**What would change the verdict:** a need for *citation-graph* functionality (which-cites-
which, co-citation counts) — a problem neither Zotero nor this resolver solves well, and a
problem this project does not currently have.

---

## 10. Files changed

| File | Change |
|---|---|
| `v0.3-prelim/docs/PAPER_V1_DRAFT.md` | 27 reference entries written; 2 re-pointed; 8 body sentences corrected; 3 duplicate pairs cross-labelled; status note rewritten |
| `v0.3-prelim/docs/AUDIT_REFERENCES.md` | 15 tier-table rows corrected; two adjudication records added (fabricated [9]/[10], resolver-gate bugs) |
| `scripts/resolve_references.py` | **new** — stdlib-only arXiv + Crossref resolver with three hardened gates |
| `docs/papers/to_verify/resolved_reference_candidates.json` | **new** — machine-readable candidate list with per-slot evidence |
| `docs/papers/to_verify/resolved_reference_candidates.md` | **new** — human-readable summary |
| `docs/papers/to_verify/zotero_developer_api.md` | Zotero revisit section added |
| `docs/V19_2_F_REFERENCE_DATA_REGISTRY.md` | §7.7 adjudication + §7.8 round record |

---

## 11. Open items

1. `[11]` and `[12]` need the author's own citation — the two slots where no candidate
   passed the agreement check.
2. The three duplicate slot pairs ([1]/[50d], [1a]/[15b], [7]/[28]) could be merged at
   final formatting time if renumbering is acceptable.
