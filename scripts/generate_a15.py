"""
V19.2-F P1+2+ — §A.15 generator (ClawsGO #5 B.2 + #7).

Per ClawsGO #5 B.2 + #7 §2, §A.15 (the "canonical channel table") is the
single source of truth for the paper's pass/fail, no-go catalogue, and
trade-off factors. This script generates §A.15 from the canonical JSON
( scripts/canonical_numbers.py output ) so the table cannot drift from
the canonical numbers by hand-editing.

§A.15 output has three blocks:
1. Pass/fail table (per-channel, with status and trade-off factors)
2. No-go catalogue (structural findings, tuning statements, open requirements)
3. UV completion no-gos (S10, 5 entries)

Each block references the canonical JSON for the underlying values; the
generator only formats the prose.

Usage:
  python scripts/generate_a15.py [--output PATH]

Default output: prints to stdout. Use --output to write to a file.
"""
from __future__ import annotations
import argparse
import json
import sys
from pathlib import Path

_THIS = Path(__file__).resolve()
_REPO = _THIS.parent.parent
CANONICAL_JSON = _REPO / "v0.3-prelim" / "data" / "results" / "canonical_numbers.json"
DEFAULT_OUTPUT = _REPO / "v0.3-prelim" / "data" / "results" / "section_A15.md"


def load_canonical():
    if not CANONICAL_JSON.exists():
        print(f"ERROR: {CANONICAL_JSON} not found.", file=sys.stderr)
        print(f"Run `python scripts/canonical_numbers.py` first.", file=sys.stderr)
        sys.exit(2)
    with open(CANONICAL_JSON) as f:
        return json.load(f)


def render_a15(canonical):
    """Render §A.15 (canonical channel table) from the canonical JSON."""
    out = []
    out.append("### A.15 Canonical Channel Table (machine-generated, single source of truth)")
    out.append("")
    out.append(
        "**This section is regenerated from `scripts/canonical_numbers.py` on every "
        "freeze round; the values here are the canonical numbers used in the abstract, "
        "§2.6, §9.17, §10, and §11. Do not edit by hand — edit `scripts/canonical_numbers.py` "
        "and re-run.** Per ClawsGO #5 B.2 + #7, this is the single source of truth for "
        "the paper's pass/fail, no-go catalogue, and trade-off factors."
    )
    out.append("")

    # ----------------------------------------------------------------------
    # Block 1: Abstract channel count (canonical, ClawsGO #7 §4)
    # ----------------------------------------------------------------------
    cc = canonical["canonical_abstract_channel_count"]
    out.append(f"**Abstract channel count (canonical):** {cc['canonical_count_string']}")
    out.append("")
    out.append("| Status | Channels |")
    out.append("|---|---|")
    for ch in cc["PASS_channels"]:
        out.append(f"| PASS (4) | {ch} |")
    for ch in cc["MARGINAL_channels"]:
        out.append(f"| MARGINAL (3) | {ch} |")
    for ch in cc["FAIL_channels"]:
        out.append(f"| FAIL (1) | {ch} |")
    out.append("")
    out.append(f"**Note on Lei/Wang double-count (ClawsGO #7 §2b):** {cc['note_on_lei_wang']}")
    out.append("")
    out.append("**Retired conventions:**")
    for r in cc["retired_conventions"]:
        out.append(f"- {r}")
    out.append("")

    # ----------------------------------------------------------------------
    # Block 2: Per-channel pass/fail at canonical Phase 44
    # ----------------------------------------------------------------------
    out.append("**Per-channel pass/fail at canonical Phase 44 (σ₀=0.052, a=1.93, "
               "σ_peak=174, v_target=29.4, σ₁=4.4):**")
    out.append("")
    out.append("| v [km/s] | Channel | σ_obs | σ_unc | kind | σ_HH | σ_eff | verdict |")
    out.append("|---|---|---|---|---|---|---|---|")
    for ch in canonical["per_channel_at_v19_2_D_canonical"]:
        out.append(
            f"| {ch['v_kms']:.0f} | {ch['label']} | {ch['sigma_obs']:.4g} | "
            f"{ch['sigma_unc']:.4g} | {ch['kind']} | {ch['sigma_HH_at_v']:.3g} | "
            f"{ch['sigma_eff']:.4g} | **{ch['verdict']}** |"
        )
    s = canonical["pass_fail_summary_v19_2_D_canonical"]
    out.append(f"| | **TOTAL** | | | | | | "
               f"**{s['PASS']} PASS / {s['MARGINAL']} MARGINAL / {s['FAIL']} FAIL** |")
    out.append("")

    # ----------------------------------------------------------------------
    # Block 3: Per-channel at v19.2-E A.2 best-fit
    # ----------------------------------------------------------------------
    out.append("**Per-channel pass/fail at v19.2-E A.2 5-param DE best-fit "
               "(σ₀=0.0265, a=1.198, σ_peak=2026, v_target=28.47, σ₁=1.2):**")
    out.append("")
    out.append("| v [km/s] | Channel | σ_obs | σ_unc | kind | σ_HH | σ_eff | verdict |")
    out.append("|---|---|---|---|---|---|---|---|")
    for ch in canonical["per_channel_at_v19_2_E_A2_best_fit"]:
        out.append(
            f"| {ch['v_kms']:.0f} | {ch['label']} | {ch['sigma_obs']:.4g} | "
            f"{ch['sigma_unc']:.4g} | {ch['kind']} | {ch['sigma_HH_at_v']:.3g} | "
            f"{ch['sigma_eff']:.4g} | **{ch['verdict']}** |"
        )
    s2 = canonical["pass_fail_summary_v19_2_E_A2_best_fit"]
    out.append(f"| | **TOTAL** | | | | | | "
               f"**{s2['PASS']} PASS / {s2['MARGINAL']} MARGINAL / {s2['FAIL']} FAIL** |")
    out.append("")

    # ----------------------------------------------------------------------
    # Block 4: Trade-off factors (canonical, ClawsGO #5+#7 §5)
    # ----------------------------------------------------------------------
    out.append("**Trade-off factors (canonical, R88(88)):**")
    out.append("")
    tf = canonical["canonical_tradeoff_factors"]
    out.append(f"{tf['canonical_text']}")
    out.append("")
    out.append("| Quantity | Factor |")
    out.append("|---|---|")
    out.append(f"| σ_eff(Cloud-9) below 50 | **{tf['cloud9_factor_below_50']:.0f}×** |")
    out.append(f"| σ_eff(SPARC) below 0.19 | **{tf['sparc_factor_below_0p19']:.0f}×** |")
    out.append("")
    out.append("**Retired values (ClawsGO #7 §5):**")
    for r in tf["retired_values"]:
        out.append(f"- {r}")
    out.append("")

    # ----------------------------------------------------------------------
    # Block 5: No-go catalogue (canonical, ClawsGO #5 B.2 + #7)
    # ----------------------------------------------------------------------
    out.append("**No-go catalogue (canonical, machine-generated):**")
    out.append("")
    out.append("**Status legend:** " + " | ".join(
        f"**{k}** = {v}" for k, v in canonical["no_go_catalogue"]["_meta"]["status_legend"].items()
    ))
    out.append("")
    for entry in canonical["no_go_catalogue"]["entries"]:
        out.append(f"- **[{entry['status']}]** **{entry['name']}** (§{entry['section']})")
        out.append(f"  - Argument: {entry['argument']}")
        if entry.get("caveat"):
            out.append(f"  - Caveat: {entry['caveat']}")
        if entry.get("factor_vs_constraint"):
            f_str = ", ".join(f"{k}={v}" for k, v in entry["factor_vs_constraint"].items())
            out.append(f"  - Factor vs constraint: {f_str}")
        out.append(f"  - Reference: {entry['R88_reference']}")
    out.append("")

    # ----------------------------------------------------------------------
    # Block 6: UV completion no-gos (S10, 5 entries)
    # ----------------------------------------------------------------------
    out.append("**UV completion no-gos (S10, 5 entries):**")
    out.append("")
    out.append("**Note (ClawsGO #7 §7):** the abstract calls these 'five UV completion "
               "no-go theorems'. Four are specific UV constructions (CONSTRAINT, 10.2a-d); "
               "the fifth (T184, 10) is a general scaling argument. Per ClawsGO #7, the "
               "abstract should either rename to 'no-go constraints/exclusions at the "
               "Phase-44 baseline' or state which are theorems and which are arguments.")
    out.append("")
    for entry in canonical["no_go_catalogue"]["UV_completion_no_gos_S10"]:
        out.append(f"- **[{entry['status']}]** **{entry['name']}** (§{entry['section']})")
        if entry.get("note"):
            out.append(f"  - {entry['note']}")
    out.append("")

    # ----------------------------------------------------------------------
    # Block 7: Halo-specific gravothermal prefactors
    # ----------------------------------------------------------------------
    out.append("**Halo-specific gravothermal prefactors (v19.2-E B):**")
    out.append("")
    out.append("| Halo | Prefactor vs Yang+ 2024 150×C | σ_eff/m [cm²/g] | t_c [Gyr] | Citation |")
    out.append("|---|---|---|---|---|")
    for halo, data in canonical["halo_specific_gravothermal_prefactors"].items():
        out.append(f"| {halo} | {data['prefactor_vs_yang2024']}× | {data['sigma_eff_per_m']} | "
                   f"{data['t_c_gyr']} | {data['citation']} |")
    out.append("")

    # ----------------------------------------------------------------------
    # Footer
    # ----------------------------------------------------------------------
    out.append("---")
    out.append("")
    out.append(
        "**Source:** `scripts/canonical_numbers.py` → "
        "`v0.3-prelim/data/results/canonical_numbers.json`. To regenerate: "
        "`python scripts/canonical_numbers.py && python scripts/generate_a15.py`."
    )

    return "\n".join(out)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=None,
                        help=f"Output file (default: {DEFAULT_OUTPUT})")
    args = parser.parse_args()

    canonical = load_canonical()
    a15_text = render_a15(canonical)

    if args.output is None:
        # Default: write to default output path AND print
        DEFAULT_OUTPUT.parent.mkdir(parents=True, exist_ok=True)
        DEFAULT_OUTPUT.write_text(a15_text, encoding='utf-8')
        print(f"§A.15 written to: {DEFAULT_OUTPUT}")
    else:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(a15_text, encoding='utf-8')
        print(f"§A.15 written to: {args.output}")


if __name__ == "__main__":
    main()
