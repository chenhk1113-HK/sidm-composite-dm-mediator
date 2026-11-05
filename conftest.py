"""
Pytest conftest — sys.path setup plus one deterministic `constants` module.
"""
import importlib.util
import os
import sys
import types

_REPO = os.path.dirname(os.path.abspath(__file__))

# Add v0.3-prelim/code to path so tests can import modules
sys.path.insert(
    0,
    os.path.join(_REPO, "v0.3-prelim", "code")
)


def _load_layer(private_name: str, path: str):
    """Load one constants layer by file path under a private module name.

    Caching in sys.modules before exec makes this cycle-safe: a layer that
    itself imports the other layer would otherwise recurse.
    """
    mod = sys.modules.get(private_name)
    if mod is None:
        spec = importlib.util.spec_from_file_location(private_name, path)
        mod = importlib.util.module_from_spec(spec)
        sys.modules[private_name] = mod
        spec.loader.exec_module(mod)
    return mod


# ---------------------------------------------------------------------------
# `constants` exists TWICE in this repo:
#   constants.py            - coupling-convention layer (ALPHA_D, KAPPA_C,
#                             KAPPA_C_ANALYTIC, MU_RED_GEV, G_CHI, compute_kappa)
#   scripts/constants.py    - numeric layer (SIGMA_0_CM2_PER_G, A_SLOPE, V_REF_KMS,
#                             V_TARGET_KMS, F_H_CANONICAL, HBAR_C_*, q_mev, ...)
# Both are consumed with the same flat name (`from constants import ...`), and
# Python caches that flat name process-wide: whichever file a process imports
# first is what every later `from constants import ...` gets, regardless of what
# the importing module put on sys.path. Two consequences, both observed here:
#   1. Collection order decided the outcome. A full-directory pytest run cached
#      the root layer first, then failed with "ImportError: cannot import name
#      'SIGMA_0_CM2_PER_G' from 'constants'" for every test that imported a
#      numeric-layer producer (5 collection errors, 2026-11-04), while the same
#      tests run as explicit files passed.
#   2. The three names defined in BOTH files were not guaranteed to agree:
#      HBAR_C_GEV_CM was 1.97327e-14 in one file and 1.973e-14 in the other
#      (0.014% apart), so anything computed through (hbar*c)^2 differed by
#      0.027% depending on which file won the name. The values are now identical
#      and tests/test_constants_single_source.py makes that a checked invariant.
# This conftest builds one composite holding BOTH layers, with a hard equality
# check on any name defined by both, so the flat name resolves the same way in
# every process regardless of import order.
# ---------------------------------------------------------------------------
_NUMERIC = _load_layer("sidm_numeric_constants", os.path.join(_REPO, "scripts", "constants.py"))
_CONVENTION = _load_layer("sidm_convention_constants", os.path.join(_REPO, "constants.py"))

_composite = types.ModuleType("constants")
_composite.__doc__ = ("Composite of constants.py (convention layer) and scripts/constants.py "
                      "(numeric layer); built in conftest.py so the flat module name cannot "
                      "resolve to a single layer by accident.")
for _layer in (_NUMERIC, _CONVENTION):
    for _k in dir(_layer):
        if _k.startswith("__"):
            continue
        if _k in _composite.__dict__ and getattr(_composite, _k) != getattr(_layer, _k):
            raise RuntimeError(
                f"constants collision: {_k!r} differs between constants.py and "
                f"scripts/constants.py ({getattr(_composite, _k)!r} vs {getattr(_layer, _k)!r})"
            )
        setattr(_composite, _k, getattr(_layer, _k))
_composite.SIDM_NUMERIC_LAYER = _NUMERIC
_composite.SIDM_CONVENTION_LAYER = _CONVENTION

sys.modules["constants"] = _composite
