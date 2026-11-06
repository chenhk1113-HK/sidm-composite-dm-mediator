"""Guard for the f_H pairing registry (finding F26).

The registry is the project's statement of WHICH pairing every module publishes. It is only worth
having if it cannot silently drift from the source, so this test re-derives it from the code on
disk and compares, then checks the two invariants the pairing rule claims:

  1. no producer module binds both pairings (mixed), and
  2. every archived-pair module says so in its own source.
"""
import json
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "scripts"))

import fH_pairing_registry as producer  # noqa: E402
import constants as framework_constants  # noqa: E402

ARTIFACT = REPO / "v0.3-prelim" / "data" / "results" / "fH_pairing_registry.json"


@pytest.fixture(scope="module")
def stored():
    assert ARTIFACT.exists(), f"missing pairing registry: {ARTIFACT}"
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def rebuilt():
    return producer.scan()


def test_registry_describes_the_current_source(rebuilt):
    """The artifact may not be a snapshot of some older tree."""
    assert ARTIFACT.exists()
    stored = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    for key in ("canonical_pair_modules", "archived_pair_modules", "mixed_pair_modules",
                "archived_contract_modules_missing_declaration"):
        assert sorted(stored.get(key, [])) == sorted(rebuilt[key]), (
            f"{key} drifted from the source: artifact-only="
            f"{sorted(set(stored.get(key, [])) - set(rebuilt[key]))} "
            f"source-only={sorted(set(rebuilt[key]) - set(stored.get(key, [])))}")


def test_no_producer_module_publishes_both_pairings(rebuilt):
    assert rebuilt["mixed_pair_modules"] == [], (
        "these modules import both an archived-looking and a live pairing name, so a reader cannot "
        f"tell which pairing they publish: {rebuilt['mixed_pair_modules']}")


def test_every_archived_module_declares_its_pairing(rebuilt):
    assert rebuilt["archived_contract_modules_missing_declaration"] == [], (
        "archived-pair modules must carry the '# PAIRING: ARCHIVED PAIR' declaration: "
        f"{rebuilt['archived_contract_modules_missing_declaration']}")


def test_both_buckets_are_populated(rebuilt):
    """A registry where everything is 'archived' or everything is 'canonical' would pass the
    invariant checks vacuously; the canonical side is the live model and must be non-empty."""
    assert len(rebuilt["canonical_pair_modules"]) >= 5
    assert len(rebuilt["archived_pair_modules"]) >= 10


def test_registry_values_match_the_live_constants(stored):
    assert stored["canonical_pair_values"]["f_H"] == framework_constants.F_H_CANONICAL
    assert stored["canonical_pair_values"]["sigma_0_cm2_per_g"] == framework_constants.SIGMA_0_CM2_PER_G
    assert (stored["canonical_pair_values"]["sigma_peak_cm2_per_g"]
            == framework_constants.SIGMA_PEAK_CM2_PER_G)
    assert stored["archived_pair_values"]["f_H"] == framework_constants.F_H_LEGACY_PLACEHOLDER_0297
    assert stored["archived_pair_values"]["sigma_0_cm2_per_g"] == framework_constants.SIGMA_0_LEGACY_PAIR_052
    assert stored["archived_pair_values"]["sigma_peak_cm2_per_g"] == framework_constants.SIGMA_PEAK_LEGACY_PAIR_174


def test_pairing_factor_is_the_squared_f_H_ratio(stored):
    """The registry's conversion factor must be derivable, not asserted."""
    k = stored["pairing_k_legacy_to_canonical"]
    expected = (framework_constants.F_H_LEGACY_PLACEHOLDER_0297 ** 2
                / framework_constants.F_H_CANONICAL ** 2)
    assert k == pytest.approx(expected, rel=1e-12)
    assert (stored["archived_pair_values"]["sigma_peak_cm2_per_g"] * k
            == pytest.approx(stored["canonical_pair_values"]["sigma_peak_cm2_per_g"], rel=1e-12))
