"""
Test class for v0.3-prelim runtime version guard.

Per R13 reviewer M1 suggestion in sidm review2.docx (2026-08-25):
'Code guardrails: add runtime checks to prevent users from accidentally
importing old v0.1/v0.2 modules when running v0.3 analysis.'

Tests:
  - Guard fires on v0.3 importing v0.1/v0.2 (warning)
  - Guard raises on strict mode (SIDM_STRICT_VERSION_GUARD=1)
  - Guard allows allowlisted cross-version imports (SPARC rotmod data)
  - Guard is inert when SIDM_SKIP_VERSION_GUARD=1 (test escape hatch)
"""
from __future__ import annotations
import importlib
import os
import sys
import warnings
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(PROJECT_ROOT / "v0.3-prelim" / "code"))

# IMPORTANT: tests of the guard must skip the guard itself
os.environ["SIDM_SKIP_VERSION_GUARD"] = "1"

from _version_guard import (
    is_cross_version_import,
    warn_or_raise,
    check_at_import,
    ALLOWLIST,
    DEPRECATED_VERSION_AT_TOP_OF_CALL_STACK,
)


class TestVersionGuard:
    """Tests for v0.3-prelim runtime version guard (R13 M1)."""

    def test_sentinel_exported(self):
        assert DEPRECATED_VERSION_AT_TOP_OF_CALL_STACK == "v0.3-prelim+guard-active"

    def test_allowlist_is_frozenset(self):
        assert isinstance(ALLOWLIST, frozenset)

    def test_allowlist_includes_sparc_rotmod(self):
        """SPARC rotmod data lives in v0.1; v0.3 needs to read it."""
        assert any("v0.1-prelim/data/Rotmod_LTG" in s for c, s in ALLOWLIST)

    def test_is_cross_version_import_v03_calling_v01(self):
        assert is_cross_version_import(
            "C:/path/v0.3-prelim/code/foo.py",
            "v0.1-prelim/code/old_module.py"
        ) is True

    def test_is_cross_version_import_v03_calling_v02(self):
        assert is_cross_version_import(
            "C:/path/v0.3-prelim/code/foo.py",
            "v0.2-prelim/code/old_module.py"
        ) is True

    def test_is_cross_version_import_v01_calling_v03(self):
        """v0.1 importing v0.3 is NOT cross-version for our purposes
        (v0.1 is older; v0.3 is canonical; this is an upgrade path)."""
        assert is_cross_version_import(
            "C:/path/v0.1-prelim/code/foo.py",
            "v0.3-prelim/code/new_module.py"
        ) is False

    def test_is_cross_version_import_v03_calling_v03(self):
        """Same-version imports don't fire the guard."""
        assert is_cross_version_import(
            "C:/path/v0.3-prelim/code/foo.py",
            "v0.3-prelim/code/other_module.py"
        ) is False

    def test_is_cross_version_import_v03_calling_sparc_rotmod(self):
        """Allowlisted: SPARC rotmod data in v0.1/data/Rotmod_LTG/."""
        assert is_cross_version_import(
            "C:/path/v0.3-prelim/code/sparc_loader.py",
            "v0.1-prelim/data/Rotmod_LTG/some_galaxy.rotmod"
        ) is False

    def test_warn_or_raise_emits_warning_in_normal_mode(self):
        """SIDM_STRICT_VERSION_GUARD not set → DeprecationWarning."""
        os.environ.pop("SIDM_STRICT_VERSION_GUARD", None)
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            warn_or_raise(
                "C:/path/v0.3-prelim/code/foo.py",
                "v0.1-prelim/code/old.py"
            )
        assert len(w) >= 1
        assert any(issubclass(item.category, DeprecationWarning) for item in w)

    def test_warn_or_raise_raises_in_strict_mode(self):
        """SIDM_STRICT_VERSION_GUARD=1 → ImportError."""
        os.environ["SIDM_STRICT_VERSION_GUARD"] = "1"
        try:
            with pytest.raises(ImportError, match="v0.3-prelim module"):
                warn_or_raise(
                    "C:/path/v0.3-prelim/code/foo.py",
                    "v0.1-prelim/code/old.py"
                )
        finally:
            os.environ.pop("SIDM_STRICT_VERSION_GUARD", None)

    def test_check_at_import_skipped_when_env_set(self):
        """SIDM_SKIP_VERSION_GUARD=1 → no-op."""
        os.environ["SIDM_SKIP_VERSION_GUARD"] = "1"
        try:
            # Should NOT raise or warn
            check_at_import("v0.1-prelim/code/anything.py")
            check_at_import("v0.2-prelim/code/anything.py")
        finally:
            os.environ.pop("SIDM_SKIP_VERSION_GUARD", None)

    def test_check_at_import_inert_for_v03_targets(self):
        """If the imported module is v0.3, no guard fires."""
        # This test runs in SIDM_SKIP mode (set at top of file), so we
        # temporarily unset to test the real behavior
        os.environ.pop("SIDM_SKIP_VERSION_GUARD", None)
        try:
            with warnings.catch_warnings(record=True) as w:
                warnings.simplefilter("always")
                check_at_import("v0.3-prelim/code/other.py")
            assert not any("v0.3-prelim module" in str(item.message) for item in w)
        finally:
            os.environ["SIDM_SKIP_VERSION_GUARD"] = "1"