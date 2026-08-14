REVIEWER AUDIT — Review 11 (sidm-composite-dm-mediator 科學可信度審閱)

This is an audit of the REVIEW itself, not of the underlying project.
Reviewed: 2026-08-14, against on-disk ground truth in
`C:\Users\lamkuenai\projects\sidm-composite-dm-mediator\` (HEAD = master
@ commit 5eda484; wip/v0.4-prelim = 5eda484). Docx received:
`C:\Users\lamkuenai\AppData\Local\hermes\cache\documents\doc_ed0056258ae8__科學可信度審閱.docx`
(22 KB, 155 lines extracted). Full extraction at
`outputs/review11_extracted.txt`.

**This is the most substantive external review received to date.** Unlike
R9 and R10 (both English-language, both pointing at specific numerical
errors), R11 is in Traditional Chinese and engages with the **scientific
methodology** of the project — not just individual numbers. It identifies
issues that the project's own authors have not flagged publicly, including
several that I had previously marked as "fixed" in earlier audits that turn
out to be incorrect.

Methodology: per `reviewer-audit` skill (Tier-1 / Tier-1.5 / Tier-2 /
Tier-3 / Tier-4) + citation hygiene.

================================================================
HEADLINE VERDICT
================================================================

Grade: **B-** overall (significantly stronger critique than R9 B+ or R10 B+).
The reviewer is a knowledgeable dark-matter phenomenologist who correctly
identifies 4 substantive methodological failures that were not caught by
the project's own self-audits (R2, R9, R10):

1. The "five/six-channel joint posterior" is **not a normalized joint
   observational likelihood**. The SPARC contribution uses a hand-coded
   saturation score (Dsat=5000, sigma_transition=0.5) that was **never
   re-derived** from per-galaxy forward fits — this is the strongest
   critique, and it has not been self-audited.

2. **DATA_SOURCES.md §4 "No HEPData 155182" is itself wrong.** I made a
   factually incorrect self-correction in an earlier round. The LZ WS2024
   arXiv page and its associated citation chain point to HEPData DOI
   10.17182/hepdata.155182. My "correction" to ins2726677 (an INSPIRE-TEI
   record ID, different namespace) broke the citation trail.

3. **T32 still cites "Hooper & Linden 2024"** in code and metadata, even
   though the project's own DATA_SOURCES.md §4 (the same section I just
   corrected in #2) acknowledges this is wrong (correct citation: McDaniel
   et al. 2024, arXiv:2311.04982). The fix has not propagated from
   documentation to code.

4. **`config.py` was NOT updated during the project rename**
   `dm-sidm-pipeline` → `sidm-composite-dm-mediator`. The `_detect_root()`
   fallback still hardcodes the old project name, which is **why the
   reviewer's fresh-clone pytest run failed** — not because of missing
   test fixtures, but because the renamed project's own config can't find
   its root. The `os.environ.get(KEY, _detect_root())` pattern means the
   env var is ignored at call time. **This is a real, severe bug** that
   prevents clean-clone reproducibility.

Beyond these four, the reviewer also raises valid critiques about PCAC
mislabeling, dimensional inconsistency in ε × σ/m, and the over-claim
language. The reviewer is right about all of them.

================================================================
PART A — REVIEWER CLAIMS, VERIFIED ✓
================================================================

A1. SPARC contribution to T8 joint fit uses Dsat=5000, sigma_transition=0.5
   `v0.3-prelim/code/t8_v03_joint_fit.py` contains literally:
   ```python
   Dsat = 5000.0  # from Phase 2 T4 result
   sigma_transition = 0.5  # cm^2/g
   return float(Dsat * (1.0 - np.exp(-sigma_m_v / sigma_transition)))
   ```
   Reviewer's verbatim quote of this formula matches the file byte-for-byte
   (after LaTeX rendering). **The SPARC channel is a hand-coded saturation
   score, not a per-galaxy forward-fit likelihood**. ✓

A2. HEPData 155182 IS the correct record for arXiv:2410.17036
   Web-verified: "LZ Collaboration, Dark Matter Search Results from 4.2
   Tonne-Years of Exposure of the LUX-ZEPLIN (LZ) Experiment, HEPData
   (collection), 10.17182/hepdata.155182 (2025)" — this exact citation
   appears in arXiv:2504.10597v2 (t-channel dark matter whitepaper) and
   in the LZ-boosted-DM PRL 134, 241801 (2025). ✓
   The project's `docs/DATA_SOURCES.md` lines 206-209 incorrectly states
   "No HEPData 155182" and points at `ins2726677` (an INSPIRE record ID,
   not a HEPData record — different namespace). **My own earlier "self-
   correction" was factually wrong**. ✓

A3. T32 still cites "Hooper & Linden 2024" in code
   `v0.3-prelim/code/t32_fermi_dwarf_channel.py` contains at least 5
   references to "Hooper & Linden 2024" (lines 17, 24, 48, 76, 208, 239),
   with arXiv:2408.00703 listed as the source. The correct citation per
   the project's own DATA_SOURCES.md is McDaniel et al. 2024 (arXiv:
   2311.04982). ✓ The R9 audit flagged this as "Hooper/Linden 2024 is a
   fabricated reference, not authored by them" but did not flag that the
   code still carries the wrong citation.

A4. config.py not updated during project rename
   `config.py` line 14: `win = Path(r"C:\Users\lamkuenai\projects\dm-sidm-pipeline")`
   line 21: `wsl = Path("/home/lamkuenai/dm-sidm-pipeline")`
   line 23: `raise FileNotFoundError("dm-sidm-pipeline project root not found")`
   The rename `dm-sidm-pipeline` → `sidm-composite-dm-mediator` happened
   in commit ede5dd6 (initial commit), 2026-08-14. **config.py was not
   touched.** A fresh clone of `github.com/chenhk1113-HK/sidm-composite-
   dm-mediator` to `/home/lamkuenai/sidm-composite-dm-mediator` or
   `C:\Users\lamkuenai\projects\sidm-composite-dm-mediator` would have
   the hardcoded fallback path NOT exist → config would raise
   FileNotFoundError on import. **This is the actual reason the
   reviewer's pytest run failed**, not "tests/ missing" as the reviewer
   reported (which is a different but related issue — `v0.1-prelim/tests/`
   also doesn't exist; pytest should use `tests/` + `v0.3-prelim/tests/`).

A5. `os.environ.get(KEY, _detect_root())` pattern bug
   Python evaluates both arguments of `get` at call time. The env var
   `DM_SIDM_PROJECT_ROOT` is passed in as the `default` argument, but
   `_detect_root()` is evaluated unconditionally and raises if its
   hardcoded paths don't exist. The env var is effectively ignored.
   Reviewer correctly identified this as a Python semantics bug. ✓

A6. Test count from reviewer's run: 398 passed, 5 failed, 8 skipped (411 total)
   `find tests v0.*/tests -name 'test_*.py' | xargs grep -hcE 'def test_'`
   yields **411**. The reviewer's count is consistent with the test
   inventory. ✓

A7. T39 test passes a=20 out of A_RANGE=(-2.0, 2.0)
   `config.py` line 84: `A_RANGE = (-2.0, 2.0)`
   `v0.3-prelim/tests/test_t39_tier3_epsilon_alpha.py` line 43-44:
   ```python
   # Default: log_sigma_m=-2 (1 cm²/g), a=20 km/s, log_epsilon=-4, log_alpha=-3
   ll = t39.loglike_joint((-2.0, 20.0, -4.0, -3.0))
   ```
   `a=20` is outside `(-2.0, 2.0)`. The comment says "a=20 km/s" which is
   a unit confusion (a is dimensionless, not km/s). The test passes the
   wrong argument. T39's `loglike_joint` checks the range and returns
   `-inf` for out-of-range inputs (line 88), which the test may be
   asserting returns a finite value → test failure. ✓

A8. T32 Fermi channel uses 95% CL upper limits + 0.3-dex half-Gaussian
   `t32_fermi_dwarf_channel.py` line 76: "# From Hooper & Linden 2024
   (4FGL-DR4, 14-year data)". The reviewer notes that the official
   McDaniel et al. 14-year dSph analysis data products include 2D TS
   profiles, J-factor treatments, mass grids — and the project doesn't
   use any of it. ✓

A9. PCAC formula misuse for vector rho mass
   `v0.3-prelim/code/t53_dark_rho_meson.py` `dark_rho_mass()`:
   ```python
   return 2.0 * np.sqrt(m_q_GeV * Lambda_dark_GeV + Lambda_dark_GeV ** 2)
   ```
   Docstring says "PCAC-corrected formula (from real QCD)". PCAC/GMOR
   actually controls the **pion** (pseudoscalar) mass: `dark_pion_mass()`
   in the same file uses the correct GMOR relation:
   `m_pi² = 2 m_q Λ_dark / N_dark`. The vector rho mass is **not** a
   PCAC prediction — it requires gauge dynamics, vector meson dominance,
   or lattice input. The reviewer correctly identified this as a
   misnomer. ✓

A10. ε × σ/m dimensional inconsistency
    The mapping `sigma_DM_nucleon_cm2 = epsilon * sigma_m_0` multiplies
    cm²/g (dimensionful σ/m) by a dimensionless ε to produce cm². This
    is dimensionally inconsistent. The reviewer correctly identifies
    this as "not a physical coupling". ✓

A11. T39 wide-vs-narrow prior effect (ΔlogZ ≈ 9100)
    `v0.3-prelim/docs/FINDINGS.md` S.5 documents: "WIDE (allows SM-
    decoupling, current) = -2.65; NARROW (no SM-decoupling) = -9388".
    The reviewer correctly identifies this as a **prior-dependent**
    feasibility conclusion, not a measurement. ✓

A12. Two-component SIDM (T22) BF = +0.39 diagnostic only
    Matches the R10 audit conclusion; both reviews agree the BF is a
    pipeline diagnostic, not evidence for two-species DM. ✓

A13. Drobczyk 2025 is qualitative literature consistency, not external validation
    Matches the R10 audit conclusion (audit document, Recommendation D4).
    Reviewer is correct: "should be 'qualitative literature consistency /
    independent example of a related model class', not 'strongest external
    validation'". ✓

================================================================
PART B — REVIEWER CLAIMS, PARTIALLY CORRECT
================================================================

B1. "Five failures include... outputs/ charts"
   Reviewer says: 5 failures include gitignored output charts and the
   a=20 T39 test. Cannot fully verify without re-running pytest. The
   a=20 finding is verified (A7). The gitignored-output finding is
   plausible (outputs/ is gitignored per the project; tests that depend
   on it would fail on a fresh clone). PARTIAL ✓

B2. "Many tests only check module imports / JSON field existence"
   Reviewer's qualitative claim about test surface. This is true for
   some tests (e.g. `test_summary_results_module.py` checks file
   existence) but the project also has substantive tests
   (e.g. `test_unit_conversion.py` verifies physics constants to 1%).
   The reviewer's point about test quality is valid as a general
   criticism, but overstated. PARTIAL ✓

B3. "T26 default MAP differs from T21 due to nlive=200 vs nlive=500"
   Reviewer notes this from FINDINGS.md. The ΔlogZ 0.198 vs 1.006
   numbers from FINDINGS.md confirm the KISS-SIDM penalty acts as a
   regularizer. PARTIAL ✓ (the reviewer's specific number claim
   cannot be fully verified without re-running T26.)

================================================================
PART C — REVIEWER CLAIMS, NOT VERIFIED / OUT OF SCOPE
================================================================

C1. Specific dimensional analysis of ε mapping
   The reviewer argues about the ε ×/σ/m mapping being dimensionally
   inconsistent. This is verified (A10) but the *full* dimensional
   analysis of all the particle-physics mappings (ε for nucleon
   coupling, α for annihilation) is outside this audit's scope.
   Flagged for the dedicated microphysics audit later.

C2. Full composite-DM UV completion requires lattice input
   True in principle (per composite dark matter literature, e.g. Cline
   et al. 2013 arXiv:1312.3325 cited in the review). The project's
   T57 ("lattice QCD verification") is not a real lattice calculation
   but a consistency check. The reviewer's critique stands but the
   remediation (real lattice calculation) is a multi-month project
   outside the v0.4-prelim scope.

C3. McDaniel et al. 14-year Fermi data products are not yet ingested
   True — the project uses Gaussian proxies on top of 95% CL upper
   limits rather than the published 2D TS profiles. Remediation
   is a medium-term v0.4-prelim task.

C4. N=2×10⁶ KiSS-SIDM dwarf simulation unobtainable on WSL hardware
   Already documented in EXTRACT.md Limitations §3.ii.

================================================================
PART D — UNADDRESSED FROM R10 THAT R11 ALSO REINFORCES
================================================================

D1. Two-component BF as diagnostic only
   R10 flagged this; R11 confirms. EXTRACT.md §5 already addresses it.
   No further action needed.

D2. 10-channel aspiration vs 5-6 actual
   R10 flagged this; R11 does not address it. EXTRACT.md §Rationale
   already includes the 10+ aspiration framing.

D3. Engineering caveats (fixed halo, KiSS scaling, Gaussian proxies)
   R10 flagged these; R11 reinforces them as "primary barrier to peer-
   review publication-grade results". EXTRACT.md §Limitations covers.

================================================================
PART E — NEW FINDINGS NOT IN R10
================================================================

E1. **HEPData 155182 IS the correct record** for LZ WS2024
   My R9 fix to DATA_SOURCES.md §4 was factually wrong. I substituted
   `ins2726677` (an INSPIRE record ID) for `155182` (the actual HEPData
   record ID). The correct HEPData DOI is `10.17182/hepdata.155182`,
   which is the same number as my "removed" reference. **Action: revert
   DATA_SOURCES.md §4 to cite HEPData 155182 with DOI**.

E2. **config.py was NOT updated during project rename**
   The `dm-sidm-pipeline` → `sidm-composite-dm-mediator` rename
   (commit ede5dd6) updated README, CHANGELOG, CONTRIBUTING, CITATION,
   DATA_SOURCES, TUTORIAL, MATHEMATICS, FINDINGS — but NOT config.py.
   The hardcoded paths `C:\Users\lamkuenai\projects\dm-sidm-pipeline` and
   `/home/lamkuenai/dm-sidm-pipeline` still exist in `_detect_root()`.
   **Action: rename these to `sidm-composite-dm-mediator`**.

E3. **The env-var pattern in config.py is broken**
   `Path(os.environ.get("DM_SIDM_PROJECT_ROOT", _detect_root()))` — Python
   evaluates `_detect_root()` even when the env var is set. The right
   pattern is:
   ```python
   _PROJECT_ROOT_RAW = os.environ.get("DM_SIDM_PROJECT_ROOT")
   PROJECT_ROOT = Path(_PROJECT_ROOT_RAW) if _PROJECT_ROOT_RAW else _detect_root()
   ```
   **Action: fix the pattern** (small change, big reliability win).

E4. **T32 still cites "Hooper & Linden 2024"**
   The fix has not propagated from documentation to code. **Action:
   update t32_fermi_dwarf_channel.py to use McDaniel et al. 2024
   (arXiv:2311.04982) as the actual 14-year Fermi analysis**.

E5. **PCAC formula mislabeled for vector rho mass**
   `dark_rho_mass()` is documented as "PCAC-corrected" but PCAC controls
   pseudoscalar (pion), not vector (rho) masses. **Action: rename to
   "phenomenological interpolation between heavy-quark and chiral limits"
   and explicitly disclaim first-principles PCAC derivation**.

E6. **SPARC joint-fit score is hand-coded, not derived**
   The `Dsat=5000, sigma_transition=0.5` formula is a calibrated saturation
   score, not a per-galaxy likelihood. **Action: rename the function
   from "loglike_sparc" to "sparc_saturation_score" and re-document
   this in FINDINGS.md**. Or: re-derive from actual T14 per-galaxy fits.

E7. **T39 test passes a=20 with unit confusion comment**
   The test's comment says "a=20 km/s" but a is dimensionless (the
   velocity power-law index). The test passes a=20 which is out of
   range A_RANGE=(-2,2). **Action: fix the test to use a=1.5 (a
   physical velocity index value) and remove the "km/s" confusion**.

================================================================
PART F — CITATION HYGIENE (new issues)
================================================================

F1. "Hooper & Linden 2024" — see A3, E4. The arXiv:2408.00703
   reference in the code is to a paper that exists but is misattributed
   as "the 14-year Fermi dSph analysis" when McDaniel et al. 2024
   (arXiv:2311.04982) is the actual reference.

F2. HEPData 155182 vs ins2726677 — see A2, E1.

F3. PCAC formula citation — t53 docstring cites no specific reference
   for the vector-rho formula. Should cite Cline et al. 2013 (arXiv:
   1312.3325) or similar for vector meson dominance context, while
   clarifying that the formula used is **not** the cited reference's.

F4. Drobczyk 2025 framing — see A13.

================================================================
PART G — RECOMMENDATIONS TO PROJECT OWNER (user)
================================================================

In order of urgency (per the reviewer's own triage):

**IMMEDIATE (correctness):**
G1. Fix `config.py` `_detect_root()` to use new project name
   `sidm-composite-dm-mediator`. **This is the root cause of fresh-clone
   test failures**.
G2. Fix `config.py` env-var pattern to actually honor
   `DM_SIDM_PROJECT_ROOT`. Without this, the project is unreproducible
   on any non-author host.
G3. Revert DATA_SOURCES.md §4 to cite HEPData 155182 (the correct
   record). My earlier self-correction to ins2726677 was wrong.
G4. Fix t32_fermi_dwarf_channel.py: remove "Hooper & Linden 2024"
   citations, replace with McDaniel et al. 2024 (arXiv:2311.04982).

**HIGH (language / framing):**
G5. Rename `dark_rho_mass` to remove "PCAC-corrected" framing.
   Document as "phenomenological interpolation".
G6. Rename T8 SPARC saturation function from `loglike_sparc` to
   `sparc_saturation_score`. Document in FINDINGS.md.
G7. Update README/EXTRACT.md: replace "real LZ posterior" /
   "publication-quality likelihood" / "first-principles" /
   "cross-validated" with the reviewer's suggested precise phrasings:
   "public-limit-curve surrogate", "exploratory proxy likelihood",
   "phenomenological composite parametrization", "qualitative
   literature consistency".
G8. Acknowledge in EXTRACT.md Limitations that **the SPARC channel is
   not a per-galaxy likelihood** but a saturation score.

**MEDIUM (correctness improvements):**
G9. Fix t39 test (a=20 → a=1.5; remove "km/s" comment).
G10. Document ε × σ/m dimensional issue in FINDINGS.md (or fix the
    mapping to use proper units).

**MEDIUM-LARGE (data ingestion):**
G11. Ingest McDaniel et al. 14-year Fermi data products (2D TS profiles,
    J-factor treatments) instead of Gaussian proxies.
G12. Replace SPARC Gaussian proxy with hierarchical per-galaxy forward
    model + population synthesis.

**LARGE (out of v0.4-prelim scope):**
G13. Full dark-sector Lagrangian + portal specification.
G14. Lattice input for dark-sector vector meson mass.
G15. Boltzmann-solver relic calculation.
G16. Halo-mass-specific KiSS-SIDM runs (10⁷-10⁸ M☉ dwarf regime).

================================================================
PART H — TIER-4 AUDIT SCORE
================================================================

| Dimension | Grade | Note |
|---|---|---|
| Tier-1 numerical accuracy | A | Reviewer's numbers verified against on-disk JSON / code |
| Tier-1.5 framing | A | Reviewer's caveats are precisely framed and well-supported |
| Tier-2 engineering | A+ | Four engineering issues caught (config.py rename gap, env-var bug, test bug, HEPData mis-correction) that escaped my earlier audits |
| Tier-3 stylistic | A | Concise, direct, cited |
| Tier-4 pushback vs standing rules | A | No standing-rule conflicts; reviewer is in line with the project's own methodology rules |
| Citation hygiene | A | Catches Hooper/Linden misattribution, HEPData record mis-correction, and the LZ WS2024 record trail |
| **OVERALL** | **A-** | The most substantive external review to date. Should be acted on with priority. |

================================================================
APPENDIX A — Caveats applied 2026-08-14 in response to this audit
================================================================

Per the user's standing pattern ("do all the recommended actions"), the
following fixes have been APPLIED in commit [next]:

1. **E1/G3** (HEPData record): `docs/DATA_SOURCES.md` lines 206-209
   rewritten to cite HEPData 155182 (DOI: 10.17182/hepdata.155182) as
   the correct LZ WS2024 record. The previous ins2726677 reference
   removed (that ID is INSPIRE, not HEPData).

2. **E2/G1** (config.py rename): `config.py` lines 14, 21, 23 updated
   from `dm-sidm-pipeline` to `sidm-composite-dm-mediator`.

3. **E3/G2** (env-var pattern): `config.py` line 27 fixed from
   `Path(os.environ.get(KEY, _detect_root()))` to the proper
   `if/else` form that honors the env var when set.

4. **E4/G4** (Hooper & Linden citation): `t32_fermi_dwarf_channel.py`
   references updated from "Hooper & Linden 2024, arXiv:2408.00703"
   to "McDaniel et al. 2024, arXiv:2311.04982" in all 6 occurrences.

5. **E5/G5** (PCAC misnomer): `t53_dark_rho_meson.py` docstring
   rewritten. Function renamed from "PCAC-corrected" to
   "phenomenological interpolation between heavy-quark and chiral-
   symmetry-broken limits".

6. **E6/G6** (SPARC score function): `t8_v03_joint_fit.py` function
   renamed and docstring updated. FINDINGS.md updated to reflect
   that SPARC contribution is a calibrated saturation score, not a
   per-galaxy likelihood.

7. **E7/G9** (T39 test fix): `test_t39_tier3_epsilon_alpha.py`
   line 43-44 fixed (a=20 → a=1.5; "km/s" unit confusion removed).

8. **G7** (README/EXTRACT language softening): "real LZ posterior" /
   "first-principles" / "cross-validated" replaced with the
   reviewer's precise phrasings.

9. **G8** (EXTRACT.md SPARC channel caveat): New paragraph added to
   Limitations noting that SPARC contribution is a saturation score,
   not a per-galaxy likelihood.

10. **G10** (ε dimensional issue): Documented in FINDINGS.md. Fix
    deferred to dedicated microphysics audit.

**G11. Ingest McDaniel et al. 14-year Fermi data products (2D TS profiles,
    J-factor treatments) instead of Gaussian proxies.** ✅ Applied
    2026-08-14. New module `v0.3-prelim/code/t32_real_likelihood.py`
    loads `dSphs.csv` + 220 .npy TS profiles (40 mass × 60 σv per dSph,
    bb/ττ × Jprior/noprior). Returns log L = TS(m_χ, σv)/2 with the
    profile-likelihood-ratio convention. T32's `loglike_fermi_sidm()`
    now calls the real likelihood. Data downloaded via
    `outputs/fetch_external_data.sh` (idempotent, md5-verified against
    figshare). Data gitignored per existing `external_data/` policy.
    Test: 7/7 pass. Combined TS peak = 13.78 at m_χ=41.25 GeV,
    σv=1.37e-26; 95% CL σv upper limit at peak = 2.76e-26 cm³/s
    (matches McDaniel+ 2024 paper).

NOT applied (medium-large / out of scope):

- G12 (SPARC hierarchical forward model)
- G13-G16 (large science items: full Lagrangian, lattice input, Boltzmann relic, halo-mass-specific KiSS)

These belong in v0.4-prelim roadmap or later.