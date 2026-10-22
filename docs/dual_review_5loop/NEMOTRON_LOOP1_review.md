# Nemotron 550B Review (Loop 1)

**Model:** `nvidia/nemotron-3-ultra-550b-a55b:free` (OpenRouter free tier)  
**Transport:** Hermes `delegate_task` child  
**Delegation:** `deleg_d3b046b1`  
**Subagent session:** `20261022_092640_105e2c`

> **Status: UNVERIFIED SECOND OPINION.** Every numerical claim below must be
> recomputed in Python before it is acted on. Where the OpenCode/DeepSeek
> reviewer disagrees, that disagreement is the claim to compute first.

## Review

Now I have all the information needed. Let me analyze and answer the four questions.

---

**[ERR] (a) V_max inconsistency: paper=31.12 km/s (PAPER_V1_DRAFT.md:167, 184, 292, 297) vs JSON=24.7546 km/s (t208...json:138). The script's `v_max_from_M_c` (T208...py:51-82) correctly implements the Reviewer-2 correction (r_max = 2.1626·r_s) and would return ~31.12 km/s. The JSON's 24.75 km/s equals the virial velocity V_vir = √(G·M/r_vir) — the OLD approximation the correction replaced. The JSON was generated with pre-correction code. Correct value for current code: **31.12 km/s** (paper value).**

**[OK] (b) t_core change with corrected V_max: For a_slope=1.0 (Phase 44 baseline), t_core formula (T208...py:97, 104) is t_core = 12.7/σ × (ρ_s/10⁻²)⁻¹ × (r_s/10⁴) × (100/V_max) with σ ∝ 1/V_max (since σ = σ₀·(100/V_max)¹·⁰). The V_max factors cancel exactly: t_core ∝ V_max / V_max = constant. Old t_core = 73.71 Gyr (JSON:145) remains 73.71 Gyr with V_max=31.12. Verdict (t_core=73.7 > t_H=13.8) **survives**.**

**[ERR] (c) Paper's 73.71 Gyr matches JSON (145) — consistent. But JSON is NOT consistent with current script: JSON V_max=24.75 (old V_vir) vs script's v_max_from_M_c returning 31.12. JSON was generated with pre-correction code.**

**[ERR] (d) Other V_max-dependent JSON values needing regeneration with corrected V_max=31.12:**
- `sigma_m_at_v_virial_C9` (JSON:141): σ ∝ 1/V_max → changes from 0.210 to 0.210×(24.75/31.12) = **0.167 cm²/g**
- `t_cross_Gyr` (JSON:146): ∝ 1/V_max → changes from 0.1155 to 0.1155×(24.75/31.12) = **0.0918 Gyr**
- `t_core_over_t_cross` (JSON:147): ∝ V_max → changes from 638.1 to 638.1×(31.12/24.75) = **802.6**
- `causality_OK` (JSON:150): threshold t_core ≥ 3·t_cross; with new t_cross=0.0918, 3·t_cross=0.275 < 73.71 → still **true** (but ratio changes)
- Subhalo cross-check V_max (JSON:155) similarly affected if its r_vir uses same method

**Paper's Cloud-9 section (§2.6/§9.12) uses canonical resonance model (σ_peak=174), not Phase 44 baseline — different physics; no direct conflict.**