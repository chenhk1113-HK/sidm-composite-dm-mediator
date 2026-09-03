# `consider4.docx` — reviewer input

Source file copied here for traceability:
[`consider4_source.docx`](consider4_source.docx) (13,101 bytes).

## Provenance

- **Uploaded by user:** 2026-09-03
- **Cached at:** `C:\Users\lamkuenai\AppData\Local\hermes\cache\documents\doc_27aeebc78f01_consider4.docx`
- **Extracted text:** 109 paragraphs, ~10.8 KB
- **Key claims:**
  - LZ 2.6σ event cannot be explained by elastic SI; viable explanations are
    inelastic-DM or SD O4 operators
  - The project's "10⁻¹¹¹ cm² elastic SI ~10⁷¹× below LZ" claim is a *red
    herring* — LZ is probing inelastic/SD channels, not elastic SI
  - The reviewer recommends computing composite-DM inelastic σ_DM-nucleon
    + LZ-event forward prediction as the missing piece that elevates the
    project from "compatible with LZ" to "predicts"

## Where the reviewer's points are addressed

| Reviewer claim | Project response |
|---|---|
| "T79 form-factor calc is pending" | ❌ Stale premise — T79 already shipped at commit `6b83904` (2026-09-02). F²_gaussian ≈ 0.93, F²_dipole ≈ 0.87 at LZ energies. |
| "Relic-density + BBN/CMB consistency pending" | ❌ Stale premise — T79 §"Relic-density consistency check" verifies freeze-in regime at ε ~ 10⁻³⁷; T_RH > 10¹⁵ GeV now surfaced in CURRENT.md + LAYMAN_SUMMARY.md as of T86.7j. |
| "10⁷¹× below LZ is a red herring" | ⚠️ Directionally right — but the project's standing posture (T86.7j commit `8bf3507`) is already "elastic SI ~10⁷¹× below LZ; inelastic/SD channels not yet quantified." Not glossing; explicit caveat. |
| "Inelastic/SD cross-section ⏳ Not started" | ⚠️ Partially right — inelastic σ_DM-DM exists (T43, T41_INELASTIC toggle, h4_inelastic_sweep, test_inelastic_wrapper_regression). Inelastic σ_DM-nucleon and SD operator decomposition for composite DM specifically are **genuinely missing**. |
| "Composite-DM SD operator decomposition + LZ forward prediction is the missing piece" | ✅ **Registering as Tier-2 roadmap Item #3** (T86.7k+C, 2026-09-03). See [`V0_6_ROADMAP.md`](../V0_6_ROADMAP.md) Item 3. |

## What T87 will compute (registered but not initiated)

Per `V0_6_ROADMAP.md` Item 3, T87 will compute:

1. **Inelastic σ_DM-nucleon** with composite-mediator coupling (T&S+W 2001
   formalism + KSFR composite sector + standard NREFT O₁ˢ operator).
2. **Forward-predicted LZ event count** at v0.7 MAP (N_events vs 1 observed
   in 2.84 tonne-years).
3. **Verdict** — one of three outcomes:
   - "predicts LZ event" (N_events ≈ 1)
   - "constrains composite-DM parameter space" (N_events >> 1)
   - "does not explain LZ event at v0.7 MAP" (N_events << 1)

Each outcome is a positive scientific result rather than an evasion.

## Honest scope-hygiene notes

- This review was uploaded **after** the T86.7j plausibility audit
  (commit `8bf3507`) was already shipped. The reviewer's "10⁷¹× below LZ"
  framing critique was already addressed in T86.7j — they may have read
  an older snapshot.
- The reviewer correctly identifies the substantive gap (composite-DM
  inelastic σ_DM-nucleon); the project's standing posture is honest about
  this gap (T77-T80 + T86.7j explicitly distinguish elastic SI from
  inelastic/SD).
- T87 is the analysis that would run at LZ ≥3σ per the project's
  pre-registered T78 trigger. Running it now is *premature* but *allowed*
  per user direction (2026-09-03 message: "I want to really close the gap").

— Hermes Agent (2026-09-03)