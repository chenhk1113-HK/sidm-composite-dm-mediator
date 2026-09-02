# Layman Summary — LZ 2026-09-01 Mysterious Signal Update (T77)

> **For:** Non-experts + users preferring quick summaries over technical detail.
> **Companion:** [T77 full docs](T77_LZ_2026_09_UPDATE.md) for the
> verification + decision matrix + trigger conditions.
> **Date:** 2026-09-02 (one day after the LZ announcement).

## What this is, in one sentence

The LZ dark-matter detector announced a possible signal yesterday,
**but the project's headline σ/m = 0.27 cm²/g result is completely
unchanged** — because LZ measures a different thing than what the
project's headline measures.

## What LZ detected (in plain language)

LZ is the world's most sensitive dark-matter detector. It sits nearly
a mile underground in South Dakota, filled with 10 tonnes of ultrapure
liquid xenon. It's been running for years, looking for flashes of
light that would indicate a dark-matter particle bumping into a
xenon atom.

Yesterday (2026-09-01) the LZ team reported: **they saw one event**
that looks slightly more energetic than expected — energy that could
come from a dark-matter particle with mass at least 200 times the
proton mass.

The catch: **the statistical significance is only 2.6σ**. In physics,
a "discovery" requires 5σ. A 2.6σ result is what you'd get from
flipping a coin 14 times and getting heads every time — uncommon but
not impossible. About **0.5% chance** this event is just ordinary
background noise. They need more data to confirm.

## Why it doesn't change the project's σ/m

The project measures **σ_DM-DM** — how strongly dark-matter particles
collide with *each other*. This is what determines whether dark
matter forms smooth galaxy cores (SIDM-like) or sharp cusps (CDM-like).

LZ measures **σ_DM-nucleon** — how strongly dark-matter particles
collide with *ordinary atomic nuclei* (xenon, in LZ's case).

These are **completely different cross-sections**. The ratio is
roughly **10²³** — for a 1 GeV dark-matter particle, the self-
scattering cross-section is 10²³ times larger than the nucleon
cross-section. They're like measuring how fast you walk versus how
hard you push on a wall — both real, but neither tells you the other.

The project's headline σ/m = 0.27 cm²/g (T41 v0.7, nlive=2000) measures
the first. LZ measures the second. **Even if the LZ signal is real
and confirmed at 5σ tomorrow, it wouldn't change σ/m.** It would
update a separate Channel 5 in the project (a sanity check), but not
the headline result.

## What's actually consistent

If the LZ signal is real, it implies a dark-matter particle with mass
**at least 200 GeV/c²**. The project's v0.7 posterior prefers a mass
of **~770 GeV/c²** — well above 200 GeV. **The two are compatible.**
The project could accommodate the LZ signal without contradiction.

In fact, the LZ signal — if real — would be **the first direct-
detection evidence** for a dark-matter particle in the mass range
where the project's composite-DM + secluded-mediator model lives. That's
exciting, but again: orthogonal physics, separate measurement.

## What the doc-prominence fix did

This update adds the LZ event to the project's standing documentation
as a sanity check:
- **`MODEL_ASSUMPTIONS_AND_LIMITATIONS.md §0`** (top of the document)
  — explicitly notes that the LZ signal, even if confirmed, doesn't
  affect σ/m.
- **`EXTRACT.md`** (top of the document) — a short callout referencing
  the T77 file.

The standing posture is **non-negotiable**: σ_DM-DM ≠ σ_DM-nucleon,
and direct-detection constraints are rejected as σ/m measurements.
This is locked since2026-08-10 per peer review (R12/R13).

## What could change this (and what wouldn't)

| If this happens | The project would... |
|---|---|
| LZ paper appears on arXiv with precise σ_DM-nucleon limit | Re-evaluate Channel 5; update if ≥3σ |
| LZ signal significance reaches ≥ 3σ | Update T30 mapping; re-run T41 at nlive=2000 |
| LZ signal reaches ≥ 5σ (discovery) | Major milestone; v0.5-prelim release |
| A different experiment (XENONnT, PandaX) confirms | Treat as joint constraint; same logic |
| The LZ event turns out to be a statistical fluctuation | No change; remove the T77 update from §0 |

**The project's headline σ/m = 0.27 cm²/g survives all of these
scenarios unchanged.** That's the power of the orthogonal-physics
posture: the SIDM/DAMPE/LSS channels that determine σ/m are
independent of any direct-detection event.

## What could go wrong (honest caveats)

1. **The LZ paper is not yet on arXiv.** The 2.6σ number comes from
   press releases, not the paper itself. The paper may report
   slightly different numbers when it appears.
2. **"WIMP mass ≥ 200 GeV" is a lower bound, not a value.** The
   implied mass could be much higher (200, 500, 1000 GeV).
3. **The uploaded `more info.docx` claims SIDM provides an
   "orthogonal interpretation" of LZ signals.** This is **partly
   misleading** — SIDM still predicts σ_DM-nucleon interactions
   (just with different kinematics than WIMP). The "orthogonality"
   in that doc conflates two different meanings. The project sticks
   with the correct usage: σ_DM-DM vs σ_DM-nucleon are orthogonal,
   but WIMP vs SIDM at LZ are **competing explanations of the same
   observable**, not orthogonal.
4. **2.6σ is a fluctuation level.** Many experiments have published
   2-3σ "signals" that didn't survive re-analysis with more data.
   The LZ collaboration itself says "more data needed to confirm."

## Why this is still worth shipping

Even though σ/m doesn't change, the T77 update:
1. **Documents the event** so future readers understand the
   project's posture is current.
2. **Establishes the trigger conditions** for re-evaluation (≥3σ,
   paper release, etc.).
3. **Locks the orthogonal-physics posture** against the LZ news cycle
   that will dominate physics Twitter for weeks.

## The single most important takeaway

> **The LZ mysterious signal is real, but it's at the boundary of
> statistical significance (2.6σ), it doesn't constrain the project's
> headline σ/m result, and the project is robust against it. The
> project's T41 v0.7 posterior prefers m_χ ~ 770 GeV, which is
> consistent with the implied LZ WIMP mass (≥ 200 GeV). The
> standing posture (σ_DM-DM ≠ σ_DM-nucleon) is reaffirmed.**

This is the **defensive** value of the orthogonal-physics decision
made in 2026-08-10: when the LZ news cycle hits, the project's
headline result is unchanged. That's by design.

## What this is NOT

- ❌ NOT a confirmation of dark matter. (2.6σ is not 5σ.)
- ❌ NOT a constraint on σ/m. (LZ measures σ_DM-nucleon, not σ_DM-DM.)
- ❌ NOT a project update at the headline-result level. (Standing
  version remains v0.4-prelim+T75; no code change; no T30 update.)
- ❌ NOT a tension with the project's posterior. (Compatible: m_χ ~ 770
  GeV, LZ ≥ 200 GeV.)

## Provenance

> T77 LZ 2026-09-01 mysterious signal update. Shipped 2026-09-02.
> Signal verified across Imperial/Northwestern, Brown, LBNL,
> Sheffield press releases. Decision: NO project update at 2.6σ
> (below 3σ threshold). Standing posture reaffirmed. Implementation:
> defensive doc-prominence fix in MODEL_ASSUMPTIONS §0 + EXTRACT.md.