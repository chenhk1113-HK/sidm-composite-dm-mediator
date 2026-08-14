"""
Tests for T68 — Cross-validation with Drobczyk 2025.
"""
import json
import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
T68_CODE = PROJECT_ROOT / "v0.3-prelim" / "code" / "t68_cross_validation_drobczyk.py"
T68_RESULT = PROJECT_ROOT / "v0.3-prelim" / "data" / "results" / "t68_cross_validation_drobczyk.json"


class TestT68CrossValidation:
    """T68 — Cross-validation with Drobczyk 2025."""

    def test_t68_importable(self):
        t68 = pytest.importorskip("t68_cross_validation_drobczyk")
        assert hasattr(t68, "main")

    def test_t68_result_has_drobczyk_data(self):
        """T68 result should include Drobczyk 2025 benchmark."""
        if not T68_RESULT.exists():
            pytest.skip("T68 not yet completed")
        with open(T68_RESULT) as f:
            d = json.load(f)
        assert "drobczyk_2025" in d
        assert "our_pipeline" in d

    def test_t68_both_models_invisible_to_direct_detection(self):
        """Both Drobczyk's sigma_SI and our sigma_DM_n should be below LZ."""
        if not T68_RESULT.exists():
            pytest.skip("T68 not yet completed")
        with open(T68_RESULT) as f:
            d = json.load(f)
        LZ_limit = 1e-47  # LZ SR1+SR3 limit at m_DM ~ 30 GeV
        drob_sigma_SI = d["drobczyk_2025"]["sigma_SI_cm2"]
        our_sigma_DM_n = d["our_pipeline"]["sigma_DM_n_cm2"]
        assert drob_sigma_SI < LZ_limit, f"Drobczyk {drob_sigma_SI} should be < LZ"
        assert our_sigma_DM_n < LZ_limit, f"Ours {our_sigma_DM_n} should be < LZ"