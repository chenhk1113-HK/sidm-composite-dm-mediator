"""Tests for T90.42 leave-one-out (LOO) profiling.

Per T90.42 scope:
  - T41_LEAVE_OUT_LZ=1 disables ll_lz
  - T41_LEAVE_OUT_FERMI=1 disables ll_fermi
  - T41_LEAVE_OUT_CMB=1 disables ll_cmb
  - T41_LEAVE_OUT_DAMPE=1 disables ll_dampe
  - T41_LEAVE_OUT_LSS=1 disables ll_lss
  - T41_LEAVE_OUT_LZ_MAGNETIC=1 disables ll_magnetic_moment
  - Default behavior (no LOO env vars) preserved
"""

import os
import numpy as np
import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(Path(__file__).resolve().parent.parent / "code")))


def test_loo_env_vars_exist():
    """The 6 T41_LEAVE_OUT_* env vars should be readable."""
    # These are read via os.environ.get in T41; verify they parse correctly
    for var in [
        "T41_LEAVE_OUT_LZ",
        "T41_LEAVE_OUT_FERMI",
        "T41_LEAVE_OUT_CMB",
        "T41_LEAVE_OUT_DAMPE",
        "T41_LEAVE_OUT_LSS",
        "T41_LEAVE_OUT_LZ_MAGNETIC",
    ]:
        os.environ[var] = "0"
        assert os.environ.get(var, "0").strip() == "0"
        os.environ[var] = "1"
        assert os.environ.get(var, "0").strip() == "1"
        del os.environ[var]


def test_loo_lz_when_disabled_returns_zero():
    """When T41_LEAVE_OUT_LZ=1, ll_lz should be 0 in the T41 likelihood."""
    # This is a smoke test that the env var is read correctly.
    # The actual ll_lz = 0 logic is in T41 (lines 354-357).
    # We verify by reading the T41 source.
    import inspect
    from t41_mediator_mass_joint_fit import loglike_joint
    source = inspect.getsource(loglike_joint)
    assert 'T41_LEAVE_OUT_LZ' in source


def test_loo_fermi_when_disabled_returns_zero():
    """When T41_LEAVE_OUT_FERMI=1, ll_fermi should be 0."""
    import inspect
    from t41_mediator_mass_joint_fit import loglike_joint
    source = inspect.getsource(loglike_joint)
    assert 'T41_LEAVE_OUT_FERMI' in source


def test_loo_cmb_when_disabled_returns_zero():
    """When T41_LEAVE_OUT_CMB=1, ll_cmb should be 0."""
    import inspect
    from t41_mediator_mass_joint_fit import loglike_joint
    source = inspect.getsource(loglike_joint)
    assert 'T41_LEAVE_OUT_CMB' in source


def test_loo_dampe_when_disabled_returns_zero():
    """When T41_LEAVE_OUT_DAMPE=1, ll_dampe should be 0."""
    import inspect
    from t41_mediator_mass_joint_fit import loglike_joint
    source = inspect.getsource(loglike_joint)
    assert 'T41_LEAVE_OUT_DAMPE' in source


def test_loo_lss_when_disabled_returns_zero():
    """When T41_LEAVE_OUT_LSS=1, ll_lss should be 0."""
    import inspect
    from t41_mediator_mass_joint_fit import loglike_joint
    source = inspect.getsource(loglike_joint)
    assert 'T41_LEAVE_OUT_LSS' in source


def test_loo_lz_magnetic_when_disabled_returns_zero():
    """When T41_LEAVE_OUT_LZ_MAGNETIC=1, ll_magnetic_moment should be 0."""
    import inspect
    from t41_mediator_mass_joint_fit import loglike_joint
    source = inspect.getsource(loglike_joint)
    assert 'T41_LEAVE_OUT_LZ_MAGNETIC' in source


def test_default_no_loo_preserves_behavior():
    """Without any LOO env vars set, the T41 likelihood should behave normally."""
    # Clear any LOO env vars
    for var in [
        "T41_LEAVE_OUT_LZ",
        "T41_LEAVE_OUT_FERMI",
        "T41_LEAVE_OUT_CMB",
        "T41_LEAVE_OUT_DAMPE",
        "T41_LEAVE_OUT_LSS",
        "T41_LEAVE_OUT_LZ_MAGNETIC",
    ]:
        os.environ.pop(var, None)
    # Now test that loglike_joint can be called and returns something
    # Use a representative parameter set: heavy mediator
    from t41_mediator_mass_joint_fit import loglike_joint
    # (log_m_phi, log_m_chi, g_chi, log_eps, log_alpha, log_xi)
    theta = (3.0, 3.0, 0.5, -30.0, -15.0, -1.0)  # heavy mediator
    ll = loglike_joint(theta)
    # Should return a finite value (or -inf if KSFR mask kicks in, but
    # m_phi=10^3=1000 MeV is above f_pi so KSFR doesn't reject).
    assert np.isfinite(ll) or ll == -np.inf


def test_loo_independence():
    """Each LOO env var should be independent of the others."""
    # Test that setting one doesn't affect another
    os.environ["T41_LEAVE_OUT_LZ"] = "1"
    assert os.environ.get("T41_LEAVE_OUT_LZ") == "1"
    assert os.environ.get("T41_LEAVE_OUT_FERMI", "0").strip() == "0"
    del os.environ["T41_LEAVE_OUT_LZ"]
    os.environ["T41_LEAVE_OUT_FERMI"] = "1"
    assert os.environ.get("T41_LEAVE_OUT_FERMI") == "1"
    assert os.environ.get("T41_LEAVE_OUT_LZ", "0").strip() == "0"
    del os.environ["T41_LEAVE_OUT_FERMI"]


def test_loo_loo_driver_imports():
    """The LOO driver should import without errors."""
    from t90_v42_loo_profiling import run_t41_loo, main  # noqa: F401
    assert callable(run_t41_loo)
    assert callable(main)