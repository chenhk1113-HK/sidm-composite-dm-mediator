#!/usr/bin/env python3
"""
audit_citation_provenance.py — Check citation [N] provenance in PAPER_V1_DRAFT.md.

For every [N] citation in the paper:
1. Verify it appears in the References section
2. Flag any [N] that's used in body but missing from references
3. Flag any reference entry that's never cited in body

Usage:
    python scripts/audit_citation_provenance.py

Exit: 0 = all citations resolve; 1 = orphaned or missing citations.
"""
import re
import sys
from pathlib import Path

REPO = Path(__file__).parent.parent
PAPER = REPO / "v0.3-prelim" / "docs" / "PAPER_V1_DRAFT.md"


def main():
    with open(PAPER) as f:
        text = f.read()

    # Find References section start
    ref_section_match = re.search(r'^## References\s*$', text, re.MULTILINE)
    if not ref_section_match:
        print("ERROR: Could not find References section")
        return 1

    ref_start = ref_section_match.start()
    body_text = text[:ref_start]
    ref_text = text[ref_start:]

    # Body citations — match [N] where N is 1-3 digit number, optionally followed by lowercase letter
    # [15], [15a], [49b]
    # Exclude [0] which is a Python array index (v_target[0], sigma[0], etc.)
    body_cite_pattern = re.compile(r'\[(\d+[a-z]?)\]')
    body_cites = body_cite_pattern.findall(body_text)
    # Filter out [0] and other single-digit low numbers that are likely array indices
    # Use heuristic: if preceded by alphanumeric or underscore, it's an array index
    real_cites = []
    for cite in body_cites:
        # Find the match position
        for m in re.finditer(rf'\[{re.escape(cite)}\]', body_text):
            # Check character before
            if m.start() > 0 and body_text[m.start()-1] in 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ_':
                continue  # Array index, skip
            real_cites.append(cite)
            break
    body_cites = real_cites
    body_cite_set = set(body_cites)
    print(f"Body citations: {len(body_cite_set)} unique, {len(body_cites)} total")
    print()

    # Reference entries — match `[N]` or `[Na]` at start of line
    ref_pattern = re.compile(r'^\[(\d+[a-z]?)\]', re.MULTILINE)
    ref_entries = ref_pattern.findall(ref_text)
    ref_set = set(ref_entries)
    print(f"Reference entries: {len(ref_set)} unique")
    print()

    # Classify
    missing_from_refs = body_cite_set - ref_set
    orphan_refs = ref_set - body_cite_set

    print("=" * 70)
    print(f"CITATION PROVENANCE AUDIT")
    print("=" * 70)

    if missing_from_refs:
        print(f"⚠ Citations used in body but MISSING from References ({len(missing_from_refs)}):")
        for cite in sorted(missing_from_refs, key=lambda c: (int(re.match(r'\d+', c).group()), c)):
            # Find first body usage
            first_use = re.search(rf'\[{re.escape(cite)}\]', body_text)
            if first_use:
                line_num = body_text[:first_use.start()].count('\n') + 1
                # Get context
                line_start = body_text.rfind('\n', 0, first_use.start()) + 1
                line_end = body_text.find('\n', first_use.start())
                ctx = body_text[line_start:line_end][:100]
                print(f"  [{cite}] (first used L{line_num}): {ctx}")
        print()
    else:
        print("✓ All body citations resolve to References entries")

    if orphan_refs:
        print(f"⚠ Reference entries NEVER CITED in body ({len(orphan_refs)}):")
        for cite in sorted(orphan_refs, key=lambda c: (int(re.match(r'\d+', c).group()), c)):
            # Find reference entry
            m = re.search(rf'^\[{re.escape(cite)}\][^\n]+', ref_text, re.MULTILINE)
            if m:
                line_num = ref_text[:m.start()].count('\n') + 1 + ref_start_pos
                entry = m.group(0)[:120]
                print(f"  [{cite}]: {entry}")
        print()
    else:
        print("✓ All Reference entries are cited in body")

    print()
    fail = missing_from_refs  # Orphan refs are notes, not errors
    if not fail:
        print("✓ No missing citations")
        return 0
    else:
        print(f"✗ {len(fail)} missing citations")
        return 1


if __name__ == "__main__":
    # Add ref_start_pos to fix scoping issue
    PAPER = Path(__file__).parent.parent / "v0.3-prelim" / "docs" / "PAPER_V1_DRAFT.md"
    with open(PAPER) as f:
        text = f.read()
    ref_section_match = re.search(r'^## References\s*$', text, re.MULTILINE)
    ref_start_pos = ref_section_match.start() if ref_section_match else 0
    sys.exit(main())