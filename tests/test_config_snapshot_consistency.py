"""
Consistency tests for the dual config.py setup (canonical + snapshot).

GOAL: When config constants are edited, the snapshot at
v0.3-prelim/code/config.py MUST be updated to match. Otherwise scripts that
explicitly do sys.path.insert(0, 'v0.3-prelim/code') and import config will
load the stale snapshot and behave inconsistently from the canonical config.

Per AGENTS.md "edit the wrong file" pattern (2026-09-12): this happens more
often than it should because the v0.3-prelim copy looks like the canonical
file (it's in a versioned subdirectory, has the same name, has nearly the
same content).

WHAT THIS TEST DOES:
- Imports the canonical config (project root, via sys.path priority)
- Imports the snapshot config (explicitly, by file path)
- Asserts that ALL key constants match
- If they don't match, reports exactly which ones differ with the diff

KEY CONSTANTS MONITORED (extend as needed):
- LENS_SIGMA_M_LOG_WIDTH (the one that bit us 2026-09-12)
- LENS_SIGMA_M_LOG_PEAK
- LOG_SIGMA_M_RANGE, A_RANGE, NLIVE, DLOGZ
- V_REF, V_GALAXY
- All observational velocity scales and prior bounds

If you intentionally diverge the snapshot from the canonical config
(e.g., a frozen release snapshot for paper reproducibility), add the
differing constants to the ALLOWLIST with a one-line explanation.
"""
from __future__ import annotations
import importlib.util
import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SNAPSHOT_PATH = PROJECT_ROOT / "v0.3-prelim" / "code" / "config.py"


def _import_snapshot():
    """Import the snapshot config.py by explicit file path.

    Bypasses sys.path priority to force loading the snapshot file directly.
    The snapshot has its own docstring/banner but should still expose the
    same module-level constants as the canonical config.
    """
    spec = importlib.util.spec_from_file_location(
        "config_snapshot_v03", SNAPSHOT_PATH
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _import_canonical():
    """Import the canonical config.py at project root via sys.path priority."""
    # Make sure the project root is on sys.path FIRST
    if str(PROJECT_ROOT) not in sys.path:
        sys.path.insert(0, str(PROJECT_ROOT))
    # Clear any cached config module so we re-import from project root
    for mod_name in list(sys.modules.keys()):
        if mod_name == "config":
            del sys.modules[mod_name]
    import config
    return config


# Constants to monitor for consistency. Add new critical constants here.
# All must be importable from BOTH the canonical and snapshot configs.
KEY_CONSTANTS = [
    "LENS_SIGMA_M_LOG_WIDTH",
    "LENS_SIGMA_M_LOG_PEAK",
    "LOG_SIGMA_M_RANGE",
    "A_RANGE",
    "NLIVE",
    "DLOGZ",
    "V_REF",
    "V_GALAXY",
    "VDEP_LOG_RHO_RANGE",
    "RESULTS_DIR_V03",
]

# Constants that are intentionally allowed to differ between canonical and
# snapshot. Add a one-line justification for each divergence.
# Format: {constant_name: "reason for divergence"}
ALLOWLIST = {
    # DM_SIDM_PROJECT_ROOT is set by _detect_root() at runtime and may differ
    # between hosts. Not a divergence of code state — just environment.
    # Remove if you want to test that _detect_root() is deterministic.
}


class TestConfigSnapshotConsistency:
    """The canonical and snapshot configs MUST agree on key constants."""

    @pytest.fixture(scope="class")
    def canonical_config(self):
        return _import_canonical()

    @pytest.fixture(scope="class")
    def snapshot_config(self):
        return _import_snapshot()

    def test_snapshot_exists(self):
        """The snapshot file must exist (otherwise this test is meaningless)."""
        assert SNAPSHOT_PATH.exists(), (
            f"Snapshot config not found at {SNAPSHOT_PATH}. "
            "If you deleted it intentionally, update this test."
        )

    def test_canonical_imports_cleanly(self, canonical_config):
        """The canonical config must import without raising."""
        assert canonical_config is not None

    def test_snapshot_imports_cleanly(self, snapshot_config):
        """The snapshot config must import without raising."""
        assert snapshot_config is not None

    @pytest.mark.parametrize("const_name", KEY_CONSTANTS)
    def test_key_constant_matches(self, canonical_config, snapshot_config,
                                   const_name):
        """Each KEY_CONSTANT must have the same value in canonical and snapshot."""
        if const_name in ALLOWLIST:
            pytest.skip(f"Allowlisted divergence: {ALLOWLIST[const_name]}")

        # Check both have the attribute
        assert hasattr(canonical_config, const_name), (
            f"Canonical config is missing '{const_name}'. "
            "Either add it to KEY_CONSTANTS or the canonical config is broken."
        )
        assert hasattr(snapshot_config, const_name), (
            f"Snapshot config is missing '{const_name}'. "
            "Either add it to KEY_CONSTANTS or the snapshot is broken."
        )

        canon_val = getattr(canonical_config, const_name)
        snap_val = getattr(snapshot_config, const_name)

        assert canon_val == snap_val, (
            f"DIVERGENCE on '{const_name}':\n"
            f"  Canonical (project-root config.py): {canon_val!r}\n"
            f"  Snapshot (v0.3-prelim/code/config.py): {snap_val!r}\n"
            f"\n"
            f"  ACTION: Edit the snapshot to match the canonical, "
            f"OR add '{const_name}' to the ALLOWLIST with a justification."
        )


class TestConfigSnapshotBanner:
    """The snapshot file must have the FROZEN-SNAPSHOT banner to prevent
    accidental edits."""

    def test_snapshot_has_frozen_banner(self):
        """The snapshot config must contain the FROZEN-SNAPSHOT banner."""
        content = SNAPSHOT_PATH.read_text()
        assert "THIS FILE IS A FROZEN SNAPSHOT" in content, (
            "The v0.3-prelim/code/config.py snapshot is missing the "
            "'FROZEN SNAPSHOT' banner. Without it, future sessions may "
            "edit this file thinking it's canonical."
        )

    def test_snapshot_banner_mentions_canonical_path(self):
        """The snapshot banner must point to the canonical config path."""
        content = SNAPSHOT_PATH.read_text()
        assert "../../config.py" in content or "project root" in content.lower(), (
            "The snapshot banner must reference the canonical config location."
        )


class TestCanonicalConfigBanner:
    """The canonical config must have the CANONICAL-LIVE banner."""

    def test_canonical_has_live_banner(self):
        """The canonical config must contain the CANONICAL-LIVE banner."""
        canonical_path = PROJECT_ROOT / "config.py"
        content = canonical_path.read_text()
        assert "THIS IS THE CANONICAL" in content, (
            "The project-root config.py is missing the 'CANONICAL (LIVE)' "
            "banner. Future sessions may edit the snapshot instead."
        )