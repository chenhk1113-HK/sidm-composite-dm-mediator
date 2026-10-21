#!/usr/bin/env python3
"""Generate test file → suite mapping table for the report."""
import os
import re

TEST_DIR = r"C:\Users\lamkuenai\projects\sidm-composite-dm-mediator\v0.3-prelim\tests"

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
    # Other
    return "Other"

files = [f for f in os.listdir(TEST_DIR) if f.startswith("test_") and f.endswith(".py")]
files.sort()

# Group by suite
suites = {}
for f in files:
    s = categorize_test(f)
    suites.setdefault(s, []).append(f)

# Print markdown table
print("| Test File | Suite / Category |")
print("|---|---|")
for s in sorted(suites.keys()):
    for f in sorted(suites[s]):
        print(f"| `{f}` | {s} |")

print(f"\nTotal: {len(files)} test files across {len(suites)} suites.")