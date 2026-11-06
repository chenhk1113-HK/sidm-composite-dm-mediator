"""Guard: the two `constants.py` files must agree, and the flat name must serve both layers.

Why this test exists (2026-11-04 integrity sweep):
- `constants.py` (convention layer) and `scripts/constants.py` (numeric layer) share the flat
  module name `constants`. Python caches that name process-wide, so a full-directory pytest run
  used whichever file was imported first and then raised
  `ImportError: cannot import name 'SIGMA_0_CM2_PER_G' from 'constants'` for tests that needed
  the numeric layer (5 collection errors), while the same tests passed when run as explicit files.
- `HBAR_C_GEV_CM` was defined in BOTH files with DIFFERENT values (1.97327e-14 vs 1.973e-14,
  0.014% apart), so a cross-section computed through (hbar*c)^2 silently differed by 0.027%
  depending on which file won the name.
- A wider scan of the repo counted 12 distinct spellings of hbar*c across 53 assignment sites
  (1.97e-14, 1.973e-14, 1.97327e-14, 1.973269804e-14, 0.1973e-13, 197.3 MeV*cm, ...), the
  coarsest being 0.166% from CODATA - a 0.33% difference in any sigma proportional to (hbar*c)^2.

This test does not re-derive physics. It pins the invariant that the shared names have exactly one
value, that the value matches CODATA, and that both layers are reachable through the flat name in
one process regardless of import order. conftest.py builds the composite it checks.
"""
from __future__ import annotations

import importlib.util
import math
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
CODATA_HBAR_C_GEV_CM = 1.973269804e-14  # GeV*cm

CONVENTION_ONLY = ("ALPHA_D", "KAPPA_C", "KAPPA_C_ANALYTIC", "MU_RED_GEV", "compute_kappa")
NUMERIC_ONLY = ("SIGMA_0_CM2_PER_G", "A_SLOPE", "V_REF_KMS", "V_TARGET_KMS", "F_H_CANONICAL",
                "HBAR_C_SQ_GEV2_CM2")


def _load_private(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def layers():
    convention = _load_private(REPO_ROOT / "constants.py", "guard_convention_layer")
    numeric = _load_private(REPO_ROOT / "scripts" / "constants.py", "guard_numeric_layer")
    return convention, numeric


def _module_level_names(module) -> dict:
    return {k: v for k, v in vars(module).items() if not k.startswith("__")}


def test_shared_names_have_exactly_one_value(layers):
    """Every name defined in both files must be identical, or the flat name is ambiguous."""
    convention, numeric = layers
    a = _module_level_names(convention)
    b = _module_level_names(numeric)
    shared = sorted(set(a) & set(b))
    assert shared, "expected the two layers to share names (C_KMS, M_CHI_GEV, HBAR_C_GEV_CM)"
    differing = [k for k in shared if a[k] != b[k]]
    assert not differing, (
        f"constants collision: {differing} differ between constants.py and scripts/constants.py: "
        + "; ".join(f"{k}: {a[k]!r} vs {b[k]!r}" for k in differing)
    )
    for required in ("C_KMS", "M_CHI_GEV", "HBAR_C_GEV_CM"):
        assert required in shared, f"{required} expected in both layers"


def test_hbar_c_matches_codata(layers):
    """The shared hbar*c must be the accepted value, not a truncated spelling."""
    _, numeric = layers
    value = numeric.HBAR_C_GEV_CM
    rel = abs(value - CODATA_HBAR_C_GEV_CM) / CODATA_HBAR_C_GEV_CM
    assert rel < 1e-6, (
        f"HBAR_C_GEV_CM = {value!r} is {rel * 100:.4f}% from CODATA {CODATA_HBAR_C_GEV_CM!r}; "
        f"a sigma built from (hbar*c)^2 inherits twice that"
    )
    # the previously-shipped truncated value must not come back
    assert value != 1.973e-14 and value != 1.97e-14


def test_hbar_c_squared_is_derived_not_hardcoded(layers):
    _, numeric = layers
    assert numeric.HBAR_C_SQ_GEV2_CM2 == numeric.HBAR_C_GEV_CM ** 2


def test_flat_name_serves_both_layers_in_one_process():
    """conftest installs a composite; both layers' exclusive names must resolve from it."""
    flat = sys.modules.get("constants")
    assert flat is not None, "expected conftest to have installed the composite 'constants'"
    missing_convention = [k for k in CONVENTION_ONLY if not hasattr(flat, k)]
    missing_numeric = [k for k in NUMERIC_ONLY if not hasattr(flat, k)]
    assert not missing_convention, f"convention-layer names missing from 'constants': {missing_convention}"
    assert not missing_numeric, f"numeric-layer names missing from 'constants': {missing_numeric}"
    assert callable(getattr(flat, "compute_kappa", None))


def test_producers_from_both_layers_resolve_to_the_same_module():
    """Import one producer per layer in the same process; each must see the composite.

    gravothermal_yang2024 consumes numeric-layer names (SIGMA_0_CM2_PER_G, A_SLOPE, V_REF_KMS);
    v19_2_f_priority1_resonance_helpers consumes convention-layer names (MU_RED_GEV, HBAR_C_GEV_CM,
    C_KMS). Before the conftest composite, a session that cached one layer first made the other
    producer's import fail or bind a different hbar*c.
    """
    sys.path.insert(0, str(REPO_ROOT / "v0.3-prelim" / "code"))
    sys.path.insert(0, str(REPO_ROOT / "scripts"))
    numeric_side = importlib.import_module("gravothermal_yang2024")
    convention_side = importlib.import_module("v19_2_f_priority1_resonance_helpers")
    flat = sys.modules["constants"]

    # gravothermal_yang2024 imports the numeric names as private aliases
    # (`SIGMA_0_CM2_PER_G as _SIGMA_0`), so a public-name-only probe finds nothing and the
    # guard would pass vacuously. Accept either spelling.
    #
    # 2026-11-06 (finding F26): the amplitude names now have a second spelling, `*_ARCHIVED`,
    # used by the modules that deliberately publish archived-pair numbers. The invariant being
    # checked is unchanged - one value per shared name - but an archived value is only legal when
    # it arrives under an archived-looking name AND the module declares its pairing. A bare
    # SIGMA_0_CM2_PER_G that holds 0.052 is exactly the ambiguity F23/F26 exists to prevent, so it
    # fails here rather than resolving to whatever the composite happens to say.
    numeric_spellings = {
        "SIGMA_0_CM2_PER_G": ("SIGMA_0_CM2_PER_G", "_SIGMA_0", "SIGMA_0_CM2_PER_G_ARCHIVED"),
        "SIGMA_PEAK_CM2_PER_G": ("SIGMA_PEAK_CM2_PER_G", "_SIGMA_PEAK",
                                 "SIGMA_PEAK_CM2_PER_G_ARCHIVED"),
        "A_SLOPE": ("A_SLOPE", "_A_SLOPE"),
        "V_REF_KMS": ("V_REF_KMS", "_V_REF_KMS", "_V_REF", "V_REF"),
        "V_TARGET_KMS": ("V_TARGET_KMS", "_V_TARGET_KMS", "_V_TARGET", "V_TARGET"),
        "SIGMA_KMS": ("SIGMA_KMS", "_SIGMA_KMS", "_SIGMA_1", "FWHM"),
    }
    ARCHIVED_VALUE = {
        "SIGMA_0_CM2_PER_G": getattr(flat, "SIGMA_0_LEGACY_PAIR_052"),
        "SIGMA_PEAK_CM2_PER_G": getattr(flat, "SIGMA_PEAK_LEGACY_PAIR_174"),
    }
    numeric_src = Path(numeric_side.__file__).read_text(encoding="utf-8", errors="replace")
    declares_archived = "PAIRING: ARCHIVED PAIR" in numeric_src
    got_numeric = []
    for a, spellings in numeric_spellings.items():
        for spelling in spellings:
            if hasattr(numeric_side, spelling):
                got_numeric.append((a, spelling, getattr(numeric_side, spelling)))
                break
    assert got_numeric, "gravothermal_yang2024 no longer binds any numeric-layer constant"
    for attr, spelling, value in got_numeric:
        live = getattr(flat, attr)
        archived = ARCHIVED_VALUE.get(attr, live)
        if spelling.endswith("_ARCHIVED"):
            assert declares_archived, (
                f"{attr}: {numeric_side.__name__} binds {spelling} to the archived pair without the "
                "'PAIRING: ARCHIVED PAIR' declaration that tells a reader which pairing it publishes")
            assert value == archived, (
                f"{attr}: {spelling} promises the archived pair but holds {value!r}; the archived "
                f"pair value is {archived!r}")
        else:
            if value != live and value == archived:
                raise AssertionError(
                    f"{attr}: {numeric_side.__name__} holds the ARCHIVED value {value!r} under the "
                    f"live-looking name {spelling!r}. Import it as "
                    f"SIGMA_0_LEGACY_PAIR_052 as {spelling}_ARCHIVED so the pairing is visible at "
                    "every use site.")
            assert value == live, f"{attr}: producer has {value!r}, composite has {live!r}"

    convention_attrs = ("HBAR_C_GEV_CM", "C_KMS", "MU_RED_GEV", "M_CHI_GEV")
    got_convention = [(a, getattr(convention_side, a)) for a in convention_attrs if hasattr(convention_side, a)]
    assert got_convention, "priority1_resonance_helpers no longer binds any convention-layer constant"
    for attr, value in got_convention:
        assert value == getattr(flat, attr), f"{attr}: producer has {value!r}, composite has {getattr(flat, attr)!r}"

    hbar = [v for a, v in got_convention if a == "HBAR_C_GEV_CM"]
    if hbar:
        rel = abs(hbar[0] - CODATA_HBAR_C_GEV_CM) / CODATA_HBAR_C_GEV_CM
        assert rel < 1e-6, f"a producer is using hbar*c = {hbar[0]!r}, {rel * 100:.4f}% from CODATA"
