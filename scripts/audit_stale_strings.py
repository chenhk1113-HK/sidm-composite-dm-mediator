#!/usr/bin/env python3
"""
audit_stale_strings.py — Gate layer 13: resurrected stale values in the paper.

WHY THIS EXISTS
---------------
Tracked gap **CG-2** in the consolidated report states the problem exactly:

  "A resurrected stale value in the prose (a value that a later fix removed,
   reintroduced by a later edit) — this is exactly how the invalid `ef645ce`
   commit passed the gate: it reintroduced `-0.47`, `0.5–2.5 cm²/g` and
   `7 of 8` and the gate said ALL GATES PASSED."

Every existing layer validates the claims it enumerates; none asserts the
ABSENCE of values the project has already retired. Layer 10 asserts absence
for one family (the F23 hierarchy chain). This layer covers the CLASS:
any value recorded in docs/STALE_STRINGS.json must not appear in the paper's
prose without an explicit retraction marker nearby.

Design (per n21 review item 6, which asked for exactly this lightweight layer):

  1. Registry: docs/STALE_STRINGS.json — one entry per documented stale-value
     finding, with the exact string variants, provenance, and an optional
     per-entry allow_regex.
  2. A hit is ALLOWED when the line it appears on also matches the entry's
     allow_regex (retraction vocabulary: retracted / legacy / placeholder /
     not the / was based on ...). The paper legitimately cites retracted
     values when explaining the retraction; the layer forbids the UNMARKED
     reappearance, not the discussion.
  3. Matching is normalised (en/em dashes -> '-', Unicode superscripts ->
     ASCII, cm² -> cm2, ×10 -> e, e+ -> e) with numeric boundary guards, so
     the Unicode and ASCII forms of the same stale value are one entry.

MUTATION-VERIFIED (project convention for every gate layer):
  - injecting "the value -0.47 and the band 0.5–2.5 cm²/g; ... 7 of 8" into a
    scratch copy of the paper without retraction markers -> exit 1;
  - the pristine paper -> exit 0.

Usage:
    python scripts/audit_stale_strings.py
    python scripts/audit_stale_strings.py --json
    python scripts/audit_stale_strings.py --paper <path>   # for mutation tests

Exit: 0 = no unmarked stale string in the paper; 1 = at least one violation.
"""
import argparse
import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
REGISTRY = REPO / "docs" / "STALE_STRINGS.json"

SUPERSCRIPT_MAP = {
    "⁻": "-", "⁰": "0", "¹": "1", "²": "2", "³": "3",
    "⁴": "4", "⁵": "5", "⁶": "6", "⁷": "7", "⁸": "8", "⁹": "9",
}
DASHES = ["–", "—", "‑", "−"]  # en, em, non-breaking, minus


def normalize(text: str) -> str:
    """Fold Unicode scientific typography to the ASCII canonical form."""
    out = text
    for d in DASHES:
        out = out.replace(d, "-")
    out = "".join(SUPERSCRIPT_MAP.get(ch, ch) for ch in out)
    out = out.replace("×10", "e").replace("x 10", "e").replace("x10", "e")
    out = out.replace("10^", "e").replace("^", "")
    out = out.replace("e+", "e")
    out = re.sub(r"\s+", " ", out)
    return out


def variant_regex(variant_norm: str) -> re.Pattern:
    """Exact match with numeric boundary guards so '-0.47' cannot match
    inside '-0.474' and '7 of 8' cannot match inside '17 of 8'."""
    prefix = r"(?<![\d.])" if variant_norm[:1].isdigit() else ""
    suffix = r"(?![\d])" if variant_norm[-1:].isdigit() else ""
    return re.compile(prefix + re.escape(variant_norm) + suffix)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--paper", default=None,
                    help="override the paper path (mutation tests)")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
    entries = registry.get("entries", [])
    if not entries:
        print("FAIL: registry has no entries — the layer cannot prove anything")
        return 1
    default_allow = re.compile(registry["default_allow_regex"])
    paper = Path(args.paper) if args.paper else REPO / registry["paper"]
    if not paper.exists():
        print(f"FAIL: paper not found: {paper}")
        return 1
    lines = paper.read_text(encoding="utf-8").splitlines()

    violations, allowed_hits, clean_hits = [], 0, 0
    for entry in entries:
        allow = re.compile(entry.get("allow_regex", registry["default_allow_regex"]))
        for variant in entry["variants"]:
            rx = variant_regex(normalize(variant))
            for i, raw in enumerate(lines, 1):
                if rx.search(normalize(raw)):
                    if allow.search(raw):
                        allowed_hits += 1          # legit retraction discussion
                    else:
                        violations.append({
                            "id": entry["id"],
                            "variant": variant,
                            "line": i,
                            "excerpt": raw.strip()[:160],
                            "why_stale": entry["why_stale"],
                        })
                        clean_hits += 1

    report = {
        "paper": str(paper),
        "registry_entries": len(entries),
        "variants": sum(len(e["variants"]) for e in entries),
        "allowed_retraction_context_hits": allowed_hits,
        "violations": violations,
        "verdict": "FAIL" if violations else "PASS",
    }

    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print(f"Stale-string audit — registry {report['registry_entries']} entries / "
              f"{report['variants']} variants; paper: {paper.name}")
        print(f"  hits in retraction context (allowed): {allowed_hits}")
        if violations:
            print(f"  VIOLATIONS ({len(violations)}):")
            for v in violations:
                print(f"    [{v['id']}] '{v['variant']}' at line {v['line']}: {v['excerpt']}")
            print("VERDICT: FAIL — a retired value reappeared without a retraction marker")
            return 1
        print("VERDICT: PASS — no unmarked stale string from the registry appears in the paper")
        return 0


if __name__ == "__main__":
    sys.exit(main())
