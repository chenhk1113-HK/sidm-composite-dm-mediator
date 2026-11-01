# evidence_n24 — n24 review response artifacts

Reproduce the claims quoted in report sections 25.1–25.8 (run from the repo
root; Python 3.14 at C:/Python314):

1. Full gate on the round's final tree (wall time and pytest count are
   recorded in report §25.9):
       python scripts/verify_release_gate.py
   Expect: 15/15 PASS, the pytest layer never SKIP (no --quick used), the
   SCOPE sentence printed, exit code 0.

2. Layer-15 mutation proof (report §25.1):
       python scripts/audit_register_state_mutation_proof.py
   -> LAYER-15 MUTATION PROOF PASSED: CONTROL green; open-set line missing a
      gap, table row flipped, and stale status sentence injected each exit 1.

3. Gate crash/SKIP-contract proof (report §25.2, §25.5):
       python scripts/verify_gate_crash_mutation_proof.py
   -> MUTATION PROOF PASSED: a killed layer turns the gate red (layer exit 3,
      gate exit 1, poisoned layer excluded from 'Checked:', no PASS phrasing);
      --quick SKIP + SCOPE contract verified end-to-end against the shipped gate.

4. Determinism (report §25.8, same evidence class as §24.3): gate_run_final.txt
   and gate_run_committed.txt — two full runs of the gate on the final tree
   (one pre-commit, one on committed HEAD). Their layer tables must be
   identical; identical totals are recorded in §25.9.

5. Layer-11 containment close-out (report §25.10, commit baa21a3):
       python v0.3-prelim/tests/test_pdf_render_relax.py
   -> ALL PASS (6 tests: split world, fused world, quote-edge symmetry,
      coverage match only via the fused variant, true-absence control).
       python scripts/audit_pdf_render.py docs/dual_review_5loop/evidence_n24/
           jobs_v114_frozen.json                     # frozen v1.14 pair
       python scripts/audit_pdf_render.py           # live v1.15 pair
   -> frozen pair RESULT: PASS (was 8 containment defects with the pre-fix
      checker — direct before/after on the git-declared byte-frozen input);
      live pair RESULT: PASS with the measured budget (69, §25.6).
   Captured logs: pdf_audit_frozen_v114.log, pdf_audit_v115_final.log,
   test_relax_units.txt.
