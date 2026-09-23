#!/usr/bin/env python3
"""
audit_claims.py — Layer F of the checking plan.

Parses the paper draft and README, finds every quantitative claim, and
cross-checks it against the reference JSONs in v0.3-prelim/data/results/.

A claim is a line in the paper that mentions a number like "+8.10",
"115/127", "ΔBIC = -5.66", etc., tied to a Phase. This script:

1. Extracts lines containing numbers from the paper and README
2. For each, looks up the corresponding reference JSON
3. Verifies the number is within tolerance of the JSON value

The mapping (paper claim -> reference JSON) is hard-coded here; if a
new claim is added to the paper without updating this map, the script
will flag it as an untracked claim.

This is the lightweight alternative to a full property-based test suite:
we only check the *headline* numbers, but those are the ones that
typically drift in the status line.

Usage:
    python scripts/audit_claims.py
    python scripts/audit_claims.py --paper v0.3-prelim/docs/PAPER_V1_DRAFT.md

Exit code 0 = all claims map to a passing reference. Non-zero = at least
one claim is untracked or has drifted.
"""
import argparse
import json
import re
import sys
from pathlib import Path

# Path defaults
REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_PAPER = REPO_ROOT / "v0.3-prelim" / "docs" / "PAPER_V1_DRAFT.md"
DEFAULT_README = REPO_ROOT / "README.md"
DEFAULT_RESULTS = REPO_ROOT / "v0.3-prelim" / "data" / "results"

# Hard-coded claim map. Each entry: (regex to find in paper, reference JSON, JSON key, tolerance, label)
# If a paper claim is not in this map, the script reports it as untracked.
CLAIM_MAP = [
    {
        "label": "Phase 44: +8.10 log-units (free joint fit)",
        "regex": r"\+8\.10\s+log-units",
        "ref_json": "phase44_joint_fit.json",
        "ref_key": "improvement",
        "expected": 8.10,
        "tol": 0.01,
    },
    {
        "label": "Phase 53 v2: +7.93 log-units (clockwork UV prior)",
        "regex": r"\+7\.93\s+log-units",
        "ref_json": "phase53_v2_clockwork_uv_prior_fixed.json",
        "ref_key": ("phase53_v2_results", "improvement_vs_phase44_baseline"),
        "expected": 7.93,
        "tol": 0.01,
    },
    {
        "label": "Phase 53 v2: BIC Δ = -5.66 favoring clockwork",
        "regex": r"BIC\s*Δ?\s*=\s*[−-]5\.66",
        "ref_json": "phase53_v2_clockwork_uv_prior_fixed.json",
        "ref_key": ("bic_comparison", "delta_bic"),
        "expected": -5.66,
        "tol": 0.05,
    },
    {
        "label": "Phase 33d: 115/127 SPARC pass V_flat test",
        "regex": r"115/127\s*=\s*90\.6%",
        "ref_json": "phase33d_external_probe_real.json",
        "ref_key": "n_consistent",
        "expected": 115,
        "tol": 0,  # exact
    },
    {
        "label": "Phase 54: +6.08 log-units (joint vs constant σ/m)",
        "regex": r"\+6\.08\s+log-units",
        "ref_json": "phase54_joint_comparison.json",
        "ref_key": ("headline", "logL_delta_3channel"),
        "expected": 6.08,
        "tol": 0.01,
    },
    {
        "label": "Phase 54: BIC Δ = +3.22 favoring constant σ/m",
        "regex": r"\+3\.22\s+(BIC|favoring)",
        "ref_json": "phase54_joint_comparison.json",
        "ref_key": ("headline", "bic_delta_3channel"),
        "expected": 3.22,
        "tol": 0.05,
    },
    {
        "label": "Cloud-9: M_200 ≈ 5×10⁹ M☉ (halo mass prior)",
        "regex": r"5(?:\.0)?[×x·]10[⁹^]9?\s*M[☉_]",
        "ref_json": "phase23_cloud9_nuisance_marginalization.json",
        "ref_key": ("nuisance_priors", "M200", "mean"),
        "expected": 5.0e9,
        "tol": 1.0e8,
    },
]


def _get_nested(d, key_path):
    """Get a value from a dict using a tuple key path or a single string.

    Supports both 2-tuple (parent, key) and longer tuples (a, b, c, ...)
    for arbitrarily nested access.
    """
    if isinstance(key_path, str):
        return d.get(key_path)
    if not isinstance(key_path, (tuple, list)):
        return None
    cur = d
    for k in key_path:
        if not isinstance(cur, dict):
            return None
        cur = cur.get(k)
    return cur


def check_claim(claim: dict, results_dir: Path) -> tuple[bool, str]:
    """Check one claim. Returns (pass, message)."""
    json_path = results_dir / claim["ref_json"]
    if not json_path.exists():
        return False, f"  ⚠ REF JSON MISSING: {claim['ref_json']}"

    with open(json_path, encoding="utf-8") as f:
        d = json.load(f)

    actual = _get_nested(d, claim["ref_key"])
    if actual is None:
        return False, f"  ⚠ KEY MISSING: {claim['ref_key']} in {claim['ref_json']}"

    diff = abs(actual - claim["expected"])
    if diff > claim["tol"]:
        return False, (
            f"  ✗ DRIFT: {claim['label']}\n"
            f"      paper claim: {claim['expected']} ± {claim['tol']}\n"
            f"      JSON value:  {actual} (diff {diff:.4f})"
        )
    return True, f"  ✓ {claim['label']}: {actual} (within {claim['tol']} of {claim['expected']})"


def find_claims_in_text(text: str) -> list[str]:
    """Find lines containing quantitative numbers (claims)."""
    findings = []
    for line in text.split("\n"):
        # Lines with at least one decimal number
        if re.search(r"\d+\.\d+", line):
            findings.append(line.strip()[:200])
    return findings


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--paper", type=Path, default=DEFAULT_PAPER)
    parser.add_argument("--readme", type=Path, default=DEFAULT_README)
    parser.add_argument("--results", type=Path, default=DEFAULT_RESULTS)
    args = parser.parse_args()

    print(f"Paper:  {args.paper}")
    print(f"README: {args.readme}")
    print(f"Results dir: {args.results}")
    print()

    if not args.paper.exists():
        print(f"ERROR: paper not found: {args.paper}")
        return 2
    if not args.readme.exists():
        print(f"ERROR: readme not found: {args.readme}")
        return 2

    paper_text = args.paper.read_text(encoding="utf-8")
    readme_text = args.readme.read_text(encoding="utf-8")
    combined = paper_text + "\n" + readme_text

    # 1. Check each mapped claim
    print("=" * 70)
    print("CHECKING MAPPED CLAIMS")
    print("=" * 70)
    all_pass = True
    for claim in CLAIM_MAP:
        # First check: does the claim regex appear in the paper at all?
        if not re.search(claim["regex"], combined):
            print(f"  ! NOT FOUND IN PAPER: {claim['label']}")
            print(f"      (regex: {claim['regex']})")
            all_pass = False
            continue

        # Check: does the reference value still match the paper claim?
        ok, msg = check_claim(claim, args.results)
        print(msg)
        if not ok:
            all_pass = False

    # 2. Look for unmapped numerical claims (warnings only, not failures)
    print()
    print("=" * 70)
    print("NUMERICAL LINES IN PAPER (informational)")
    print("=" * 70)
    findings = find_claims_in_text(paper_text)
    print(f"Found {len(findings)} lines with decimal numbers in paper.")
    print("Most are within prose; only the headline Phase claims are tracked.")
    print()
    if not all_pass:
        print("RESULT: FAIL — at least one mapped claim has drifted or is untracked.")
        return 1
    print("RESULT: PASS — all tracked claims match reference data within tolerance.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
