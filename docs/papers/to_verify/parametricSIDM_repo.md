# parametricSIDM (github.com/DanengYang/parametricSIDM)

**Status:** TO VERIFY (GitHub repo inspected 2026-10-17, no local install)
**Repo:** [github.com/DanengYang/parametricSIDM](https://github.com/DanengYang/parametricSIDM)
**Paper:** arXiv:2305.16176 (Yang et al. — *the paper incorrectly cited in v40.4 as if it were the gravothermal Cloud-9 paper*)
**License:** Has LICENSE file (need to read to confirm terms)

## Authorship
- **Daneng Yang** (UCR) — same author as the v19.2-F canonical Cloud-9 paper arXiv:2305.05067
- (Other coauthors of 2305.16176: see Yang+ 2024 Parametric SIDM Halos, JCAP)

## What it provides
- **Parametric model for SIDM halos**: analytic density profiles (core → collapse) from CDM NFW parameters
- Optional **baryons** component
- V_max–R_max basis conversion
- Tutorial + samples + figures
- This is the **same model used internally by SASHIMI-SIDM** (arXiv:2403.16633)

## v19.2-F relevance assessment

**Relevance:** MEDIUM — could supplement or replace parts of the v19.2-F gravothermal pipeline.

**What's directly useful:**
- Analytic SIDM density profiles for the **core → collapse transition** — exactly what v40.7 gravothermal t_c analysis needs
- Could provide a **calibrated upgrade** to the project's existing `gravothermal_yang2024.py` (currently Balberg-style)
- Same author as the Cloud-9 paper — likely consistent with v19.2-F's existing framework
- Has samples and tutorial — easy to evaluate

**What's NOT directly useful for v40.x:**
- v40.x gravothermal already has a working pipeline (3 t_c functions: literal, BM2-calibrated, legacy)
- The Balberg-style collapse time formula in `gravothermal_yang2024.py` is intentional (matches the "Yang+ 2024 gravothermal" Loop 4 analysis)
- Integration cost: would need to re-validate Loop 4 t_c values against the parametric model

**The CRITICAL context — connection to v40.4 bug:**
- v40.4 Loop 1 code cited arXiv:2305.16176 as the gravothermal/isothermal comparison paper
- ACTUAL paper at arXiv:2305.16176: "A Parametric Model for SIDM Halos" (this repo's paper)
- CORRECT paper for gravothermal/isothermal comparison: arXiv:2305.05067 (MNRAS 533, 4007)
- Fixed in v40.13; parametricSIDM is a real, useful paper but NOT the gravothermal reference

**Cited in v19.2-F?** Only via the v40.4 wrong-citation bug (which has been fixed in v40.13+v40.14). Not actively used.

**If adopted, would need to:**
1. Read full paper to confirm core-collapse formula
2. Add to `docs/papers/verified/` once read
3. Re-validate Loop 4 t_c values against parametric model
4. Update KB entries + registry
5. Possibly archive `gravothermal_yang2024.py` if parametricSIDM replaces it

## TO VERIFY
- LICENSE terms (BSD? MIT? GPL?)
- Last commit / maintenance status
- Read full paper to confirm core-collapse formula matches v19.2-F use case
- Cross-check V_max–R_max conversion against Cloud-9 (5×10⁹ M☉, V_max ~ 10 km/s)
