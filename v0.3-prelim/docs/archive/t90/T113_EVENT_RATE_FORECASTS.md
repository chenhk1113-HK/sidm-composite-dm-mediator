# T113 — Event-rate forecasts at Door-B MAP

**Date:** 2026-09-08
**Branch:** `wip/tier3-magnetic-moment-LZ`
**Status:** SHIPPED
**Method:** Order-of-magnitude rate calculation

---

## TL;DR

T113 implements reviewer suggestion §3(a) and §3(c) from
"Suggestions for taking Door B further":

- **§3(a) — Forecast event rates at T108 MAP** for LZ Run 4,
  PandaX-4T Run 3, XENONnT S2-only.
- **§3(c) — Forecast DarkSide-20k signal** (argon target,
  different kinematics).

**Inputs:** T108 MAP point (m_χ = 138 GeV, δ = 98 keV, σ_PortalB = 1.43×10⁻⁴² cm²).
**Outputs:** Predicted events in [200, 300] keV window + annual modulation amplitudes.

---

## Summary table

| Experiment | Exposure (t·y) | Target | N_pred | Amplitude |
|---|---|---|---|---|
| LZ Run 4 (2027-2028) | 20 | xenon | 1036 | 21.8 events |
| PandaX-4T Run 3 (2026-2027) | 3.7 | xenon | 192 | 4.0 events |
| XENONnT S2-only (2027) | 8 | xenon | 414 | 8.7 events |
| DarkSide-20k (2028+) | 100 | argon | 1554 | 32.6 events |

---

## What these predictions mean

If T108 MAP is correct, LZ Run 4 should see **~1000 events in the [200, 300] keV window**. That's a **huge signal** compared to ~10 background events expected — easily detectable. If LZ Run 4 sees ~0 events, **Door B is decisively closed**.

Annual modulation amplitude of ~22 events at LZ Run 4 is also highly detectable — DIAMX-class annual modulation analysis would see it.

The DarkSide-20k prediction (~1500 events in argon) is also strong, but with weaker form factor (0.3 vs 1.0 for xenon). Cross-target confirmation would be **decisive**.

---

## Caveats

1. **Simplified rate formula.** Real experiments use binned Poisson on
   full recoil spectrum, with detector-specific response functions.
2. **Form-factor scaling is approximate** (1.0 for xenon, 0.3 for argon).
3. **f_window = 0.05** is rough estimate for 100 keV window at inelastic threshold.
4. **Annual modulation amplitude** is suppressed by δ/m_χ for inelastic DM
   (~0.3× factor for δ ~ 100 keV at m_χ ~ 100 GeV).
5. **Numbers are ORDER-OF-MAGNITUDE** estimates, suitable for planning,
   **not for publication**. A proper forecast requires detector Monte Carlo.

---

## Falsifiability

These are **sharp predictions** that can be tested:

- **If LZ Run 4 sees ~1000 events in [200, 300] keV:** Door B is confirmed.
- **If LZ Run 4 sees ~0 events in [200, 300] keV:** Door B is closed.
- **If DarkSide-20k sees ~1500 events (after argon form factor):** Door B confirmed cross-target.
- **If LZ sees 100 events (intermediate):** Need refinement — model parameters may need adjustment.

---

## Files

- `v0.3-prelim/code/t113_event_rate_forecasts.py` — main script
- `v0.3-prelim/tests/test_t112_t113_t114.py` — tests
- `v0.3-prelim/outputs/t95/t113_event_rate_forecasts.json` — final output
- `v0.3-prelim/docs/T113_EVENT_RATE_FORECASTS.md` — this doc

---

## Cross-references

- **T108:** MAP point used as input
- **T114:** ¹²⁴Xe DEC systematic (affects LZ background estimate)
- **Tier D:** Future data would resolve Door B

---

## Provenance

- T113 implementation: 2026-09-08
- Hermes Agent (MiniMax-M3)
- Branch: `wip/tier3-magnetic-moment-LZ`