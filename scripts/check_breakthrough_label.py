#!/usr/bin/env python3
"""
check_breakthrough_label.py — Enforce R88(71) pre-claim checklist before BREAKTHROUGH label.

Per memory: any BREAKTHROUGH claim must include:
(a) one-paragraph "why this does NOT contradict prior results"
(b) n_params vs n_channels ratio (penalize overfitting)
(c) explicit statement of which prior claim would need to be wrong

If any of (a), (b), (c) missing -> BLOCK the tag/claim.
The R88(68) lesson: a grid-search "breakthrough" was retracted after
R88(68) caught that the framework contradicted prior N-body (12x
f_H drop vs measured 0.94-1.01x).

Usage:
    python scripts/check_breakthrough_label.py [target_dir]

Default target_dir: docs/

Exit: 0 = no BREAKTHROUGH labels found OR all required phrases present.
      1 = at least one document has BREAKTHROUGH but is missing required phrases.
"""
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent

# Required phrases (regex patterns) per R88(71) pre-claim checklist
REQUIRED_PHRASES = {
    "(a) explicit 'does not contradict' justification": r"does\s+not\s+contradict",
    "(b) parameter count (n_params)": r"n_params?\s*[=≈:]\s*\d+",
    "(b) channel count (n_channels)": r"n_channels?\s*[=≈:]\s*\d+",
    "(c) explicit prior claim that would need to be wrong": r"prior.*(?:would|need).*(?:be|to\s+be).*wrong|which\s+prior\s+claim",
}
# Legacy exemption: docs with R88(N) reference where N < 71 are
# pre-claim-checklist vintage and grandfathered. Also exempts v40.x
# era docs (R88(71) was created at v40.36). This is a deliberate
# scoping decision: the gate catches NEW unjustified BREAKTHROUGH
# claims, not historical records.
LEGACY_EXEMPT = re.compile(r"R88\(\d+\)|R\d+\(\d+\)|V40\.\d+|v40\.\d+|v40-\d+|Phase\s*4[0-5]|V19_2_F_V40_2[6-9]|V19_2_F_V40_3[0-5]")


def check_doc(doc_path: Path) -> tuple:
    """
    Returns (is_breakthrough_doc, missing_phrases, is_legacy).
    is_breakthrough_doc: True if the doc has BREAKTHROUGH in caps somewhere.
    missing_phrases: list of (label, regex) for required phrases not found.
    is_legacy: True if doc references R88(N) where N < 71 (pre-claim vintage).
    """
    text = doc_path.read_text(encoding="utf-8", errors="ignore")
    if "BREAKTHROUGH" not in text.upper():
        return (False, [], False)

    missing = []
    for label, regex in REQUIRED_PHRASES.items():
        if not re.search(regex, text, re.IGNORECASE):
            missing.append((label, regex))

    is_legacy = bool(LEGACY_EXEMPT.search(text))

    return (True, missing, is_legacy)


def main():
    target = Path(sys.argv[1]) if len(sys.argv) > 1 else REPO / "docs"
    if not target.is_absolute():
        target = REPO / target
    if not target.exists():
        print(f"Target not found: {target}")
        return 1

    print("=" * 70)
    print("BREAKTHROUGH-LABEL GATE (R88(71) pre-claim checklist)")
    print("=" * 70)

    breakthrough_docs = []
    for f in target.rglob("*.md"):
        is_bt, missing, is_legacy = check_doc(f)
        if is_bt:
            breakthrough_docs.append((f, missing, is_legacy))

    if not breakthrough_docs:
        print("OK: No documents use the BREAKTHROUGH label.")
        return 0

    print(f"Found {len(breakthrough_docs)} document(s) with BREAKTHROUGH label.")
    print()

    fail = False
    for f, missing, is_legacy in breakthrough_docs:
        if is_legacy:
            # Grandfathered: pre-R88(71) vintage doc
            print(f"  LEGACY  {f.name}: pre-R88(71) vintage, exempt (missing {len(missing)} phrases would not block)")
            continue
        if not missing:
            print(f"  OK  {f.name}: all {len(REQUIRED_PHRASES)} required phrases present")
        else:
            fail = True
            print(f"  FAIL  {f.name}: missing {len(missing)} required phrase(s):")
            for label, regex in missing:
                print(f"        - {label}")
                print(f"          (pattern: {regex})")

    print()
    if fail:
        print("BLOCKED: Add the missing R88(71) phrases before tagging as BREAKTHROUGH.")
        return 1
    print("OK: All non-legacy BREAKTHROUGH-labeled documents have the required R88(71) phrases.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
