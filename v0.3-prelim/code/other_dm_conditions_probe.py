"""other_dm_conditions_probe.py — can the same sigma/m(v) parameterisation explain OTHER dark-matter
conditions, judged against published bounds?

Built because the owner asked (2026-11-06): "i want to pursue whether the parameter of the quarter
percent can apply to explain other dm conditions". The "quarter percent" is the Cloud-9 near-miss
against this project's own >= 100 cm^2/g bar (F21 showed that bar is internal). This probe therefore
does NOT re-test the internal bar. It takes the framework's velocity-dependent sigma/m(v), evaluates
it at the velocities each *other* published system actually probes, and compares.

Every bound below is quoted from a verified KB entry under docs/papers/verified/ (arXiv id and the
line in that summary are recorded in the artifact). Nothing here is invented or paraphrased from
memory.

Conventions carried through, because the repo uses all three (F21):
  total      : t120_4_joint_fit.total_sigma_m_gaussian at the Phase-44 parameter set
  effective  : f_H^2 * total (two-component, core-forming halo at r = 0.05 r_vir)
  phase44    : the canonical published-likelihood values stored in sigma_m_phase44.json
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

_CODE_DIR = Path(__file__).resolve().parent
if str(_CODE_DIR) not in sys.path:
    sys.path.insert(0, str(_CODE_DIR))

_RESULTS_DIR = _CODE_DIR.parent / "data" / "results"
ARTIFACT = _RESULTS_DIR / "other_dm_conditions_probe.json"

import t120_4_joint_fit as T120  # noqa: E402
from t120_cloud9_bound import HALO_TYPE, R_OVER_RVIR, model_quantities  # noqa: E402

import numpy as np  # noqa: E402

PHASE44 = json.loads((_RESULTS_DIR / "sigma_m_phase44.json").read_text(encoding="utf-8"))
PHASE44_KEYS = {3.0: "v3.0_extreme_UFD", 5.0: "v5.0_UFD", 7.0: "v7.0_edge_UFD",
                10.0: "v10.0_UFD", 15.0: "v15.0_classical_dSph", 28.0: "v28.0_Cloud-9",
                100.0: "v100.0_SPARC", 500.0: "v500.0_cluster"}


# The producer scores each channel with its OWN halo type and observation radius (they are NOT the
# same for dwarf, Cloud-9, SPARC and cluster points). Using one global convention for every velocity
# silently changes the answer by up to an order of magnitude, so this table mirrors the producer's
# point list and test_t120_cloud9_bound_provenance.py pins that the mirror reproduces the producer.
T120_POINTS = {
    3.0:   ("core_collapsed", 0.20, "extreme UFD"),
    5.0:   ("core_collapsed", 0.20, "UFD"),
    7.0:   ("core_collapsed", 0.20, "edge UFD"),
    10.0:  ("core_collapsed", 0.20, "UFD"),
    15.0:  ("core_collapsed", 0.20, "classical dSph"),
    28.0:  ("core_forming", 0.05, "Cloud-9"),
    100.0: ("intermediate", 0.05, "SPARC"),
    500.0: ("core_collapsed", 0.50, "cluster"),
}

# Velocities the producer does not sample. The halo convention is declared explicitly and the
# artifact marks these rows as extensions rather than producer outputs.
EXTRAPOLATED_POINTS = {
    40.0: ("core_collapsed", 0.20, "TBTF host subhalo, Elbert+ 2015 v_rms ~ 40 km/s"),
}


def producer_values(a_slope_override=None):
    """The producer's own eight channel values (single source of truth)."""
    return T120.joint_fit_full_evaluation(a_slope_override=a_slope_override)


def model_values(v, a_slope_override=None):
    """Return the three conventions' sigma/m at velocity v (km/s), using the producer's own
    halo-type/radius convention for that velocity when the producer samples it."""
    p44 = _load_phase44_cached()
    a_slope = a_slope_override if a_slope_override is not None else p44["a_slope"]
    sigma_HH = T120.total_sigma_m_gaussian(
        v, T120.T120_4_V_TARGETS, T120.T120_4_SIGMA_PEAKS,
        T120.T120_4_W_LIST_DEFAULT, p44["sigma_0"], a_slope,
    )
    total = float(np.atleast_1d(sigma_HH)[0])
    if v in T120_POINTS:
        halo_type, r, _lbl = T120_POINTS[v]
        kind = "producer_point"
    elif v in EXTRAPOLATED_POINTS:
        halo_type, r, _lbl = EXTRAPOLATED_POINTS[v]
        kind = "extension"
    else:
        raise ValueError(f"no declared halo convention for v={v}")
    effective = float(T120.sigma_eff_two_comp(v, total, halo_type, r))
    phase44 = PHASE44[PHASE44_KEYS[v]] if v in PHASE44_KEYS else None
    return {"total_cm2_per_g": total, "effective_cm2_per_g": effective,
            "phase44_stored_cm2_per_g": phase44,
            "halo_type": halo_type, "r_over_rvir": r, "point_kind": kind}


def _load_phase44_cached():
    global _PHASE44_PARAMS
    if _PHASE44_PARAMS is None:
        _PHASE44_PARAMS = T120._load_phase44_params()
    return _PHASE44_PARAMS


_PHASE44_PARAMS = None


# (the old _phase44_bg() helper was removed: model_values now reads the cached Phase-44 params,
# so there is exactly one parameter path in this file)


# ---------------------------------------------------------------------------
# Published conditions, each traced to a verified KB entry.
# kind: "ceiling" (data say sigma must be below), "floor" (data say sigma must be above),
#       "band", or "methodology" (a validity caveat rather than a bound).
# ---------------------------------------------------------------------------
CONDITIONS = [
    {
        "id": "mw_satellites_horigome",
        "system": "Milky Way satellites (Gaia DR3 kinematics + subhalo N-body)",
        "velocity_km_s": [3.0, 5.0, 7.0, 10.0, 15.0],
        "kind": "ceiling",
        "bound_cm2_per_g": 0.8,
        "source": {"arxiv": "2503.13650", "kb": "2503.13650_horigome_2025.md", "line": 16,
                   "quote": "| σ/m upper limit (w=10 km/s velocity-dep) | 0.8 cm²/g | 95% | Eq. 7, Table 1 |"},
        "note": "KB line 22 of the same entry already records the paper's own claim that this "
                "framework exceeds the Horigome+ 2025 threshold by 3.6-23.7x at v_eff = 5-20 km/s; "
                "the measurement here is an independent recomputation of that statement.",
    },
    {
        "id": "segue_streams_gilman2023",
        "system": "galaxy clusters / BCG stellar streams (relative velocities below 30 km/s)",
        "velocity_km_s": [28.0],
        "kind": "ceiling",
        "bound_cm2_per_g": 100.0,
        "source": {"arxiv": "2207.13111", "kb": "2207.13111_gilman2023.md", "line": 14,
                   "quote": "the strongest constraints obtained for cross section strengths exceeding "
                            "100 cm²/g at relative velocities below 30 km/s"},
        "note": "KB line 23 of that entry states this is a CORE-COLLAPSE TIMING constraint, not a "
                "direct sigma/m constraint: a high sigma/m is disfavored only if it makes a majority "
                "of halos core collapse. Treat the 100 as where the disfavoring begins, not a hard "
                "cutoff.",
    },
    {
        "id": "dwarf_dispersion_gilman2026",
        "system": "ultra-faint dwarf velocity dispersion (sigma at 10 km/s)",
        "velocity_km_s": [10.0],
        "kind": "floor",
        "bound_cm2_per_g": 10.0,
        "source": {"arxiv": "2610.40766", "kb": "2610.40766_gilman_2026.md", "line": 31,
                   "quote": "| Disfavored region | σ(10 km/s) < 10 cm²/g | §\"Results\" |"},
    },
    {
        "id": "dracos_core_collapse_sameie",
        "system": "Dracos dSph / subhalo core collapse",
        "velocity_km_s": [10.0],
        "kind": "floor",
        "bound_cm2_per_g": 5.0,
        "source": {"arxiv": "1904.07872", "kb": "1904.07872_sameie_2020.md", "line": 29,
                   "quote": "| σ/m threshold for core collapse | > 5 cm²/g | Sameie+ 2020 §1 |"},
        "note": "Direction check, not a demand: below this threshold the framework does not produce a "
                "core-collapsed dwarf at that velocity. Other SIDM work does build core-collapsed "
                "subhalos, at σ0/m = 147.1 cm²/g with w = 120 km/s (2610.31881 line 186).",
    },
    {
        "id": "tbtf_elbert",
        "system": "too-big-to-fail in MW-mass halos",
        "velocity_km_s": [40.0],
        "kind": "band",
        "bound_cm2_per_g": [0.5, 50.0],
        "source": {"arxiv": "1412.1477", "kb": "1412.1477_elbert_2015.md", "line": 28,
                   "quote": "| σ/m range for TBTF | [0.5, 50] cm²/g | Elbert+ 2015 §1 |"},
        "note": "Elbert+ 2015 shows what alleviates TBTF; it does not require a specific value. KB "
                "line 13 adds the sweet spot for the largest cores at 5-10 cm²/g.",
    },
    {
        "id": "macs0138_odonnell",
        "system": "MACS J0138-2155 galaxy cluster",
        "velocity_km_s": [500.0],
        "kind": "ceiling",
        "bound_cm2_per_g": 0.613,
        "source": {"arxiv": "2508.20179", "kb": "2508.20179_odonnell2025.md", "line": 14,
                   "quote": "σ/m < 0.613 cm²/g** at ⟨v_pair⟩ < 2090 km/s"},
        "note": "Evaluated at 500 km/s, the highest velocity this framework samples. sigma/m falls "
                "with velocity, so the real v_pair < 2090 km/s only strengthens the agreement.",
    },
    {
        "id": "desi_bao_zhu",
        "system": "cosmic web / DESI BAO",
        "velocity_km_s": [500.0],
        "kind": "ceiling",
        "bound_cm2_per_g": 0.2,
        "source": {"arxiv": "2610.26877", "kb": "2610.26877_zhu_2026.md", "line": 14,
                   "quote": "σ/m < 0.2 cm²/g (DESI BAO alone)"},
        "note": "The same line gives < 0.01 cm²/g with CMB priors at v_rel ~ 1000 km/s, which this "
                "framework cannot evaluate at that velocity (no sampled point there); evaluated at "
                "500 km/s. KB adjudication for this paper: CORROBORATES (conditional, "
                "model-dependent).",
    },
    {
        "id": "cloud9_optimum_ohana",
        "system": "Cloud-9 (VLA HI + UV background, cosmological c-M prior)",
        "velocity_km_s": [28.0],
        "kind": "target",
        "bound_cm2_per_g": 200.0,
        "source": {"arxiv": "2608.04362", "kb": "2608.04362_ohana_2026_cloud9_cdm_sidm.md", "line": 29,
                   "quote": "| SIDM deviation minimised at | **~3σ** for σ/m ≈ 200 cm²/g | §3.2, "
                            "Fig. 3 bottom-left |"},
        "extra_published_values": {
            "tau_018_fiducial_inferred_sigma_m_cm2_per_g": 483.0,
            "tau_018_fiducial_kb_line": 26,
            "cdm_requires_sigma_below_cM_median": 7.3,
            "cdm_kb_line": 22,
        },
        "note": "This is the published Cloud-9 preference. It is NOT the >= 100 bar the project used "
                "internally (F21): 100 and 128 are project-internal numbers, 200 (and 483 for the "
                "tau = 0.18 fiducial) are what the paper reports.",
    },
    {
        "id": "yang_family_validity_gurian",
        "system": "validity of the Yang+ 2024 gravothermal family at the Cloud-9 anchor",
        "velocity_km_s": [28.0],
        "kind": "methodology",
        "bound_cm2_per_g": None,
        "source": {"arxiv": "2610.28745", "kb": "2610.28745_gurian_2026.md", "line": 14,
                   "quote": "at **σ≲100 cm²/g** halos enter dense-core/SMFP and the Yang family "
                            "becomes inaccurate"},
        "note": "Not a bound on sigma/m: a caveat about the model family this project uses. The "
                "framework's effective value at Cloud-9 is 100.04, i.e. exactly at the boundary "
                "where Gurian+ 2026 say the Yang family stops being accurate.",
    },
]


def _classify(kind, value, bound):
    if kind == "methodology":
        return "NOT_A_BOUND"
    if kind == "ceiling":
        if value <= bound:
            return "CONSISTENT"
        return "VIOLATED" if value > 2.0 * bound else "TENSION"
    if kind == "floor":
        if value >= bound:
            return "CONSISTENT"
        return "VIOLATED" if value < 0.1 * bound else "TENSION"
    if kind == "band":
        lo, hi = bound
        return "CONSISTENT" if lo <= value <= hi else "OUTSIDE"
    if kind == "target":
        ratio = value / bound
        if 0.5 <= ratio <= 2.0:
            return "CONSISTENT"
        if 0.2 <= ratio < 0.5 or 2.0 < ratio <= 5.0:
            return "TENSION"
        return "VIOLATED"
    raise ValueError(kind)


def _verify_mirror():
    """Fail closed if this file's point table stops reproducing the producer's own values."""
    ev = producer_values()
    for v, (halo_type, r, lbl) in T120_POINTS.items():
        key = f"v{v}_{lbl.replace(' ', '_')}"
        mine = model_values(v)["effective_cm2_per_g"]
        theirs = float(ev[key])
        if abs(mine - theirs) > 1e-12 * max(1.0, abs(theirs)):
            raise AssertionError(
                f"point-table mirror drifted: v={v} {lbl}: mirror {mine!r} vs producer {theirs!r}")


def _eff(row, v):
    return row["model_at_these_velocities"][str(v)]["model"]["effective_cm2_per_g"]


def _measured_ratios(rows):
    """value / bound for every published condition that has a numeric bound (effective convention).
    >1 means the framework is above a ceiling or above a floor; <1 means below."""
    out = {}
    for row in rows:
        b = row["bound_cm2_per_g"]
        if b is None or row["kind"] == "methodology":
            continue
        if row["kind"] == "band":
            lo, hi = b
            out[row["id"]] = {str(v): {"effective": _eff(row, v),
                                       "x_above_band_low": _eff(row, v) / lo,
                                       "x_below_band_high": hi / _eff(row, v)}
                              for v in row["velocity_km_s"]}
            continue
        out[row["id"]] = {str(v): {"effective": _eff(row, v), "bound": b,
                                   "value_over_bound": _eff(row, v) / b}
                          for v in row["velocity_km_s"]}
    return out


def _headline(rows):
    """Computed from the measured rows, so this text cannot drift away from the numbers."""
    by_id = {r["id"]: r for r in rows}
    hor = _measured_ratios([by_id["mw_satellites_horigome"]])["mw_satellites_horigome"]
    gil26 = _measured_ratios([by_id["dwarf_dispersion_gilman2026"]])["dwarf_dispersion_gilman2026"]
    hor10 = hor["10.0"]["value_over_bound"]
    hor3 = hor["3.0"]["value_over_bound"]
    gil26_gap = by_id["dwarf_dispersion_gilman2026"]["bound_cm2_per_g"] / \
        by_id["mw_satellites_horigome"]["bound_cm2_per_g"]
    dwarf_ratios = [d["value_over_bound"] for d in hor.values()]
    high = [_eff(by_id["macs0138_odonnell"], 500.0) / 0.613,
            _eff(by_id["desi_bao_zhu"], 500.0) / 0.2]
    c9_eff = _eff(by_id["segue_streams_gilman2023"], 28.0)
    ohana_ratio = c9_eff / 200.0
    ohana_total_ratio = model_quantities()["Q_total_cm2_per_g"] / 200.0
    return {
        "high_velocity_systems": (
            f"CONSISTENT with large margin. At v = 500 km/s the framework gives "
            f"{_eff(by_id['macs0138_odonnell'], 500.0):.4g} cm2/g, i.e. "
            f"{1/high[0]:.0f}x below the MACS J0138 ceiling (0.613) and "
            f"{1/high[1]:.0f}x below the DESI BAO ceiling (0.2). sigma/m falls with velocity, so "
            "the agreement only strengthens at the true v_pair ~ 2090 km/s."),
        "dwarf_velocity_systems": (
            f"VIOLATED against Horigome+ 2025: the framework is {hor3:.1f}x above their 0.8 cm2/g "
            f"95% ceiling at v = 3 km/s and {hor10:.2f}x above it at v = 10 km/s "
            f"({_eff(by_id['mw_satellites_horigome'], 10.0):.4g} cm2/g)."),
        "published_dwarf_data_conflict": (
            f"The two published dwarf conditions bracket sigma/m(10 km/s) in opposite directions: "
            f"Horigome+ 2025 requires < 0.8 cm2/g while Gilman+ 2026 disfavours < 10 cm2/g, a "
            f"{gil26_gap:.1f}x contradiction. No single value — this framework's "
            f"{_eff(by_id['dwarf_dispersion_gilman2026'], 10.0):.4g} included — can satisfy both."),
        "cloud9_velocity": (
            f"At v = 28 km/s the framework gives {c9_eff:.4g} cm2/g effective "
            f"({model_quantities()['Q_total_cm2_per_g']:.4g} total). Gilman+ 2023 begin to disfavor "
            f"> 100 cm2/g below 30 km/s (ratio {c9_eff/100.0:.4f}). Ohana+ 2026's published Cloud-9 "
            f"optimum is ~200 cm2/g, so the framework is {1/ohana_ratio:.2f}x below it on the "
            f"effective convention and {1/ohana_total_ratio:.2f}x below it on the total convention "
            f"(the paper's tau = 0.18 fiducial infers 483 cm2/g)."),
        "what_the_quarter_percent_means": (
            "The 0.198-0.247% Cloud-9 near-miss is a comparison against this project's own internal "
            "bar (F21). Against published data from other systems the "
            f"dwarf-regime discrepancies run {min(dwarf_ratios):.2f}x to "
            f"{max(dwarf_ratios):.1f}x above the published ceiling, and the cluster-regime margins "
            f"run {1/max(high):.0f}x to {1/min(high):.0f}x below the published ceilings."),
    }


ARM_A_SLOPES = [0.5, 0.8, 1.0, None]  # None = the producer's own Phase-44 default


def _rows_for(a_slope):
    rows = []
    for cond in CONDITIONS:
        per_v = {}
        for v in cond["velocity_km_s"]:
            mv = model_values(v, a_slope_override=a_slope)
            numeric = {k: mv[k] for k in ("total_cm2_per_g", "effective_cm2_per_g",
                                          "phase44_stored_cm2_per_g") if mv[k] is not None}
            verdicts = {
                conv: _classify(cond["kind"], val, cond["bound_cm2_per_g"])
                for conv, val in numeric.items()
            }
            per_v[str(v)] = {"model": mv, "verdict_by_convention": verdicts}
        rows.append({**cond, "model_at_these_velocities": per_v})
    return rows


def _tally(rows):
    tally = {"CONSISTENT": 0, "TENSION": 0, "VIOLATED": 0, "OUTSIDE": 0, "NOT_A_BOUND": 0}
    for row in rows:
        for per_v in row["model_at_these_velocities"].values():
            tally[per_v["verdict_by_convention"].get("effective_cm2_per_g", "NOT_A_BOUND")] += 1
    return tally


def build():
    _verify_mirror()
    rows = _rows_for(None)
    default_a = _load_phase44_cached()["a_slope"]

    arms = {}
    for a in ARM_A_SLOPES:
        label = "default_phase44" if a is None else f"a_slope_{a}"
        arm_rows = _rows_for(a)
        arms[label] = {
            "a_slope": default_a if a is None else a,
            "tally_effective_convention": _tally(arm_rows),
            "effective_cm2_per_g_by_velocity": {
                str(v): model_values(v, a_slope_override=a)["effective_cm2_per_g"]
                for v in sorted(set(T120_POINTS) | set(EXTRAPOLATED_POINTS))
            },
        }
        if a is not None:  # the mirror must also reproduce the producer on override arms
            ev = producer_values(a_slope_override=a)
            for v, (_ht, _r, lbl) in T120_POINTS.items():
                mine = model_values(v, a_slope_override=a)["effective_cm2_per_g"]
                theirs = float(ev[f"v{v}_{lbl.replace(' ', '_')}"])
                if abs(mine - theirs) > 1e-12 * max(1.0, abs(theirs)):
                    raise AssertionError(f"arm {label} mirror drift at v={v}: {mine!r} vs {theirs!r}")

    return {
        "question": "does the framework's velocity-dependent sigma/m(v), fitted to Cloud-9 at "
                    "v = 28 km/s, also satisfy published constraints from other dark-matter systems?",
        "parameter_set": {
            "sigma_0_cm2_per_g": _load_phase44_cached()["sigma_0"],
            "a_slope": default_a,
            "resonance_targets_km_s": list(T120.T120_4_V_TARGETS),
            "f_H_squared": model_quantities()["f_H_squared"],
        },
        "conditions": rows,
        "tally_effective_convention": _tally(rows),
        "arms": arms,
        "arm_dependence": (
            "Every dwarf-velocity verdict below is an a_slope verdict as much as a sigma/m(v) verdict: "
            "the same framework with a_slope = 1.0 instead of the Phase-44 default changes the "
            "effective value at v = 3 km/s by roughly an order of magnitude, which is larger than the "
            "0.198-0.247% Cloud-9 near-miss the internal bar was measuring."),
        "measured_ratios": _measured_ratios(rows),
        "headline": _headline(rows),
    }


def main():
    report = build()
    _RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    with open(ARTIFACT, "w", encoding="utf-8") as fh:
        json.dump(report, fh, indent=2)
    print(f"wrote {ARTIFACT}")
    for row in report["conditions"]:
        for v, per_v in row["model_at_these_velocities"].items():
            eff = per_v["model"]["effective_cm2_per_g"]
            tot = per_v["model"]["total_cm2_per_g"]
            print(f"  {row['id']:<28} v={v:<6} eff={eff:>10.4g} total={tot:>10.4g} "
                  f"bound={row['bound_cm2_per_g']} -> {per_v['verdict_by_convention'].get('effective_cm2_per_g')}")
    print("tally (effective convention):", report["tally_effective_convention"])
    for label, arm in report["arms"].items():
        print(f"  arm {label:<18} a_slope={arm['a_slope']:.4f} tally={arm['tally_effective_convention']}")
    for k, v in report["headline"].items():
        print(f"  [{k}] {v}")


if __name__ == "__main__":
    main()
