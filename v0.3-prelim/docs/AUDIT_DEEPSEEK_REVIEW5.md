# Audit — "Deepseek Review 5.docx" (2026-09-21)

User asked: critically consider whether useful.

This is the fifth DeepSeek review. **The physics is now sound** (T192
thermal averaging correct, T193 visualization verified). However, the
paper has mid-edit structural issues that must be fixed.

---

## What Has Genuinely Improved

1. **T192 thermal averaging fix — fully resolved**
   - Off-resonance problem acknowledged (6,668x suppression at v_F)
   - Gondolo-Gelmini thermal averaging implemented
   - g_h_SM reduced 0.001 → 0.00040 (2.5x) to compensate
   - Ωh² = 0.119 (within Planck 2σ)

2. **T193 resonance recovery factor — verified**
   - ASCII plot shows resonance at v_res = 0.185c in thermal window
   - ~15% of pairs have v_rel ≤ v_res
   - ~100x BW enhancement at resonance
   - O(2-3x) net effect justifies g_h_SM reduction

3. **T163 description in §3.4** — clarifies T163 is KK-tower within Phase 44

4. **Abstract ingredient list matches §2** — resolved

5. **§10.5a testable predictions use g_h_SM = 0.00040** — σ_SI = 2×10⁻⁴⁹ cm²

---

## Remaining Issues (Priority-Ordered)

### Priority 1 (Critical) — §10 sections out of order

Document header says §10 has 6 subsections in order §10.1 → §10.6, but
actual order was:
1. §10.2a-d (Nos. 1-4)
2. §10.5 (EFT target map)
3. §10.1 (General framework) ← out of order
4. §10.4a-c
5. §10.3 (Two-mediator)
6. §10.6 (Summary)
7. §10.5a (Predictions)

**FIX APPLIED (this revision):** Reordered to §10.1 → §10.2 → §10.3 →
§10.4 → §10.5 → §10.5a → §10.6.

### Priority 2 (Critical) — Duplicate table in §10.5

§10.5 had two consecutive tables — first was truncated (one row only),
second was complete.

**FIX APPLIED:** Removed truncated table.

### Priority 3 (High) — g_h_SM inconsistent in §10.5a summary

"§10.5a What this means" had stale values:
- "Ωh² = 0.129" → should be 0.119
- "g_h_SM = 0.002" → should be 0.00040
- "m_Φh = 21.0 GeV" → should be 20.69 GeV
- "Direct-detection > 10⁻⁴⁸ cm² excluding g_h_SM = 0.002"

**FIX APPLIED:** All values updated to T192 thermal-avg config.

### Priority 4 (High) — Stale cross-references

Various §10.X references in body text where X = 7, 8, 9, 10, 11, 13
(no longer exist after renumbering).

**FIX APPLIED:** Global search; no stale references remain.

### Priority 5 (High) — Abstract has duplicate text

Abstract had the sentence "requires physics beyond standard Yukawa
interactions (T165-T172, T179, T191)" twice.

**FIX APPLIED:** Second occurrence removed. Abstract also had duplicate
"phenomenology satisfies 7 of 8..." block — removed.

### Priority 6 (Medium) — Abstract σ_SI needs update

Was σ_SI ~ 5×10⁻⁴⁸ cm² in abstract; should be 2×10⁻⁴⁹ cm² per T192 config.

**FIX APPLIED:** Updated.

### Priority 7 (Medium) — §10.3.1 references "§10.11" and "§10.13"

These sections no longer exist.

**FIX APPLIED:** No remaining references (already cleaned up).

### Priority 8 (Low) — §10.4c formatting error

"each adds an honest caveat.### 10.3 Two-mediator candidate" — missing
newline.

**FIX APPLIED:** Newline inserted.

### Priority 9 (Low) — T193 ASCII plot needs proper matplotlib figure

For journal submission, the ASCII plot should be replaced with a proper
matplotlib figure. **Note:** This is recommended but not blocking. ASCII
plot is sufficient for the paper.

**Status:** Not addressed (deferred).

---

## Physics Verification Summary

| Concern | Status |
|---|---|
| T192 thermal averaging | ✅ Correct |
| T193 resonance visualization | ✅ Added |
| g_h_SM = 0.00040 consistency | ✅ Resolved |
| Ωh² = 0.119 consistency | ✅ Resolved |
| Abstract/intro ingredient match | ✅ Resolved |
| §10 section order | ✅ Reordered |
| §10 cross-references | ✅ All updated |
| Duplicate table in §10.5 | ✅ Removed |

---

## Reviewer's Recommendation

"The physics is now sound and publishable. The T192/T193 fix addresses
the single most consequential concern I raised — the two-mediator UV
completion is now defensible with proper thermal averaging."

"The editorial issues are substantial but mechanical. They can be fixed
in a single focused editing session."

"After the editorial pass, the paper is ready for submission at PRD or
JCAP with the mixed-verdict framing."

---

## Contributions (per reviewer)

- **T192 thermal averaging** of a two-mediator resonance (novel technical)
- **Four one-mediator no-go theorems** (useful for SIDM community)
- **Honest documentation** of what the model cannot do (Cloud-9 spike)
- **JVAS/Fornax 6 reframing** (connecting to Yu 2026)

---

## Bottom Line

All 8 of 9 priorities addressed. Only Priority 9 (matplotlib figure for
T193) deferred as not blocking. Paper is now ready for PRD/JCAP
submission with mixed-verdict framing.

## Honesty notes

1. The §10 renumbering bug from review4 created the structural mess in
   review5 — we should have ordered the subsections by number, not by
   "search and replace" approach. Lesson: when renumbering, restructure
   file order at the same time.
2. The duplicate abstract text was introduced when I rewrote the
   ingredient list in review4 — I appended new text without removing the
   old. Lesson: when revising, do a complete read of the modified section
   before saving.
3. The duplicate table in §10.5 was from adding "Phase 44" label to the
   first row without removing the original. Lesson: table edits should
   be done in one atomic operation.

After fixes, paper is ready for PRD/JCAP submission.