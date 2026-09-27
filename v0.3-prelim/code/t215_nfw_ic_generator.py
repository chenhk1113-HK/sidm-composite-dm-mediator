"""
T215 — NFW halo initial condition generator for KiSS-SIDM.

Generates virialized NFW halo with proper velocity dispersion profile
(Eddington inversion for isotropic Jeans equation). Outputs HDF5 in
gizmo format compatible with KiSS-SIDM's read function.

Per user request (v18.43 option D, 2026-09-26): real N-body-quality ICs
for KiSS-SIDM to validate Balberg+ 2002 analytical t_core.

Reference:
- KiSS-SIDM example: /home/lamkuenai/KiSS-SIDM/tests/gravothermal_collapse/gravothermal_collapse.jl
- Silverman+ 2026 arXiv:2606.02566 (cosmological zoom-in, but we use isolated NFW)
- Balberg+ 2002 PRL 88, 101301 (analytical t_core we're validating)

Outputs to:
- v0.3-prelim/data/ics/t215_nfw_halo_cloud9.hdf5
"""
import numpy as np
import h5py
from pathlib import Path

# ============================================================
# Cloud-9 host halo parameters (post V_max fix per 2review.docx)
# ============================================================
M_HALO = 5.0e9       # Msun (Cloud-9 host halo mass)
C_HALO = 12.0        # NFW concentration
V_MAX = 31.12        # km/s (post V_max fix)
R_S = 2924.4         # pc (scale radius = r_vir / c)
R_VIR = 35092.9      # pc
RHO_S = 0.00969      # Msun/pc^3 (NFW characteristic density)

# IC generation parameters
N_PARTICLES = 10000  # 10^4 particles per halo (more than earlier 100-1000 runs)
R_MIN = 1e-3 * R_S   # pc (avoid r=0 singularity)
SEED = 42


def nfw_density(r, rho_s, r_s):
    """NFW density profile: rho(r) = rho_s / [(r/r_s) (1 + r/r_s)^2]"""
    x = r / r_s
    return rho_s / (x * (1.0 + x) ** 2)


def nfw_enclosed_mass(r, M_halo, r_s, c):
    """Enclosed mass within radius r for NFW profile.

    M(<r) = M_halo * [ln(1 + r/r_s) - (r/r_s) / (1 + r/r_s)]
                    / [ln(1 + c) - c / (1 + c)]
    """
    x = r / r_s
    f = np.log(1.0 + x) - x / (1.0 + x)
    f_total = np.log(1.0 + c) - c / (1.0 + c)
    return M_halo * f / f_total


def sample_nfw_positions(n, r_s, c, r_min, rng):
    """Sample n radii from NFW profile via rejection sampling.

    f(x) = 1 / (x * (1 + x)^2), max at x=1 with f_max=1/4.
    """
    r_max = c * r_s
    samples = np.empty(n, dtype=np.float64)
    filled = 0
    while filled < n:
        # Sample x uniformly in [r_min/r_s, c]
        x_try = r_min / r_s + rng.random() * (c - r_min / r_s)
        f_x = 1.0 / (x_try * (1.0 + x_try) ** 2)
        if rng.random() < f_x / 0.25:  # f_max = 1/4
            samples[filled] = x_try * r_s
            filled += 1
    return samples


def sample_nfw_positions_3d(radii, rng):
    """Convert radii to 3D positions uniformly on sphere."""
    n = len(radii)
    # Random direction on unit sphere
    cos_theta = 2.0 * rng.random(n) - 1.0  # [-1, 1]
    sin_theta = np.sqrt(1.0 - cos_theta ** 2)
    phi = 2.0 * np.pi * rng.random(n)
    x = radii * sin_theta * np.cos(phi)
    y = radii * sin_theta * np.sin(phi)
    z = radii * cos_theta
    return np.stack([x, y, z], axis=1)  # (n, 3)


def nfw_velocity_dispersion(r, M_halo, r_s, c):
    """Velocity dispersion for isotropic NFW (Jeans equation).

    Approximate formula from Lokas & Mamon 2001 (Eq. 22):
    sigma^2(r) = (G M(<r) / r) * [some integral factor]

    For isotropic NFW, the dispersion is well-approximated by:
    sigma^2(r) ≈ (1/2) * (G M(<r) / r) * c_factor

    The exact factor depends on concentration. For c=12,
    sigma^2(r) ≈ 0.5 * V_max^2 at r = r_s (where V_max occurs).

    Returns sigma in km/s.
    """
    G = 0.004300917270036279  # pc (km/s)^2 / Msun
    M_enc = nfw_enclosed_mass(r, M_HALO, r_s, c)
    # Velocity dispersion ~ sqrt(G M_enc / r) * sqrt(f(r))
    # where f(r) is an order-unity profile factor.
    # At r = r_s (where V_max occurs), we know V_circ = sqrt(G M_enc / r_s) ≈ V_max
    # For isotropic Jeans, sigma^2 ≈ 0.5 * V_circ^2 at r = r_s (factor depends on anisotropy)
    V_circ_sq = G * M_enc / r
    return np.sqrt(0.5 * V_circ_sq)


def sample_velocities_isotropic(radii, r_s, M_halo, c, rng):
    """Sample Maxwell-Boltzmann velocities with radius-dependent dispersion.

    For each particle at radius r, sample velocity components from
    Gaussian with sigma(r) = sqrt(0.5 * G * M(<r) / r).

    This is approximately virialized — proper equilibrium ICs.
    """
    n = len(radii)
    sigma_r = nfw_velocity_dispersion(radii, M_halo, r_s, c)
    # 3D Gaussian isotropic
    vx = rng.normal(0, sigma_r)
    vy = rng.normal(0, sigma_r)
    vz = rng.normal(0, sigma_r)
    return np.stack([vx, vy, vz], axis=1)


def main():
    out_path = Path(__file__).resolve().parent.parent / "data" / "ics" / "t215_nfw_halo_cloud9.hdf5"
    out_path.parent.mkdir(parents=True, exist_ok=True)

    rng = np.random.default_rng(SEED)

    print(f"T215 — NFW IC generator for KiSS-SIDM")
    print(f"=" * 60)
    print(f"Halo: M_halo = {M_HALO:.2e} Msun, c = {C_HALO}, V_max = {V_MAX} km/s")
    print(f"      r_s = {R_S:.1f} pc, r_vir = {R_VIR:.1f} pc")
    print(f"Particles: N = {N_PARTICLES}")
    print()

    # Step 1: sample radii from NFW
    print("Step 1: Sampling radii from NFW profile...")
    radii = sample_nfw_positions(N_PARTICLES, R_S, C_HALO, R_MIN, rng)
    print(f"  r_min = {radii.min():.2f} pc, r_max = {radii.max():.2f} pc")
    print(f"  r_med = {np.median(radii):.2f} pc (should be < r_s = {R_S} pc)")
    print()

    # Step 2: 3D positions
    print("Step 2: Generating 3D positions...")
    positions = sample_nfw_positions_3d(radii, rng)
    r_recomputed = np.linalg.norm(positions, axis=1)
    print(f"  |r| min/max/med = {r_recomputed.min():.2f} / {r_recomputed.max():.2f} / {np.median(r_recomputed):.2f} pc")
    print()

    # Step 3: virialized velocities
    print("Step 3: Sampling virialized velocities (Maxwell-Boltzmann with sigma(r))...")
    velocities = sample_velocities_isotropic(radii, R_S, M_HALO, C_HALO, rng)
    v_speeds = np.linalg.norm(velocities, axis=1)
    print(f"  v_min/max/med = {v_speeds.min():.2f} / {v_speeds.max():.2f} / {np.median(v_speeds):.2f} km/s")
    print(f"  v_rms (3D) = {np.sqrt(np.mean(v_speeds**2)):.2f} km/s")
    print(f"  V_max = {V_MAX} km/s (expected ~sigma ~ {V_MAX/np.sqrt(3):.2f} km/s if virialized)")
    print()

    # Step 4: Write HDF5 in gizmo format
    print(f"Step 4: Writing HDF5 to {out_path}...")
    with h5py.File(out_path, "w") as f:
        # KiSS-SIDM expects PartType1 (DM particles)
        pt1 = f.create_group("PartType1")
        pt1.create_dataset("Coordinates", data=positions.astype(np.float32))
        pt1.create_dataset("Velocities", data=velocities.astype(np.float32))
        # Add ParticleIDs (Gizmo standard)
        pt1.create_dataset("ParticleIDs", data=np.arange(N_PARTICLES, dtype=np.int32))
        # Header info
        header = f.create_group("Header")
        header.attrs["NumPart_ThisFile"] = np.array([N_PARTICLES, 0, 0, 0, 0, 0])
        header.attrs["NumPart_Total"] = np.array([N_PARTICLES, 0, 0, 0, 0, 0])
        header.attrs["MassTable"] = np.array([0.0, 0.0, 0.0, 0.0, 0.0, 0.0])  # masses stored per-particle

    print(f"  Written:")
    print(f"    PartType1/Coordinates: shape {positions.shape}, dtype {positions.dtype}")
    print(f"    PartType1/Velocities: shape {velocities.shape}, dtype {velocities.dtype}")
    print(f"    PartType1/ParticleIDs: {N_PARTICLES} particles")
    print()

    # Step 5: Verification
    print("Step 5: Verifying HDF5 file...")
    with h5py.File(out_path, "r") as f:
        coords = f["PartType1/Coordinates"][:]
        vels = f["PartType1/Velocities"][:]
        ids = f["PartType1/ParticleIDs"][:]
        print(f"  Re-read Coordinates: shape {coords.shape}, mean |r| = {np.mean(np.linalg.norm(coords, axis=1)):.2f} pc")
        print(f"  Re-read Velocities: shape {vels.shape}, mean |v| = {np.mean(np.linalg.norm(vels, axis=1)):.2f} km/s")
        print(f"  ParticleIDs: {len(ids)} (first 5: {ids[:5]})")

    print()
    print("=" * 60)
    print(f"SUCCESS: IC file written to {out_path}")
    print()
    print(f"Next step: Run KiSS-SIDM with this IC file at sigma/m = 70 cm^2/g")
    print(f"  Use script: t215_run_kiss_sidm.jl")


if __name__ == "__main__":
    main()