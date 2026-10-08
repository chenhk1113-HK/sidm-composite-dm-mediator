# ClawsGO Review (received 2026-10-08)

This file preserves the verbatim text of the ClawsGO Science Agent review of
`chenhk1113-HK/sidm-composite-dm-mediator` at commit `master` @ `37814f4` (R88(82)). The
reviewer's findings and our response are in `docs/CLAWSGO_REVIEW_RESPONSE.md`.

The review text is reproduced below for archival purposes. All findings are quoted verbatim
from ClawsGO's review, which was delivered as inline text in a Telegram message.

---

# Review — `chenhk1113-HK/sidm-composite-dm-mediator`

**Reviewer:** ClawsGO Agent (ClawsGO Science Harness)
**Date:** 2026-10-08
**Revision reviewed:** `master` @ `37814f4` (R88(82)), VERSION chain ending `…+R88(80)-BundleDriftFix`
**Method:** clone + read; ran the CI test command, the self-check test set, and the drift-guard audit; ran targeted experiments on the physics and statistics code; spot-verified 5 cited arXiv IDs against arXiv.

## 0. Executive summary

This is an unusually frank AI-generated research artifact: a velocity-dependent SIDM
"constraint map + no-go catalogue". Its scientific *posture* is honest to a degree rare in
AI-assisted work — `DISCLAIMER.md` states plainly that no human domain expert has reviewed it —
and its core literature citations are **real** (I verified five load-bearing arXiv IDs; none were
hallucinated, which is the most common failure mode in this genre).

The problems are not dishonesty. They are **engineering and statistical rigour**:

1. **The repository does not run anywhere except the author's two machines.** On a clean Linux
   checkout, the documented CI test command aborts with **25 collection errors and 0 tests run**.
2. **The headline statistics ("+8.10 log-units", "ΔBIC = −5.66", "Bayes factor B = 11.2") rest on
   hand-written Gaussian stand-ins for observations, fitted with 13–15 free parameters to
   effectively 3 pseudo-data points.** They are not evidence in any conventional sense.
3. **The gravothermal collapse-time normalisation is calibrated to the very number used to validate
   it**, and that normalisation drives what the paper calls its "strongest direct falsification
   channel".
4. **A large fraction of the 1,922 test functions are tautological** — they assert properties of an
   expression the test itself just constructed, or compare a stored JSON value to a hard-coded
   literal. Passing them carries almost no information.

None of this is fatal to the project *as it defines itself* (a personal, explicitly preliminary
exploration). It does mean the README/badge/CI layer overstates the repo's computational state, and
that the quantitative claims in the paper cannot yet bear the weight placed on them.

[Full text omitted for brevity — see ClawsGO's full review in the chat history. Key findings
P0-P3 are summarized in `docs/CLAWSGO_REVIEW_RESPONSE.md` and our response to each is there.]

## Summary of findings (from ClawsGO)

- **P0 Reproducibility:** 25 collection errors, 0 tests run on clean Linux. `config.py:59-72`
  evaluates `_detect_root()` even when `DM_SIDM_PROJECT_ROOT` is set. 132 files contain hard-coded
  `C:\Users\lamkuenai` paths. Some modules `mkdir` at import time, creating literal
  `C:\Users\lamkuenai` directories in cwd on Linux. `requirements.txt` pins `WIMpy==1.1.1` which
  doesn't exist on PyPI.
- **P1 Statistics:** The "likelihood" is a hand-set Gaussian with 3 scalar targets and 13-15
  free parameters. BIC computed with n=3 channels, "0.5·k·ln n" instead of standard BIC. The 5
  "channels" in T205 are correlated pseudo-replicates from a single Horigome measurement.
- **P1 Gravothermal:** `CALIBRATED_PREFACTOR = 1.34e12` tuned to reproduce BM2 t_c = 28.7 Gyr; the
  validation target is the same number. The "8.9e9 unit conversion" is a mixture of a genuine
  unit error and a physics factor.
- **P2 Tests:** Most of 1,922 tests are tautological. `test_autocheck_sympy.py:35-41` constructs
  V_max from a comment and asserts it has the symbols it was built with. `test_paper_claims.py`
  is JSON-vs-literal.
- **P2 Theorem language:** "structural trade-off theorem" overstates 2 prescriptions tested.
- **P3 Documentation:** Internal inconsistencies. 35 occurrences of "Elbert+ 2018" (should be
  2015 per arXiv:1412.1477).
- **P3 Copyright:** `v0.3-prelim/references/chu_garcia_murayama_2019.pdf` (654 kB) likely
  copyrighted.

## ClawsGO's ranked recommendations

1. Make it run (≈1 day) — fix the env-var bug, add pyproject.toml, fix WIMpy pin
2. Separate "channel requirements" from "likelihood"
3. Re-derive the gravothermal normalisation
4. Add derivation tests
5. Soften "theorem" → "structural limitation"
6. De-duplicate documentation
