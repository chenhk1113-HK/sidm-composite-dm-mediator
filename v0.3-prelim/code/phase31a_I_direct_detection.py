"""
Phase 31a Test I — Direct-detection / beam-dump consistency

Per consider8.docx: With m_chi = 6 GeV and a light mediator (~8 MeV),
the model makes concrete predictions for low-threshold DD experiments
and beam-dump searches. Even if kinetic mixing is tiny, the parameter
space can be checked against existing limits.

Method:
- Compute sigma_SI from kinetic mixing epsilon
- Compare to LZ, XENONnT, PandaX limits
- Check beam-dump reach for epsilon in [10^-5, 10^-3]
"""
from __future__ import annotations
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from t62_lz_direct_detection import sigma_DM_n, LZ_limit, M_NUCLEON_GEV, HBAR_C_GEV_CM

RESULTS_DIR = Path(__file__).resolve().parent.parent / "data" / "results"


def main():
    # Load Phase 29 results
    phase29_path = RESULTS_DIR / "phase29_full_resonant_joint_fit.json"
    with open(phase29_path) as f:
        phase29 = json.load(f)

    med = phase29["posterior_medians"]
    m_chi = med["m_chi_GeV"]["p50"]  # GeV
    m_phi_MeV = med["m_phi_MeV"]["p50"]  # MeV
    m_phi_GeV = m_phi_MeV / 1000.0

    print("=" * 70)
    print("TEST I — Direct-detection / beam-dump consistency")
    print("=" * 70)
    print()
    print(f"Phase 29 posterior median: m_chi = {m_chi:.2f} GeV, m_phi = {m_phi_MeV:.2f} MeV")
    print()

    # LZ limit at m_chi = 6 GeV
    lz_limit = LZ_limit(m_chi)
    print(f"LZ upper limit at m_chi = {m_chi:.2f} GeV: {lz_limit:.2e} cm^2")
    print()

    # Compute sigma_DM_n for various epsilon
    print(f"{'epsilon':>10}  {'sigma_DM_n (cm^2)':>18}  {'Below LZ?':>10}")
    print("-" * 50)
    eps_values = [1e-7, 1e-6, 1e-5, 1e-4, 1e-3, 1e-2]
    max_allowed_eps = None
    for eps in eps_values:
        sigma = sigma_DM_n(m_chi, m_phi_GeV, eps)
        below = sigma < lz_limit
        print(f"{eps:10.0e}  {sigma:18.4e}  {'YES' if below else 'NO':>10}")
        if below and max_allowed_eps is None:
            max_allowed_eps = eps

    print()

    # Find max epsilon that satisfies LZ
    print("Finding max epsilon that satisfies LZ:")
    for eps in [1e-5, 1e-4, 1e-3]:
        sigma = sigma_DM_n(m_chi, m_phi_GeV, eps)
        below = sigma < lz_limit
        print(f"  epsilon = {eps:.0e}: sigma = {sigma:.4e} cm^2, {'OK' if below else 'EXCLUDED'}")
    print()

    # Beam-dump reach (NA64, LDMX)
    # For m_phi < 100 MeV, beam dumps constrain epsilon ~ 10^-5 to 10^-3
    # depending on coupling structure
    print(f"Beam-dump reach for m_phi = {m_phi_MeV:.2f} MeV:")
    print(f"  NA64 (visible decay): epsilon < ~1e-5 to 1e-3 (depends on mass)")
    print(f"  LDMX (missing energy): epsilon < ~1e-4")
    print(f"  If epsilon < 1e-5: model evades all DD + beam-dump constraints")
    print()

    # For the resonant SIDM model, we use asymmetric DM (no annihilation), so:
    # - DD constraint: epsilon must be small enough to evade LZ
    # - Beam-dump constraint: epsilon must be small enough to evade NA64/LDMX
    # Our model doesn't predict epsilon — it's a free parameter

    # What's the smallest epsilon consistent with thermalization?
    # For asymmetric DM, epsilon can be 0 (no kinetic mixing needed)
    print("For asymmetric DM (Phase 22 switch):")
    print("  epsilon can be 0 (no coupling to SM needed)")
    print("  DD sigma = 0, beam-dump constraints trivially satisfied")
    print()

    # Verdict
    print("VERDICT:")
    # Find max epsilon that satisfies LZ (sigma < LZ_limit)
    # sigma = eps^2 * constant, so eps_max = sqrt(LZ_limit / constant)
    sigma_constant = sigma_DM_n(m_chi, m_phi_GeV, 1.0)  # sigma at eps=1
    eps_max = np.sqrt(lz_limit / sigma_constant)
    print(f"  Max epsilon satisfying LZ: {eps_max:.2e}")
    print(f"  LZ limit: {lz_limit:.4e} cm^2")
    print(f"  sigma_DM_n at epsilon=1e-3: {sigma_DM_n(m_chi, m_phi_GeV, 1e-3):.4e} cm^2")
    print()

    # For asymmetric DM, epsilon can be 0 — model trivially evades DD
    # If epsilon must be small (< eps_max), it's a constraint but not exclusion
    if eps_max > 1e-10:
        verdict = "EVADES_DD_LIMITS"
        msg = f"Model evades DD limits if epsilon < {eps_max:.2e} (consistent with asymmetric DM)"
    else:
        verdict = "EXCLUDED_BY_DD"
        msg = "Even with epsilon -> 0, model is in tension with DD"

    print(f"  {verdict}: {msg}")

    out = {
        "test": "Phase31a_I_direct_detection",
        "median_params": {
            "m_chi_GeV": m_chi,
            "m_phi_MeV": m_phi_MeV,
            "m_phi_GeV": m_phi_GeV,
        },
        "lz_limit_cm2": float(lz_limit),
        "sigma_DM_n_scan": {
            f"epsilon_{eps:.0e}": float(sigma_DM_n(m_chi, m_phi_GeV, eps))
            for eps in eps_values
        },
        "verdict": verdict,
    }

    out_path = RESULTS_DIR / "phase31a_I_direct_detection.json"
    with open(out_path, "w") as f:
        json.dump(out, f, indent=2, default=float)
    print(f"\nResults written to: {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())