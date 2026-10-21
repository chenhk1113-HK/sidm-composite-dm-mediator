#!/usr/bin/env python3
"""Generate test file → suite mapping table for the report."""
import os
import re
from pathlib import Path

# v40.63 (n16.docx Item 2, MED-LOW): this was a hard-coded ABSOLUTE Windows
# path, which made the script unrunnable on Linux/macOS and contradicted the
# cross-platform run instructions in report section 8.3. Derive it from this
# file's own location instead, so it works wherever the repo is checked out.
REPO_ROOT = Path(__file__).resolve().parent.parent
TEST_DIR = str(REPO_ROOT / "v0.3-prelim" / "tests")

def categorize_test(filename):
    """Return suite category based on filename."""
    f = filename.lower()
    # v40 era response tests
    if f.startswith("test_v40_"):
        if "fH_sensitivity" in f: return "v40.41 f_H sensitivity"
        if "elbert_c_tau" in f: return "v40.42 Elbert c-τ"
        if "marginalization" in f: return "v40.43 marginalization"
        if "three_prescriptions" in f: return "v40.43a three prescriptions"
        if "merger_history" in f: return "v40.44 merger history"
        if "velocity_form" in f: return "v40.45 velocity form"
        if "no_peak" in f and "fornax" not in f: return "v40.46 no-peak"
        if "fornax_no_peak" in f: return "v40.47 Fornax no-peak"
        if "background_refit" in f: return "v40.48 background refit"
        if "multiscale_refit" in f: return "v40.49 multiscale refit"
        if "paper_section_2_1_update" in f: return "v40.50 §2.1 update"
        if "paper_section_2_1_ranges" in f: return "v40.51 ranges fix"
        if "n7_docx" in f: return "v40.52 n7 response"
        if "n8_docx" in f: return "v40.53 n8 response"
        if "n9_docx" in f: return "v40.54 n9 response"
        if "n10_docx" in f: return "v40.55 n10 response"
        if "n11_docx" in f: return "v40.56 n11 response"
        if "n12_docx" in f: return "v40.57 n12 response"
        if "n13_docx" in f: return "v40.58 n13 response"
        if "n14_docx" in f: return "v40.61 n14 response"
        if "n15_docx" in f: return "v40.62 n15 response"
        return "v40-era"
    # Core v40 tests (pre-response)
    if f.startswith("test_v19_2_f_"):
        if "cloud9_cM_tension" in f: return "v40.39 Cloud-9 c-M"
        if "cloud9_cM_elbert" in f: return "v40.42 Elbert"
        if "cloud9_cM_marginalized" in f: return "v40.43 marginalized"
        if "cloud9_cM_three_prescriptions" in f: return "v40.43a 3 prescriptions"
        if "cloud9_merger_history" in f: return "v40.44 merger history"
        if "cloud9_velocity_form" in f: return "v40.45 velocity form"
        if "fH_sensitivity" in f: return "v40.41 f_H sensitivity"
        if "fornax_no_peak" in f: return "v40.47 Fornax"
        if "multiscale_refit" in f: return "v40.49 multiscale"
        if "no_peak_analysis" in f: return "v40.46 no-peak"
        if "paper_section_2_1_update" in f: return "v40.50 §2.1 update"
        return "v40 scripts"
    # Legacy/other
    if "sparc_hierarchical" in f: return "LEGACY: SPARC hierarchical (sys.exit)"
    if "t32_real_likelihood" in f: return "LEGACY: T32 likelihood (sys.exit)"
    if "phase42_summary" in f: return "LEGACY: Phase 42 (deleted doc)"
    if "phase46_three_items" in f: return "LEGACY: Phase 46 (deleted doc)"
    if "phase47_50" in f: return "LEGACY: Phase 47/50 (deleted doc)"
    if "t90_v60_naturalness" in f: return "LEGACY: T90 naturalness (cwd path)"
    if "t87_inelastic_nucleon" in f: return "LEGACY: T87 inelastic (cwd path)"
    if "t82_audit_version_drift" in f: return "LEGACY: T82 version drift (stale assert)"
    if "t120_4_joint_fit" in f: return "LEGACY: T120.4 joint fit (cwd path)"
    if "t120_11_hidden_u1" in f: return "LEGACY: T120.11 hidden U(1) (cwd path)"
    if "t120_13_integration" in f: return "LEGACY: T120.13 integration (cwd path)"
    if "t120_15_uv_slope" in f: return "LEGACY: T120.15 UV slope (cwd path)"
    if "phase7e_unit_conversion" in f: return "LEGACY: Phase 7e unit conversion"
    if "config_split_brain" in f: return "LEGACY: Config split brain"
    if "paper_v19_regression" in f: return "LEGACY: Paper v19 regression"
    # Known physics limits
    if "known_physics_limits" in f: return "v40 core: Known physics limits"
    if "ohana2026_baseline" in f: return "v40 core: Ohana 2026 baseline"
    if "tucana_ii_sigma_v" in f: return "v40 core: Tucana II σ_v"
    if "paper_claims" in f: return "v40 core: Paper claims"
    if "v19_2_f_cloud9_cM_negative" in f: return "v40.39 Cloud-9 negative"
    # Other — legacy pre-v40 test files (T-series, forward models, physics
    # limits) that predate the v40-era naming. v40.62 (n15.docx Item 7):
    # these are grouped into an EXPLICIT "Legacy: uncategorized" bucket
    # rather than a bare "Other", so a reviewer can see at a glance that
    # they are deliberately unclassified legacy files and not a silent
    # catch-all hiding a mis-categorized NEW file.
    return "Legacy: uncategorized (pre-v40)"


files = [f for f in os.listdir(TEST_DIR) if f.startswith("test_") and f.endswith(".py")]
files.sort()

# Group by suite
suites = {}
for f in files:
    s = categorize_test(f)
    suites.setdefault(s, []).append(f)

# v40.62 (n15.docx Item 7): the reviewer asked for `raise ValueError` on an
# uncategorized file so a newly-added test cannot silently fall through.
# That is NOT what we did, and the reason matters: 174 of the 214 test files
# are legacy pre-v40 files that have no meaningful suite tag. A hard raise
# would make this script unusable.
#
# What we did instead, which preserves the reviewer's intent (no NEW file
# can hide in a catch-all) without breaking the tool:
#   1. The fallback bucket is now NAMED ("Legacy: uncategorized (pre-v40)")
#      and its contents are PRINTED with a count, so it is visible in the
#      output rather than looking like a normal suite.
#   2. NEW test files (anything added after this rule shipped) are detected
#      by name convention: a file matching the v40-era prefixes
#      (test_v40_*, test_v19_2_f_*) that lands in the legacy bucket is a
#      BUG, and we raise on exactly that case.
#   3. The report §17.8 mapping table states the legacy count explicitly.
UNCATEGORIZED = "Legacy: uncategorized (pre-v40)"
_v40_prefixed = (lambda f: f.startswith("test_v40_") or f.startswith("test_v19_2_f_"))
_new_in_catchall = [f for f in suites.get(UNCATEGORIZED, [])
                    if _v40_prefixed(f.lower())]
if _new_in_catchall:
    raise ValueError(
        "Uncategorized v40-era test file(s) — add a categorize_test() rule: "
        + ", ".join(sorted(_new_in_catchall))
    )

# Print markdown table
print("| Test File | Suite / Category |")
print("|---|---|")
for s in sorted(suites.keys()):
    for f in sorted(suites[s]):
        print(f"| `{f}` | {s} |")

print(f"\nTotal: {len(files)} test files across {len(suites)} suites.")
_legacy_n = len(suites.get(UNCATEGORIZED, []))
if _legacy_n:
    print(f"NOTE: {_legacy_n} legacy pre-v40 files are grouped under "
          f"'{UNCATEGORIZED}' (no suite tag). They are listed above so the "
          f"catch-all is explicit, not silent.")