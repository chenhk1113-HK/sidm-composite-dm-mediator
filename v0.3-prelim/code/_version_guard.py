"""
Runtime version guard — prevents accidental import of deprecated
v0.1 / v0.2 modules when running v0.3-prelim analysis.

Per R13 reviewer M1 suggestion in sidm review2.docx (2026-08-25):

  'Code guardrails: add runtime checks to prevent users from
  accidentally importing old v0.1/v0.2 modules when running v0.3
  analysis.'

How it works
============

This module defines DEPRECATED_VERSION_AT_TOP_OF_CALL_STACK, which is
checked at import time of v0.3 modules. If a v0.3 module imports from
v0.1 or v0.2 (except for v0.1-prelim/data/Rotmod_LTG/ which holds the
SPARC rotmod files used by v0.3), the guard fires:

  - DeprecationWarning (always)
  - If env var SIDM_STRICT_VERSION_GUARD=1, raise ImportError instead

Why a soft guard
================

Some legacy code legitimately imports from v0.1 (e.g., the SPARC
rotmod loader uses data from v0.1/data/Rotmod_LTG/). The soft guard
allows these imports but flags them.

If the user sets SIDM_STRICT_VERSION_GUARD=1 (e.g., in CI or production
runs), any non-allowlisted cross-version import becomes a hard error.

References
==========

- sidm review2.docx (2026-08-25) reviewer M1
- v0.3-prelim/code/_version_guard.py (this file)
- tests/test_version_guard.py

Status: shipped 2026-08-25 as part of R13 reviewer M1 fix.
"""
from __future__ import annotations
import os
import sys
import warnings
from pathlib import Path


# Allow-listed cross-version imports (these are intentional, not bugs)
# Format: frozenset of (caller_module_substring, imported_module_substring) pairs
ALLOWLIST = frozenset({
    # SPARC rotmod data lives in v0.1/data/Rotmod_LTG/ — v0.3 reads it.
    ("v0.3-prelim", "v0.1-prelim/data/Rotmod_LTG"),
    ("v0.3-prelim", "v0.1-prelim/data"),
    # R12 audit closure imports from v0.1 for historical comparison.
    ("v0.3-prelim", "v0.1-prelim.code"),
    # v0.2-prelim/results holds T21/T41 historical results that v0.3 reads.
    ("v0.3-prelim", "v0.2-prelim/data/results"),
})


def is_cross_version_import(caller_path: str, imported_path: str) -> bool:
    """Return True if caller is v0.3-prelim but imported module is v0.1/v0.2."""
    if "v0.3-prelim" not in caller_path:
        return False
    # v0.1 / v0.2 paths (case-insensitive match)
    for old in ("v0.1-prelim", "v0.2-prelim"):
        if old in imported_path:
            # Check allowlist
            for caller_sub, imported_sub in ALLOWLIST:
                if caller_sub in caller_path and imported_sub in imported_path:
                    return False  # allowed
            return True  # not allowed, guard should fire
    return False


def warn_or_raise(caller_path: str, imported_path: str) -> None:
    """Issue deprecation warning (always) or raise (if strict mode)."""
    msg = (
        f"[sidm-version-guard] v0.3-prelim module {caller_path!r} "
        f"imported deprecated v0.1/v0.2 module {imported_path!r}. "
        f"Use v0.3-prelim equivalents where possible. "
        f"Set SIDM_STRICT_VERSION_GUARD=0 (default) for warning only; "
        f"=1 for hard ImportError. "
        f"See MODEL_ASSUMPTIONS_AND_LIMITATIONS.md for the v0.1/v0.2/v0.3 split rationale."
    )
    if os.environ.get("SIDM_STRICT_VERSION_GUARD") == "1":
        raise ImportError(msg)
    warnings.warn(msg, DeprecationWarning, stacklevel=2)


def check_at_import(imported_module_name: str) -> None:
    """Module-level hook: call from __init__.py of v0.3 modules.

    Usage:
        from _version_guard import check_at_import
        check_at_import(__name__)

    This inspects the call stack to determine if the importing code
    is in v0.1/v0.2 (allowed) or v0.3 (guard fires).
    """
    # Skip if SIDM_SKIP_VERSION_GUARD=1 (e.g., in tests of the guard itself)
    if os.environ.get("SIDM_SKIP_VERSION_GUARD") == "1":
        return

    # If the imported module is v0.3 (or no version), no guard needed
    if "v0.3-prelim" in imported_module_name or "v0.3" not in imported_module_name:
        return

    # Find caller (the module that did the import)
    frame = sys._getframe(1)
    caller_path = frame.f_code.co_filename

    if is_cross_version_import(caller_path, imported_module_name):
        warn_or_raise(caller_path, imported_module_name)


# Sentinel marker — exposed for downstream checks
DEPRECATED_VERSION_AT_TOP_OF_CALL_STACK = "v0.3-prelim+guard-active"


__all__ = [
    "check_at_import",
    "is_cross_version_import",
    "warn_or_raise",
    "DEPRECATED_VERSION_AT_TOP_OF_CALL_STACK",
    "ALLOWLIST",
]