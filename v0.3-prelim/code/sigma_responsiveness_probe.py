"""Measure whether a claimed ``SIDM`` rotation-curve profile actually depends on sigma/m.

Why this exists (2026-11-04, integrity sweep finding F1 / open decision D1):
``phase39_nfw_vs_sidm.py`` and ``phase40_corrected_comparison.py`` label their result
``STRONG_SIDM`` / ``WEAK_BURKERT`` from a ``v_circ_sidm*`` profile whose core radius is clamped
to ``max(r_core, 0.1*r_s)`` everywhere in the fitted grid. The consequence is that ``sigma_0``,
the resonance peak heights and ``a_slope`` never reach the rotation curve at all, so the
"SIDM" curve there is a fixed cored shape, not a self-interacting one. The verdicts therefore
compare a cored profile against a cuspy NFW one; they are not evidence about SIDM.

That was previously a *prose disclosure*. This module turns it into a measurement that the
producers run on themselves and store in their own artifacts, so the disclosure cannot drift
away from the code: if somebody fixes the core-radius formula so that sigma/m really does
propagate, the probe stops reporting "inert" and the scope sentence changes automatically.

The probe is deliberately generic — it takes any function of ``(sigma_0, r)`` — so it can also
prove that a profile which *should* respond does respond (see
``v0.3-prelim/tests/test_sigma_responsiveness_probe.py``), which is what keeps this guard from
being a vacuous "always inert" check.
"""
from __future__ import annotations

import numpy as np

# Multiplicative scalings applied to the producer's own sigma_0. Chosen to span far more than
# any plausible systematic: a responsive profile cannot stay flat across a 10^4 range.
SIGMA_SCALES = (0.01, 1.0, 100.0)

# Anything below this across a 10^4 change in sigma_0 is numerically the same curve.
INERT_TOLERANCE_KMS = 1e-6

PROBE_RADII_KPC = (0.5, 1.0, 2.0, 5.0, 10.0, 20.0)

# The sigma/m values this project actually uses, plus two decades of headroom on each side:
# 0.06-0.68 cm2/g is the canonical galaxy-scale range, 7.1 is the dwarf anchor (BM2), and
# 147.1 / 174.1 are the Cloud-9 anchors. 1e-3 and 1e3 bracket all of them.
PHYSICAL_SIGMA_SWEEP_CM2_PER_G = (1e-3, 0.06, 0.195, 0.68, 7.1, 147.1, 174.0, 1e3)


def sigma_m_responsiveness_kms(v_of_sigma, baseline_sigma_0, radii_kpc=PROBE_RADII_KPC,
                               sigma_0_values=None, inert_tolerance_kms=INERT_TOLERANCE_KMS):
    """Max change in circular speed produced by changing sigma_0.

    ``v_of_sigma`` is ``(sigma_0, r_kpc) -> circular speed in km/s`` for the profile under test.
    ``baseline_sigma_0`` is that producer's own sigma_0; the probe sweeps it by ``SIGMA_SCALES``
    unless an explicit ``sigma_0_values`` list is given.

    Returns ``max_abs_delta_kms``, ``max_relative_delta``, the ``curves`` that produced them, and
    ``is_sigma_inert`` — True when the whole sweep moves the curve by less than
    ``inert_tolerance_kms``.
    """
    if sigma_0_values is None:
        sigma_0_values = [baseline_sigma_0 * s for s in SIGMA_SCALES]
    sigma_0_values = [float(s) for s in sigma_0_values]
    radii_kpc = [float(r) for r in radii_kpc]
    if len(sigma_0_values) < 2:
        raise ValueError("need at least two sigma_0 values to measure a response")
    if min(sigma_0_values) <= 0:
        raise ValueError("sigma_0 values must be positive")

    def _eval(sigma_0, radius):
        # The producers' v_circ_* helpers expect array radii (they call r.max()), so probe with a
        # length-1 array and accept either a scalar or a length-1 array back.
        val = v_of_sigma(sigma_0, np.asarray([radius], dtype=float))
        arr = np.atleast_1d(np.asarray(val, dtype=float))
        if arr.size != 1:
            raise ValueError(
                f"v_of_sigma returned {arr.size} values for a single radius; expected 1")
        if not np.isfinite(arr[0]):
            raise ValueError(f"v_of_sigma returned non-finite speed at sigma_0={sigma_0}, r={radius}")
        return float(arr[0])

    curves = [[_eval(s, r) for r in radii_kpc] for s in sigma_0_values]
    ref = curves[0]
    max_abs = 0.0
    max_rel = 0.0
    for curve in curves[1:]:
        for base, val in zip(ref, curve):
            d = abs(val - base)
            max_abs = max(max_abs, d)
            max_rel = max(max_rel, d / max(abs(base), 1e-12))

    return {
        "sigma_0_values": sigma_0_values,
        "radii_kpc": radii_kpc,
        "curves_km_per_s": curves,
        "max_abs_delta_kms": max_abs,
        "max_relative_delta": max_rel,
        "inert_tolerance_kms": inert_tolerance_kms,
        "is_sigma_inert": bool(max_abs < inert_tolerance_kms),
    }


def worst_case(resp_list):
    """Aggregate several per-halo probe results into one scope statement."""
    if not resp_list:
        raise ValueError("no probe results to aggregate")
    return {
        "sigma_0_values": list(resp_list[0]["sigma_0_values"]),
        "radii_kpc": list(resp_list[0]["radii_kpc"]),
        "n_halos_probed": len(resp_list),
        "max_abs_delta_kms": max(r["max_abs_delta_kms"] for r in resp_list),
        "max_relative_delta": max(r["max_relative_delta"] for r in resp_list),
        "inert_tolerance_kms": resp_list[0]["inert_tolerance_kms"],
        "is_sigma_inert": all(r["is_sigma_inert"] for r in resp_list),
    }


def scope_sentence(resp):
    """The sentence a producer must publish next to its verdict."""
    n = resp.get("n_halos_probed")
    which = f"each of its {n} fitted halos" if n else "its profile"
    if resp["is_sigma_inert"]:
        return (
            "SCOPE LIMIT (measured, not asserted): the 'SIDM' profile in this test is sigma/m-"
            f"inert in {which} — sweeping sigma_0 over {resp['sigma_0_values'][0]:.1e} to "
            f"{resp['sigma_0_values'][-1]:.1e} cm^2/g "
            f"moves the rotation curve by at most {resp['max_abs_delta_kms']:.3e} km/s. The verdict "
            "therefore compares a fixed CORED profile against a CUSPY NFW one; it is not evidence "
            "about self-interacting dark matter. The sigma/m-responsive comparison is "
            "phase39b_sidm_responsive_profile.py."
        )
    return (
        f"This profile does respond to sigma/m: the sweep moves the rotation curve by up to "
        f"{resp['max_abs_delta_kms']:.4g} km/s (relative {resp['max_relative_delta']:.3g}). The "
        "verdict is a genuine SIDM-versus-NFW statement, subject to the model caveats above."
    )
