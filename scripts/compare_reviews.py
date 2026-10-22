#!/usr/bin/env python3
"""
compare_reviews.py — Compare two independent reviewer outputs on the same artifact
and surface the disagreements, which are the claims worth computing first.

WHY
---
Two reviewers looking at the same draft fail differently. The AGREEMENT is
reassuring but weakly informative (they may share a blind spot). The
DISAGREEMENT is the high-value signal: a number or a verdict that one reviewer
accepts and the other rejects is exactly where a silent error lives.

This script does NOT judge either review. It extracts:
  - the tagged findings ([ERR] / [Q] / [OK]) from each review
  - the distinct NUMBERS each reviewer cites
  - the numbers only one reviewer mentions
  - verdicts/claims where the two reviewers differ in stance

and prints a consolidated brief. The controller then COMPUTES the contested
numbers in Python -- that step is not optional and is not automated here,
because judging a physics claim is the controller's job, not a regex's.

USAGE
-----
    python compare_reviews.py --a docs/NEMOTRON_REVIEW_X.md \\
                              --b docs/OPENCODE_REVIEW_X.md
    python compare_reviews.py --a <file> --b <file> --json
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

# Numbers that appear in almost every physics review and carry no signal.
BOILERPLATE = {
    "0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10",
    "100", "1000", "2024", "2025", "2026",
}

# Lines that are provenance/metadata, not claims. Their numbers (durations,
# HTTP codes, delegation ids, line numbers) must not be read as physics claims.
METADATA_LINE_RE = re.compile(
    r"^\s*(\*\*|[-*]|\||#|>)?\s*"
    r"(model|generated|duration|transport|reviewer role|prompt source|status|"
    r"attempt log|delegation id|priority chain|reviews?|result|verdict|"
    r"\*\*status|\|)",
    re.IGNORECASE,
)
# Metadata-ish lines to drop before number extraction.
META_DROP_RE = re.compile(
    r"(HTTP\s*40[0-9]|OpenRouter|opencode run|deleg_[0-9a-f]{6,}|"
    r"\bses_[0-9a-z]+\b|\bprt_[0-9a-f]+\b|\bmsg_[0-9a-f]+\b|"
    r"\*\*Duration|\*\*Generated|\*\*Model|\*\*Transport|\*\*Reviewer role|"
    r"\*\*Prompt source|\*\*Delegation|\|\s*`?opencode/|\|\s*`?nvidia/|"
    r"^\s*\|\s*Model\s*\|)",
    re.IGNORECASE | re.MULTILINE,
)

# Tag patterns. The prompt convention is [ERR] / [Q] / [OK]; the older Nemotron
# docs use "KEY FINDINGS:" + "REVISED ... VERDICT" prose, so both are handled.
# The tag may be wrapped in markdown bold: **[ERR]**. Nemotron emits that form;
# without the optional ** the parser silently reported "0 findings" for its reviews.
TAG_RE = re.compile(r"^\s*(?:[-*•]\s*)?(?:\*\*)?\[(ERR|Q|OK|HIGH|MED|LOW|CRITICAL)\](?:\*\*)?\s*(.*)$",
                    re.IGNORECASE)
FINDING_RE = re.compile(r"^\s*(?:\d+[.)]\s*)?(?:\*\*)?(CRITICAL|HIGH|MEDIUM|LOW)\b[:\s]",
                        re.IGNORECASE)

# A number with optional sign, optional exponent, optional leading decimal.
NUM_RE = re.compile(r"[-+]?\d+(?:\.\d+)?(?:[eE][-+]?\d+)?")
# Numbers that carry a unit suffix are more physically meaningful.
NUM_UNIT_RE = re.compile(
    r"[-+]?\d+(?:\.\d+)?(?:[eE][-+]?\d+)?\s*"
    r"(?:%|Gyr|Myr|yr|km/s|cm²|cm\^2|cm2|pb|GeV|MeV|keV|ev|eV|"
    r"M☉|Msun|M_sun|kpc|Mpc|pc|dex|s\b)"
)


def read(path: str) -> str:
    return Path(path).read_text(encoding="utf-8", errors="replace")


def strip_code_fences(text: str) -> str:
    """Drop fenced code blocks -- they contain example numbers, not claims."""
    out, in_fence = [], False
    for line in text.splitlines():
        if line.strip().startswith("```"):
            in_fence = not in_fence
            continue
        if not in_fence:
            out.append(line)
    return "\n".join(out)


def strip_metadata(text: str) -> str:
    """Drop provenance lines (durations, ids, HTTP codes, attempt tables).

    Their numbers are bookkeeping, not physics claims. Without this, a 23.18s
    review duration and a 403 error code show up in the "numbers only one
    reviewer cited" list and dilute the real signal.
    """
    body = strip_code_fences(text)
    kept = []
    for line in body.splitlines():
        if META_DROP_RE.search(line):
            continue
        if METADATA_LINE_RE.match(line) and "[" not in line[:12]:
            continue
        kept.append(line)
    return "\n".join(kept)


def extract_findings(text: str) -> list[dict]:
    """Pull tagged findings out of a review body."""
    findings: list[dict] = []
    for i, line in enumerate(strip_code_fences(text).splitlines()):
        m = TAG_RE.match(line)
        if m:
            findings.append({"tag": m.group(1).upper(), "text": m.group(2).strip(),
                             "line": i + 1})
            continue
        m2 = FINDING_RE.match(line)
        if m2:
            findings.append({"tag": m2.group(1).upper(), "text": line.strip(),
                             "line": i + 1})
    return findings


def extract_numbers(text: str) -> set[str]:
    """Distinct numeric literals, normalised, with unit-bearing ones flagged."""
    body = strip_metadata(text)
    nums: set[str] = set()
    for m in NUM_RE.finditer(body):
        raw = m.group(0)
        try:
            val = float(raw)
        except ValueError:
            continue
        if val == int(val) and abs(val) < 1e15:
            norm = str(int(val))
        else:
            norm = f"{val:.6g}"
        if norm in BOILERPLATE:
            continue
        nums.add(norm)
    return nums


def extract_verdicts(text: str) -> list[str]:
    """Verdict-like sentences: the claims a second reviewer would contradict."""
    verdicts = []
    for line in strip_code_fences(text).splitlines():
        s = line.strip()
        low = s.lower()
        if not s or len(s) < 25:
            continue
        if any(k in low for k in (
            "verdict", "structural", "known artifact", "artifact", "no-go",
            "is consistent", "is inconsistent", "contradict", "overclaim",
            "over-claim", "genuine constraint", "not a real constraint",
            "supports", "does not support", "well within", "in tension",
            "excluded", "tension", "recommend",
        )):
            verdicts.append(s[:400])
    return verdicts


def verdict_stance(sentence: str) -> str:
    """Coarse polarity: does the sentence assert, deny, or hedge?"""
    low = sentence.lower()
    deny = ("not a real", "no-go", "overclaim", "over-claim", "contradict",
            "does not", "is not", "inconsistent", "incorrect", "wrong",
            "cannot", "artifact")
    affirm = ("is a real", "genuine", "structural", "consistent", "supports",
              "excluded", "tension", "recommend", "is correct")
    if any(k in low for k in deny):
        return "NEG"
    if any(k in low for k in affirm):
        return "POS"
    return "NEU"


def compare(a_text: str, b_text: str, a_name: str, b_name: str) -> dict:
    a_f, b_f = extract_findings(a_text), extract_findings(b_text)
    a_n, b_n = extract_numbers(a_text), extract_numbers(b_text)
    a_v, b_v = extract_verdicts(a_text), extract_verdicts(b_text)

    only_a = sorted(a_n - b_n)
    only_b = sorted(b_n - a_n)
    shared = sorted(a_n & b_n)

    # Which numbers appear in one review with a unit suffix but not the other?
    def unit_numbers(t: str) -> set[str]:
        return {m.group(0).strip() for m in NUM_UNIT_RE.finditer(strip_metadata(t))}

    a_u, b_u = unit_numbers(a_text), unit_numbers(b_text)

    # Stance conflicts: same key phrase, opposite polarity.
    a_st = {s: verdict_stance(s) for s in a_v}
    b_st = {s: verdict_stance(s) for s in b_v}
    conflicts = []
    for sa, pa in a_st.items():
        for sb, pb in b_st.items():
            key_a = set(re.findall(r"[a-z_]{6,}", sa.lower()))
            key_b = set(re.findall(r"[a-z_]{6,}", sb.lower()))
            overlap = key_a & key_b
            if len(overlap) >= 2 and pa != pb and "NEU" not in (pa, pb):
                conflicts.append({"topic": sorted(overlap)[:6], "a": sa[:220],
                                  "b": sb[:220], "a_stance": pa, "b_stance": pb})

    return {
        "reviewer_a": a_name, "reviewer_b": b_name,
        "a_findings": a_f, "b_findings": b_f,
        "a_finding_count": len(a_f), "b_finding_count": len(b_f),
        "a_severity_counts": count_tags(a_f), "b_severity_counts": count_tags(b_f),
        "numbers_shared": shared,
        "numbers_only_a": only_a, "numbers_only_b": only_b,
        "unit_numbers_only_a": sorted(a_u - b_u)[:20],
        "unit_numbers_only_b": sorted(b_u - a_u)[:20],
        "verdict_conflicts": conflicts[:10],
        "a_verdict_count": len(a_v), "b_verdict_count": len(b_v),
    }


def count_tags(findings: list[dict]) -> dict:
    out: dict[str, int] = {}
    for f in findings:
        out[f["tag"]] = out.get(f["tag"], 0) + 1
    return out


def print_report(r: dict) -> None:
    print("=" * 74)
    print("TWO-REVIEWER COMPARISON")
    print("=" * 74)
    print(f"A: {r['reviewer_a']}  -> {r['a_finding_count']} findings {r['a_severity_counts']}")
    print(f"B: {r['reviewer_b']}  -> {r['b_finding_count']} findings {r['b_severity_counts']}")
    print()
    print("-" * 74)
    print("NUMBERS CITED BY ONLY ONE REVIEWER  (compute these first)")
    print("-" * 74)
    print(f"  only in A ({len(r['numbers_only_a'])}): {', '.join(r['numbers_only_a'][:25]) or '(none)'}")
    print(f"  only in B ({len(r['numbers_only_b'])}): {', '.join(r['numbers_only_b'][:25]) or '(none)'}")
    print(f"  shared ({len(r['numbers_shared'])}): {', '.join(r['numbers_shared'][:20]) or '(none)'}")
    print()
    if r["unit_numbers_only_a"] or r["unit_numbers_only_b"]:
        print("  unit-bearing numbers unique to one reviewer:")
        for x in r["unit_numbers_only_a"][:10]:
            print(f"    A only: {x}")
        for x in r["unit_numbers_only_b"][:10]:
            print(f"    B only: {x}")
        print()
    print("-" * 74)
    print("VERDICT-STANCE CONFLICTS  (same topic, opposite polarity)")
    print("-" * 74)
    if not r["verdict_conflicts"]:
        print("  (none detected by keyword overlap -- read both verdicts manually)")
    for c in r["verdict_conflicts"]:
        print(f"  topic: {', '.join(c['topic'])}")
        print(f"    A [{c['a_stance']}]: {c['a']}")
        print(f"    B [{c['b_stance']}]: {c['b']}")
        print()
    print("-" * 74)
    print("REMINDER")
    print("-" * 74)
    print("  Agreement is weak evidence; disagreement is the signal. Compute every")
    print("  number in 'only A' and 'only B' in Python BEFORE acting on either review.")
    print("  Free-tier reviewers fabricate plausible numbers -- verify, then decide.")
    print("=" * 74)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--a", required=True, help="reviewer A file")
    ap.add_argument("--b", required=True, help="reviewer B file")
    ap.add_argument("--json", action="store_true", help="emit JSON")
    args = ap.parse_args(argv)

    a_text, b_text = read(args.a), read(args.b)
    r = compare(a_text, b_text, Path(args.a).name, Path(args.b).name)
    if args.json:
        print(json.dumps(r, indent=2, ensure_ascii=False))
    else:
        print_report(r)
    return 0


if __name__ == "__main__":
    sys.exit(main())
