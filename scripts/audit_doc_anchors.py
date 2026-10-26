#!/usr/bin/env python3
"""
audit_doc_anchors.py — Gate layer 8: cross-document section-anchor integrity.

WHY THIS EXISTS
---------------
On 2026-10-26 the consolidated report shipped TWO dangling section
cross-references of its own ("§18.6", which does not exist in a document whose
sections end at §18.5) inside the very section that documents the rule
"resolve a review's section anchor mechanically before believing the sentence
containing it". The shipped report also mis-stated which model ran its
verification. Both classes are invisible to the existing 7 gate layers,
because every one of them validates the PAPER against the CODE — none of them
validates a DOCUMENT against itself.

This layer closes the anchor half of that gap. It resolves every "§N" /
"§N.M" reference in the two round-5 deliverables and in the paper against the
actual heading sets, and classifies each one:

  OK       - resolves to a live heading in one of the audited documents
  STALE    - the section heading once existed and was removed (a pointer to a
             retired section). Reported, not a failure: the paper has eight of
             these, inherited from the 2026-10-05 copy-edit, and they are a
             tracked gap rather than something this layer may silently repair.
  DANGLING - the section never existed at all. THIS IS A FAILURE. It is the
             class that shipped twice.

The distinction between STALE and DANGLING is the whole point. A reference to
a section that was deleted is a different (and milder) defect from a reference
to a section that was never written, and a checker that cannot tell them apart
will either cry wolf on the paper's retired pointers or — far worse —
wave through a reference to a section that does not exist.

RESOLUTION SCOPE (the subtle part)
-----------------------------------
A section number is only meaningful WITHIN a document. Two different
documents here both have a "§9.3", and they are different sections. So the
resolution target is determined per document, not by a flat union:

  paper      -> the paper's own headings ONLY. The paper never cites the
                report or the companion, and letting it resolve against
                them is how a real defect gets masked.
  report     -> the report's headings, then the paper's (the report is about
                the paper and cites it constantly), then the companion's.
  companion  -> the companion's headings, then the paper's, then the
                report's.

An earlier draft of this layer used a flat union of all three heading sets.
That silently resolved the paper's "§9.3" against the COMPANION's §9.3 — a
real paper defect hidden by an unrelated document. The per-document scoping
below is the fix, and it is recorded here because it is the kind of bug that
a union-based checker will always have.

QUOTED-BAD REFERENCES
---------------------
The deliverables quote the external reviewer's wrong anchors on purpose
("n20 cites §23-§25 and §26", "§26 does not exist", ...). Those are
quotations of an error, not errors, and the layer recognises them by the
surrounding negating language rather than by a hand-maintained line list — so
the exemption set cannot rot as the documents are edited.

PAPER STALE-ANCHOR BASELINE
----------------------------
The paper carries eight references to sections removed by commit 10b7552
(the 2026-10-05 "R88 decisive copy-edit") and by earlier retirements. They are
listed in RETIRED_PAPER_SECTIONS below with the commit that retired each. This layer
FAILS if the paper's stale-anchor set grows, and it reports any
RETIRED_PAPER_SECTIONS
entry that is no longer triggered, so the list has to be re-audited every
cycle instead of accumulating dead exemptions.

Usage:
    python scripts/audit_doc_anchors.py            # audit + print the table
    python scripts/audit_doc_anchors.py --json     # machine-readable output

Exit: 0 = no DANGLING references; 1 = at least one DANGLING reference, or the
paper's stale-anchor baseline grew.
"""
import argparse
import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent

DOCS = REPO / "docs" / "dual_review_5loop"
REPORT = DOCS / "SIDM_ROUND5_CONSOLIDATED_FIXES_v1.10_2026-10-26.md"
COMPANION = DOCS / "SIDM_ROUND5_CHANGED_CODE_v1.8_2026-10-26.md"
PAPER = REPO / "v0.3-prelim" / "docs" / "PAPER_V1_DRAFT.md"

# A heading is "## 17. Title", "### 17.3 Title", "#### 10.4g.1 Title".
# The trailing dot on top-level headings is optional; the number may carry
# letter suffixes (9.3b, 10.4g.1).
HEADING_RE = re.compile(
    r"^(#{2,4})\s+(?:§)?(\d+(?:\.\d+[a-z]?)*)\.?\s+(\S.*)$", re.MULTILINE
)
# A section reference in body text: "§17.3", "§23", "§10.4g.1".
SECTION_REF_RE = re.compile(r"§(\d+(?:\.\d+[a-z]?)*)")

# A reference that is being QUOTED as wrong. The deliverables quote the
# external reviewer verbatim and adjudicate the quote, so the anchor inside
# the quotation is expected not to resolve. Recognised by the negating
# language around it, not by a line list, so it survives edits.
QUOTED_BAD_CONTEXT_RE = re.compile(
    r"does not exist"
    r"|doesn'?t exist"
    r"|no §"
    r"|nonexistent"
    r"|non-existent"
    r"|not exist"
    r"|top out at"
    r"|n20 cites"
    r"|n20 claims"
    r"|wrong anchor"
    r"|wrong section"
    r"|dangling"
    r"|cited as"
    r"|has no §"
    r"|no such"
    r"|DISAGREES"
    r"|cross-reference",
    re.IGNORECASE,
)

# References to sections of OTHER documents. The paper's "ClawsGO #7 §4" and
# "ClawsGO #7 §7" cite the ClawsGO Science Agent's review #7, not the
# paper's own sections - the paper has no §4 and no §7. The existing
# audit_section_refs.py exempts the same pattern; this layer must too, or it
# will report external citations as dangling internal anchors.
EXTERNAL_DOC_REF_RE = re.compile(
    r"ClawsGO\s*#\d+\s*§"
    r"|ClawsGO[^)\n]{0,40}§"
    r"|Technical\s*§"
    r"|T\d+\s*§"
    r"|R\d+\(\d+\)[^)\n]{0,20}§",
    re.IGNORECASE,
)

# Sections of the PAPER that were RETIRED. A reference to one of these is
# STALE, not DANGLING: the heading existed and was removed. Each entry names
# the commit that retired it, so the exemption can be re-audited.
#
# Every entry here is a section that WAS a heading in the paper's history.
# A number that never was a heading must NOT appear here - that is the
# DANGLING class, and admitting it to this list would wave through exactly
# the defect this layer exists to catch.
#
# The paper's stale anchors are a tracked gap (CG-13), not something this
# layer repairs; it reports them and fails only if the set GROWS.
RETIRED_PAPER_SECTIONS = {
    "3.7": "retired in 799f4ef (2026-10-05 R88 paper cleanup); last a "
           "heading at ac1311c (devplan1.docx reviewer refinements)",
    "9.3": "retired in 799f4ef (2026-10-05 R88 paper cleanup); last a "
           "heading at 32d720b (v1.11 -> v1.12)",
    "10.4c": "retired in 10b7552 (2026-10-05 R88 decisive copy-edit); last "
            "a heading at d1a7131",
    "10.4d": "retired in 10b7552 (2026-10-05 R88 decisive copy-edit); last "
            "a heading at df9aadd (v18.40 Path A3 + Path B3 trim)",
    "10.5a": "retired in 3bd4520 (S10.4g.6 dedup + S11 Conclusions + "
             "References stub); last a heading at d1a7131",
    "10.7": "retired in 10b7552 (2026-10-05 R88 decisive copy-edit)",
}

# Maximum number of STALE references the paper may carry. CG-13 was CLOSED on
# 2026-10-26: all 14 retired-section pointers were re-pointed at the sections
# that now hold the content (or dropped, where the content was deleted rather
# than moved). The baseline is therefore ZERO - a single new pointer to a
# retired section fails this layer.
#
# Do NOT raise this to accommodate a new stale reference. It is zero because
# the paper has none; a non-zero reading means an edit re-introduced the defect.
PAPER_STALE_BASELINE = 0


# A citation made external by a marker AFTER the section symbol (e.g.
# "§4 of the supplementary"). Kept separate from the prefix rule so the two
# have visibly different reach.
EXTERNAL_SUFFIX_RE = re.compile(r"^[^\n]{0,40}\bsupplement", re.IGNORECASE)
# How far BEFORE a reference an external marker may sit and still be read as
# belonging to it. A marker further away is a different citation.
EXTERNAL_PREFIX_WINDOW = 55


def is_external_ref(line, off, ref):
    """True when the § at `off` belongs to another document's citation.

    The marker must be adjacent - immediately before the symbol, or within a
    short suffix window after it. A whole-line test would exempt every
    reference on the line, including an unrelated stale one.
    """
    # NB two constraints on this slice, both learned from a failed mutation
    # test:
    #  (a) it INCLUDES the section symbol - every alternative in
    #      EXTERNAL_DOC_REF_RE ends with '§', so a slice stopping short of it
    #      matches nothing and every external citation becomes dangling;
    #  (b) it stops at the PREVIOUS section symbol, so the marker found can
    #      only be the one attached to THIS reference. Without (b) a citation
    #      earlier in the same sentence ("...(ClawsGO #9 §4). See §10.7")
    #      reached forward and exempted the stale reference too.
    prev_ref = line.rfind("\u00a7", 0, off)
    start = max(off - EXTERNAL_PREFIX_WINDOW, prev_ref + 1 if prev_ref >= 0 else 0)
    prefix = line[start:off + 1]
    if EXTERNAL_DOC_REF_RE.search(prefix):
        return True
    suffix = line[off + 1 + len(ref):off + 1 + len(ref) + 45]
    return bool(EXTERNAL_SUFFIX_RE.search(suffix))


def headings(text):
    """Return {section_number: (line_no, title)} for every heading."""
    out = {}
    for m in HEADING_RE.finditer(text):
        out.setdefault(m.group(2).rstrip("."), (text[: m.start()].count("\n") + 1,
                                                 m.group(3)[:70]))
    return out


def scan_refs(text):
    """Yield (line_no, ref, line_text) for every body-text section reference.

    Skips fenced code blocks (a § reference inside a diff hunk is quoted
    source, not a live cross-reference) and heading lines.
    """
    lines = text.split("\n")
    in_fence = False
    for i, line in enumerate(lines, 1):
        if line.strip().startswith("```"):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        if line.lstrip().startswith("#"):
            continue
        for m in SECTION_REF_RE.finditer(line):
            yield (i, m.group(1), line.strip(), m.start())


def audit_doc(path, doc_label, registries, allow_quoted, retired_only):
    """Classify every section reference in one document.

    registries: ordered list of {section: ...} to try, nearest first.
    retired_only: only these section numbers may be classified STALE.
    """
    empty = {"label": doc_label, "path": str(path), "missing_file": True,
             "ok": [], "stale": [], "dangling": [], "quoted": [],
             "external": [], "heading_count": 0}
    if not path.exists():
        return empty
    text = path.read_text(encoding="utf-8")
    own = headings(text)
    res = {"label": doc_label, "path": str(path), "missing_file": False,
           "ok": [], "stale": [], "dangling": [], "quoted": [],
           "external": [], "heading_count": len(own)}
    for line_no, ref, line, off in scan_refs(text):
        if any(ref in reg for reg in registries):
            res["ok"].append((line_no, ref, line))
            continue
        # A reference to another document's section is not a dangling internal
        # anchor. Checked BEFORE the quoted-bad test because an external
        # citation is a legitimate reference, not a quotation of an error.
        #
        # This test is PER REFERENCE, not per line. Testing the whole line made
        # every reference on a line that happened to contain a ClawsGO
        # citation invisible to this layer - so a stale §10.7 appended to such
        # a line passed. The marker that makes a citation external sits
        # immediately BEFORE its own §, so the test is anchored there.
        if is_external_ref(line, off, ref):
            res["external"].append((line_no, ref, line))
            continue
        if allow_quoted and QUOTED_BAD_CONTEXT_RE.search(line):
            res["quoted"].append((line_no, ref, line))
            continue
        if ref in retired_only:
            res["stale"].append((line_no, ref, line))
            continue
        res["dangling"].append((line_no, ref, line))
    return res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", action="store_true",
                    help="emit machine-readable JSON")
    args = ap.parse_args()

    # ---- load the three audited documents --------------------------------
    paths = {"report": REPORT, "companion": COMPANION, "paper": PAPER}
    texts = {k: (p.read_text(encoding="utf-8") if p.exists() else "")
             for k, p in paths.items()}
    H = {k: headings(v) for k, v in texts.items()}

    # ---- per-document resolution scope (see the module docstring) --------
    # The paper resolves against itself ONLY. The paper never cites the
    # report or the companion, and letting it resolve against them is how a
    # real defect gets masked - an earlier draft used a flat union of all
    # three heading sets and silently resolved the paper's "S9.3" against the
    # COMPANION's "S9.3".
    paper = audit_doc(PAPER, "paper", [H["paper"]], allow_quoted=False,
                      retired_only=RETIRED_PAPER_SECTIONS)
    # The report resolves against itself, then the paper (the report is about
    # the paper and cites it constantly), then the companion.
    report = audit_doc(REPORT, "report", [H["report"], H["paper"], H["companion"]],
                       allow_quoted=True, retired_only=RETIRED_PAPER_SECTIONS)
    # The companion resolves against itself, then the paper, then the report.
    companion = audit_doc(COMPANION, "companion",
                          [H["companion"], H["paper"], H["report"]],
                          allow_quoted=True, retired_only=RETIRED_PAPER_SECTIONS)

    # The paper's stale anchors are a tracked gap (CG-13), not a failure - but
    # growth is a failure, because that means a new pointer to a retired
    # section was introduced.
    paper_stale_growth = len(paper["stale"]) > PAPER_STALE_BASELINE

    # RETIRED_PAPER_SECTIONS entries no longer triggered anywhere are dead
    # exemptions: the reference was fixed, so the entry should be removed.
    triggered = {ref for d in (report, companion, paper)
                 for _, ref, _ in d["stale"]}
    dead_exemptions = sorted(set(RETIRED_PAPER_SECTIONS) - triggered)

    total_dangling = (len(report["dangling"]) + len(companion["dangling"])
                      + len(paper["dangling"]))

    out = {
        "report": report, "companion": companion, "paper": paper,
        "paper_stale_baseline": PAPER_STALE_BASELINE,
        "paper_stale_growth": paper_stale_growth,
        "dead_exemptions": dead_exemptions,
        "total_dangling": total_dangling,
    }

    if args.json:
        print(json.dumps(out, indent=2, default=str))
        return 1 if (total_dangling or paper_stale_growth) else 0

    print("=" * 74)
    print("CROSS-DOCUMENT SECTION-ANCHOR AUDIT (gate layer 8)")
    print("=" * 74)
    print(f"Paper   : {PAPER.name}")
    print(f"Report  : {REPORT.name}")
    print(f"Companion: {COMPANION.name}")
    print()
    for res in (report, companion, paper):
        if res.get("missing_file"):
            print(f"  {res['label']:10} MISSING FILE: {res['path']}")
            continue
        print(f"  {res['label']:10} headings={res['heading_count']:3}  "
              f"OK={len(res['ok']):3}  STALE={len(res['stale']):3}  "
              f"EXT={len(res['external']):3}  "
              f"QUOTED-BAD={len(res['quoted']):3}  DANGLING={len(res['dangling']):3}")
    print()
    print(f"Paper stale-anchor baseline: {PAPER_STALE_BASELINE} "
          f"(actual {len(paper['stale'])})"
          + ("  *** GROWTH - FAIL ***" if paper_stale_growth else "  (ok)"))
    print()

    if paper["stale"]:
        print("-" * 74)
        print("STALE references (point to a section that was retired) - reported, "
              "not a failure:")
        print("-" * 74)
        for line_no, ref, line in paper["stale"]:
            print(f"  paper L{line_no} §{ref}: {line[:96]}")
            print(f"      retired: {RETIRED_PAPER_SECTIONS[ref][:88]}")
        print()

    if any(d["external"] for d in (report, companion, paper)):
        print("-" * 74)
        print("EXTERNAL-DOCUMENT references (cite another document's section, "
              "not this one's - exempt):")
        print("-" * 74)
        for res in (report, companion, paper):
            for line_no, ref, line in res["external"]:
                print(f"  {res['label']} L{line_no} §{ref}: {line[:88]}")
        print()

    if report["quoted"] or companion["quoted"]:
        print("-" * 74)
        print("QUOTED-BAD references (the reviewer's wrong anchors, quoted on "
              "purpose - exempt):")
        print("-" * 74)
        for res in (report, companion):
            for line_no, ref, line in res["quoted"]:
                print(f"  {res['label']} L{line_no} §{ref}: {line[:92]}")
        print()

    if dead_exemptions:
        print("-" * 74)
        print("DEAD EXEMPTIONS (RETIRED_PAPER_SECTIONS entries no longer triggered - "
              "re-audit and remove):")
        print("-" * 74)
        for ref in dead_exemptions:
            print(f"  §{ref}: {RETIRED_PAPER_SECTIONS[ref][:90]}")
        print()

    if total_dangling:
        print("-" * 74)
        print(f"DANGLING references - section does not exist and was never "
              f"written ({total_dangling} total). FAIL:")
        print("-" * 74)
        for res in (report, companion, paper):
            for line_no, ref, line in res["dangling"]:
                print(f"  {res['label']} L{line_no} §{ref}: {line[:96]}")
        print()
        print("  Every § reference must resolve to a live heading in the report, "
              "the companion,\n  or the paper - or be a quotation of a known-bad "
              "anchor (the context must\n  negate it explicitly).")
    else:
        print("OK: no DANGLING section references in the report, the companion, "
              "or the paper.")
    print()

    if total_dangling or paper_stale_growth:
        print("RESULT: FAIL")
        return 1
    print("RESULT: PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
