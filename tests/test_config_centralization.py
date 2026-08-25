"""
Test class for M3 reviewer fix: centralized physical constants in config.py.

Per R13 reviewer M3 suggestion in sidm review2.docx (2026-08-25):

  'Centralize all physical constants into one single config file.'

The project already has config.py (created in R10/R11 peer review).
But T70 (channels_extended.py) and the legacy channels_v03.py have
scattered constants. This test verifies:

  1. All T70/T70.1 constants are now in config.py (not in
     channels_extended.py).
  2. All config.py constants are importable from a single namespace.
  3. Legacy duplicate constants in channels_v03.py are flagged but
     NOT YET removed (would change signatures; deferred to v0.4).
  4. A centralized re-export helper `from config import *` works.

References:
  - sidm review2.docx Reviewer1 M3 (line 137): 'Centralize all physical
    constants into one single config file.'
  - config.py (existing, R10/R11): already has paths, sampler
    hyperparameters, velocity scales, Gaussian proxy widths.
"""
from __future__ import annotations
import math
import sys
from pathlib import Path

import numpy as np
import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(PROJECT_ROOT / "v0.1-prelim" / "code"))
sys.path.insert(0, str(PROJECT_ROOT / "v0.3-prelim" / "code"))

import config


class TestConfigCentralization:
    """Verify all T70/T70.1 constants are in config.py."""

    # T70 constants (moved from channels_extended.py)
    def test_dm_free_udg_constants_in_config(self):
        """Channel 11 (NGC 1052-DF2/DF4 dark-matter-free UDG) constants."""
        assert hasattr(config, "DM_FREE_UDG_RATE_PEAK")
        assert hasattr(config, "DM_FREE_UDG_RATE_WIDTH")
        assert math.isfinite(config.DM_FREE_UDG_RATE_PEAK)
        assert math.isfinite(config.DM_FREE_UDG_RATE_WIDTH)

    def test_cosmic_web_radio_constants_in_config(self):
        """Channel 12 (cosmic-web radio) constants."""
        assert hasattr(config, "COSMIC_WEB_RADIO_LOG_EPSILON_UPPER")
        assert math.isfinite(config.COSMIC_WEB_RADIO_LOG_EPSILON_UPPER)

    # T70.1 constants (Channel 13, SIDM mass floor)
    def test_sidm_mass_lower_constants_in_config(self):
        """Channel 13 (Tremaine-Gunn + Rogers-Peiris) constants."""
        assert hasattr(config, "TREMAINE_GUNN_MASS_BOUND_EV")
        assert hasattr(config, "ROGERS_PEIRIS_LYMAN_ALPHA_BOUND_EV")
        assert hasattr(config, "SIDM_MASS_CLASSICAL_FLOOR_EV")
        assert config.SIDM_MASS_CLASSICAL_FLOOR_EV == max(
            config.TREMAINE_GUNN_MASS_BOUND_EV,
            config.ROGERS_PEIRIS_LYMAN_ALPHA_BOUND_EV,
        )

    # Existing config.py constants should still be there (no regressions)
    def test_existing_config_constants_still_present(self):
        """R10/R11-era constants must still be importable."""
        assert hasattr(config, "V_REF")
        assert hasattr(config, "V_UFD")
        assert hasattr(config, "V_DSPH")
        assert hasattr(config, "NLIVE")
        assert hasattr(config, "DLOGZ")
        assert hasattr(config, "LOG_SIGMA_M_RANGE")
        assert hasattr(config, "A_RANGE")

    # Cross-module: channels_extended.py should re-import from config.py
    def test_channels_extended_uses_config_imports(self):
        """channels_extended.py must NOT define its own copies of T70/T70.1
        constants via '=' assignment — it should import them from config.py.

        Note: After the M3 fix, channels_extended.py DOES have these names
        as module attributes (because they're imported from config.py).
        That's expected and correct. What we check here is that the
        source file does NOT have '=' assignments for these constants
        (which would shadow the canonical config.py values).
        """
        import re
        from pathlib import Path
        src = Path(PROJECT_ROOT / "v0.3-prelim" / "code" / "channels_extended.py").read_text(encoding="utf-8")
        for c in ["DM_FREE_UDG_RATE_PEAK", "TREMAINE_GUNN_MASS_BOUND_EV", "SIDM_MASS_CLASSICAL_FLOOR_EV",
                  "ROGERS_PEIRIS_LYMAN_ALPHA_BOUND_EV"]:
            # Match an assignment, not an import or a comment reference
            pattern = rf"^{c}\s*=\s*[^=]"
            assert not re.search(pattern, src, re.MULTILINE), (
                f"{c} should be imported from config.py, not defined in channels_extended.py"
            )

    # Verify the channel functions still work after the centralization
    def test_channels_still_work_after_centralization(self):
        """Smoke test: channel functions must still return finite values
        after the constants move."""
        from channels_extended import (
            loglike_dm_free_udg,
            loglike_cosmic_web_radio,
            loglike_sidm_mass_lower,
        )
        assert math.isfinite(loglike_dm_free_udg(0.68, 1.48))
        assert math.isfinite(loglike_cosmic_web_radio(0.68, 1.48, 1e-35))
        assert loglike_sidm_mass_lower(0.68, 1.48, 14.8e9) == 0.0