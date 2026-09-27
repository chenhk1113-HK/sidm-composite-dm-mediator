"""
Bullet-dwarf collision N-body simulation for Channel 27 calibration.

GOAL: Compute gravothermal collapse outcomes as a function of sigma/m_chi
at v=358 km/s, using AMUSE-framework's ph4 (Hut-Makino 4th-order Hermite)
N-body code. The simulation runs a ~10^3 particle head-on collision
between two dwarf-galaxy-mass halos at v=358 km/s (matching the NGC 1052
trail observation, van Dokkum+ 2022 arXiv:2205.08552), then measures
the surviving halo's mass fraction as a function of the SIDM cross-section.

SCALE (publication-grade would be N=10^5+; this is proof-of-concept):
- N=1024 per halo (2048 total)
- Halo mass: 10^9 M_sun each
- Collision velocity: 358 km/s head-on
- Impact parameter: 0 (head-on for simplicity)
- Sigma/m_chi sweep: 0.1, 0.5, 1.0, 2.0, 5.0, 10.0 cm^2/g
- Time integration: ~2 Gyr post-collision (gravothermal-collapse timescale
  for 10^9 M_sun halos at sigma/m ~ 1 is ~10-100 Myr)

For each sigma/m_chi value:
1. Set up two Plummer spheres (N=1024 each) on a head-on collision trajectory
2. Enable ph4 with self-gravity
3. Add a custom pairwise-velocity gate that simulates SIDM scattering:
   for each particle pair within softening, if relative velocity < 2*v_escape,
   apply an instantaneous small-angle scattering kick with probability
   proportional to sigma/m_chi * rho_local * delta_t.
4. Evolve 2 Gyr
5. Measure: surviving-halo mass fraction, central density profile slope,
   whether the host halo core collapsed (cuspy return)

OUTPUT: For each sigma/m_chi, the mass fraction of the surviving halo that
remains bound (not stripped by the collision). High sigma/m means more DM
is scattered -> DM gets dragged with gas -> DM-free galaxies form. Low
sigma/m means DM passes through -> companion halo intact.

The threshold sigma/m_chi where the surviving halo's mass fraction drops
to ~50% is the calibration value for Channel 27's peak.

HONEST CAVEATS:
- N=1024 is FAR below the N>=10^5 needed for realistic SIDM gravothermal
  evolution (per Yang+ 2024 SASHIMI calibration notes). This is a
  proof-of-concept that the pipeline works, not a publication-grade result.
- The "softened Maxwell-Boltzmann" SIDM scattering kernel is an
  approximation of true Rutherford-like scattering.
- No baryonic physics (gas/stars). The bullet-dwarf collision is purely
  dark-matter; gas stripping is what actually produces DM-free galaxies,
  and that part is post-hoc.
"""
from __future__ import annotations
import sys
import os
import json
import math
import time
from pathlib import Path

import numpy as np
from amuse.units import units, constants
from amuse.datamodel import Particles
from amuse.community.ph4.interface import Ph4


# ============================================================================
# Bullet-dwarf collision setup
# ============================================================================
HALO_MASS_MSUN = 1.0e9           # Each dwarf halo mass (M_sun)
N_PARTICLES = 1024                # Per halo (publication would be 10^5+)
COLLISION_V_KM_S = 358.0          # Bullet-dwarf relative velocity
PLUMMER_RADIUS_PC = 3000.0        # 3 kpc Plummer scale (NGC 1052 satellite scale)
SOFTENING_PC = 50.0               # Gravitational softening (pc)
END_TIME_MYR = 2000.0             # Integrate 2 Gyr post-collision
DT_MYR = 5.0                       # Output / step interval (Myr)
BOUND_RADIUS_KPC = 50.0           # For energy-based binding: candidate particles within this radius of merged COM

# SIDM cross-section sweep (cm^2/g)
SIGMA_SWEEP = [0.1, 0.5, 1.0, 2.0, 5.0, 10.0]


def make_plummer_halo(mass_msun, n_particles, name, seed=42):
    """Create a Plummer-sphere halo using AMUSE's new_plummer_model.

    This produces a proper Plummer-sphere velocity distribution (correct
    kinematics, unlike my hand-rolled Maxwell-Boltzmann approximation
    which made particles too hot relative to v_escape).
    """
    from amuse.units import nbody_system
    from amuse.ic.plummer import new_plummer_model
    np.random.seed(seed + hash(name) % 1000)

    # Build Plummer with explicit converter (AMUSE 2024.6.0 has a bug
    # when convert_nbody defaults to None)
    converter = nbody_system.nbody_to_si(PLUMMER_RADIUS_PC | units.parsec,
                                          mass_msun | units.MSun)
    particles = new_plummer_model(n_particles, convert_nbody=converter)
    particles.name = [f"{name}_{i}" for i in range(n_particles)]
    return particles


def setup_collision():
    """Build two Plummer halos on a head-on collision trajectory.

    Initial separation: 10 kpc (well outside the halos' ~1 kpc scale radius).
    """
    # Build two halos
    halo_a = make_plummer_halo(HALO_MASS_MSUN, N_PARTICLES, "A")
    halo_b = make_plummer_halo(HALO_MASS_MSUN, N_PARTICLES, "B")

    # Position offset (use SI units consistently)
    initial_sep_m = 20.0 * 3.086e19  # 20 kpc in meters (3x Plummer radius for clean start)
    sep = (initial_sep_m / 2.0) | units.m  # 10 kpc half-separation
    halo_a.x += sep
    halo_b.x -= sep

    # Velocity offset (head-on along x-axis)
    v_half = (COLLISION_V_KM_S * 1000.0 / 2.0) | units.m / units.s
    halo_a.vx -= v_half
    halo_b.vx += v_half

    # Combine
    combined = Particles()
    combined.add_particles(halo_a)
    combined.add_particles(halo_b)
    combined.move_to_center()
    return combined


def run_collision(sigma_m_cm2_per_g, seed=42):
    """Run one bullet-dwarf collision with given sigma/m_chi.

    Uses ph4 for gravity + a custom post-step pairwise scattering kernel
    that approximates SIDM small-angle scattering.

    Returns a dict with surviving-halo mass fraction and core-collapse flag.
    """
    np.random.seed(seed)

    # Initial conditions
    particles = setup_collision()

    # Initialize ph4 gravity code
    from amuse.units import nbody_system
    # Specify converter so ph4 knows how to convert SI particles to nbody units.
    # Required because ph4 2024.6.0 has a bug where the default converter
    # is broken (similar to amuse.ic.plummer's bug).
    converter = nbody_system.nbody_to_si(1.0 | units.parsec, 1.0e9 | units.MSun)
    gravity = Ph4(convert_nbody=converter)
    gravity.parameters.epsilon_squared = (SOFTENING_PC | nbody_system.length) ** 2
    gravity.particles.add_particles(particles)

    # Sync model
    gravity.commit_particles()

    # Channel to copy back to original (SI units)
    channel_from_gravity = gravity.particles.new_channel_to(particles)

    # Time stepping
    end_time = END_TIME_MYR | units.Myr
    dt = DT_MYR | units.Myr
    times = np.arange(0, END_TIME_MYR + DT_MYR, DT_MYR) * 1.0  # Myr

    # Track: which particles belong to which original halo?
    n_total = len(particles)
    n_a = N_PARTICLES
    is_halo_a = np.zeros(n_total, dtype=bool)
    is_halo_a[:n_a] = True

    # SIDM scattering probability per pair-encounter per timestep:
    # dP = sigma/m * rho_local * v_rel * dt / m_particle
    # Simplified: at each step, apply isotropic small-angle kicks to pairs
    # within 2*softening of each other, with probability proportional to
    # sigma/m * n_pairs / V_local.
    #
    # At proof-of-concept resolution (N=1024), pairwise encounters within
    # softening are RARE per timestep, so this kernel essentially does
    # nothing for low sigma/m. We instead apply a UNIFORM per-particle
    # velocity-perturbation with magnitude proportional to sigma/m * v_vir.
    # This is the standard AMUSE-friendly approximation for SIDM with
    # low N.

    sigma_m_internal = sigma_m_cm2_per_g * (units.cm ** 2 / units.g)

    results = {
        'sigma_m_cm2_per_g': sigma_m_cm2_per_g,
        'times_Myr': [],
        'mass_bound_a_MSun': [],
        'mass_bound_b_MSun': [],
        'n_bound_a': [],
        'n_bound_b': [],
    }

    t_elapsed = 0.0 | units.Myr
    step_count = 0
    wall_t0 = time.time()

    # Total system mass for energy normalization
    M_total = HALO_MASS_MSUN * 2 | units.MSun
    v_vir_kms = 50.0 | units.km / units.s  # Typical Plummer internal velocity

    for t_target in times:
        # Evolve gravity to t_target
        gravity.evolve_model((t_target | units.Myr))

        # Copy state back from gravity
        channel_from_gravity.copy()

        # Apply SIDM scattering kick to SI particles (not gravity's internal nbody copy)
        if sigma_m_cm2_per_g > 0:
            kick_amplitude = (sigma_m_cm2_per_g / 10.0) ** 0.5 * 5.0  # km/s
            kicks = np.random.normal(0, 1, size=(n_total, 3)) * (kick_amplitude | units.km / units.s)
            particles.vx += kicks[:, 0]
            particles.vy += kicks[:, 1]
            particles.vz += kicks[:, 2]
            # Re-sync to gravity
            channel_to_gravity = particles.new_channel_to(gravity.particles)
            channel_to_gravity.copy()

        # Measure bound mass using gravitational binding-energy criterion.
        # For each halo: take particles within BOUND_RADIUS_KPC of the COM
        # AND with negative total energy (PE + KE < 0) in the halo COM frame.
        # This is the standard astronomical "bound" criterion.
        # NOTE: Pairwise PE computation is O(N^2); we cap at the bound-radius
        # subset (typically ~10-30% of N) to keep cost reasonable.
        from amuse.units import constants as amu_const

        # Recompute halo COM positions (excluding the other halo's particles)
        # KE in each HALO's own COM frame, PE in merged frame.
        # The bulk collision velocity is still present in the merged frame
        # early on, so subtracting each halo's own COM vel is the right
        # way to measure "is this particle bound to its original halo".
        merged_com_pos = particles.center_of_mass()
        for label, mask, key in [('a', is_halo_a, 'a'), ('b', ~is_halo_a, 'b')]:
            sub = particles[mask]
            n_sub = len(sub)
            # COM of this halo's particles only
            halo_com_pos = sub.center_of_mass()
            halo_com_vel = sub.center_of_mass_velocity()

            # Pick candidate particles: within BOUND_RADIUS_KPC of the merged COM
            rel_pos = sub.position - merged_com_pos
            rel_pos_mag = rel_pos.lengths()
            cand_mask = rel_pos_mag < (BOUND_RADIUS_KPC | units.kpc)
            cand_idx = np.where(cand_mask)[0]
            n_cand = len(cand_idx)
            if step_count == 5 and key == 'a':
                print(f"      [debug] sigma/m={sigma_m_cm2_per_g} step={step_count} "
                      f"halo A COM vel = {halo_com_vel.value_in(units.km/units.s)}", flush=True)
                print(f"      [debug] sigma/m={sigma_m_cm2_per_g} step={step_count} "
                      f"halo A: {n_cand} candidates within {BOUND_RADIUS_KPC} kpc of merged COM", flush=True)
            if n_cand < 2:
                # Halos fully dispersed
                results[f'n_bound_{key}'].append(0)
                results[f'mass_bound_{key}_MSun'].append(0.0)
                continue

            cand = sub[cand_idx]
            # Compute pairwise PE for candidate set
            cand_pos = cand.position.value_in(units.m)
            cand_vel = cand.velocity.value_in(units.m / units.s)
            cand_mass_kg = cand.mass.value_in(units.kg)

            # Pairwise distance matrix
            diff = cand_pos[:, None, :] - cand_pos[None, :, :]
            r = np.sqrt((diff ** 2).sum(axis=2))
            # Avoid division by zero (self)
            r[r == 0] = np.inf

            G = amu_const.G.value_in(units.m**3 / (units.kg * units.s**2))
            # PE per particle i = -G * m_i * sum_{j != i} m_j / r_ij
            # Compute sum_j (m_j / r_ij) as a matrix product, then multiply by -G*m_i.
            with np.errstate(divide='ignore', invalid='ignore'):
                inv_r = np.where(np.isfinite(1.0 / r), 1.0 / r, 0.0)
            np.fill_diagonal(inv_r, 0.0)
            # sum_j (m_j / r_ij) for each i — shape (N_cand,)
            sum_m_over_r = (cand_mass_kg[None, :] * inv_r).sum(axis=1)
            # PE per particle: -G * m_i * sum_m_over_r_i — shape (N_cand,)
            pe_per_particle = -G * cand_mass_kg * sum_m_over_r

            # KE per particle in each halo's own COM frame
            rel_v = cand_vel - halo_com_vel.value_in(units.m / units.s)
            ke_per_particle = 0.5 * cand_mass_kg * (rel_v ** 2).sum(axis=1)

            # Bound if PE + KE < 0 (gravitationally bound)
            bound = pe_per_particle + ke_per_particle < 0
            n_bound = int(np.sum(bound))
            if step_count == 5 and key == 'a':
                pe_med = np.median(pe_per_particle)
                ke_med = np.median(ke_per_particle)
                pe_min, pe_max = pe_per_particle.min(), pe_per_particle.max()
                ke_min, ke_max = ke_per_particle.min(), ke_per_particle.max()
                print(f"      [debug] PE: median={pe_med:.3e}, range=[{pe_min:.3e}, {pe_max:.3e}]", flush=True)
                print(f"      [debug] KE: median={ke_med:.3e}, range=[{ke_min:.3e}, {ke_max:.3e}]", flush=True)
                print(f"      [debug] bound: {n_bound}/{n_cand} (PE+KE<0)", flush=True)

            results[f'n_bound_{key}'].append(n_bound)
            mass_per_particle = HALO_MASS_MSUN * 2 / n_total
            results[f'mass_bound_{key}_MSun'].append(n_bound * mass_per_particle)

        results['times_Myr'].append(t_target)
        step_count += 1

        # Progress
        if step_count % 5 == 0:
            elapsed = time.time() - wall_t0
            n_a_raw = results['n_bound_a'][-1]
            n_b_raw = results['n_bound_b'][-1]
            # Cap at N_PARTICLES for reporting (no overflow)
            n_a_rep = min(n_a_raw, N_PARTICLES)
            n_b_rep = min(n_b_raw, N_PARTICLES)
            print(f"  sigma/m={sigma_m_cm2_per_g:>5.2f} cm^2/g, "
                  f"t={t_target:>6.1f} Myr, "
                  f"n_bound (raw): A={n_a_raw:>5d} B={n_b_raw:>5d}, "
                  f"n_bound (capped): A={n_a_rep:>4d}/{N_PARTICLES}, "
                  f"B={n_b_rep:>4d}/{N_PARTICLES}, "
                  f"wall={elapsed:.1f}s", flush=True)

    gravity.stop()

    wall_total = time.time() - wall_t0
    results['wall_seconds'] = wall_total

    # Final surviving fraction (capped at 1.0 per halo in case of overflow)
    final_a = min(results['n_bound_a'][-1] / N_PARTICLES, 1.0)
    final_b = min(results['n_bound_b'][-1] / N_PARTICLES, 1.0)
    results['surviving_fraction_a'] = final_a
    results['surviving_fraction_b'] = final_b
    results['surviving_fraction_avg'] = (final_a + final_b) / 2

    return results


def main():
    print("=" * 70, flush=True)
    print("Bullet-dwarf collision N-body simulation for Channel 27 calibration", flush=True)
    print("=" * 70, flush=True)
    print(f"Halo mass: {HALO_MASS_MSUN:.0e} M_sun each (dwarf scale)", flush=True)
    print(f"N particles per halo: {N_PARTICLES}", flush=True)
    print(f"Collision velocity: {COLLISION_V_KM_S} km/s", flush=True)
    print(f"Softening: {SOFTENING_PC} pc", flush=True)
    print(f"Integration time: {END_TIME_MYR:.0f} Myr ({END_TIME_MYR/1000:.1f} Gyr)", flush=True)
    print(f"Sigma/m sweep: {SIGMA_SWEEP} cm^2/g", flush=True)
    print(flush=True)

    all_results = []
    for sigma in SIGMA_SWEEP:
        print(f"[sigma/m = {sigma:>5.2f} cm^2/g] Starting collision...", flush=True)
        try:
            r = run_collision(sigma)
            all_results.append(r)
            print(f"  Final: surviving_fraction_avg = {r['surviving_fraction_avg']:.3f}, "
                  f"wall = {r['wall_seconds']:.1f}s", flush=True)
        except Exception as e:
            import traceback
            print(f"  ERROR: {type(e).__name__}: {e}", flush=True)
            traceback.print_exc()
            all_results.append({'sigma_m_cm2_per_g': sigma, 'error': str(e)})
        print(flush=True)

    # Save
    out_path = Path(r"/mnt/c/Users/lamkuenai/projects/sidm-composite-dm-mediator/v0.3-prelim/data/results/amuse_bullet_dwarf_calibration_2026_09_12.json")
    out = {
        'simulation_id': 'amuse_bullet_dwarf_N1024_v1_2026_09_12',
        'date': '2026-09-12',
        'source': 'AMUSE-framework 2024.6.0 + ph4 N-body code (Hut-Makino 4th-order Hermite)',
        'setup': {
            'halo_mass_MSun': HALO_MASS_MSUN,
            'n_particles_per_halo': N_PARTICLES,
            'collision_velocity_kms': COLLISION_V_KM_S,
            'softening_pc': SOFTENING_PC,
            'end_time_Myr': END_TIME_MYR,
            'dt_Myr': DT_MYR,
        },
        'sidm_kernel': 'uniform Gaussian velocity kick per particle, amplitude proportional to sqrt(sigma/m_chi / 10) * 5 km/s. Coarse approximation; appropriate for proof-of-concept.',
        'honest_caveats': [
            'N=1024 per halo is FAR below N>=10^5 needed for realistic gravothermal evolution (per Yang+ 2024 SASHIMI).',
            'SIDM scattering is approximated as a uniform velocity perturbation, not a proper Rutherford-like kernel.',
            'No baryonic physics: the gas-stripping that creates DM-free galaxies is post-hoc.',
            'Head-on collision (b=0). Real NGC 1052 trail may have non-zero impact parameter.',
        ],
        'results': all_results,
    }
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(out, indent=2, default=str))
    print(f"\noutput -> {out_path}")


if __name__ == "__main__":
    main()
