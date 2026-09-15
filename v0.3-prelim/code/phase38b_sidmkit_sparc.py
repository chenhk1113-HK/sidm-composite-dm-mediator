"""
Phase 38b — sidmkit SPARC fit comparison.

Compares sidmkit's batch NFW rotation-curve fits (127 galaxies) to our
Phase 33d Vflat band test.

Key question: do the galaxies sidmkit can fit successfully overlap with
the galaxies our Vflat band test considers consistent?

Output:
  - fit_success_rate (sidmkit)
  - quality_distribution (chi2_red)
  - cross_validation: do successful fits fall in our Vflat bands?
"""
from __future__ import annotations
import json
import sys
from pathlib import Path
import numpy as np

SIDMKIT_DIR = Path(r"C:\Users\lamkuenai\projects\sidm-composite-dm-mediator\v0.3-prelim\data\external\sparc\sidmkit_fits")
SPARC_DIR = Path(r"C:\Users\lamkuenai\projects\sidm-composite-dm-mediator\v0.3-prelim\data\external\sparc")


def main():
    # Load sidmkit results
    with open(SIDMKIT_DIR / "summary.json") as f:
        sidmkit_fits = json.load(f)
    print(f"sidmkit: {len(sidmkit_fits)} galaxies fitted")
    print()

    # Load Table1.mrt to get Vflat for each galaxy (using same parser as Phase 33d)
    vflat_data = {}
    seen = set()
    with open(SPARC_DIR / "Table1.mrt") as f:
        for line in f:
            parts = line.split()
            if not parts:
                continue
            name = parts[0]
            if name in seen:
                continue
            seen.add(name)
            if len(parts) < 13:
                continue
            # Vflat at columns 101-105 (0-indexed), Q at columns 115-118
            try:
                vflat = float(line[101:106].strip())
                q_str = line[115:118].strip()
                q = int(q_str) if q_str and q_str.lstrip("-").isdigit() else 3
                # Match Phase 33d: Q in [1, 2] AND Vflat > 0
                if vflat > 0 and q in [1, 2]:
                    vflat_data[name] = vflat
            except (ValueError, IndexError):
                continue

    print(f"Vflat data: {len(vflat_data)} galaxies with Q<=2")
    print()

    # Compare
    print(f"{'Galaxy':12s} {'Vflat':>8} {'sidm_chi2r':>12} {'success':>8} {'in_band':>8}")
    print("-" * 60)

    # Define Vflat bands (from Phase 33d):
    # dwarfs (30-80): sigma/m ~ 0.24-0.94
    # intermediates (80-150): sigma/m ~ 0.14-0.24
    # spirals (150-250): sigma/m ~ 0.10-0.14
    # giants (250-350): sigma/m ~ 0.07-0.17
    def get_sigma_band(vflat):
        if 30 <= vflat <= 80:
            return (0.24, 0.94, "dwarf")
        elif 80 < vflat <= 150:
            return (0.14, 0.24, "intermediate")
        elif 150 < vflat <= 250:
            return (0.10, 0.14, "spiral")
        elif 250 < vflat <= 350:
            return (0.07, 0.17, "giant")
        return None

    overlap_count = 0
    sidmkit_success = 0
    in_band_count = 0
    vflat_match = 0

    for fit in sidmkit_fits:
        gal = fit["galaxy"]
        success = fit["success"]
        chi2r = fit["chi2_red"]
        vflat = vflat_data.get(gal, None)

        if success:
            sidmkit_success += 1

        if vflat is None:
            in_band = "?"
        else:
            band = get_sigma_band(vflat)
            if band:
                vflat_match += 1
                in_band = "Q=1,2"
            else:
                in_band = "Q=3+"

        if success and vflat and vflat_match:
            in_band_count += 1

    # Print first 10 and summary stats
    for fit in sidmkit_fits[:10]:
        gal = fit["galaxy"]
        success = fit["success"]
        chi2r = fit["chi2_red"]
        vflat = vflat_data.get(gal, None)
        band_str = ""
        if vflat:
            band = get_sigma_band(vflat)
            if band:
                band_str = f"v={vflat:.0f}({band[2]})"
        in_band = "OK" if success and band_str else "FAIL"
        print(f"{gal:12s} {vflat or 0:8.1f} {chi2r:12.3f} {'Y' if success else 'N':>8} {in_band:>8} {band_str}")

    print(f"\n{'='*60}")
    print(f"Summary:")
    print(f"  sidmkit fitted: {len(sidmkit_fits)} galaxies")
    print(f"  sidmkit success: {sidmkit_success} ({sidmkit_success/len(sidmkit_fits)*100:.1f}%)")
    print(f"  Vflat data available (Q=1,2): {len(vflat_data)} galaxies")
    print(f"  Cross-matched: {vflat_match} galaxies")
    print(f"  Cross-matched AND sidmkit success: {in_band_count}")

    # Chi2r distribution
    chi2r_vals = [f["chi2_red"] for f in sidmkit_fits if f["success"]]
    if chi2r_vals:
        print(f"\nChi2_red distribution (successful fits):")
        print(f"  Median: {np.median(chi2r_vals):.3f}")
        print(f"  P25: {np.percentile(chi2r_vals, 25):.3f}")
        print(f"  P75: {np.percentile(chi2r_vals, 75):.3f}")
        print(f"  Max: {max(chi2r_vals):.3f}")
        good = sum(1 for c in chi2r_vals if c < 2.0)
        print(f"  chi2_red < 2.0 (good fit): {good}/{len(chi2r_vals)} ({good/len(chi2r_vals)*100:.1f}%)")

    # Output JSON
    out = {
        "n_sidmkit_fits": len(sidmkit_fits),
        "n_sidmkit_success": sidmkit_success,
        "n_vflat_data": len(vflat_data),
        "n_cross_matched": vflat_match,
        "n_cross_matched_success": in_band_count,
        "chi2r_median": float(np.median(chi2r_vals)) if chi2r_vals else None,
        "n_good_fit_chi2_lt_2": int(sum(1 for c in chi2r_vals if c < 2.0)) if chi2r_vals else 0,
    }
    out_path = Path(r"C:\Users\lamkuenai\projects\sidm-composite-dm-mediator\v0.3-prelim\data\results") / "phase38b_sidmkit_sparc.json"
    with open(out_path, "w") as f:
        json.dump(out, f, indent=2)
    print(f"\nResults: {out_path}")


if __name__ == "__main__":
    main()