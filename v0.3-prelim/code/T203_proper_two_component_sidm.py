"""
T203 — Proper two-component SIDM N-body simulation.

Improvements over T202:
1. N = 10^5 particles (50x more) — collisionless regime
2. Proper energy-and-momentum conserving SIDM scattering
   (replace 10% random kick with actual pairwise momentum exchange)
3. NFW initial conditions instead of Plummer (cosmological-like)
4. Both Phase 44 (σ/m = 0.052 cm^2/g) AND Yang+ control (σ/m = 147.1 cm^2/g)

The script does NOT try to match Cloud-9's ~100 pc core (would need N > 10^6
and proper cosmological initial conditions + gravity solver with adaptive
refinement). T203 is a "real but tractable" validation.

Honest caveats (carried from T202):
- N = 10^5 << N >= 10^6 for realistic Cloud-9 core resolution
- No baryonic physics
- Single isolated halo, not cosmological context
- Ph4 gravity solver is collisionless; SIDM scattering is via explicit kernel

References:
- T202 (the prior version with N=2048 and 10% kick)
- AMUSE-ph4 2024.6.0
- Yang, Tsai, Fan 2025 PRD 112, 083011 (target paper whose f_H(r) we test)
- v0.3-prelim/code/amuse_bullet_dwarf.py (existing infrastructure)

OUTPUT:
- v0.3-prelim/data/results/t203_phase44.json
- v0.3-prelim/data/results/t203_yang_control.json
"""
from __future__ import annotations
import sys
import os
import json
import time
import argparse
from pathlib import Path

import numpy as np

from amuse.units import units, nbody_system
from amuse.datamodel import Particles
from amuse.ic.plummer import MakePlummerModel
from amuse.community.ph4.interface import Ph4


# ============================================================================
# Simulation parameters
# ============================================================================
HALO_MASS_MSUN_TOTAL = 1.0e9  # Total halo mass (M_sun)
MASS_RATIO_HEAVY_TO_LIGHT = 10.0  # heavy:light per-particle mass
HALO_MASS_HEAVY = HALO_MASS_MSUN_TOTAL * MASS_RATIO_HEAVY_TO_LIGHT / (1 + MASS_RATIO_HEAVY_TO_LIGHT)
HALO_MASS_LIGHT = HALO_MASS_MSUN_TOTAL / (1 + MASS_RATIO_HEAVY_TO_LIGHT)

# NFW profile parameters (cosmological-like)
NFW_C = 10.0  # concentration parameter
NFW_RS_PC = 300.0  # scale radius (pc); r_vir ~ c * r_s = 3000 pc

# Phase 44 sigma/m
SIGMA_M_PHASE44 = 0.052       # cm^2/g (paper's claim)
SIGMA_M_YANG = 147.1          # cm^2/g (Yang+ 2025)
V_REF_KMS = 100.0             # reference velocity for sigma/m

# Time integration
END_TIME_MYR = 5000.0         # 5 Gyr (Hubble time)
DT_MYR = 100.0                # output interval

# Output
N_PER_COMPONENT = 50000       # 10^5 total particles
SOFTENING_PC = 30.0           # pc (smaller than T202 because more particles)


def make_nfw_halo(M_total, N, c, r_s_pc):
    """Create an NFW halo (not Plummer) using inverse-CDF sampling.

    NFW profile: rho(r) = rho_s / ((r/r_s) * (1 + r/r_s)^2)

    Use the cumulative mass distribution:
        M(r) = M_total * [ln(1 + r/r_s) - r/(r + r_s)] / [ln(1 + c) - c/(1 + c)]

    Generate uniform random numbers in [0, 1), solve for r via bisection.
    Velocities from isotropic Maxwell-Boltzmann with dispersion given by
    the Jeans equation approximation (simplified).
    """
    r_vir = c * r_s_pc
    # Cumulative mass fraction at r_vir (should be ~1)
    f_vir = (np.log(1 + c) - c / (1 + c)) / (np.log(1 + c) - c / (1 + c))
    # Inverse CDF: solve for r given uniform u in (0, 1)
    # Use root finding on f(r) = u * f_vir - (ln(1 + r/r_s) - r/(r + r_s))
    r_grid = np.logspace(np.log10(0.001 * r_s_pc), np.log10(r_vir * 2), 5000)
    m_grid = np.log(1 + r_grid / r_s_pc) - r_grid / (r_grid + r_s_pc)
    m_grid /= m_grid[-1]  # normalize to 1 at r_vir
    r_cdf = np.interp(np.linspace(0, 1, N), m_grid, r_grid)

    # Isotropic velocities (Maxwell-Boltzmann with characteristic velocity)
    # Use v_circ(r_vir) ~ sqrt(G M / r_vir) for a rough velocity scale
    G_geom = 4.30091e-3  # (pc/M_sun) * (km/s)^2
    v_circ = np.sqrt(G_geom * M_total / r_vir)  # km/s

    # 3D Gaussian velocities
    rng = np.random.default_rng(seed=42)
    v_disp = v_circ / np.sqrt(2)  # rough dispersion
    vx = rng.normal(0, v_disp, N)
    vy = rng.normal(0, v_disp, N)
    vz = rng.normal(0, v_disp, N)

    return r_cdf, vx, vy, vz


def make_two_component_nfw(M_total, M_heavy, M_light, N_heavy, N_light, c, r_s_pc):
    """Create NFW halo with heavy + light components overlapping."""
    # Heavy component
    r_h, vx_h, vy_h, vz_h = make_nfw_halo(M_total, N_heavy, c, r_s_pc)
    # Light component
    r_l, vx_l, vy_l, vz_l = make_nfw_halo(M_total, N_light, c, r_s_pc)

    # Random angles on sphere
    rng = np.random.default_rng(seed=43)
    theta_h = rng.uniform(0, np.pi, N_heavy)
    phi_h = rng.uniform(0, 2 * np.pi, N_heavy)
    theta_l = rng.uniform(0, np.pi, N_light)
    phi_l = rng.uniform(0, 2 * np.pi, N_light)

    # Cartesian positions
    pos_h = np.column_stack([
        r_h * np.sin(theta_h) * np.cos(phi_h),
        r_h * np.sin(theta_h) * np.sin(phi_h),
        r_h * np.cos(theta_h),
    ])
    pos_l = np.column_stack([
        r_l * np.sin(theta_l) * np.cos(phi_l),
        r_l * np.sin(theta_l) * np.sin(phi_l),
        r_l * np.cos(theta_l),
    ])

    # Per-particle masses
    M_heavy_per = M_heavy / N_heavy
    M_light_per = M_light / N_light

    nbody_conv = nbody_system.nbody_to_si(M_total | units.MSun, r_s_pc * c | units.pc)

    particles = Particles(N_heavy + N_light)
    # Heavy particles
    pos_all = np.vstack([pos_h, pos_l])
    vel_all = np.column_stack([
        np.concatenate([vx_h, vx_l]),
        np.concatenate([vy_h, vy_l]),
        np.concatenate([vz_h, vz_l]),
    ])
    particles.position = pos_all | units.pc
    particles.velocity = vel_all | (units.km / units.s)
    particles.mass = np.concatenate([
        np.full(N_heavy, M_heavy_per),
        np.full(N_light, M_light_per),
    ]) | units.MSun

    return particles, nbody_conv


def apply_proper_sidm_scatter(particles, sigma_per_mass_cm2_g, dt_myr,
                               v_threshold_factor=2.0):
    """Proper energy-and-momentum conserving SIDM scattering.

    For each pair of particles within softening:
        - Compute relative velocity v_rel
        - Compute scattering probability p = sigma_per_mass * rho * v_rel * dt
          (per-particle scattering rate)
        - If scattering occurs:
            - Conserve momentum and kinetic energy
            - Apply isotropic scattering in CM frame

    This is the proper way to do SIDM scattering, vs T202's 10% random kick.

    For efficiency with N = 10^5, use cell-linked list for neighbor finding.
    (Brute force is O(N^2) = 10^10 ops per step - infeasible.)
    """
    pos = particles.position.value_in(units.pc)
    vel = particles.velocity.value_in(units.km / units.s)
    mass = particles.mass.value_in(units.MSun)
    N = len(particles)

    # Convert sigma/m to per-mass cross section (cm^2 / g)
    # Total cross section for particle i: sigma_i = (sigma/m) * m_i
    # In CGS: sigma_i (cm^2) = sigma_per_mass (cm^2/g) * m_i (g)
    # Convert M_sun to g: 1 M_sun = 1.989e33 g
    M_SUN_G = 1.989e33
    sigma_per_particle_cm2 = sigma_per_mass_cm2_g * mass * M_SUN_G

    # Cell-linked list for neighbor search
    soft_radius_sq = SOFTENING_PC ** 2
    # Use box of size ~4 * softening around center for cell size
    cell_size = 2.0 * SOFTENING_PC
    pos_min = pos.min(axis=0)
    pos_max = pos.max(axis=0)
    box_size = pos_max - pos_min
    n_cells = np.maximum(1, (box_size / cell_size).astype(int))
    n_cells = np.minimum(n_cells, 50)  # cap cells

    # Compute cell index for each particle
    cell_idx = np.floor((pos - pos_min) / cell_size).astype(int)
    cell_idx = np.clip(cell_idx, 0, n_cells - 1)
    # Linear cell ID
    cell_id = cell_idx[:, 0] * n_cells[1] * n_cells[2] + cell_idx[:, 1] * n_cells[2] + cell_idx[:, 2]

    # Build cell-to-particle index
    cell_to_particles = {}
    for i, c in enumerate(cell_id):
        cell_to_particles.setdefault(c, []).append(i)

    rng = np.random.default_rng(seed=44)
    new_vel = vel.copy()
    n_scatters = 0

    cells_3d = [(dx, dy, dz)
                for dx in range(-1, 2)
                for dy in range(-1, 2)
                for dz in range(-1, 2)]

    for c, parts_in_cell in cell_to_particles.items():
        # Process pairs within this cell + 26 neighbors
        candidates = set()
        for dx, dy, dz in cells_3d:
            cell_x = c // (n_cells[1] * n_cells[2])
            cell_y = (c // n_cells[2]) % n_cells[1]
            cell_z = c % n_cells[2]
            nx = (cell_x + dx) % n_cells[0]
            ny = (cell_y + dy) % n_cells[1]
            nz = (cell_z + dz) % n_cells[2]
            neighbor_id = nx * n_cells[1] * n_cells[2] + ny * n_cells[2] + nz
            candidates.update(cell_to_particles.get(neighbor_id, []))

        for i in parts_in_cell:
            for j in candidates:
                if j <= i:
                    continue
                diff = pos[i] - pos[j]
                dist_sq = np.dot(diff, diff)
                if dist_sq > soft_radius_sq or dist_sq < 1e-6:
                    continue

                # Local mass density
                # Use average of i and j's mass
                M_local = mass[i] + mass[j]
                V_local = (4.0 / 3.0) * np.pi * soft_radius_sq ** 1.5
                rho_local = M_local / V_local  # M_sun / pc^3
                # Convert to g/cm^3: 1 M_sun/pc^3 = 1.989e33 / (3.086e18)^3 g/cm^3
                rho_local_cgs = rho_local * M_SUN_G / (3.086e18 ** 3)  # g/cm^3

                # Relative velocity
                v_rel_vec = vel[i] - vel[j]
                v_rel = np.linalg.norm(v_rel_vec)

                # Scattering cross section for the pair (geometric mean)
                sigma_pair_cm2 = np.sqrt(sigma_per_particle_cm2[i] * sigma_per_particle_cm2[j])

                # Scattering probability per unit time
                # rate ~ n * sigma * v_rel, where n is number density
                # For pair-specific rate: rate ~ sigma * v_rel / V_local
                # Probability in dt: p = rate * dt
                dt_s = dt_myr * 3.1557e10  # 1 Myr in s
                rate = sigma_pair_cm2 * v_rel * 1e5 / V_local  # v in km/s -> cm/s
                prob = min(1.0, rate * dt_s)

                if prob > rng.random():
                    # Proper isotropic scattering in CM frame
                    # Compute CM velocity
                    m_total = mass[i] + mass[j]
                    v_cm = (mass[i] * vel[i] + mass[j] * vel[j]) / m_total

                    # Transform to CM frame
                    u_i = vel[i] - v_cm
                    u_j = vel[j] - v_cm

                    # Random direction for new u_i (energy conservation: |u_i| conserved)
                    u_rel = u_i - u_j  # relative velocity in CM
                    v_rel_mag = np.linalg.norm(u_rel)
                    if v_rel_mag < 1e-6:
                        continue

                    # Random rotation of u_rel about a random axis
                    # Generate random direction for new u_rel (still magnitude v_rel_mag)
                    new_dir = rng.normal(size=3)
                    new_dir /= np.linalg.norm(new_dir)
                    new_u_rel = new_dir * v_rel_mag

                    # New u_i, u_j in CM (split by mass ratio)
                    # m_i * u_i_new + m_j * u_j_new = 0 (CM frame momentum zero)
                    # u_i_new - u_j_new = new_u_rel
                    # => u_i_new = new_u_rel * m_j / m_total
                    #    u_j_new = -new_u_rel * m_i / m_total
                    u_i_new = new_u_rel * mass[j] / m_total
                    u_j_new = -new_u_rel * mass[i] / m_total

                    # Transform back to lab frame
                    new_vel[i] = v_cm + u_i_new
                    new_vel[j] = v_cm + u_j_new
                    n_scatters += 1

    particles.velocity = new_vel | (units.km / units.s)
    return n_scatters


def measure_f_H_r(particles, R_vir_pc, n_bins=20, heavy_mass_cut=None):
    """Measure heavy fraction profile (same as T202)."""
    pos = particles.position.value_in(units.pc)
    mass = particles.mass.value_in(units.MSun)

    if heavy_mass_cut is None:
        heavy_mass_cut = HALO_MASS_HEAVY / N_PER_COMPONENT

    is_heavy = mass >= heavy_mass_cut
    r_3d = np.linalg.norm(pos, axis=1)

    r_max = R_vir_pc
    bins = np.linspace(0, r_max, n_bins + 1)
    bin_centers = (bins[:-1] + bins[1:]) / 2

    f_H_profile = np.zeros(n_bins)
    for b in range(n_bins):
        in_bin = (r_3d >= bins[b]) & (r_3d < bins[b + 1])
        if in_bin.sum() == 0:
            f_H_profile[b] = np.nan
            continue
        mass_in_bin = mass[in_bin].sum()
        mass_heavy = mass[in_bin & is_heavy].sum()
        f_H_profile[b] = mass_heavy / mass_in_bin if mass_in_bin > 0 else 0.0

    return bin_centers / r_max, f_H_profile


def run_simulation(sigma_m_cm2_g, output_filename, label):
    """Run a single simulation with given sigma/m."""
    print(f"\n{'='*60}")
    print(f"T203: Two-component SIDM N-body ({label})")
    print(f"sigma/m = {sigma_m_cm2_g} cm^2/g at v={V_REF_KMS} km/s")
    print(f"{'='*60}")

    # Setup NFW halo
    print("Creating NFW halo with heavy + light components...")
    t0 = time.time()
    all_particles, nbody_conv = make_two_component_nfw(
        HALO_MASS_MSUN_TOTAL, HALO_MASS_HEAVY, HALO_MASS_LIGHT,
        N_PER_COMPONENT, N_PER_COMPONENT,
        NFW_C, NFW_RS_PC,
    )
    print(f"  Created {len(all_particles)} particles in {time.time()-t0:.1f}s")
    print(f"  Heavy total: {HALO_MASS_HEAVY:.3e} M_sun, Light total: {HALO_MASS_LIGHT:.3e} M_sun")

    # Initialize gravity solver
    print("Initializing Ph4 gravity solver...")
    gravity = Ph4(redirection="none", convert_nbody=nbody_conv)
    gravity.parameters.epsilon_squared = (SOFTENING_PC | units.pc) ** 2
    gravity.particles.add_particles(all_particles)

    # Time evolution
    n_outputs = int(END_TIME_MYR / DT_MYR)
    snapshots = []
    sigma_total = sigma_m_cm2_g * HALO_MASS_MSUN_TOTAL * 1.989e33  # cm^2

    for step in range(n_outputs + 1):
        t_now = step * DT_MYR
        t_loop_start = time.time()

        # Apply SIDM scattering (skip at step 0)
        if step > 0:
            n_scatters = apply_proper_sidm_scatter(
                gravity.particles,
                sigma_m_cm2_g,
                DT_MYR,
            )
            # Update gravity particle velocities
            gravity.particles.velocity = gravity.particles.velocity
        else:
            n_scatters = 0

        # Evolve gravity
        gravity.evolve_model(DT_MYR | units.Myr)

        # Measure f_H
        r_rvir, f_H = measure_f_H_r(gravity.particles, NFW_C * NFW_RS_PC)

        snapshots.append({
            't_myr': t_now,
            'r_rvir': r_rvir.tolist(),
            'f_H': f_H.tolist(),
            'n_scatters_this_step': int(n_scatters),
        })

        if step % 5 == 0 or step == n_outputs:
            elapsed = time.time() - t_loop_start
            try:
                f_005 = f_H[np.argmin(np.abs(r_rvir - 0.05))]
                f_01 = f_H[np.argmin(np.abs(r_rvir - 0.1))]
                f_02 = f_H[np.argmin(np.abs(r_rvir - 0.2))]
                print(f"  t={t_now:.0f} Myr (step {elapsed:.1f}s): "
                      f"f_H(0.05)={f_005:.3f}, f_H(0.1)={f_01:.3f}, f_H(0.2)={f_02:.3f}, "
                      f"n_scatters={n_scatters}")
            except (ValueError, IndexError):
                print(f"  t={t_now:.0f} Myr (step {elapsed:.1f}s): f_H measurement failed")

    gravity.stop()

    # Save
    output_dir = Path(__file__).resolve().parent.parent / 'data' / 'results'
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / f'{output_filename}.json'
    output = {
        'T203_summary': f'Two-component SIDM N-body ({label})',
        'date': '2026-09-23',
        'parameters': {
            'HALO_MASS_MSUN_TOTAL': HALO_MASS_MSUN_TOTAL,
            'HALO_MASS_HEAVY': HALO_MASS_HEAVY,
            'HALO_MASS_LIGHT': HALO_MASS_LIGHT,
            'N_PER_COMPONENT': N_PER_COMPONENT,
            'MASS_RATIO_HEAVY_TO_LIGHT': MASS_RATIO_HEAVY_TO_LIGHT,
            'NFW_C': NFW_C,
            'NFW_RS_PC': NFW_RS_PC,
            'SIGMA_M_CM2_PER_G': sigma_m_cm2_g,
            'V_REF_KM_S': V_REF_KMS,
            'END_TIME_MYR': END_TIME_MYR,
            'DT_MYR': DT_MYR,
            'SOFTENING_PC': SOFTENING_PC,
        },
        'snapshots': snapshots,
        'HONEST_LIMITATIONS': [
            'N=10^5 is below N>=10^6 for realistic Cloud-9 core resolution',
            'No baryonic physics',
            'Single isolated NFW halo, not cosmological context',
            'Ph4 gravity is collisionless; SIDM scattering via explicit kernel',
            'Proper pairwise scattering (vs T202 random kick), but cell-list is approximate',
        ],
    }
    with open(output_path, 'w') as f:
        json.dump(output, f, indent=2)
    print(f"\nResults saved to {output_path}")

    return output_path


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--mode', choices=['phase44', 'yang', 'both'], default='both',
                       help='Which simulation(s) to run')
    args = parser.parse_args()

    print(f"T203 starts at {time.strftime('%H:%M:%S')}")
    t_start = time.time()

    if args.mode in ('phase44', 'both'):
        run_simulation(SIGMA_M_PHASE44, 't203_phase44', 'Phase 44')

    if args.mode in ('yang', 'both'):
        run_simulation(SIGMA_M_YANG, 't203_yang_control', 'Yang+ 2025 control')

    print(f"\nTotal wall time: {time.time() - t_start:.1f}s")
    print(f"T203 finished at {time.strftime('%H:%M:%S')}")


if __name__ == '__main__':
    main()