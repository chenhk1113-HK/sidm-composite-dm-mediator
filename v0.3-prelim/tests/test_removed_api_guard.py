"""
Regression guard for APIs removed by the pinned scientific stack.

Bug class (found 2026-11-04): ``v0.3-prelim/code/phase39_nfw_vs_sidm.py`` line 89
calls ``np.trapz``, which NumPy 2.x removed. The environment the release gate runs
on (``.venv-sidm-bench``, numpy 2.5.2) therefore raises::

    AttributeError: module 'numpy' has no attribute 'trapz'

when ``v_circ_burkert()`` is actually called. The Phase 39 test file
(``test_phase39_nfw_vs_sidm.py``) never calls the function -- it only reads the
stored ``phase39_nfw_vs_sidm.json`` -- so the whole suite passed while the code path
that produced that JSON could no longer run. A test that reads an artifact cannot
detect that its producer is dead.

Same class on the third-party side: ``WIMpy`` at the pinned commit imports
``scipy.integrate.trapz``, which SciPy 1.18 removed. The local install carries a
hand patch (``from scipy.integrate import trapezoid as trapz``). That patch is now
recorded in ``patches/0003-wimpy-scipy118-trapezoid.patch``; it is not in upstream.

Two checks here:
  1. A static scan: no call site may use a removed API.
  2. A live call: ``v_circ_burkert`` must execute and return finite, positive values.
"""
from __future__ import annotations

import importlib.util
import re
import sys
from pathlib import Path

import numpy as np

REPO = Path(__file__).resolve().parents[2]
SCAN_ROOTS = [
    REPO / "v0.3-prelim" / "code",
    REPO / "v0.3-prelim" / "tests",
    REPO / "scripts",
]

# Removed by NumPy 2.x / SciPy 1.18. A quoted name inside getattr(...) compat
# shims is deliberately NOT matched: only real call sites and real imports.
BANNED_CALL = re.compile(r"\b(?:np|numpy)\.trapz\s*\(")
BANNED_IMPORT = re.compile(r"^\s*from\s+scipy\.integrate\s+import[^\n]*\btrapz\b(?!\s*as)")
COMPAT_OK = re.compile(r"trapezoid\s+as\s+trapz")


def _scan_offenders() -> list[str]:
    offenders: list[str] = []
    for root in SCAN_ROOTS:
        if not root.is_dir():
            continue
        for py in sorted(root.rglob("*.py")):
            if "__pycache__" in py.parts:
                continue
            if py.name == Path(__file__).name:
                continue  # this file carries the banned pattern on purpose (probe strings)
            try:
                lines = py.read_text(encoding="utf-8", errors="replace").splitlines()
            except OSError:
                continue
            for i, line in enumerate(lines, start=1):
                stripped = line.strip()
                if stripped.startswith("#"):
                    continue  # comment lines may name the removed API to explain the fix
                if COMPAT_OK.search(line):
                    continue
                if BANNED_CALL.search(line) or BANNED_IMPORT.search(line):
                    offenders.append(f"{py.relative_to(REPO)}:{i}: {line.strip()}")
    return offenders


def test_no_removed_numpy_trapz_call_sites():
    """np.trapz was removed in NumPy 2.x; the pinned numpy here is 2.5.2."""
    offenders = _scan_offenders()
    listing = "\n  ".join(offenders)
    assert not offenders, (
        "Removed API used in the pinned environment (np.trapz was removed in "
        "NumPy 2.x). Offenders:\n  " + listing
    )


def test_v_circ_burkert_actually_runs():
    """The Phase 39 producer must be executable, not just its output file present."""
    src = REPO / "v0.3-prelim" / "code" / "phase39_nfw_vs_sidm.py"
    spec = importlib.util.spec_from_file_location("phase39_nfw_vs_sidm_probe", src)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)

    r = np.array([1.0, 5.0, 10.0, 50.0])
    log_rho_b, r_b = 10.0, 0.5
    v = np.asarray(mod.v_circ_burkert(r, log_rho_b, r_b), dtype=float)
    assert v.shape == r.shape, f"shape drift: {v.shape} vs {r.shape}"
    assert np.all(np.isfinite(v)), f"non-finite circular speed: {v}"
    assert np.all(v > 0), f"non-positive circular speed: {v}"

    # Cross-code check against an independent quadrature of the same Burkert
    # profile, using the SAME gravitational constant the module uses. This is what
    # proves the integrator is intact, not merely that the file imports.
    from scipy.integrate import quad
    # Take the constant FROM the producer instead of copying it. On 2026-11-04 the
    # producer moved from the kpc/Gyr-native G = 4.5e-6 to the km/s-native
    # G_KPC_KMS = 4.302e-6 (config.py:111); a hard-coded copy of the old value made
    # this guard fail by exactly sqrt(4.302/4.5) = 0.978 and hid that the integrator
    # was in fact intact.
    G = float(getattr(mod, "G_KPC_KMS", 4.302e-6))  # kpc (km/s)^2 / Msun
    rho_b = 10.0**log_rho_b
    rho = lambda x: rho_b * r_b**3 / ((x + r_b) * (x**2 + r_b**2))
    for ri, vi in zip(r, v):
        m_enc, _ = quad(lambda x: 4 * np.pi * rho(x) * x * x, 0.0, ri, limit=400)
        v_ref = np.sqrt(G * m_enc / ri)
        assert abs(vi - v_ref) / v_ref < 0.01, f"v_circ_burkert({ri}) = {vi:.4f} vs quadrature {v_ref:.4f}"

    # Beyond the Burkert core (r >> r_b) the profile goes as r^-2, so v_circ must
    # FALL as 1/sqrt(r). Inside the core it rises. Asserting the wrong regime is
    # how this guard nearly shipped a false physics claim.
    assert v[0] > v[-1], f"expected v_circ to decline far outside the core: {v}"


def test_removed_api_guard_is_not_vacuous():
    """Prove the scanner can fail: a synthetic offender must be reported."""
    probe = "    M = 4 * np.pi * np.trapz(y, x)\n"
    assert BANNED_CALL.search(probe), "guard regex no longer matches the bug it guards"
    assert BANNED_IMPORT.search("from scipy.integrate import trapz, cumtrapz, quad")
    assert not BANNED_CALL.search("    _trapz = getattr(np, 'trapezoid', None)\n")
    assert COMPAT_OK.search("from scipy.integrate import trapezoid as trapz")
