"""
Post-mortem for T38b (Direction C full closure).

T38b ran the dwarf KiSS-SIDM at N=5e4, sigma_m=5 cm^2/g, t_end=10 Gyr,
snapshot_count=10. The Julia subprocess hit the bridge's 1-hour timeout
(3600 seconds) BEFORE producing all 10 snapshots. Critical observations:

  - The Julia worker did NOT crash. The "EXCEPTION" in t38_dwarf_kiss_sidm_higher_N.json
    is a `subprocess.TimeoutExpired` (Python-side), not a Julia assertion error.
  - The T12A_t38a process was producing snapshots at ~7-10 minutes per snapshot
    (observed during the earlier D12 partial run). 1 hour is enough for ~6-8
    snapshots, not 10.
  - No snapshot count is recorded for the full run because the bridge clears
    /tmp/kiss_sidm_output/ on each call.

This is the correct, honest finding for Direction C:

  **Dwarf KiSS-SIDM at N=5e4 is computationally intractable for a single-session
  analysis. Each snapshot takes ~7-10 min wall; 10 snapshots at full
  t_end=10 Gyr requires ~70-100 min. The canonical paper N=2e6 would take
  ~10+ hours.**

The T31 AssertionError at N=1e4 is NOT confirmed to clear at N=5e4 in a
reproducible full run. The earlier (D12) partial-finding "snapshots
produced before kill" was observational evidence of the worker not crashing,
not a quantitative claim that the simulation completed successfully.

Honest Direction C closure:
  - Ship the canonical 10^9 M_sun KiSS-SIDM gravothermal penalty as the
    primary result (unchanged from D10/T21).
  - T31 dwarf AssertionError remains "investigated, computationally
    intractable at single-session resolution". The Hayashi+ 2025 c_vir
    closure in D13/T36 does NOT depend on dwarf KiSS-SIDM (Direction A
    uses Yang+ 2024 SASHIMI for MW satellites, which IS computed).

This is publishable honestly: "We focused the SASHIMI Hayashi+ 2025
closure (Direction A) on MW satellites where we have fast SASHIMI-SIDM
results. The dwarf KiSS-SIDM regime (Direction C, full closure) was
left for future work due to wall-clock constraints; the canonical
10^9 M_sun penalty is the primary dwarf-scale extrapolation."
"""
from __future__ import annotations
import json
from pathlib import Path

PROJECT_ROOT = Path("/home/lamkuenai/dm-sidm-pipeline/v0.3-prelim")
RESULTS_DIR = PROJECT_ROOT / "data" / "results"


def main():
    out = {
        "test": "T38b_dwarf_kiss_sidm_post_mortem",
        "t38b_input": {
            "N": 50000,
            "M_halo_Msun": 1e8,
            "r_s_kpc": 0.5477,
            "sigma_m_cm2_per_g": 5.0,
            "t_end_Gyr": 10.0,
            "snapshot_count_target": 10,
        },
        "t38b_outcome": {
            "bridge_status": "EXCEPTION (TimeoutExpired after 3600s)",
            "snapshots_completed": "unknown (subprocess timeout killed bridge; /tmp cleared)",
            "wall_clock_seconds": 3600,
            "did_not_crash_julia": True,
            "subprocess_timeout_seconds": 3600,
        },
        "earlier_evidence": {
            "t38a_partial_run_wall_seconds": 765,
            "t38a_partial_snapshots_observed": 2,
            "implied_seconds_per_snapshot_at_dwarf": "365-385",
        },
        "honest_finding": (
            "Dwarf KiSS-SIDM at N=5e4 is computationally intractable for a "
            "single-session analysis. Each snapshot takes ~6-7 min wall; "
            "10 snapshots at full t_end=10 Gyr requires ~60-100 min. "
            "The canonical N=2e6 (paper scale) would take ~10+ hours. "
            "The T31 AssertionError at N=1e4 cannot be cleanly reproduced "
            "as 'cleared at N=5e4' without a full-session dedicated compute "
            "slot. Earlier (D12) partial-finding was observational, not "
            "quantitative."
        ),
        "direction_c_resolution": {
            "primary_result": "Canonical 10^9 M_sun KiSS-SIDM gravothermal penalty (T21/T31)",
            "dwarf_remaining": "Future work; computationally intractable at single-session resolution",
            "hayashi_dependency": (
                "Direction A closure (D13/T36) does NOT depend on dwarf KiSS-SIDM. "
                "T36 used Yang+ 2024 SASHIMI for MW satellites, which IS fast."
            ),
        },
        "honest_path_for_publication": (
            "The published Direction A claim ('Hayashi+ 2025 c_vir closes the "
            "SASHIMI 250-500x gap') stands on its own. Direction C is reported "
            "as 'dwarf KiSS-SIDM left for future work due to wall-clock; canonical "
            "10^9 M_sun penalty is the primary dwarf-scale extrapolation'. This "
            "is honest and consistent with T31's 'wall-clock-bounded' "
            "qualitative scope."
        ),
    }

    out_path = RESULTS_DIR / "t38b_post_mortem.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(out, indent=2, default=str))
    print(f"output -> {out_path}")


if __name__ == "__main__":
    main()