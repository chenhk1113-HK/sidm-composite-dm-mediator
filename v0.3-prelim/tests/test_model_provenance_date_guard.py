"""Unit tests for the provenance date guard in scripts/audit_model_provenance.py.

Class prevented (found live 2026-11-01 by the crash proof's CONTROL run): the
model-matching fallback cross-matched delegation records whose own agent-log
entries had been rotated out (2026-10-26) to sessions from a DIFFERENT day
(2026-10-31) that merely ran the same reviewer models — api_calls=140 against
the claims' 27 — and reported a fabricated CONTRADICTION against the report.

Guard asserted here: a model match counts ONLY within the manifest's own
calendar day; with no same-day match the function returns None, which main()
reports as UNVERIFIABLE (loud) rather than as evidence.
"""
import importlib.util
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
AUDIT_PATH = REPO / "scripts" / "audit_model_provenance.py"

_spec = importlib.util.spec_from_file_location("audit_model_provenance", AUDIT_PATH)
audit = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(audit)


def _manifest():
    # The 2026-10-26 delegation whose log record was later rotated out.
    return {"started": "2026-10-26 14:03:41",
            "tasks": [{"model": "deepseek-v4.1-flash"}]}


def _api_cross_day_only():
    # Only a 2026-10-31 session ran the model (the rotation scenario).
    return {"20261031_101010_deadbee": {"n_calls": 140,
                                        "models": {"deepseek-v4.1-flash"}}}


def _api_same_day_available():
    return {
        "20261031_101010_deadbee": {"n_calls": 140,
                                    "models": {"deepseek-v4.1-flash"}},
        "20261026_140341_realbeef": {"n_calls": 27,
                                     "models": {"deepseek-v4.1-flash"}},
    }


class TestDateGuard:
    def test_cross_day_match_is_refused(self):
        """Rotation scenario: the only model match is from another day -> None."""
        assert audit.session_for_delegation(_manifest(), _api_cross_day_only()) is None

    def test_same_day_match_still_works(self):
        got = audit.session_for_delegation(_manifest(), _api_same_day_available())
        assert got == "20261026_140341_realbeef"

    def test_higher_cross_day_count_never_wins(self):
        """Even a 140-call cross-day candidate loses to a 27-call same-day one."""
        got = audit.session_for_delegation(_manifest(), _api_same_day_available())
        assert got is not None and got.startswith("20261026")

    def test_primary_timestamp_path_untouched(self):
        """The date guard must not weaken the primary timestamp match."""
        api = _api_same_day_available()
        api["20261026_140340_primary"] = {"n_calls": 30,
                                          "models": {"nvidia/nemotron-3.5-lightning:free"}}
        got = audit.session_for_delegation(_manifest(), api)
        # Primary path: within 5 s of 'started' -> the primary session, even
        # though its model differs from the manifest's.
        assert got == "20261026_140340_primary" or (
            isinstance(got, list) and "20261026_140340_primary" in got)
