"""
Tests for T73-T76 (reviewer corrections on cross-validation).
"""
import json
import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
T73_CODE = PROJECT_ROOT / "v0.3-prelim" / "code" / "t73_fix_fifth_force_error.py"
T74_CODE = PROJECT_ROOT / "v0.3-prelim" / "code" / "t74_dark_sector_thermalization.py"
T75_CODE = PROJECT_ROOT / "v0.3-prelim" / "code" / "t75_updated_plot_with_bands.py"
T76_CODE = PROJECT_ROOT / "v0.3-prelim" / "code" / "t76_reframe_direct_detection.py"
T73_RESULT = PROJECT_ROOT / "v0.3-prelim" / "data" / "results" / "t73_fix_fifth_force_error.json"
T76_RESULT = PROJECT_ROOT / "v0.3-prelim" / "data" / "results" / "t76_reframe_direct_detection.json"


class TestT73FifthForceFix:
    """T73 — Fix fifth-force error (URGENT correction)."""

    def test_t73_importable(self):
        t73 = pytest.importorskip("t73_fix_fifth_force_error")
        assert hasattr(t73, "compton_wavelength_fm")
        assert hasattr(t73, "stellar_cooling_bound")

    def test_t73_mev_is_nuclear_scale(self):
        """A 0.1 MeV mediator has NUCLEAR-scale range, NOT sub-mm."""
        t73 = pytest.importorskip("t73_fix_fifth_force_error")
        # 0.1 MeV should give ~ 2 pm = ~ 2000 fm, nuclear scale
        lam_fm = t73.compton_wavelength_fm(0.1)
        assert lam_fm < 1e5, f"0.1 MeV Compton wavelength = {lam_fm} fm (should be < 1e5 fm)"
        # 15 MeV (Drobczyk) should give ~ 13 fm, nuclear scale
        lam_fm_drob = t73.compton_wavelength_fm(15.0)
        assert 1 < lam_fm_drob < 100, f"15 MeV Compton wavelength = {lam_fm_drob} fm"

    def test_t73_stellar_cooling_is_main_bound(self):
        """Stellar cooling is the main bound for sub-MeV mediators."""
        t73 = pytest.importorskip("t73_fix_fifth_force_error")
        b = t73.stellar_cooling_bound(1.0)
        assert b["severity"] == "STRONG", "Stellar cooling should be STRONG for sub-MeV"


class TestT74Thermalization:
    """T74 — Dark-sector thermalization in early universe."""

    def test_t74_importable(self):
        t74 = pytest.importorskip("t74_dark_sector_thermalization")
        assert hasattr(t74, "main")


class TestT75UpdatedPlot:
    """T75 — Updated plot with Drobczyk bands."""

    def test_t75_importable(self):
        t75 = pytest.importorskip("t75_updated_plot_with_bands")
        assert hasattr(t75, "main")


class TestT76Reframe:
    """T76 — Re-frame as evasion not prediction."""

    def test_t76_importable(self):
        t76 = pytest.importorskip("t76_reframe_direct_detection")
        assert hasattr(t76, "sigma_SI_composite")

    def test_t76_below_neutrino_floor(self):
        """Our sigma_SI should be FAR below the neutrino floor."""
        t76 = pytest.importorskip("t76_reframe_direct_detection")
        sigma_SI = t76.sigma_SI_composite(34.16, 3.55, epsilon=1e-50)
        nu_floor = t76.neutrino_floor(34.16)
        ratio = sigma_SI / nu_floor
        assert ratio < 1e-30, f"sigma_SI / nu_floor = {ratio} (should be far below 1)"

    def test_t76_LZ_invisible(self):
        """Our sigma_SI should be FAR below LZ limit."""
        t76 = pytest.importorskip("t76_reframe_direct_detection")
        sigma_SI = t76.sigma_SI_composite(34.16, 3.55, epsilon=1e-50)
        lz_limit = t76.LZ_limit(34.16)
        ratio = sigma_SI / lz_limit
        assert ratio < 1e-30, f"sigma_SI / LZ = {ratio} (should be far below 1)"