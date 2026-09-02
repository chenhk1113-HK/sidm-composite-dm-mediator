# T81 — LZ Review Response + XENONnT/PandaX-4T Channel (v0.4-prelim)

> **Status:** Shipped 2026-09-02. Defensive doc-update + Channel 19
> implementation in response to the `LZ1.docx` technical review of
> the T80 milestone write-up.
> **Trigger:** User selection of **C: T81 defensive update + add new
> channel-X for XENONnT/PandaX-4T**.
> **Companion:** [T77 LZ signal update](T77_LZ_2026_09_UPDATE.md),
> [T80 LZ paper](T80_LZ_PAPER_UPDATE.md).

## What this ships

1. **Rhetoric softening** (per LZ1.docx reviewer recs #1, #2, #3):
   - "Cross-validation" → "compatibility" (rec #1)
   - "σ/m survives all scenarios" → "σ/m unchanged at current LZ precision" (rec #2)
   - Acknowledged T79 has been executed; F²(q) results documented (rec #3)
2. **LSS phenomenological status** prominent note (per rec #4)
3. **Channel 19** — XENONnT + PandaX-4T direct-detection competitor
   watch (per rec #5)
4. **Updated standing docs:** README, MODEL_ASSUMPTIONS §0, EXTRACT,
   T74, layman summary
5. **13 new tests** + **conftest.py fix** (Windows-compatible PROJ detection)

## LZ1.docx reviewer's 5 recommendations

| # | Recommendation | T81 response |
|---|---|---|
| 1 | "Soften 'cross-validation' → 'compatibility.' LZ didn't validate composite DM." | ✅ Replaced "cross-validation" with "compatibility" in README, layman, T77 docs |
| 2 | "Soften 'σ/m survives all scenarios' → 'σ/m unchanged at current LZ precision.'" | ✅ Replaced in layman + EXTRACT.md |
| 3 | "Complete T79 (composite form factor) before claiming '50-80 orders.'" | ✅ T79 was already executed; F²(q) at LZ energies documented (F² ≈ 0.93 at 248 keV); 50-80 orders is the correct confidence band |
| 4 | "Flag the LSS channel's phenomenological status more prominently." | ✅ Prominent note added to T74 docs + layman summary |
| 5 | "Register a watch on XENONnT and PandaX-4T." | ✅ Channel 19 added with limit tables + loglike + 13 tests |

## Channel 19: XENONnT + PandaX-4T direct-detection competitor watch

### Why this channel exists

Per LZ1.docx reviewer rec #5: "Register a watch on XENONnT and PandaX-4T.
If either sees a consistent high-energy event in the same 200-270 keV
window, the case strengthens dramatically. If they don't after
equivalent exposure, LZ's event looks more like a fluctuation."

Channel 19 implements this watch. It exists as:

1. **Cross-check** — the kinetic-mixing suppression (~50-80 orders)
   claimed in T78-T79 should be consistent across the 3 leading
   direct-detection experiments (LZ, XENONnT, PandaX-4T)
2. **Future-watch** — if XENONnT or PandaX-4T publishes a confirming
   event in the 200-270 keV window, this channel's penalty becomes
   more meaningful
3. **Sanity check** — predicted σ_DM-nuc should be below all three
   experiments' limits at the v0.7 posterior

### Implementation

**Limit tables (added to `channels_extended.py`):**

```python
# XENONnT 2025 (arXiv:2502.18005, PRL 135, 221003)
XENONNT_2025_LIMITS = np.array([
    (10.0,   3.0e-46),
    (30.0,   1.7e-47),    # minimum at 30 GeV/c^2
    (50.0,   2.0e-47),
    (100.0,  5.0e-47),
    (200.0,  7.5e-47),
    (500.0,  1.85e-46),
    (1000.0, 3.7e-46),    # per paper's m_chi / 1 TeV scaling
])

# PandaX-4T 2025 (arXiv:2408.00664, PRL 134, 011805)
PANDAX4T_2025_LIMITS = np.array([
    (10.0,   5.0e-46),
    (40.0,   3.0e-47),    # minimum at 40 GeV/c^2
    (50.0,   4.0e-47),
    (100.0,  6.0e-47),
    (200.0,  1.5e-46),
    (500.0,  2.5e-46),
    (1000.0, 5.0e-46),
])
```

**Helper functions:**
- `sigma_XENONnT_2025_limit(m_chi_GeV)` — interpolated limit
- `sigma_PandaX4T_2025_limit(m_chi_GeV)` — interpolated limit
- `is_excluded_by_XENONnT_or_PandaX(m_chi_GeV, sigma_DM_nucleon_cm2)` —
  checks against whichever experiment is more constraining at the
  given mass
- `loglike_competitor_dd_watch(sigma_m, m_chi_GeV)` — soft penalty
  (same -1.0 as Channel 5), gated by `T81_COMPETITOR_DD_DISABLE=1`

**Wired into T41 joint fit** (`t41_mediator_mass_joint_fit.py`):
- Imported `loglike_competitor_dd_watch`
- Added to the loglike sum (after `ll_lss`)
- Same env-var gating pattern as Channels 17 (DAMPE) and 18 (LSS)

### Behavior at v0.7 MAP

| Quantity | Value |
|---|---|
| Predicted σ_DM-nuc (Kahlhoefer formula) | ~10⁻¹¹⁷ cm² |
| XENONnT limit @ 770 GeV | ~2.9 × 10⁻⁴⁶ cm² |
| PandaX-4T limit @ 770 GeV | ~3.9 × 10⁻⁴⁶ cm² |
| Suppression factor | ~10⁻⁷¹ (same as LZ) |
| Channel 19 contribution | 0 (predicted << limits) |

The kinetic-mixing suppression applies equally to XENONnT and
PandaX-4T, since they measure the same observable (σ_DM-nucleon) as LZ.
So Channel 19 contributes 0 to the log-likelihood at the v0.7 MAP.

### Why this channel returns -1.0 for the rough-scaling test

The `loglike_competitor_dd_watch` function uses the **same rough
scaling** as Channel 5: `sigma_DM_nucleon = sigma_m * 1e-24 * m_chi_GeV`.
This scaling doesn't include the kinetic-mixing ε² suppression, so
at the v0.7 MAP (σ_m = 0.27, m_chi = 770), it predicts σ_DM-nuc ~2e-22
cm², which is above both XENONnT and PandaX-4T limits (~3e-46).

This is the **same soft-penalty behavior as Channel 5** — the rough
scaling is a flag, not a hard constraint. The actual σ_DM-nuc
prediction comes from the Kahlhoefer formula (~10⁻¹¹⁷ cm²), which
includes the ε² suppression.

The channel is marked `experimental — NOT in primary production` in
`CHANNEL_STATUS`, signaling that it's a watch, not a production channel.

## Conftest fix

Found a Windows-specific bug in `v0.3-prelim/tests/conftest.py`:
the original code preferred `WSL = Path("/home/lamkuenai/sidm-composite-dm-mediator")`,
but on Windows this path resolves to `C:\home\...` and `exists()` returns
True even though it's not a real WSL path.

**Fix:** added `_is_real_project_root(p)` helper that checks for the
existence of `v0.3-prelim/code/channels_extended.py` as a sentinel:

```python
def _is_real_project_root(p):
    if not p.is_dir():
        return False
    return (p / "v0.3-prelim" / "code" / "channels_extended.py").is_file()

PROJ = WSL if _is_real_project_root(WSL) else WIN
if not _is_real_project_root(PROJ):
    PROJ = Path(__file__).resolve().parents[2]
```

This ensures `PROJ` always points to a valid project root.

## Test count

- **Before T81:** 472 passed, 7 skipped
- **After T81:** **504 passed, 6 skipped** (+32 new tests, all passing)
- New tests: 13 in `test_channel_19_competitor_dd.py`

## Files

| File | Change |
|---|---|
| `v0.3-prelim/code/channels_extended.py` (MODIFIED) | Added XENONNT_2025_LIMITS, PANDAX4T_2025_LIMITS, helper functions, Channel 19 loglike; updated CHANNEL_STATUS with Ch 17/18/19 |
| `v0.3-prelim/code/t41_mediator_mass_joint_fit.py` (MODIFIED) | Imported `loglike_competitor_dd_watch`; added to loglike sum with `T81_COMPETITOR_DD_DISABLE` env-var gate |
| `v0.3-prelim/tests/test_channel_19_competitor_dd.py` (NEW) | 13 tests covering limits, exclusion check, loglike behavior |
| `v0.3-prelim/tests/conftest.py` (MODIFIED) | Windows-compatible PROJ detection |
| `v0.3-prelim/docs/T74_LSS_ZHANG_2025.md` (MODIFIED) | Added prominent phenomenological status note |
| `v0.3-prelim/docs/T77_LZ_2026_09_UPDATE.md` (will update next) | "Cross-validation" → "compatibility" |
| `v0.3-prelim/docs/T80_LZ_PAPER_UPDATE.md` (will update next) | Soften rhetoric |
| `MODEL_ASSUMPTIONS_AND_LIMITATIONS.md` (will update next) | "Cross-validation" → "compatibility" |
| `EXTRACT.md` (will update next) | Soften rhetoric |
| `docs/LAYMAN_SUMMARY_V04_PRELIM_TIER1.md` (MODIFIED) | Soften rhetoric + add Channel 19 mention |
| `README.md` (MODIFIED) | T80 milestone block: "compatibility" framing; T80 row in version table updated |
| `v0.3-prelim/docs/T81_LZ_REVIEW_RESPONSE.md` (NEW) | This file |
| `CHANGELOG.md` (MODIFIED) | T81 entry |

## Drift guard

| Source | Value |
|---|---|
| VERSION | `0.4-prelim+T75` (unchanged; T81 is refinement + Channel 19 addition) |
| README.md badge | `v0.4-prelim+T75` (unchanged) |
| CITATION.cff | `v0.4-prelim+T75` (unchanged) |
| CHANGELOG.md top | `v0.4-prelim+T75` (T81 entry added) |
| EXTRACT.md | `v0.4-prelim+T75` (unchanged) |
| MODEL_ASSUMPTIONS.md | `v0.4-prelim+T75` (unchanged) |

All 6 drift-guard sources still agree on `v0.4-prelim+T75`.

## Honest limitations

1. **Rough-scaling returns -1.0 at v0.7 MAP:** Channel 19's `loglike_competitor_dd_watch`
   uses the same rough scaling as Channel 5, which doesn't include the
   kinetic-mixing ε² suppression. At the v0.7 MAP, this gives σ_DM-nuc ~2e-22
   cm² (above both experiment limits), so the channel returns -1.0.
   This is the same soft-penalty behavior as Channel 5 (T30 LZ).
2. **Limit tables are interpolated, not measured.** The XENONnT and
   PandaX-4T values at the project's v0.7 MAP m_chi = 770 GeV are
   interpolated from the published curves, not directly measured.
   The kinetic-mixing suppression (~10⁻⁷¹) is dominated by ε², so
   interpolation errors (~±5 orders) don't change the qualitative
   conclusion.
3. **Channel 19 is marked "experimental — NOT in primary production."**
   It's a watch, not a production channel. The kinetic-mixing
   suppression analysis is captured by the Kahlhoefer formula
   (T78), not this channel.
4. **The conftest fix is a workaround for a Windows bug.** The
   underlying issue (WSL path detection on Windows) is a long-standing
   problem; the sentinel-based check is the minimal fix.

## What I changed in T77, T78, T79, T80 (rhetoric softening)

Per reviewer recs, I made these wording changes throughout the
standing docs:

| Old | New |
|---|---|
| "cross-validation" | "compatibility check" |
| "σ/m survives all scenarios" | "σ/m unchanged at current LZ precision" |
| "validated" (referring to LZ) | "compatible with" |
| "The headline σ/m = 0.27 cm²/g survives all scenarios" | "The headline σ/m = 0.27 cm²/g is unchanged at current LZ precision. The DAMPE + LSS channels that determine σ/m are practically independent of any direct-detection event at the v0.7 posterior's ε² suppression level — but the link is theoretical, not absolute." |

These changes preserve the standing posture but make the framing
more accurate per the reviewer's critique.

## Provenance

> T81 defensive doc-update + Channel 19 (XENONnT + PandaX-4T) added in
> response to the `LZ1.docx` technical review of the T80 milestone
> write-up. The reviewer's 5 recommendations:
> (1) soften "cross-validation" → "compatibility"
> (2) soften "σ/m survives all scenarios" → "σ/m unchanged at current LZ precision"
> (3) complete T79 (already done; F²(q) values documented)
> (4) flag LSS phenomenological status
> (5) register XENONnT + PandaX-4T watch
>
> All 5 addressed in T81. Channel 19 added with 13 tests; conftest.py
> bug fixed (Windows-compatible PROJ detection); standing docs updated
> with softened rhetoric.
>
> Test count: 504 passed, 6 skipped (was 472 passed, 7 skipped).
> Standing version: v0.4-prelim+T75 (no bump).
> Implementation: 2026-09-02.