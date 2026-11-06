"""
T120 constraint scoreboard — single-source producer (F18 / D9, 2026-11-05).

WHY THIS FILE EXISTS
--------------------
The T120.4 / T120.11 / T120.13 / T120.15 test suites used to assert, in prose and
in code, that "all constraints pass" / "all 8 points pass" / "Phase 44 joint fit
still passes". Those assertions were hard-coded literals; they did not call a
producer that measures the physics. When the producers were re-run the claims were
false (finding F18, decision D9 in docs/INTEGRITY_FINDINGS_2026-11-04.md):

  * Cloud-9 (v=28) sigma/m is 88.02 (w1=2), 100.04 (default), 106.81 (w1=5) and
    99.75-99.89 (a_slope 0.5-1.5) against a stated floor of >= 100;
  * dSph (v=15) sigma/m is 1.132 (default) against a stated ceiling of <= 0.8;
  * the "v1.13 passes all 8 points" arm measures 6 of 8 at a_slope=1.0;
  * the claimed two-component mechanism ratio "~2.9" measures 2.2511.

This module is the ONE place that turns the producers' raw sigma/m values into a
PASS / MARGINAL / FAIL tally, mirroring the F16 channel-taxonomy fix
(scripts/canonical_numbers.py + v0.3-prelim/tests/test_channel_taxonomy_single_source.py).
No physics is re-implemented here: every value comes from the existing producers
``t120_4_joint_fit.joint_fit_full_evaluation`` (the 8-observation v1.13 entry point)
and ``t120_4_joint_fit.joint_fit_evaluation`` (the 4-constraint entry point).

PRODUCER DISCREPANCY — MEASURED, DISCLOSED (not silently reconciled)
-------------------------------------------------------------------
A ~0.235% gap between "Cloud-9 = 100.0361" and "Cloud-9 = 99.80" has been quoted as
a disagreement between the two producer entry points. It is NOT one. Measured in this
task with the repo venv (Python 3.12, numpy 2.5.2, scipy 1.18.1):

    joint_fit_evaluation()["Cloud-9"]                         = 100.03606419810939
    joint_fit_full_evaluation(a_slope_override=None)["v28.0_Cloud-9"] = 100.03606419810939
    joint_fit_evaluation(a_slope_override=1.0)["Cloud-9"]      = 99.80168969102034
    joint_fit_full_evaluation(a_slope_override=1.0)["v28.0_Cloud-9"]  = 99.80168969102034

At EQUAL a_slope the two entry points agree to a relative difference of exactly 0.0.
The 0.2348% gap is entirely the a_slope parameter: the Phase-44 best-fit default
a_slope = 1.928675 (giving 100.0361) versus the v1.13 override a_slope = 1.0 (giving
99.8017). Which entry point a test uses therefore does NOT change any Cloud-9
verdict; which a_slope it uses does. The 8-observation family uses
joint_fit_full_evaluation; the 4-constraint family uses joint_fit_evaluation; both
must pass the SAME a_slope for their shared points to agree.
"""
from __future__ import annotations

from pathlib import Path
import sys

_CODE_DIR = Path(__file__).resolve().parent
if str(_CODE_DIR) not in sys.path:
    sys.path.insert(0, str(_CODE_DIR))

from t120_4_joint_fit import (  # noqa: E402
    joint_fit_evaluation,
    joint_fit_full_evaluation,
)


# ============================================================================
# DECLARED TOLERANCES — the ONLY mechanism that can score a bound-miss as
# anything other than FAIL. Bounds themselves are never moved (D9 rule 3).
# ============================================================================
#
# MARGINAL_BAND_RELATIVE: a value that misses its stated bound by at most this
# FRACTION of the bound is scored MARGINAL, not FAIL. Justification: the Phase-44
# sigma/m parameterisation plus the two-component / gravothermal reduction carry a
# modelling spread that is not smaller than a fraction of a percent, so a miss of
# <= 5 % of the bound is a declared near-miss, not a clean violation.
#
# 5 % is deliberately WIDER than every near-miss actually observed in the T120
# family (the Cloud-9 near-misses are 0.198 % at a_slope=1.0 and 0.247 % at
# a_slope=0.5), and NARROWER than every genuine violation: the smallest UFD
# violation is 21.1 % over (dSph/v=3 at a_slope=1.0, 0.9686 vs 0.8) and the
# smallest non-UFD violation is 41.8 % over (dSph v=15 at a_slope=1.93, 1.1347 vs
# 0.8). The band therefore cannot be tuned to turn a real violation into a
# MARGINAL, and it cannot be widened without admitting the smallest real
# violation -- the observed data sit in a clean gap either side of it.
MARGINAL_BAND_RELATIVE = 0.05

# Float-comparison floor for the relative shortfall, so a value that equals its
# bound to within np.float64 round-off is PASS, not a spurious MARGINAL.
_REL_EPS = 1e-12


# ============================================================================
# Observation table — the 8 v1.13 points, keyed to the producer's output keys.
# (key, label, kind, bound).  kind in {"ceiling", "floor", "band"}:
#   ceiling : value must be <= bound
#   floor   : value must be >= bound
#   band    : bound is (lo, hi); value must satisfy lo <= value <= hi
# These bounds are the ones the retired tests stated; they are NOT re-derived here.
# ============================================================================
OBSERVATIONS = (
    ("v3.0_extreme_UFD",      "UFD v=3 km/s (extreme)",   "ceiling", 0.8),
    ("v5.0_UFD",              "UFD v=5 km/s",             "ceiling", 0.8),
    ("v7.0_edge_UFD",         "UFD v=7 km/s (edge)",      "ceiling", 0.8),
    ("v10.0_UFD",             "UFD v=10 km/s",            "ceiling", 0.8),
    ("v15.0_classical_dSph",  "classical dSph v=15 km/s", "ceiling", 0.8),
    ("v28.0_Cloud-9",         "Cloud-9 v=28 km/s",        "floor",   100.0),
    ("v100.0_SPARC",          "SPARC v=100 km/s",         "band",    (0.05, 0.5)),
    ("v500.0_cluster",        "cluster v=500 km/s",       "ceiling", 1.0),
)

_UNITS = "cm^2/g"

# Bound provenance (finding F21, 2026-11-06). Read from the local verified PDFs, not from memory.
#   Horigome+ 2025 (arXiv:2503.13650): "we obtain 95%-percentile upper limits of 0.8 cm2/g for
#     w = 10 km/s and 0.04 cm2/g for the velocity-independent case" (extracted line 261-262). The
#     0.8 ceiling below is therefore published; the per-bin 0.155/0.093/0.067/0.047/0.032 values in
#     T205_full_likelihood_published.py are this project's own splitting of that limit across
#     velocity bins (its docstring says so) and must not be quoted as five separate measurements.
#   Cloud-9 (arXiv:2406.18643 + arXiv:2608.04362): NO published floor at 100 or 128 (see docstring
#     and code/t120_cloud9_bound.py). INTERNAL.
#   Lelli+ 2016 SPARC band: the T120 family uses (0.05, 0.5); the paper's 8-channel table uses
#     0.1-0.5. The framework's value passes both, but the two families disagree on the lower edge.
#   Cluster: the T120 family uses < 1.0; the canonical published channel (Randall+ 2008-like) uses
#     2.5e-4 +/- 5e-4 in T205. The framework's 2.5e-6 passes both, but the T120 bound is ~4000x
#     looser than the project's own published-likelihood bound and must not be quoted as strict.
BOUND_PROVENANCE = {
    "v3.0_extreme_UFD": "published: Horigome+ 2025 95% upper limit 0.8 cm^2/g (w=10 km/s)",
    "v5.0_UFD": "published: Horigome+ 2025 95% upper limit 0.8 cm^2/g (w=10 km/s)",
    "v7.0_edge_UFD": "published: Horigome+ 2025 95% upper limit 0.8 cm^2/g (w=10 km/s)",
    "v10.0_UFD": "published: Horigome+ 2025 95% upper limit 0.8 cm^2/g (w=10 km/s)",
    "v15.0_classical_dSph": "published: Horigome+ 2025 95% upper limit 0.8 cm^2/g (w=10 km/s)",
    "v28.0_Cloud-9": "INTERNAL (F21): project working anchor; no published Cloud-9 floor exists",
    "v100.0_SPARC": "published band (Lelli+ 2016); T120 lower edge 0.05 vs paper 0.1",
    "v500.0_cluster": "INTERNAL in this family: T120 uses <1.0 while T205 uses 2.5e-4 (Randall+ 2008)",
}

# The 4-point entry point keys its results differently; map them onto the same provenance so the
# two families can never disagree about where a bound came from.
_FOUR_TO_EIGHT = {
    "Cloud-9": "v28.0_Cloud-9",
    "dSph": "v15.0_classical_dSph",
    "SPARC": "v100.0_SPARC",
    "cluster": "v500.0_cluster",
}


# ============================================================================
# OWNER-DECLARED MODEL ARM (decision recorded 2026-11-06, owner K Lam)
# ============================================================================
# "adopt 0.5-0.8; keep 100" -- the dwarf-compatible arm is the project's declared
# model arm for the T120 family, and the Cloud-9 floor stays at 100 cm^2/g.
#
# Consequence stated honestly rather than hidden: under the adopted arm the Cloud-9
# floor is MISSED, not passed (99.7529 at a_slope=0.5 and 99.7784 at a_slope=0.8
# against the retained 100.0 floor, i.e. 0.2471 % and 0.2216 % short). Both misses
# fall inside the declared MARGINAL_BAND_RELATIVE = 0.05 above, so the scoreboard
# scores them MARGINAL, not PASS and not FAIL. The Phase-44 best-fit default
# a_slope = 1.9286750353457855 reaches 100.0361 (PASS on Cloud-9) but scores only
# 3 of 8 overall, and is therefore reported below as the LEGACY arm, not the headline.
ADOPTED_A_SLOPE_ARMS = (0.5, 0.8)
LEGACY_A_SLOPE_ARMS = (None, 1.0)  # None = producer default 1.9286750353457855
ADOPTION_NOTE = (
    "owner decision 2026-11-06: model arm = a_slope 0.5-0.8 (dwarf-compatible); "
    "Cloud-9 bar retained at 100 cm^2/g as an INTERNAL yardstick (F21)"
)


def _cloud9_shortfall(scoreboard):
    obs = scoreboard["observations"]["v28.0_Cloud-9"]
    value, bound = obs["value"], float(obs["bound"])
    return (bound - value) / bound if value < bound else 0.0


def adopted_arm_declaration():
    """Machine-readable declaration of which arm is 'the model', computed live."""
    arms = []
    for a in ADOPTED_A_SLOPE_ARMS:
        sb = constraint_scoreboard(a_slope_override=a)
        arms.append({
            "a_slope": a,
            "role": "adopted",
            "n_pass": sb["summary"]["n_pass"],
            "n_marginal": sb["summary"]["n_marginal"],
            "n_fail": sb["summary"]["n_fail"],
            "n_total": sb["summary"]["n_total"],
            "cloud9_value_cm2_per_g": sb["observations"]["v28.0_Cloud-9"]["value"],
            "cloud9_verdict": sb["observations"]["v28.0_Cloud-9"]["verdict"],
            "cloud9_shortfall_fraction": _cloud9_shortfall(sb),
            "parameter_set": sb["summary"]["parameter_set"],
        })
    legacy = []
    for a in LEGACY_A_SLOPE_ARMS:
        sb = constraint_scoreboard(a_slope_override=a)
        legacy.append({
            "a_slope": a,
            "role": "legacy_default_fit" if a is None else "legacy_v113_override",
            "n_pass": sb["summary"]["n_pass"],
            "n_marginal": sb["summary"]["n_marginal"],
            "n_fail": sb["summary"]["n_fail"],
            "n_total": sb["summary"]["n_total"],
            "cloud9_value_cm2_per_g": sb["observations"]["v28.0_Cloud-9"]["value"],
            "cloud9_verdict": sb["observations"]["v28.0_Cloud-9"]["verdict"],
            "cloud9_shortfall_fraction": _cloud9_shortfall(sb),
            "parameter_set": sb["summary"]["parameter_set"],
        })
    return {
        "adopted_arms": arms,
        "legacy_arms": legacy,
        "cloud9_bound_cm2_per_g": float(dict(OBSERVATIONS and [(o[0], o[3]) for o in OBSERVATIONS])["v28.0_Cloud-9"]),
        "cloud9_bound_provenance": BOUND_PROVENANCE["v28.0_Cloud-9"],
        "marginal_band_relative": MARGINAL_BAND_RELATIVE,
        "note": ADOPTION_NOTE,
    }


# The declaration is also emitted as an artifact, for two reasons: (1) headline docs must point at
# a file rather than assert a tally in prose (drift_guard's F16 rule requires the claim's own line
# to carry an artifact pointer), and (2) the numbers a doc quotes then have a byte-checkable source.
RESULTS_DIR = Path(__file__).resolve().parents[1] / "data" / "results"
ADOPTION_ARTIFACT = RESULTS_DIR / "t120_adopted_arm_declaration.json"


def write_adoption_artifact():
    """Regenerate the adopted-arm declaration from the live producers and write it to disk."""
    import json

    payload = adopted_arm_declaration()
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    with open(ADOPTION_ARTIFACT, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(payload, fh, indent=2, sort_keys=True)
        fh.write("\n")
    return payload


def _nearest_band_bound(value, bound):
    """For a band (lo, hi), return the endpoint nearest to `value` in relative terms."""
    lo, hi = bound
    d_lo = abs(value - lo) / lo
    d_hi = abs(value - hi) / hi
    return lo if d_lo <= d_hi else hi


def _score_one(value, kind, bound):
    """Return (verdict, ratio_to_bound) for one observation.

    verdict in {"PASS", "MARGINAL", "FAIL"}. ratio_to_bound = value / bound for a
    ceiling or floor; for a band it is value / (nearest endpoint).
    """
    if kind == "ceiling":
        ratio = value / bound
        if value <= bound * (1.0 + _REL_EPS):
            return "PASS", ratio
        rel = (value - bound) / bound
    elif kind == "floor":
        ratio = value / bound
        if value >= bound * (1.0 - _REL_EPS):
            return "PASS", ratio
        rel = (bound - value) / bound
    elif kind == "band":
        lo, hi = bound
        nearest = _nearest_band_bound(value, bound)
        ratio = value / nearest
        if lo * (1.0 - _REL_EPS) <= value <= hi * (1.0 + _REL_EPS):
            return "PASS", ratio
        rel = min(abs(value - lo) / lo, abs(value - hi) / hi)
    else:
        raise ValueError(f"unknown kind: {kind!r}")
    return ("MARGINAL" if rel <= MARGINAL_BAND_RELATIVE else "FAIL"), ratio


def _parameter_label(a_slope_override, w_list):
    if a_slope_override is None:
        base = "phase44_default_a_slope (producer default, joint_fit_full_evaluation(a_slope_override=None))"
    else:
        base = f"a_slope_override={a_slope_override}"
    if w_list is not None:
        base += f", w_list={list(w_list)}"
    return base


# ============================================================================
# Public API
# ============================================================================

def constraint_scoreboard(a_slope_override=None, w_list=None):
    """Compute the measured constraint scoreboard from the existing producers.

    Parameters
    ----------
    a_slope_override : float or None
        Forwarded to ``joint_fit_full_evaluation``. None uses the Phase-44
        best-fit a_slope (the producer default).
    w_list : sequence or None
        Forwarded as the Gaussian BW widths. None uses the producer default.

    Returns
    -------
    dict with:
      "observations" : {key: {"label", "value", "bound", "kind",
                              "verdict" (PASS|MARGINAL|FAIL), "ratio_to_bound"}}
      "summary"      : {"n_pass", "n_marginal", "n_fail", "n_total",
                        "parameter_set", "tolerance_label", "units"}
    """
    if w_list is None:
        ev = joint_fit_full_evaluation(a_slope_override=a_slope_override)
    else:
        ev = joint_fit_full_evaluation(w_list=w_list, a_slope_override=a_slope_override)

    observations = {}
    tally = {"PASS": 0, "MARGINAL": 0, "FAIL": 0}
    for key, label, kind, bound in OBSERVATIONS:
        value = float(ev[key])
        verdict, ratio = _score_one(value, kind, bound)
        tally[verdict] += 1
        observations[key] = {
            "label": label,
            "value": value,
            "bound": list(bound) if kind == "band" else bound,
            "kind": kind,
            "verdict": verdict,
            "ratio_to_bound": ratio,
            "bound_provenance": BOUND_PROVENANCE[key],
        }

    summary = {
        "n_pass": tally["PASS"],
        "n_marginal": tally["MARGINAL"],
        "n_fail": tally["FAIL"],
        "n_total": len(OBSERVATIONS),
        "parameter_set": _parameter_label(a_slope_override, w_list),
        "tolerance_label": MARGINAL_BAND_RELATIVE,
        "units": _UNITS,
    }
    return {"observations": observations, "summary": summary}


def four_constraint_scoreboard(a_slope_override=None, w_list=None):
    """Scoreboard for the 4-constraint entry point ``joint_fit_evaluation``.

    Kept separate so the 4-point and 8-point views are never conflated. The shared
    points (Cloud-9, dSph, SPARC, cluster) must carry the SAME value here as in
    ``constraint_scoreboard`` at the same a_slope -- the two producers agree exactly
    at equal a_slope (see module docstring).
    """
    if w_list is None:
        ev = joint_fit_evaluation(a_slope_override=a_slope_override)
    else:
        ev = joint_fit_evaluation(w_list=w_list, a_slope_override=a_slope_override)

    spec = (
        ("Cloud-9", "Cloud-9 v=28 km/s", "floor", 100.0),
        ("dSph",    "classical dSph v=15 km/s", "ceiling", 0.8),
        ("SPARC",   "SPARC v=100 km/s", "band", (0.05, 0.5)),
        ("cluster", "cluster v=500 km/s", "ceiling", 1.0),
    )
    observations = {}
    tally = {"PASS": 0, "MARGINAL": 0, "FAIL": 0}
    for key, label, kind, bound in spec:
        value = float(ev[key])
        verdict, ratio = _score_one(value, kind, bound)
        tally[verdict] += 1
        observations[key] = {
            "label": label, "value": value,
            "bound": list(bound) if kind == "band" else bound,
            "kind": kind, "verdict": verdict, "ratio_to_bound": ratio,
            "bound_provenance": BOUND_PROVENANCE[_FOUR_TO_EIGHT[key]],
        }
    summary = {
        "n_pass": tally["PASS"], "n_marginal": tally["MARGINAL"], "n_fail": tally["FAIL"],
        "n_total": len(spec),
        "parameter_set": _parameter_label(a_slope_override, w_list),
        "tolerance_label": MARGINAL_BAND_RELATIVE, "units": _UNITS,
    }
    return {"observations": observations, "summary": summary}


if __name__ == "__main__":
    payload = write_adoption_artifact()
    print(f"wrote {ADOPTION_ARTIFACT}")
    for a in (None, 0.5, 0.8, 1.0, 1.2, 1.5, 1.93):
        sb = constraint_scoreboard(a_slope_override=a)
        s = sb["summary"]
        print(f"{s['parameter_set']:<72} "
              f"PASS={s['n_pass']} MARGINAL={s['n_marginal']} FAIL={s['n_fail']} / {s['n_total']}")
        for k, o in sb["observations"].items():
            print(f"    {k:<24} {o['value']:>12.6f}  {o['kind']:<8} "
                  f"{str(o['bound']):<14} {o['verdict']}")
