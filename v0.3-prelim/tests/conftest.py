"""Conftest.py — sets up sys.path for tests/ to find the right config.py.

The project has TWO config.py files:
  - config.py at the project root (contains V_REF/RADIO_RELIC but NOT eROSITA)
  - v0.3-prelim/code/config.py (the real one, has eROSITA)

Pytest's path resolution can pick up the root one when running from
v0.3-prelim/tests/. This conftest forces the right one to be found first.
"""

import sys
from pathlib import Path

PROJECT_CODE = Path(__file__).resolve().parent.parent / "code"
PROJECT_CODE_STR = str(PROJECT_CODE)
if PROJECT_CODE_STR not in sys.path:
    sys.path.insert(0, PROJECT_CODE_STR)

# Drop any stale 'config' module that may have been imported from the wrong
# location (the root config.py).
sys.modules.pop("config", None)