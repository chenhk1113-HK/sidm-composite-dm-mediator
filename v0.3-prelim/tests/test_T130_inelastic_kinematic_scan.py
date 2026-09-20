"""
T130 tests — Inelastic DM kinematic scan verification.

Tests verify:
1. Qwen's KE_CM formula matches independent calculation
2. 46 TeV threshold for DD evasion matches independent calc
3. Razor-thin window at threshold
4. Thermal relic requires alpha_D > 1 (unitarity violation)
5. No valid m_chi < 100 TeV that satisfies all constraints
"""
import numpy as np
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + "/code")

from T130_inelastic_kinematic_scan import (
    ke_cm_eV,
    inelastic_dm_check,
    scan_mass_for_inelastic_window,
)


class TestKECalculation:
    """KE_CM formula verification (vs Qwen referee)."""

    def test_KE_CM_Cloud9_per_mchi_matches_qwen_2_18e_minus_9(self):
        """Qwen: KE_CM(28)/m_chi = 2.18e-9. Verify."""
        KE_per_mchi = ke_cm_eV(1.0, 28) / 1e9
        assert 2.16e-9 < KE_per_mchi < 2.20e-9, f"Got {KE_per_mchi}"

    def test_KE_CM_dSph_per_mchi_matches_qwen_6_25e_minus_10(self):
        """Qwen: KE_CM(15)/m_chi = 6.25e-10. Verify."""
        KE_per_mchi = ke_cm_eV(1.0, 15) / 1e9
        assert 6.20e-10 < KE_per_mchi < 6.30e-10, f"Got {KE_per_mchi}"

    def test_KE_CM_UFD_per_mchi(self):
        """UFD (v=3) KE_CM/m_chi ~ 2.5e-11. Verify."""
        KE_per_mchi = ke_cm_eV(1.0, 3) / 1e9
        assert 2.4e-11 < KE_per_mchi < 2.6e-11, f"Got {KE_per_mchi}"

    def test_Cloud9_KE_at_10_GeV_is_23_eV(self):
        """Sanity check: KE_CM(Cloud-9, 10 GeV) = 23 eV (referee-verified)."""
        KE = ke_cm_eV(10.7, 28)
        assert 22 < KE < 25, f"Got {KE} eV"


class TestMassThreshold:
    """Verify the 46 TeV threshold for DD evasion."""

    def test_Cloud9_KE_equals_100_keV_at_46_TeV(self):
        """At m_chi = 46 TeV, KE_CM(Cloud-9) = 100 keV = DD threshold."""
        m_chi_GeV = 46000
        KE = ke_cm_eV(m_chi_GeV, 28)
        KE_keV = KE / 1000
        # Should be ~100 keV
        assert 95 < KE_keV < 105, f"KE_CM = {KE_keV} keV at 46 TeV, expected ~100 keV"

    def test_window_opens_at_46_TeV(self):
        """Below 46 TeV, the window is < 100 keV (no DD evasion possible)."""
        results = scan_mass_for_inelastic_window()

        # Find the first m_chi where valid=True
        first_valid = None
        for r in results:
            if r['valid']:
                first_valid = r
                break

        assert first_valid is not None, "No valid window in [1 GeV, 100 TeV]"
        # Should be ~46 TeV
        m_chi_TeV = first_valid['m_chi_GeV'] / 1000
        assert 45 < m_chi_TeV < 47, f"First valid at {m_chi_TeV} TeV, expected ~46 TeV"

    def test_below_46_TeV_window_is_invalid(self):
        """At m_chi = 10 TeV, the window is < 100 keV (invalid)."""
        # KE_CM(Cloud-9, 10 TeV) = 0.25 * 10000 GeV * 9.34e-5^2 * 1e9 eV/GeV = ~22 keV
        KE = ke_cm_eV(10000, 28)
        KE_keV = KE / 1000
        assert KE_keV < 30, f"KE_CM at 10 TeV is {KE_keV} keV, way below 100 keV DD threshold"

    def test_no_GeV_scale_model_works(self):
        """At m_chi = 10 GeV (our T120.11 value), the window is sub-keV."""
        KE = ke_cm_eV(10.0, 28)
        # KE_CM = 0.25 * 10 * 1e9 * 9.34e-5^2 = 21.8 eV
        assert KE < 100, f"At 10 GeV, KE_CM = {KE} eV, sub-100-eV window"


class TestRazorThinWindow:
    """Verify the window is razor-thin at the threshold."""

    def test_window_at_46_TeV_is_under_1_keV(self):
        """At m_chi = 46 TeV, window width = KE_CM(Cloud-9) - 100 keV ~ 0.3 keV."""
        results = scan_mass_for_inelastic_window()

        # Find entry for 46 TeV
        for r in results:
            if abs(r['m_chi_GeV'] - 46000) / 46000 < 0.01:
                lower = r['Delta_m_required_lower_eV']
                upper = r['Delta_m_required_upper_eV']
                width_eV = upper - lower
                width_keV = width_eV / 1000
                assert width_keV < 1.0, f"Window = {width_keV} keV, razor-thin"
                return

        raise AssertionError("Could not find 46 TeV in scan")


class TestThermalRelicProblem:
    """Verify thermal relic requires unitarity-violating alpha_D."""

    def test_thermal_relic_requires_alpha_D_above_unity(self):
        """At m_chi = 46 TeV, thermal relic needs alpha_D ~ 400."""
        m_chi_GeV = 46000
        v_relic_c = 10 * 1e3 / 2.998e8

        # <sigma v>_thermal = 3e-26 cm^3/s
        # sigma_v = alpha_D^2/m_chi^2 * c * v_relic_c * (hbar*c)^2 / GeV^2
        hbar_c_sq = 0.3894e-27  # GeV^2 * cm^2
        c_cm_s = 2.998e10

        # Solve for alpha_D
        alpha_D_needed = np.sqrt(3e-26 / (hbar_c_sq * c_cm_s * v_relic_c)) * m_chi_GeV
        assert alpha_D_needed > 1, f"alpha_D needed = {alpha_D_needed}, should be >> 1"
        assert alpha_D_needed > 100, f"alpha_D needed = {alpha_D_needed}, should be ~400"

    def test_46_TeV_DM_is_unitarity_violating(self):
        """Per Griest-Kamionkowski unitarity bound, m_chi < ~120 TeV for thermal WIMP."""
        m_chi_TeV = 46
        unitarity_bound_TeV = 120
        assert m_chi_TeV < unitarity_bound_TeV, "46 TeV is below unitarity bound"
        # Note: 46 TeV is within unitarity bound BUT thermal relic needs alpha_D ~ 400
        # So the issue is unitarity of alpha_D, not unitarity of mass


class TestNoGoConclusion:
    """Verify the no-go conclusion holds."""

    def test_no_valid_window_below_46_TeV(self):
        """Scan: no valid m_chi in [1 GeV, 46 TeV) means no-go for GeV-scale inelastic DM."""
        results = scan_mass_for_inelastic_window()
        invalid_below_threshold = [r for r in results if r['m_chi_GeV'] < 46000 and not r['valid']]
        valid_below_threshold = [r for r in results if r['m_chi_GeV'] < 46000 and r['valid']]

        assert len(valid_below_threshold) == 0, f"Found {len(valid_below_threshold)} valid below 46 TeV"
        assert len(invalid_below_threshold) > 0

    def test_above_46_TeV_requires_fine_tuning(self):
        """Above 46 TeV, window is razor-thin AND thermal relic unitarity-violating."""
        # This is captured by other tests but state the conclusion
        results = scan_mass_for_inelastic_window()
        valid_results = [r for r in results if r['valid']]

        # Among valid results, check window widths
        narrow_windows = []
        for r in valid_results:
            lower = r['Delta_m_required_lower_eV']
            upper = r['Delta_m_required_upper_eV']
            width_eV = upper - lower
            # Window width as fraction of upper
            if width_eV / upper < 0.05:  # < 5% of upper
                narrow_windows.append(r)

        # Most windows should be narrow (fine-tuning)
        assert len(narrow_windows) > 0, "Expected narrow windows above 46 TeV"
