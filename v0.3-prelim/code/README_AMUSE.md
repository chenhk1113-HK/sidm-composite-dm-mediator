# AMUSE bullet-dwarf simulation pipeline (v0.3-prelim)

**Status:** Working pipeline. Reproducibility across seeds verified at σ/m_peak = 3.07 cm²/g (within ±0.05 nats n_bound variance). Sigma/m_peak is a **softening-resolution threshold**, not a half-disruption measurement — see docs.

**Last validated:** 2026-09-12 (`67b92a5`)
**Author:** Hermes + MiniMax M3 (joint authoring session)
**Python required:** 3.10 (WSL Ubuntu 26.04 repos don't have 3.10 — use `uv`)

---

## TL;DR — what these scripts do

A 4-script pipeline that runs an AMUSE-ph4 N-body simulation of two dwarf-galaxy halos colliding at v=358 km/s (the NGC 1052 trail velocity), sweeps σ/m across {0.1, 0.5, 1.0, 2.0, 5.0, 10.0} cm²/g, and fits a sigmoid to extract σ/m_peak. A SASHIMI-SIDM benchmark step checks whether AMUSE's softening can resolve the predicted SIDM core.

**Critical caveat (per SASHIMI benchmark):** The "σ/m_peak" is a **transient pre-disruption snapshot**, not an asymptotic half-disruption measurement. By t > 350 Myr, all halos fully disrupt regardless of σ/m (because N=1024 is too low for realistic gravothermal evolution). The peak also coincides with the SASHIMI-predicted σ/m at which AMUSE first sees a SIDM core (r_core > 5× softening). See `v0.3-prelim/docs/AMUSE_FRESH_RUN_WITH_SASHIMI_2026_09_12.md` for full benchmark.

---

## Files in this pipeline

| File | Purpose | Wall time |
|---|---|---|
| `amuse_bullet_dwarf.py` | Core simulation: ph4 N-body + uniform-Gaussian SIDM scattering kernel. Defines `run_collision(sigma_m, seed)`. | ~310 s per σ/m |
| `amuse_simulation_benchmark.py` | 3 sanity-check benchmarks (static halo, collisionless collision, σ/m=0.1 collision). | ~5 min total |
| `amuse_rerun_with_sashimi.py` | Full 8-σ sweep + SASHIMI benchmark (abandoned in favor of focused rerun; kept for reference). | ~80 min (don't run) |
| `amuse_focused_rerun.py` | **Recommended rerun driver.** 5-σ sweep × 400 Myr × multi-time-slice extraction + SASHIMI benchmark. | ~7 min total |
| `ch27_peak_from_amuse.py` | Post-processing: fits sigmoid to surviving-fraction curve, outputs σ/m_peak with time-slice sensitivity table + SASHIMI resolution check. | ~10 s |

**Output JSON files** (all written to `v0.3-prelim/data/results/`):
- `amuse_bullet_dwarf_calibration_2026_09_12.json` — seed=42 baseline (N=1024, 2 Gyr)
- `amuse_focused_rerun_with_sashimi_2026_09_12.json` — seed=20260912, multi-time-slice + SASHIMI (note: JSON serialization was buggy; partial save)
- `amuse_seed_comparison_2026_09_12.json` — side-by-side comparison of seed=42 vs seed=20260912
- `amuse_simulation_benchmark_2026_09_12.json` — 3-benchmark output
- `ch27_sigma_m_peak_from_amuse_2026_09_12.json` — final σ/m_peak fit + sensitivity table + SASHIMI resolution check

---

## How to run

### Prerequisites

1. **AMUSE Python 3.10 venv at `~/.local/amuse-py310-venv/`** (per Hermes skill `amuse-install-recipe`):
   ```bash
   uv venv ~/.local/amuse-py310-venv --python 3.10
   source ~/.local/amuse-py310-venv/bin/activate
   uv pip install amuse-framework
   ```

2. **ph4 N-body worker compiled** — included with amuse-framework, but MPI may not be available (warning is OK; falls back to sockets).

3. **Project mounted in WSL** at `/mnt/c/Users/lamkuenai/projects/sidm-composite-dm-mediator/` (default for Windows users).

### Quick run (recommended)

```bash
wsl -- bash -c "/home/lamkuenai/.local/amuse-py310-venv/bin/python \
    /mnt/c/Users/lamkuenai/projects/sidm-composite-dm-mediator/v0.3-prelim/code/amuse_focused_rerun.py 2>&1"
```

Wall time: ~7 minutes for the full 5-σ × 400 Myr sweep + SASHIMI benchmark.

### Full sweep (deprecated)

`amuse_rerun_with_sashimi.py` runs an 8-σ × 2 Gyr sweep that takes ~80 minutes and produces the same conclusions as the focused rerun. **Don't run unless you specifically need the 8-σ data.**

### Post-processing (Windows-side, no AMUSE needed)

```bash
cd /c/Users/lamkuenai/projects/sidm-composite-dm-mediator
/c/Python314/python.exe v0.3-prelim/code/ch27_peak_from_amuse.py
```

Outputs:
- σ/m_peak at primary time slice (default t=300 Myr)
- Multi-time-slice sensitivity table at t=200, 250, 300, 320, 340 Myr
- SASHIMI resolution check (r_core vs AMUSE softening)
- **Critical warning** if peak is at the resolution threshold

---

## Honest caveats (from SASHIMI benchmark)

These should be in any publication using these results:

1. **N=1024 is ~100× below publication-grade** (Yang+ 2024 SASHIMI requires N≥10⁵).
2. **SIDM kernel is uniform Gaussian velocity perturbation**, not pairwise Rutherford-like scattering.
3. **Head-on collision only** (b=0). Real NGC 1052 trail may have non-zero impact parameter.
4. **No baryonic physics** — gas stripping is post-hoc.
5. **σ/m_peak is time-slice dependent** — slides from ~6 cm²/g at t=200 Myr to 1.2 cm²/g at t=320 Myr.
6. **By t > 350 Myr, all halos fully disrupt** regardless of σ/m — the fit captures the transient window only.
7. **σ/m_peak ≈ 3 cm²/g is at the resolution threshold** — SASHIMI predicts this is exactly where AMUSE first sees a SIDM core. NOT a measurement of physical σ/m at v=358 km/s.

---

## What future work would change

- **N=10⁵ particles** (~10× wall time → 70 minutes): would let gravothermal evolution play out realistically. Currently we hit the "all halos disrupt" wall at t > 350 Myr.
- **Pairwise Rutherford-like SIDM scattering**: replace uniform Gaussian velocity perturbation with proper pairwise scattering kernel. Would let AMUSE measure σ/m_peak as a physics quantity, not a resolution threshold.
- **Non-zero impact parameter**: the head-on (b=0) setup is unrealistic. Real NGC 1052 trail probably has b ~ 10-50 kpc.
- **Baryonic physics**: gas stripping is the actual mechanism creating DM-free UDGs. Without it, we're missing half the story.
- **Time-since-collision match**: the current t=300 Myr is heuristic. A real study would match the time slice to the inferred NGC 1052 trail age (probably 1-2 Gyr).

These would all be substantive work (~weeks to months, depending on N).

---

## References

- Yang+Yu 2024 (arXiv:2403.16633): SASHIMI-SIDM parametric model — `v0.3-prelim/code/sashimi_parametric.py`
- AMUSE-framework 2024.6.0 + ph4 (Hut-Makino 4th-order Hermite N-body): `pip install amuse-framework`
- `v0.3-prelim/docs/AMUSE_FRESH_RUN_WITH_SASHIMI_2026_09_12.md` — full SASHIMI benchmark writeup
- `v0.3-prelim/docs/AMUSE_SIMULATION_BENCHMARK_2026_09_12.md` — sanity-check benchmarks
- `v0.3-prelim/docs/CH04_TENSION_RESOLUTION_2026_09_12.md` — the ch04 width fix (separate from AMUSE but referenced for context)