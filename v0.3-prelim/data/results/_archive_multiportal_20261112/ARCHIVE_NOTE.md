# Archived: multi-portal joint-fit artifacts (2026-11-12)

`t90_v45_multi_portal_joint_fit.json` (9143 s run), its `_nlive200` variant and the legacy
`_nlive50` variant are archived here, not deleted.

Why archived rather than regenerated:

- The 2026-11-11 Born transfer-factor correction moved the joint fit's MAP to
  sigma/m(28 km/s) = 10.7 cm^2/g - below the Cloud-9 band the pipeline was exploring.
- After the 2026-11-12 re-binding of the Cloud-9 M_200 claim to the T208 host-halo
  artifact, **no tracked claim in `scripts/audit_claims.py` and no standing number in
  `v0.3-prelim/docs/PAPER_STANDING_NUMBERS.md` depends on any of these files.**
- The seed+interval forward rule (`scripts/seed_interval_audit.py`) applies to artifacts
  dated 2026-11-11 or later: complying would mean re-running a 2.5 h nested sampling job
  (and a 22 min variant) for a result nobody cites. Standing policy: pipelines that
  support no standing claim are marked superseded, and artifacts that are not useful are
  archived rather than re-run.

The archived artifacts predate the seed+interval contract (no `seed` key, no credible
intervals) - that is exactly why they were not kept live in `data/results/`.

Consumers: `phase21/22/23/24/25_*.py` read `t90_v45_multi_portal_joint_fit_nlive200.json`
from `data/results/`; they will not find it after this commit. Of those, only
`phase23`'s stored artifact is retained (for its disclosed 4.7e9 nuisance-prior value);
the phase21/22/24/25 multi-portal outputs are not claim sources. The pipeline code is
retained unchanged for provenance.
