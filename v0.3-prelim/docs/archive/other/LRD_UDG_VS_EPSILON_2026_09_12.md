# LRD/UDG channels vs the ε ~10⁻³⁷ naturalness problem (2026-09-12)

**Status:** DISTINCT PROBLEMS. The reviewer (LRD2.docx) is correct that adding more astrophysical constraints does not improve the ε problem. This doc clarifies which work each problem touches and how the project handles them.

**TL;DR:** ε lives in T39 (Tier-3 marginalization over ε-α joint posterior). LRD lives in T90.63-v3 (Cloud-9 hybrid fit, Jiang 2026 ApJL 996 L19). UDG lives in Channels 11 (DM-free) and 13 (DM-dominated, NEW 2026-09-12). The three problems are orthogonal.

---

## The three problems

| Problem | What it asks | Which channel/subproject addresses it |
|---|---|---|
| ε naturalness | Why is kinetic mixing ~10⁻³⁵ to 10⁻⁴⁰ instead of O(1)? | **T39 Tier-3** (ε-α joint fit), Channel 12 (cosmic-web radio upper limit on ε) |
| LRD abundance | Can SIDM gravothermal collapse produce the observed LRD number density at z ~ 5-10? | **T90.63** (Cardelli dust law + Jiang 2026) |
| UDG dual populations | Can the model reproduce BOTH DM-free (NGC 1052-DF2) AND DM-dominated (LSB-6) UDGs? | **Channel 11** (DM-free) + **Channel 13** (DM-dominated, NEW 2026-09-12) |

These are three different physics questions, three different subprojects. Solving one does not solve the others.

---

## What the reviewer said (paraphrased)

> "The ε ~10⁻³⁷ required for LZ evasion remains a naturalness catastrophe regardless of how many astrophysical channels are satisfied. Adding more astrophysical constraints does not make the particle physics more plausible."

**This claim is correct in direction but needs refinement.** The project does have a separate ε-handling subproject (T39), it's just not coupled to LRD/UDG. Adding Ch13 (DM-dominated UDG) to constrain σ/m at LSB-6's velocity scale does not touch the ε question — they are physically orthogonal (one is a σ/m question, the other is a kinetic-mixing question).

What IS true:
- Astrophysical channels constrain σ/m_0 and `a` (the SIDM shape parameters)
- The ε question is a separate dimension that lives in the dark photon kinetic mixing sector
- Adding more astrophysical channels does NOT rescue ε naturalness, because they don't constrain ε

What the reviewer got slightly wrong:
- The framing "Adding more astrophysical constraints does not make the particle physics more plausible" is correct, but the LRD/UDG channels were never claimed to do so. They constrain σ/m shape, not ε.

---

## What Channel 13 (NEW 2026-09-12) does and doesn't do

**Does:**
- Constrains σ/m_0 + a at v_LSB6 ~ 15 km/s to ~14.3 cm²/g
- Tests BOTH UDG extremes (DM-free via Ch11, DM-dominated via Ch13) per LRD2.docx reviewer recommendation
- Adds 1 more channel to the 9-channel joint fit → 10 channels

**Doesn't do:**
- Constrain ε (kinetic mixing) — orthogonal parameter
- Resolve LRD σ/m tension with Cloud-9 calibration — separate question
- Fix the dSph "large peak" test failure — that's a separate bug in `channels_v03.py`

---

## Honest caveat: Channel 13 overfit

Adding Ch13 increased mean overfit penalty from 0.58 nats (9 channels) to **0.97 nats (10 channels)** — a 67% increase. Ch13 itself has **3.3 nats overfit penalty**, comparable to the original ch04 problem (was 31.8 nats before fix). This is **exactly the "evidence spread thinner" concern the reviewer raised**.

Interpretation:
1. The model cannot simultaneously fit DM-free AND DM-dominated UDGs as cleanly as it fits other channels. This is the "discriminating test" the reviewer warned about.
2. The 3.3 nats overfit is not catastrophic (threshold of "catastrophic" was ch04's 31.8 → 4.6 after fix). It's a meaningful but manageable tension.
3. **Future work**: The LSB-6 σ/m_eff = 14.3 cm²/g value (arXiv:2609.10700) is from the abstract only; full paper retrieval may revise the number or the assumed velocity scale. If LSB-6's σ/m_eff were actually 1-3 cm²/g (within Ch11's MAP), both channels would simultaneously peak and the overfit would disappear.

---

## What this doc does NOT cover

- The original dSph channel's "large peak" test failure (pre-existing, separate issue, tracked in `v0.3-prelim/docs/PRE_EXISTING_TEST_FAILURES_2026_09_12.md`)
- The ch04 width-revision backstory (covered in `v0.3-prelim/docs/CH04_TENSION_RESOLUTION_2026_09_12.md`)
- The ε marginalization posterior in detail (T39 subproject — separate doc)

---

## References

- **Reviewer**: LRD2.docx (uploaded 2026-09-12)
- **arXiv:2609.10700**: Probing dynamics of extreme galaxies I. Dark matter content in ultra-diffuse galaxies (LSB-6 σ/m constraint)
- **arXiv:2506.L19 (Jiang et al. 2026 ApJL 996 L19)**: SIDM core collapse → LRD seed mechanism
- **AGENTS.md rule 12**: catch and flag (per this doc — Channel 13 overfit is a real signal, not noise)
- **AGENTS.md rule 23**: watch for silent computational failure (this doc is the formal capture of the Ch13 overfit signal)

---

## Update: DF44 (Buzzo+ 2026) — consistency with v ≈ 28 km/s Cloud-9 peak [Phase 51+]

**arXiv:2607.26152v2** (Buzzo, van Dokkum, Abraham, Danieli, Romanowsky 2026, accepted ApJ Letters). The paper reports new ultra-deep HST WFC3/UVIS F350LP imaging of the "failed galaxy" Dragonfly-44 (DF44):

| Quantity | Value |
|---|---|
| N_GC | 73.1 ± 8.6 (settles earlier factor-of-4 controversy) |
| Half-number radius R_gc | 1.48^{+0.39}_{-0.51} R_e |
| Specific frequency S_N | 42.1 ± 4.9 |
| Inferred log(M_vir/M_⊙) | 11.5 ± 0.3 (via GC–halo mass relation) |
| Profile | Consistent with cored halo mass from stellar kinematics |

**Relevance to this project (low priority but citable):**

- **DF44 is not in our channels.** Our UDG scope is NGC 1052-DF2/DF4/DF9 (Channel 11, DM-free UDGs) and LSB-6 (Channel 13, DM-dominated UDGs). DF44 is a *separate* UDG class (massive + cored + GC-rich, in tension with the DM-free NGC 1052 family). Building a DF44 channel is a separate subproject and not recommended at this stage.

- **DF44 IS consistent with the v ≈ 28 km/s Cloud-9 peak.** The inferred cored profile at log M_vir = 11.5 indicates core-formation physics (not core-collapse) at DF44's velocity scale (~15–30 km/s). Our multi-resonance architecture predicts σ/m ≈ 100 cm²/g at v ≈ 28 km/s (Phase 44 / Cloud-9 channel), which is precisely the regime where DF44's cored profile indicates core-formation rather than collapse. **No tension with our architecture.**

- **Practical use:** cite as the modern DF44 census in any synthesis paper that touches UDGs. Do not add a DF44-specific channel; the marginal information value over our existing NGC 1052 + LSB-6 channels is low.

- **Reviewer verdict** (halo2.docx): "Moderately useful — relevant to the UDG / failed-galaxy side of your project, but not to the multi-resonance SIDM core physics." **Confirmed accurate.**

**Refs for this update:**
- arXiv:2607.26152v2 (Buzzo+ 2026, accepted ApJ Letters)
- reviewer doc: halo2.docx (uploaded 2026-09-16)
- our v ≈ 28 km/s peak: `v0.3-prelim/data/results/phase44_joint_fit.json`, `phase47_stress_test.json`
- our UDG channels: `code/channels_extended.py` (Channel 11), `code/amuse_bullet_dwarf.py`, `code/ch27_ngc1052_trail_channel.py`