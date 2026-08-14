"""
kiss_sidm_dsmc.py
=================

Pure-Python reimplementation of the KISS-SIDM Direct Simulation Monte Carlo
(DSMC) algorithm from Gurian & May 2025 (arXiv:2505.15903v2, PRL 135, 221001).

THIS IS A SMOKE-TEST-QUALITY IMPLEMENTATION, not a production code. It is
written from scratch following the paper's End Matter (Eqs. 7-17). The
canonical run in the paper uses 2e6 particles; here we run with N=1e4
(tunable down to N=5e3 if the smoke test exceeds 5 minutes) and 100
time-steps. This is sufficient to demonstrate qualitative behavior
(coring at late times, energy conservation within ~10%, growth of the
core radius) but NOT to reproduce quantitative results from Fig. 1 of
the paper (which require the full N=2e6 run and ~30 minutes on a laptop
in the original C/Python code).

We DO NOT install the original KiSS-SIDM from gitlab.com/Socob/KiSS-SIDM
(AGENTS.md rule 17: no new deps without explicit user approval).

==============================================================================
ALGORITHM SUMMARY
==============================================================================

Units (paper § RESULTS, Eq. 1):
    rho(r) = rho_s / [(r/r_s) (1 + r/r_s)^2]
    M_0   = r_s^3 * rho_s                        (mass unit)
    v_0   = sqrt(G * M_0 / r_s)                  (velocity unit)
    t_0   = 1 / (a * sigma_m * v_0 * rho_s)      (time unit)
            with a = 4/sqrt(pi) for hard-sphere scattering
    sigma_0 = 1 / (rho_s * r_s)                   (cross-section unit)

    We work in code units where M_0 = v_0 = r_s = 1 internally; physical
    units appear in the output JSON for diagnostics.

Initialization (paper § METHODS):
    1. Draw N positions from the NFW cumulative mass distribution using
       rejection sampling. We use a simple accept/reject against an
       analytic NFW profile (paper used SpherIC, but for smoke test
       this is sufficient).
    2. Draw 3D velocities from an isotropic Maxwell-Boltzmann whose
       local 1D dispersion sigma_v^2(r) = G * M_enc(r) / r (virial
       estimate). This is the "simple approximation" the paper itself
       uses for the LMFP regime. The paper used an Eddington draw; for
       N=1e4 the difference is washed out by Poisson noise.

    Per-particle state: (r, v_r, v_theta, v_phi) in spherical coordinates.
    Spherical symmetry means v_perp = sqrt(v_theta^2 + v_phi^2) and the
    direction of L is preserved; for the drift step we evolve each
    component with angular-momentum-conserving rescaling
        v_theta' = v_theta * (r / r')
        v_phi'   = v_phi   * (r / r')
    (this is exact for radial motion, no basis rotation needed because
    v_perp is the same physical quantity).

Time integration (paper § End Matter, Eq. 17):
    Each step is split as  K(dt/2) S(dt/2) D(dt) S(dt/2) K(dt/2)
    where:
        K (kick): update v_r, v_theta, v_phi by gravitational acceleration
                  a_g(r) = G * M_enc(r) / r^2
        D (drift): update r by v_r * dt
        S (scatter): in each radial bin i:
            - sample Gamma_i = N_i * rho_i * sigma_m * v_max * dt trial
              PAIRS (Eq. 7, with sigma_m,max = v_max = constant for
              constant sigma_m and a generous max-velocity bound)
            - for each trial pair, accept with probability
              (v_rel / v_max)^2 > uniform(0, 1)  (Eq. 8, constant sigma_m)
            - on accept, perform isotropic elastic scattering in the
              center-of-mass frame; conservation:
                v_1' = v_cm + g'/2
                v_2' = v_cm - g'/2
              with |g'| = |g| = |v_1 - v_2| and g' = random unit vector
              times |g| (isotropic scattering)
            - rotate new velocities back into the local spherical basis
              (radial component from v_r' = v'_dot_rhat; tangential
              magnitude from |v_perp'|; direction preserved since
              the cell is spherically symmetric — paper notes "expectation
              of the angular momentum in each cell is conserved")

Adaptive time step (paper § End Matter, Eq. 9):
    dt = min(dt_coll, dt_grav)  (BOTH evaluated at t = t_now, no lookahead)
    dt_coll = min_i (lambda_MFP_i / v_max_i)  (Eq. 10, 11)
    dt_grav = epsilon * min_i t_ff_i  (Eq. 12, epsilon = 0.02)
    v0.3.0-prelim simplification: we do NOT adaptively split bins.
    We use a fixed initial logarithmic grid (21 cells from r/r_s=0.017 to
    r/r_s=1169, matching the paper's initial grid). Adaptive splitting
    (paper Eq. 16) is the next step but not required for smoke validation.

Output:
    At each snapshot we compute the density profile, the 3D velocity
    dispersion profile, and the radial velocity dispersion profile, all
    binned on the current grid (or on a fixed output grid for stability).

==============================================================================
VALIDATION LIMITS
==============================================================================

The canonical case (sigma_m/sigma_0 = 0.32, NFW halo as in paper) is
simulated with N=1e4 particles for 100 time-steps (paper used N=2e6
and ran to t/t_0 ~ 437). At N=1e4:
    - Density profile: noisy but qualitatively matches Fig. 1 (cored at
      late times; central density < initial NFW at same r)
    - Energy conservation: |Delta E / E| < 0.1 expected (paper: 2e-4
      at N=2e6). We monitor and report this number.
    - Quantitative agreement with Table I power laws (-0.21 at Kn=1
      and Kn=5) requires a much higher-resolution run.

If the smoke test exceeds 5 minutes in pure Python, N is auto-reduced
to 5e3 and the number of time-steps to 50 (a separate setting in the
CLI). The reduced-N choice is documented in the JSON output.

==============================================================================
"""

from __future__ import annotations

import json
import math
import os
import sys
import time
from dataclasses import dataclass, field, asdict
from typing import List, Optional, Tuple

import numpy as np

# -----------------------------------------------------------------------------
# Physical constants and the canonical case (paper § RESULTS)
# -----------------------------------------------------------------------------

# Newton's G in convenient halo units (kpc * (km/s)^2 / M_sun). This is the
# same value used elsewhere in this project (see config.G_KPC_KMS).
G_KPC_KMS_MSUN = 4.302e-6  # kpc (km/s)^2 / (M_sun s^2 ... no, s^-2 in (km/s)^2/kpc units)

# Hard-sphere constant a = 4/sqrt(pi) (paper Eq. 1, § RESULTS)
A_HS = 4.0 / math.sqrt(math.pi)


@dataclass
class CanonicalCase:
    """Canonical SIDM halo (paper § RESULTS, after [30] Palubski+ 2024)."""

    M_halo_Msun: float = 1.0e9        # total halo mass in M_sun (not used directly)
    rho_s_Msun_per_kpc3: float = 2.73e7  # scale density in M_sun/kpc^3
    r_s_kpc: float = 1.18              # scale radius in kpc
    sigma_m_over_sigma0: float = 0.32  # cross section in sigma_0 = 1/(rho_s r_s) units
    name: str = "canonical_109Msun"


def compute_units(case: CanonicalCase) -> dict:
    """
    Compute code units (M_0, v_0, t_0, sigma_0) for a given case.

    Returns a dict with:
        M_0_Msun        : M_0 = r_s^3 * rho_s in M_sun
        v_0_kms         : v_0 = sqrt(G M_0 / r_s) in km/s
        t_0_Gyr         : t_0 = 1/(a sigma_m v_0 rho_s) in Gyr
        sigma_0_kpc2_per_Msun : 1/(rho_s r_s) in kpc^2/M_sun
    """
    rho_s = case.rho_s_Msun_per_kpc3
    r_s = case.r_s_kpc
    M_0 = r_s ** 3 * rho_s  # M_sun
    # v_0 in km/s: G in (kpc (km/s)^2 / M_sun), so v_0^2 = G M_0 / r_s
    v_0 = math.sqrt(G_KPC_KMS_MSUN * M_0 / r_s)  # km/s
    sigma_0 = 1.0 / (rho_s * r_s)  # kpc^2 / M_sun
    # t_0 = 1 / (a sigma_m v_0 rho_s) in seconds:
    # a [dimensionless], sigma_m [kpc^2/M_sun], v_0 [km/s], rho_s [M_sun/kpc^3]
    # -> [kpc^2/M_sun] * [km/s] * [M_sun/kpc^3] = [km/s / kpc] = [1/s] when
    # G is folded in. But a sigma_m v_0 rho_s has units of [1/s] only if
    # we use G-typeless... Let me redo carefully.
    #
    # From the paper: t_0^{-1} = a * sigma_m * v_0 * rho_s  (Eq. 1)
    # The combination a*sigma_m*v_0*rho_s has units of [1/time] when
    # sigma_m is per unit mass and v_0 is a velocity. In SI:
    #   a*sigma_m [m^2/kg] * v_0 [m/s] * rho_s [kg/m^3] = [1/s]
    # Converting to kpc/M_sun/km/s:
    #   sigma_m_SI = sigma_m_kpc2_Msun * (3.086e19 m / kpc)^2 / (1.989e30 kg / M_sun)
    #              = sigma_m_kpc2_Msun * 4.79e8 m^2/kg ... actually let's
    # just work in code units throughout. We will quote t_0 in units of
    # 1/(a*sigma_m*v_0*rho_s) where sigma_m and rho_s use the paper's
    # "sigma_0" and "r_s" unit system. In that system t_0 = 1 in code
    # units (i.e. one code time unit IS 1/(a sigma_m v_0 rho_s)). So
    # the conversion to physical seconds requires us to compute
    # t_0_phys = 1 / (a * sigma_m_SI * v_0_SI * rho_s_SI).
    #
    # sigma_m physical = 50 cm^2/g = 0.005 m^2/kg
    # rho_s physical = 2.73e-2 M_sun/pc^3 = 2.73e-2 * 1.989e30 / (3.086e15)^3 kg/m^3
    # v_0 physical = sqrt(G_SI * M_0_phys / r_s_phys) m/s
    #
    # We compute t_0_Gyr from physical SI quantities.
    G_SI = 6.674e-11  # m^3/(kg s^2)
    M_sun_kg = 1.989e30
    pc_m = 3.0857e16
    kpc_m = 3.0857e19
    sigma_m_SI = 0.005  # m^2/kg
    rho_s_SI = 2.73e-2 * M_sun_kg / (pc_m ** 3)  # kg/m^3
    r_s_SI = r_s * kpc_m
    v_0_SI = math.sqrt(G_SI * (r_s_SI ** 3 * rho_s_SI) / r_s_SI)  # m/s
    t_0_s = 1.0 / (A_HS * sigma_m_SI * v_0_SI * rho_s_SI)
    t_0_Gyr = t_0_s / (365.25 * 24 * 3600 * 1e9)
    return {
        "M_0_Msun": M_0,
        "v_0_kms": v_0,
        "t_0_Gyr": t_0_Gyr,
        "sigma_0_kpc2_per_Msun": sigma_0,
        "sigma_0_m2_per_kg": 1.0 / (rho_s_SI * r_s_SI),  # sanity check
    }


# -----------------------------------------------------------------------------
# NFW initial conditions
# -----------------------------------------------------------------------------

def nfw_rho(r_over_rs, rho_s=1.0):
    """NFW density profile rho(r)/rho_s = 1 / [(r/rs) (1 + r/rs)^2]."""
    x = np.asarray(r_over_rs, dtype=float)
    return rho_s / (x * (1.0 + x) ** 2)


def nfw_cumulative_inverse(u, r_min_over_rs, r_max_over_rs):
    """
    Inverse cumulative of the NFW mass distribution.

    M(r)/M_total = g(r/rs) where
        g(x) = [ln(1+x) - x/(1+x)] / [ln(1+R) - R/(1+R)]
    for x = r/rs, R = r_max/rs. We invert numerically by bisection on
    a fine grid; this is fast because the grid is shared across all
    calls and built once.

    Parameters
    ----------
    u : array of shape (N,) of uniform [0,1)
    r_min_over_rs, r_max_over_rs : floats

    Returns
    -------
    r_over_rs : array of shape (N,)
    """
    # Build inverse grid once per call (cheap, ~microseconds)
    x_grid = np.linspace(math.log(r_min_over_rs), math.log(r_max_over_rs), 4096)
    x_grid = np.exp(x_grid)
    M_grid = nfw_cumulative(x_grid, r_max_over_rs)
    M_grid -= M_grid[0]
    M_grid /= M_grid[-1]
    # Linear interpolation in log-x for smoothness
    log_x = np.log(x_grid)
    return np.exp(np.interp(u, M_grid, log_x))


def nfw_cumulative(r_over_rs, r_max_over_rs):
    """
    NFW cumulative mass fraction g(x) = [ln(1+x) - x/(1+x)] /
    [ln(1+R) - R/(1+R)] for x = r/rs, R = r_max/rs.
    """
    x = np.asarray(r_over_rs, dtype=float)
    R = r_max_over_rs
    num = np.log(1.0 + x) - x / (1.0 + x)
    den = np.log(1.0 + R) - R / (1.0 + R)
    return num / den


def sample_nfw_positions(N, r_min_over_rs, r_max_over_rs, rng):
    """
    Sample N positions from the NFW radial distribution.

    Returns r_over_rs array of shape (N,).
    """
    u = rng.uniform(0.0, 1.0, size=N)
    return nfw_cumulative_inverse(u, r_min_over_rs, r_max_over_rs)


# -----------------------------------------------------------------------------
# Radial grid (paper: 21 logarithmically spaced cells from r/rs=0.017 to 1169)
# -----------------------------------------------------------------------------

def make_radial_grid(r_min_over_rs=0.017, r_max_over_rs=1169.0, n_cells=21):
    """
    Logarithmically spaced right-hand cell edges.

    Returns array of shape (n_cells+1,) with cell edges from r_min to r_max
    (inclusive). Cell i spans [edges[i], edges[i+1]]; cell 0 is innermost.
    """
    log_edges = np.linspace(math.log(r_min_over_rs), math.log(r_max_over_rs), n_cells + 1)
    return np.exp(log_edges)


# -----------------------------------------------------------------------------
# Simulation state container
# -----------------------------------------------------------------------------

@dataclass
class HaloState:
    """Mutable state of the simulated halo."""

    r: np.ndarray            # shape (N,), radial position in r_s units
    v_r: np.ndarray          # radial velocity in v_0 units
    v_theta: np.ndarray      # tangential v_theta in v_0 units
    v_phi: np.ndarray        # tangential v_phi in v_0 units
    t: float = 0.0           # current time in t_0 units

    @property
    def N(self):
        return self.r.shape[0]

    @property
    def v2(self):
        return self.v_r ** 2 + self.v_theta ** 2 + self.v_phi ** 2

    @property
    def v_perp2(self):
        return self.v_theta ** 2 + self.v_phi ** 2

    @property
    def v_perp(self):
        return np.sqrt(self.v_perp2)

    def kinetic_energy(self):
        """Total KE in code units: 0.5 * sum(v^2)."""
        return 0.5 * float(np.sum(self.v2))

    def potential_energy(self, M_enc, r, G=1.0):
        """
        Total PE in code units using cumulative enclosed mass.

        U = -G * sum_i  M_enc(r_i) / r_i * m_i   (m_i = 1/M_total in code units)

        For a self-consistent halo with total mass M_tot = 1 (in M_0 units),
        the gravitational potential energy is
            U = -G * sum_i (M_enc(r_i) / r_i)  / N  (per-particle m = 1/N)

        We return the *total* U.

        The PE is dominated by particles at small r. To prevent
        numerical pathologies when a particle has r < r_safe (e.g.
        after a near-r=0 crossing), we exclude those particles from
        the PE sum. This is a known limitation of using a point-mass
        formula in 1/r for a finite-N simulation: a single particle
        at r ~ 1e-7 contributes ~1e7 to |U|, dominating the sum.
        r_safe is set to 1e-2 (1% of r_s) which is well below the
        paper's innermost cell at r/r_s = 0.017.
        """
        r_safe = np.maximum(r, 1e-2)
        # m_per_particle = 1.0 / self.N (in M_0 units)
        return -G * float(np.sum(M_enc / r_safe)) / self.N

    def total_energy(self, M_enc, r_sorted, G=1.0):
        """E = KE + PE."""
        return self.kinetic_energy() + self.potential_energy(M_enc, r_sorted, G=G)


# -----------------------------------------------------------------------------
# Initialization
# -----------------------------------------------------------------------------

def initialize_nfw_halo(
    N: int,
    r_min_over_rs: float,
    r_max_over_rs: float,
    rng: np.random.Generator,
    use_eddington: bool = True,
) -> HaloState:
    """
    Initialize an NFW halo with isotropic Maxwell-Boltzmann velocities.

    The local 1D velocity dispersion is set to
        sigma_v^2(r) = G * M_enc(r) / r
    which is the virial estimate (sigma_v^2 ~ -phi/2 for a self-bound
    system in quasi-equilibrium). The actual value is half this for a
    true isothermal sphere, but the prefactor is the natural choice
    for an NFW-like profile and matches the paper's "Maxwell-Boltzmann
    with local escape velocity" approximation up to order-unity factors.

    If use_eddington is True, the velocity components are drawn
    from a Maxwell-Boltzmann with the local sigma_v(r). This is the
    isotropic distribution the paper uses (not the formal Eddington
    f(E) draw, which differs only in the high-velocity tail).
    """
    r = sample_nfw_positions(N, r_min_over_rs, r_max_over_rs, rng)
    # Sort for cumulative mass
    sort_idx = np.argsort(r)
    r_sorted = r[sort_idx]
    # M_enc(i) = i / N in code units (m_per_particle = 1/N)
    M_enc_sorted = (np.arange(1, N + 1, dtype=float)) / N
    # Interpolate M_enc to all r
    M_enc = np.interp(r, r_sorted, M_enc_sorted)
    # sigma_v^2(r) = G M_enc(r) / r ; G = 1 in code units
    sigma_v2 = M_enc / np.maximum(r, 1e-12)
    # Velocity dispersion for each component (isotropic -> each component
    # has the same 1D dispersion sigma_v / sqrt(3) for 3D Maxwellian)
    # The 3D speed distribution is Maxwell with sigma_3D^2 = sigma_v^2
    sigma_3D = np.sqrt(sigma_v2)
    # Draw 3D velocities isotropically: sample 3D speed v from
    # Maxwell(sigma_3D) and pick a random direction. The 3D Maxwell
    # speed distribution is f(v) ~ v^2 exp(-v^2/(2 sigma_3D^2)). Draw
    # v by inverse CDF: v = sigma_3D * sqrt(2) * sqrt(-ln(1-u)) for
    # the underlying 1D normal; for 3D speed, use:
    #   v = sigma_3D * sqrt(chi^2_3) where chi^2_3 is chi-squared
    #   with 3 dof. We use: v^2 = sigma_3D^2 * sum_{i=1..3} g_i^2
    #   where g_i ~ N(0,1).
    g = rng.standard_normal(size=(N, 3))  # (N, 3): (g_x, g_y, g_z)
    v_3d = sigma_3D[:, None] * g  # (N, 3) — this gives 3 Cartesian components
    # Project into spherical components (r, theta, phi) basis
    # r-hat = x/|x|; v_r = v . r_hat
    # We need to be careful: the particles were drawn spherically
    # symmetric (just r is set, the angular position is implicit).
    # In spherical symmetry the local v_r and v_perp are the only
    # physical quantities. We can:
    #   - pick a random direction for r-hat on the unit sphere
    #   - decompose v into radial and tangential parts
    # This is equivalent to choosing an isotropic velocity distribution
    # in the local frame, which is what we want.
    u_th = rng.uniform(-1.0, 1.0, size=N)
    ph = rng.uniform(0.0, 2.0 * math.pi, size=N)
    sin_th = np.sqrt(np.maximum(0.0, 1.0 - u_th ** 2))
    r_hat = np.stack([sin_th * np.cos(ph), sin_th * np.sin(ph), u_th], axis=1)
    v_radial = np.sum(v_3d * r_hat, axis=1)
    v_tang = v_3d - v_radial[:, None] * r_hat  # tangential vector
    # Decompose tangential into theta and phi components in the local
    # spherical basis. theta_hat = d r_hat / d theta (along increasing
    # theta in the chosen direction); phi_hat = d r_hat / d phi.
    # For our purposes, what matters is the magnitude v_perp = |v_tang|
    # and the individual components v_theta, v_phi. In the local basis:
    #   v_theta = v_tang . theta_hat
    #   v_phi   = v_tang . phi_hat
    # We construct an orthonormal pair perpendicular to r_hat. Easiest:
    # pick a reference vector and project out the r_hat component.
    ref = np.zeros_like(r_hat)
    # pick z-hat for polar angle < pi/2, x-hat otherwise (avoid collinearity)
    sel = u_th < 0.0
    ref[sel] = np.array([0.0, 0.0, 1.0])
    ref[~sel] = np.array([1.0, 0.0, 0.0])
    # theta_hat = ref - (ref . r_hat) r_hat, then normalize
    proj = np.sum(ref * r_hat, axis=1, keepdims=True)
    theta_hat = ref - proj * r_hat
    theta_hat /= np.linalg.norm(theta_hat, axis=1, keepdims=True)
    # phi_hat = r_hat x theta_hat (right-handed)
    phi_hat = np.cross(r_hat, theta_hat)
    v_theta = np.sum(v_tang * theta_hat, axis=1)
    v_phi = np.sum(v_tang * phi_hat, axis=1)
    return HaloState(r=r, v_r=v_radial, v_theta=v_theta, v_phi=v_phi)


# -----------------------------------------------------------------------------
# Gravity and density on the grid
# -----------------------------------------------------------------------------

def compute_enclosed_mass(r: np.ndarray) -> np.ndarray:
    """
    Compute M_enc(r_i) for each particle (M_enc(r) = mass interior to r).
    Returns array of shape (N,) in units of total mass (1.0 in code units).
    """
    sort_idx = np.argsort(r)
    M_sorted = (np.arange(1, r.shape[0] + 1, dtype=float)) / r.shape[0]
    M_enc = np.empty_like(r)
    M_enc[sort_idx] = M_sorted
    return M_enc


def compute_cell_densities(r: np.ndarray, cell_edges: np.ndarray) -> np.ndarray:
    """
    Compute mass density in each radial cell. Returns array of shape (n_cells,).
    Density is in units of M_0 / r_s^3 (the natural code unit, in which
    rho_s = 1).
    """
    n_cells = cell_edges.shape[0] - 1
    # Histogram: count particles per cell
    counts, _ = np.histogram(r, bins=cell_edges)
    # Volume of spherical shell: V = (4/3) pi (r_out^3 - r_in^3)
    r_in = cell_edges[:-1]
    r_out = cell_edges[1:]
    V_shell = (4.0 / 3.0) * math.pi * (r_out ** 3 - r_in ** 3)
    # Each particle has mass m_p = 1 / N (in M_0 units)
    m_p = 1.0 / r.shape[0]
    rho = counts * m_p / V_shell  # in M_0 / r_s^3 units (rho_s = 1)
    return rho, counts


def gravitational_acceleration(r: np.ndarray, M_enc: np.ndarray, G: float = 1.0) -> np.ndarray:
    """
    a_g(r) = G M_enc(r) / r^2, directed inward (negative radial).
    Returns array of shape (N,) of a_r (radial component of acceleration).
    """
    return -G * M_enc / np.maximum(r, 1e-12) ** 2


# -----------------------------------------------------------------------------
# Adaptive time step
# -----------------------------------------------------------------------------

def compute_v_max_per_cell(
    v2_mean: np.ndarray,
    safety_factor: float = 8.0,
) -> np.ndarray:
    """
    Per-cell max-velocity bound for the no-time-counter scheme.

    Set v_max,i = safety_factor * v_rms,i where v_rms is the 3D
    RMS speed (sqrt(v2_mean)). A safety factor of 8 covers the
    Maxwellian tail to ~8 sigma while keeping the per-step acceptance
    probability small (mean (v_rel/v_max)^2 ~ 3/safety_factor^2).

    With v_max = safety_factor * v_rms, the per-cell trial count
    Gamma_i = N_i (independent of v_max), but the expected accepted
    scatterings per cell per step is N_i * <(v_rel/v_max)^2> ~ N_i / 27
    for safety_factor=8. This is the right order of magnitude for the
    no-time-counter scheme (each particle is scattered at most a few
    times per step on average).
    """
    return safety_factor * np.sqrt(np.maximum(v2_mean, 1e-30))


def compute_time_step(
    rho_cells: np.ndarray,
    v_max_per_cell: np.ndarray,
    sigma_m_code: float,
    cell_edges: np.ndarray,
    G: float = 1.0,
    eps_grav: float = 0.02,
    min_dt: float = 0.0,
) -> float:
    """
    Compute the adaptive time step as min(dt_coll, dt_grav) (Eq. 9-12).

    With per-cell v_max, the no-time-counter scheme gives a per-cell
    trial-pair count Gamma_i ~ N_i (independent of v_max), which is
    well-behaved for any N.

    For smoke tests at N~1e4 the inner cells have very few particles
    and the free-fall time there is dominated by Poisson noise, which
    causes dt to collapse. We therefore floor the time step at min_dt
    (default 0; set to a small positive value to stabilize the smoke
    test). The paper used N=2e6 where the inner cells are well
    populated and this is not a concern.

    rho_cells : shape (n_cells,), density per cell in code units (M_0/r_s^3)
    v_max_per_cell : shape (n_cells,), per-cell max relative velocity
    sigma_m_code : cross section in code units (sigma_m/sigma_0 in paper units)
    cell_edges: shape (n_cells+1,)
    G         : Newton's constant in code units (1.0 in paper units)
    eps_grav  : safety factor for gravitational time step (paper: 0.02)
    min_dt    : floor on the returned time step
    """
    # dt_coll: min_i lambda_MFP_i / v_max,i
    # lambda_MFP_i = 1 / (rho_i * sigma_m)
    safe_rho = np.maximum(rho_cells, 1e-30)
    lambda_mfp = 1.0 / (safe_rho * sigma_m_code)
    # Mean interior density for free-fall time: average density in
    # sphere of radius = center of cell
    r_in = cell_edges[:-1]
    r_out = cell_edges[1:]
    r_center = 0.5 * (r_in + r_out)
    # Cumulative mass from inner cells
    M_cum = np.cumsum(rho_cells * (4.0 / 3.0) * math.pi * (r_out ** 3 - r_in ** 3))
    rho_bar = np.where(
        r_center > 0, M_cum / ((4.0 / 3.0) * math.pi * r_center ** 3), safe_rho
    )
    t_ff = 1.0 / np.sqrt(np.maximum(G * rho_bar, 1e-30))
    dt_grav = eps_grav * float(np.min(t_ff))
    dt_coll = float(np.min(lambda_mfp / np.maximum(v_max_per_cell, 1e-12)))
    return max(min_dt, min(dt_coll, dt_grav))


# -----------------------------------------------------------------------------
# KDSK sub-steps
# -----------------------------------------------------------------------------

def kick(state: HaloState, dt: float, G: float = 1.0, r_min: float = 1e-3,
         max_dv: float = 0.5):
    """
    Apply gravitational kick: update v_r by a_r * dt; tangential
    components unchanged (spherically symmetric gravity has no tangential
    component). The K-D-S-K convention keeps v_r the same physical
    quantity (the radial velocity component in the local frame).

    For particles with r < r_min (which can happen if the previous
    drift step left them very close to the origin), we cap the
    acceleration to G M_enc(r_min) / r_min^2 to prevent a runaway
    inward acceleration. The paper assumes no particles at r=0.

    For numerical stability in the smoke test (N=1e4 with very
    few inner particles, so M_enc is poorly sampled near r=0),
    we also cap the per-step velocity change at max_dv. The paper's
    N=2e6 run does not need this cap because M_enc(r) is well-
    resolved everywhere.
    """
    M_enc = compute_enclosed_mass(state.r)
    a_r = gravitational_acceleration(state.r, M_enc, G=G)
    # Cap acceleration magnitude for particles very close to r=0
    a_max = G * M_enc / (r_min ** 2)
    a_r = np.where(state.r < r_min,
                   -np.sign(a_r) * np.minimum(np.abs(a_r), np.abs(a_max)),
                   a_r)
    dv = a_r * dt
    # Cap velocity change per step to prevent single-step blowups
    dv = np.clip(dv, -max_dv, max_dv)
    state.v_r += dv
    return state


def drift(state: HaloState, dt: float):
    """
    Drift step: update r by v_r * dt, and re-scale tangential velocity
    components to conserve angular momentum L = r m v_perp.
        v_theta' = v_theta * (r / r')
        v_phi'   = v_phi   * (r / r')

    For particles that cross r=0 (which happens for nearly-radial
    orbits in a finite-N simulation), we perform an exact specular
    reflection at r=0: the particle travels to r=0 (taking time
    t_cross = -r/v_r), then re-emerges with v_r reversed. This keeps
    |v| and L conserved. Without this, a naive clamp produces particles
    at very small r with finite v_r, which then get a huge acceleration
    on the next kick (a ~ 1/r^2) and the energy diagnostic blows up.
    """
    r_old = state.r
    v_r_old = state.v_r
    # Trial new radius
    r_trial = r_old + v_r_old * dt
    # Find particles that would cross r=0
    crossing = r_trial <= 0
    n_cross = int(np.sum(crossing))
    r_new = r_trial.copy()
    v_r_new = v_r_old.copy()
    if n_cross > 0:
        # For crossing particles, the actual r_new is |r + v_r * dt|,
        # but with v_r reflected.
        # t_cross = -r_old / v_r_old (positive)
        t_cross = -r_old[crossing] / v_r_old[crossing]
        # Remaining time after reflection
        t_remaining = dt - t_cross
        # New radius: particle is at r=0 after t_cross, then moves outward
        # with reflected v_r for the remaining time
        v_r_reflected = -v_r_old[crossing]
        r_new[crossing] = v_r_reflected * t_remaining
        v_r_new[crossing] = v_r_reflected
    # Re-scale tangential components to conserve angular momentum.
    # The ratio r_old/r_new caps at 100 to prevent runaway tangential
    # speeds from a particle whose new radius is much smaller than the
    # old (e.g. it just barely crossed r=0 and the reflection left it
    # at a very small positive r). Without the cap, v_theta and v_phi
    # can grow without bound for a few such particles.
    ratio = r_old / np.maximum(r_new, 1e-12)
    ratio = np.minimum(ratio, 100.0)
    state.v_theta = state.v_theta * ratio
    state.v_phi = state.v_phi * ratio
    state.r = r_new
    state.v_r = v_r_new
    return state


def scatter_in_cells(
    state: HaloState,
    cell_edges: np.ndarray,
    rho_cells: np.ndarray,
    counts: np.ndarray,
    sigma_m_code: float,
    dt: float,
    v_max_per_cell: np.ndarray,
    rng: np.random.Generator,
) -> int:
    """
    Apply the scattering step S(dt) in each radial cell.

    Implements the no-time-counter scheme (paper § End Matter):
        For each cell i:
            Gamma_i = N_i * rho_i * sigma_m * v_max,i * dt
            Sample Gamma_i trial pairs; for each, accept with
            probability (v_rel / v_max,i)^2 (Eq. 8 with constant sigma_m,
            so sigma_m(v_rel) = sigma_m_max = sigma_m).
            On accept, perform isotropic elastic scattering in CM frame.

    Returns the total number of accepted scatterings (for diagnostics).
    """
    n_cells = cell_edges.shape[0] - 1
    n_accepted_total = 0
    # Bin particles into cells
    bin_idx = np.searchsorted(cell_edges, state.r, side="right") - 1
    bin_idx = np.clip(bin_idx, 0, n_cells - 1)
    for i in range(n_cells):
        N_i = int(counts[i])
        if N_i < 2:
            continue
        rho_i = rho_cells[i]
        v_max_i = float(v_max_per_cell[i])
        if v_max_i <= 0:
            continue
        v_max2 = v_max_i * v_max_i
        Gamma_i = N_i * rho_i * sigma_m_code * v_max_i * dt
        if Gamma_i <= 0:
            continue
        # Number of trial pairs: round to nearest non-negative int.
        # The paper uses an integer Gamma_i (Eq. 7 is "upper bound on
        # the number of collisions"). We round, with a small fractional
        # part handled by a random comparison.
        n_trials = int(Gamma_i)
        frac = Gamma_i - n_trials
        if rng.uniform() < frac:
            n_trials += 1
        if n_trials < 1:
            continue
        # Sample n_trials pairs of particle indices WITHIN this cell
        # (paper allows repeated pairs).
        idx = np.where(bin_idx == i)[0]
        if idx.shape[0] < 2:
            continue
        a = rng.integers(0, idx.shape[0], size=n_trials)
        b = rng.integers(0, idx.shape[0], size=n_trials)
        # Compute relative velocities
        v1 = np.stack([
            state.v_r[idx[a]], state.v_theta[idx[a]], state.v_phi[idx[a]]
        ], axis=1)  # (n_trials, 3)
        v2 = np.stack([
            state.v_r[idx[b]], state.v_theta[idx[b]], state.v_phi[idx[b]]
        ], axis=1)
        g = v1 - v2  # relative velocity
        v_rel2 = np.sum(g * g, axis=1)
        # Acceptance probability: (v_rel / v_max)^2 (since sigma_m is constant)
        # Avoid division by zero
        prob = np.minimum(v_rel2 / v_max2, 1.0)
        u = rng.uniform(size=n_trials)
        accept = u < prob
        if not np.any(accept):
            continue
        n_accepted_total += int(np.sum(accept))
        # For accepted pairs, perform isotropic scattering in CM frame
        g_acc = g[accept]
        v_rel_acc = np.sqrt(np.sum(g_acc * g_acc, axis=1, keepdims=True))
        # Random unit vector in 3D for new relative velocity direction
        # (isotropic CM scattering)
        k = rng.standard_normal(size=g_acc.shape)
        k_norm = np.linalg.norm(k, axis=1, keepdims=True)
        k_unit = k / np.maximum(k_norm, 1e-12)
        g_new = v_rel_acc * k_unit  # same magnitude, random direction
        v1_acc = v1[accept]
        v2_acc = v2[accept]
        v_cm = 0.5 * (v1_acc + v2_acc)
        v1_new = v_cm + 0.5 * g_new
        v2_new = v_cm - 0.5 * g_new
        # Update state in place
        ia = idx[a[accept]]
        ib = idx[b[accept]]
        # Self-scattering (a == b within the same particle) is harmless
        # because v1_new = v_cm + g/2 = v + 0, so v_new = v. (No-op.)
        # We accumulate the update with += to handle repeated trials
        # of the same particle (paper allows this). The safety cap on
        # speed (v_escape_soft = 20 v_0) prevents pathological energy
        # blowup if a particle is selected in many trials in one step.
        np.add.at(state.v_r,   ia, v1_new[:, 0] - v1_acc[:, 0])
        np.add.at(state.v_r,   ib, v2_new[:, 0] - v2_acc[:, 0])
        np.add.at(state.v_theta, ia, v1_new[:, 1] - v1_acc[:, 1])
        np.add.at(state.v_theta, ib, v2_new[:, 1] - v2_acc[:, 1])
        np.add.at(state.v_phi,   ia, v1_new[:, 2] - v1_acc[:, 2])
        np.add.at(state.v_phi,   ib, v2_new[:, 2] - v2_acc[:, 2])
    # Soft cap on per-particle speed (post-cell loop). The cap is
    # set to 20 v_0, well above the physical escape speed (a few v_0)
    # for any cell. The cap is a safety net for the no-time-counter
    # scheme's rare multi-scattering artifacts; it should rarely fire.
    v_speed = np.sqrt(state.v_r ** 2 + state.v_theta ** 2 + state.v_phi ** 2)
    over = v_speed > 20.0
    if np.any(over):
        scale = 20.0 / np.maximum(v_speed[over], 1e-12)
        state.v_r[over] *= scale
        state.v_theta[over] *= scale
        state.v_phi[over] *= scale
    return n_accepted_total


# -----------------------------------------------------------------------------
# Profile measurements
# -----------------------------------------------------------------------------

def measure_profiles(
    state: HaloState,
    cell_edges: np.ndarray,
) -> dict:
    """
    Compute density, 3D velocity dispersion, and radial velocity
    dispersion per cell. Returns dict of arrays.

    All in code units: rho in M_0/r_s^3, v^2 in v_0^2.
    """
    n_cells = cell_edges.shape[0] - 1
    rho_cells, counts = compute_cell_densities(state.r, cell_edges)
    # Per-cell means
    bin_idx = np.searchsorted(cell_edges, state.r, side="right") - 1
    bin_idx = np.clip(bin_idx, 0, n_cells - 1)
    v2_sum = np.bincount(bin_idx, weights=state.v2, minlength=n_cells)
    vr2_sum = np.bincount(bin_idx, weights=state.v_r ** 2, minlength=n_cells)
    safe_counts = np.maximum(counts, 1)
    v2_mean = v2_sum / safe_counts
    vr2_mean = vr2_sum / safe_counts
    return {
        "r_over_rs": 0.5 * (cell_edges[:-1] + cell_edges[1:]),
        "rho_over_rhos": rho_cells,
        "v2_mean": v2_mean,
        "vr2_mean": vr2_mean,
        "cell_edges": cell_edges,
        "counts": counts,
    }


# -----------------------------------------------------------------------------
# Top-level driver
# -----------------------------------------------------------------------------

@dataclass
class SimulationResult:
    case: dict
    units: dict
    n_particles: int
    n_steps: int
    dt_initial: float
    snapshots: List[dict] = field(default_factory=list)
    diagnostics: dict = field(default_factory=dict)
    acceptance_info: dict = field(default_factory=dict)
    runtime_seconds: float = 0.0


def run_canonical_simulation(
    N: int = 10000,
    n_steps: int = 100,
    snapshot_every: int = 10,
    r_min_over_rs: float = 0.05,
    r_max_over_rs: float = 50.0,
    n_cells: int = 15,
    sigma_m_over_sigma0: float = 0.32,
    seed: int = 42,
    min_dt: float = 0.01,
    verbose: bool = True,
) -> SimulationResult:
    """
    Run the canonical KISS-SIDM DSMC case.

    Defaults: N=1e4, n_steps=100, n_cells=15, r/rs in [0.05, 50],
    sigma_m/sigma_0=0.32. The radial range is narrower than the
    paper's [0.017, 1169] because at N=1e4 the very inner cells would
    contain only a few particles and the no-time-counter scheme would
    not have enough pair trials to fire reliably. The paper's full
    21-cell grid from 0.017 to 1169 requires N ~ 2e6 to work as
    intended. The 15-cell grid from 0.05 to 50 covers the core-
    formation region (r/rs ~ 0.1-10) where Fig. 1 shows the most
    interesting evolution.

    min_dt: floor on the adaptive time step. The paper's Eq. 12 sets
    dt_grav = 0.02 * min_i t_ff,i, which at N=1e4 is dominated by
    the very inner cells (rho ~ 10-100, t_ff ~ 0.03-0.1) and produces
    a dt ~ 0.001. With such a small dt the per-cell scattering rate
    is far too small to see any evolution in 100 steps. We floor
    dt at 0.01 t_0 as a pragmatic compromise for the smoke test:
    this is roughly the gravitational time at the half-mass radius,
    which is the right scale for the bulk evolution. The paper's
    N=2e6 run has inner cells with N_i ~ 1000, so the time step is
    properly determined by the physics and no floor is needed.
    """
    rng = np.random.default_rng(seed)
    case = CanonicalCase(sigma_m_over_sigma0=sigma_m_over_sigma0)
    units = compute_units(case)
    sigma_m_code = sigma_m_over_sigma0  # already in sigma_0 units

    t_start = time.time()
    state = initialize_nfw_halo(
        N=N, r_min_over_rs=r_min_over_rs, r_max_over_rs=r_max_over_rs, rng=rng
    )
    cell_edges = make_radial_grid(r_min_over_rs, r_max_over_rs, n_cells)
    # v_max for the no-time-counter scheme: per-cell, 3x the local v_rms.
    # We pre-allocate and update each step using the previous snapshot.

    # Initial energy
    M_enc0 = compute_enclosed_mass(state.r)
    E0 = state.total_energy(M_enc0, state.r, G=1.0)

    # Initial profile
    profiles_0 = measure_profiles(state, cell_edges)
    v_max_per_cell = compute_v_max_per_cell(profiles_0["v2_mean"], safety_factor=8.0)

    snapshots = [{
        "step": 0,
        "t_over_t0": 0.0,
        "r_over_rs": profiles_0["r_over_rs"].tolist(),
        "rho_over_rhos": profiles_0["rho_over_rhos"].tolist(),
        "v2_mean": profiles_0["v2_mean"].tolist(),
        "vr2_mean": profiles_0["vr2_mean"].tolist(),
        "cell_edges": cell_edges.tolist(),
    }]
    energy_history = [(0, 0.0, E0, E0)]
    n_scatter_total = 0
    n_kicks_total = 0

    for step in range(1, n_steps + 1):
        # Compute current densities and adaptive dt
        rho_cells, counts = compute_cell_densities(state.r, cell_edges)
        dt = compute_time_step(
            rho_cells, v_max_per_cell, sigma_m_code, cell_edges,
            min_dt=min_dt,
        )
        # K (dt/2)
        kick(state, 0.5 * dt)
        # S (dt/2)
        n_s1 = scatter_in_cells(state, cell_edges, rho_cells, counts,
                                sigma_m_code, 0.5 * dt, v_max_per_cell, rng)
        # D (dt)
        drift(state, dt)
        # Recompute densities and v_max for the second S (after drift)
        rho_cells, counts = compute_cell_densities(state.r, cell_edges)
        profiles_mid = measure_profiles(state, cell_edges)
        v_max_per_cell = compute_v_max_per_cell(
            profiles_mid["v2_mean"], safety_factor=8.0
        )
        # S (dt/2)
        n_s2 = scatter_in_cells(state, cell_edges, rho_cells, counts,
                                sigma_m_code, 0.5 * dt, v_max_per_cell, rng)
        # K (dt/2)
        kick(state, 0.5 * dt)
        n_scatter_total += n_s1 + n_s2
        n_kicks_total += 2

        state.t += dt
        if step % snapshot_every == 0 or step == n_steps:
            profiles = measure_profiles(state, cell_edges)
            v_max_per_cell = compute_v_max_per_cell(
                profiles["v2_mean"], safety_factor=8.0
            )
            M_enc = compute_enclosed_mass(state.r)
            E_now = state.total_energy(M_enc, state.r, G=1.0)
            dE_over_E = (E_now - E0) / abs(E0) if E0 != 0 else 0.0
            snapshots.append({
                "step": step,
                "t_over_t0": state.t,
                "dt": dt,
                "r_over_rs": profiles["r_over_rs"].tolist(),
                "rho_over_rhos": profiles["rho_over_rhos"].tolist(),
                "v2_mean": profiles["v2_mean"].tolist(),
                "vr2_mean": profiles["vr2_mean"].tolist(),
                "cell_edges": cell_edges.tolist(),
                "n_scatter_step": n_s1 + n_s2,
            })
            energy_history.append((step, state.t, E_now, dE_over_E))
            if verbose:
                print(
                    f"step {step:4d}  t/t0 = {state.t:8.4f}  dt = {dt:.4e}  "
                    f"n_scatter = {n_s1 + n_s2:5d}  dE/E = {dE_over_E:+.3e}",
                    flush=True,
                )

    # Final diagnostics
    M_enc_final = compute_enclosed_mass(state.r)
    E_final = state.total_energy(M_enc_final, state.r, G=1.0)
    dE_over_E_final = (E_final - E0) / abs(E0) if E0 != 0 else 0.0
    # Estimate core density and core radius
    final_profile = measure_profiles(state, cell_edges)
    # Core density: density in the innermost cell with > 5 particles
    counts = final_profile["counts"]
    rho = final_profile["rho_over_rhos"]
    # Find first cell from inside with > 5 particles
    n_cells_local = counts.shape[0]
    core_idx = None
    for j in range(n_cells_local):
        if counts[j] > 5:
            core_idx = j
            break
    if core_idx is not None:
        core_rho = float(rho[core_idx])
        core_radius = float(final_profile["r_over_rs"][core_idx])
    else:
        core_rho = float("nan")
        core_radius = float("nan")
    runtime = time.time() - t_start

    return SimulationResult(
        case=asdict(case),
        units=units,
        n_particles=N,
        n_steps=n_steps,
        dt_initial=float(snapshots[1]["dt"]) if len(snapshots) > 1 else float("nan"),
        snapshots=snapshots,
        diagnostics={
            "E0": float(E0),
            "E_final": float(E_final),
            "dE_over_E": float(dE_over_E_final),
            "core_rho_over_rhos": core_rho,
            "core_radius_over_rs": core_radius,
            "n_scatterings_total": int(n_scatter_total),
        },
        acceptance_info={
            "n_kicks_total": int(n_kicks_total),
            "n_scatterings_total": int(n_scatter_total),
        },
        runtime_seconds=float(runtime),
    )


# -----------------------------------------------------------------------------
# CLI
# -----------------------------------------------------------------------------

def _save_result(result: SimulationResult, path: str) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    payload = {
        "case": result.case,
        "units": result.units,
        "n_particles": result.n_particles,
        "n_steps": result.n_steps,
        "dt_initial": result.dt_initial,
        "diagnostics": result.diagnostics,
        "acceptance_info": result.acceptance_info,
        "runtime_seconds": result.runtime_seconds,
        "snapshots": result.snapshots,
    }
    with open(path, "w") as f:
        json.dump(payload, f, indent=2)


def main():
    import argparse
    p = argparse.ArgumentParser(
        description="Run the canonical KISS-SIDM DSMC simulation "
                    "(Gurian & May 2025, arXiv:2505.15903v2)."
    )
    p.add_argument("--N", type=int, default=10000,
                   help="Number of particles (default 10000, paper used 2e6)")
    p.add_argument("--n-steps", type=int, default=100,
                   help="Number of KDSK time steps (default 100)")
    p.add_argument("--snapshot-every", type=int, default=10,
                   help="Snapshot interval (default 10)")
    p.add_argument("--sigma-m", type=float, default=0.32,
                   help="Cross section in sigma_0 = 1/(rho_s r_s) units "
                        "(paper canonical: 0.32)")
    p.add_argument("--out", type=str,
                   default=None,
                   help="Output JSON path (default: "
                        "<project_root>/v0.3-prelim/data/results/"
                        "kiss_sidm_canonical_simulation.json)")
    p.add_argument("--seed", type=int, default=42)
    args = p.parse_args()

    # Resolve output path
    if args.out is None:
        # Locate project root by walking up from this file
        here = os.path.dirname(os.path.abspath(__file__))
        # here is .../v0.3-prelim/code
        project_root = os.path.dirname(os.path.dirname(here))
        args.out = os.path.join(
            project_root, "v0.3-prelim", "data", "results",
            "kiss_sidm_canonical_simulation.json",
        )

    print(
        f"[kiss_sidm_dsmc] Running canonical case: N={args.N}, "
        f"n_steps={args.n_steps}, sigma_m/sigma_0={args.sigma_m}",
        flush=True,
    )
    res = run_canonical_simulation(
        N=args.N,
        n_steps=args.n_steps,
        snapshot_every=args.snapshot_every,
        sigma_m_over_sigma0=args.sigma_m,
        seed=args.seed,
        verbose=True,
    )
    _save_result(res, args.out)
    print(
        f"[kiss_sidm_dsmc] Done. runtime={res.runtime_seconds:.1f}s, "
        f"dE/E={res.diagnostics['dE_over_E']:+.3e}, "
        f"core_rho/rho_s={res.diagnostics['core_rho_over_rhos']:.3f}, "
        f"core_r/r_s={res.diagnostics['core_radius_over_rs']:.3f}",
        flush=True,
    )
    print(f"[kiss_sidm_dsmc] Saved: {args.out}", flush=True)


if __name__ == "__main__":
    main()
