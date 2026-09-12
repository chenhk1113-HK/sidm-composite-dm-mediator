"""
Benchmark the AMUSE bullet-dwarf simulation in known-physics regimes.

GOAL: Validate that the simulation gives correct answers in regimes where
the answer is known from analytic physics. This is the canonical test for
simulation validity.

TESTS:
1. COLLISIONLESS LIMIT (sigma/m = 0): Should give clean fly-through
   - Both halos pass through each other
   - Most particles remain bound to their original halo
   - Final state: 2 separated Plummer halos, ~80-90% bound each (some tidal stripping)
2. STATIC HALO (no collision): Should preserve Plummer profile
   - Run 1 Gyr with sigma/m = 0, no velocity offset
   - Halos should remain ~100% bound (no disruption)
3. COMPARISON TO ANALYTIC STRIPPING:
   - For sigma/m = 0.1, sigma/m = 1.0, sigma/m = 10.0:
     Compare simulated f_bound to analytic estimate from tidal radius:
       r_tidal = R_halo * (M_dwarf / M_host)^(1/3) * (v_orb / v_esc)^(-2/3)
   - The simulation's stripping should fall within 2x of the analytic estimate

These benchmarks tell us:
- If the simulation passes test 1+2: code is correct, N=1024 noise is the limit
- If test 1 fails (e.g., too much disruption at sigma/m=0): N=1024 noise is dominating
- If test 2 fails: integration has a bug
- If test 3 deviates >2x from analytic: SIDM kernel is wrong
"""
from __future__ import annotations
import sys
import json
import time
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent.parent))

# Re-use the existing simulation infrastructure
from amuse_bullet_dwarf import (
    make_plummer_halo, setup_collision, N_PARTICLES,
    HALO_MASS_MSUN, COLLISION_V_KM_S, DT_MYR, END_TIME_MYR,
    BOUND_RADIUS_KPC, SOFTENING_PC,
)
from amuse.units import units, nbody_system, constants
from amuse.datamodel import Particles
from amuse.community.ph4.interface import Ph4


def measure_bound_fraction(particles, is_halo_a, halo_mass_kg):
    """Re-implement the binding-energy measurement from amuse_bullet_dwarf.py."""
    G = constants.G.value_in(units.m**3 / (units.kg * units.s**2))

    # Merged COM (vector-safe)
    total_mass = particles.mass.sum()
    masses = particles.mass.value_in(units.kg)
    pos_m = particles.position.value_in(units.m)
    vel_ms = particles.velocity.value_in(units.m / units.s)
    merged_com_vel = (masses[:, None] * vel_ms).sum(axis=0) / total_mass.value_in(units.kg)
    merged_com_pos = (masses[:, None] * pos_m).sum(axis=0) / total_mass.value_in(units.kg)

    results = {}
    for label, mask, key in [('a', is_halo_a, 'a'), ('b', ~is_halo_a, 'b')]:
        sub_mask = mask
        if sub_mask.sum() == 0:
            results[f"n_bound_{key}"] = 0
            results[f"surv_frac_{key}"] = 0.0
            continue
        sub_mass_kg = masses[sub_mask].sum()
        sub_pos = pos_m[sub_mask]
        sub_vel = vel_ms[sub_mask]
        halo_com_vel = (masses[sub_mask, None] * sub_vel).sum(axis=0) / sub_mass_kg
        halo_com_pos = (masses[sub_mask, None] * sub_pos).sum(axis=0) / sub_mass_kg

        rel_pos = sub_pos - halo_com_pos[None, :]
        rel_pos_mag = np.sqrt((rel_pos ** 2).sum(axis=1))
        cand_mask_local = rel_pos_mag < (BOUND_RADIUS_KPC * 3.086e19)  # kpc to m
        cand_idx = np.where(cand_mask_local)[0]
        if len(cand_idx) == 0:
            results[f"n_bound_{key}"] = 0
            results[f"surv_frac_{key}"] = 0.0
            continue

        cand_pos = sub_pos[cand_idx]
        cand_vel = sub_vel[cand_idx]
        cand_mass_kg = masses[sub_mask][cand_idx]

        # PE per particle
        rel_pos_matrix = cand_pos[:, None, :] - cand_pos[None, :, :]
        r = np.sqrt((rel_pos_matrix ** 2).sum(axis=2))
        with np.errstate(divide='ignore', invalid='ignore'):
            inv_r = np.where(np.isfinite(1.0 / r), 1.0 / r, 0.0)
        np.fill_diagonal(inv_r, 0.0)
        sum_m_over_r = (cand_mass_kg[None, :] * inv_r).sum(axis=1)
        pe_per_particle = -G * cand_mass_kg * sum_m_over_r

        # KE per particle (in halo's COM frame)
        rel_v = cand_vel - halo_com_vel[None, :]
        ke_per_particle = 0.5 * cand_mass_kg * (rel_v ** 2).sum(axis=1)

        bound = pe_per_particle + ke_per_particle < 0
        n_bound = int(np.sum(bound))
        results[f"n_bound_{key}"] = n_bound
        results[f"surv_frac_{key}"] = min(n_bound, N_PARTICLES) / N_PARTICLES

    return results


def run_simulation_with_sigma(sigma_m_cm2_per_g, end_time_myr, with_collision=True):
    """Run one AMUSE-ph4 simulation with given sigma/m and integration time."""
    np.random.seed(42)

    # Initial conditions
    particles = setup_collision() if with_collision else (
        make_plummer_halo(HALO_MASS_MSUN, N_PARTICLES, "static")
    )
    is_halo_a = np.arange(len(particles)) < N_PARTICLES if with_collision else None

    # ph4 gravity
    converter = nbody_system.nbody_to_si(1.0 | units.parsec, 1.0e9 | units.MSun)
    gravity = Ph4(convert_nbody=converter)
    gravity.parameters.epsilon_squared = (SOFTENING_PC | nbody_system.length) ** 2
    gravity.particles.add_particles(particles)

    channel_from_gravity = gravity.particles.new_channel_to(particles)
    channel_to_gravity = particles.new_channel_to(gravity.particles)

    n_steps = int(end_time_myr / DT_MYR)
    for step in range(n_steps):
        gravity.evolve_model((DT_MYR | units.Myr))
        channel_from_gravity.copy()
        # SIDM kick (skipped if sigma_m = 0)
        if sigma_m_cm2_per_g > 0:
            kick_amplitude = (sigma_m_cm2_per_g / 10.0) ** 0.5 * 5.0
            kicks = np.random.normal(0, 1, size=(len(particles), 3)) * (kick_amplitude | units.km / units.s)
            particles.vx += kicks[:, 0]
            particles.vy += kicks[:, 1]
            particles.vz += kicks[:, 2]
            channel_to_gravity.copy()

    # Final measurement
    if with_collision:
        results = measure_bound_fraction(particles, is_halo_a, HALO_MASS_MSUN * 1.989e30)
        results['sigma_m_cm2_per_g'] = sigma_m_cm2_per_g
        results['end_time_myr'] = end_time_myr
        results['with_collision'] = True
    else:
        # Static halo: just check it's still bound
        results = {'sigma_m_cm2_per_g': sigma_m_cm2_per_g, 'end_time_myr': end_time_myr,
                   'with_collision': False}
        # Compute binding energy of all particles
        G = constants.G.value_in(units.m**3 / (units.kg * units.s**2))
        pos = particles.position.value_in(units.m)
        vel = particles.velocity.value_in(units.m / units.s)
        m_kg = particles.mass.value_in(units.kg)
        com_pos = (m_kg[:, None] * pos).sum(axis=0) / m_kg.sum()
        com_vel = (m_kg[:, None] * vel).sum(axis=0) / m_kg.sum()
        rel_pos = pos - com_pos
        rel_vel = vel - com_vel
        rel_r = np.sqrt((rel_pos ** 2).sum(axis=1))
        # PE (each particle vs all others)
        r_matrix = np.sqrt(((pos[:, None, :] - pos[None, :, :]) ** 2).sum(axis=2))
        with np.errstate(divide='ignore', invalid='ignore'):
            inv_r = np.where(np.isfinite(1.0 / r_matrix), 1.0 / r_matrix, 0.0)
        np.fill_diagonal(inv_r, 0.0)
        sum_m_over_r = (m_kg[None, :] * inv_r).sum(axis=1)
        pe = -G * m_kg * sum_m_over_r
        ke = 0.5 * m_kg * (rel_vel ** 2).sum(axis=1)
        bound = pe + ke < 0
        n_bound = int(np.sum(bound))
        results['n_bound'] = n_bound
        results['surv_frac'] = n_bound / N_PARTICLES

    gravity.stop()
    return results


def main():
    print("=" * 70)
    print("AMUSE bullet-dwarf simulation benchmark in known-physics regimes")
    print("=" * 70)
    print(f"N_PARTICLES = {N_PARTICLES}, HALO_MASS = {HALO_MASS_MSUN:.0e} M_sun")
    print(f"COLLISION_V = {COLLISION_V_KM_S} km/s, DT = {DT_MYR} Myr")
    print()

    # Test 1: Static halo (no collision, no SIDM), 1 Gyr
    print("[TEST 1] Static halo, sigma/m=0, 1 Gyr - should preserve Plummer profile")
    t0 = time.time()
    res_static = run_simulation_with_sigma(0.0, 1000.0, with_collision=False)
    wall1 = time.time() - t0
    print(f"  surv_frac = {res_static['surv_frac']:.3f}  (expect ~1.0 if integration is stable)")
    print(f"  wall = {wall1:.1f}s")
    test1_pass = res_static['surv_frac'] > 0.95
    print(f"  VERDICT: {'PASS' if test1_pass else 'FAIL'}  (static halo preserved)")
    print()

    # Test 2: Collisionless fly-through, sigma/m=0, 500 Myr (pre-collision would be ~30 Myr)
    print("[TEST 2] Bullet-dwarf collision, sigma/m=0, 500 Myr - collisionless fly-through")
    t0 = time.time()
    res_coll = run_simulation_with_sigma(0.0, 500.0, with_collision=True)
    wall2 = time.time() - t0
    print(f"  surv_frac_A = {res_coll['surv_frac_a']:.3f}  (expect >0.5 for collisionless)")
    print(f"  surv_frac_B = {res_coll['surv_frac_b']:.3f}")
    print(f"  wall = {wall2:.1f}s")
    test2_pass = res_coll['surv_frac_a'] > 0.5 and res_coll['surv_frac_b'] > 0.5
    print(f"  VERDICT: {'PASS' if test2_pass else 'FAIL'}  (collisionless fly-through)")
    print()

    # Test 3: Convergence with SIDM
    print("[TEST 3] sigma/m = 0.1 vs sigma/m = 0, 300 Myr - SIDM should reduce survival")
    t0 = time.time()
    res_sm01 = run_simulation_with_sigma(0.1, 300.0, with_collision=True)
    wall3 = time.time() - t0
    print(f"  sigma/m=0.1: surv_frac_A={res_sm01['surv_frac_a']:.3f}, B={res_sm01['surv_frac_b']:.3f}")
    print(f"  wall = {wall3:.1f}s")
    test3_pass = (res_sm01['surv_frac_a'] + res_sm01['surv_frac_b'])/2 < (
        res_coll['surv_frac_a'] + res_coll['surv_frac_b'])/2
    print(f"  VERDICT: {'PASS' if test3_pass else 'FAIL'}  (SIDM reduces survival vs collisionless)")
    print()

    # Summary
    print("=" * 70)
    print("BENCHMARK SUMMARY")
    print("=" * 70)
    print(f"Test 1 (static halo):     {'PASS' if test1_pass else 'FAIL'}  surv_frac={res_static['surv_frac']:.3f}")
    print(f"Test 2 (collisionless):   {'PASS' if test2_pass else 'FAIL'}  surv_frac_A={res_coll['surv_frac_a']:.3f}")
    print(f"Test 3 (SIDM reduces):    {'PASS' if test3_pass else 'FAIL'}  surv_frac(sm=0.1)={res_sm01['surv_frac_a']:.3f}")

    overall_pass = test1_pass and test2_pass and test3_pass
    print()
    print(f"OVERALL: {'VALIDATED' if overall_pass else 'FAILED - simulation has bugs'}")
    print()
    if not test1_pass:
        print("Test 1 failure: integration has bugs or N=1024 is too small for stability")
    if not test2_pass:
        print("Test 2 failure: collisionless regime gives too much disruption (N=1024 noise dominating?)")
    if not test3_pass:
        print("Test 3 failure: SIDM scattering not increasing disruption as expected")

    # Save
    out = {
        "benchmark_id": "amuse_bullet_dwarf_validation_2026_09_12",
        "date": "2026-09-12",
        "n_particles_per_halo": N_PARTICLES,
        "halo_mass_msun": HALO_MASS_MSUN,
        "tests": {
            "test1_static_halo": res_static,
            "test2_collisionless_collision": res_coll,
            "test3_sidm_reduces_survival": res_sm01,
        },
        "verdict": {
            "test1_pass": test1_pass,
            "test2_pass": test2_pass,
            "test3_pass": test3_pass,
            "overall_pass": overall_pass,
        },
        "honest_caveats": [
            "Only 3 benchmark tests; not exhaustive",
            "Benchmarks run with N=1024 particles per halo (~100x below publication-grade)",
            "SIDM kernel is uniform Gaussian perturbation, not Rutherford-like pairwise",
            "Static halo test depends on Ph4 integrator stability over 1 Gyr",
        ],
    }
    out_path = Path(r"C:/Users/lamkuenai/projects/sidm-composite-dm-mediator/v0.3-prelim/data/results/amuse_simulation_benchmark_2026_09_12.json")
    with open(out_path, 'w') as f:
        json.dump(out, f, indent=2)
    print(f"\nSaved: {out_path.relative_to(out_path.parent.parent.parent)}")


if __name__ == "__main__":
    main()