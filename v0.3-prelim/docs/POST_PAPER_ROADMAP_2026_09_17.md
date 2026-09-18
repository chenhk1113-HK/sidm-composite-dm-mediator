# Post-Paper Roadmap (T100–T103) — 2026-09-17

**Status:** KIV — to be executed after Paper v1.8 (or later) is submitted/frozen.
**Triggered by:** `qwen1.docx` reviewer critique (2026-09-17).

---

## Why this document exists

The `qwen1.docx` reviewer provided a 5-phase critique + T100–T103 roadmap for elevating this project from an "AI-driven phenomenological sandbox" to a "rigorous publishable scientific framework." The critique is broadly valid for the **master branch** (`v0.4-prelim+T88E`, Composite Dark Pion + Elementary Dark Photon), which has a documented ε ~ 10^-37 kinetic mixing issue and uses a "saturation score" for SPARC.

The critique is **partially relevant to the WIP branch** (`wip/cloud-9-relhic`, Paper v1.8), where:

- The multi-resonance architecture is a fundamentally different mechanism (Breit-Wigner resonances + Yukawa background, with 5 UV embeddings) and does NOT use the ε ~ 10^-37 framework
- The semi-classical Yukawa transfer cross-section and per-channel likelihood structure are **shared limitations** between the master and WIP branches
- These shared limitations are the ones Paper v1.8 §8.4 documents as "Limitations and Future Work"

This document records the **post-paper scope** for elevating the WIP branch.

---

## Scope classification

### Phase 1 — Fix the cosmological history (master-branch critical, WIP-branch minor)

The reviewer's Action 1 (Boltzmann solver integration) is the most important for the **master branch** but is **less critical for the WIP branch**, because:

- The WIP branch's multi-resonance architecture is not strongly constrained by relic density in the same way as a single-ε composite-pion model
- The 4 Breit-Wigner resonances + Yukawa background can produce the observed relic density through a different mechanism (canonical WIMP-like freeze-out with resonance enhancement)
- The current calibrated 1/⟨σv⟩ mapping is a known limitation that should be replaced, but it does NOT make the +8.10 log-unit gain invalid

**Action 1.1 (WIP branch, KIV for T100):** Integrate Boltzmann solver (micrOMEGAs or custom `scipy.integrate.odeint`) for the multi-resonance relic density calculation.

- Add strict penalty if Ω_χ h² > 0.12 (Planck 2018 + ACTPol)
- Expected effort: 2-3 weeks
- Risk: medium (new external code, changes likelihood structure)

### Phase 2 — Upgrade SPARC to hierarchical forward-model (WIP-branch actionable)

The reviewer's critique of the SPARC "saturation score" applies directly to the WIP branch. The current 115/127 = 90.6% pass count is a *lower bound*, not a tight constraint.

**Action 2.1 (WIP branch, KIV for T102):** Replace the SPARC per-channel likelihood with a hierarchical Bayesian forward-model (similar to the `sidmkit` methodology).

- Marginalize over galaxy-specific nuisance parameters (distance, inclination, stellar mass-to-light ratio Υ_*)
- Globally fit the dark matter halo profile (cusp vs. core) with the multi-resonance σ/m(v)
- Expected effort: 1-2 months
- Risk: medium-high (touches every Phase 33 sub-analysis)

### Phase 3 — Quantum scattering precision (WIP-branch highest value)

The reviewer's partial-wave analysis recommendation is the **most directly relevant** to the WIP branch's known limitations. Currently:

- σ/m(v) uses semi-classical Yukawa transfer cross-section (Born approximation)
- This is accurate for weak coupling but breaks down near Breit-Wigner resonances
- Resonant Sommerfeld enhancement could produce σ/m ∝ v^-4 at low v
- This could reduce the σ/m peak height needed for Cloud-9 by a factor of a few
- Narrowing the dSph tension (currently 38×) would follow naturally

**Action 3.1 (WIP branch, KIV for T101):** Replace the analytic Yukawa transfer cross-section with a numerical partial-wave solver.

- Compute phase shifts δ_l up to high l for the composite-state scattering
- Derive the exact quantum-mechanical σ_T(v) at each velocity
- Re-fit Phase 32 (Cloud-9 anchor), Phase 33d (SPARC), Phase 36 (dSph) with the new σ/m
- Expected effort: 2-3 months
- Risk: high (touches the core σ/m model; all Phase 32–54 results would need re-running)

### Phase 4 — Dark QCD realism (low priority for WIP branch)

The reviewer's KSFR-relation critique applies to the master branch. The WIP branch already uses 5 UV embeddings (clockwork q^k, Secluded U(1) n², power-law, integer, dark-SU(N_c)) — the KSFR relations are not directly used in the σ/m(v) calculation.

**Action 4.1 (KIV, low priority):** Map the dark confinement scale Λ_d and dark pion mass m_π_d using actual lattice scaling laws for SU(N_c) with varying N_f.

- Use LSD Collaboration data (Brower et al. 2024/2025) for SU(N_c) gauge theories
- Dynamically reject parameter spaces that push the dark sector into a non-confining or conformal regime
- Expected effort: 1-2 months
- Risk: low

### Phase 5 — Multi-messenger sanity checks (background)

The reviewer's recommendations for JWST strong-lensing, DESI BAO, neutrino floor, etc. are **future scope**, not blockers for Paper v1.8.

- These are out of scope for the current WIP branch (which focuses on Cloud-9 + SPARC + JVAS)
- They would naturally appear in follow-up work after Paper v1.8 is published

---

## Suggested T-round roadmap

| Round | Action | Effort | Risk | Recommended timing |
|---|---|---|---|---|
| **T100** | Integrate Boltzmann solver for relic density | 2-3 weeks | medium | After Paper v1.8 submitted |
| **T101** | Partial-wave / numerical Schrödinger σ/m(v) | 2-3 months | high | After Paper v1.8 submitted; before v2.0 |
| **T102** | Hierarchical SPARC forward-model | 1-2 months | medium-high | After T101 (needs new σ/m first) |
| **T103** | Lattice-informed dark QCD scaling | 1-2 months | low | Optional; for v3.0 paper |

---

## What Paper v1.8 already acknowledges

Paper v1.8 §8.4 "Limitations and Future Work" explicitly documents:

1. Semi-classical Yukawa transfer cross-section (corresponds to T101)
2. Per-galaxy SPARC hierarchical likelihood not yet implemented (corresponds to T102)
3. Boltzmann solver for relic density not yet integrated (corresponds to T100)

Paper v1.8 §8.5 "Honest mixed verdict" closes with: "The combination of these is appropriate for a 'mixed-verdict' paper at PRD / JCAP / JHEP, not for a strong-claim discovery paper."

This framing is consistent with the reviewer's verdict that the project is currently "a masterclass in computational honesty but a failure as a predictive physical theory" — the WIP branch is honest about its limitations and frames the work as appropriate for a mixed-verdict paper, not as a discovery paper.

---

## The "fundamental fault" question (revisited)

User asked earlier: "what i worry is whether it implies a fundamental fault in our model framework, is it so?"

Answer (still valid): **No fundamental fault.** The multi-resonance architecture is physically meaningful — σ/m matches constraints at velocities that matter (v=41 for Cloud-9, v=100 for SPARC), and the BW-tail behavior is acknowledged in paper.

The reviewer's critique confirms this: the WIP branch's limitations are **scope of work** (semi-classical Yukawa, per-channel likelihood, calibrated relic density), not **fundamental framework errors**. Each of these can be addressed in turn without invalidating the core multi-resonance architecture.

The master branch's ε ~ 10^-37 is a more serious problem, but that's a separate evolution line and not the WIP branch's concern.

---

## Conclusion

KIV. The T100–T103 roadmap is **post-paper scope**, not Paper v1.8 scope. Paper v1.8 already documents the relevant limitations honestly in §8.4 and frames the work appropriately in §8.5. The next actionable step is to **submit Paper v1.8** (or later revision) and then execute T100–T103 as a post-publication roadmap.

**No further action required for Paper v1.8.**