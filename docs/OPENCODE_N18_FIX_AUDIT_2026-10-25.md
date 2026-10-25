# Independent Reviewer Audit — n18 review-response fix set (Reviewer B)

**Reviewer:** `opencode/deepseek-v4.1-flash-free` (opencode CLI, free tier).
**Date:** 2026-10-25
**Audit target:** the n18.docx review-response round (fixes F1–F16) in the SIDM v19.2-F paper project.
**Repository:** `C:\Users\lamkuenai\projects\sidm-composite-dm-mediator` (branch `wip/v19.2-F-init`)
**Companion audit:** `docs/NEMOTRON_N18_FIX_AUDIT_2026-10-25.md` (Reviewer A, Nemotron 550B).

## How this review was obtained

`scripts/dual_review.py` passes the prompt as a **command-line argument** to `opencode run`.
A 23 KB prompt exceeds the Windows command-line limit, so every model in the priority chain
returned `EXIT_1 The command line is too long` and no review was written. The working pattern
keeps the argv small and attaches the bulky material:

```bash
opencode run --model opencode/deepseek-v4.1-flash-free --format json \
  "$(cat short_prompt.txt)" -f excerpt_paper.txt -f excerpt_sweep.txt > review.jsonl
```

The message must come **first**: `-f` is an array option and swallows a later positional.
Raw JSONL transcript: `~/.hermes/cache/scratch/opencode_audit2.jsonl`.

## Verbatim reviewer output

This reviewer returned **4 of 6 claims VERIFIED and 2 PARTLY-WRONG**, and raised the finding
that the controller had missed — the stale §2.6a Fornax σ_HL column (see consolidated report §14.1).

---

**CLAIM 1 — VERIFIED.** L102 now reads “For **0 of 8** halos, |σ_HL| < 0.05 cm²/g”; JSON L222–223 gives `n_halos=8` and `n_halos_abs_sigma_HL_below_0.05=0`. The comma repairs the old “0 of 8 halos is” error. It is still compressed— “0 of 8 halos satisfy” would be clearer—but not ungrammatical.

**CLAIM 2 — VERIFIED.** L102 has “σ_HL = −0.534 cm²/g, indicating an **internal inconsistency …**”; the old `.,` and `an**` are gone. JSON L220 `sigma_HL_cm2_per_g.max = -0.534026514…` rounds to −0.534. The period sits outside the bold span, which is correct.

**CLAIM 3 — PARTLY-WRONG.** L151 restores the “σ_1 = 4.4” label, but 7.5×10⁻¹² is not consistent with the same paragraph’s like-for-like v=28 bounds. 7.5e-12 / 1.78e-13 = 42.1 (denominator 1,775× larger); a bound 42× looser cannot be the v=28 baseline. 7.5e-12 is only ~0.74× the v=100 bound 1.01e-11, so it could be a v≈100 number, but the sentence does not say so. As written, it contradicts the 1.78e-13 / 1.84e-13 / 2.84e-13 set.

**CLAIM 4 — VERIFIED.** Generator L80 sets `F_H_CC = 0.30`; 0.30² × 2.845457 = 0.256091 → 0.256, and 0.30² × 16.865226 = 1.517870 → 1.518. The docstring L24 matches, as do JSON L210–213. The paper L102’s 0.257 comes from using rounded 2.85; that is a separate rounding, not the docstring claim.

**CLAIM 5 — VERIFIED.** The test reads JSON `_derived_ranges` L210–213 and the generator’s `F_H_CC`, computes the expected range, regex-captures the docstring, and asserts equality. All four tests pass locally. Changing either the JSON or the docstring fails it. The hard-coded 0.257–1.589 check is an extra guard, not the pin itself.

**CLAIM 6 — PARTLY-WRONG.** §3 is a diff, not the full 241-line file, and its added `_derived_ranges`, interpretation, and limitation content matches `git diff 7cc8d8a^ HEAD`. But it is not verbatim: long lines are manually soft-wrapped with literal backslashes (`\cm^2/g`, `\Per`) absent from git; it says 39 diff lines while `git diff | wc -l` = 41 (`+19/−1`); and it says 9,895 bytes while the file is 10,135 bytes.

**D1 — ARITHMETIC CORRECT, PREMISE STALE.** (0.032 − 0.09×2.5597)/0.42 = −0.4723 and (0.0318 − 0.09×2.845457)/0.42 = −0.53403. But the 2.6a JSON (excerpt_sweep L4) is stale: `scripts/v192_a_phase44_sigma_peak_sensitivity.py` L35 uses `V1_V_TARGET = 29.4` and L230 says v−29.4; `compute_row(174)` now gives σ/m(15)=2.8455, σ_HL=−0.5336, c4 σ/m=120.354, t_core=4.955 Gyr. The checked-in JSON gives 2.5597/−0.4723 and c4 149.991/3.976. So −0.47 is a stale-output artifact, not a live alternate parameterization; the distinction is defensible only for the old files.

**D2 — NO.** CommonMark does parse intraword `**` as `<strong>`, but it inserts no spaces: L102 “calibrated**independently**—” renders “calibratedindependently—”; L151 “constraint**depends” renders “constraintdepends”. With 109 such instances, these are visible copy defects; add spaces around bold spans.

**D3 — NO.** Both `does not..` and `curves .**` are on L120, inside the repaired §2.5 region, and that same line still has stale `σ_HL = -0.47` and `σ/m = 2.85–18` (JSON max 16.865). Pre-dating Round 5 does not make them correct, and the line needed editing anyway.

**ADDITIONAL FINDINGS**
- L120 still says Fornax `σ_HL = -0.47`; canonical JSON L220 says −0.5340. The F8 fix changed L115 and L221 but missed L120. L194 also says “At σ_peak = 174 (canonical), σ_HL = −0.47”; either label it “§2.6a v=28 stale” or update it.
- The §2.6a section mixes anchors: L190/L194 use −0.47 from the stale v=28 JSON, while L192 uses σ/m=120.32 and t_core=4.97, which match the current v=29.4 generator. The checked-in 2.6a JSON must be regenerated.
- Minor: L102 exact 0.09×2.845457 = 0.25609 → 0.256, not 0.257; 0.2565/0.0318 = 8.07, not 8.0. L115 0.297²×2.85 = 0.2514, not 0.252. Recompute from unrounded values.
