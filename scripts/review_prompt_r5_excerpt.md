You are Reviewer 2 for the SIDM composite dark matter paper. You have READ access to the project files.

FILE TO READ: docs/R5_EXCERPT.md — this contains the EXACT numbered line ranges from v0.3-prelim/docs/PAPER_V1_DRAFT.md that are under review. Line numbers in the excerpt (e.g. "11|") are the paper's own line numbers. Read ONLY this excerpt; do not read the whole paper (it is 2400 lines).

Do NOT rewrite anything. Return findings only, with exactly these tags:
- **[ERR]** definite error
- **[Q]** question or unverifiable claim
- **[OK]** checked and found correct

For every number, cite the excerpt line number. If you compute anything, show the formula and numbers. If unsure, use [Q] rather than asserting. Keep the review UNDER 600 WORDS. Do not use tools other than reading docs/R5_EXCERPT.md.

CONTEXT: This is Round 5, a final verification pass. Rounds 1-4 already fixed 17 defects. Your job is (a) confirm each fix actually landed correctly, and (b) find anything still broken.

VERIFY THESE FIXES (one line each in your answer):

F1 (Q1, L11) Abstract must distinguish microphysical σ/m from σ_eff = f_H²·σ/m, and must state σ_eff(15) = 0.251 is BELOW the 0.8 ceiling while the excess is in σ/m. Is this coherent? Note the "3.6-23.7x" ratio refers to σ/m, not σ_eff — is that clearly stated?

F2 (Q8/Q11, L36, L2205-2210) Horigome ceilings: the 0.2 cm²/g value is the "decisive CDM-preference threshold" AND the w=10 km/s velocity-dependent limit; the velocity-independent w→∞ upper limit is 0.04. Are the labels now correct? Are the 27-49x and 830x numbers right against 0.2? Check: does 0.8/0.04 = 20 relate to any quoted number?

F3 (Q4, L117) Gaussian tail at v=15: exp[-(15-29.4)²/(2·3.0²)]. Compute it. The paper should quote ~1.0e-5 (was 8e-5). Is it right?

F4 (Q5, L143-145) Hierarchy bound direction: the D-5 (σ_1=1.0) constraint is LOOSER than the σ_1=4.4 headline. Does the paper say LOOSER/LESS restrictive? Check the numbers: v=28 bound 2.84e-13 vs headline 1.74e-13 — is 2.84e-13 really looser than 1.74e-13?

F5 (Q2, L57) Breit-Wigner normalization must have unit peak (peak value 1, at v=v_t). Is it stated that way, and is there a note that the code uses the energy-space unit-peak form?

F6 (Q3, L82) s-channel resonance formula must be v_res = c·sqrt(8·ΔM/(2·m_χ)), NOT v_res = (m_med/m_χ)·c. Verify the excerpt's stated ΔM = 2.40 eV and ΔM/(2·m_χ) = 1.2e-9 give v_res = 29.4 km/s: compute c·sqrt(8·1.2e-9).

F7 (Q3, L82) The "four mediators" claim must be GONE, and v₂-v₄ must be described as bookkeeping nodes not physical resonances (see Q12, L896-898). Is it?

F8 (Q6, L189-190) Both σ_peak causality caps must read 47.67. Compute: if ratio(σ_peak) = K/σ_peak and ratio(50) = 2.86, what is the cap at ratio = 3.0? Is 47.67 right?

F9 (Q7, L1012) The "7 of 8" must be framed as a RETRACTED v1.12/v1.13 placeholder claim, NOT a current finding, and must not contradict the adjacent statement that SPARC cannot be matched. Is it?

F10 (Q9/Q10, L1602-1604, L2264) Channel counts: 4 PASS / 3 MARGINAL / 1 FAIL over 8 constrained channels. Verify the named lists: 4 PASS = Cluster v=500, dSph v=10, Cloud-9 v=28, SPARC v=100; 3 MARGINAL = UFD v=3, v=5, v=15; 1 FAIL = dSph v=7. Do these sum to 8 and are they consistent across all occurrences in the excerpt?

FIND ANYTHING ELSE in the excerpt that is internally inconsistent or wrong. Report it with [ERR] or [Q].