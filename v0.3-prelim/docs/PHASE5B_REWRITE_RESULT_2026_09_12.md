# Phase 5b: Channel Likelihood Rewrite (2026-09-12)

**Status:** Phase 5b COMPLETE. The channel likelihoods (dSph Ch2, UFD Ch3, Bullet Ch4, UDG Ch9+Ch10, SPARC helper) now accept a `mediator_class` parameter and use the mediator registry instead of inline power-law linearizations.

**KEY FINDING (per AGENTS.md rule 23, computational-failure hook):** The Phase 5b rewrite **exposed a sign error in the original inline linearization** for `loglike_dm_dominated_udg`. The inline code used `log_sm_eff = log10(σ/m_0) - 0.699 * a` but the correct math is `+0.699 * a` (from `log[σ/m(v)] = log[σ/m_0] + a × log[v_ref/v]`). The Phase 5b rewrite fixes this; existing tests were updated to reflect correct math.

---

## What was changed

### 1. New file: `v0.3-prelim/code/mediator_registry.py` (165 lines)

- `MEDIATOR_FORMS` dictionary with 4 sigma/m(v) functional forms
- `MEDIATOR_NAMES` mapping class_id → human-readable name
- `sigma_m_at_v(sigma_m_0, a, v, mediator_class='power_law')` dispatcher

### 2. Parameterized channels

The following channels now accept `mediator_class: str = "power_law"` parameter:

| Channel | Function | File | Was | Now |
|---|---|---|---|---|
| Ch2 (dSph) | `loglike_dsph_v03` | channels_v03.py | `sigma_m_at_v(...)` | `sigma_m_at_v_mediator(...)` |
| Ch3 (UFD) | `loglike_ufd_v03` | channels_v03.py | `sigma_m_at_v(...)` | `sigma_m_at_v_mediator(...)` |
| Ch4 (Bullet) | `loglike_bullet_v03` | channels_v03.py | `sigma_m_at_v(...)` | `sigma_m_at_v_mediator(...)` |
| Ch4 variant | `loglike_bullet_v03_sensitivity_0p2` | channels_v03.py | `sigma_m_at_v(...)` | `sigma_m_at_v_mediator(...)` |
| Ch8 (SPARC helper) | `sparc_loglike_grid` | channels_v03.py | `sigma_m_at_v(...)` | `sigma_m_at_v_mediator(...)` |
| Ch9 (DM-free UDG) | `loglike_dm_free_udg` | channels_extended.py | inline linearization | mediator registry |
| Ch10 (DM-dom UDG) | `loglike_dm_dominated_udg` | channels_extended.py | inline linearization | mediator registry |

### 3. Backward compatibility

All existing call sites (without `mediator_class`) continue to work — the default is `'power_law'`, which preserves the original behavior. The pre-existing `sigma_m_at_v` function is kept as a wrapper around the registry.

### 4. Bug fix (per AGENTS.md rule 23)

The inline linearization in `loglike_dm_dominated_udg` had a sign error: `log_sm_eff = log10(sigma_m_0) - 0.699 * a`. The correct math for the power-law form is:

```
σ/m(v) = σ/m_0 × (v/v_ref)^(-a)
log[σ/m(v)] = log[σ/m_0] - a × log(v/v_ref) = log[σ/m_0] + a × log(v_ref/v)
```

For v_LSB6 = 20, v_ref = 100: `log(v_ref/v) = log(5) = +0.699`. The original code had `-0.699` (sign error). The Phase 5b rewrite uses the canonical power-law form (sign-correct).

**Impact:** Tests for `a=1` and `a=2` cases had been passing because the sign error happened to give plausible-looking values; the corrected math is now used in the codebase. Test values were updated to reflect correct math.

---

## Test count

| Phase | Tests | Status |
|---|---|---|
| Phase 5b (new) | 29 | All green |
| Pre-existing tests (updated for sign fix) | 3 | All green |
| Total | 296/296 passing | (was 267 before Phase 5b) |

---

## What was NOT changed

### SPARC grid (`sparc_hierarchical_grid.npz`)

The pre-computed grid used by `loglike_sparc_hierarchical` (Ch8 main path) still uses the power-law form internally. Rebuilding the grid for 4 mediator classes requires:

1. Modifying `precompute_sparc_hierarchical.py` to accept mediator_class
2. Regenerating 4 grids (~5-10 min each = ~30-40 min total)
3. Modifying `loglike_sparc_hierarchical` to load the appropriate grid

**Deferred to follow-up commit** because it requires wall-clock time on a long-running precompute job. The main SPARC pipeline still works correctly with `power_law` (default).

### LZ, Fermi, Bullet, Cosmic-web channels

These channels don't use `sigma_m_at_v` directly — they take other inputs (σ_DM-nucleon, σ_v, etc.) that are computed separately. The mediator_class parameter doesn't apply to them in their current form.

---

## What's now possible

With the Phase 5b rewrite, channel likelihoods can now give **different loglike values for different mediator classes**. The Phase 5 structural limitation is **partially lifted** for the channels that use sigma/m_at_v directly:

| Channel | Now discriminates classes? |
|---|---|
| Ch2 (dSph) | YES |
| Ch3 (UFD) | YES |
| Ch4 (Bullet) | YES |
| Ch8 (SPARC main path) | NO (grid is power-law-only) |
| Ch8 (SPARC helper `sparc_loglike_grid`) | YES (but rarely used) |
| Ch9 (DM-free UDG) | YES |
| Ch10 (DM-dom UDG) | YES |

For a full Phase 5 redo that discriminates classes via SPARC, the grid rebuild is needed. That's deferred.

---

## Tracking

- **Files added:**
 - `v0.3-prelim/code/mediator_registry.py` (165 lines)
 - `tests/test_phase5b_rewrite.py` (155 lines, 29 tests)
- **Files modified:**
 - `v0.3-prelim/code/channels_v03.py` (added parameter to 5 functions)
 - `v0.3-prelim/code/channels_extended.py` (added parameter to 2 functions)
 - `tests/test_dm_dominated_udg_channel.py` (3 tests updated for sign fix)
- **Branch:** `wip/cloud-9-relhic` @ `20bfead` (parent; this commit pending)
- **Tests:** 296/296 passing (was 267)
- **Per AGENTS.md rule 27:** Zero unicode superscripts in this doc

---

## Next steps

1. **Re-run Phase 5** with the rewrite — get a physics-grounded Bayes factor (commit pending)
2. **Optionally rebuild SPARC grid** for 4 mediator classes (deferred)
3. **Continue to Phase 6 (gravothermal)** or Phase 7 (LZ event) — both depend on this rewrite being merged first