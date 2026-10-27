# Zotero Developer API — evaluation (Tier 3, parked 2026-10-26)

**Resource:** Zotero developer documentation — <https://www.zotero.org/support/dev/>
**Status:** evaluated, NOT adopted
**Tier:** 3 (park — do not adopt now)
**License:** docs are Zotero's; the relevant community tools carry their own licenses
(zot: see repo; zotero-mcp 54yyyu: MIT per third-party listings — verify before install)

## What was evaluated

A docx (user-supplied, Chinese) arguing that Zotero's developer docs (Web API,
HTTP Citing Protocol, CSL, MCP servers) would improve the SIDM project's
AI-assisted research pipeline. Evaluated against the project's ACTUAL literature
workflow, not against the doc's description of it.

## Why parked

The project **already has** a working literature infrastructure that covers most of
what Zotero would add, and the remaining gap is NOT a tooling gap:

| Zotero offers | Project already has | Gap? |
|---|---|---|
| Programmatic metadata retrieval | `docs/papers/` KB — 11 verified `.md`+`.pdf` pairs, 23 `to_verify` entries, each with a per-paper extraction (key findings, key numbers, "how v19.2-F uses this paper") | **No** — and richer (Zotero stores metadata, not extracted numbers) |
| Citation provenance auditing | `scripts/audit_citation_provenance.py` (gate layer) + `docs/V19_2_F_REFERENCE_DATA_REGISTRY.md` (26 arXiv ids, verification status) | **No** |
| Reproducible paper download | `docs/papers/download_papers.sh` (idempotent, re-download from arXiv) | **No** |
| Formatted bibliography for submission | **32 `[NEEDS CITATION]` entries** still to fill — this IS the real gap | **Yes, but** see below |
| AI/LLM integration | `scholarkg` MCP (installed, `enabled: false`) + `arxiv` skill + 9 MCP servers already | **No** — and adding a 10th dormant MCP repeats the unused-inventory problem |

### The actual gap is metadata retrieval, not library management

The 32 unfilled reference entries need author / title / journal / volume / page / year
/ arXiv id. That is retrievable **without Zotero** — verified live 2026-10-26:

- `https://export.arxiv.org/api/query?id_list=<ids>` → authors, title, published date,
  DOI, and `arxiv:journal_ref` (e.g. `1904.07872` → `Phys. Rev. Lett. 124, 141102 (2020)`)
- `https://api.crossref.org/works/<doi>` → journal, volume, page, year, authors
  (e.g. `10.1103/physrevd.111.035005` → Physical Review D vol 111)

**Zotero would add a GUI, a sync account, a local desktop app, and an API-key
lifecycle — to do what two free HTTP endpoints already do.** The doc's own "CONCERNING"
note about API keys and pagination applies more to Zotero's Web API than to
arXiv/Crossref.

### Cost of adopting anyway

- Zotero desktop app is **not installed** on this host (verified: no `~/Zotero`, no
  Program Files entry) — so every MCP/CLI route needs it installed and running.
- The Web API needs a **cloud account + API key** (a credential to manage and protect).
- `zotero-mcp` (54yyyu, 5.6k stars) requires either the Zotero desktop app's Local API
  or a cloud key; it is a **new permanent MCP surface** on a host that already has 9.
- Migration: 41 paper references + 34 KB entries would need importing, and the KB's
  *extracted-number* content has no Zotero equivalent — it would have to be re-entered
  or kept in parallel.


## REVISIT 2026-10-27 — the prediction was tested, and it held

The Tier-3 verdict rested on one falsifiable claim: *the real gap is metadata retrieval,
and that is solvable with zero new dependencies.* That claim has now been tested end-to-end.

**`scripts/resolve_references.py`** (stdlib `urllib` only — no pip install, no API key, no
account, no 10th MCP surface) resolved **39 of the paper's 41 reference slots** against
arXiv + Crossref, and in doing so:

- **Caught two fabricated citations** that no library manager would have flagged, because
  both DO exist in a bibliographic index — they are simply attributed to the wrong people.
  `[10]`'s DOI resolves to a paper by *different authors*; `[9]` names an author (*Kuranchi*)
  who appears in **zero** author records in arXiv, InspireHEP, Crossref, Semantic Scholar and
  OpenAlex. Zotero would have imported both silently, because its import path trusts the
  metadata you hand it — the failure mode here is a wrong *attribution*, not a missing record.
- **Caught six more body-level attribution errors** that no reference-list tool can see,
  because the error is in the *prose*, not the entry: `[5]`'s venue pointed at a different
  Feng-Kaplinghat-Yu paper; `[7]` credited the wrong Chu paper; `[50c]` credited the wrong
  author set; `[55a]`'s 6th author was wrong; `[13]`/`[30]`'s year was wrong.
- **Rejected 8 plausible-looking wrong matches** that a looser tool would have accepted —
  including a *Physics World* news item for an ApJ paper, a *drug-development book* for a
  dark-matter paper, and an *optical-fibre traffic-sensing paper* for a dark-matter paper.

**What this changes about the Zotero decision: nothing, but it makes the reasoning
falsifiable rather than rhetorical.** The three strongest arguments against adopting Zotero
were all *structural*, and none of them is affected:

| Argument | Status after the test |
|---|---|
| The gap is metadata retrieval, not library management | **Confirmed** — 39/41 slots filled with zero new dependencies. A library manager was never the bottleneck. |
| Zotero needs a desktop app + cloud account + API key | Unchanged — none of that was needed, and none of it would have caught a mis-attribution. |
| The KB's extracted-number content has no Zotero equivalent | Unchanged — and now more clearly so: the resolver found errors that live *between* the paper and the reference, which is exactly the layer a metadata store does not model. |

**One honest caveat.** The resolver needed three rounds of gate hardening, each found by
mutation-testing it against a record that had already fooled it. A tool that has to be
hardened this much is not obviously "safer than Zotero" — it is *different*. The argument for
the resolver is not that it is more reliable; it is that its failure modes are **visible and
auditable** (every verdict is recorded with its evidence in
`docs/papers/to_verify/resolved_reference_candidates.json`) rather than silent. A Zotero
import that mis-attributes a paper leaves no trace at all.

**Recommendation unchanged: Tier 3, do not adopt.** Re-open only if the project needs
*citation-graph* functionality (which-cites-which, co-citation counts) — a problem neither
Zotero nor this resolver solves well, and a problem the project does not currently have.

## Claims in the source doc that did NOT check out

1. **`zot item export KEY1 KEY2 --as bibliography --style nature`** — no such command.
   `zot` (sylvainHellin/zot, R CLI) exposes `zot export <key>...` with
   `--format bibtex|ris|csljson`; it has **no** `item` subcommand and **no** `--as`/`--style`
   flags. The doc conflated `zot` with `zotero-cli` (jianghao-zhang/zotero-cli, Rust),
   which is a different tool with different subcommands.
2. **`zotLocalItems()` / `zotGetAll()`** — these are R package `zot` functions, correct
   as quoted but only if R is the target language. The project is Python + Julia.
3. **The example script `v19.2_f_priority1_resonance_helpers.py`** — the doc cites it as
   evidence of the project's style; it does exist, but at
   `v0.3-prelim/code/v19.2_f_priority1_resonance_helpers.py` (not at repo root).
4. **"PRD or JCAP"** — the paper's stated submission target is **Physics of the Dark
   Universe or JCAP** (paper L31). PRD is plausible but not what the paper says.

The document's *directional* advice is sound (script the citation pipeline); its
*specific* commands are not all real.

## Side-finding: paper reference [10] does not resolve

Found while verifying the reference inventory. **Not a Zotero problem — a paper problem.**

Paper L2015 reads:

> `[10] S. Girmohanta, Y. Yasuoka, Phys. Rev. D 111, 035005 (2025).`

Crossref resolves `10.1103/physrevd.111.035005` to a **different paper**:
*"Theoretical bounds on dark Higgs mass in a self-interacting dark matter model with
U(1)′"*, **Li, Yang, Zhang, Zhu** — not Girmohanta & Yasuoka.

And no Girmohanta & Yasuoka co-authored paper exists:
- arXiv full-text search `all:Girmohanta AND all:Yasuoka` → **0 entries**
- Crossref author-pair search → no PRD paper with both authors
- arXiv's own Girmohanta listing (20 most recent, 2022-2026) → **no Yasuoka co-author**;
  his SIDM papers are with **Shrock** (PRD 106, 063013 (2022); PRD 107, 063006 (2023))

This is the same shape as the project's earlier citation-drift bugs (v40.4 cited
arXiv:2305.16176 instead of 2305.05067). Reference [10] is cited in the body twice —
L38 ("geometric mass-ladder constructions (Hong, Kuranchi & Perez 2020 [9],
Girmohanta & Yasuoka 2025 [10])") and L90 ("The Girmohanta-Yasuoka 2025 [10] dark-photon
model is structurally similar but uses a different UV-completion story").

**Status: needs a decision.** Either the intended paper is a Girmohanta & Shrock SIDM
paper (both exist), or the reference is fabricated and must be cut. It was already
flagged in `v0.3-prelim/docs/AUDIT_REFERENCES.md` ("Concern: Authors may not exist;
PRD 111, 035005 should be checked against PRD table of contents") — that check was
never completed. **This is a candidate use for exactly the API path above.**

## Re-evaluation triggers

Revisit if ANY of these become true:
- The 32 `[NEEDS CITATION]` entries stop being fillable from arXiv + Crossref alone
  (e.g. a reference with no DOI, no arXiv id, and no ADS entry).
- The project needs **formatted** bibliography output (a `.bib` or CSL-JSON file the
  journal's submission system accepts) — Zotero/CSL would then earn its keep, and the
  cheapest route is `zot export --format csljson` or a 20-line CSL-JSON writer, not a
  desktop app.
- The user decides to run Zotero desktop locally and wants AI access to it. Then
  `zotero-mcp` (54yyyu) is the well-maintained option — MIT, 5.6k stars — but it is a
  **new MCP surface requiring explicit approval**, and the `scholarkg` MCP should be
  enabled/evaluated first (it is already installed and disabled).

## Cheapest path that gets 90% of the value (no new dependency)

A script that reads the paper's `[N]` citation slots, resolves each via
arXiv → Crossref → (fallback) Semantic Scholar, and writes a candidate reference
entry with its verification status into `docs/papers/to_verify/` + the registry.
Stdlib + `urllib` only — no install, no account, no GUI. That is the same shape as
the existing `download_papers.sh`.
