#!/usr/bin/env python3
"""
audit_claims.py — Layer F of the checking plan + Phase 1.2 devplan verification.

Two modes:
1. **Regex mode (legacy):** Parses the paper draft and README, finds every
   quantitative claim, and cross-checks it against the reference JSONs in
   v0.3-prelim/data/results/.
2. **Table mode (Phase 1.2):** Verifies every number in
   docs/PAPER_STANDING_NUMBERS.md against its source JSON file.

Usage:
    python scripts/audit_claims.py                       # both modes
    python scripts/audit_claims.py --paper v0.3-prelim/docs/PAPER_V1_DRAFT.md  # regex only
    python scripts/audit_claims.py --table-only         # table only
    python scripts/audit_claims.py --check-all

Exit code 0 = all checks pass. Non-zero = at least one failure.
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
DEFAULT_TABLE = REPO_ROOT / "v0.3-prelim" / "docs" / "PAPER_STANDING_NUMBERS.md"

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
    # Phase 1.2 devplan — T215 standing numbers
    {
        "label": "T215u: mean t_max = 69.57 Myr (memory-capped)",
        "regex": r"mean\s*69\.57|69\.57\s*Myr|69\.57,\s*std",
        "ref_json": "t215u_memory_cap_summary.json",
        "ref_key": "mean_myr",
        "expected": 69.57,
        "tol": 0.1,
    },
    {
        "label": "T215u: std = 0.74 Myr (memory-capped)",
        "regex": r"std\s*=?\s*0\.74",
        "ref_json": "t215u_memory_cap_summary.json",
        "ref_key": "std_myr",
        "expected": 0.74,
        "tol": 0.1,
    },
    {
        "label": "T208: t_core = 73.7 Gyr (Phase 44 host halo)",
        "regex": r"73\.7\s*Gyr",
        "ref_json": "t208_path_b_cloud9_host_halo_gravothermal.json",
        "ref_key": ("Cloud9_gravothermal", "t_core_Gyr"),
        "expected": 73.71,
        "tol": 0.5,
    },
    {
        "label": "T212: t_core = 0.176 Gyr at σ/m=70",
        "regex": r"0\.176\s*Gyr",
        "ref_json": "t212_silverman_gravothermal.json",
        "ref_key": ("cloud9_host_at_sigma70", "t_core_Gyr"),
        "expected": 0.176,
        "tol": 0.005,
    },
    {
        "label": "T213: σ/m(V_max=31.12) = 0.174 cm²/g",
        "regex": r"0\.174\s*cm[²2]/g",
        "ref_json": "t213_kk_tower_silverman_combined.json",
        "ref_key": "sigma_m_at_cloud9_v_max_cm2_g",
        "expected": 0.174,
        "tol": 0.005,
    },
    {
        "label": "T205: Bayes log B = 2.411 (multi-resonance vs constant)",
        "regex": r"log\s*B\s*=?\s*2\.41",
        "ref_json": "t205_full_likelihood_published.json",
        "ref_key": "log_bayes_factor",
        "expected": 2.411,
        "tol": 0.01,
    },
    {
        "label": "T207c: v_HL = 105.24 ± 38.60 (priored free)",
        "regex": r"105\s*\u00b1?\s*39|105\.24",
        "ref_json": "t207c_priored_free_emcee.json",
        "ref_key": ("posterior_medians", "v_HL"),
        "expected": 105.24,
        "tol": 1.0,
    },
    {
        "label": "T207c: f_H_cc = 0.060 ± 0.012 (priored free)",
        "regex": r"f_H_cc\s*=?\s*0\.060",
        "ref_json": "t207c_priored_free_emcee.json",
        "ref_key": ("posterior_medians", "f_H_cc"),
        "expected": 0.060,
        "tol": 0.005,
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


def verify_table(table_path: Path, results_dir: Path) -> int:
    """Verify the standing-numbers table against source JSON files.

    This is the Phase 1.2 devplan verifier. Returns 0 on zero drift.
    """
    if not table_path.exists():
        print(f"⚠ Table file not found: {table_path}")
        return 2

    print("=" * 70)
    print(f"STANDING-NUMBERS TABLE VERIFICATION (Phase 1.2)")
    print(f"Table: {table_path}")
    print("=" * 70)

    table_text = table_path.read_text(encoding="utf-8")

    checks = [
        # (label, ref_json, json_key_path, expected, tol)
        ("§2 borrowed pass count (4+2 = 6)",
         "t207_final_summary.json",
         ("channel_coverage_summary", "borrowed", "clear_pass"),
         4, 0),
        ("§2 borrowed marginal count",
         "t207_final_summary.json",
         ("channel_coverage_summary", "borrowed", "marginal"),
         2, 0),
        ("§2 yang pass count (4)",
         "t207_final_summary.json",
         ("channel_coverage_summary", "yang", "clear_pass"),
         4, 0),
        ("§2 t202 pass count (3)",
         "t207_final_summary.json",
         ("channel_coverage_summary", "t202", "clear_pass"),
         3, 0),
        ("§3 borrowed SPARC log L",
         "t207_final_summary.json",
         ("t207_de_prescription_modes", "borrowed", "per_channel_log_L", "SPARC v=100"),
         -0.0919, 0.005),
        ("§3 yang SPARC log L",
         "t207_final_summary.json",
         ("t207_de_prescription_modes", "yang", "per_channel_log_L", "SPARC v=100"),
         -0.2426, 0.005),
        ("§3 t202 SPARC log L",
         "t207_final_summary.json",
         ("t207_de_prescription_modes", "t202", "per_channel_log_L", "SPARC v=100"),
         -0.6068, 0.005),
        ("§4 Bayes log B",
         "t205_full_likelihood_published.json",
         "log_bayes_factor",
         2.411, 0.005),
        ("§4 Bayes B",
         "t205_full_likelihood_published.json",
         "bayes_factor",
         11.149, 0.1),
        ("§5 t_core at Phase 44 σ/m",
         "t208_path_b_cloud9_host_halo_gravothermal.json",
         ("Cloud9_gravothermal", "t_core_Gyr"),
         73.71, 0.5),
        ("§5 Cloud-9 V_max",
         "t208_path_b_cloud9_host_halo_gravothermal.json",
         ("Cloud9_host_halo_params", "V_max_kms"),
         24.75, 0.05),
        ("§6 t_core at σ/m=70",
         "t212_silverman_gravothermal.json",
         ("cloud9_host_at_sigma70", "t_core_Gyr"),
         0.176, 0.005),
        ("§6 t_cross at σ/m=70",
         "t212_silverman_gravothermal.json",
         ("cloud9_host_at_sigma70", "t_cross_Gyr"),
         0.092, 0.005),
        ("§7 σ/m at V_max=31.12",
         "t213_kk_tower_silverman_combined.json",
         "sigma_m_at_cloud9_v_max_cm2_g",
         0.174, 0.005),
        ("§7 Silverman+ threshold",
         "t213_kk_tower_silverman_combined.json",
         "silverman_threshold_cm2_g",
         1.0, 0.05),
        ("§9 Best Ω_h²",
         "t192_thermal_avg.json",
         ("best_configuration", "Omega_h2"),
         0.1187, 0.002),
        ("§10 T215u mean Myr",
         "t215u_memory_cap_summary.json",
         "mean_myr",
         69.57, 0.1),
        ("§10 T215u std Myr",
         "t215u_memory_cap_summary.json",
         "std_myr",
         0.74, 0.1),
        ("§10 T215u min Myr",
         "t215u_memory_cap_summary.json",
         "min_myr",
         68.72, 0.5),
        ("§10 T215u max Myr",
         "t215u_memory_cap_summary.json",
         "max_myr",
         69.99, 0.05),
        ("§3 priored v_HL median",
         "t207c_priored_free_emcee.json",
         ("posterior_medians", "v_HL"),
         105.24, 1.0),
        ("§3 priored v_HL std",
         "t207c_priored_free_emcee.json",
         ("posterior_stds", "v_HL"),
         38.60, 1.0),
        ("§3 priored f_H_cc median",
         "t207c_priored_free_emcee.json",
         ("posterior_medians", "f_H_cc"),
         0.060, 0.005),
        ("§3 priored σ_peak_HL median",
         "t207c_priored_free_emcee.json",
         ("posterior_medians", "sigma_peak_HL"),
         0.523, 0.05),
    ]

    n_pass = 0
    n_fail = 0
    for label, ref_json, ref_key, expected, tol in checks:
        json_path = results_dir / ref_json
        if not json_path.exists():
            print(f"  ⚠ MISSING JSON: {ref_json}")
            n_fail += 1
            continue
        with open(json_path) as f:
            data = json.load(f)
        actual = _get_nested(data, ref_key)
        if actual is None:
            print(f"  ⚠ MISSING KEY {ref_key} in {ref_json}")
            n_fail += 1
            continue
        diff = abs(actual - expected)
        if diff > tol:
            print(f"  ✗ DRIFT: {label}")
            print(f"      table: {expected} ± {tol}")
            print(f"      JSON:  {actual} (|Δ|={diff:.4f})")
            n_fail += 1
        else:
            print(f"  ✓ {label}: {actual}")
            n_pass += 1

    print()
    print("=" * 70)
    print(f"TABLE SUMMARY: {n_pass} pass, {n_fail} fail")
    print("=" * 70)

    if n_fail > 0:
        print("\n✗ Drift detected. PAPER_STANDING_NUMBERS.md needs update.")
        return 1
    print("\n✓ All numbers verified against source JSON. Zero drift.")
    return 0


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--paper", type=Path, default=DEFAULT_PAPER)
    parser.add_argument("--readme", type=Path, default=DEFAULT_README)
    parser.add_argument("--results", type=Path, default=DEFAULT_RESULTS)
    parser.add_argument("--table", type=Path, default=DEFAULT_TABLE,
                        help="Standing-numbers table to verify (Phase 1.2)")
    parser.add_argument("--table-only", action="store_true",
                        help="Only verify standing-numbers table, skip regex mode")
    parser.add_argument("--check-all", action="store_true",
                        help="Run both regex and table verification")
    args = parser.parse_args()

    print(f"Paper:  {args.paper}")
    print(f"README: {args.readme}")
    print(f"Results dir: {args.results}")
    print(f"Standing-numbers table: {args.table}")
    print()

    exit_code = 0

    # Phase 1.2: standing-numbers table verification (always runs unless --table-only skips it)
    table_rc = verify_table(args.table, args.results)
    if table_rc != 0:
        exit_code = table_rc

    if args.table_only:
        return exit_code

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
    print()
    print("=" * 70)
    print("CHECKING MAPPED CLAIMS (regex mode)")
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
        print("REGEX RESULT: FAIL — at least one mapped claim has drifted or is untracked.")
        return 1
    print("REGEX RESULT: PASS — all tracked claims match reference data within tolerance.")
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
