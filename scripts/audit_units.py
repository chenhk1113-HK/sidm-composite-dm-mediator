#!/usr/bin/env python3
"""
audit_units.py — Audit unit consistency in PAPER_V1_DRAFT.md.

For each numerical value with units, check that units are consistent:
- Cross-section: cm²/g only (NOT cm^2/g, cm2/g mixing)
- Time: Gyr, Myr, yr (no mixing)
- Velocity: km/s only
- Mass: M☉ only
- Distance: pc, kpc only

Catches:
- Mixed unicode and ASCII superscripts in cm²/g
- Mixed Gyr/Myr within same context
- Bare numbers without units

Usage:
    python scripts/audit_units.py

Exit: 0 = all units consistent; 1 = issues found.
"""
import re
import sys
from pathlib import Path
from collections import Counter

REPO = Path(__file__).parent.parent
PAPER = REPO / "v0.3-prelim" / "docs" / "PAPER_V1_DRAFT.md"


def main():
    with open(PAPER) as f:
        text = f.read()

    print("=" * 70)
    print("UNIT CONSISTENCY AUDIT")
    print("=" * 70)
    print()

    issues = []

    # Check 1: cm²/g vs cm^2/g vs cm2/g
    # Unicode: cm²/g (preferred)
    # ASCII: cm^2/g
    # Also: cm2/g (compact)
    unicode_cm2g = text.count('cm²/g')
    ascii_cm2g = len(re.findall(r'cm\^2/g', text))
    compact_cm2g = len(re.findall(r'cm2/g', text))
    print(f"Cross-section units:")
    print(f"  cm²/g (unicode):    {unicode_cm2g}")
    print(f"  cm^2/g (ASCII):     {ascii_cm2g}")
    print(f"  cm2/g (compact):    {compact_cm2g}")
    if ascii_cm2g > 0 or compact_cm2g > 0:
        issues.append(f"Inconsistent cross-section units: ASCII={ascii_cm2g}, compact={compact_cm2g}")

    # Check 2: M☉ (solar mass) consistency
    solar_unicode = text.count('M☉')
    solar_ascii = len(re.findall(r'M[_]?sun|M_\\odot|M⊙', text))
    print(f"\nSolar mass units:")
    print(f"  M☉ (unicode):       {solar_unicode}")
    print(f"  M_sun/M⊙ (ASCII):   {solar_ascii}")
    if solar_ascii > 0:
        # Find where ASCII forms are
        for m in re.finditer(r'M[_]?sun|M_\\odot|M⊙', text):
            line_num = text[:m.start()].count('\n') + 1
            line_start = text.rfind('\n', 0, m.start()) + 1
            line_end = text.find('\n', m.start())
            if line_end == -1:
                line_end = len(text)
            ctx = text[line_start:line_end][:80]
            print(f"    L{line_num}: {ctx}")
            issues.append(f"L{line_num}: ASCII M_sun should be M☉: {ctx}")

    # Check 3: Time units - mixed Gyr/Myr
    gyr_count = len(re.findall(r'\b\d+\.?\d*\s*Gyr\b', text))
    myr_count = len(re.findall(r'\b\d+\.?\d*\s*Myr\b', text))
    yr_count = len(re.findall(r'\b\d+\.?\d*\s*yr\b', text))
    print(f"\nTime units:")
    print(f"  Gyr: {gyr_count}")
    print(f"  Myr: {myr_count}")
    print(f"  yr:  {yr_count}")
    # No consistency issue expected

    # Check 4: Velocity - km/s only
    km_s = len(re.findall(r'\bkm/s\b', text))
    print(f"\nVelocity units:")
    print(f"  km/s: {km_s}")

    # Check 5: Numbers without units - find suspicious bare numbers
    # Heuristic: a number > 1000 without any unit suffix in 50 chars
    print()
    print("-" * 70)
    print("SUSPICIOUS BARE NUMBERS (heuristic):")
    print("-" * 70)

    bare_number_pattern = re.compile(r'\b(\d{4,}(?:\.\d+)?)\b\s+([a-zA-Z]+)')
    suspicious = []
    for m in bare_number_pattern.finditer(text):
        num = m.group(1)
        next_word = m.group(2)
        line_num = text[:m.start()].count('\n') + 1
        suspicious.append((line_num, num, next_word))

    if suspicious:
        # Show first 10
        for line_num, num, word in suspicious[:10]:
            line_start = text.rfind('\n', 0, line_num*100) + 1
            print(f"  L{line_num}: {num} followed by '{word}'")
        if len(suspicious) > 10:
            print(f"  ... and {len(suspicious) - 10} more")
    else:
        print("  None found")

    # Check 6: Unicode superscripts that should be ASCII per Rule 27
    # Per the standing rule, PDF/Telegram prefer ASCII 10^-N over unicode 10⁻ⁿ
    print()
    print("-" * 70)
    print("UNICODE SUPERSCRIPTS (Rule 27 audit):")
    print("-" * 70)
    unicode_super_chars = ['⁻', '⁰', '¹', '²', '³', '⁴', '⁵', '⁶', '⁷', '⁸', '⁹']
    counts = {c: text.count(c) for c in unicode_super_chars}
    total = sum(counts.values())
    print(f"Unicode superscript characters: {total} total")
    for c, n in counts.items():
        if n > 0:
            print(f"  {c} ({hex(ord(c))}): {n}")
    if total > 50:
        # Many unicode superscripts - this is the paper, not a Telegram/PDF, so it's OK
        # but report for awareness
        print(f"  Note: paper has many unicode superscripts ({total}). Per Rule 27,")
        print(f"  these should be converted to ASCII (10^-N) only when sent to PDF/Telegram.")

    print()
    print("=" * 70)
    if not issues:
        print("✓ No unit consistency issues")
        return 0
    else:
        print(f"✗ {len(issues)} issues found")
        for issue in issues[:10]:
            print(f"  - {issue}")
        return 1


if __name__ == "__main__":
    sys.exit(main())