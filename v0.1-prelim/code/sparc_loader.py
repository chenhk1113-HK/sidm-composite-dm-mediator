#!/usr/bin/env python
"""
SPARC galaxy loader for SIDM-pipeline v0.1.

Reads SPARC rotmod files (Lelli, McGaugh, Schombert 2016c, AJ 152, 157).
Each rotmod file has 9 columns:
    Rad [kpc], Vobs [km/s], errV [km/s], Vgas, Vdisk, Vbul, SBdisk, SBbul, [extra]

The baryonic contribution at each radius is:
    Vbar^2 = Vdisk^2 + Vbul^2 + (Vgas * 1.33)^2  (gas factor 1.33 = helium correction, Lelli+ 2016c Eq. 5)

The dark matter contribution is fitted via halo profile.
"""
from __future__ import annotations
import re
from pathlib import Path
import numpy as np

# Lelli+ 2016c Eq. 5: total baryonic circular speed squared
GAS_HELIUM_FACTOR = 1.33  # 1.33 = sqrt(M_HI + M_He + M_metals) / M_HI


class SPARCGalaxy:
    """One SPARC galaxy from one rotmod file."""

    def __init__(self, name: str, rad: np.ndarray, vobs: np.ndarray, errv: np.ndarray,
                 vgas: np.ndarray, vdisk: np.ndarray, vbul: np.ndarray,
                 sbdisk: np.ndarray, sbbul: np.ndarray):
        self.name = name
        self.Rad = rad
        self.Vobs = vobs
        self.errV = errv
        self.Vgas = vgas
        self.Vdisk = vdisk
        self.Vbul = vbul
        self.SBdisk = sbdisk
        self.SBbul = sbbul
        # Baryonic circular speed squared (Lelli+ 2016c Eq. 5)
        self.Vbar_sq = self.Vdisk**2 + self.Vbul**2 + (self.Vgas * GAS_HELIUM_FACTOR)**2

    @property
    def n_pts(self) -> int:
        return len(self.Rad)

    def __repr__(self) -> str:
        return f"SPARCGalaxy({self.name}, n={self.n_pts}, R=[{self.Rad.min():.2f}, {self.Rad.max():.2f}] kpc)"


def _parse_rotmod_file(path: Path) -> SPARCGalaxy:
    """Parse one SPARC rotmod .dat file."""
    rad_list, vobs_list, errv_list = [], [], []
    vgas_list, vdisk_list, vbul_list = [], [], []
    sbdisk_list, sbbul_list = [], []
    name = path.stem.replace("_rotmod", "")
    with open(path) as fh:
        for line in fh:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            cols = line.split()
            if len(cols) < 6:
                continue
            rad_list.append(float(cols[0]))
            vobs_list.append(float(cols[1]))
            errv_list.append(float(cols[2]))
            vgas_list.append(float(cols[3]))
            vdisk_list.append(float(cols[4]))
            vbul_list.append(float(cols[5]))
            sbdisk_list.append(float(cols[6]) if len(cols) > 6 else 0.0)
            sbbul_list.append(float(cols[7]) if len(cols) > 7 else 0.0)
    return SPARCGalaxy(
        name=name,
        rad=np.array(rad_list),
        vobs=np.array(vobs_list),
        errv=np.array(errv_list),
        vgas=np.array(vgas_list),
        vdisk=np.array(vdisk_list),
        vbul=np.array(vbul_list),
        sbdisk=np.array(sbdisk_list),
        sbbul=np.array(sbbul_list),
    )


def load_all_sparc(data_dir: str | Path) -> list[SPARCGalaxy]:
    """Load all 175 SPARC galaxies from a directory of rotmod files."""
    data_dir = Path(data_dir)
    rotmod_dir = data_dir / "Rotmod_LTG"
    if not rotmod_dir.exists():
        rotmod_dir = data_dir
    galaxies = []
    for f in sorted(rotmod_dir.glob("*_rotmod.dat")):
        try:
            galaxies.append(_parse_rotmod_file(f))
        except Exception as e:
            print(f"[load_all_sparc] skipped {f.name}: {e}")
    return galaxies


def load_one_sparc(data_dir: str | Path, name: str) -> SPARCGalaxy:
    """Load one SPARC galaxy by name."""
    data_dir = Path(data_dir)
    rotmod_dir = data_dir / "Rotmod_LTG"
    if not rotmod_dir.exists():
        rotmod_dir = data_dir
    path = rotmod_dir / f"{name}_rotmod.dat"
    if not path.exists():
        raise FileNotFoundError(f"No rotmod file: {path}")
    return _parse_rotmod_file(path)


if __name__ == "__main__":
    # Smoke test
    import sys
    data_dir = sys.argv[1] if len(sys.argv) > 1 else "data"
    gs = load_all_sparc(data_dir)
    print(f"Loaded {len(gs)} SPARC galaxies.")
    if gs:
        g = gs[0]
        print(f"  First galaxy: {g}")
        print(f"  Vbar at first 3 radii: {np.sqrt(g.Vbar_sq[:3])}")
        print(f"  Vobs at first 3 radii:  {g.Vobs[:3]}")