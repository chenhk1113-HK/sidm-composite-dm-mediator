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

    def test_snapshot_constants_match_canonical(self):
        """The frozen snapshot must carry the SAME constants as the canonical config.

        Design (documented in both file headers): the project-root config.py is the live
        canonical file; v0.3-prelim/code/config.py is a FROZEN SNAPSHOT kept only so that
        scripts which do sys.path.insert(0, ".../v0.3-prelim/code") keep importing a local
        config module. Their header comment blocks deliberately differ. What must NOT drift
        is the code: every module-level constant (and every import) has to be identical,
        otherwise a script that picks up the snapshot silently gets old values.
        """
        import ast

        canonical = PROJECT_ROOT / "config.py"
        snapshot = PROJECT_ROOT / "v0.3-prelim" / "code" / "config.py"
        assert canonical.exists(), f"canonical config.py missing at {canonical}"
        assert snapshot.exists(), f"frozen snapshot missing at {snapshot}"

        def module_surface(path: Path) -> dict:
            tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
            surface: dict = {}
            for node in tree.body:
                if isinstance(node, ast.Assign):
                    for target in node.targets:
                        if isinstance(target, ast.Name):
                            surface[target.id] = ast.dump(ast.fix_missing_locations(node.value))
                elif isinstance(node, (ast.Import, ast.ImportFrom)):
                    surface[f"import::{ast.dump(node)}"] = True
                elif isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
                    surface[node.target.id] = ast.dump(node.value) if node.value else "<annotated>"
            return surface

        c_surface = module_surface(canonical)
        s_surface = module_surface(snapshot)
        assert c_surface, "canonical config.py defines no module-level constants"

        only_canonical = sorted(set(c_surface) - set(s_surface))
        only_snapshot = sorted(set(s_surface) - set(c_surface))
        mismatched = sorted(
            name for name in set(c_surface) & set(s_surface)
            if c_surface[name] != s_surface[name]
        )

        # Declared exemption (CG-16, 2026-11-08). The canonical config.py gained a
        # bootstrap that imports the single host-path source `scripts/paths.py`. The frozen
        # snapshot deliberately does NOT get it: the scripts that import the snapshot would
        # then resolve their roots against whatever tree they happen to run from, which is the
        # silent re-read risk the CG-16 inventory explicitly refuses
        # (v0.3-prelim/data/results/cg16_host_path_inventory.json -> decision.frozen_rule).
        # The exemption is narrow by construction: private `_CG16_*` names and the import
        # statements that bring `paths` (plus its sys/pathlib aliases) in. A constant name can
        # never be excused by it, which the assertion below proves rather than asserts in prose.
        def _is_cg16_bootstrap(name: str) -> bool:
            if name.startswith("_CG16_"):
                return True
            if name.startswith("import::"):
                body = name[len("import::"):]
                return "module='paths'" in body or (
                    "alias(name='sys'" in body and "alias(name='pathlib'" in body)
            return False

        # The classifier must not be a loophole: a physics-constant name is not bootstrap.
        assert not _is_cg16_bootstrap("SIGMA_0_CM2_G")
        assert not _is_cg16_bootstrap("REPO")
        assert not _is_cg16_bootstrap("import::Import(names=[alias(name='numpy')])")

        bootstrap = [n for n in only_canonical if _is_cg16_bootstrap(n)]
        drift = [n for n in only_canonical if not _is_cg16_bootstrap(n)]
        assert not (drift or only_snapshot or mismatched), (
            "frozen snapshot has drifted from the canonical config:\n"
            f"  missing in snapshot: {drift[:10]}\n"
            f"  extra in snapshot:   {only_snapshot[:10]}\n"
            f"  different value:     {mismatched[:10]}\n"
            f"  declared CG-16 bootstrap exempted: {bootstrap}"
        )

    def test_wsl_scratch_copy_divergence_is_recorded(self):
        """The WSL working copy is a SEPARATE scratch checkout, not a mirror.

        It is 13,686 B of an older-generation config used by some outputs/*.py diagnostic
        scripts that hardcode /home/lamkuenai/sidm-composite-dm-mediator. Byte-equality with
        the Windows files was therefore the wrong invariant (it failed on 2026-11-05 and the
        divergence is now recorded as an integrity finding instead of being asserted away).
        This test keeps the divergence visible: the copy must still exist, must still parse,
        and the divergence must be written down in the integrity report.
        """
        wsl_path_str = "/home/lamkuenai/sidm-composite-dm-mediator/v0.3-prelim/code/config.py"
        win_path = PROJECT_ROOT / "v0.3-prelim" / "code" / "config.py"
        report = PROJECT_ROOT / "docs" / "INTEGRITY_FINDINGS_2026-11-04.md"

        if sys.platform == "win32":
            if not (win_path.exists() and _wsl_path_exists(wsl_path_str)):
                pytest.skip("WSL scratch config.py not reachable from this session")
            status = subprocess.run(
                ["wsl", "--", "python3", "-c",
                 f"import ast,sys; ast.parse(open({wsl_path_str!r}).read()); print('PARSE_OK')"],
                capture_output=True, text=True, timeout=30,
            )
            assert "PARSE_OK" in status.stdout, (
                f"WSL scratch config.py no longer parses:\n{status.stdout}\n{status.stderr}"
            )
        else:
            if not Path(wsl_path_str).exists():
                pytest.skip("WSL scratch config.py not reachable from this session")

        assert report.exists(), f"integrity report missing at {report}"
        text = report.read_text(encoding="utf-8")
        assert "WSL scratch config" in text, (
            "the config.py split-brain divergence must be recorded in "
            "docs/INTEGRITY_FINDINGS_2026-11-04.md"
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