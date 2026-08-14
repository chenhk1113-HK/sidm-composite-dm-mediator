"""
Regression tests for config.py cross-location availability.

History: 2026-08-11 (Full Codebase R2 review audit) — discovered that
config.py was ONLY at /home/lamkuenai/sidm-composite-dm-mediator/v0.3-prelim/code/
(WSL-side), NOT at /mnt/c/Users/lamkuenai/projects/sidm-composite-dm-mediator/v0.3-prelim/code/
(Windows-side). The T-series scripts (T21, T22, T23) did `from config import
RESULTS_DIR_V03`, but on Windows-side Python, the import would fail.

Fix: config.py is now COPIED to both locations. This test enforces that
the canonical config.py must be importable from BOTH sides.

Standing rule (AGENTS.md): no new dependencies.
"""
import json
import subprocess
import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent


def _wsl_path_exists(wsl_path: str) -> bool:
    """Check whether a POSIX WSL path exists, by shelling out to `wsl -- bash -c test -e`.

    On a pure-Windows Python process, ``Path("/home/lamkuenai/...").exists()``
    resolves to ``C:\\home\\lamkuenai\\...`` which is NEVER where the WSL-side
    mirror lives. The only reliable cross-environment path check is to ask
    WSL directly. Falls back to ``False`` if WSL is not installed.
    """
    try:
        result = subprocess.run(
            ["wsl", "--", "bash", "-c", f"test -e {wsl_path} && echo YES || echo NO"],
            capture_output=True, text=True, timeout=15,
        )
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False
    return "YES" in result.stdout


class TestConfigCrossLocation:
    """config.py must be importable from BOTH WSL and Windows Python."""

    @pytest.mark.skipif(sys.platform != "win32", reason="Windows-only test")
    def test_config_importable_from_windows_python(self):
        """Windows-side Python can import config when run from v0.3-prelim/code/."""
        code_dir = PROJECT_ROOT / "v0.3-prelim" / "code"
        # Run Windows-side Python: import config, print RESULTS_DIR_V03
        result = subprocess.run(
            ["python", "-c", "import sys; sys.path.insert(0, '.'); import config; print(config.RESULTS_DIR_V03)"],
            cwd=str(code_dir), capture_output=True, text=True, timeout=30,
        )
        assert result.returncode == 0, (
            f"Windows-side Python failed to import config:\n"
            f"stdout: {result.stdout}\nstderr: {result.stderr}"
        )
        assert "v0.3-prelim" in result.stdout
        assert "data" in result.stdout
        assert "results" in result.stdout

    def test_config_file_exists_in_both_locations(self):
        """config.py must exist at both WSL-side and Windows-side paths."""
        wsl_path_str = "/home/lamkuenai/sidm-composite-dm-mediator/v0.3-prelim/code/config.py"
        wsl_path = Path(wsl_path_str)
        win_path = PROJECT_ROOT / "v0.3-prelim" / "code" / "config.py"
        # WSL-side: shell out to wsl since Windows Python can't see POSIX mounts
        if sys.platform == "win32":
            assert _wsl_path_exists(wsl_path_str), (
                f"WSL-side config.py missing at {wsl_path_str}"
            )
        else:
            assert wsl_path.exists(), f"WSL-side config.py missing at {wsl_path}"
        assert win_path.exists(), f"Windows-side config.py missing at {win_path}"

    def test_config_files_are_identical(self):
        """Both copies of config.py must have the same content (no drift)."""
        wsl_path_str = "/home/lamkuenai/sidm-composite-dm-mediator/v0.3-prelim/code/config.py"
        win_path = PROJECT_ROOT / "v0.3-prelim" / "code" / "config.py"
        if sys.platform == "win32":
            if not (win_path.exists() and _wsl_path_exists(wsl_path_str)):
                pytest.skip("One of the config.py files is missing")
            # Read Windows-side directly; read WSL-side via wsl cat
            win_content = win_path.read_bytes()
            result = subprocess.run(
                ["wsl", "--", "bash", "-c", f"cat {wsl_path_str} | base64"],
                capture_output=True, text=True, timeout=15,
            )
            assert result.returncode == 0, f"wsl cat failed: {result.stderr}"
            import base64
            wsl_content = base64.b64decode(result.stdout.strip())
        else:
            wsl_path = Path(wsl_path_str)
            if not (wsl_path.exists() and win_path.exists()):
                pytest.skip("One of the config.py files is missing")
            wsl_content = wsl_path.read_bytes()
            win_content = win_path.read_bytes()
        assert wsl_content == win_content, (
            f"config.py has drifted between WSL and Windows sides:\n"
            f"WSL size: {len(wsl_content)}, Win size: {len(win_content)}"
        )

    def test_config_has_required_exports(self):
        """config.py must export the constants used by T-series scripts."""
        win_path = PROJECT_ROOT / "v0.3-prelim" / "code" / "config.py"
        if not win_path.exists():
            pytest.skip("Windows-side config.py missing")
        content = win_path.read_text()
        # Symbols that T-series scripts depend on
        required = [
            "RESULTS_DIR_V01",
            "RESULTS_DIR_V03",
            "LOG_SIGMA_M_RANGE",
            "A_RANGE",
            "NLIVE",
            "DLOGZ",
            "V_REF",
            "V_DSPH",
            "V_GALAXY",
            "V_CLUSTER",
        ]
        for sym in required:
            assert sym in content, f"Missing export: {sym}"

    def test_config_auto_detects_paths(self):
        """config.py must auto-detect WSL vs Windows paths (no hardcoded failure)."""
        win_path = PROJECT_ROOT / "v0.3-prelim" / "code" / "config.py"
        if not win_path.exists():
            pytest.skip("Windows-side config.py missing")
        content = win_path.read_text()
        # Should have _detect_root() function with both path checks
        assert "_detect_root" in content
        assert "C:\\\\Users\\\\lamkuenai" in content or "/home/lamkuenai" in content, (
            "config.py must check at least one canonical path"
        )
        assert "DM_SIDM_PROJECT_ROOT" in content, (
            "config.py must support env-var override"
        )


class TestConfigUsesIt:
    """T-series scripts must actually use config (not bypass it)."""

    def test_t21_uses_config(self):
        """t21_real_kiss_sidm_gravothermal.py imports from config."""
        t21_path = PROJECT_ROOT / "v0.3-prelim" / "code" / "t21_real_kiss_sidm_gravothermal.py"
        if not t21_path.exists():
            pytest.skip("t21 not at Windows-side")
        content = t21_path.read_text()
        assert "from config import" in content, "t21 must use config.py"

    def test_t22_uses_config(self):
        """t22_real_kiss_sidm_two_comp.py imports from config."""
        t22_path = PROJECT_ROOT / "v0.3-prelim" / "code" / "t22_real_kiss_sidm_two_comp.py"
        if not t22_path.exists():
            pytest.skip("t22 not at Windows-side")
        content = t22_path.read_text()
        assert "from config import" in content, "t22 must use config.py"

    def test_t23_uses_config(self):
        """t23_real_kiss_sidm_two_comp_imfp.py imports from config."""
        t23_path = PROJECT_ROOT / "v0.3-prelim" / "code" / "t23_real_kiss_sidm_two_comp_imfp.py"
        if not t23_path.exists():
            pytest.skip("t23 not at Windows-side")
        content = t23_path.read_text()
        assert "from config import" in content, "t23 must use config.py"