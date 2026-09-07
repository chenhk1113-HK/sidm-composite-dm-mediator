"""
T90 Path C.4.7 (v17) — LZ 248 keV time-series analysis.

STATUS: DRAFT STUB. Path 2 of the 'proceed 1,2 3 4 6 7' plan.

PURPOSE
=======
Reanalyze the LZ 248 keV event in the context of LZ's
background model and check for:
  1. Consistency with 124Xe double-electron-capture (DEC)
     background
  2. Time-series features (annual modulation, clustering)
  3. Energy-spectrum context (what other events are in
     the same time/energy window)

WHY THIS MATTERS
================
The LZ 248 keV event has 2.6σ global significance. To
distinguish it from background:
  - 124Xe DEC at 2.825 MeV (gamma) and 64.3 keV (X-ray
    cascade) — NOT at 248 keV
  - 83mKr calibration at 41.5 keV — NOT at 248 keV
  - Solar neutrino scatters (pp chain) — peaked at <50 keV
  - 8B solar neutrinos — extended to ~MeV but very rare
  - 220Rn / 219Rn / 222Rn backgrounds — sub-100 keV

The 248 keV energy is in a region of low LZ background
(mainly 238U/232Th chain gammas), making it harder to
attribute to background.

STUB STATUS: This script is a placeholder. The LZ data
is not publicly available in a usable form; this would
require either:
  - Access to LZ collaboration internal data
  - Reanalysis of publicly released LZ data (Phase 1)
  - Use of public LZ likelihood functions

REFERENCES TO READ BEFORE COMPLETING
=====================================
- LZ Collaboration (2026), arXiv:2609.02823 — the 248 keV
  event paper
- LZ Collaboration (2023), PRL 131, 041002 — first results
- 124Xe DEC background: Mei+ 2015, PRC 92, 035503
- Annual modulation: Freese+ 2013, RPP 85, 035001

OUTPUT (when complete):
  - outputs/t90/lz_time_series.json
  - For each hypothesis (magnetic-moment, 124Xe DEC,
    solar neutrino, instrumental): posterior probability

CONSTRAINTS:
  - No new dependencies (rule 17/24)
  - Branch-local on wip/tier3-magnetic-moment-LZ
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

_PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_PROJECT_ROOT / "code"))


def xe124_dec_background_rate(exposure_kg_day: float) -> float:
    """Compute the expected number of 124Xe double-electron-capture
    events in the LZ analysis window.

    Per Mei+ 2015: 124Xe has a 2.825 MeV gamma and a 64.3 keV
    X-ray cascade. The cascade X-rays are at 25.3, 27.4, 30.8,
    31.9, 33.6 keV (K-shell cascade) — NOT at 248 keV.

    The 248 keV line is NOT in the 124Xe DEC spectrum.

    Returns:
      Expected N_events in the LZ 248 keV window
    """
    # TODO: verify by reading Mei+ 2015 and the LZ background paper.
    return 0.0  # PLACEHOLDER


def solar_neutrino_background_at_248keV(exposure_kg_day: float) -> float:
    """Compute the expected solar neutrino scattering rate at
    248 keV recoil energy in LZ.

    The dominant solar neutrino background at this energy
    is from 8B neutrinos (spectrum extends to ~15 MeV).

    TODO: implement using Bahcall+ 2005 solar neutrino flux.
    """
    # PLACEHOLDER: order-of-magnitude estimate
    return 0.01  # very small


def annual_modulation_signature(events: list, dates: list) -> dict:
    """Test for annual modulation in the event rate.

    Standard dark-matter annual modulation: June 2 is the
    peak (Earth's velocity relative to DM halo is maximum).

    Args:
      events: list of event energies (keV)
      dates: list of event dates (datetime objects)

    Returns:
      Dict with amplitude, phase, chi^2 vs flat
    """
    # TODO: implement Lomb-Scargle periodogram
    # Standard references: Freese+ 2013 RPP
    raise NotImplementedError(
        "Annual modulation analysis not yet implemented; "
        "needs Lomb-Scargle periodogram (scipy.signal.lombscargle)"
    )


def main():
    print("=" * 70)
    print("T90 Path C.4.7 (v17) — LZ time-series analysis (DRAFT STUB)")
    print("=" * 70)
    print()
    print("STATUS: This is a draft stub. The structure is correct but")
    print("the LZ data analysis requires access to LZ collaboration")
    print("data or reanalysis of publicly released Phase 1 data.")
    print()

    exposure = 2.84 * 1000.0 * 365.25  # kg*day

    print(f"LZ exposure (SR0+SR1 combined): {exposure:.3e} kg*day")
    print()

    n_124xe = xe124_dec_background_rate(exposure)
    print(f"Expected 124Xe DEC events in 248 keV window: {n_124xe}")
    print()

    n_solar = solar_neutrino_background_at_248keV(exposure)
    print(f"Expected solar neutrino events at 248 keV recoil: {n_solar:.3e}")
    print()

    print("To complete this path:")
    print("  1. Get access to LZ data (collaboration or public release)")
    print("  2. Implement xe124_dec_background_rate from Mei+ 2015")
    print("  3. Implement solar_neutrino_background_at_248keV from Bahcall+ 2005")
    print("  4. Implement annual_modulation_signature (Lomb-Scargle)")
    print("  5. Compute posteriors for each hypothesis")
    print("  6. Write tests + commit")


if __name__ == '__main__':
    main()
