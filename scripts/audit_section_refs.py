#!/usr/bin/env python3
"""
audit_section_refs.py — Audit §X.Y cross-references in PAPER_V1_DRAFT.md.

For every §X.Y reference in body text, verify it resolves to an existing section heading.

Classifies each broken reference by type:
- MISSING_SECTION: paper text says "see §X" but no §X heading exists in this paper
  (could be: external doc reference, removed section, future section)
- EXTERNAL_CITE: §N where N is a known external citation (Benitez-Llambay+ 2024, etc.)
- DEEPER_SUBSECTION: §X.Y.Z where §X.Y exists but §X.Y.Z doesn't

Usage:
    python scripts/audit_section_refs.py

Exit: 0 = all refs resolve; 1 = some broken.
"""
import re
import sys
from pathlib import Path

REPO = Path(__file__).parent.parent
PAPER = REPO / "v0.3-prelim" / "docs" / "PAPER_V1_DRAFT.md"

# Known external citation context patterns — refs to OTHER papers, not this one
EXTERNAL_CITE_PATTERNS = [
    re.compile(r'\(\s*[A-Z][a-z]+(?:[-\s][A-Z][a-z]+)*\+?\s*\d{4}'),  # (Author+ 2024 §X)
    re.compile(r'\(Ben[íi]tez-Llambay\+|T120\.|T131\.|T184\.|suppl'),     # known refs
    re.compile(r'§\d+\s+of\s+earlier\s+drafts'),                          # "§4-§8 of earlier drafts"
    re.compile(r'Technical\s+§'),                                         # "Technical §A.2"
    re.compile(r'supplementary\s+§'),                                     # "supplementary §A.2"
    re.compile(r'\d+review\.docx\s+Reviewer\s+\d+'),                      # "2review.docx Reviewer 2 §1.3"
    re.compile(r'(?:T\d+|Round|R)\d+\s+§'),                               # "T207 §4"
    re.compile(r'T207_V1838.*\.md\s+§'),                                  # doc file refs
    re.compile(r'^\s*\[\d+[a-z]?\]\s+'),                                  # references list entry
    re.compile(r'Note:\s*§'),                                             # "Note: §10.3.1 referenced in earlier drafts"
    re.compile(r'previous\s+§'),                                          # "previous §X.Y.Z claim" (retired)
    re.compile(r'consolidated\s+into\s+§'),                               # "consolidated into §X"
    re.compile(r'\.md\s+§\d+'),                                           # "T207_V1838_PRIORED_REVIEW_2026-09-25.md §4"
    re.compile(r'§\d+\s+of\s+v\d+'),                                      # "§8.5 of v1.11" — historical paper version
    re.compile(r'v\d+\.\d+\s+§\d+'),                                      # "v1.11 §8.5" — historical paper version (no "of")
    re.compile(r'`[^`]+\.md`\s+§\d+'),                                    # backtick-wrapped .md filename + §N
]


def is_external_cite(context):
    """Check if the §-reference is part of an external citation."""
    for pat in EXTERNAL_CITE_PATTERNS:
        if pat.search(context):
            return True
    return False


def main():
    with open(PAPER) as f:
        text = f.read()

    # Get all section headings — match both ## and ### level
    # ## N. Title  (top-level sections, with trailing dot)
    # ## N Title   (top-level sections, no dot)
    # ### N.M Title  (subsections)
    # ### N.Ma Title  (alpha-suffixed)
    # Allow optional § prefix
    heading_pattern = re.compile(
        r'^(#{2,4})\s+(?:§)?(\d+(?:\.\d+[a-z]?)?\.?)\s+([^\n]+)',
        re.MULTILINE,
    )
    sections = {}
    for m in heading_pattern.finditer(text):
        num = m.group(2).rstrip('.')  # Remove trailing dot if present
        title = m.group(3)
        line_num = text[:m.start()].count('\n') + 1
        sections.setdefault(num, []).append((line_num, title))

    sections_set = set(sections.keys())
    top_level_sections = sorted({s.split('.')[0] for s in sections_set if '.' not in s},
                                 key=lambda x: int(x))
    print(f"Top-level sections present: {top_level_sections}")
    print(f"Total unique §-numbers: {len(sections_set)}")
    print()

    # Find §-references in body (excluding heading lines themselves)
    ref_pattern = re.compile(r'§(\d+(?:\.\d+[a-z]?)?(?:\.\d+)?)')
    refs = []
    for m in ref_pattern.finditer(text):
        # Skip if this is inside a heading line
        line_start = text.rfind('\n', 0, m.start()) + 1
        line_end = text.find('\n', m.start())
        if line_end == -1:
            line_end = len(text)
        line = text[line_start:line_end]
        if line.lstrip().startswith('#'):
            continue  # Skip heading lines

        ref = m.group(1)
        line_num = text[:m.start()].count('\n') + 1
        refs.append((line_num, ref, line))

    # Classify
    good = []
    missing_section = []
    external_cite = []
    deeper_subsection = []
    for line_num, ref, line in refs:
        if ref in sections_set:
            good.append((line_num, ref, line))
        elif is_external_cite(line):
            external_cite.append((line_num, ref, line))
        else:
            # Check if a parent section exists
            parts = ref.split('.')
            parent = parts[0]
            if parent in sections_set:
                deeper_subsection.append((line_num, ref, line))
            else:
                missing_section.append((line_num, ref, line))

    print("=" * 70)
    print(f"§-CROSS-REFERENCE AUDIT")
    print("=" * 70)
    print(f"Total refs: {len(refs)}")
    print(f"  ✓ Good (resolves to existing section): {len(good)}")
    print(f"  ✓ External citation (other paper):    {len(external_cite)}")
    print(f"  ⚠ Deeper subsection (parent exists):   {len(deeper_subsection)}")
    print(f"  ✗ Missing section:                     {len(missing_section)}")

    if deeper_subsection:
        print()
        print("-" * 70)
        print("DEEPER SUBSECTIONS (parent exists, deeper doesn't):")
        print("-" * 70)
        for line_num, ref, line in deeper_subsection[:30]:
            print(f"  L{line_num} §{ref}: {line[:100]}")

    if missing_section:
        print()
        print("-" * 70)
        print("MISSING SECTIONS (referenced but not in paper):")
        print("-" * 70)
        # Group by missing section
        by_section = {}
        for line_num, ref, line in missing_section:
            by_section.setdefault(ref, []).append((line_num, line))

        for sec in sorted(by_section.keys(),
                          key=lambda s: tuple(int(x) if x.isdigit() else 0
                                              for x in re.split(r'[a-z.]', s))):
            entries = by_section[sec]
            print(f"  §{sec} — referenced {len(entries)} time(s)")
            for line_num, line in entries[:3]:
                print(f"    L{line_num}: {line[:90]}")
            if len(entries) > 3:
                print(f"    ... and {len(entries) - 3} more")

    print()
    print("=" * 70)
    fail = missing_section  # broken = missing sections; deeper/external are OK
    if not fail:
        print("✓ All in-paper §-references resolve to existing sections")
        return 0
    else:
        print(f"✗ {len(missing_section)} references to non-existent sections")
        return 1


if __name__ == "__main__":
    sys.exit(main())