#!/usr/bin/env python3
"""
verify_numbers_in_paper.py — Cross-validate PAPER_STANDING_NUMBERS.md against PAPER_V1_DRAFT.md.

For every numbered claim in the standing-numbers table, check that the number appears in the
paper at least once. For each "MUST NOT appear" item, verify the paper does NOT contain it.

This is the Round-12 cross-validation pass per devplan1.docx.

Usage:
    python scripts/verify_numbers_in_paper.py

Exit: 0 = all pass; 1 = missing numbers or forbidden numbers found.
"""
import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).parent.parent
PAPER = REPO / "v0.3-prelim" / "docs" / "PAPER_V1_DRAFT.md"


def load_paper():
    with open(PAPER) as f:
        return f.read()


def main():
    paper = load_paper()

    # Required numbers — must appear in paper
    required = [
        # §1 Observational anchors
        ("Cloud-9 σ/m floor", "50 cm", "σ/m ≥ 50 cm²/g or σ/m ≥ 50 cm/g in paper"),
        ("dSph σ/m ceiling", "0.8 cm", "dSph σ/m ≲ 0.8 cm²/g"),
        ("SPARC σ/m target", "0.193", "SPARC σ/m ≈ 0.193"),
        ("Cluster σ/m ceiling", "0.1 cm", "cluster σ/m ceiling"),

        # §2 Channel coverage
        ("Channel borrowed pass", "6 of 8 or 6 / 8 or 6/8", "borrowed mode 6/8"),
        ("Channel priored free fail", "-2.03", "SPARC log L ≈ -2.03 or -2.0"),

        # §3 Path F1
        ("Path F1 v_HL borrowed", "100.61 or 100 km", "v_HL ≈ 100.61 or 100 km/s"),
        ("Path F1 σ_HL peak", "0.343 or 0.34", "σ_HL peak ≈ 0.343 or 0.34"),
        ("Path F1 yang f_H", "0.45", "yang f_H ≈ 0.45"),

        # §4 Statistics
        ("Bayes log B", "2.411", "Bayes log B = 2.411 or ≈ 2.411"),
        ("Bayes B factor", "11.149 or 11.15 or ≈ 11", "Bayes B = 11.149 or ≈ 11"),
        ("BIC penalty", "+3.22", "ΔBIC = +3.22 or BIC +3.22"),

        # §5 Cloud-9 host
        ("Cloud-9 M_halo", "5×10⁹ or 5e9 or 5 × 10⁹", "5×10⁹ M☉"),
        ("Cloud-9 concentration", "12", "concentration c = 12"),
        ("Cloud-9 t_core Phase 44", "73.71 or 73.7 Gyr", "t_core ≈ 73.7 Gyr or 73.71"),
        ("Hubble time", "13.8 Gyr", "t_Hubble = 13.8 Gyr"),

        # §6 Silverman+ T212
        ("Silverman threshold", "1.0 cm²/g or 1 cm²/g", "Silverman+ threshold"),
        ("T212 t_core at σ/m=70", "0.176 Gyr or 176 Myr", "t_core ≈ 176 Myr or 0.176 Gyr"),
        ("T212 causality", "FALS", "causality violation or Cloud-9 violation"),

        # §7 KK tower T213
        ("KK tower σ/m", "0.174", "σ/m ≈ 0.174 or 0.17 cm²/g"),
        ("KK tower ratio", "5.7", "5.7× below Silverman+"),

        # §8 No-gos
        ("LZ direct detection no-go", "REFUTED", "LZ no-go verdict"),
        ("Kinematic forbiddance", "REFUTED", "kinematic no-go"),
        ("Unitarity violation", "REFUTED", "unitarity no-go"),
        ("Flat velocity dependence", "REFUTED", "flat velocity no-go"),

        # §9 Drobczyk
        ("Drobczyk Ωh²", "0.1187 or 0.119", "Ωh² = 0.1187 or 0.119"),
        ("Drobczyk delta", "0.43", "δ = 0.43%"),

        # §10 KiSS methods
        ("T215u mean Myr", "69.57", "mean 69.57 or 69.57 Myr"),
        ("T215u std Myr", "0.74", "std 0.74"),
        ("T215r mean Myr", "41.85", "uncapped mean 41.85 or ≈ 41.85"),
        ("T215r std Myr", "21.13", "uncapped std 21.13"),
        ("ulimit cap", "ulimit", "ulimit -v in paper"),
        ("Std reduction factor", "28×", "28× or 28x variance reduction"),
        ("Range reduction", "46×", "46× range reduction"),

        # §11 Qualitative signature
        ("Interior up ratio", "1.76", "1.76× or 1.76-2.99× interior up"),
        ("Outer down ratio", "0.34", "0.34-0.63× outer down or 0.34"),
    ]

    # Forbidden phrases — MUST NOT appear (strict regex, not loose match)
    forbidden = [
        ("'6-7 of 8'", r"6[–-]7\s+of\s+8"),
        ("'Cloud-9 t_core measured'", r"t_core\s+(?:was|has\s+been|is|are)\s+measured"),
        ("'multi-resonance BIC-favored'", r"multi-resonance.*BIC.favored"),
        ("'KiSS-SIDM runs are deterministic'", r"KiSS-SIDM.*runs?\s+are\s+deterministic|runs?\s+are\s+deterministic.*KiSS"),
        ("'first-principles f_H from N-body'", r"first.principles.*f_H.*from.*N.body"),
        # Note: "Cloud-9 tension" is OK; only flag "tension is RESOLVED" / "is now resolved" / "we resolved"
        ("'Cloud-9 tension resolved (positive)'", r"Cloud.9.*tension.*(is|has\s+been|was)\s+(?:now\s+)?resolved"),
        ("'8/8 channel pass as headline'", r"8\s*/\s*8.*(?:headline|all\s+channels\s+pass)"),
    ]

    # Allow unicode superscript and ASCII forms of "10^-N"
    # The paper text might use "10⁹" or "10^9"

    print("=" * 70)
    print("ROUND 12 CROSS-VALIDATION: PAPER_STANDING_NUMBERS ↔ PAPER_V1_DRAFT.md")
    print("=" * 70)
    print()

    required_pass = 0
    required_fail = []
    for name, marker, note in required:
        # Handle "or" patterns
        if " or " in marker:
            options = [m.strip() for m in marker.split(" or ")]
            found = any(opt in paper for opt in options)
        else:
            found = marker in paper
        if found:
            required_pass += 1
            print(f"  ✓ {name:35s} ({note})")
        else:
            required_fail.append((name, marker))
            print(f"  ✗ {name:35s} MISSING — expected '{marker}' ({note})")

    print()
    print(f"REQUIRED: {required_pass}/{len(required)} pass")

    print()
    print("-" * 70)
    print("FORBIDDEN PHRASES (must NOT appear):")
    print("-" * 70)

    forbidden_pass = 0
    forbidden_fail = []
    for name, regex in forbidden:
        match = re.search(regex, paper, re.IGNORECASE)
        if match:
            # Get context
            start = max(0, match.start() - 30)
            end = min(len(paper), match.end() + 30)
            context = paper[start:end].replace("\n", " ")
            forbidden_fail.append((name, regex, context))
            print(f"  ✗ {name:40s} FOUND — context: ...{context}...")
        else:
            forbidden_pass += 1
            print(f"  ✓ {name:40s} NOT FOUND")

    print()
    print(f"FORBIDDEN: {forbidden_pass}/{len(forbidden)} pass (0 expected to appear)")

    print()
    print("=" * 70)
    print(f"VERDICT: {len(required_fail) + len(forbidden_fail)} issues found")
    if not required_fail and not forbidden_fail:
        print("✓ All cross-validation checks pass")
    else:
        if required_fail:
            print(f"  Required missing: {len(required_fail)}")
            for name, marker in required_fail:
                print(f"    - {name}: expected '{marker}'")
        if forbidden_fail:
            print(f"  Forbidden found: {len(forbidden_fail)}")
            for name, regex, ctx in forbidden_fail:
                print(f"    - {name}: {ctx}")

    return 0 if (not required_fail and not forbidden_fail) else 1


if __name__ == "__main__":
    sys.exit(main())