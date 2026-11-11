"""Seed-and-interval contract tests (ReviewResponse round, 2026-11-11).

Covers the three things the rule needs to be worth anything:
  1. the interval helper returns an interval that actually comes from the samples;
  2. recording a seed genuinely makes a stochastic run repeatable (dynesty `rstate`),
     and changing it genuinely changes the draw (so a recorded seed means something);
  3. the headline producers cannot silently lose the contract again, and the forward-rule
     audit runs clean.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import numpy as np
import pytest

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "scripts"))
import paths  # noqa: E402
sys.path.insert(0, str(paths.CODE_DIR))
import repro_contract as rc  # noqa: E402


# ----------------------------------------------------------------- interval math
def test_unweighted_interval_comes_from_the_samples():
    samples = np.linspace(0.0, 100.0, 1001)
    out = rc.credible_interval(samples)
    assert out["median"] == pytest.approx(50.0, abs=0.05)
    lo, hi = out["credible_16_84"]
    assert lo == pytest.approx(16.0, abs=0.05)
    assert hi == pytest.approx(84.0, abs=0.05)
    assert lo < out["median"] < hi
    assert out["n_samples"] == 1001
    assert "percentile" in out["basis"]


def test_weighted_interval_shifts_toward_the_weight():
    samples = np.array([0.0, 1.0, 2.0, 3.0, 4.0])
    flat = rc.credible_interval(samples)
    heavy_high = rc.credible_interval(samples, weights=np.array([1, 1, 1, 10, 10]))
    assert heavy_high["credible_16_84"][0] > flat["credible_16_84"][0]


def test_posterior_summary_labels_are_checked():
    chain = np.random.default_rng(3).normal(size=(500, 3))
    out = rc.posterior_summary(chain, ["a", "b", "c"])
    for name in ("a", "b", "c"):
        lo, hi = out[name]["credible_16_84"]
        assert lo <= out[name]["median"] <= hi
    assert out["_meta"]["n_samples"] == 500
    with pytest.raises(ValueError):
        rc.posterior_summary(chain, ["a", "b"])  # width mismatch must be refused


def test_median_std_companion_is_symmetric():
    assert rc.interval_from_median_std(2.0, 0.5) == [1.5, 2.5]


def test_seed_block_is_refused_without_a_seed():
    with pytest.raises(ValueError):
        rc.seed_provenance(None)
    payload = rc.attach_reproducibility({"result": 1.0}, 42, sampler="emcee", n_samples=10)
    assert payload["seed"] == 42
    assert payload["reproducibility"]["seed"] == 42
    assert payload["reproducibility"]["sampler"] == "emcee"
    assert "numpy" in payload["reproducibility"]


# ----------------------------------------------------------------- seeding is real
def _toy_loglike(x):
    x = np.asarray(x)
    return -0.5 * float(np.sum((x - 1.0) ** 2))


def _toy_prior(u):
    return -2.0 + 4.0 * np.asarray(u)


def _run(seed: int):
    import dynesty
    sampler = dynesty.NestedSampler(_toy_loglike, _toy_prior, 2, nlive=16,
                                    rstate=np.random.default_rng(seed))
    sampler.run_nested(dlogz=1.0)
    return sampler.results


def test_same_seed_reproduces_and_another_seed_does_not():
    a = _run(20261111)
    b = _run(20261111)
    c = _run(20261112)
    assert float(a.logz[-1]) == pytest.approx(float(b.logz[-1]), abs=1e-9), \
        "the same recorded seed must reproduce the same evidence"
    assert a.samples.shape == b.samples.shape
    assert np.allclose(a.samples, b.samples), "same seed must give the same posterior samples"
    assert not np.isclose(float(a.logz[-1]), float(c.logz[-1]), atol=1e-9), \
        "a different seed should change the draw, otherwise the recorded seed is decoration"


# ----------------------------------------------------------------- producers keep it
@pytest.mark.parametrize("name", ["T205_full_likelihood_published.py",
                                  "T207c_priored_free_emcee.py"])
def test_headline_producers_carry_the_contract(name):
    src = (paths.CODE_DIR / name).read_text(encoding="utf-8")
    assert "repro_contract" in src, f"{name} no longer imports the reproducibility contract"
    assert "attach_reproducibility" in src, f"{name} no longer records its seed"
    if name.startswith("T205"):
        assert src.count("rstate=np.random.default_rng(SEED)") == 2, \
            "both T205 nested samplers must be seeded"
        assert "posterior_credible_16_84" in src, "T205 must publish credible intervals"


def test_seed_interval_audit_runs_and_enforces_the_forward_rule():
    proc = subprocess.run(
        [sys.executable, str(paths.SCRIPTS_DIR / "seed_interval_audit.py"), "--json"],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
        env={**os.environ, "PYTHONUTF8": "1"}, timeout=600,
    )
    assert proc.returncode == 0, f"audit failed:\n{proc.stdout[-2000:]}\n{proc.stderr[-2000:]}"
    data = json.loads((proc.stdout or "").strip())
    counts = data["counts"]
    assert counts["total"] > 0
    assert counts["stochastic"] > 0, "no stochastic artifact recognised - audit is not scanning"
    assert counts["forward_violation"] == 0
    assert counts["seed"] > 0 and counts["interval"] > 0
    inv = Path(data["inventory"])
    assert inv.exists()
    payload = json.loads(inv.read_text(encoding="utf-8"))
    assert payload["conduct_date"] == rc.CONDUCT_DATE
    assert len(payload["per_stochastic_file"]) == counts["stochastic"]
    assert payload["corrupt_artifacts"], "the disclosed truncated artifact must stay listed"


def test_audit_flags_a_new_run_that_skips_the_contract(tmp_path):
    """The forward rule must actually fail closed, not just report."""
    script = tmp_path / "probe_audit.py"
    script.write_text(
        "import sys\n"
        f"sys.path.insert(0, {str(paths.SCRIPTS_DIR)!r})\n"
        "import seed_interval_audit as a\n"
        "payload = {'posterior_medians': {'sigma_peak': 196.3},\n"
        "           'metadata': {'description': 'dynesty nested sampling, nlive=200'}}\n"
        "assert a.looks_stochastic(payload), 'a sampler-shaped artifact must be recognised'\n"
        "assert not a.has_seed(payload)\n"
        "assert not a.has_interval(payload)\n"
        "good = dict(payload, seed=7,\n"
        "            credible_16_84=[190.0, 202.0])\n"
        "assert a.has_seed(good) and a.has_interval(good)\n"
        "print('FLAGGED')\n",
        encoding="utf-8",
    )
    proc = subprocess.run([sys.executable, str(script)], capture_output=True, text=True,
                          encoding="utf-8", errors="replace", timeout=120)
    assert "FLAGGED" in (proc.stdout or ""), proc.stdout + proc.stderr
