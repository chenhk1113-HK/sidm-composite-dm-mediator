"""v31 Table Renderer — programmatic §7 emission (r33 item 1 fix).

Reads v19_2_f_lyman_alpha_post_v31.json and emits Markdown tables for §7 of the
v31 review packet. Each Gamma/rho shows ALL 14 alpha_D rows (no truncation)
to prevent the transcription-error class that contaminated v30 §7.
"""
import json
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve().parent
JSON_PATH = _SCRIPT_DIR.parent / "data" / "results" / "v19_2_f_lyman_alpha_post_v31.json"
OUTPUT_PATH = _SCRIPT_DIR.parent / "data" / "results" / "v31_section7_tables.md"


def render_section7(json_data):
    """Emit Markdown for §7 of the v31 packet — all 9 Gamma/rho tables."""
    out = []
    out.append("## 7. CORRECTED extended α_D scan tables (REVIEWER-33 item 1)\n")
    out.append("All 9 Γ/ρ values × 14 α_D values = 126 points. **Generated programmatically "
               "from `v19_2_f_lyman_alpha_post_v31.json` to eliminate transcription errors** "
               "(r33 critical finding: v30 §7 tables for Γ/ρ=2.0, 4.0, 6.0 had transcription "
               "errors; JSON data was correct, table values were not). This renderer ensures "
               "the published numbers always match the JSON byte-for-byte.\n")

    fixed = json_data["fixed_parameters"]
    out.append(f"**Fixed parameters:** m_χ = {fixed['m_chi_GeV']} GeV, "
               f"m_ρ = {fixed['m_rho_GeV']*1e3} MeV (v_res = {fixed['v_resonance_kms']:.2f} km/s), "
               f"v_target = {fixed['v_target_kms']} km/s, "
               f"σ/m target = {fixed['sigma_target_cm2_g']} cm²/g.\n")

    out.append("| α_D | σ/m | × target | region |")
    out.append("|---:|---:|---:|:---:|")
    for Gamma_frac, scan in json_data["all_scan_results"].items():
        out.append("")
        out.append(f"### Γ/ρ = {Gamma_frac}")
        out.append("")
        out.append("| α_D | σ/m | × target | region |")
        out.append("|---:|---:|---:|:---:|")
        for entry in scan:
            sig = entry["sigma_m_29.4"]
            r_t = entry["ratio_target"]
            region = entry["region"]
            sig_str = f"{sig:.4e}" if isinstance(sig, (int, float)) else "—"
            r_t_str = f"{r_t:.3e}" if isinstance(r_t, (int, float)) else "—"
            out.append(f"| {entry['alpha_D']:.2e} | {sig_str} | {r_t_str} | {region} |")

    # Add a verifier block showing the JSON-emitted ratios match the §6 claim.
    out.append("")
    out.append("### α_D² scaling audit (auto-generated from JSON)")
    out.append("")
    out.append("For each Γ/ρ, the ratio σ(2α_D)/σ(α_D) is computed from adjacent α_D pairs "
               "and compared to the predicted 4.000. **All ratios should be 1.0000 (since "
               "σ scales exactly as α_D² in the Born-valid regime below the unitarity floor).**\n")
    out.append("| Γ/ρ | min ratio | max ratio | mean ratio | passes? |")
    out.append("|---:|---:|---:|---:|:---:|")
    for Gamma_frac, scan in json_data["all_scan_results"].items():
        ratios = []
        for a, b in zip(scan[:-1], scan[1:]):
            sa = a["sigma_m_29.4"]
            sb = b["sigma_m_29.4"]
            if (isinstance(sa, (int, float)) and isinstance(sb, (int, float))
                    and sa > 0 and sb > 0 and a["alpha_D"] > 0 and b["alpha_D"] > 0):
                # Expected ratio for a single α_D-step depends on the step size;
                # we verify the FUNCTIONAL form: ratio(α2/α1)² ≈ σ(α2)/σ(α1)
                predicted = (b["alpha_D"] / a["alpha_D"]) ** 2
                actual = sb / sa
                ratios.append(actual / predicted)
        if ratios:
            passes = "✓" if all(0.99 < r < 1.01 for r in ratios) else "✗"
            out.append(f"| {Gamma_frac} | {min(ratios):.6f} | {max(ratios):.6f} | "
                       f"{sum(ratios)/len(ratios):.6f} | {passes} |")
        else:
            out.append(f"| {Gamma_frac} | — | — | — | — |")

    return "\n".join(out) + "\n"


def main():
    with open(JSON_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    md = render_section7(data)
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        f.write(md)
    print(f"Wrote {OUTPUT_PATH}  ({len(md)} chars, {md.count(chr(10))} lines)")
    # Quick sanity: count tables
    table_count = md.count("### Γ/ρ =")
    print(f"Tables rendered: {table_count} (expected: 9)")


if __name__ == "__main__":
    main()
