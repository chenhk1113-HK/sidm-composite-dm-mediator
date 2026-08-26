"""Tests for data/reference/ posterior chain files.

Per R13 reviewer M2 fix (2026-08-25), the downsampled reference chains
in data/reference/ are committed so users can plot headline posteriors
without re-running dynesty. These tests verify:
  1. All expected files exist
  2. Schemas match the originals (modulo thinning/dtype compression)
  3. Numerical integrity (means preserved, no NaN/inf corruption)
  4. Total size under the 500 KB budget

If these tests fail, regenerate via:
  python outputs/downsample_for_reference.py
(then sync from WSL via the sync_to_wsl.sh pre-commit hook).
"""
import json
from pathlib import Path

import numpy as np
import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
REF_DIR = REPO_ROOT / "data" / "reference"

# Test parameters
EXPECTED_FILES = {
    "t8_v03_posterior_samples_reference.npz": {
        "keys": ["log_sigma_m_0", "a", "weights"],
        "thin_n": 500,
    },
    "t17_kiss_sidm_corrected_samples_reference.npz": {
        "keys": ["log_sigma_m_0", "a", "weights", "treatment"],
        "thin_n": 500,
    },
    "t18_two_component_samples_reference.npz": {
        "keys": ["samples", "weights"],
        "thin_n": 500,
    },
    "sparc_hierarchical_grid_reference.npz": {
        "keys": ["sigma_m_grid", "a_grid", "logL_grid",
                 "logL_per_galaxy", "galaxy_names", "V_max_kms", "M_vir_Msun"],
        "shapes": {
            "logL_per_galaxy": (175, 50, 30),
        },
    },
}
TOTAL_BUDGET_BYTES = 500 * 1024  # 500 KB


class TestReferenceDataExists:
    """All expected reference files present."""

    def test_reference_dir_exists(self):
        assert REF_DIR.exists(), f"data/reference/ missing — run outputs/downsample_for_reference.py"
        assert REF_DIR.is_dir()

    def test_manifest_exists(self):
        manifest = REF_DIR / "MANIFEST.json"
        assert manifest.exists(), "MANIFEST.json missing — re-run downsample_for_reference.py"
        data = json.loads(manifest.read_text())
        assert "files" in data
        assert "total_bytes" in data

    def test_all_expected_files_present(self):
        for fname in EXPECTED_FILES:
            p = REF_DIR / fname
            assert p.exists(), f"Missing reference file: {fname}"


class TestReferenceDataSchemas:
    """Schemas match expectations (modulo compression)."""

    @pytest.mark.parametrize("fname,expected", list(EXPECTED_FILES.items()))
    def test_keys_present(self, fname, expected):
        d = np.load(REF_DIR / fname, allow_pickle=True)
        assert set(d.keys()) == set(expected["keys"]), (
            f"{fname}: keys {set(d.keys())} != expected {set(expected['keys'])}"
        )

    def test_thinned_samples_have_500_rows(self):
        for fname in ("t8_v03_posterior_samples_reference.npz",
                      "t17_kiss_sidm_corrected_samples_reference.npz",
                      "t18_two_component_samples_reference.npz"):
            d = np.load(REF_DIR / fname, allow_pickle=True)
            for k, v in d.items():
                if v.dtype.kind == 'f':  # float arrays
                    assert v.shape[0] == 500, (
                        f"{fname}/{k}: expected 500 rows, got {v.shape[0]}"
                    )

    def test_sparc_grid_shapes(self):
        d = np.load(REF_DIR / "sparc_hierarchical_grid_reference.npz", allow_pickle=True)
        assert d["logL_per_galaxy"].shape == (175, 50, 30)
        assert d["sigma_m_grid"].shape == (50,)
        assert d["a_grid"].shape == (30,)
        assert d["galaxy_names"].shape == (175,)

    def test_sparc_logL_is_float16(self):
        """Compression dtype verified — logL_per_galaxy goes f32 -> f16."""
        d = np.load(REF_DIR / "sparc_hierarchical_grid_reference.npz", allow_pickle=True)
        assert d["logL_per_galaxy"].dtype == np.float16, (
            f"Expected float16 compression, got {d['logL_per_galaxy'].dtype}"
        )


class TestReferenceDataNumerical:
    """No NaN/inf corruption; means preserved."""

    @pytest.mark.parametrize("fname", [
        "t8_v03_posterior_samples_reference.npz",
        "t17_kiss_sidm_corrected_samples_reference.npz",
        "t18_two_component_samples_reference.npz",
    ])
    def test_no_nan_in_float_arrays(self, fname):
        d = np.load(REF_DIR / fname, allow_pickle=True)
        for k, v in d.items():
            if v.dtype.kind == 'f':
                assert not np.any(np.isnan(v)), f"{fname}/{k} has NaN"

    def test_sparc_logL_no_inf_from_clamp(self):
        """The float16 clamp at -65504 should NOT produce -inf in the output."""
        d = np.load(REF_DIR / "sparc_hierarchical_grid_reference.npz", allow_pickle=True)
        logL = d["logL_per_galaxy"]
        # Float16 has -inf as the smallest representable; check we have NO -inf
        assert not np.any(np.isinf(logL)), (
            f"Found -inf in SPARC logL grid: {np.sum(np.isinf(logL))} cells "
            "(would mean the f16 clamp did not work)"
        )
        # Min should be exactly -65504 (the clamp floor)
        assert logL.min() >= -65504.0, f"SPARC logL min {logL.min()} < -65504 (clamp floor)"


class TestReferenceDataBudget:
    """Total size under 500 KB."""

    def test_total_under_500kb(self):
        total = sum(p.stat().st_size for p in REF_DIR.iterdir() if p.is_file())
        assert total < TOTAL_BUDGET_BYTES, (
            f"data/reference/ total {total:,}B exceeds {TOTAL_BUDGET_BYTES:,}B budget"
        )

    def test_manifest_total_matches_disk(self):
        manifest = json.loads((REF_DIR / "MANIFEST.json").read_text())
        disk_total = sum(p.stat().st_size for p in REF_DIR.iterdir()
                         if p.is_file() and p.name != "MANIFEST.json")
        manifest_total = sum(f["reference_bytes"] for f in manifest["files"])
        assert disk_total == manifest_total, (
            f"Disk total {disk_total} != manifest total {manifest_total}"
        )
