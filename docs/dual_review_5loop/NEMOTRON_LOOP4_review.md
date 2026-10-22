# Nemotron 550B Review (Loop 4)

**Model:** `nvidia/nemotron-3-ultra-550b-a55b:free` (OpenRouter free tier)  
**Transport:** Hermes `delegate_task` child  
**Delegation:** `deleg_b1fc89ec`  
**Subagent session:** `20261022_092709_327a61`

> **Status: UNVERIFIED SECOND OPINION.** Every numerical claim below must be
> recomputed in Python before it is acted on. Where the OpenCode/DeepSeek
> reviewer disagrees, that disagreement is the claim to compute first.

## Review

[OK] v0.3-prelim/code/T208_path_b_cloud9_host_halo_gravothermal.py:48-82 — Script's `nfw_rho_s_from_concentration` reproduces JSON `rho_s = 9.68962001e-3 M_sun/pc^3` exactly. Formula: `rho_s = M_halo/(4π r_s^3)/[ln(1+c)-c/(1+c)]` with `M_halo=5e9`, `c=12`, `r_vir=35092.9 pc`, `r_s=2924.4 pc` → `9.68962e-3`.

[ERR] v0.3-prelim/docs/PAPER_V1_DRAFT.md:166-168 — Paper states `rho_s = (200/3)*rho_crit*c / [ln(1+c)-c/(1+c)]` (missing `c^3`). Correct NFW definition: `rho_s = (200/3)*rho_crit*c^3 / [ln(1+c)-c/(1+c)]` because `M_vir = (4/3)π r_vir^3·200ρ_crit` and `r_s = r_vir/c`. Paper's formula gives `6.73e-5` (factor 144 low). Both script formula and correct `c^3` formula yield `9.68962e-3` (ratio=1.0).

[OK] v0.3-prelim/code/T208_path_b_cloud9_host_halo_gravothermal.py:48-82 — Script's `v_max_from_M_c` for `c=12` yields `V_max = 31.1186 km/s` (paper: 31.12). For `c=4` yields `25.5881 km/s` (paper: 25.59). Both match.

[ERR] v0.3-prelim/data/results/t208_path_b_cloud9_host_halo_gravothermal.json:138 — JSON reports `V_max_kms = 24.75455` for `c=12`. This equals `V_vir = sqrt(G·M_halo/r_vir) = 24.7546 km/s`, not the true NFW `V_max = 31.12 km/s`. JSON uses virial approximation, inconsistent with script's own function and paper claims.

[ERR] v0.3-prelim/data/results/t208_path_b_cloud9_host_halo_gravothermal.json:155 — `subhalo_1e6_crosscheck V_max_kms = 1.44765` for `M=1e6, c=15`. This equals `V_vir = 1.44765 km/s`. Correct NFW `V_max = 1.9245 km/s` (33% higher). Not consistent with script's NFW routine. Expected for `1e6 M_sun` halo: `~1.92 km/s`.

[ERR] v0.3-prelim/code/T208_path_b_cloud9_host_halo_gravothermal.py:62-65 — Docstring claims `M(<r_max)/M_vir ≈ 0.20` and `V_max/V_vir ≈ sqrt(0.20×12) ≈ 1.55`. Actual: `M(<r_max)/M_vir = 0.2848`, `sqrt(0.2848×12) = 1.85`, actual ratio `= 1.257`. The `0.20` is wrong (should be `~0.285`). However, the "20-30% underestimate" claim is roughly correct: `(V_max-V_vir)/V_max = 20.5%`, `(V_max-V_vir)/V_vir = 25.7%`.

[Q] v0.3-prelim/data/results/t208_path_b_cloud9_host_halo_gravothermal.json:160 — `matches_T204: false` for subhalo crosscheck. Likely explained by T204 using correct NFW `V_max` while T208 JSON uses `V_vir`. Undermines cross-check validity; paper does not explicitly explain this failure in provided excerpts.