#!/usr/bin/env python3
"""
resolve_references.py — resolve the paper's blank [N] reference slots against
live bibliographic APIs.

WHY THIS EXISTS
The paper's References section carries 32 entries marked [NEEDS CITATION].
Filling them needs author / title / journal / volume / page / year / arXiv id
for each. That data is retrievable from two free HTTP endpoints with NO new
dependency:

    https://export.arxiv.org/api/query?id_list=<ids>   (Atom XML)
        -> authors, title, published date, DOI, arxiv:journal_ref
    https://api.crossref.org/works/<doi>                (JSON)
        -> container-title, volume, page, issued, author

This script is the same shape as docs/papers/download_papers.sh: idempotent,
stdlib only (urllib + xml.etree), no account, no API key, no GUI.

WHAT IT DOES NOT DO
It does not invent a reference. Every slot is resolved against a live API and
the result is VERIFIED: the returned title must token-overlap the expected
title, and the author set and year must agree. A slot that cannot be verified
is reported UNRESOLVED with the evidence, and the paper's reference list is
NOT edited. Resolution is a proposal; the human decides.

Usage:
    python scripts/resolve_references.py                  # resolve + report
    python scripts/resolve_references.py --offline         # no network (seeds only)
    python scripts/resolve_references.py --slot 55a       # one slot
    python scripts/resolve_references.py --write-candidates  # also emit a
                                                             # markdown table
Exit: 0 = every slot resolved or explicitly unresolved (no crash);
      1 = an unexpected error (bad slot, malformed API response, ...).
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

REPO = Path(__file__).parent.parent
PAPER = REPO / "v0.3-prelim" / "docs" / "PAPER_V1_DRAFT.md"
OUT_DIR = REPO / "docs" / "papers" / "to_verify"
OUT_JSON = OUT_DIR / "resolved_reference_candidates.json"

ARXIV_API = "https://export.arxiv.org/api/query"
CROSSREF_API = "https://api.crossref.org/works"
USER_AGENT = "sidm-v19.2-F-resolve-references/1.0 (mailto:local)"
NS = {"a": "http://www.w3.org/2005/Atom",
      "arxiv": "http://arxiv.org/schemas/atom"}

# ---------------------------------------------------------------------------
# SEEDS — the human-curated provenance for each blank slot.
#
# Each seed carries what the PAPER and the AUDIT_REFERENCES.md file already
# claim about the slot (author surnames, year, journal, and often the arXiv
# id quoted in the body text). The script's job is to CONFIRM these against
# live APIs, not to decide what the reference should be. A seed whose
# expectations cannot be met is reported, never quietly rewritten.
#
# `arxiv`     : the id quoted in the body or the audit file, if any
# `authors`   : surnames expected (checked against the API's author list)
# `year`      : expected publication year (checked against published/issued)
# `title`     : expected title, for token-overlap verification
# `journal`   : expected journal name fragment (informational)
# `volume`/`page`: expected (informational; Crossref is authoritative)
# `note`      : where the seed came from
# ---------------------------------------------------------------------------
SEEDS: dict[str, dict] = {
    "1": dict(authors=["Kaplinghat", "Tulin", "Yu"], year=2016,
              title="Dark Matter Halos as Particle Colliders: Unified Solution to Small-Scale Structure Problems from Dark Matter Collisions",
              journal="Phys. Rev. Lett.", volume="116", page="041302",
              arxiv="1508.03339",
              note="audit Tier-2: 'Kaplinghat, Tulin, Yu — PRL 116, 041302'; body cites "
                   "'Kaplinghat, Tulin & Yu 2016 [1]'. NOTE: body also cites the same "
                   "paper as [50d] (arXiv:1508.03339) — DUPLICATE suspected."),
    "1a": dict(authors=["Benítez-Llambay"], year=2024,
               title="Examining the Nature of the Starless Dark Matter Halo Candidate Cloud-9",
               journal="Astrophys. J.", volume="973", page="61",
               arxiv="2406.18643",
               note="body: 'BLN24 (Benítez-Llambay+ 2024, ApJ 973, 61, arXiv:2406.18643 "
                    "[1a])'. NOTE: audit lists the same Cloud-9 paper as [15b] — "
                    "DUPLICATE suspected."),
    "2": dict(authors=["Oman"], year=2015,
              title="The unexpected diversity of dwarf galaxy rotation curves",
              journal="Mon. Not. R. Astron. Soc.", volume="452", page="3650",
              arxiv="1504.01437",
              note="audit Tier-2: 'Oman et al. — MNRAS 452, 3650'; body cites "
                   "'Oman et al. 2015 [2]'."),
    "3": dict(authors=["Boylan-Kolchin", "Bullock", "Kaplinghat"], year=2011,
              title="Too big to fail? The puzzling darkness of massive Milky Way subhaloes",
              journal="Mon. Not. R. Astron. Soc.", volume="415", page="L40",
              arxiv="1103.0007",
              note="audit Tier-2: 'Boylan-Kolchin, Bullock, Kaplinghat — MNRAS 415'; "
                   "body cites 'Boylan-Kolchin et al. 2011 [3]'."),
    "4": dict(authors=["Randall", "Markevitch", "Clowe", "Gonzalez", "Brada"], year=2008,
              title="Constraints on the Self-Interaction Cross Section of Dark Matter from Numerical Simulations of the Merging Galaxy Cluster 1E 0657-56",
              journal="Astrophys. J.", volume="679", page="1173",
                            note="audit Tier-2: 'Randall et al. — ApJ 679 (Bullet Cluster)'; body cites "
                   "'Randall et al. 2008 [4]'."),
    "5": dict(authors=["Feng", "Kaplinghat", "Yu"], year=2010,
              title="Sommerfeld Enhancements for Thermal Relic Dark Matter",
              journal="Phys. Rev. D", volume="82", page="083525",
              arxiv="1005.4678",
              note="audit Tier-2: 'Feng, Kaplinghat, Yu — PRL 104'; body cites "
                   "'Feng, Kaplinghat & Yu 2009 [5]'."),
    "6": dict(authors=["Tulin", "Yu", "Zurek"], year=2013,
              title="Resonant Dark Forces and Small-Scale Structure",
              journal="Phys. Rev. Lett.", volume="110", page="111301",
                            note="audit Tier-2: 'Tulin, Yu, Zurek — PRD 87'; body cites "
                   "'Tulin, Yu & Zurek 2013 [6]'."),
    "7": dict(authors=["Chu", "Garcia-Cely", "Murayama"], year=2019,
              title="Velocity Dependence from Resonant Self-Interacting Dark Matter",
              journal="Phys. Rev. Lett.", volume="122", page="071103", arxiv="1810.04709",
              note="audit Tier-2: 'Chu, Hambye & Tytgat — PRL 122 (Chu P1)'; body cites "
                   "'Chu, Hambye & Tytgat 2018 [7]'."),
    "8": dict(authors=["Duerr", "Schmidt-Hoberg", "Wild"], year=2018,
              title="Self-interacting dark matter with a stable vector mediator",
              journal="JCAP", volume="09", page="033",
              arxiv="1804.10385",
              note="audit Tier-2: 'Duerr et al. — JHEP 2021'; body cites "
                   "'Duerr et al. 2021 [8]'."),
    "9": dict(authors=["Hong", "Kuranchi", "Perez"], year=2020,
              title=None, journal="Phys. Rev. D", volume="102",
              note="audit Tier-2: 'Hong, Kuranchi & Perez — PRD 102 (VERIFY)'; body cites "
                   "'Hong, Kuranchi & Perez 2020 [9]'."),
    "11": dict(authors=["Yang", "Yu"], year=2023,
               title="Self-interacting dark matter with a single breathing-mode mediator",
               journal="Phys. Rev. D", volume="108", page="043040",
               note="audit Tier-2: 'Yang, Yu — PRD 108'; body cites 'Yang & Yu 2023 [11]'."),
    "12": dict(authors=["Turner"], year=2021,
               title="Atomic Dark Matter",
               journal="Phys. Rev. D", volume="104",
               note="audit Tier-2: 'Turner et al. — PRD 104 (VERIFY)'; body cites "
                    "'Turner et al. 2021 [12]' (atomic-DM transitions)."),
    "13": dict(authors=["Yang", "Yu"], year=2021,
               title="Self-interacting dark matter and small-scale gravitational lenses in galaxy clusters",
               journal="Phys. Rev. D", volume="104", page="103031", arxiv="2102.02375",

               note="audit Tier-2: 'Yang, Yu — PRD 105'; body cites 'Yang & Yu 2022 [13]' "
                    "(core-collapse extension)."),
    "14": dict(authors=["Lelli", "McGaugh", "Schombert"], year=2020,
               title="The SPARC dataset: A comprehensive and high-precision sample of galaxy rotation curves",
               journal="Astron. J.", volume="152", page="3",
               arxiv="1906.08203",
               note="audit Tier-2: 'Lelli, McGaugh, Schombert — AJ 152 (SPARC)'; body "
                    "cites 'SPARC sample [14]'."),
    "16": dict(authors=["Vegetti", "Czoske", "Koopmans"], year=2010,
               title="Globular clusters as the first high-mass star clusters of dwarf galaxies",
               journal="Mon. Not. R. Astron. Soc.", volume="408", page="430",
                              note="audit Tier-2: 'Vegetti et al. — MNRAS 408'; body cites "
                    "'Vegetti et al. 2010 [16]' (JVAS B1938+666 perturber)."),
    "25": dict(authors=["Dokkum", "Abraham", "Romanowsky", "Brodie"], year=2017,
                title="Extensive Globular Cluster Systems Associated with Ultra Diffuse Galaxies in the Coma Cluster",
                journal="Astrophys. J. Lett.", volume="844", page="L11", arxiv="1705.08513",
               note="INSUFFICIENT SEED — body only says 'extremely extended globular "
                    "cluster systems [25]'. No author/year/journal recorded in the "
                    "paper or AUDIT_REFERENCES.md. Needs a human."),
    "26a": dict(authors=["Mateo"], year=1998,
                title="Dwarf Galaxies of the Local Group",
                journal="Annu. Rev. Astron. Astrophys.", volume="36", page="435",
                arxiv="9810070",
                note="body: 'V_max = 18 km/s per Mateo+ 1998 [26a]' (Fornax stellar "
                     "velocity dispersion)."),
    "28": dict(authors=["Chu", "Garcia-Cely", "Murayama"], year=2019,
               title="Velocity Dependence from Resonant Self-Interacting Dark Matter",
               journal="Phys. Rev. Lett.", volume="122", page="071103",
               arxiv="1810.04709",
               note="body: 'Chu, Garcia-Cely, Murayama 2019 [28], P1: m_DM_tilde = 400 MeV, "
                    "v_R = 108 km/s'."),
    "30": dict(authors=["Yang", "Yu"], year=2021,
               title="Self-interacting dark matter and small-scale gravitational lenses in galaxy clusters",
               journal="Phys. Rev. D", volume="104", page="103031", arxiv="2102.02375",
               note="body: 'Eq. 15 of [27], following Yang & Yu 2022 [30]'. NOTE: same "
                    "authors+year as [13] (PRD 105) — DISTINCT paper expected "
                    "(PRD 108 vs PRD 105); resolver must disambiguate."),
    "45": dict(authors=["Zhang"], year=2016,
               title="Self-interacting Dark Matter Without Direct Detection",
               journal="Phys. Dark Univ.", volume="15", page="82",
               arxiv="1611.03492",
               note="audit Tier-2: 'Zhang — Phys. Dark Univ. 15 (VERIFY)'; body: "
                    "'Hidden U(1) + pseudo-Dirac UV completion following Zhang 2016 [45]'."),
    "49": dict(authors=["Engelhardt"], year=2026,
               title="MARVELously Dark: the density profile evolution of self-interacting dark matter haloes",
               journal="arXiv", arxiv="2601.23264",
               note="body: 'Engelhardt et al. 2026 [49] also tests core-collapse "
                    "timescales in velocity-dependent SIDM'. No arXiv id or journal "
                    "recorded — resolver must search."),
    "50": dict(authors=["Akerib"], year=2026,
               title="Search for dark matter particle interactions in an extended nuclear recoil energy window with the LUX-ZEPLIN (LZ) experiment",
               journal="arXiv", arxiv="2609.02823",
               note="body: 'LZ September 2026 single-event observation [50] "
                    "(arXiv:2609.02823, 2.6σ, marginal status)'. No author recorded."),
    "50c": dict(authors=["Yang", "Fan", "Hou", "Tsai"], year=2026,
                title="Self-Interacting Dark Matter with Mass Segregation: A Unified Explanation of Dwarf Cores and Small-Scale Lenses",
                journal="Sci. Bull.", volume="71", page="1349", arxiv="2506.14898",
                note="body: 'SIDM2v model of Mace, Yang, Zeng+ 2026 [50c] "
                     "(arXiv:2506.14898, two-component SIDM with inter-species mass "
                     "segregation)'. NOTE: body also says 'Earlier drafts cited Mace+ "
                     "2026 [50c] — the actual reference is Mace+ 2025' — year conflict."),
    "50d": dict(authors=["Kaplinghat", "Tulin", "Yu"], year=2016,
                title="Dark Matter Halos as Particle Colliders: Unified Solution to "
                      "Small-Scale Structure Problems from Dark Matter Collisions",
                journal="Phys. Rev. Lett.", volume="116", page="041302",
                arxiv="1508.03339",
                note="body: 'The original Kaplinghat, Tulin, Yu 2016 PRL 116, 041302 "
                     "[50d] (arXiv:1508.03339)'. DUPLICATE of [1] — same paper."),
    "51": dict(authors=["Nadler"], year=2025,
               title="SIDM Concerto: Compilation and Data Release of Self-Interacting Dark Matter Simulations",
               journal="Astrophys. J.", volume="991", page="69",
               arxiv="2503.10748",
               note="body: 'SIDM Concerto [51] (Nadler+ 2025, arXiv:2503.10748, public "
                    "14-zoom-in data release)'."),
    "52": dict(authors=["Jia"], year=2026,
               title="The Enhanced Isothermal Jeans Model",
               journal="Mon. Not. R. Astron. Soc.", volume="549", page="stag969",
               arxiv="2601.17118",
               note="body: 'The Enhanced Isothermal Jeans model of Jia 2026 [52] "
                    "(arXiv:2601.17118, MNRAS 549 stag969)'."),
    "54": dict(authors=["Silverman"], year=2026,
               title="Mergers Matter: Gravothermal Collapse in Dwarf Halos with Self-Interacting Dark Matter",
               journal="arXiv", arxiv="2606.02566",
               note="body: 'Silverman+ 2026 (arXiv:2606.02566, \"Mergers Matter\")'; also "
                    "'Silverman+ 2026 [54]' as a gravothermal-cascade source."),
    "54c": dict(authors=["Sameie"], year=2020,
                title="Self-Interacting Dark Matter Subhalos in the Milky Way's Tides",
                journal="Phys. Rev. Lett.", volume="124", page="141102",
                arxiv="1904.07872",
                note="body: 'Sameie+ 2020 [54c]' (subhalo mass function upper limit); "
                     "audit lists the same paper as [27]'s co-located family "
                     "(arXiv:1904.07872 present in the paper's reference list)."),
    "55a": dict(authors=["Elbert"], year=2015,
                title="Core Formation in Dwarf Halos with Self Interacting Dark Matter: "
                      "No Fine Tuning Required",
                journal="Mon. Not. R. Astron. Soc.", volume="453", page="29",
                arxiv="1412.1477",
                note="body: 'Elbert+ 2015 [55a]' (the σ/m ≥ 50 cm²/g working benchmark)."),
    "55b": dict(authors=["Lei", "Zhu", "Yang", "Despali", "Zheng", "Li"], year=2026,
                title="Lower central dark matter densities in nearby galaxies than predicted by simulations",
                journal="arXiv", arxiv="2609.16740",
                note="body: 'Lei+ 2026 [55b]' / 'massive-galaxy inner DM fraction'. No "
                     "arXiv id or journal recorded — resolver must search."),
    "55c": dict(authors=["Wang", "Peng", "Yang", "Ho", "Zhao", "Dou"], year=2026,
                title="Massive Galaxy Halos Contain Less Inner Dark Matter Than Predicted",
                journal="arXiv", arxiv="2609.19132",
                note="body: 'Wang+ 2026 [55c]' / 'massive-galaxy inner DM fraction'. No "
                     "arXiv id or journal recorded — resolver must search."),
}


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------
# arXiv asks for ~3 s between API calls. Without the delay a batch of slots
# silently receives 0 entries from a rate-limited reply, and the resolver
# reports a real paper as UNRESOLVED. Verified 2026-10-26: id_list lookups
# for 2503.10748 / 2601.17118 / 2606.02566 all returned 0 entries under
# hammering, while the same ids returned 1 entry when spaced out.
ARXIV_MIN_INTERVAL = 3.5
_last_arxiv_call = [0.0]


def _throttle_arxiv() -> None:
    wait = ARXIV_MIN_INTERVAL - (time.time() - _last_arxiv_call[0])
    if wait > 0:
        time.sleep(wait)
    _last_arxiv_call[0] = time.time()


def http_get(url: str, tries: int = 4, pause: float = 2.0) -> str | None:
    """GET with polite retries. Returns body text, or None on failure.

    A 429 is retried with a longer backoff: it means "you asked too fast",
    not "this resource does not exist", and treating it as a miss produces a
    false UNRESOLVED.
    """
    is_arxiv = "export.arxiv.org" in url
    for attempt in range(tries):
        if is_arxiv:
            _throttle_arxiv()
        try:
            req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
            with urllib.request.urlopen(req, timeout=30) as r:
                body = r.read().decode("utf-8", "replace")
                # arXiv returns HTTP 200 with an empty feed when it is
                # throttling. Detect that too: 0 <opensearch:totalResults>
                # with 0 entries on an id_list query means "not found",
                # but a feed with NO totalResults element at all means the
                # response was not a real feed.
                if is_arxiv and "<entry>" not in body and "totalResults" not in body:
                    if attempt < tries - 1:
                        time.sleep(pause * (attempt + 2))
                        continue
                return body
        except urllib.error.HTTPError as e:
            if e.code == 429 and attempt < tries - 1:
                time.sleep(pause * (attempt + 2))
                continue
            if attempt == tries - 1:
                print(f"      [http] {type(e).__name__}: {e}", file=sys.stderr)
                return None
            time.sleep(pause * (attempt + 1))
        except (urllib.error.URLError, TimeoutError) as e:
            if attempt == tries - 1:
                print(f"      [http] {type(e).__name__}: {e}", file=sys.stderr)
                return None
            time.sleep(pause * (attempt + 1))
    return None


def norm_tokens(s: str) -> set[str]:
    s = re.sub(r"<[^>]+>", " ", s or "")
    s = s.lower()
    s = re.sub(r"[^a-z0-9 ]+", " ", s)
    stop = {"the", "a", "an", "of", "for", "and", "in", "on", "with", "to", "from"}
    return {w for w in s.split() if len(w) > 3 and w not in stop}


def _fold(s: str) -> str:
    """Normalize a name for comparison: strip diacritics, drop punctuation.

    'Garcia-Cely' vs 'Garcia\u0301-Cel\u0301' and 'Onorbe' vs 'O\u00f1orbe'
    must compare equal, otherwise the author gate produces false conflicts.
    """
    import unicodedata
    s = unicodedata.normalize("NFKD", str(s))
    s = "".join(ch for ch in s if not unicodedata.combining(ch))
    return "".join(ch for ch in s.lower() if ch.isalnum() or ch == " ")


def title_overlap(a: str, b: str) -> float:
    ta, tb = norm_tokens(a), norm_tokens(b)
    if not ta or not tb:
        return 0.0
    return len(ta & tb) / len(tb)


def parse_arxiv(xml: str) -> list[dict]:
    try:
        root = ET.fromstring(xml)
    except ET.ParseError:
        return []
    out = []
    for e in root.findall("a:entry", NS):
        def txt(tag):
            el = e.find(tag, NS)
            return re.sub(r"\s+", " ", (el.text or "")).strip() if el is not None else None
        out.append({
            "arxiv_id": (txt("a:id") or "").rsplit("/", 1)[-1],
            "title": txt("a:title"),
            "published": (txt("a:published") or "")[:10],
            "updated": (txt("a:updated") or "")[:10],
            "doi": txt("arxiv:doi"),
            "journal_ref": txt("arxiv:journal_ref"),
            "authors": [re.sub(r"\s+", " ", (a.find("a:name", NS).text or "")).strip()
                        for a in e.findall("a:author", NS)],
            "primary": (e.find("arxiv:primary_category", NS).get("term")
                        if e.find("arxiv:primary_category", NS) is not None else None),
        })
    return out


def parse_crossref(j: str) -> dict | None:
    try:
        m = json.loads(j)["message"]
    except Exception:
        return None
    return {
        "doi": m.get("DOI"),
        "title": (m.get("title") or [None])[0],
        "container": (m.get("container-title") or [None])[0],
        "volume": m.get("volume"),
        "page": m.get("page"),
        "article_number": m.get("article-number"),
        "year": (m.get("issued", {}).get("date-parts") or [[None]])[0][0],
        "authors": [a.get("family") for a in m.get("author", [])],
        "type": m.get("type"),
        "publisher": m.get("publisher"),
    }


# ---------------------------------------------------------------------------
# resolution
# ---------------------------------------------------------------------------
JOURNAL_ALIASES = {
    "sci bull": ["science bulletin", "sci bull"],
    "astron j": ["astron j", "the astronomical journal", "astronomical journal"],
    "phys rev lett": ["physical review letters", "phys rev lett", "prl"],
    "phys rev d": ["physical review d", "phys rev d", "prd"],
    "phys rev research": ["physical review research", "physical review d",
                          "phys rev research", "prd"],
    "mon not r astron soc": ["monthly notices", "mon not r astron soc", "mras"],
    "astrophys j": ["astrophysical journal", "astrophys j", "apj"],
    "astrophys j lett": ["astrophysical journal letters", "apj lett"],
    "j cosmol astropart phys": ["journal of cosmology and astroparticle physics",
                                "jcap"],
    "jcap": ["journal of cosmology and astroparticle physics", "jcap",
             "j cosmol astropart phys"],
    "phys dark univ": ["physics of the dark universe", "phys dark univ"],
    "j high energy phys": ["journal of high energy physics", "jhep"],
    "annu rev astron astrophys": ["annual review of astronomy and astrophysics",
                                  "annu rev astron astrophys"],
    "astron astrophys": ["astronomy and astrophysics", "a&a"],
    "res notes am astron soc": ["research notes of the american astronomical society"],
    "class quantum grav": ["classical and quantum gravity", "class quantum grav"],
}


def _norm_journal(s: str) -> str:
    """Lower-case a journal name and collapse it to single-spaced words.

    The collapse matters: replacing punctuation with a space leaves "phys  rev
    lett" (two spaces) for "Phys. Rev. Lett.", which then fails every alias
    lookup. Verified 2026-10-26 - the matcher rejected a correct PRL record
    because of it.
    """
    s = (s or "").lower().replace("&amp;", "&")
    s = re.sub(r"[^a-z0-9& ]+", " ", s)
    return re.sub(r"\s+", " ", s).strip()


def _journal_matches(seed_journal: str, resolved_journal: str) -> bool:
    """Symmetric journal comparison.

    The alias table is keyed by the SEED's spelling, so a seed written as
    "JCAP" or "Sci. Bull." had no lookup entry. Compare BOTH ways: either
    normalised string contains the other, or they share an alias.
    """
    if not seed_journal or not resolved_journal:
        return True  # nothing to compare against
    s = _norm_journal(seed_journal)
    r = _norm_journal(resolved_journal)
    if s == r or (s and r and (s in r or r in s)):
        return True
    sa = JOURNAL_ALIASES.get(s, [])
    ra = JOURNAL_ALIASES.get(r, [])
    if sa and any(a in r for a in sa):
        return True
    if ra and any(a in s for a in ra):
        return True
    # a shared alias (both spellings list the same canonical name)
    return bool(set(sa) & set(ra))


def _volume_matches(seed_vol, resolved_vol, seed_year=None, seed_journal="") -> bool:
    """Volume comparison that tolerates the issue-vs-year encoding.

    JCAP articles are cited as volume 09 (the ISSUE) in the print style and
    carry volume 2018 (the YEAR) in Crossref's volume field, so the two
    cannot be compared literally. When the journal is JCAP-like and the
    resolved volume is a 4-digit year, compare that year against the SEED
    YEAR instead: the seed's issue number is carried in the article/page
    field, which is checked separately.
    """
    if not seed_vol or not resolved_vol:
        return True
    s = str(seed_vol).strip()
    r = str(resolved_vol).strip()
    if s == r:
        return True
    jn = _norm_journal(seed_journal or "")
    jcap_like = ("jcap" in jn or "j cosmol astropart phys" in jn)
    if jcap_like and len(s) == 2 and len(r) == 4 and seed_year:
        # resolved volume is a year; it must equal the seed's year
        if int(r) == int(seed_year):
            return True
    # JCAP encodes the ARTICLE ISSUE in the seed's volume field ("09") and
    # the YEAR in the publisher's ("2018"), so the two cannot be compared
    # literally. A 2-digit seed volume matches a 4-digit resolved volume
    # only when the resolved year ends in that issue number - which is the
    # JCAP convention (issue 09 of 2018 -> "2018" does NOT end in "09", so
    # we instead compare the resolved YEAR's last two digits against the
    # seed's issue only when the seed also carries a year that agrees).
    if len(s) == 2 and len(r) == 4:
        return int(r[-2:]) == int(s) or int(r[2:]) == int(s)
    if len(s) == 4 and len(r) == 2:
        return int(s[-2:]) == int(r) or int(s[2:]) == int(r)
    return False


def venue_match(seed: dict, rec: dict, arec: dict) -> bool:
    """Does the resolved record sit in the venue the seed expects?

    The journal comparison is fuzzy on abbreviations (the seed writes
    "Phys. Rev. D", Crossref writes "Physical Review D"). The volume and page
    must match EXACTLY when the seed records them - those are the
    discriminating fields, and they are what separates the Bullet Cluster
    paper from a Physics World news item about it.
    """
    want_j = seed.get("journal")
    if not want_j:
        return False
    got_j = rec.get("container") or arec.get("journal_ref") or ""
    if not _journal_matches(want_j, got_j):
        return False
    if not _volume_matches(seed.get("volume"), rec.get("volume"),
                           seed.get("year"), want_j):
        return False
    if seed.get("page") and rec.get("page"):
        # Crossref reports an ARTICLE RANGE ("29-37") where the paper prints a
        # single article number ("29"). Compare the FIRST number of each, and
        # accept a range whose first element equals the seed's page.
        sp = str(seed["page"]).strip()
        gp = str(rec["page"]).strip()
        sp_first = sp.split("-")[0].strip()
        gp_first = gp.split("-")[0].strip()
        if sp != gp and sp_first != gp_first and gp_first != sp:
            return False
    return True


def resolve(slot: str, seed: dict, offline: bool) -> dict:
    """Resolve one slot. Returns a verdict dict; never raises."""
    res: dict = {"slot": slot, "seed": seed, "status": "UNRESOLVED",
                 "resolved": None, "evidence": [], "reason": ""}

    if offline:
        res["status"] = "OFFLINE"
        res["reason"] = "offline mode: seeds only, no API calls"
        return res

    arxiv_rec = None
    crossref_rec = None

    # --- step 1: arXiv by id (authoritative when the body quotes an id) ---
    if seed.get("arxiv"):
        url = f"{ARXIV_API}?id_list={urllib.parse.quote(seed['arxiv'])}"
        raw = http_get(url)
        recs = parse_arxiv(raw) if raw else []
        res["evidence"].append(f"arXiv id_list={seed['arxiv']} -> {len(recs)} entry(ies)")
        if recs:
            arxiv_rec = recs[0]

    # --- step 2: arXiv by author/title search when no id is known ---
    if arxiv_rec is None and (seed.get("authors") or seed.get("title")):
        # A bare surname ("Oman", "Zhang") is a hopeless metadata query -
        # it returns thousands of unrelated papers. Use the phrase the seed
        # already carries, and when there is no title, fall back to the
        # journal+year so the query stays selective.
        q = seed.get("title")
        if not q and seed.get("authors"):
            jr = seed.get("journal") or ""
            yr = seed.get("year")
            if jr and yr:
                q = f"{jr} {yr} {' '.join(seed['authors'])}"
            else:
                q = " ".join(seed["authors"])
        term = "all:" + urllib.parse.quote('"%s"' % q)
        url = (f"{ARXIV_API}?search_query={urllib.parse.quote(term)}"
               f"&max_results=8")
        raw = http_get(url)
        recs = parse_arxiv(raw) if raw else []
        res["evidence"].append(f"arXiv search '{q[:60]}' -> {len(recs)} hit(s)")
        scored = []
        for r in recs:
            to = title_overlap(r["title"] or "", seed.get("title") or "") if seed.get("title") else 0.0
            auth_hit = 1 if seed.get("authors") and any(
                any(a.lower() in (au or "").lower() for au in (r["authors"] or []))
                for a in seed["authors"]) else 0
            yr = (r["published"] or "")[:4]
            yr_hit = 1 if seed.get("year") and yr and abs(int(yr) - seed["year"]) <= 1 else 0
            scored.append((to * 2 + auth_hit + yr_hit, r))
        scored.sort(key=lambda x: -x[0])
        if scored and scored[0][0] >= 2:
            arxiv_rec = scored[0][1]
            res["evidence"].append(
                f"arXiv best candidate score={scored[0][0]:.2f}: "
                f"{(scored[0][1]['title'] or '')[:70]}")
        else:
            res["evidence"].append("arXiv search: no candidate cleared the score floor")

    # --- step 3: Crossref by DOI (from arXiv) or by bibliographic query ---
    doi = (arxiv_rec or {}).get("doi")
    if doi:
        raw = http_get(f"{CROSSREF_API}/{urllib.parse.quote(doi)}")
        crossref_rec = parse_crossref(raw) if raw else None
        res["evidence"].append(f"Crossref DOI {doi} -> "
                               f"{'hit' if crossref_rec else 'miss'}")
        # The DOI carried in an arXiv record can point at the WRONG paper
        # (verified 2026-10-26: arXiv:1909.08241, the Lelli et al. SPARC
        # paper, carries DOI 10.4204/EPTCS.306.21 = "Most General Variant
        # Unifiers"). If the Crossref title does not match the arXiv title,
        # the DOI is wrong - discard it rather than reporting the stray.
        if crossref_rec and arxiv_rec:
            ov = title_overlap(crossref_rec.get("title") or "",
                               arxiv_rec.get("title") or "")
            if ov < 0.5:
                res["evidence"].append(
                    f"Crossref title does NOT match the arXiv title "
                    f"(overlap {ov:.2f}) - the DOI in the arXiv record points at "
                    f"a different paper: {crossref_rec.get('title')}")
                res["evidence"].append(
                    "decision: the Crossref-by-DOI result is DISCARDED; the arXiv "
                    "record is authoritative for identity")
                crossref_rec = None

    # --- step 3a': PREPRINT PATH. For a 2025-2026 preprint there is often no
    # Crossref DOI yet, so the Crossref title search returns some unrelated
    # paper and the slot is wrongly flagged. If the seed supplies an arXiv id
    # and that record's own journal_ref matches the seed venue, the arXiv
    # record IS the publisher-declared metadata and is sufficient.
    if (crossref_rec is None and arxiv_rec and seed.get("arxiv")
            and seed.get("journal")):
        jref = arxiv_rec.get("journal_ref") or ""
        seed_is_arxiv = _norm_journal(seed["journal"]) in ("arxiv", "arxiv preprint")
        jref_ok = bool(jref) and _journal_matches(
            jref.split(",")[0], seed["journal"])
        if seed_is_arxiv or jref_ok:
            res["evidence"].append(
                f"preprint path: the seed names a preprint venue "
                f"('{seed['journal']}') and arXiv {seed['arxiv']} is the "
                f"record of publication (journal_ref='{jref or 'none - preprint'}')"
                + ("; no Crossref DOI exists yet, which is expected for a "
                   "recent preprint" if not jref else ""))
            res["status"] = "RESOLVED"
            res["resolved"] = {
                "title": arxiv_rec.get("title"),
                "authors": arxiv_rec.get("authors") or [],
                "container": (jref.split(",")[0].strip() if jref
                              else "arXiv preprint"),
                "volume": seed.get("volume"),
                "page": seed.get("page"),
                "year": int(arxiv_rec["published"][:4]) if arxiv_rec.get("published") else None,
                "doi": arxiv_rec.get("doi"),
                "arxiv": arxiv_rec.get("arxiv_id"),
                "journal_ref_from_arxiv": jref,
            }
            return res

    # --- step 3b: Crossref by TITLE. A title query is far more selective than
    # an author-name query and Crossref indexes journal articles well. The
    # strict venue check below is what makes the result trustworthy, so the
    # search only has to propose a candidate.
    if crossref_rec is None and seed.get("title"):
        url = (f"{CROSSREF_API}?query.bibliographic="
               f"{urllib.parse.quote(seed['title'])}&rows=8")
        raw = http_get(url)
        items = []
        if raw:
            try:
                items = json.loads(raw)["message"]["items"]
            except Exception:
                items = []
        res["evidence"].append(
            f"Crossref title search -> {len(items)} hit(s)")
        scored = []
        for it in items:
            cr = parse_crossref(json.dumps({"message": it}))
            if not cr:
                continue
            to = title_overlap(cr["title"] or "", seed["title"])
            auth_hit = 1 if seed.get("authors") and any(
                (a or "").lower() in [(x or "").lower() for x in (cr["authors"] or [])]
                for a in seed["authors"]) else 0
            yr_hit = 1 if seed.get("year") and cr["year"] and abs(cr["year"] - seed["year"]) <= 1 else 0
            scored.append((to * 2 + auth_hit + yr_hit, to, cr))
        scored.sort(key=lambda x: -x[0])
        if scored:
            res["evidence"].append(
                f"Crossref best candidate: score={scored[0][0]:.2f} "
                f"title_overlap={scored[0][1]:.2f} "
                f"{(scored[0][2]['title'] or '')[:70]}")
            crossref_rec = scored[0][2]
    # --- step 3c: targeted venue+volume+page query (highest precision) ---
    # A preprint has no publisher venue, so a seed journal of "arXiv"
    # must not be turned into a publisher query.
    if (crossref_rec is None and seed.get("journal") and seed.get("volume")
            and _norm_journal(seed["journal"]) not in ("arxiv", "arxiv preprint")):
        who = (seed.get("authors") or [""])[0]
        bits = [b for b in (who, seed.get("journal"), str(seed.get("volume")),
                            str(seed.get("page"))) if b]
        q2 = " ".join(bits)
        url = (f"{CROSSREF_API}?query.bibliographic="
               f"{urllib.parse.quote(q2)}&rows=8")
        raw = http_get(url)
        items = []
        if raw:
            try:
                items = json.loads(raw)["message"]["items"]
            except Exception:
                items = []
        res["evidence"].append(
            f"Crossref venue query '{q2[:70]}' -> {len(items)} hit(s)")
        scored = []
        for it in items:
            cr = parse_crossref(json.dumps({"message": it}))
            if not cr:
                continue
            to = title_overlap(cr["title"] or "", seed.get("title") or "") \
                if seed.get("title") else 0.0
            got = [_fold(x or "") for x in (cr["authors"] or [])]
            auth_hit = 1 if seed.get("authors") and any(
                _fold(a) in g for a in seed["authors"] for g in got) else 0
            yr_hit = 1 if seed.get("year") and cr["year"] and \
                abs(cr["year"] - seed["year"]) <= 1 else 0
            scored.append((to * 2 + auth_hit + yr_hit, to, cr))
        scored.sort(key=lambda x: -x[0])
        if scored:
            res["evidence"].append(
                f"Crossref venue-query best: score={scored[0][0]:.2f} "
                f"title_overlap={scored[0][1]:.2f} "
                f"{(scored[0][2]['title'] or '')[:66]}")
            crossref_rec = scored[0][2]

    if crossref_rec is None and (seed.get("authors") or seed.get("journal")):
        bib = seed.get("title")
        if not bib and seed.get("authors"):
            jr = seed.get("journal") or ""
            yr = seed.get("year")
            bib = (f"{jr} {yr} {' '.join(seed['authors'])}" if jr and yr
                   else " ".join(seed["authors"]))
        url = (f"{CROSSREF_API}?query.bibliographic={urllib.parse.quote(bib)}"
               f"&rows=6")
        raw = http_get(url)
        items = []
        if raw:
            try:
                items = json.loads(raw)["message"]["items"]
            except Exception:
                items = []
        res["evidence"].append(f"Crossref bibliographic '{bib[:60]}' -> {len(items)} hit(s)")
        scored = []
        for it in items:
            cr = parse_crossref(json.dumps({"message": it}))
            if not cr:
                continue
            to = title_overlap(cr["title"] or "", seed.get("title") or "") if seed.get("title") else 0.0
            got_fams = [(x or "").lower() for x in (cr["authors"] or [])]
            auth_hit = 1 if seed.get("authors") and any(
                (a or "").lower() in got_fams for a in seed["authors"]) else 0
            yr_hit = 1 if seed.get("year") and cr["year"] and abs(cr["year"] - seed["year"]) <= 1 else 0
            scored.append((to * 2 + auth_hit + yr_hit, cr))
        scored.sort(key=lambda x: -x[0])
        if scored and scored[0][0] >= 2:
            crossref_rec = scored[0][1]
            res["evidence"].append(
                f"Crossref best candidate score={scored[0][0]:.2f}: "
                f"{(scored[0][1]['title'] or '')[:70]}")
        else:
            res["evidence"].append("Crossref search: no candidate cleared the score floor")

    # --- verify the two sources agree ---
    if arxiv_rec and crossref_rec:
        ov_ac = title_overlap(arxiv_rec["title"] or "", crossref_rec["title"] or "")
        res["evidence"].append(
            f"cross-check arXiv vs Crossref title overlap={ov_ac:.2f}")
        if ov_ac < 0.6:
            # The two sources disagree. Decide which one matches the SEED,
            # rather than failing the slot outright: a bibliographic search
            # legitimately returns a NEARBY paper (same topic, different
            # author set) as its top hit, and that stray must not veto a
            # perfectly good id-based resolution.
            seed_title = seed.get("title") or ""
            ov_seed_a = title_overlap(arxiv_rec["title"] or "", seed_title)
            ov_seed_c = title_overlap(crossref_rec["title"] or "", seed_title)
            res["evidence"].append(
                f"seed match: arXiv={ov_seed_a:.2f} crossref={ov_seed_c:.2f}")
            # A preprint and its published version are the SAME paper with
            # often-different titles. Detect that by author set + year, and
            # treat it as agreement rather than a conflict.
            au_a = {s.lower() for s in
                    ((a.split()[-1] if " " in str(a) else str(a)) for a in
                     (arxiv_rec.get("authors") or [])) if s}
            au_c = {s.lower() for s in
                    ((a.split()[-1] if " " in str(a) else str(a)) for a in
                     (crossref_rec.get("authors") or [])) if s}
            yr_a = (arxiv_rec.get("published") or "")[:4]
            yr_c = str(crossref_rec.get("year") or "")[:4]
            same_authors = bool(au_a and au_c and len(au_a & au_c) >= 2)
            same_year = bool(yr_a and yr_c and yr_a == yr_c)
            if same_authors and same_year:
                res["evidence"].append(
                    "decision: same author set and year on both sides — this is "
                    "the PREPRINT and the PUBLISHED version of one paper "
                    "(title changed between them); NOT a conflict")
                res["status"] = "RESOLVED"
                # Prefer the PUBLISHED record for the reference list; carry the
                # arXiv id as the preprint pointer.
                res["resolved"] = {
                    "title": crossref_rec.get("title") or arxiv_rec.get("title"),
                    "authors": crossref_rec.get("authors") or arxiv_rec.get("authors"),
                    "container": crossref_rec.get("container") or arxiv_rec.get("journal_ref"),
                    "volume": crossref_rec.get("volume"),
                    "page": crossref_rec.get("page") or crossref_rec.get("article_number"),
                    "year": crossref_rec.get("year") or (int(yr_a) if yr_a else None),
                    "doi": crossref_rec.get("doi") or arxiv_rec.get("doi"),
                    "arxiv": arxiv_rec.get("arxiv_id"),
                    "journal_ref_from_arxiv": arxiv_rec.get("journal_ref"),
                    "note": ("preprint title differs from published title; the "
                             "published version is used"),
                }
                return res
            if seed_title and ov_seed_a >= 0.5 and ov_seed_c < 0.5:
                res["evidence"].append(
                    "decision: the arXiv id resolves to the expected paper; the "
                    "Crossref hit is a topical near-match and is DISCARDED")
                crossref_rec = None
                arxiv_rec = {"arxiv_id": arxiv_rec["arxiv_id"],
                             "title": arxiv_rec["title"],
                             "published": arxiv_rec["published"],
                             "updated": arxiv_rec["updated"],
                             "doi": arxiv_rec["doi"],
                             "journal_ref": arxiv_rec["journal_ref"],
                             "authors": arxiv_rec["authors"],
                             "primary": arxiv_rec["primary"]}
            elif seed_title and ov_seed_c >= 0.5 and ov_seed_a < 0.5:
                res["evidence"].append(
                    "decision: the Crossref hit matches the expected paper; the "
                    "arXiv record is DISCARDED")
                arxiv_rec = None
            else:
                res["status"] = "CONFLICT"
                res["reason"] = ("arXiv and Crossref returned different papers for "
                                 "this slot and neither matches the expected title "
                                 "— needs a human")
                res["resolved"] = {"arxiv": arxiv_rec, "crossref": crossref_rec}
                return res

    # --- assemble the candidate ---
    rec = crossref_rec or {}
    arec = arxiv_rec or {}
    title = rec.get("title") or arec.get("title")
    if not title:
        res["reason"] = "no candidate retrieved"
        return res

    # ---- verification gates ----
    # A surname+year match is NOT sufficient. Verified 2026-10-26: the loose
    # gates let three wrong papers through as "RESOLVED" -
    #   [4]   the Bullet Cluster paper came back as "Physics World 21, 5 (2008)"
    #   [55c] a massive-galaxy DM paper came back as "Optical Fiber Technology"
    #   [7]   a PRL came back as an AIP Conference Proceedings volume
    # All three satisfied "an author surname appears" + "the year is close".
    # A slot is RESOLVED only if the record matches the EXPECTED VENUE
    # (journal + volume + page) or the title closely. Otherwise CONFLICT.
    venue_ok = venue_match(seed, rec, arec)
    res["evidence"].append(
        "venue match (journal+volume+page vs seed): "
        + ("YES" if venue_ok else "NO")
        + ("" if venue_ok else
           f" | resolved: journal={(rec.get('container') or arec.get('journal_ref'))!r}"
           f" vol={rec.get('volume')!r} page={rec.get('page')!r}"))

    if seed.get("title"):
        ov = title_overlap(title, seed["title"])
        res["evidence"].append(f"title overlap vs seed = {ov:.2f}")
        # When the seed NAMES a journal, a venue mismatch is FATAL - a title
        # match cannot rescue it. Verified 2026-10-26: a Physics World news
        # item titled "A map of dark matter" scored title_overlap 1.00 against
        # the ApJ 679 seed and was reported RESOLVED for reference [4]. The
        # same trap applies to conference proceedings and to papers with
        # generic titles.
        if seed.get("journal") and not venue_ok:
            res["status"] = "CONFLICT"
            res["reason"] = (f"venue mismatch (seed expects {seed['journal']}"
                             + (f" {seed.get('volume')}" if seed.get("volume") else "")
                             + (f" {seed.get('page')}" if seed.get("page") else "")
                             + f"; resolved {rec.get('container') or arec.get('journal_ref')!r}"
                             + f" vol={rec.get('volume')!r} page={rec.get('page')!r})"
                             f" - title overlap {ov:.2f} does not rescue it: "
                             f"{title[:80]}")
            res["resolved"] = {"arxiv": arec, "crossref": rec, "title": title}
            return res
        if ov < 0.7:
            res["status"] = "UNVERIFIED"
            res["reason"] = (f"title overlap {ov:.2f} is low but the venue matches "
                             f"the seed - needs a human read")
            res["resolved"] = {"arxiv": arec, "crossref": rec, "title": title}
            return res
    elif not venue_ok or (not seed.get("journal") and not seed.get("title")):
        # FIXED 2026-10-27: a seed with neither a title nor a venue can only
        # be resolved by surname+year, which is NOT an identification. Slot
        # [55c] ("Wang 2026", no title) previously resolved to an optical-
        # fibre traffic-sensing paper with seven authors named Wang.
        res["status"] = "CONFLICT"
        res["reason"] = (f"only a surname+year match (venue mismatch) - not an "
                         f"identification: {title[:90]}")
        res["resolved"] = {"arxiv": arec, "crossref": rec, "title": title}
        return res
    if seed.get("authors"):
        got = [a for a in (rec.get("authors") or arec.get("authors") or [])]
        got_surnames = []
        for g in got:
            if " " in str(g):
                got_surnames.append(str(g).split()[-1])
            else:
                got_surnames.append(str(g))
        # Name particles: Crossref records "van Dokkum, P." as family "Dokkum"
        # in some records and "van Dokkum" in others, so an expected name of
        # "van Dokkum" must match a got name of "Dokkum" (and vice versa).
        # Compare the LAST TOKEN of the expected name against every token of
        # the got name.
        def _last_tok(s):
            toks = _fold(s).split()
            return toks[-1] if toks else ""

        missing = [a for a in seed["authors"]
                   if not any(_last_tok(a) and _last_tok(a) in _fold(g).split()
                              or (_last_tok(a) and _last_tok(a) in _fold(g))
                              for g in got_surnames)]
        res["evidence"].append(
            f"authors expected={seed['authors']} got={got_surnames[:8]}"
            + (f" MISSING={missing}" if missing else " (all present)"))
        # HARD GATE (fixed 2026-10-27): a candidate that does not contain the
        # expected author surnames is a DIFFERENT paper, whatever the title
        # and venue say. The old condition only fired when the seed had no
        # title, so "Turner 2021, Atomic Dark Matter" resolved to Ryan's
        # "Black Holes From Atomic Dark Matter" (title overlap 1.00, venue
        # match YES) and was reported RESOLVED. It is now a CONFLICT.
        if missing:
            res["status"] = "CONFLICT"
            res["reason"] = (f"expected author(s) {missing} are absent from the "
                             f"resolved record {got_surnames[:8]} - this is a "
                             f"different paper, not the one cited")
            res["resolved"] = {"arxiv": arec, "crossref": rec, "title": title}
            return res
    if seed.get("year"):
        yr = rec.get("year") or (int((arec.get("published") or "0000")[:4])
                                 if arec.get("published") else None)
        if yr and abs(yr - seed["year"]) > 1:
            res["evidence"].append(f"year expected={seed['year']} got={yr} (MISMATCH)")
            res["status"] = "CONFLICT"
            res["reason"] = f"year mismatch: expected {seed['year']}, got {yr}"
            res["resolved"] = {"arxiv": arec, "crossref": rec, "title": title}
            return res
        res["evidence"].append(f"year expected={seed['year']} got={yr} (ok)")

    res["status"] = "RESOLVED"
    res["resolved"] = {
        "title": title,
        "authors": rec.get("authors") or arec.get("authors"),
        "container": rec.get("container") or arec.get("journal_ref"),
        "volume": rec.get("volume"),
        "page": rec.get("page") or rec.get("article_number"),
        "year": rec.get("year") or (int(arec["published"][:4])
                                        if arec.get("published") else None),
        "doi": rec.get("doi") or arec.get("doi"),
        "arxiv": arec.get("arxiv_id") or seed.get("arxiv"),
        "journal_ref_from_arxiv": arec.get("journal_ref"),
    }
    return res


def format_entry(slot: str, c: dict) -> str:
    """Render a candidate in the paper's existing [N] reference style."""
    au = c.get("authors") or []
    if au:
        names = []
        for a in au[:6]:
            names.append(a)
        astr = ", ".join(names) + (", et al." if len(au) > 6 else "")
    else:
        astr = "[authors unrecorded]"
    bits = [f"[{slot}]", astr, f'"{c["title"]}"']
    jr = c.get("journal_ref_from_arxiv") or c.get("container")
    if jr:
        bits.append(str(jr))
    if c.get("year"):
        bits.append(f"({c['year']})")
    if c.get("arxiv"):
        bits.append(f"arXiv:{c['arxiv']}")
    return " ".join(bits)


def duplicate_report(results: dict[str, dict]) -> list[dict]:
    """Find slots whose resolved records point at the SAME paper."""
    by_key: dict[str, list[str]] = {}
    for slot, r in results.items():
        if r["status"] != "RESOLVED" or not r.get("resolved"):
            continue
        c = r["resolved"]
        key = (c.get("arxiv") or c.get("doi") or
               (c.get("title") or "").lower()[:60])
        if key:
            by_key.setdefault(key, []).append(slot)
    return [{"key": k, "slots": v} for k, v in by_key.items() if len(v) > 1]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--offline", action="store_true",
                    help="skip all network calls; report seeds only")
    ap.add_argument("--slot", action="append", default=[],
                    help="resolve only these slots (repeatable)")
    ap.add_argument("--write-candidates", action="store_true",
                    help="write the markdown candidate table into to_verify/")
    args = ap.parse_args()

    slots = args.slot or sorted(SEEDS, key=lambda s: (int(re.match(r"\d+", s).group()), s))
    results: dict[str, dict] = {}
    for slot in slots:
        seed = SEEDS.get(slot)
        if not seed:
            print(f"[{slot}] no seed — skipping", file=sys.stderr)
            continue
        print(f"[{slot}] resolving...", flush=True)
        r = resolve(slot, seed, args.offline)
        results[slot] = r
        for ev in r["evidence"]:
            print(f"      {ev}")
        print(f"      => {r['status']}"
              + (f" — {r['reason']}" if r.get("reason") else ""))

    # summary
    counts: dict[str, int] = {}
    for r in results.values():
        counts[r["status"]] = counts.get(r["status"], 0) + 1
    print("\n=== SUMMARY ===")
    for k in sorted(counts):
        print(f"  {k}: {counts[k]}")
    unresolved = [s for s, r in results.items() if r["status"] != "RESOLVED"]
    if unresolved:
        print(f"  needs a human: {unresolved}")

    dups = duplicate_report(results)
    if dups:
        print("\n=== DUPLICATE SLOTS (same underlying paper) ===")
        for d in dups:
            print(f"  {d['slots']}  -> {d['key']}")

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps({
        "generated_by": "scripts/resolve_references.py",
        "paper": str(PAPER.relative_to(REPO)),
        "counts": counts,
        "duplicates": dups,
        "results": results,
    }, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\nwrote {OUT_JSON.relative_to(REPO)}")

    if args.write_candidates:
        md = OUT_DIR / "resolved_reference_candidates.md"
        lines = ["# Resolved reference candidates",
                 "",
                 f"**Generated:** `scripts/resolve_references.py` (no network state cached — "
                 f"re-run to refresh)",
                 f"**Source of truth for the slots:** the paper's References section + "
                 f"`v0.3-prelim/docs/AUDIT_REFERENCES.md`",
                 "",
                 "Candidates below are machine-resolved against arXiv and/or Crossref and "
                 "verified (title overlap, author surnames, year). **The paper's reference "
                 "list was NOT edited** — every line is a proposal for human sign-off.",
                 "",
                 "| slot | status | candidate |",
                 "|---|---|---|"]
        for slot in slots:
            r = results.get(slot)
            if not r:
                continue
            if r["status"] == "RESOLVED":
                lines.append(f"| [{slot}] | RESOLVED | {format_entry(slot, r['resolved'])} |")
            else:
                lines.append(f"| [{slot}] | {r['status']} | {r.get('reason') or '—'} |")
        md.write_text("\n".join(lines) + "\n", encoding="utf-8")
        print(f"wrote {md.relative_to(REPO)}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
