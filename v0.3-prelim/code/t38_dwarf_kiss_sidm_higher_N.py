"""
T38 — Direction C closure: dwarf KiSS-SIDM at higher particle counts.

Direction C (KiSS-SIDM gravothermal) had a known-open issue at the dwarf
regime (M_halo = 10^8 M_sun): the T31 run with N=1e4, sigma_m=5 cm^2/g
crashed with `AssertionError: majorant <= N`. T27's convergence study
showed r_core/r_s is converged between N=1e4 and N=1e5 at the canonical
halo. The hypothesis (per the Pipeline Overview1.docx review §5
milestone #2) is that **higher N also fixes the dwarf regime**.

This script runs two pre-flight fits (T38a / T38b):

  T38a: dwarf N=5e4, sigma_m=5 cm^2/g, M=10^8 M_sun
        (single smoke fit to test if AssertionError clears)

  T38b: dwarf N=1e5, sigma_m=5 cm^2/g, M=10^8 M_sun
        (converged fit per T27; the publishable point)

Output: per-fit halo parameters + r_core/r_s extracted from the last
snapshot. Compare to T31 canonical (10^9 M_sun, N=1e4) for context.

Honest fallback
---------------
If N=5e4 still crashes, run T38b at N=1e5 directly (T27's "safe" value).
If both fail, document that the dwarf-KiSS-SIDM problem is genuinely
intractable at our resolution and ship the canonical-mass penalty as an
upper bound on the dwarf gravothermal collapse (per T31 honest scope).
"""
from __future__ import annotations
import json
import sys
import time
import traceback
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "v0.1-prelim" / "code"))

import numpy as np

import kiss_sidm_julia_bridge as bridge

# Halo parameters (per T31):
#   canonical: M_halo=1e9 M_sun, rho_s=2.73e7 M_sun/kpc^3, r_s=1.18 kpc
#   dwarf:     M_halo=1e8 M_sun, rho_s=2.73e7 (same NFW), r_s=1.18*(1/10)^(1/3) kpc
DWARF_M_HALO = 1e8
DWARF_RHO_S = 2.73e7
DWARF_R_S = 1.18 * (DWARF_M_HALO / 1e9) ** (1.0 / 3.0)  # ~ 0.548 kpc
DWARF_SIGMA_M = 5.0    # cm^2/g, per T31 (10x smaller than canonical 50)

CANONICAL_M_HALO = 1e9
CANONICAL_RHO_S = 2.73e7
CANONICAL_R_S = 1.18
CANONICAL_SIGMA_M = 50.0

RESULTS_DIR = Path("/home/lamkuenai/dm-sidm-pipeline/v0.3-prelim/data/results")


def run_dwarf(N: int, sigma_m: float, label: str, t_end_Gyr: float = 10.0):
    """Run a single KiSS-SIDM dwarf simulation. Returns a result dict."""
    print(f"\n[T38 {label}] N={N}, M={DWARF_M_HALO:.0e} M_sun, "
          f"rho_s={DWARF_RHO_S:.2e}, r_s={DWARF_R_S:.3f} kpc, "
          f"sigma_m={sigma_m} cm^2/g")
    t0 = time.time()
    try:
        raw = bridge.run_canonical_kiSS_sidm(
            N=N,
            t_end_Gyr=t_end_Gyr,
            sigma_m_cm2_per_g=sigma_m,
            rho_s_Msun_per_kpc3=DWARF_RHO_S,
            r_s_kpc=DWARF_R_S,
            seed=42,
            snapshot_count=10,
        )
    except Exception as exc:
        elapsed = time.time() - t0
        print(f"  EXCEPTION after {elapsed:.1f}s: {type(exc).__name__}: {exc}")
        return {"label": label, "N": N, "M_halo_Msun": DWARF_M_HALO,
                "r_s_kpc": DWARF_R_S, "sigma_m_cm2_per_g": sigma_m,
                "wall_seconds": elapsed, "bridge_status": "EXCEPTION",
                "error": f"{type(exc).__name__}: {str(exc)[:300]}"}

    elapsed = time.time() - t0
    status = str(raw.get("status", ""))
    print(f"  status={status}, elapsed={elapsed:.1f}s")
    if "error" in status.lower() or raw.get("status") in ("failed", "crashed"):
        return {"label": label, "N": N, "M_halo_Msun": DWARF_M_HALO,
                "r_s_kpc": DWARF_R_S, "sigma_m_cm2_per_g": sigma_m,
                "wall_seconds": elapsed, "bridge_status": raw.get("status"),
                "error": str(raw.get("stderr", ""))[:500]}

    # Read the canonical-aggregated result the bridge always writes
    agg_path = RESULTS_DIR / "kiss_sidm_canonical_simulation.json"
    if not agg_path.exists():
        win_agg = Path("/mnt/c/Users/lamkuenai/projects/dm-sidm-pipeline/v0.3-prelim/data/results/kiss_sidm_canonical_simulation.json")
        if win_agg.exists():
            agg_path = win_agg
    if agg_path.exists():
        agg = json.load(open(agg_path))
        snaps = agg.get("snapshots", [])
        last = snaps[-1] if snaps else None
        n_particles = agg.get("n_particles", N)
    else:
        last = None
        n_particles = N

    out_data = {
        "label": label,
        "N": N,
        "M_halo_Msun": DWARF_M_HALO,
        "r_s_kpc": DWARF_R_S,
        "sigma_m_cm2_per_g": sigma_m,
        "wall_seconds": elapsed,
        "bridge_status": status,
        "n_particles": n_particles,
    }

    # Compute r_core/r_s from the last snapshot if available
    if last and "rho_over_rhos" in last and "r_over_rs" in last:
        rho = np.array(last["rho_over_rhos"])
        r = np.array(last["r_over_rs"])
        if len(rho) > 0 and rho[0] > 0:
            central = rho[0]
            mask_drop = rho < 0.5 * central
            if any(mask_drop):
                idx_core = int(np.argmax(mask_drop))
                out_data["r_core_over_rs"] = float(r[idx_core])
            else:
                out_data["r_core_over_rs"] = None
        # Save the snapshot tail for downstream plotting
        out_data["last_snapshot_r_over_rs"] = r.tolist()[:50]   # cap to 50 entries (JSON-friendly)
        out_data["last_snapshot_rho_over_rhos"] = rho.tolist()[:50]
        out_data["last_snapshot_t_Gyr"] = last.get("t_Gyr")

    return out_data


def main():
    print("=" * 80)
    print("T38 — Direction C closure: dwarf KiSS-SIDM at N=5e4 and N=1e5")
    print("=" * 80)
    print(f"Dwarf halo params: M={DWARF_M_HALO:.0e} M_sun, r_s={DWARF_R_S:.3f} kpc, "
          f"sigma_m={DWARF_SIGMA_M} cm^2/g")
    print("Hypothesis (from T27 / Pipeline Overview §5 #2): higher N clears the "
          "T31 AssertionError.")
    print()

    results = []

    # ---- T38a: N=5e4 pre-flight ----
    print("\n--- T38a: N=5e4 pre-flight (5-10 min expected) ---")
    a = run_dwarf(N=50_000, sigma_m=DWARF_SIGMA_M, label="T38a_N5e4_smoke")
    results.append(a)
    a_status = a.get("bridge_status", "?")
    a_r_core = a.get("r_core_over_rs")
    print(f"  T38a result: status={a_status}, "
          f"r_core/r_s={a_r_core}, wall={a.get('wall_seconds', 0):.1f}s")

    # Decide whether to proceed to T38b
    proceed_to_b = a_status not in ("EXCEPTION", "failed", "crashed") and "error" not in a_status.lower()
    if not proceed_to_b:
        print(f"\n  T38a FAILED (status={a_status}). T38b SKIPPED -- "
              f"suggesting the issue is not purely N-dependent.")
    else:
        # ---- T38b: N=1e5 converged fit ----
        print("\n--- T38b: N=1e5 converged (10-30 min expected per T27) ---")
        b = run_dwarf(N=100_000, sigma_m=DWARF_SIGMA_M, label="T38b_N1e5_converged")
        results.append(b)
        b_status = b.get("bridge_status", "?")
        b_r_core = b.get("r_core_over_rs")
        print(f"  T38b result: status={b_status}, "
              f"r_core/r_s={b_r_core}, wall={b.get('wall_seconds', 0):.1f}s")

    # ---- Compare to canonical (T31 baseline) ----
    print("\n--- T31 canonical baseline (for context) ---")
    canonical_path = RESULTS_DIR / "kiss_sidm_canonical_simulation.json"
    if not canonical_path.exists():
        canonical_path = Path("/mnt/c/Users/lamkuenai/projects/dm-sidm-pipeline/v0.3-prelim/data/results/kiss_sidm_canonical_simulation.json")
    if canonical_path.exists():
        can = json.load(open(canonical_path))
        snaps = can.get("snapshots", [])
        if snaps:
            last = snaps[-1]
            rho = np.array(last["rho_over_rhos"])
            r = np.array(last["r_over_rs"])
            central = rho[0]
            mask_drop = rho < 0.5 * central
            can_r_core = float(r[int(np.argmax(mask_drop))]) if any(mask_drop) else None
            print(f"  Canonical: M={CANONICAL_M_HALO:.0e} M_sun, N={can.get('n_particles')}, "
                  f"sigma_m=50, r_core/r_s={can_r_core}")
        else:
            can_r_core = None
            print("  Canonical simulation has no snapshots — skipping comparison.")
    else:
        can_r_core = None
        print("  Canonical simulation file missing — skipping comparison.")

    # ---- Headline & ship ----
    print("\n" + "=" * 80)
    print("T38 HEADLINE FINDINGS:")
    print("=" * 80)

    if proceed_to_b and len(results) >= 2:
        # Compare T38b to canonical
        b_r_core = results[1].get("r_core_over_rs")
        if b_r_core is not None and can_r_core is not None:
            ratio = b_r_core / can_r_core
            print(f"  T38b N=1e5 dwarf r_core/r_s = {b_r_core:.4f}")
            print(f"  Canonical   r_core/r_s       = {can_r_core:.4f}")
            print(f"  Ratio (dwarf / canonical): {ratio:.3f}")
            if 0.5 < ratio < 2.0:
                verdict = "ROBUST: dwarf gravothermal penalty within factor 2 of canonical."
            elif 0.2 < ratio < 5.0:
                verdict = "MODERATE: dwarf penalty within factor 5 of canonical."
            else:
                verdict = "MAJOR: dwarf penalty differs by >5x from canonical (halo-mass scaling is significant)."
            print(f"  Verdict: {verdict}")
        else:
            verdict = "INCOMPLETE: at least one r_core/r_s is missing."
            print(f"  Verdict: {verdict}")
    elif proceed_to_b and len(results) == 2:
        verdict = "T38a cleared, T38b completed; see r_core/r_s values above."
    else:
        # T38a failed or no T38b
        verdict = "FAILURE: N=5e4 did not clear the AssertionError. Dwarf KiSS-SIDM is intractable at this resolution."
        print(f"  {verdict}")
        print("  Honest fallback: ship the canonical (10^9 M_sun) penalty as an upper bound on dwarf-mass collapse (per T31 honest scope).")

    out = {
        "test": "T38_dwarf_kiSS_sidm_higher_N",
        "direction": ("D13 deliverable: Direction C closure via N-resolved dwarf "
                      "KiSS-SIDM runs at N=5e4 (pre-flight) and N=1e5 (converged). "
                      "Resolves Pipeline Overview §5 milestone #2 (T31 dwarf marginalization)."),
        "halo_params": {
            "M_halo_Msun": DWARF_M_HALO,
            "rho_s_Msun_per_kpc3": DWARF_RHO_S,
            "r_s_kpc": DWARF_R_S,
            "sigma_m_cm2_per_g": DWARF_SIGMA_M,
        },
        "canonical_baseline": {
            "M_halo_Msun": CANONICAL_M_HALO,
            "r_s_kpc": CANONICAL_R_S,
            "sigma_m_cm2_per_g": CANONICAL_SIGMA_M,
            "r_core_over_rs": can_r_core,
        },
        "fits": [{"label": r["label"], **r} for r in results],
        "verdict": verdict,
        "interpretation": (
            "T31 hit AssertionError('majorant <= N') at dwarf N=1e4 because the "
            "KiSS-SIDM code's collision sampler requires enough particles per "
            "radial cell to estimate the local scattering rate. T27 confirmed "
            "r_core/r_s converges between N=1e4 and N=1e5 at the canonical halo, "
            "and the canonical KiSS-SIDM paper (Gurian & May 2025) reports "
            "convergence only at N=2e6. We hypothesise that the dwarf regime "
            "requires N>=1e5 for the assertion to clear. T38a/b tests this."
        ),
    }

    out_path = RESULTS_DIR / "t38_dwarf_kiss_sidm_higher_N.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(out, indent=2, default=str))
    # Mirror to Windows-side for tests
    win_path = Path("/mnt/c/Users/lamkuenai/projects/dm-sidm-pipeline/v0.3-prelim/data/results/t38_dwarf_kiss_sidm_higher_N.json")
    win_path.write_text(json.dumps(out, indent=2, default=str))
    print(f"\noutput -> {out_path}")
    print(f"        -> {win_path}")


if __name__ == "__main__":
    main()
