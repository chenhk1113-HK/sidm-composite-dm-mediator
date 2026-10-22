# ROUND 5 FINAL DUAL REVIEW — FIXED PAPER (post-Rounds 1-4)

You are the second-pass physics reviewer for the SIDM composite dark matter paper (v0.3-prelim/docs/PAPER_V1_DRAFT.md). You have READ access to the project files. Read them. Do NOT rewrite the paper. Return findings only, using exactly these tags:
- **[ERR]** for a definite error
- **[Q]** for a question or unverifiable claim
- **[OK]** for something you checked and found correct

For every number you quote, state the file and line you got it from. If you compute anything, show the formula and the numbers. If you are unsure, say so in a **[Q]** tag rather than asserting.

## TARGET: Verify the 4 rounds of fixes and check for remaining structural issues

The paper has gone through 4 rounds of defect fixes:
- **Round 1**: T208 JSON staleness + mechanism gate
- **Round 2**: 5 defects (Horigome labels L36/L2153/L2210, abstract σ_eff L11, Gaussian tail L117, hierarchy direction L143-L145, BW normalization L57)
- **Round 3**: 6 defects (s-channel formula L82, four mediators L82, σ_peak caps L189/L190, channel count framings)
- **Round 4**: Honest framing of "7 of 8" retracted claim L1012

### QUESTION 1 (Horigome ceiling labels — Round 2 F1):
Search the paper for "0.2" and "0.04" in the context of Horigome. The paper previously said "velocity-independent limit of 0.2" which was WRONG — 0.2 is the "decisive CDM-preference threshold" (Abstract, arXiv:2503.13650) and the velocity-dependent limit at w=10 km/s, while 0.04 is the actual velocity-independent w→∞ upper limit. Verify: (a) Are the ceiling labels now correctly referencing "0.2 as decisive CDM-preference threshold"? (b) Is the velocity-independent upper limit now stated as 0.04? (c) Are the 27-49x and 830x numbers correct against the 0.2 threshold?

### QUESTION 2 (Abstract σ_eff conflation — Round 2 F2):
Read L11 of the abstract. The paper previously said "σ/m at dSph velocities above 0.8 by 3.6-23.7x" which conflated σ/m with σ_eff. Verify: (a) Does the abstract now distinguish σ/m from σ_eff? (b) Does it correctly state σ_eff = f_H²·σ/m is BELOW the ceiling while σ/m exceeds it? (c) Is σ_eff(15) ≈ 0.251 cm²/g correct for the canonical Phase 44 parameters?

### QUESTION 3 (Gaussian tail — Round 2 F3):
Read L117. The paper previously said exp(-(15-29.4)²/(2·3.0²)) ≈ 8×10⁻⁵. Verify: (a) The correct value is exp(-19.92) ≈ 2.5×10⁻⁹ for the Gaussian term at v=15. (b) Does the paper now use the correct value (1.0×10⁻⁵ or similar)? (c) Is the number consistent with the paper's own σ/m values at v=15?

### QUESTION 4 (Hierarchy direction — Round 2 F4):
Read L143-L145. The paper previously said the hierarchy constraint was "more restrictive" than the σ₁ = 4.4 headline, but it was actually LOOSER. Verify: (a) Does the paper now say the v=28 bound is LESS restrictive (or LOOSER) than the σ₁ = 4.4 headline? (b) Are the ratio numbers correct: v=28 ratio ≈ 9.85×10²¹, v=100 ratio ≈ 1.24×10²⁵?

### QUESTION 5 (BW normalization — Round 2 F5):
Read L57. The paper previously had a BW normalization that peaked at 1/v_t² instead of 1. Verify: (b) Does the paper now state a unit-peak normalization? (c) Is there a note about the code using the energy-space unit-peak form?

### QUESTION 6 (s-channel formula — Round 3 F1):
Read L82. The paper previously said "v_res = (m_med/m_χ) c" which is the t-channel/Yukawa form. Verify: (a) Does the paper now use the correct s-channel near-threshold form v_res = c·sqrt(8·ΔM/(2·m_χ))? (b) Does it reference the paper's own L807 derivation (ΔM = 2.40 eV, ΔM/(2·m_χ) = 1.2×10⁻⁹ → v_res = 29.4 km/s)?

### QUESTION 7 (Four mediators — Round 3 F5):
The paper previously said "four mediators with hierarchical masses" at L82. Verify: (a) Is this claim removed? (b) Does the paper now correctly state v₂–v₄ are bookkeeping nodes, not physical resonances (per L896-898)?

### QUESTION 8 (σ_peak caps — Round 3 F3):
Read L189-L190. The paper previously had caps 47.65 and 47.71 (two rounding of the same interpolation). Verify: (a) Are both now 47.67? (b) Is the interpolation source (K = 2.86·50, cap = K/3 = 47.667) noted?

### QUESTION 9 (Channel count framings — Round 3 F4):
Search for "4 of 7", "7 of 10", "6 of 8", "1 of 8", "5 of 8" in the paper. Verify: (a) Does each occurrence have context about which likelihood/f_H/channel-set it describes? (b) Are they no longer ambiguous?

### QUESTION 10 (Honest "7 of 8" framing — Round 4 F1):
Read L1010-L1015. The paper previously said "7 of 8 channels pass" with borrowed f_H in the "Honest summary", contradicting L1010 "replaces the v1.12/v1.13 7 of 8 claim". Verify: (a) Is the "7 of 8" now correctly framed as a retracted claim? (b) Does it no longer contradict the statement that SPARC cannot be matched by single-channel σ_eff?

### QUESTION 11 (Overall coherence):
Read the paper's structure. Verify: (a) The abstract (L7-L17) matches the main text. (b) The channel count summary (L19, L25, L1602-1604, L2264) is consistent across all occurrences. (c) The no-go catalogue (L2268-L2277) is complete and consistent with the main text. (d) There are no stale cross-references or dead section links.

### QUESTION 12 (Any remaining defects):
Read the full paper. Flag any remaining errors, inconsistencies, or unclear statements that were NOT covered by Rounds 1-4.
