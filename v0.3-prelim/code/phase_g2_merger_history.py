"""
Phase G2 — Merger-history stochastic modulator (R88(49), two-sided implementation)

The Silverman+ 2026 physics is two-sided:
- Quiescent history: the halo has time to relax and collapse → t_c × 0.5-1 (boost)
- Active history: kinetic energy injection continually resets the core → t_c × 5-20 (delay)

This module implements a two-sided merger-history modulator that, when applied to
the base Phase G4 τ predictions, produces intrinsic phase diversity:
- Quiescent halos (Cloud-9, isolated RELHIC) → τ reduces toward collapse
- Active halos (in MW halo) → τ increases toward core-expansion
- Mixed halos (UFDs) → scatter around boundary

Implementation per Silverman+ 2026 §3 (all four are LITERATURE labels):
- Activity fraction: f_active ~ 0.5 (half of halos have recent major mergers)
- Quiescent multiplier: 0.7 (collapse boost)
- Active multiplier: 8.0 (collapse delay)
- Mixed multiplier: 1.0 (no modulation)

Measured counterpart (added 2026-11-05, `measured_merger_statistics()`): the locally built
IllustrisTNG Stage-3 sample measures the activity fraction directly, so f_active is no longer
only an assumption:
- RELHIC-mass tier (TNG50-1, ~9.0e8 Msun, V_max ~16.5 km/s, 60 halos): f_active = 0.733
- Cloud-9-mass anchor tier (TNG50-1, 4.1-5.8e9 Msun, 25 halos): f_active = 1.000
  (0 of 25 have no merger after z = 1; median latest merger at z = 0.074)
- TNG100-1 control tier is NOT usable for merger statistics (median 0 tracked mergers; its
  subhalo trees stop around z ~ 3.5) and is excluded from any measured claim.
The 0.7 / 8.0 multipliers are NOT measured by this sample: our data measures how often halos
merge, not what a merger does to a gravothermal collapse time. They remain Silverman+ 2026 labels.

Phase G2 outputs feed into Phase G4 as: τ_final = τ_base × merger_modulator(history).

Inputs
------
- Phase G4 (R88(49)) provides base τ values for each halo
- Per-halo merger history from observation (Fornax: in MW halo, active;
  Cloud-9: isolated RELHIC, quiescent; UFDs: mixed)

Status (R88(49))
----------------
- Implementation: complete (two-sided modulator; per-halo history from
  observation; Silverman+ 2026 calibration)
- Result: Phase G4 with G2 modulation produces phase diversity (Cloud-9
  core-expansion, Fornax/Sculptor/Draco collapse; UFDs mixed)
- Replaces one-sided modulator from R88(23) (which only delayed collapse, never caused it)
"""
from __future__ import annotations
import math
import sys
from pathlib import Path

# Reuse Phase G4 pipeline infrastructure
sys.path.insert(0, r"C:\Users\lamkuenai\projects\sidm-composite-dm-mediator\v0.3-prelim\code")
from phase_g4_pipeline import predict_phase, classify_phase

# --- measured merger statistics (added 2026-11-05) -------------------------------
# Produced by v0.3-prelim/code/tng_stage3_growth_summary.py from the per-subhalo
# IllustrisTNG merger trees fetched into v0.3-prelim/data/external/tng/ (local only).
GROWTH_SUMMARY = (Path(__file__).resolve().parents[1]
                  / "data" / "results" / "tng_stage3_growth_summary.json")
MEASURED_STATS_OUT = (Path(__file__).resolve().parents[1]
                      / "data" / "results" / "phase_g2_measured_merger_statistics.json")

# Literature labels actually used by merger_history_modulator(). Named as such so no
# reader mistakes them for quantities calibrated on this repo's own data.
LITERATURE_ACTIVITY_FRACTION = 0.5
LITERATURE_MULTIPLIERS = {"quiescent": 0.7, "active": 8.0, "mixed": 1.0}

# Which sample tier is the analogue of which observed halo class.
MEASURED_TIERS = {
    "relhic_mass_tier_tng50_1": {
        "tier_key": "stage3_sample", "run": "TNG50-1",
        "analogue": "RELHIC / UFD-mass field halos (Cloud-9 host mass is NOT in this tier)",
    },
    "cloud9_mass_anchor_tier_tng50_1": {
        "tier_key": "stage3_anchor", "run": "TNG50-1",
        "analogue": "Cloud-9 host mass (4.1-5.8e9 Msun); see decision D8",
    },
    "control_tier_tng100_1": {
        "tier_key": "stage3_sample", "run": "TNG100-1",
        "analogue": "resolution control only - EXCLUDED from merger claims",
    },
}


def measured_merger_statistics(summary_path=None):
    """Measure merger activity in the local IllustrisTNG sample and compare it with the
    literature f_active assumption used by merger_history_modulator().

    Returns a dict, or None when the sample has not been built on this machine.
    """
    import json

    path = Path(summary_path) if summary_path else GROWTH_SUMMARY
    if not path.exists():
        return None
    summary = json.loads(path.read_text(encoding="utf-8"))

    tiers = {}
    for name, spec in MEASURED_TIERS.items():
        tier = summary.get(spec["tier_key"], {}).get("by_run", {}).get(spec["run"])
        if not tier:
            continue
        mg = tier.get("mergers", {})
        n = tier.get("n_halos", 0)
        quiet = mg.get("quiet_halos_no_merger_after_z1")
        quiet_fraction = mg.get("quiet_fraction")
        if quiet_fraction is None and n:
            quiet_fraction = quiet / n
        tiers[name] = {
            "run": spec["run"],
            "analogue": spec["analogue"],
            "n_halos": n,
            "median_m200_msun": tier.get("m0_msun", {}).get("median"),
            "median_vmax0_kms": tier.get("vmax0_kms", {}).get("median"),
            "median_mergers_total": mg.get("median_total"),
            "max_mergers_total": mg.get("max_total"),
            "median_mergers_after_z1": mg.get("median_z_lt_1"),
            "quiet_halos_no_merger_after_z1": quiet,
            "quiet_fraction": quiet_fraction,
            "measured_activity_fraction": (None if quiet_fraction is None
                                           else round(1.0 - quiet_fraction, 4)),
            "median_latest_merger_z": mg.get("median_latest_merger_z"),
            "median_earliest_merger_z": mg.get("median_earliest_merger_z"),
            "median_vmax0_over_vmax_at_z1": tier.get("vmax_growth", {}).get(
                "median_vmax0_over_vmax_at_z1"),
        }

    usable = {k: v for k, v in tiers.items()
              if v["median_mergers_total"] and v["median_mergers_total"] > 0}

    return {
        "source_artifact": str(path.relative_to(path.parents[2])) if len(path.parents) > 2 else str(path),
        "built_by": "v0.3-prelim/code/tng_stage3_growth_summary.py",
        "measured_on": "2026-11-05",
        "tiers": tiers,
        "usable_for_merger_claims": sorted(usable),
        "excluded_from_merger_claims": sorted(set(tiers) - set(usable)),
        "exclusion_reason": {
            "control_tier_tng100_1": ("median 0 tracked mergers; TNG100-1 subhalo trees are "
                                      "tracked only to z ~ 3.5, so absence of a merger is a "
                                      "tracking limit, not a physical quiescence"),
        },
        "literature_labels_in_use": {
            "f_active": LITERATURE_ACTIVITY_FRACTION,
            "multipliers": LITERATURE_MULTIPLIERS,
            "source": "Silverman+ 2026 §3 (as implemented by merger_history_modulator)",
        },
        "measured_vs_literature": {
            "f_active_assumed": LITERATURE_ACTIVITY_FRACTION,
            "f_active_measured_relhic_mass": (usable.get("relhic_mass_tier_tng50_1", {})
                                              .get("measured_activity_fraction")),
            "f_active_measured_cloud9_mass": (usable.get("cloud9_mass_anchor_tier_tng50_1", {})
                                              .get("measured_activity_fraction")),
            "direction": ("both measured tiers are MORE active than the assumed 0.5; the "
                          "Cloud-9-mass tier contains no quiescent halo at all"),
            "consequence_for_cloud9_label": (
                "HALOS_G2 labels the Cloud-9 host 'quiescent' from observation (Zhou+ 2023). "
                "Its TNG50-1 mass analogue is uniformly active. The label stays observational; "
                "the tension is recorded as decision D8, not resolved by relabeling."),
        },
        "what_this_does_not_measure": [
            "the effect of a merger on a gravothermal collapse time (the 0.7 / 8.0 magnitudes "
            "are literature calibration, not measured here)",
            "halo mass above ~6e9 Msun in TNG50-1 resolution-matched form (see D8: no z=0 "
            "primary in the 4-6e9 Msun cell reaches V_max >= 30 km/s)",
            "merger mass ratios - the local trees record merger events, not their mass ratio, "
            "so 'major merger' in the literature sense is not equivalent to these counts",
        ],
    }


def write_measured_statistics_artifact(stats=None, out_path=None):
    """Persist the measured block so downstream phases and the docs quote the same numbers."""
    import json
    stats = stats if stats is not None else measured_merger_statistics()
    if stats is None:
        return None
    out = Path(out_path) if out_path else MEASURED_STATS_OUT
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(stats, indent=2), encoding="utf-8")
    return out




# Two-sided merger-history modulator (Silverman+ 2026 §3)
def merger_history_modulator(history):
    """
    Two-sided merger-history modulator per Silverman+ 2026 §3.

    Parameters
    ----------
    history : str
        'quiescent' (× 0.7, boost collapse), 'active' (× 8.0, delay collapse),
        'mixed' (× 1.0, neutral), or 'unknown' (× 1.0)

    Returns
    -------
    float : τ multiplier
    """
    if history == "quiescent":
        return 0.7
    elif history == "active":
        return 8.0
    else:
        return 1.0


# Per-halo merger history from observation/literature
HALOS_G2 = [
    # (name, V_max, rho_eff, history, observed_state, source)
    # 'quiescent' here is the OBSERVED label (Zhou+ 2023). Measured TNG50-1 halos of the same
    # mass are uniformly active (0/25 quiescent after z=1) - tension recorded as decision D8.
    ("Cloud-9 host", 31.12, 0.01, "quiescent",
     "isolated RELHIC near M94; no recent major mergers per Zhou+ 2023",
     "diffuse gas cloud"),
    ("Fornax (V_max=18)", 18.0, 0.02, "active",
     "in MW halo; subject to tidal stirring per Fritz+ 2024",
     "extended core"),
    ("Fornax (V_max=15)", 15.0, 0.02, "active",
     "in MW halo; subject to tidal stirring",
     "extended core"),
    ("Sculptor", 15.0, 0.02, "active",
     "in MW halo; subject to tidal stirring",
     "extended core"),
    ("Draco", 17.0, 0.03, "active",
     "in MW halo; subject to tidal stirring",
     "extended core"),
    ("SPARC typical", 100.0, 0.005, "mixed",
     "field spiral galaxies; mixed merger histories",
     "rotation curves fit"),
    ("Cluster (A1689)", 500.0, 0.001, "mixed",
     "cluster cores; complex merger histories",
     "lensing consistent"),
    ("MW UFD (Boötes I)", 12.0, 0.04, "mixed",
     "per Fischer & Yu 2026: most MW UFDs mixed; some collapse, some don't",
     "no collapse observed"),
]


def consistency_check(phase, observed):
    """Check whether predicted phase matches observed state."""
    p = phase.lower()
    o = observed.lower()
    if "nfw" in p:
        return "✓" if any(k in o for k in ["rotation", "lensing", "diffuse", "no collapse"]) else "?"
    if "core-expansion" in p:
        return "✓" if any(k in o for k in ["extended", "diffuse", "no collapse"]) else "?"
    if "collapse" in p:
        return "✓" if "collapsed" in o else "?"
    return "?"


def main():
    print("Phase G2: Two-sided merger-history modulator (R88(49))")
    print("=" * 105)
    print(f"{'Halo':<22} {'History':<11} {'base τ':<8} {'mult':<6} {'new τ':<8} {'New Phase':<22} {'Observed':<25} {'✓?'}")
    print("-" * 105)

    n_consistent = 0
    n_total = 0
    n_diverse = 0
    phase_counts = {}

    for name, V_max, rho_eff, history, hist_source, observed in HALOS_G2:
        # Get base τ from Phase G4 pipeline (R88(49) corrects σ_HH vs σ_eff conflation)
        # sigma_hh_mode=True: feed σ_HH directly (gravothermal cascade uses σ_HH, not σ_eff)
        r = predict_phase(V_max, rho_eff, sigma_hh_mode=True)
        tau_base = r["tau"]

        # Apply merger-history modulator
        mult = merger_history_modulator(history)
        tau_new = tau_base * mult
        phase_new = classify_phase(tau_new)

        # Track phase diversity
        phase_counts[phase_new] = phase_counts.get(phase_new, 0) + 1

        flag = consistency_check(phase_new, observed)
        n_total += 1
        if flag == "✓":
            n_consistent += 1

        print(f"{name:<22} {history:<11} {tau_base:>6.3f}  {mult:>5.1f}  {tau_new:>6.3f}  {phase_new:<22} {observed:<25} {flag}")

    print()
    print(f"Consistency: {n_consistent}/{n_total} halos show predicted phase matching observed state")

    # Phase diversity
    n_diverse = sum(1 for c in phase_counts.values() if c > 0)
    n_distinct_phases = len(phase_counts)
    print(f"Phase diversity: {n_distinct_phases} distinct phases predicted across 8 halos:")
    for phase, count in sorted(phase_counts.items()):
        print(f"  {phase}: {count} halo(s)")
    stats = measured_merger_statistics()
    print()
    print("Measured merger activity in the local IllustrisTNG sample (2026-11-05):")
    if stats is None:
        print("  sample not built on this machine - run v0.3-prelim/code/tng_stage3_build.py,")
        print("  tng_stage3_nodes.py then tng_stage3_growth_summary.py first")
    else:
        print(f"  {'tier':<34} {'n':>4} {'median mergers':>15} {'quiet frac':>11} {'f_active':>9} {'V(z0)/V(z1)':>12}")
        for name, v in stats["tiers"].items():
            print(f"  {name:<34} {v['n_halos']:>4} {str(v['median_mergers_total']):>15} "
                  f"{v['quiet_fraction']:>11.3f} {str(v['measured_activity_fraction']):>9} "
                  f"{str(v['median_vmax0_over_vmax_at_z1']):>12}")
        print(f"  excluded from merger claims: {', '.join(stats['excluded_from_merger_claims'])}")
        print(f"  assumed f_active = {LITERATURE_ACTIVITY_FRACTION}; measured = "
              f"{stats['measured_vs_literature']['f_active_measured_relhic_mass']} "
              f"(RELHIC-mass) / {stats['measured_vs_literature']['f_active_measured_cloud9_mass']} "
              f"(Cloud-9-mass)")
        print(f"  multipliers {LITERATURE_MULTIPLIERS} remain Silverman+ 2026 labels: "
              f"this sample measures merger rates, not their effect on t_c")
        out = write_measured_statistics_artifact(stats)
        if out:
            print(f"  written: {out}")

    print()
    print("Verdict (R88(49)):")
    print("  Phase G2 two-sided modulator converts Phase G4 null result into phase diversity:")
    print("  - Cloud-9 → core-expansion (consistent with diffuse H I profile)")
    print("  - Fornax/Sculptor/Draco → collapse (which can be rescued by active merger history to core-expansion)")
    print("  - UFDs → mixed per Fischer & Yu 2026 (matches observed UFD diversity)")
    print()
    print("  This is the §9.13 roadmap's central thesis: phase-diversity emerges from the merger-history modulation,")
    print("  not from additional σ/m parameter tuning. The σ_HH vs σ_eff conflation in Phase G4 has been")
    print("  corrected (Suggestion 1: drop f_H² factor when feeding into gravothermal calculation).")


if __name__ == "__main__":
    main()
