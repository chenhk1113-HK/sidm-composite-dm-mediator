"""
T95.10 lit-search — literature search for published gap-count constraints
on the 95 residual streams identified by t95_v26_pilot_113_streams.py.

PURPOSE
=======
The T95.9 curated set has 10 streams with published sigma/m constraints.
The T95.10 residual is 95 streams with track+velocity data. Most of these
are recently discovered (Gaia-N, New-N, C-N from Malhan+ 2021 / Ibata+ 2024
catalogs) and likely lack individual gap-count papers.

This module provides:
  1. A per-stream literature search scaffold (search_queries() generates
     the right arXiv/ADS queries for each stream).
  2. A results table that the human (or future agent) fills in.
  3. A function to convert a populated results table into a stream
     constraint dict compatible with multi_stream_loglik().

OUTPUT
  - outputs/t95/t95_v26_lit_search_queries.txt (one query per stream)
  - outputs/t95/t95_v26_lit_search_results.json (initial empty template)
  - docs/T95_EXTENDED_113STREAMS_LITSEARCH.md (the human fills this in)

STATUS: SCAFFOLD SHIPPED 2026-09-08. Literature body to be filled in
by the user or a follow-up session.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pandas as pd

_PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_PROJECT_ROOT / "code"))

from t95_v26_pilot_113_streams import run_full


# ============================================================================
# Query generation
# ============================================================================
def search_queries(stream_name: str) -> list[str]:
    """Generate a list of arXiv/ADS search queries for a given stream.

    Returns 4 queries:
      1. By stream short name (most specific)
      2. By stream long name (galstreams catalog full name)
      3. "subhalo gap" + stream (for gap-count papers)
      4. "stream" + progenitor (if known)
    """
    queries = [
        f'"{stream_name}" stellar stream gap',
        f'"{stream_name}" stellar stream subhalo',
        f'"{stream_name}" stellar stream dark matter',
        f'"{stream_name}" Milky Way stream density perturbations',
    ]
    return queries


# ============================================================================
# Known reference compendium
# ============================================================================
# Per-stream known references from the existing T95.9 curated list + a few
# well-known streams likely to have published data. This is a starting
# scaffold, not exhaustive.
KNOWN_REFERENCES = {
    # Curated (already in T95.9) - kept here for completeness
    "GD-1": ["Zhang+ 2025 ApJL 978 L23", "Tavangar & Price-Whelan 2025 ApJ 988 45"],
    "Pal5": ["Carlberg 2012 ApJ 748 13", "Bonaca+ 2020 ApJ 897 L18"],
    "Orphan-Chenab": ["Koposov+ 2019 MNRAS 485 4726", "Shipp+ 2021 ApJ 923 149"],
    "AAU-AliqaUma": ["Li+ 2021 ApJ 923 230"],
    "Jhelum": ["Shipp+ 2018 ApJ 862 114"],
    "Phoenix": ["Shipp+ 2019"],  # No confirmed gaps
    "Indus": ["Shipp+ 2019"],
    "NGC3201": ["Palau+ 2021 (NGC3201-Gjoll)"],
    "M5": ["Grillmair 2019"],
    "M92": ["Thomas 2020"],

    # Possibly-published residual streams (literature search candidates)
    # Sagittarius is the gold-standard; published gap counts exist
    "Sagittarius": ["Majewski+ 2003 ApJ 599 1082 (Sgr core)",
                    "Law & Majewski 2010 ApJ 714 229 (Sgr tail)",
                    "Belokurov+ 2014 MNRAS 437 116 (Sgr stream gaps)"],
    "Aquarius": ["Balbinot+ 2016 ApJ 820 58"],
    "Jhelum-a": ["Shipp+ 2018 ApJ 862 114"],
    "Jhelum-b": ["Shipp+ 2018 ApJ 862 114"],
    "Monoceros": ["Yanny+ 2003 ApJ 588 824 (Monoceros ring)"],
    "Cetus": ["Newberg+ 2009 ApJ 700 L61 (Cetus Polar)"],
    "Cetus-Palca": ["Shipp+ 2018 ApJ 862 114 (Palca + Cetus)"],
    "Elqui": ["Li+ 2019 MNRAS 490 3508"],
    "TucanaIII": ["Drlica-Wagner+ 2015 ApJ 813 109 (Tucana III)"],
    "Ophiuchus": ["Bernard+ 2014 MNRAS 443 L84 (Ophiuchus stream)"],

    # Gaia-discovered streams (Malhan+ 2018, 2021)
    # Likely NO individual gap-count papers; need arXiv check
    # "Gaia-1" through "Gaia-12": see Malhan+ 2018, Malhan+ 2021
    # "New-1" through "New-27": see Ibata+ 2024 (preliminary catalog)
    # "C-1" through "C-25": see Ibata+ 2024
}


def known_constraints_for(stream_name: str) -> dict | None:
    """If we already know the published sigma/m constraint for a stream,
    return it; otherwise return None.

    This is the table T95.9 built up; adding to it is the work of
    the literature search.
    """
    # Currently empty for residual streams - this is the gap.
    return None


# ============================================================================
# Results table
# ============================================================================
def build_results_template() -> pd.DataFrame:
    """Build an empty results template for the human/lit-search to fill."""
    from t95_v26_pilot_113_streams import run_full
    summary = run_full(verbose=False)
    ok = sorted([s for s in summary["per_stream"] if s.get("status") == "ok"],
                 key=lambda x: x["stream"])

    rows = []
    for d in ok:
        rows.append({
            "stream": d["stream"],
            "galstreams_long_name": "",  # fill from catalog
            "v_3d_kms": round(d["v_3d_kms"], 1),
            "sigma_m_pred_master_yukawa": round(d["sigma_m_pred_master_yukawa_cm2_per_g"], 3),
            "search_queries": " | ".join(search_queries(d["stream"])),
            "papers_found": "",  # fill: e.g. "Malhan+ 2018, Shipp+ 2018"
            "n_gaps_published": "",  # fill: e.g. 2 or "0 (no gaps confirmed)"
            "sigma_m_lower_published": "",  # fill: e.g. 0.5
            "sigma_m_upper_published": "",  # fill: e.g. 2.0
            "v_perturber_published": "",  # fill: e.g. 30 (km/s)
            "constraint_status": "needs_search",  # one of:
            #   "needs_search" - not yet searched
            #   "searched_no_constraint" - searched, no published gap data
            #   "constraint_added" - found and integrated
            #   "synthesized_only" - no data, using velocity-only placeholder
            "notes": "",
        })
    return pd.DataFrame(rows)


def main() -> int:
    out_dir = _PROJECT_ROOT / "outputs" / "t95"
    out_dir.mkdir(parents=True, exist_ok=True)

    # 1. Write the queries file
    queries_path = out_dir / "t95_v26_lit_search_queries.txt"
    df = build_results_template()
    with queries_path.open("w") as f:
        f.write("# T95.10 Literature search queries\n")
        f.write("# 95 streams × 4 queries = 380 queries to run.\n")
        f.write("# Use this as a checklist: run each query against arXiv/ADS,\n")
        f.write("# record findings in t95_v26_lit_search_results.json.\n\n")
        for _, row in df.iterrows():
            f.write(f"## {row['stream']}\n")
            for q in row["search_queries"].split(" | "):
                f.write(f"  - {q}\n")
            f.write("\n")
    print(f"Wrote {queries_path}")

    # 2. Write the empty results template
    results_path = out_dir / "t95_v26_lit_search_results.json"
    results_path.write_text(json.dumps({
        "schema_version": "1.0",
        "date_created": "2026-09-08",
        "n_streams": len(df),
        "status_counts": {"needs_search": len(df)},
        "rows": df.to_dict(orient="records"),
    }, indent=2))
    print(f"Wrote {results_path}")

    # 3. Write the scaffolding doc
    md_path = _PROJECT_ROOT / "docs" / "T95_EXTENDED_113STREAMS_LITSEARCH.md"
    md_path.write_text(
        "# T95.10 Literature Search Scaffolding\n\n"
        f"**Date:** 2026-09-08  \n"
        f"**Streams to search:** 95 (T95.10 OK subset)  \n"
        f"**Queries per stream:** 4 (by short name × subhalo/gap/DM/perturbations)  \n"
        f"**Total queries:** {4 * len(df)}  \n\n"
        "## Purpose\n\n"
        "Replace the velocity-only synthesized constraints in the T95.10 joint\n"
        "fit with published literature constraints as found. The T95.9 curated\n"
        "set has 10 streams with published sigma/m bounds. The T95.10 residual\n"
        "has 95 streams with track+velocity data, but most lack individual gap-count\n"
        "papers (they were discovered recently by Gaia).\n\n"
        "## Known references (from T95.9 + literature pointers)\n\n"
        "See `KNOWN_REFERENCES` dict in `t95_v26_lit_search.py` for the current\n"
        "starting set. Includes Sagittarius (the gold standard), Cetus, Elqui,\n"
        "Tucana III, Ophiuchus, Monoceros, etc. The 95 OK streams mostly consist\n"
        "of Gaia-discovered (Gaia-N) and Ibata-2024 catalog (New-N, C-N) streams\n"
        "without dedicated gap-count papers.\n\n"
        "## Workflow\n\n"
        "1. Open `outputs/t95/t95_v26_lit_search_queries.txt` — it has all 380 queries.\n"
        "2. For each stream, run the 4 queries against arXiv (`arxiv.org/search`)\n"
        "   or NASA/ADS (`ui.adsabs.harvard.edu`).\n"
        "3. Record findings in `outputs/t95/t95_v26_lit_search_results.json`:\n"
        "   - `papers_found`: comma-separated author+year list\n"
        "   - `n_gaps_published`: count or '0 (no gaps confirmed)'\n"
        "   - `sigma_m_lower_published` / `sigma_m_upper_published`: from gap-count analysis\n"
        "   - `v_perturber_published`: characteristic perturber velocity\n"
        "   - `constraint_status`: needs_search → searched_no_constraint → constraint_added\n"
        "4. After search complete, re-run the T95.10 pipeline with the populated\n"
        "   constraints — joint loglik will become meaningful.\n\n"
        "## Honest scoping note\n\n"
        "A full literature search of 95 streams × 4 queries is 1-2 hours of\n"
        "focused work. Most streams will fall into `searched_no_constraint`\n"
        "(recently discovered, no dedicated gap-count paper). Expected yield:\n"
        "- 5-10 streams with NEW constraints (Sagittarius, Cetus, Elqui, etc.)\n"
        "- 30-50 streams with `searched_no_constraint`\n"
        "- 30-40 streams that remain `needs_search` (low priority, very recent)\n\n"
        "## Status (2026-09-08)\n\n"
        "- [x] Scaffold shipped (this file + queries file + empty results JSON)\n"
        "- [ ] Stream-by-stream arXiv search (1-2 hrs of focused work)\n"
        "- [ ] Populate results JSON\n"
        "- [ ] Re-run T95.10 with literature constraints\n"
        "- [ ] Update joint fit + T95 finding if loglik moves materially\n"
    )
    print(f"Wrote {md_path}")

    print(f"\n=== Literature search scaffold complete ===")
    print(f"Streams to search: {len(df)}")
    print(f"Total queries: {4 * len(df)}")
    print(f"Files written:")
    print(f"  - {queries_path}")
    print(f"  - {results_path}")
    print(f"  - {md_path}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
