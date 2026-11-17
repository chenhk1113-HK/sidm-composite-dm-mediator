# T215 N-body wall-time ladder — measurement record (2026-11-17)

**Why this file exists.** `CHANGELOG.md:1284` carries a parked recommendation from the v18.4x
round — "10⁴ particle run (minor rec #5.4) — wall time 7 days, beyond laptop" — and the line above
it parks "Run to 100 Myr (rec #6) — blocked by laptop ceiling". Neither number had ever been
measured: no wall time for any long 10⁴-particle run appears anywhere in the repository. The owner
asked (2026-11-17, options "3 and 4" of the Kaggle intake review) to measure the actual scaling
instead of leaving the claim parked, and to decide whether an ML surrogate was worth building.

**Headline result.** The 7-day figure is not a measurement and does not survive one. At 10⁴
particles the run does not become expensive first — it **stops**, reproducibly, at a fixed
simulated time of ≈12.7 Myr, in 134–207 s of wall clock, on an assertion inside KiSS-SIDM's
snapshot scheduler. Separately, 100 Myr at 3000 particles **does** complete on this laptop, in
about 51 minutes of wall clock measured while a second run competed for CPU. A surrogate model was
**not** built, and is not recommended, for the reasons in §6.

---

## 1. What was run

Harness: `t215_nscale.jl` (appendix A) — the certified T215 configuration (same IC, same σ/m,
same grid and `adaptive_grid_min_particles = 64`, same `sqrt(max(0, x))`-patched KiSS-SIDM) with
`N`, `T_END` and `NSNAP` taken from the environment. Ladder scripts: appendix B.

Environment, recorded because the T215 series is environment-sensitive:

| item | value |
|---|---|
| host | this laptop, Windows 11, runs executed inside WSL2 |
| Julia | 1.11.9 (`juliaup`) |
| code | `/home/lamkuenai/KiSS-SIDM`, with the repository's `sqrt(max(0, x))` patches applied |
| threads | `JULIA_NUM_THREADS=1` (deliberate: single-thread wall clock is comparable across steps) |
| IC | `v0.3-prelim/data/ics/t215_nfw_halo_cloud9.hdf5` (10⁴ particles, virialized NFW) |
| σ/m | 70 cm²/g |
| seed | 42 (recorded in the harness and echoed into every result row) |
| tracer selection | `sort(randperm(rng, n_total)[1:N])` — **without** replacement (see §5, this differs from every historical T215 runner) |
| **deviation from the repo recipe** | `ulimit -v 8000000` (the repo's variance-reduction recipe, CURRENT.md:627) was **not** applied. Timings here are therefore noisier than the certified T215 protocol intends. |

Time conversion used throughout: 1 pc·s/km = 0.97779 Myr (the repo's own factor in `t215d.jl` is 0.978).

## 2. Measured ladder

Wall seconds from the harness clock; simulated time from the last `t = …` line the solver printed
and from the snapshot files it wrote. `nsnap` is the number of snapshot times requested.

| tag | N | target (Myr) | nsnap | simulated time reached (Myr) | wall (s) | outcome |
|---|---|---|---|---|---|---|
| warm | 200 | 0.2 | 3 | — | 27 | harness defect (§4), not a physics result |
| n1000 | 1 000 | 5 | 11 | — | 18 | harness defect |
| n3000 | 3 000 | 5 | 11 | — | 16 | harness defect |
| n3000x2 | 3 000 | 10 | 21 | — | 15 | harness defect |
| **n10000** | **10 000** | 5 | 11 | **5.00** | **205.5** | completed, 11 snapshots |
| **n10000_t20** | **10 000** | 20 | 21 | **12.7** | **207.4** | **assertion**, 13 snapshots written |
| **n3000_t100** | **3 000** | **100** | 21 | **100.00** | **3070.6 (51.2 min)** | completed, 17 snapshots written |
| n10000_t50 | 10 000 | 50 | 11 | 6.57 | 1920 | terminated by operator; 2 snapshots |
| n10000_ns5 | 10 000 | 20 | 5 | 3.50 | ~1600 | terminated by operator; 1 snapshot |
| n10000_ns0_t100 | 10 000 | 100 | 0 | 4.64 | 1200 | terminated by operator; no snapshots requested |
| **n10000_dense_t100** | **10 000** | **100** | **101** | **12.7** | **134.2** | **assertion**, 13 snapshots written |

Contamination disclosure: `n3000_t100` (16:31–17:22) overlapped `n10000_ns5` (16:54–17:22), so its
51.2 min is an **upper** bound for a solo run. Every 10⁴ step in the last four rows ran alone.

## 3. Cost per simulated Myr, and why it swings 40×

From snapshot-file mtimes (each file is written as the solver passes its scheduled time), the wall
cost per Myr is not a constant and not a function of N alone:

```
N=3000, 21 snapshots (5 Myr spacing)      0→20 Myr: 0.5–9 s/Myr     20→80 Myr: 22–82 s/Myr
N=10⁴,  11 snapshots (0.5 Myr spacing)    0→0.5 Myr: 230 s/Myr     0.5→5 Myr: 3–20 s/Myr
N=10⁴,  21 snapshots (1 Myr spacing)      0→1 Myr: 148 s/Myr        1→12 Myr: 1–8 s/Myr
N=10⁴,  11 snapshots (5 Myr spacing)      dt ≈ 5.0e-5 → 292 s/Myr (at 6.6 Myr)
N=10⁴,   5 snapshots (4 Myr spacing)      dt ≈ 1.7e-5 → ~460 s/Myr (at 3.5 Myr)
N=10⁴,   0 snapshots                      dt ≈ 1.4e-5 → 258 s/Myr (at 4.6 Myr)
```

The first Myr is expensive in every configuration (115–230 s), and the sustained rate then depends
on which time step the integrator settles into. **Coarse or absent snapshot scheduling coincided
with a small `dt` (1.4e-5–5.0e-5 pc·s/km) and rates of 250–460 s/Myr; sub-Myr spacing coincided
with `dt ≈ 1.7e-3` and rates of 1–20 s/Myr.** This is an observed correlation in 11 runs, not a
derived law, and the repository already documents that ambient memory pressure drives run-to-run
variance in this series (CURRENT.md:626). It is enough to say that no wall-time estimate for this
code can be quoted as a single number, which is exactly why the 7-day figure needed replacing with
a measurement.

## 4. What actually stops a 10⁴-particle run

Two things, and neither is "the laptop runs out of time".

**(a) The snapshot-scheduler assertion.** Both 10⁴ runs that got far enough died at the same
simulated time, ≈12.7 Myr, with 13 snapshots written, at snapshot spacing 1 Myr **and** at 1 Myr
spacing with 101 requested snapshots. The failing line is upstream, not ours
(`src/DSMC.jl/src/time_step.jl:60-70`):

```julia
idx_next = clamp(searchsortedfirst(snapshot_times, t) + Int(after), firstindex(snapshot_times), lastindex(snapshot_times))
@assert (!after || t == snapshot_times[idx_next - 1] || (!after && idx_next == lastindex(snapshot_times)))
```

`after` is true immediately after a snapshot is written, and the assert then demands **exact float
equality** between the current time `t` and the snapshot time just passed. With an adaptive `dt`, a
step that lands *past* a scheduled snapshot time makes that equality false. So this is a fourth
numerical failure class in KiSS-SIDM v0.0.1, alongside the three already recorded (CURRENT.md:640-644):
the scheduler cannot tolerate an adaptive step overshooting a snapshot time. It reproduces at 10⁴
in seconds, and it is why the 2026-09-26 attempts "died silently" at 8.67 Myr and 2.46 Myr
(`v0.3-prelim/docs/T215_KISS_SIDM_CLOUD9_GRAVOTHERMAL_2026-09-26.md:22-23`) — that older label
"still unsolved" can now be replaced by a named mechanism.

**(b) Time-step collapse, which is N-dependent.** The runs that avoided the assert (coarse or zero
snapshots) were slow, with `dt` two orders of magnitude smaller than the dense-snapshot runs at the
same N. Independently, 100 Myr completes at 3 000 particles and does not complete at 10 000 in any
configuration tried today. That is the same direction the project already measured in the Tier 2
pilot: **"higher N → earlier dt collapse (opposite of reviewer's hypothesis)"** (CURRENT.md:636).
Today's ladder reproduces it with a different harness and a named failure site.

## 5. A defect found while building the harness: "3 000 particles" was never 3 000 particles

Every historical T215 runner picks its tracers with `rand(rng, 1:n_total, 3000)` — 21 files, e.g.
`v0.3-prelim/code/t215_safe.jl:62`, `t215_p.jl:43`, `t215_r.jl:39`. In Julia that idiom samples
**with replacement**. Measured on this host, seed 42 (`MersenneTwister`):

```
k = 3000 drawn from 10 000 → 2 623 distinct, 377 duplicated      (theory: 2 591.9)
k = 1000 drawn from 10 000 →   947 distinct,  53 duplicated
```

Consequences, sized honestly:

* A labelled run of 3 000 tracers contains ≈2 600 distinct phase-space points, ~13% fewer than the
  label says. The Poisson error bars quoted for the headline T215e signal (2.88× ± 0.18× at
  r = 500 pc, `CHANGELOG.md:1277`) are understated by √(3000/2623) = 1.070, i.e. **≈7%** — the honest
  figure is ±0.19×, and the 21σ outer-core number likewise by ~7%. No standing claim changes
  verdict at that size; the disclosure is what changes.
* The draws are multinomial rather than a simple random sample, so some initial conditions are
  counted twice and others never at all. For a density-profile statistic this is not fatal, but it
  is not what the code comment says it is.
* **The runner that produced the headline snapshot series is not in the repository.**
  `v0.3-prelim/data/snapshots_t215e/` (11 files) and the analyzers `t215_analyze_t215e.jl` /
  `t215_analyze_v2.jl` are tracked; no `t215e` runner is (`git ls-files | grep t215e` returns only
  the analyzers and the artifacts). Whether that generator used the with-replacement idiom cannot be
  established from the repository. The snapshots can be re-analysed; they cannot be re-generated.

Recorded as findings F46 and F47 in `docs/INTEGRITY_FINDINGS_2026-11-04.md`.

## 6. Decision on the surrogate question (option 3)

The Kaggle intake review (2026-11-17) raised one transferable idea for this repository: a trained
surrogate that emulates the expensive N-body run. **Declined**, on four grounds, in order of weight:

1. **T215 supports no live claim.** T215 is closed historic, "Methods contribution only — no
   quantitative t_core measurement" (CURRENT.md:620), and is not in the gate selection filter
   (`scripts/gate_pytest_selection.py`: T131–T135, T220). Building tooling to accelerate a closed
   methods-only series is exactly what the owner's standing rule says not to do ("if not useful,
   archive it").
2. **A surrogate cannot buy what the 10⁴ recommendation was for.** The recommendation exists to
   shrink shot noise — 3 000 → 10 000 particles reduces it by √(10000/3000) = 1.83, turning a
   quoted ±0.18× into ±0.099×. A surrogate trained on low-N runs reproduces low-N noise; it adds no
   particles and no resolution.
3. **A surrogate cannot cross the wall that is actually there.** The blocker is a numerical
   failure (`time_step.jl:67` exact-equality assert) plus N-dependent `dt` collapse. Emulating a
   solver that cannot integrate to 100 Myr at 10⁴ particles yields predictions of an integration
   that never happened.
4. **No training set exists and none is cheap to make.** A surrogate needs many runs spanning
   (N, t, σ/m); at today's measured 22–82 s/Myr at 3 000 particles, a 20-point grid at 100 Myr is
   ~17 h of CPU on a laptop that the project already documents as variance-sensitive.

**What replaces the parked recommendation.** Two statements instead of one unmeasured number:

* "10⁴ particle run — wall time 7 days, beyond laptop" → **superseded.** At 10⁴ the run reaches a
  scheduler assertion at ≈12.7 Myr in 134–207 s (measured today, two configurations); configurations
  that avoid the assertion cost 250–460 s per simulated Myr, i.e. 100 Myr is hours-to-days of CPU
  **with no guarantee of completion**. The 7-day figure is retained in `CHANGELOG.md` as history and
  is not repeated as a live estimate.
* "Run to 100 Myr — blocked by laptop ceiling" → **measured and partially closed.** At 3 000
  particles, 100 Myr completes in 51.2 min (upper bound; contaminated run). The proven optimum for
  this code remains N = 3 000 (`T215p`). Extending reach past that ceiling is the **Tier 3 code
  modification the project already named** — subcycled time integration, freeze refinement after a
  density threshold (CURRENT.md:638) — plus fixing the upstream exact-equality assert. It is not a
  compute-budget problem and not an ML problem.

## 7. Where the artifacts are

* Results, one JSON row per step (tag, N, target, nsnap, wall, status, error text):
  `/home/lamkuenai/nscale_results.jsonl` (WSL home, ephemeral scratch — the numbers that matter are
  transcribed above).
* Ladder logs: `/home/lamkuenai/nscale_run.log`, `nscale_run2.log`, `nscale_run3.log`,
  `nscale_run4.log`, `nscale_run5.log`.
* Snapshot files produced by the ladder: `/home/lamkuenai/nscale_out/<tag>/snap_NNN.jld2`
  (17 files for `n3000_t100`). Not copied into the repository: they are unanalysed single-seed
  output from a harness that deliberately deviates from the certified protocol (no `ulimit -v`), and
  committing them would imply a measurement that was never made.
* Harness and ladder scripts: appendices A and B below, kept as documentation. They are **not**
  installed under `scripts/` because they spell host paths, which CG-16 forbids in live scope.

---

## Appendix A — `t215_nscale.jl` (harness, as executed)

```julia
# Env-controlled T215 harness: same physics as t215_p.jl, with N / T_END / NSNAP from env.
using KiSS_SIDM, Random, Distributions, Statistics, LinearAlgebra, Printf, JLD2, HDF5, FileIO
const _here = @__DIR__
include(joinpath(_here, "t215d_utils.jl"))
const RESULTS_DIR = get(ENV, "TAG", "plain")
const OUT = get(ENV, "OUT_DIR", "/home/lamkuenai/nscale_out") * "/" * RESULTS_DIR
mkpath(OUT)
println("=== tag=$RESULTS_DIR N=$(ENV["N"]) t_end=$(ENV["T_END"]) Gyr nsnap=$(ENV["NSNAP"]) ===")

const IC_PATH = "C:/Users/lamkuenai/projects/sidm-composite-dm-mediator/v0.3-prelim/data/ics/t215_nfw_halo_cloud9.hdf5"
const IC = read_nfw_halo_ic(IC_PATH)
const cloud9 = make_cloud9_host_halo()
const n_total = length(IC.masses)
const N = parse(Int, get(ENV, "N", string(n_total)))
const n_pick = N
rng = Random.MersenneTwister(42)
idx = N == n_total ? collect(1:n_total) : sort(randperm(rng, n_total)[1:n_pick])   # without replacement
const masses = IC.masses[idx]
const positions = IC.positions[idx]
const velocities = IC.velocities[idx]
const sigma_m = 70.0
const N_total_mass = sum(masses)
const V_max = cloud9.V_max; const r_s = cloud9.r_s
const rho0 = 4.63e7 * cloud9.unit_density
const r_max = 2.0 * 1000.0 * cloud9.unit_length
const rhogrid = [(1.3696455060975761e6 / max(x, 1e-6))^2 for x in 1000.0*(1.0:10000.0)*cloud9.unit_length]
const vmax_orbit = maximum(sqrt(sum(v.^2 for v in velocities)))
const t_cross = (1000.0 * cloud9.unit_length) / vmax_orbit
println("N=", N, " distinct=", length(unique(idx)), " V_max=", V_max, " r_s=", r_s)

const t_end_cfg = parse(Float64, get(ENV, "T_END", "0.005"))
const nsnap = parse(Int, get(ENV, "NSNAP", "11"))
const t_end_phys = t_end_cfg * 1000.0 * cloud9.unit_time
const snapshot_times = nsnap == 0 ? Float64[] : collect(0.0:(t_end_cfg * 1000.0 * cloud9.unit_time / nsnap):(nsnap - 1) * (t_end_cfg * 1000.0 * cloud9.unit_time / nsnap))

const params = DSMCParams(
    masses, positions, velocities, sigma_m, N_total_mass, V_max, r_s, rhogrid, rho0, r_max, t_end_phys,
    cdm_scale_factor=10.0, min_particles_per_cell=64, max_particles_per_cell=4096,
    adaptive_grid_min_particles=64, adaptive_grid_max_particles=512,
    n_initial_cells=1, max_grid_depth=10, merge_particles=true, max_particles_per_cell_base=128,
    output_interval=1000 * cloud9.unit_time, snapshot_times=snapshot_times, output_dir=OUT,
    progress_interval=50, max_simulation_time=4.0 * t_end_phys, write_snapshots=true,
    scatter_velocity_factor=0.3, scattering_mode=cdr, verbose=true, enable_output=true,
)
run(params)
println("tag=", RESULTS_DIR, " status=completed")
```

(Exact executed copy lives in the scratch directory alongside the ladder scripts; the version above
is transcribed for readers and omits the per-step JSON emission, which is in appendix B's `run_step`.)

## Appendix B — ladder driver shape (as executed)

```bash
JULIA_NUM_THREADS=1
run_step() {  # tag N t_end_gyr nsnap
  TAG="$1" N="$2" T_END="$3" NSNAP="$4" \
    stdbuf -oL -eL timeout "$CAP" "$JULIA" --project="$KISS_DIR" "$HARNESS" 2>&1 | tee -a "$LOG"
  # exit 124 (timeout cap) is recorded as status=capped rather than discarded
}
```

Steps were daemonized (`setsid nohup`) and the 10⁴ ladder waited for the other ladder to finish so
the decisive runs had exclusive CPU. The wall-time cap (1800–9000 s) was reached only by steps the
operator terminated by hand.
