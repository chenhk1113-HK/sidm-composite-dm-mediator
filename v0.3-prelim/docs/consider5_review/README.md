# Consider5.docx — R15 Reviewer Round

**Source document:** `consider5_source.docx` (5,266 bytes, 35 lines, 733 words).
Extracted 2026-09-03 from `C:/Users/lamkuenai/AppData/Local/hermes/cache/documents/doc_fac0d8163730_cosider5.docx`.

## Reviewer ask

"Consider if any datasets are useful for our project." The reviewer proposes
**6 datasets** spanning **4 orders of magnitude in velocity** (10-1000 km/s)
relevant to the SIDM joint-fit pipeline:

| # | Dataset | Velocity | Type |
|---|---|---|---|
| P1 | JWST Deep Cluster Strong Lensing (AS1063, Abell 2744, SMACS 0723) | ~1000 km/s | strong lensing core sizes |
| P2 | Euclid EDR/DR1 Cluster Catalogs | ~1000 km/s | cluster density profiles, BCG offsets |
| P3 | Euclid Strong Lensing Substructure Sample | ~100-200 km/s | subhalo mass function dN/dM |
| P4 | JWST Resolved Stellar Kinematics of Local Group UFDs | ~10-30 km/s | central density / core-cusp |
| P5 | eROSITA All-Sky Survey (eRASS Group/Cluster Catalogs) | ~300-800 km/s | X-ray cluster catalog |
| P6 | XRISM (Resolve Microcalorimeter) | all scales | ICM spectroscopy + line flux |

## Audit outcome (R15)

| Proposal | Verdict |
|---|---|
| P1 JWST cluster lensing | **Marginal** — Channel 8 (cluster upper limit) covers |
| P2 Euclid cluster profiles | **Marginal** — Channels 3+8 cover |
| P3 Euclid subhalo dN/dM | **Genuinely useful** — quantitative upgrade over Channel 6 |
| P4 JWST UFD kinematics | **Genuinely useful** — adds density profiles vs upper limits |
| P5 eROSITA X-ray clusters | **Genuinely useful** — fills velocity gap |
| P6 XRISM ICM spectra | **Partially useful** — (a) baryonic vs SIDM useful; (b) mediator decay line NULL at v0.7 ε |

**Recommended acquisition order** (if user wants to act):
1. P5 (eROSITA eRASS1) — lowest cost; immediate velocity-gap fill
2. P6a (XRISM Perseus ICM velocity) — already published (arXiv:2510.12782)
3. P3 (Euclid Q1 subhalo) — fresh data; needs analysis pipeline
4. P4 (JWST UFD kinematics) — pipeline not yet mature
5. P1+P2 — deferred; Channels 3+8 cover

**Numerical check on P6b:** τ_φ = 1/(α ε² m_φ) ≈ **1.6×10⁵² s ≈ 5×10⁴⁴ yr ≈ 3.6×10³⁴ × Hubble time**.
Completely undetectable by XRISM at v0.7 ε.

**Verdict:** Cosider5 reviewer's framing of the velocity gap (300-800 km/s) is correct
but the eROSITA mission status (German contribution halted Feb 2024) means future data
is uncertain. The XRISM mediator-decay proposal is asymptotically null at v0.7 ε.
The AS1063 finding IS real (Diego+ 2026, arXiv:2602.15940) but the paper itself
flags fuzzy-DM as an alternative explanation — not a clean SIDM-only signal.

## Audit provenance

- Reviewer source: `consider5_source.docx` (preserved here for traceability)
- External fact-checks: arXiv:2602.15940 (AS1063), arXiv:2510.12782 (XRISM Perseus),
  A&A 701, A283 (eROSITA eRASS1)
- Audit performed: 2026-09-03 (per AGENTS.md rule 21 — thorough reading + ground-truth
  verification before commenting)
- Standing posture preserved: v0.4-prelim+T75, log Z = −163.29 ± 0.085, σ/m = 0.27 cm²/g.
  No posterior re-run; no new channels shipped (R15 is doc-only audit).
