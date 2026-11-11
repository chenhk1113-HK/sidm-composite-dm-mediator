# ReviewResponse-2026-11-11 — claim sync, reproducibility contract, docs drift, CI health

Round type: **review-response / integrity round. No VERSION change, no physics change.**
Trigger: the reviewer document `gemini1.docx` and four follow-up items ("do all 1 to 4").
Tree at start: `wip/v19.2-F-init` @ `f72dd76` (2026-11-11).

---

## Item 1 — paper §10.5 mixed up two different model comparisons

**Defect found.** §10.5 presented a table headed *single-resonance (v40.28) vs multi-resonance
(v40.34)* — i.e. a 4-parameter vs 7-parameter fit — and put the Bayes factor (log B = 2.411) and
the Phase 54 BIC penalty (+3.22) in that table. Those two numbers do not come from that
comparison at all:

| Source artifact | What it actually compares | Value |
|---|---|---|
| `v0.3-prelim/data/results/t205_full_likelihood_published.json` | 15-param multi-resonance (`model_A_multi_resonance`, `n_params: 15`) vs constant σ/m (`model_B_constant`, `n_params: 2`) | logZ −14.285314279516502 vs −16.69669052746084; log B 2.4113762479443395; B 11.14929 |
| `v0.3-prelim/data/results/phase54_joint_comparison.json` | same pair (Phase 54 counts the constant model as 1 parameter) | ΔBIC +3.217868 (3-channel), ΔBIC −1.3912045 (2-channel), Δlog-likelihood +6.081352, BIC penalty 14·ln(n_channels) = 15.2992 |
| `v0.3-prelim/data/results/t177_bayes_factor.json` | same pair with hand-picked σ_unc | logZ −8.123124941758261 ± 0.4244373 vs −11.180100389351648 ± 0.1181528; B 21.2631483 |
| `v0.3-prelim/data/results/t207c_priored_free_emcee.json` | 15-param free-f_H emcee (not a Bayes comparison) | logL total at median 12.27023411814096 |

The 4-vs-7 pair is a **basin-coverage** comparison (v40.28 4 params vs v40.34 7 params), which
carries no Bayes factor and no BIC.

**Fix applied** (`v0.3-prelim/docs/PAPER_V1_DRAFT.md` §10.5, byte-exact rewrite of one span, CRLF
preserved):
* Split into **Comparison A** (evidence: constant σ/m vs 15-param multi-resonance, with logZ for
  both models, log B 2.411, Δlog-likelihood +6.081, ΔBIC +3.22 in the 3-channel variant and
  **−1.391 in the 2-channel variant**) and **Comparison B** (basin coverage, 4 vs 7 parameters,
  explicitly labelled as not a model-evidence comparison).
* **Withdrawn:** the "prior volume in the 7-parameter space is 3.6× larger" explanation. Two
  independent reasons: (i) it names the wrong model pair; (ii) the Occam factor is already inside
  dynesty's log Z — log Z integrates the likelihood over the prior volume, so a model spread over
  14 extra parameters is *penalized* by that integral, not credited by it. The measured direction
  is the opposite of the withdrawn claim: multi-resonance wins 2.411 log-units **despite** the
  larger prior volume.
* Verdict restated to match `README.md` and `v0.3-prelim/docs/REFEREE_RESPONSES.md`, which already
  said "wins the raw joint log-likelihood (+6.08), loses on BIC (+3.22)". The paper was the outlier.

**Registry (`v0.3-prelim/docs/PAPER_STANDING_NUMBERS.md` §4).** Seven rows added/rewritten, each now
naming the artifact and the JSON key path behind it: Bayes log Z (multi-resonance), Bayes log Z
(constant), T177 Bayes B, T177 log Z pair, Phase 54 ΔBIC 2-channel, Phase 54 Δlog-likelihood, and
the Phase 54 BIC penalty row renamed to "(3-channel)" with its scoring rule stated (one channel =
one datum).

**Claim audit (`scripts/audit_claims.py`).** Eight new markdown-mirror entries bind those registry
rows to the same JSON keys the regex mode already checked, so a future edit that changes one side
fails the gate instead of drifting. Both audit modes green after the change (see Verification).

---

## Item 2 — stochastic results recorded neither their seed nor their interval

**Measured, before any change** (`scripts/seed_interval_audit.py` over
`v0.3-prelim/data/results/*.json`):

| quantity | count |
|---|---|
| artifacts scanned | 487 |
| stochastic (sampler / Monte Carlo / N-body output) | 203 |
| record a seed | 2 |
| record an interval (credible / percentile / limit) | 136 |
| record **both** | 0 |
| legacy gap (dated before 2026-11-11) | 203 |
| unparseable artifacts | 1 (disclosed) |

**What was added.**
* `v0.3-prelim/code/repro_contract.py` — one place that writes the two fields:
  `"seed"` plus a `"reproducibility"` block (seed, numpy/python/platform, sampler, n samples), and
  `credible_16_84` computed from the samples that were actually drawn. `posterior_summary` refuses
  a label list whose length does not match the chain width.
* Producers wired: `T205_full_likelihood_published.py` (both nested samplers now take
  `rstate=np.random.default_rng(SEED)`, output carries `posterior_credible_16_84` for all 17
  sampled parameters and a reproducibility block) and `T207c_priored_free_emcee.py` (the existing
  `default_rng(42)` became a recorded `SEED`; intervals were already stored as q16/q84).
* `scripts/seed_interval_audit.py` — inventory plus a **forward rule**: any stochastic artifact
  dated on or after 2026-11-11 must carry seed + interval, or the audit exits 1. Legacy artifacts
  are reported, not rewritten.
* `v0.3-prelim/tests/test_repro_contract.py` — 10 tests, including the empirical proof that the
  seeding is real: the same seed reproduces `logz` and the whole posterior sample set bit-for-bit,
  and a different seed changes them. A seeded sampler is only worth recording if it is the thing
  that decides the number.

**Dating trap found on the way.** Filesystem mtime is not evidence of a run date here: a `git
checkout` had refreshed nine artifacts' mtimes to 2026-11-11 while their contents were unchanged
since 2026-11-05/06. The audit therefore reads the date from (1) a date field inside the artifact
(84 cases), (2) the last git commit touching it (399 cases), (3) mtime only as a labelled last
resort (3 cases).

**Open finding.** `v0.3-prelim/data/results/amuse_focused_rerun_with_sashimi_2026_09_12.json` is
truncated at 203,917 bytes, mid-value, ending at `"core_collapsed":` — the writer cut the AMUSE
benchmark off. It is disclosed in the audit's `CORRUPT_ALLOWLIST` and printed on every run rather
than hidden. Either re-run the benchmark or archive the fragment; it is currently unreadable, so
nothing in it can be cited.

**Not done (deliberate).** The published T205 / T207c / T177 artifacts were **not** regenerated.
Their stored logZ values came from unseeded runs, and re-running them would move headline numbers
that ~30 documents quote. The contract applies to runs from 2026-11-11 onward; regenerating the
published pair is an owner decision, listed below.

---

## Item 3 — README told the reader to use Python 3.11

`README.md` Quick start said `python3.11 -m venv .venv` while `self_check.yml` pins `3.12` and the
working venv used for record rounds (`.venv-sidm-bench`) is 3.12.13. Fixed to `python3.12`, with
the CI-parity line (`pip install -r requirements-ci.txt`) added next to the full-stack line.

---

## Item 4 — CI trigger coverage: measured, healthy, and now guarded

The 2026-11-03 note that trigger coverage was absent on `wip/v19.2-F-init` is **no longer true**.
Measured 2026-11-11 against GitHub's API (unauthenticated, HTTP 200):

* workflow `Self-check` (`.github/workflows/self_check.yml`) — state **active**;
* repository run count 842; the 15 most recent runs are all `Self-check`, branch
  `wip/v19.2-F-init`, event `push`, status `completed`, conclusion **success** (2026-11-08 → 2026-11-10);
* triggers cover `master` (the remote default, `origin/HEAD -> origin/master`), `wip/cloud-9-relhic`
  and `wip/v19.2-F-init` for both `push` and `pull_request`, plus `workflow_dispatch`;
* `ci.yml` remains disabled by owner decision **D12** (renamed to `ci.yml.disabled`).

`v0.3-prelim/tests/test_ci_workflow_wiring.py` (7 checks, all passing) keeps the three drift
classes that produced this problem from silently returning: trigger coverage of the branch that
carries the workflow, README-vs-CI Python agreement, and CI installing the pinned
`requirements-ci.txt` rather than bare `pytest`. The guard is **stdlib-only on purpose**:
`requirements-ci.txt` has no PyYAML, so a guard written with `pytest.importorskip("yaml")` would
skip in CI and assert nothing.

The workflow gained a **`Run reproducibility + CI wiring guards (Layer G)`** step running those
two test files plus `scripts/seed_interval_audit.py`, so a new artifact published without a seed
or an interval fails CI rather than sitting in the inventory.

---

## Verification

| check | result |
|---|---|
| `scripts/audit_claims.py` (both regex and markdown-mirror modes) | exit 0 — PASS |
| `audit_markdown_tables.py`, `audit_section_refs.py`, `audit_doc_anchors.py`, `audit_stale_strings.py`, `drift_guard.py`, `load_standing_numbers.py` | exit 0 each |
| `audit_glyph_coverage.py` | PASS under the interpreter that has pdfplumber (the project venv does not) |
| `sidm_validate_paper_section("10.5")` | ok, 64 numeric claims |
| `sidm_compare_paper_to_json("10.5")` | ok, 17/30 JSON values found in-section (informational value-search, not a gate layer) |
| `pytest v0.3-prelim/tests/test_repro_contract.py` | 10 passed |
| `pytest v0.3-prelim/tests/test_ci_workflow_wiring.py` | 6 passed |
| `python -m py_compile` on every file written | clean |
| `scripts/seed_interval_audit.py` | exit 0, forward-rule violations 0, 1 disclosed corrupt artifact |

---

## What could still be wrong

1. **The producer patches are compile-and-same-shape verified, not re-run.** T205/T207c were not
   executed end-to-end, because a re-run changes published numbers. The seeded-sampler call shape
   (`dynesty 3.1.0`, `nlive`, `rstate=np.random.default_rng(SEED)`, `results.samples`) was verified
   by execution in the test, on a toy likelihood, in the same venv.
2. **203 stochastic artifacts keep their legacy gap.** An interval cannot be recovered from a JSON
   that only ever stored a point estimate; only the chain on disk could supply it.
3. **The truncated AMUSE artifact is still on disk** and still unparseable.
4. **`audit_glyph_coverage.py` needs an interpreter with pdfplumber** (present in `C:\Python314`,
   absent from `.venv-sidm-bench`); CI does not run it.
5. Owner decision open: **re-run T205 (and optionally T177/T207c) under the recorded seeds** so the
   headline Bayes numbers become reproducible artifacts with intervals, and cascade any change
   through the registry, paper §10.5 and the README. This round deliberately did not do that.
