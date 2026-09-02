"""KIV-check for the LZ 2026-09-01 mysterious signal paper.

Scheduled to run 60 days after announcement (2026-11-01).
Goal: check whether the LZ paper has appeared on arXiv and if its
significance has changed; if so, re-evaluate the T77 update.
"""
from __future__ import annotations

import json
import re
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ARXIV_QUERY_URL = "http://export.arxiv.org/api/query"
LZ_PRESS_RELEASE_URL = "https://newscenter.lbl.gov/2026/09/01/lz-sees-surprising-result-search-dark-matter"
LZ_SHEFFIELD_URL = "https://sheffield.ac.uk/news/unexplained-signal-search-dark-matter-could-mark-major-breakthrough"

# Common search terms for the LZ 2026-09 paper (flexible)
SEARCH_QUERIES = [
    'au:"LUX-ZEPLIN" AND ti:"mysterious"',
    'au:"LZ Collaboration" AND ti:"mysterious"',
    'ti:"LZ" AND ti:"single event" AND ti:"WIMP"',
    'au:"Aalbers" AND ti:"mysterious"',  # LZ spokesperson search
    'abs:"LUX-ZEPLIN" AND abs:"single event"',
    'au:"LUX-ZEPLIN" AND abs:"two sigma"',  # catch the actual paper
    'au:"LUX-ZEPLIN" AND abs:"mysterious"',
]


def query_arxiv(query: str, max_results: int = 10) -> list:
    """Query arXiv API and return list of result dicts."""
    url = (
        f"{ARXIV_QUERY_URL}?search_query={query}&max_results={max_results}"
        "&sortBy=relevance&sortOrder=descending"
    )
    try:
        with urllib.request.urlopen(url, timeout=30) as resp:
            data = resp.read().decode("utf-8")
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError) as e:
        return [{"error": f"arxiv API failed: {e}"}]

    # Parse arXiv API XML response (simplified)
    entries = []
    for match in re.finditer(
        r"<entry>(.*?)</entry>", data, re.DOTALL
    ):
        entry = match.group(1)
        # Extract arxiv-id
        id_match = re.search(r"<id>(.*?)</id>", entry)
        title_match = re.search(r"<title>(.*?)</title>", entry, re.DOTALL)
        authors = re.findall(r"<author>\s*<name>(.*?)</name>", entry)
        date_match = re.search(
            r"<published>(\d{4}-\d{2}-\d{2})", entry
        )
        summary_match = re.search(
            r"<summary>(.*?)</summary>", entry, re.DOTALL
        )
        if id_match:
            entries.append({
                "arxiv_id": id_match.group(1).split("/")[-1],
                "title": title_match.group(1).strip() if title_match else "",
                "authors": authors,
                "published": date_match.group(1) if date_match else "",
                "summary": (
                    re.sub(r"\s+", " ", summary_match.group(1)).strip()
                    if summary_match else ""
                ),
            })
    return entries


def search_for_lz_paper() -> dict:
    """Search arXiv for the LZ mysterious-signal paper."""
    print(f"[{datetime.now(timezone.utc).isoformat()}] KIV-check starting...")
    print()

    all_hits = []
    for query in SEARCH_QUERIES:
        print(f"Query: {query!r}")
        hits = query_arxiv(query)
        for hit in hits:
            if "error" in hit:
                print(f"  ERROR: {hit['error']}")
            else:
                print(f"  hit: {hit['arxiv_id']} ({hit['published']}) {hit['title'][:80]}")
                if hit["arxiv_id"] not in [h["arxiv_id"] for h in all_hits]:
                    all_hits.append(hit)
        print()

    return {
        "kiv_check_date": datetime.now(timezone.utc).isoformat(),
        "kiv_origin_date": "2026-09-02",
        "kiv_origin_event": "LZ 2026-09-01 mysterious signal announcement (2.6σ, ≥ 200 GeV/c² WIMP)",
        "search_queries": SEARCH_QUERIES,
        "arxiv_hits_found": all_hits,
        "n_hits": len(all_hits),
    }


def assess_results(results: dict) -> dict:
    """Assess whether the LZ paper has appeared and what to do."""
    hits = results["arxiv_hits_found"]
    n = results["n_hits"]

    # Heuristic: a "real" LZ paper has the LZ spokesperson as author
    # (Aalbers, Gaitskell, etc.) and ≥5 authors
    if n == 0:
        verdict = "NOT_FOUND"
        action = (
            "NO LZ paper found on arXiv as of 2026-11-01. The 2026-09-01 "
            "signal has NOT been published. Consider: (a) extend KIV by "
            "another 60-90 days, or (b) check LZ website directly."
        )
    else:
        # Inspect hits
        candidates = []
        for hit in hits:
            authors_n = len(hit["authors"])
            title_lower = hit["title"].lower()
            if (
                authors_n >= 5  # LZ papers have hundreds of authors; small lists are not LZ
                and ("lz" in title_lower or "lux-zeplin" in title_lower or "wimp" in title_lower or "dark matter" in title_lower)
            ):
                candidates.append(hit)

        if candidates:
            verdict = "FOUND"
            action = (
                f"LZ paper appears to be on arXiv: {candidates[0]['arxiv_id']} "
                f"({candidates[0]['published']}). Re-evaluate T77 update per the "
                f"trigger conditions in v0.3-prelim/docs/T77_LZ_2026_09_UPDATE.md."
            )
        else:
            verdict = "AMBIGUOUS"
            action = (
                f"{n} arXiv hits found but none clearly match the LZ signal paper. "
                f"Manual inspection required."
            )

    return {
        "verdict": verdict,
        "action": action,
        "candidates": candidates if n > 0 else [],
    }


def main():
    results = search_for_lz_paper()
    assessment = assess_results(results)
    full = {**results, "assessment": assessment}

    out_path = Path(
        "v0.3-prelim/data/results/2026-11-01_lz_kiv_check.json"
    )
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w") as f:
        json.dump(full, f, indent=2, default=str)

    print("=" * 60)
    print(f"Verdict: {assessment['verdict']}")
    print(f"Action: {assessment['action']}")
    print(f"Full results: {out_path}")
    print(f"  ({out_path.stat().st_size} B)")

    # Print summary for the cron stdout
    print()
    print("=" * 60)
    print("CRON OUTPUT SUMMARY (visible to user when fired)")
    print("=" * 60)
    print(f"Date of check: {results['kiv_check_date']}")
    print(f"Original event: LZ 2026-09-01 mysterious signal (2.6σ)")
    print(f"Searched {len(SEARCH_QUERIES)} arXiv queries")
    print(f"Found {n} unique arXiv hits")
    print(f"Verdict: {assessment['verdict']}")
    print(f"Action: {assessment['action']}")


if __name__ == "__main__":
    main()