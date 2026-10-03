# v19.2-D Plan — Prioritized (R80, three R79 reviewer issues resolved)

**Date:** 2026-10-01
**Status:** v19.2-C milestone in `c486782`, R72-R79 in `7f82a7c`/`4017499`/`03888ab`/`7aa10d7`/`d4e464c`/`51d6fcc`/`e90d0e6`/`c546dee`, R80 in this commit

---

## R79 plan-reviewer feedback → R80 resolutions

### Issue 1 — ρ_s = 0.05 row V_max ambiguity — RESOLVED

**Reviewer:** "If V_max = 15 and ρ_s = 0.05, t_core = 5.07 × 0.4 = 2.03, not 0.31. So the ρ_s = 0.05 row must use V_max = 18."

**Resolution:** R80 sensitivity table restructured with explicit V_max column. Each row shows V_max and ρ_s clearly:
- V_max = 18, ρ_s = 0.05 → σ/m = 6.35 cm²/g → t_core = **0.31 Gyr** (factor 0.4 from ρ_s × 2.5; canonical V_max 18, canonical ρ_s 0.05)

### Issue 2 — Fornax core citation (stellar vs DM) — RESOLVED

**Reviewer:** "Is this the DM core or the stellar core? Mateo 1998 is a review; the M_c ~ 10⁷ M☉ likely refers to Fornax's stellar mass. If the paper wants to say 'Fornax has a diffuse DM core,' cite Walker+ 2009, Read+ 2019, or Hayashi+ 2020."

**Resolution:** R80 §3.3 citation corrected:
- DM core: **Walker+ 2009 / Read+ 2019 / Hayashi+ 2020** (kinematic decomposition)
- NOT Mateo 1998 (which gives stellar mass, not DM core)
- Peñarrubia+ 2008: dynamical mass profile (different quantity)

### Issue 3 — Implication statement (tension + resolution path + falsification criterion) — RESOLVED

**Reviewer:** "The paper should say which outcome: Falsification, Open question, or Constraint. Given D-5 is the test, the paper's interim statement should be: 'The framework predicts collapse for Fornax-like halos on timescales of <1 Gyr. This is a real tension with observations. The framework's phenomenological width σ = 4.4 km/s may be too broad; a narrower width (σ ≲ 3 km/s) would suppress the dSph tail while preserving the Cloud-9 bulk (see §D-5). If no such width is consistent with the eight-channel dataset, the framework is falsified at dSph scales.'"

**Resolution:** R80 §3.3 adds three-outcome statement:
- **Resolution by narrower width (D-5):** σ_1 ≤ 3.0 km/s consistent with 8 channels → tension resolved
- **Open question (N-body resolution):** Silverman+ 2026 merger-history mechanism
- **Falsification:** If no narrower width works AND no merger correction → framework falsified at dSph scales

**Interim conclusion** explicitly stated in §3.3.

---

# DO NOW (unchanged from R79)

1. R80 patches DONE in this commit
2. D-5 σ_peak width test (4-6 hr) — THE critical test for §3.3 falsification criterion
3. D-8 post-diction audit
4. D-13 reference audit
5. Abstract readability (200 words)
6. Figure rendering
7. D-17 PDF build

---

# Submission checklist (R80)

- [x] R72-R79 all previous patches
- [x] R80 ρ_s = 0.05 row V_max explicit
- [x] R80 Fornax DM core citation corrected (Walker+ 2009, Read+ 2019, Hayashi+ 2020)
- [x] R80 Implication statement: 3 outcomes + interim conclusion
- [ ] D-5: σ_peak width test (σ_1 ≤ 3.0 km/s test for §3.3 resolution)
- [ ] D-8: Post-diction audit
- [ ] D-13: Reference audit
- [ ] Abstract 200 words
- [ ] Figure rendering
- [ ] D-17: PDF build

---

*Plan revised 2026-10-01 per R79 reviewer feedback*
*Stored at `v0.3-prelim/docs/V192_D_PRIORITIZED_PLAN_2026-10-01.md`*
*Will be re-uploaded as R80 (commit pending)*