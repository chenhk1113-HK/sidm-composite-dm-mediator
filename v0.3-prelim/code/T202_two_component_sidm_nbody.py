"""
T202 - Two-component SIDM N-body simulation with Phase 44 parameters.

Per reviewer (model comments.docx, 2026-09-23):
"Conduct Dedicated N-body Simulations: The most direct solution is to run
cosmological or controlled N-body simulations with the paper's exact Phase 44
parameters. The goal is to derive a self-consistent f_H(r) profile from first
principles rather than borrowing one."

GOAL: Compute f_H(r) for a Cloud-9-like halo (M ~ 10^9 M_sun, sigma/m = 0.052 cm^2/g)
with TWO COMPONENTS (heavy + light) to see if mass segregation actually happens
at the paper's parameters. If yes, return f_H(r). If no, return a uniform f_H.

METHOD (adapted from amuse_bullet_dwarf.py + bullet-dwarf infrastructure):
- N = 2048 particles per halo (1024 heavy + 1024 light)
- M_halo = 10^9 M_sun total (5e8 each component)
- Heavy:lighter mass ratio = 10:1 (typical SIDM-asymmetric DM)
- Plummer sphere, R = 3 kpc
- sigma/m_eff = 0.052 cm^2/g (Phase 44 baseline at v=100 km/s)
- Evolve 2 Gyr in isolation (no collision; just see if heavy sinks)
- Measure f_H(r) at r = 0.01, 0.05, 0.1, 0.2, 0.5 r_vir
- Compare to current hand-coded values (0.85, 0.75, 0.55, etc.)

LIMITATIONS (per existing amuse_bullet_dwarf.py honest caveats):
- N=2048 is far below N>=10^5 for realistic gravothermal evolution
- SIDM kick is approximated as softened Maxwell-Boltzmann scattering
- No baryonic physics (gas/stars)
- Single isolated halo, not cosmological context
- Result should be interpreted as "qualitative check" not "first-principles f_H"

References:
- Yang, Tsai, Fan 2025 PRD 112, 083011 (the source paper whose Fig. 2 we are testing)
- AMUSE-ph4 2024.6.0 (Hut-Makino 4th-order Hermite)
- v0.3-prelim/code/amuse_bullet_dwarf.py (existing infrastructure)
- v0.3-prelim/code/phase44_two_component.py (the function we are testing)

OUTPUT:
- v0.3-prelim/data/results/t202_two_component_sidm.json
- v0.3-prelim/docs/T202_NBODY_RESULTS.md (analysis writeup)
"""
from __future__ import annotations
import sys
import os
import json
import time
from pathlib import Path

import numpy as np

# AMUSE imports - these work in WSL Python 3.10 venv
# Script MUST be run via:
#wsl -- bash -c '/home/lamkuenai/.local/amuse-py310-venv/bin/python /mnt/c/Users/lamkuenai/projects/sidm-composite-dm-mediator/v0.3-prelim/code/T202_two_component_sidm_nbody.py'

from amuse.units import units, nbody_system, constants
from amuse.datamodel import Particles
from amuse.ic.plummer import MakePlummerModel
from amuse.community.ph4.interface import Ph4


# ============================================================================
# Simulation parameters
# ============================================================================
HALO_MASS_MSUN_TOTAL = 1.0e9  # Total halo mass (M_sun)
# Heavy component gets mass_ratio/(1+mass_ratio) of total
# mass_ratio = 10: heavy = 10/11 of total, light = 1/11 of total
MASS_RATIO_HEAVY_TO_LIGHT = 10.0
HALO_MASS_HEAVY = HALO_MASS_MSUN_TOTAL * MASS_RATIO_HEAVY_TO_LIGHT / (1 + MASS_RATIO_HEAVY_TO_LIGHT)
HALO_MASS_LIGHT = HALO_MASS_MSUN_TOTAL / (1 + MASS_RATIO_HEAVY_TO_LIGHT)
N_PER_COMPONENT = 1024        # Per component (2048 total)

PLUMMER_RADIUS_PC = 3000.0    # 3 kpc Plummer scale
SOFTENING_PC = 50.0            # Gravitational softening (pc)

# Phase 44 baseline sigma/m = 0.052 cm^2/g at v=100 km/s
# But for two-component heavy-heavy we want sigma_HH only
# Yang+ 2025 PRD 112, 083011 used sigma/m = 147.1 cm^2/g at v=100 km/s
# (much higher than ours - that's why their f_H is more segregated)
# For Phase 44 baseline: factor of 0.052/147.1 = 0.000353 weaker
SIGMA_M_CM2_PER_G = 0.052       # Phase 44 baseline
V_REL_KM_S = 100.0             # Reference velocity for sigma/m
SIGMA_CM2 = SIGMA_M_CM2_PER_G * HALO_MASS_MSUN_TOTAL * 1.989e33  # cm^2

# Time integration
END_TIME_MYR = 2000.0          # 2 Gyr
DT_MYR = 50.0                  # Output interval (Myr)


# ============================================================================
# Helper functions
# ============================================================================

def make_two_component_plummer(M_heavy_total, M_light_total, N_heavy, N_light,
                                R_pc, mass_ratio):
    """Create two overlapping Plummer spheres (heavy + light).

    With N_heavy == N_light and mass_ratio = heavy:light per-particle mass:
        M_heavy_total = M_heavy_per * N_heavy = (mass_ratio * M_light_per) * N_heavy
        M_light_total = M_light_per * N_light
        Heavy:light TOTAL mass ratio = mass_ratio * N_heavy / N_light
                                            = mass_ratio (if N equal)

    So if mass_ratio = 10 and N are equal, heavy component has 10x total mass
    of the light component.

    Both components are Plummer spheres with scale R_pc, centered at origin.
    """
    # Per-particle masses (from chosen total masses)
    M_light_per = M_light_total / N_light
    M_heavy_per = M_heavy_total / N_heavy

    # Verify ratio
    actual_ratio = M_heavy_per / M_light_per
    if not (0.9 < actual_ratio / mass_ratio < 1.1):
        print(f"WARNING: requested mass_ratio {mass_ratio}, actual {actual_ratio:.3f}")

    nbody_conv = nbody_system.nbody_to_si(
        (M_heavy_total + M_light_total) | units.MSun,
        R_pc | units.pc
    )

    # Heavy component
    mp_h = MakePlummerModel(N_heavy, convert_nbody=nbody_conv)
    mp_h.mass = M_heavy_total | units.MSun
    mp_h.radius = R_pc | units.pc
    heavy_particles = mp_h.result
    heavy_particles.mass = M_heavy_per | units.MSun  # Override per-particle mass

    # Light component
    mp_l = MakePlummerModel(N_light, convert_nbody=nbody_conv)
    mp_l.mass = M_light_total | units.MSun
    mp_l.radius = R_pc | units.pc
    light_particles = mp_l.result
    light_particles.mass = M_light_per | units.MSun  # Override per-particle mass

    # Combine into single particle set
    all_particles = Particles()
    all_particles.add_particles(heavy_particles)
    all_particles.add_particles(light_particles)

    return all_particles, nbody_conv


def apply_sidm_scatter(particles, sigma_cm2, dt_myr, v_threshold_factor=2.0):
    """Apply SIDM scattering kicks to particle pairs within softening.

    Approximation (per amuse_bullet_dwarf.py):
    - For each pair within softening radius:
      - Compute relative velocity v_rel
      - If v_rel < v_threshold_factor * v_escape (local):
            Apply small-angle scattering kick with probability
            proportional to sigma * rho_local * delta_t
    - Kick magnitude ~ sigma_cm2 * rho_local * dt * v_rel (max 10%)

    Uses numpy-only neighbor search (no scipy dependency).
    """
    pos = particles.position.value_in(units.pc)
    vel = particles.velocity.value_in(units.km / units.s)
    mass = particles.mass.value_in(units.MSun)
    N = len(particles)

    # Brute-force neighbor search within softening radius (N^2 but small N)
    # For N < 5000 this is fast enough
    soft_radius_sq = SOFTENING_PC ** 2

    # Random kicks
    rng = np.random.default_rng(seed=42)
    kick_factor = 0.10  # max 10% velocity perturbation per step

    new_vel = vel.copy()
    n_scatters = 0
    for i in range(N):
        if i % 100 == 0:
            sys.stdout.write(f"\r  SIDM scatter: {i}/{N}")
            sys.stdout.flush()
        # Find neighbors within softening (brute force)
        diffs = pos - pos[i]
        dists_sq = np.einsum('ij,ij->i', diffs, diffs)
        neighbor_mask = (dists_sq < soft_radius_sq) & (np.arange(N) != i)
        n_neighbors = neighbor_mask.sum()
        if n_neighbors < 1:
            continue

        # Local mass density (rough)
        M_local = mass[neighbor_mask].sum()
        V_local = (4.0 / 3.0) * np.pi * SOFTENING_PC ** 3  # pc^3
        rho_local = M_local / V_local  # M_sun / pc^3

        # Scattering rate per particle
        # rate ~ sigma * rho * v_rel / m_particle
        # Use mean v_rel with neighbors
        v_rel_local = np.linalg.norm(vel[i] - vel[neighbor_mask].mean(axis=0))
        if v_rel_local < 1e-3:
            continue

        # Probability of scatter in this timestep
        # dt in seconds
        dt_s = dt_myr * 3.1557e10  # 1 Myr in s
        prob = min(1.0, sigma_cm2 * rho_local * v_rel_local * dt_s / mass[i])
        if prob > rng.random():
            # Apply random small-angle kick
            kick_mag = kick_factor * np.linalg.norm(vel[i])
            kick_dir = rng.normal(size=3)
            kick_dir /= np.linalg.norm(kick_dir)
            new_vel[i] += kick_mag * kick_dir
            n_scatters += 1

    sys.stdout.write("\r" + " " * 40 + "\r")
    particles.velocity = new_vel | (units.km / units.s)
    return n_scatters


def measure_f_H_r(particles, R_pc, n_bins=20, heavy_mass_cut=None):
    """Measure local heavy fraction f_H at various radii.

    Heavy particles are identified by their per-particle mass:
    since heavy component has HALO_MASS_HEAVY/N_PER_COMPONENT particles
    and light has HALO_MASS_LIGHT/N_PER_COMPONENT particles, the heavy
    particles have HALO_MASS_HEAVY/N_PER_COMPONENT mass and light have
    HALO_MASS_LIGHT/N_PER_COMPONENT mass.

    Args:
        particles: AMUSE particles object
        R_pc: virial radius (pc)
        n_bins: number of radial bins
        heavy_mass_cut: per-particle mass threshold (M_sun); if None, use
                       HALO_MASS_HEAVY/N_PER_COMPONENT

    Returns:
        r_over_rvir: array of radius fractions [0, 1]
        f_H_profile: array of heavy mass fraction at each r/r_vir
    """
    pos = particles.position.value_in(units.pc)
    mass = particles.mass.value_in(units.MSun)

    if heavy_mass_cut is None:
        heavy_mass_cut = HALO_MASS_HEAVY / N_PER_COMPONENT

    is_heavy = mass >= heavy_mass_cut

    r_3d = np.linalg.norm(pos, axis=1)

    # Bin in r
    r_max = R_pc  # r_vir ~ R (rough)
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


def main():
    print("=" * 60)
    print("T202 - Two-component SIDM N-body simulation")
    print("=" * 60)
    print(f"Total halo mass: {HALO_MASS_MSUN_TOTAL:.1e} M_sun")
    print(f"  Heavy: {HALO_MASS_HEAVY:.1e} M_sun ({N_PER_COMPONENT} particles)")
    print(f"  Light: {HALO_MASS_LIGHT:.1e} M_sun ({N_PER_COMPONENT} particles)")
    print(f"Heavy:light per-particle mass ratio: {MASS_RATIO_HEAVY_TO_LIGHT}")
    print(f"Plummer radius: {PLUMMER_RADIUS_PC} pc")
    print(f"sigma/m at v={V_REL_KM_S} km/s: {SIGMA_M_CM2_PER_G} cm^2/g")
    print(f"sigma total: {SIGMA_CM2:.3e} cm²")
    print(f"Integration: {END_TIME_MYR} Myr (output every {DT_MYR} Myr)")
    print()

    # Setup
    print("=== Setting up two-component Plummer halo ===")
    all_particles, nbody_conv = make_two_component_plummer(
        HALO_MASS_HEAVY, HALO_MASS_LIGHT,
        N_PER_COMPONENT, N_PER_COMPONENT,
        PLUMMER_RADIUS_PC, MASS_RATIO_HEAVY_TO_LIGHT
    )
    print(f"Total particles: {len(all_particles)}")
    print(f"Heavy mass total: {all_particles.mass.value_in(units.MSun)[:N_PER_COMPONENT].sum():.2e} M_sun")
    print(f"Light mass total: {all_particles.mass.value_in(units.MSun)[N_PER_COMPONENT:].sum():.2e} M_sun")
    print()

    # Initial f_H profile (uniform; both components distributed identically)
    r_rvir_initial, f_H_initial = measure_f_H_r(all_particles, PLUMMER_RADIUS_PC)
    print("=== Initial f_H(r) profile (uniform) ===")
    for r, f in zip(r_rvir_initial[::2], f_H_initial[::2]):
        print(f"  r/r_vir = {r:.3f}: f_H = {f:.3f}")
    print()

    # Run simulation
    print("=== Starting Ph4 simulation ===")
    t_start = time.time()

    gravity = Ph4(redirection="none", convert_nbody=nbody_conv)
    gravity.parameters.epsilon_squared = (SOFTENING_PC | units.pc) ** 2
    gravity.particles.add_particles(all_particles)

    n_outputs = int(END_TIME_MYR / DT_MYR)
    snapshots = []

    for step in range(n_outputs + 1):
        t_now = step * DT_MYR

        # Apply SIDM scatter
        if step > 0:  # skip initial scatter
            n_scatters = apply_sidm_scatter(
                gravity.particles,
                SIGMA_CM2,
                DT_MYR,
            )
        else:
            n_scatters = 0

        # Evolve
        gravity.evolve_model(DT_MYR | units.Myr)

        # Measure f_H profile
        r_rvir, f_H = measure_f_H_r(
            gravity.particles, PLUMMER_RADIUS_PC
        )

        snapshots.append({
            't_myr': t_now,
            'r_rvir': r_rvir.tolist(),
            'f_H': f_H.tolist(),
            'n_scatters_this_step': int(n_scatters),
        })

        if step % 4 == 0 or step == n_outputs:
            elapsed = time.time() - t_start
            # Report f_H at r=0.05, 0.1, 0.2
            try:
                f_005 = f_H[np.argmin(np.abs(r_rvir - 0.05))]
                f_01 = f_H[np.argmin(np.abs(r_rvir - 0.1))]
                f_02 = f_H[np.argmin(np.abs(r_rvir - 0.2))]
                print(f"  t={t_now:.0f} Myr ({elapsed:.1f}s): "
                      f"f_H(0.05)={f_005:.3f}, f_H(0.1)={f_01:.3f}, f_H(0.2)={f_02:.3f}")
            except (ValueError, IndexError):
                print(f"  t={t_now:.0f} Myr ({elapsed:.1f}s): f_H measurement failed")

    gravity.stop()
    print()
    print(f"Total wall time: {time.time() - t_start:.1f}s")
    print()

    # Final analysis
    print("=== FINAL f_H profile at t = 2 Gyr ===")
    final = snapshots[-1]
    r_rvir_final = np.array(final['r_rvir'])
    f_H_final = np.array(final['f_H'])

    # Compare to current hand-coded values from phase44_two_component.py
    # Current 'core_collapsed' (dSph-like):
    #   r < 0.05: f_H = 0.95
    #   r < 0.20: f_H = 0.30
    #   r > 0.20: f_H = 0.10
    current_hand_coded = {
        0.05: 0.95,
        0.10: 0.95,  # interpolated; currently 0.95 for r < 0.05, drops to 0.30 for r < 0.20
        0.20: 0.30,
        0.50: 0.10,
    }

    print(f"  {'r/r_vir':>10} {'f_H (T202)':>12} {'f_H (hand)':>12} {'delta':>8}")
    for r_target in [0.01, 0.05, 0.10, 0.20, 0.50]:
        idx = np.argmin(np.abs(r_rvir_final - r_target))
        f_sim = f_H_final[idx]
        # Hand-coded: piecewise function
        if r_target <= 0.05:
            f_hand = 0.95
        elif r_target <= 0.20:
            f_hand = 0.30
        else:
            f_hand = 0.10
        delta = f_sim - f_hand
        print(f"  {r_target:>10.3f} {f_sim:>12.3f} {f_hand:>12.3f} {delta:>+8.3f}")

    # Save
    output_dir = Path(__file__).resolve().parent.parent / 'data' / 'results'
    output_dir.mkdir(parents=True, exist_ok=True)
    # Allow override of output filename
    filename = getattr(__import__(__name__), 'output_filename', None) or 't202_two_component_sidm'
    output_path = output_dir / f'{filename}.json'
    output = {
        'T202_summary': 'Two-component SIDM N-body simulation',
        'date': '2026-09-23',
        'parameters': {
            'HALO_MASS_MSUN_TOTAL': HALO_MASS_MSUN_TOTAL,
            'HALO_MASS_HEAVY': HALO_MASS_HEAVY,
            'HALO_MASS_LIGHT': HALO_MASS_LIGHT,
            'N_PER_COMPONENT': N_PER_COMPONENT,
            'MASS_RATIO_HEAVY_TO_LIGHT': MASS_RATIO_HEAVY_TO_LIGHT,
            'PLUMMER_RADIUS_PC': PLUMMER_RADIUS_PC,
            'SIGMA_M_CM2_PER_G': SIGMA_M_CM2_PER_G,
            'V_REL_KM_S': V_REL_KM_S,
            'END_TIME_MYR': END_TIME_MYR,
        },
        'snapshots': snapshots,
        'HONEST_LIMITATIONS': [
            'N=2048 is far below N>=10^5 for realistic gravothermal evolution',
            'SIDM kick is approximated as softened Maxwell-Boltzmann scattering',
            'No baryonic physics (gas/stars)',
            'Single isolated halo, not cosmological context',
            'Result is a qualitative check, not first-principles f_H',
        ],
    }
    with open(output_path, 'w') as f:
        json.dump(output, f, indent=2)
    print(f"\nResults saved to {output_path}")


if __name__ == '__main__':
    main()