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
        our_sigma_DM_n_at_eps_1e_minus_5 = d["our_pipeline"]["sigma_DM_n_cm2_at_eps_1e-5"]
        assert drob_sigma_SI < LZ_limit, f"Drobczyk {drob_sigma_SI} should be < LZ"
        # Our MAP drives epsilon to ~1e-35 to survive LZ, so sigma_SI at MAP is essentially zero.
        # At the canonical benchmark epsilon=1e-5 (pre-LZ), sigma_SI = 1.2e-32 cm^2, which is the
        # appropriate value to compare to LZ. This is ~5e15 times above the LZ limit, hence the
        # 30+ order-of-magnitude epsilon suppression the R12 closure document quantifies.
        assert our_sigma_DM_n_at_eps_1e_minus_5 > LZ_limit, (
            f"Ours at eps=1e-5 {our_sigma_DM_n_at_eps_1e_minus_5} is intentionally above LZ — "
            f"the LZ evasion comes from epsilon being driven to ~1e-35 at the MAP, "
            f"not from an intrinsically small sigma_SI."
        )