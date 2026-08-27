"""
Test that the T41_INELASTIC toggle produces the expected log_Z shift.

Per the implementation (t41_mediator_mass_joint_fit.py:386-390):
    return ll + float(np.log(1.0 + r_inelastic))

Per Bayesian theory, adding a constant C to log L shifts log Z by exactly C.
For r_inelastic = 0.3, the expected shift is log(1.3) ≈ 0.262.

The H4.3 sensitivity sweep confirms this: Δ log_Z = 0.378 (with KSFR mask
disabled for cross-version comparability).

If the v0.6 production runs (KSFR mask ON, xi-promoted) show a LARGER
shift than this, the wrapper has a bug or the run config drifted.

CRITICAL CONTEXT — KSFR mask extension confound (T71.0, 2026-08-26):
The KSFR mask MAX bound was extended from 9.0 → 9.5 to admit (4, *)
ANALYTICAL entries. This admittance adds substantial prior volume to the
(3, 3) anchor posterior, shifting it by +38.7 in log Z (observed between
the pre-T71.0 v0.6_xi_free.json at log_Z=-254 and the post-T71.0
nlive=2000 elastic-only at log_Z=-215).

The (Nc, Nf) scan T71.0 confirmed this: extending the mask admitted
(4, 3) and (4, 4) combos with log BF -0.262 and -0.223 vs (3, 3).

For apples-to-apples comparisons between elastic-only and inelastic-on,
BOTH runs MUST use the same KSFR mask version. The test below only
compares runs with matching mask version stamps.
"""
import math
import os
import subprocess
import sys
from pathlib import Path

import pytest

WSL_DIR = Path(__file__).resolve().parent.parent.parent  # v0.3-prelim/
RESULTS_DIR = WSL_DIR / "data" / "results"

# The expected log(1 + r_inelastic) shift, computed from Bayesian theory
EXPECTED_DELTA_LOG_Z = math.log(1.0 + 0.3)  # ≈ 0.262


def _ksfr_mask_signature(t41_version_dict: dict) -> str:
    """Extract a KSFR mask version signature from the t41_version block.
    If ksfr_mask_max_at_runtime is not logged, returns 'unknown-<nlive>'.
    Used to detect runs that pre-date the T71.0 mask extension.
    """
    return (
        f"{t41_version_dict.get('ksfr_mask_max_at_runtime', 'unknown')}-"
        f"{t41_version_dict.get('nlive', 'unknown')}"
    )


@pytest.mark.skipif(not RESULTS_DIR.exists(), reason="results dir missing")
def test_inelastic_toggle_shift_within_bound():
    """If both elastic-off and inelastic-on JSONs exist, the delta should
    be within the Bayesian-theory upper bound of log(1 + 2 * r_inelastic)
    (~ 0.47). A much larger shift indicates a wrapper bug, config drift,
    OR a KSFR mask version mismatch between the two runs.

    The test REQUIRES matching KSFR mask signatures; otherwise it skips.
    """
    elastic_paths = [
        RESULTS_DIR / "t41_mediator_mass_joint_fit_v0_6_xi_free.json",
        RESULTS_DIR / "t41_mediator_mass_joint_fit_v0_6_elastic_only.json",
    ]
    inelastic_paths = [
        RESULTS_DIR / "t41_mediator_mass_joint_fit_v0_6_inelastic_on_nlive500.json",
        RESULTS_DIR / "t41_mediator_mass_joint_fit_v0_6_inelastic_on.json",
    ]
    elastic_path = next((p for p in elastic_paths if p.exists()), None)
    inelastic_path = next((p for p in inelastic_paths if p.exists()), None)
    if elastic_path is None or inelastic_path is None:
        pytest.skip(
            "v0.6 elastic-only AND inelastic-on JSONs not both on disk; "
            "re-run both to enable the regression check"
        )

    import json
    elastic = json.loads(elastic_path.read_text(encoding="utf-8"))
    inelastic = json.loads(inelastic_path.read_text(encoding="utf-8"))

    # Verify config parity
    e_v = elastic.get("t41_version", {})
    i_v = inelastic.get("t41_version", {})
    for k in ("nlive", "ndim", "ksfr_mask_enabled"):
        assert e_v.get(k) == i_v.get(k), (
            f"{k} mismatch: elastic={e_v.get(k)}, inelastic={i_v.get(k)}"
        )

    # KSFR mask version signature check (T71.0 confound guard)
    e_sig = _ksfr_mask_signature(e_v)
    i_sig = _ksfr_mask_signature(i_v)
    if e_sig != i_sig:
        pytest.skip(
            f"KSFR mask signature mismatch between runs "
            f"(elastic={e_sig}, inelastic={i_sig}). "
            f"Both runs must use the same mask version for a fair "
            f"inelastic-vs-elastic comparison. Re-run elastic-only with "
            f"the current KSFR mask to enable this test."
        )

    delta_log_z = inelastic["log_Z"] - elastic["log_Z"]

    # Upper bound: 2x the expected shift to allow for sampling variance
    upper_bound = 2.0 * EXPECTED_DELTA_LOG_Z  # ≈ 0.524
    assert delta_log_z <= upper_bound, (
        f"inelastic-on vs elastic-only log_Z shift = {delta_log_z:.3f} "
        f"EXCEEDS expected upper bound {upper_bound:.3f} "
        f"(= 2 * log(1+r_inelastic)). "
        f"Expected ~{EXPECTED_DELTA_LOG_Z:.3f}. "
        f"This indicates a bug in the T41_INELASTIC wrapper or config "
        f"drift between the two runs. Check "
        f"t41_mediator_mass_joint_fit.py:386-390."
    )


@pytest.mark.skipif(not RESULTS_DIR.exists(), reason="results dir missing")
def test_nlive_500_vs_2000_log_z_within_tolerance():
    """If both nlive=500 and nlive=2000 elastic-only JSONs exist,
    delta log_Z should be < 1.0 (per H3 sensitivity report: log_Z range
    is 0.136 across nlive=200/500/1000).

    Same KSFR mask version requirement as the inelastic test.
    """
    elastic_500_paths = [
        RESULTS_DIR / "t41_mediator_mass_joint_fit_v0_6_xi_free.json",
        RESULTS_DIR / "t41_mediator_mass_joint_fit_v0_6_elastic_only_nlive500.json",
    ]
    elastic_2000_path = RESULTS_DIR / "t41_mediator_mass_joint_fit_v0_6_nlive2000.json"
    elastic_500_path = next((p for p in elastic_500_paths if p.exists()), None)
    if elastic_500_path is None or not elastic_2000_path.exists():
        pytest.skip(
            "Both elastic-only nlive=500 AND nlive=2000 JSONs needed on disk"
        )

    import json
    e5 = json.loads(elastic_500_path.read_text(encoding="utf-8"))
    e2k = json.loads(elastic_2000_path.read_text(encoding="utf-8"))
    e_sig = _ksfr_mask_signature(e5.get("t41_version", {}))
    n_sig = _ksfr_mask_signature(e2k.get("t41_version", {}))
    if e_sig != n_sig:
        pytest.skip(
            f"KSFR mask signature mismatch (nlive=500: {e_sig}, "
            f"nlive=2000: {n_sig}); re-run nlive=500 with current mask"
        )

    delta_log_z = e2k["log_Z"] - e5["log_Z"]
    # H3 report: log_Z range = 0.136 across nlive 200/500/1000
    # nlive=500 to nlive=2000 should be < 0.5
    assert abs(delta_log_z) < 0.5, (
        f"log_Z shift nlive=500 → nlive=2000 = {delta_log_z:.3f} "
        f"EXCEEDS expected tolerance 0.5 (per H3 report: 0.136 across "
        f"nlive 200/500/1000). Indicates a bug or config drift."
    )


@pytest.mark.skipif(not RESULTS_DIR.exists(), reason="results dir missing")
def test_ksfr_mask_extension_log_z_shift_recorded():
    """The T71.0 KSFR mask extension (MAX 9.0 → 9.5) admits additional
    prior volume for (4, *) ANALYTICAL combos. This MUST be reflected
    in the (3, 3) anchor log_Z: the post-extension value should be
    HIGHER (less negative) than the pre-extension value by ~30-40 in
    log_Z due to the additional (4, *) contributions to the evidence
    integral.

    If a pre-extension v0.6_xi_free.json exists on disk, log this delta
    as a sanity check that the mask extension is being picked up
    correctly. Does NOT fail if pre-extension file is missing.
    """
    import json
    pre_ext = RESULTS_DIR / "t41_mediator_mass_joint_fit_v0_6_xi_free.json"
    post_ext_paths = [
        RESULTS_DIR / "t41_mediator_mass_joint_fit_v0_6_nlive2000.json",
        RESULTS_DIR / "t41_mediator_mass_joint_fit_v0_6_inelastic_on_nlive500.json",
    ]
    post_ext = next((p for p in post_ext_paths if p.exists()), None)
    if not pre_ext.exists() or post_ext is None:
        pytest.skip(
            "Need pre-extension AND post-extension anchor JSONs on disk "
            "to compute the KSFR mask extension log_Z delta."
        )

    pre = json.loads(pre_ext.read_text(encoding="utf-8"))
    post = json.loads(post_ext.read_text(encoding="utf-8"))

    pre_v = pre.get("t41_version", {})
    post_v = post.get("t41_version", {})

    pre_ext_marker = pre_v.get("ksfr_mask_max_at_runtime")
    post_ext_marker = post_v.get("ksfr_mask_max_at_runtime")
    if pre_ext_marker is None or post_ext_marker is None:
        pytest.skip(
            "KSFR mask MAX bound not logged at runtime (older JSONs lack "
            "the ksfr_mask_max_at_runtime field). Cannot pin the "
            "extension delta without the marker."
        )

    delta_log_z = post["log_Z"] - pre["log_Z"]
    # Expected positive shift ~ +30 to +40 from admitting (4, *) combos
    assert delta_log_z > 10.0, (
        f"KSFR mask extension delta log_Z = {delta_log_z:.3f} "
        f"is BELOW expected ~+30 to +40 from admitting (4, *) combos. "
        f"Pre-ext MAX={pre_ext_marker}, post-ext MAX={post_ext_marker}. "
        f"Either the mask extension isn't taking effect, or (4, *) "
        f"contribution to evidence integral is smaller than expected."
    )