# evidence_n24 — n24 review response artifacts

Files here:
- det_runA.json / det_runB.json / det_runC.json — full gate summaries from the
  three back-to-back determinism runs (run #3 in the n24 sequence): identical
  canonical fingerprint across all three (report section 25.8).
  Reproduce: python scripts/verify_release_gate.py --mutations _proofs/det_runX.json --mutations-only (x3, compare).

Proof scripts (re-run to reproduce the claims quoted in report sections 25.3 / 25.6):
- python scripts/verify_gate_crash_mutation_proof.py
    -> MUTATION PROOF PASSED: killed layer turns the gate red (run 1: exit 3,
       no 'ALL GATES PASSED', poisoned layer excluded from 'Checked:');
       --quick SKIP + SCOPE contract verified end-to-end (run 2).
- python scripts/audit_register_state_mutation_proof.py
    -> LAYER-15 MUTATION PROOF PASSED: all three n23 finding shapes caught
       (open-set missing a gap; table/prose disagreement; stale status
       sentence) with frozen history exempt (CONTROL run green).
