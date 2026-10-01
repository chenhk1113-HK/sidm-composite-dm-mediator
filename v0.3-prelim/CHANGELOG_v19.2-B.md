# Changelog — v19.2-B §2.7 cycle (R26 → R36, 2026-09-30)

## Summary

Eleven review rounds (R26 → R35) on §2.7 (Ohana+ 2026 c-M consistency), each catching an error the previous introduced. The cycle ended with §2.7 **PARTIALLY CLOSED**: the 0.16 dex consistency check is verified (chain is valid: Ohana+ → DJ19 §2.1 → DK14/DK15); the 0.07/0.085 dex values are reframed as sensitivity results, not literature predictions.

R36 added single-source-of-truth numbers file + drift check. **§2.7 is frozen. No more iteration. Next phase: paper thesis.**

# Changelog — v19.2-B Cloud-9 positioning cycle (R38 → R47, 2026-09-30 to 2026-10-01)

## Summary

Ten review rounds (R38 → R47) attempting to anchor the framework's σ_peak = 174 cm²/g to an external observation, each producing a new claim that did not survive quantitative check. The cycle ended with R47 retracted and the **natural stopping point** declared: the framework as currently constructed is a **catalog of features** that need UV derivation, not a theory that distinguishes itself from ΛCDM or other SIDM models.

The substantive result from this cycle that **survives** the retraction sequence is the **Mace+ 2026 SIDM2v comparison** (R39): under a benchmark of ~50 cm²/g at dwarf velocities (Elbert+ 2015's largest simulation value, not a Cloud-9 requirement), Mace+ falls ~7× short at v = 28 km/s.

## Timeline

### R37 — Simon 2019 observational anchor + 0.085 dex user-exact phrasing
- Added Simon 2019 (arXiv:1901.05465, ARA&A 57, 375) as reference [26a]
- Added anchor sentence: "UFDs are known dark-matter-dominated systems whose kinematics are sensitive to the inner DM profile (Simon 2019, ARA&A 57, 375 [26a])."
- Corrected [26] from incorrect "Mutlu-Pakdil et al. (Aquarius II companion)" to correct "Cerny et al. 2026 (Aquarius IV discovery, arXiv:2608.02601, RNAAS)"
- Refined 0.085 dex wording in §2.7 to user-exact phrasing
- Script version bumped to v19.2-B.12 (R37)
- Status: closed (already in CHANGELOG above)

### R38 (f2604c9) — §3.5a position vs Das+ 2026 (insight1.docx Part 2)
- Added §3.5a paragraph on Das+ 2026 (arXiv:2609.06825) "Inelastic SIDM and LZ 248 keV Event in a Dirac Modular Inverse Seesaw"
- Added reference [50b] for Das+ 2026
- Initial framing: "complementary, not competing" — **REVISED in R40/R41 to MUTUALLY EXCLUSIVE**
- standing_numbers.json _changelog updated
- Status: closed (with later revision)

### R39 (a1b0794) — UNIFIED DM MODEL EXPLORATION (per user "explore as much as feasible")
- **SUBSTANTIVE RESULT that survives:** Mace+ 2026 SIDM2v (arXiv:2506.14898) σ_eff computation at v=28 km/s
- Using Mace+ parameters (σ_H/m_H = 6.89, w_H = 275, σ_x/m_H = 1.125, w_x = 2200, m_H/m_L = 3): maximum σ_eff = **6.89 cm²/g at f_H=1**, ~7× short of Elbert+ 2015's 50 cm²/g benchmark
- For mass-weighted f_H = 0.75: σ_eff = 4.4 cm²/g, ~11× short
- §3 "Position vs unified SIDM models" paragraph added
- Status: closed (this is the surviving substantive result)

### R40 (e77a175) — r33.docx reviewer feedback (4 substantive issues)
- **Issue 1: σ/m ≥ 50 floor source UNANCHORED** — framed as "Cloud-9 requires σ/m ≥ 50"
- **Issue 2: 3.6× vs 7.26× inconsistency** — disambiguated
- **Issue 3: σ_peak "prediction" but is fit** — relabeled "best-fit Gaussian Breit-Wigner"
- **Issue 4: LZ treatment: Das+ and our model MUTUALLY EXCLUSIVE not complementary** — rewrote §3.5a
- **INTRODUCED ERROR (caught in R41):** miscited BLN24 as giving "hydrostatic-equilibrium inference for Cloud-9's σ/m floor"
- Status: closed (with R41 correction)

### R41 (bcfcf80) — Critical citation correction (r34.docx Issue 1)
- **MAJOR CORRECTION:** BLN24 (Benítez-Llambay, Dutta, Fumagalli, Navarro 2024, ApJ 973, 61, arXiv:2406.18643) does NOT report σ/m ≥ 50 cm²/g — the paper reports M₂₀₀ from VLA hydrostatic equilibrium
- The σ/m ≥ 50 value comes from Elbert+ 2015 (MNRAS 453, 29)
- **INTRODUCED ANOTHER ERROR (caught in R41-R42):** cited Elbert+ 2015 as arXiv:1503.06815 — **WRONG**. Actual arXiv ID is arXiv:1412.1477. arXiv:1503.06815 is a carbon nanotube paper.
- §3 "Position vs unified SIDM models" paragraph rewritten with correct attribution
- Script version bumped to v19.2-B.12 (R41)
- Status: closed

### R42 (db4a91e) — r35.docx reviewer feedback (6 issues)
- Re-framed σ/m ≥ 50 as "working benchmark" (Elbert+ 2015 simulation upper end), not "Cloud-9 floor"
- Mace+ comparison at σ_eff(v=28) ≲ 7 cm²/g ~ 7× short of 50 cm²/g benchmark
- Acknowledged: framework's σ_peak = 174 cm²/g satisfies Elbert+ 2015 benchmark by construction
- Status: closed

### R43 (6351e3d) — §10.4d consistency pass
- Added "Authoritative source clarification" to §10.4d: σ/m ≥ 50 "floor" refers to Elbert+ 2015 dwarf-scale simulation upper end
- Status: closed

### R44 (c2dd258) — Insight Part 2 three-option exploration (per user directive 2026-10-01)
- Option 1: σ_peak UV motivation — Yukawa can give amplitude (g_χ ~ 2×10⁻⁵) but NOT position/width
- Option 2: Joint SIDM+LZ signal under v_trans ~ 30-50 km/s — g_portal ≲ 10⁻¹⁰ required
- Option 3: σ_eff sensitivity study — robustly < 10 cm²/g across parameter variations
- Status: closed (NEW SCIENCE per Reviewer 2 ship stance)

### R45 (4fc76ce) — Honest Cloud-9 framing (per proposalcomment.docx reviewer)
- Cloud-9's data do NOT place σ/m ≥ 50 lower bound (it's Elbert+ 2015's largest simulation)
- Cloud-9's diffuse structure places upper bound (collapse would over-thermalize)
- Framework's σ_peak = 174 satisfies Elbert+ 2015 by construction; collapse upper bound unquantified
- Reference [55a] Elbert+ 2015 arXiv ID: fixed from 1503.06815 → 1412.1477
- Status: closed

### R46 (9797119, then retracted ef84ae5) — External anchor attempt (Sánchez Almeida+ 2025)
- Found Sánchez Almeida+ 2025 (arXiv:2510.05682) "Constraints on dark matter models from the stellar cores observed in ultra-faint dwarf galaxies"
- σ/m range 0.3-200 cm²/g from UFD cores
- **ERROR (caught in retraction):** used Eq 10 at r_c = 25,000 pc (Cloud-9's halo virial scale), but formula is calibrated for UFD stellar cores (r_c ~ 20-60 pc). Burkert constant ρ_c × r_c ~ 44 M☉/pc² does NOT hold at 25 kpc. 500× extrapolation outside regime.
- Retracted; framework remains unanchored
- Status: retracted

### R47 (94e22ca, then retracted fa475f8) — Quantitative Cloud-9 "prediction"
- Computed virial velocity σ³ᴰ = √(G M_c / (3 r_c)) = 12.81 km/s
- **ERROR 1 (caught in retraction):** σ³ᴰ does NOT depend on σ_peak — same 12.81 km/s for any NFW halo with M=5×10⁹ M☉, c=4. Counterfactual: change σ_peak from 174 to 50 or 500, virial velocity unchanged. "Prediction" was generic, not framework-specific.
- **ERROR 2:** W₅₀ comparison conflated thermal broadening with DM dispersion. Gas W₅₀ = 12 km/s reflects thermal broadening at T ~ 10⁴ K (c_s ~ 12 km/s per BLN24), not DM velocity dispersion.
- **ERROR 3:** Reintroduced Sánchez Almeida scalings at Cloud-9 scale (same issue as R46 retraction)
- Retracted; framework remains a "catalog of features" without UV derivation
- Status: retracted

### Natural stopping point (per proposalcomment.docx second-pass reviewer recommendation)
- The framework as currently constructed is a catalog of features that need UV derivation, not a theory
- Substantive results from R26–R47 that survive: Mace+ σ_eff comparison (R39), standing_numbers.json infrastructure (R36), §2.7 Ohana+ consistency (R31–R35)
- Next scientific step: EITHER derive σ_peak from UV completion (R44 Option 1: bound-state formation, second mediator, Sommerfeld, specific Yukawa + Breit-Wigner) OR rewrite abstract around constraint map ("a systematic exploration of SIDM parameter space against Cloud-9, UFD cores, dSph, SPARC, and cluster constraints, with a benchmark comparison against Mace+ 2026")
- Per reviewer: "Another retraction of another retraction isn't progress. The next document from this project should either be a UV derivation or an honest abstract."

---

## Process Lessons (per user feedback)

### 1. The 11-bundle loop is the signal (R26–R36, applied to §2.7)

Each iteration caught an error the previous introduced:
- Initial: fabricated 0.06σ
- R26: wrong c-M formula (units bug)
- R27: dropped overclaim
- R28: docstring arithmetic fix
- R29: §2.7 added
- R30: paper-JSON reconciled
- R31: SCATTER CORRECTION (6.18σ → 3.29σ)
- R31-VER: REPRODUCTION → CONSISTENCY CHECK
- R32: wording polish (introduced scatter-attribution error)
- R33: scatter verification (corrected R32, introduced meta-correction error)
- R34: meta-correction (corrected R33, closed citation chain)
- R35: sensitivity-result reframing (terminal)

This is **not convergence**. It's a verification gap upstream: three files (paper, script, JSON) each maintained their own copy of standing numbers. The fix is a single source of truth, implemented in R36 as `v0.3-prelim/data/standing_numbers.json` + `scripts/load_standing_numbers.py` (drift check).

### 2. Over-iteration risk

Eleven adversarial review cycles on one subsection, ending in a number that is footnote-only and a citation that was wrong twice — suggests the review loop was generating work rather than resolving it. The 0.16 dex side is genuinely closed. Take the win and move.

### 3. §2.7 is a robustness check, not a result

The 3.16σ consistency at fiducial under Ohana+'s scatter convention, using synthetic data at that fiducial, is exactly what it is: a self-consistency check. It does not discriminate SIDM from CDM, does not test against real data, and does not need the abstract.

### 4. The R38–R47 Cloud-9 positioning loop (different failure mode)

Per proposalcomment.docx second-pass reviewer: "This is now the seventh document in a row (R40 → R41 → R42 → R46 → R46 retraction → R47 → R47 retraction) where the response to a critique is a new claim that doesn't hold up, followed by a retraction."

The failure mode is different from §2.7:
- §2.7: numbers diverged between paper/JSON/script (verification gap)
- §3: numbers were applied outside their regime of validity (R46), used formulas with wrong units (R47), or compared quantities of different physical types (R47 W₅₀)

The fix is NOT another round of retract-and-retry. The fix is either:
- Derive σ_peak from UV physics (R44 Option 1) — produces a distinguishing prediction
- OR rewrite the abstract around the constraint map (Mace+ comparison + systematic exploration) — produces an honest contribution

### 5. Citation error pattern (R26–R47)

Four citation errors in sequence:
1. Ohana+ R34 — fabricated content (claimed paper said X when it didn't)
2. BLN24 R41 — fabricated content (claimed paper gives σ/m floor; actual paper gives M_200)
3. Elbert+ R41-R42 — wrong identifier (arXiv:1503.06815 is a nanotube paper; actual is arXiv:1412.1477)
4. Sánchez Almeida+ R46 — wrong application (real citation, real equations, used 500× outside regime)

Permanent rules adopted (per user directives):
- R42 rule: "No quantitative citation without verbatim quote from a fetched source"
- R46-retraction rule: "No citation applied outside its regime of validity. Always check paper's parameter ranges and methodology scope before using equations in new regimes."
- Reviewer attribution rule: "Remember the 'first correct citation' was wrong. Use paraphrased reviews ONLY with explicit acknowledgment of paraphrasing."

---

## R38–R47 Detailed Timeline (in addition to the summary above)

### R38 (f2604c9) — §3.5a position vs Das+ 2026
### R39 (a1b0794) — Unified DM model exploration (Mace+ σ_eff survives)
### R40 (e77a175) — r33.docx reviewer feedback
### R41 (bcfcf80) — Critical citation correction
### R42 (db4a91e) — r35.docx reviewer feedback
### R43 (6351e3d) — §10.4d consistency pass
### R44 (c2dd258) — Insight Part 2 three-option exploration
### R45 (4fc76ce) — Honest Cloud-9 framing + Elbert+ 2015 arXiv ID correction
### R46 (9797119, retracted ef84ae5) — External anchor attempt (Sánchez Almeida+ 2025)
### R47 (94e22ca, retracted fa475f8) — Quantitative Cloud-9 "prediction"

---

## Next Phase (pending user direction)

Per the reviewer's final recommendation (2026-10-01):
1. **Stop the R-cycle on Cloud-9 positioning.** R47 retraction is the natural stopping point.
2. **Either derive σ_peak from UV physics** (R44 Option 1) **or rewrite the abstract around the constraint map.**
3. **Build on R39's Mace+ comparison** — that's the one substantive result that survives.
4. **No more bundles responding to reviewer comments about the same subsection.**

The framework's σ_peak = 174 cm²/g is a phenomenological parameter (R33 Issue 3, R37 caveats) that is **unanchored to any external observation**. The framework as currently constructed is a **catalog of features** that need UV derivation. Continuing the R-cycle on Cloud-9 positioning is no longer productive.

**§2.7 is frozen at R35-POLISH. Cloud-9 positioning cycle ended at R47 retraction. Next move: UV derivation OR constraint-map abstract.**

---

## §2.7 Final Status (frozen)

| Component | Status |
|---|---|
| 0.16 dex consistency check (3.16σ at fiducial) | **CLOSED** |
| Citation chain Ohana+ → DJ19 → DK14/DK15 | **CLOSED** (chain is valid) |
| DK14/DK15 identity | **CLOSED** (arXiv:1407.4730 → ApJ 799, 108, 2015) |
| 0.085 dex / 6.18σ | **OPEN** — reframed as sensitivity result, not literature prediction |
| 0.07 dex / 7.51σ | **OPEN** — reframed as sensitivity result (sibling value) |
| **v19.2-B overall** | **PARTIALLY CLOSED** |

## Next Phase (pending user direction)

Per R35 + R36 + user directive 2026-09-30:
1. ~~Stale branch disposition~~ — archived (1)
2. **One-page thesis statement** — deferred per user instruction (sentence to be decided later)
3. ~~Consolidate 11-bundle history~~ — this changelog (now extended through R47)
4. **Decide paper thesis before any new section work** — gravothermal cascade / σ_eff / LZ direct-detection
5. **Defer v19.2-B v3** until thesis is set; v3 is expensive and only worth doing if Cloud-9 tension is central to the thesis

**§2.7 is frozen at R35-POLISH. Single source of truth lives at `v0.3-prelim/data/standing_numbers.json`. Drift check: `python scripts/load_standing_numbers.py`. Next move: paper thesis OR UV derivation (per R47 reviewer final).**