"""Reproducibility contract for stochastic results (added 2026-11-11, ReviewResponse round).

Rule this implements: a number produced by a sampler, a Monte Carlo, a bootstrap or a random
initialisation is a random variable. Two things must be recorded in the artifact that carries it:

  1. the seed that generated it, so the number can be re-derived without reading the source;
  2. an interval, from the distribution the estimator already produces, so the number is
     falsifiable rather than an anecdote.

Point estimates with no interval and no recorded seed cannot be reproduced or refuted, so they
cannot be cited. This module is the single place that writes both, so individual analysis scripts
do not each invent their own spelling of the same fields.

Two field conventions, used consistently:

  "seed": <int>                                  # the integer passed to numpy.default_rng
  "reproducibility": {seed, python, numpy, sampler, n_posterior_samples, recorded_at, ...}
  "credible_16_84": [low, high]                  # 16th/84th percentile of the posterior samples
  plus "median", "mean", "n_samples" for the distribution it came from

Legacy artifacts (written before 2026-11-11) are grandfathered: an interval cannot be recovered
from a JSON that only ever stored a point estimate. scripts/seed_interval_audit.py inventories
the gap and enforces the rule for artifacts written from CONDUCT_DATE onwards.
"""
from __future__ import annotations

import datetime as _dt
import platform

import numpy as np

#: Artifacts written on or after this date must carry seed + interval
#: (enforced by scripts/seed_interval_audit.py; earlier ones are grandfathered).
CONDUCT_DATE = "2026-11-11"

DEFAULT_QUANTILES = (16.0, 50.0, 84.0)


def _now_iso() -> str:
    return _dt.datetime.now(_dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def library_versions() -> dict:
    """Interpreters and libraries that a stochastic run depends on."""
    return {
        "python": platform.python_version(),
        "numpy": np.__version__,
        "platform": platform.platform(),
    }


def seed_provenance(seed: int, *, sampler: str | None = None,
                    n_samples: int | None = None, sampler_options: dict | None = None,
                    note: str | None = None) -> dict:
    """Build the `reproducibility` block. `seed` is required: a stochastic run without a
    recorded seed is not reproducible, so this refuses to build an empty block."""
    if seed is None:
        raise ValueError("seed is required for a stochastic result")
    block = {
        "seed": int(seed),
        "rng": "numpy.random.default_rng",
        "recorded_at": _now_iso(),
        **library_versions(),
    }
    if sampler is not None:
        block["sampler"] = sampler
    if n_samples is not None:
        block["n_posterior_samples"] = int(n_samples)
    if sampler_options:
        block["sampler_options"] = dict(sampler_options)
    if note:
        block["note"] = note
    return block


def credible_interval(samples, weights=None, quantiles=DEFAULT_QUANTILES) -> dict:
    """Summarise a single-parameter sample as a point plus an earned interval.

    Unweighted -> percentile interval. Weighted (dynesty live-point weights; emcee chains are
    effectively unweighted) -> weighted percentile interval. Nothing here is hand-picked: the
    interval comes from the samples that were actually drawn.

    One parameter per call. A multi-parameter chain goes through posterior_summary, which calls
    this once per column - that way a parameter index can never be confused with a quantile index.
    """
    arr = np.asarray(samples, dtype=float)
    if arr.ndim == 2 and arr.shape[1] == 1:
        arr = arr.ravel()
    if arr.ndim != 1:
        raise ValueError(
            "credible_interval takes a one-parameter sample; use posterior_summary for a chain")
    if arr.size == 0:
        raise ValueError("no samples to summarise")
    if len(quantiles) != 3:
        raise ValueError("quantiles must be (low, median, high), e.g. (16, 50, 84)")
    lo_q, med_q, hi_q = quantiles
    if weights is None:
        lo = float(np.percentile(arr, lo_q))
        med = float(np.percentile(arr, med_q))
        hi = float(np.percentile(arr, hi_q))
        basis = "unweighted"
    else:
        w = np.asarray(weights, dtype=float)
        if w.shape[0] != arr.shape[0]:
            raise ValueError("weights must have one entry per sample")
        if not np.any(w > 0):
            raise ValueError("all sample weights are zero")
        lo, med, hi = _weighted_percentile(arr, w, quantiles)
        basis = "weighted"
    return {
        "median": med,
        "mean": float(np.mean(arr)),
        _interval_key(quantiles): [lo, hi],
        "n_samples": int(arr.shape[0]),
        "basis": f"{basis} percentile {lo_q:g}/{med_q:g}/{hi_q:g}",
    }


def posterior_summary(samples, labels, weights=None, quantiles=DEFAULT_QUANTILES) -> dict:
    """Per-parameter credible intervals for a (n_samples, n_params) chain.

    `labels` must match the parameter order the sampler actually used; a wrong label is a
    data-integrity error, so the chain width is checked rather than assumed.
    """
    chain = np.asarray(samples, dtype=float)
    if chain.ndim != 2:
        raise ValueError("posterior_summary needs a 2-D chain (n_samples, n_params)")
    if len(labels) != chain.shape[1]:
        raise ValueError(
            f"labels ({len(labels)}) do not match chain width ({chain.shape[1]})")
    key = _interval_key(quantiles)
    out = {}
    basis, n_samples = None, None
    for i, name in enumerate(labels):
        one = credible_interval(chain[:, i], weights=weights, quantiles=quantiles)
        out[name] = {"median": one["median"], "mean": one["mean"], key: one[key]}
        basis, n_samples = one["basis"], one["n_samples"]
    out["_meta"] = {"basis": basis, "n_samples": n_samples}
    return out


def interval_from_median_std(median, std) -> list:
    """1-sigma companion interval for an artifact that stored a median and a standard
    deviation but no chain. Derived arithmetic from stored values - NOT a recovered
    credible interval, which is why it is labelled separately by the caller."""
    return [float(median) - float(std), float(median) + float(std)]


def attach_reproducibility(payload: dict, seed: int, *, sampler: str | None = None,
                           n_samples: int | None = None, sampler_options: dict | None = None,
                           note: str | None = None) -> dict:
    """Write the seed block into a result payload. Mutates and returns the same dict so a
    caller cannot accidentally save the payload without it."""
    payload["reproducibility"] = seed_provenance(
        seed, sampler=sampler, n_samples=n_samples,
        sampler_options=sampler_options, note=note)
    payload["seed"] = int(seed)
    return payload


def _interval_key(quantiles) -> str:
    return f"credible_{int(quantiles[0])}_{int(quantiles[-1])}"


def _weighted_percentile(values, weights, quantiles) -> tuple:
    """Percentiles under sample weights (dynesty live-point weights are not equal)."""
    values = np.asarray(values, dtype=float)
    w = np.abs(np.asarray(weights, dtype=float))
    order = np.argsort(values)
    ordered_values = values[order]
    cdf = np.cumsum(w[order]) / np.sum(w)
    out = []
    for q in quantiles:
        pos = int(np.clip(np.searchsorted(cdf, q / 100.0), 0, len(values) - 1))
        out.append(float(ordered_values[pos]))
    return tuple(out)
