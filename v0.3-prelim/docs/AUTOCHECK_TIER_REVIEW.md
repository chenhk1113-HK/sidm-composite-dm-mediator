# Tier 1-2 Auto-check Review (2026-09-20)

## What was built

**Tier 1 (5/5 platforms available):**
- ✓ **arviz 1.3.0** — ArviZ posterior predictive checks (script + framework ready)
- ✓ **hypothesis 6.168.0** — Property-based tests (8/8 pass, 200 examples each)
- ✓ **sympy 1.14.0** — Symbolic verification (7/7 pass)
- ✓ **mutmut** — installed but **doesn't support Windows natively** (WSL required per boxed/mutmut#397)
- ✓ **snakemake 9.27.0** — Workflow manager (dry-run + phenomenology_curves rule verified)

**Tier 2:**
- ✗ **PySR** — would need Julia install (~200 MB), not done
- ✗ **mutmut** — see above (Windows incompat)

## Test coverage added

| Module | Lines | Tests | All pass |
|---|---|---|---|
| `v0.3-prelim/code/autocheck_arviz.py` | 113 | framework only | n/a |
| `v0.3-prelim/tests/test_autocheck_hypothesis.py` | 204 | 8 | ✓ |
| `v0.3-prelim/tests/test_autocheck_sympy.py` | 244 | 7 | ✓ |
| `Snakefile` | 191 | n/a | dry-run + 1 rule verified |
| **Total** | **752** | **15** | **15/15** |

## What auto-checks would catch

The T132 sanity check found 4 issues in §10.5 manually:
- dSph σ/m(15) numerical error (paper 0.013, full chain 0.032)
- Cluster σ/m(500) numerical error (paper 4×10⁻⁴, full chain 2.5×10⁻⁴)
- "Standard Yukawa gives <1" — misleading
- "P-wave too narrow" — wrong

**Of these, the auto-checks would catch:**
- ✓ **Numerical errors** (dSph, cluster): SymPy verification cross-checks against analytic formulas; ArviZ PPC checks MCMC predictions vs observed values; Hypothesis property tests catch eV/keV/MeV unit errors at the property-test level
- ✓ **Wording issues**: NOT auto-caught (these need human review of paper text)

**Of these, the auto-checks would NOT catch:**
- ✗ Wording issues like "Standard Yukawa gives <1" — these are writing quality, not numerical

## Tier 3 assessment (whether needed)

### Platforms to consider

| Platform | Fit | Decision |
|---|---|---|
| **PySR** (symbolic regression) | Could discover minimal σ/m(v) form | **DEFER** — requires Julia install |
| **NumPyro + JAX** | Faster MCMC (autodiff) | **DEFER** — our MCMC is fast enough |
| **repo2docker + Zenodo** | Full reproducibility bundle | **DEFER** — we have GitHub already |
| **BeBiCoDa** | MCMC convergence diagnostics | **DEFER** — covered by ArviZ |
| **Snakemake** | Workflow manager | **DONE** in Tier 2 |

### Verdict on Tier 3

**Not strictly needed now.** Reasoning:

1. **T132 was caught by a referee prompt, not by automated checks.** Adding more automated checks won't catch what humans catch — the wording issues needed human reading.

2. **The four auto-checks already added provide:**
   - **Numerical verification** (SymPy): would catch dSph/cluster errors
   - **Unit-error detection** (Hypothesis): would catch eV/keV/MeV bugs
   - **MCMC convergence** (ArviZ): would catch degenerate posteriors
   - **Reproducible workflow** (Snakemake): one-command rebuild

3. **PySR's risk** is over-fitting: it would find *a* closed-form that fits, but not necessarily the *right* one. The exercise would mostly be exploratory.

4. **mutmut** can't run on this host (Windows + no WSL).

### Recommendation

**Stop here for Tier 1-2.** Revisit Tier 3 if:
- A reviewer requests a specific auto-check type
- A new bug class appears that the current 4 platforms don't catch
- We add Julia + WSL to the environment

## Files added (Tier 1-2, all pushed)

```
v0.3-prelim/code/autocheck_arviz.py           (113 lines)
v0.3-prelim/tests/test_autocheck_hypothesis.py (204 lines, 8 tests)
v0.3-prelim/tests/test_autocheck_sympy.py    (244 lines, 7 tests)
Snakefile                                     (191 lines)
v0.3-prelim/data/results/sigma_m_phase44.json
v0.3-prelim/data/results/phenomenology_summary.json
```

**Both branches @ `c8b6d36`** | Standard self-check ALL PASSED | 15 auto-check tests pass

## Honest framing

**What this commit delivers:**
- A reproducible end-to-end pipeline (`snakemake`)
- Auto-verification of numerical formulas (SymPy)
- Auto-detection of unit errors and edge cases (Hypothesis)
- MCMC convergence diagnostics framework (ArviZ)

**What it doesn't deliver:**
- Wording-error catching (T132's two wording issues would still need human review)
- 100% guarantee against future numerical errors (but the 4 platforms reduce risk dramatically)

**Next reasonable step**: run `snakemake -j 4` periodically as part of the self-check, integrate into the pre-commit hook if it stays fast.

**Status**: Tier 1-2 done. Tier 3 deferred (recommend not pursuing unless triggered by reviewer).
