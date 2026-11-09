"""v19.2-F: Y24 / profile-family recheck of the Cloud-9 c-M tension claim.

CLAIM UNDER TEST (PAPER_V1_DRAFT.md, sec 5 headline):
    "CDM requires c_200 ~7 sigma below the c-M median; the best-fit SIDM interpretation
     (sigma/m = 483, c_200 = 4.0) reduces the tension to 3.2 sigma."
Both numbers descend from Ohana+ 2026's NFW fit (0.16 dex scatter, DK14 convention).

QUESTIONS
  1. Is the paper's own sigma bookkeeping internally consistent (one median, one scatter)?
  2. Does the Y24 profile family (Gilman+ 2021 / Yang+ 2024 = [43], the family AIDA-TNG
     [48] fits SIDM halos with) change the answer, and can it be applied to Cloud-9?

EVERY INPUT IS NAMED. Nothing here is quoted from memory: AIDA-TNG statements are quoted
from docs/papers/verified/_extracted_text_20261109/2512.15869.txt, and the Y24 evolution
factors are the project's own implementation in gravothermal_yang2024.py.

Run: C:/Python314/python.exe v19_2_f_y24_profile_family_recheck.py
"""
import math
import sys

sys.path.insert(0, ".")

# ---------------------------------------------------------------- conventions
DEX = 0.16           # scatter convention used throughout the draft (DK14/DJ19)
C_OBS = 4.0          # Ohana+ NFW-fit c_200 for Cloud-9
TENSION_OBS = 3.16   # the draft's own sigma count for C_OBS (sec 2.7)
C_0_NFW = 12.0       # framework's NFW baseline concentration (sec 2.6c)
TAUS = (16.3, 29.7, 46.3, 90.8, 156.9, 185.3)   # draft sec 2.6c table, deep-collapse tau
M200 = 5.0e9         # Cloud-9 host halo mass, Msun
H0 = 70.0


def tension(c, median):
    """Sigma below the c-M median, dex convention: log10(median/c)/scatter."""
    return math.log10(median / c) / DEX


def main():
    # --- 1. the median the paper's own numbers imply ------------------------
    median = C_OBS * 10 ** (TENSION_OBS * DEX)
    print(f"[1] median implied by the draft's own pair (c={C_OBS} -> {TENSION_OBS} sigma, {DEX} dex): {median:.2f}")
    for c in (4.0, 6.0, 26.4):
        print(f"    c_200 = {c:>5} -> {tension(c, median):+6.2f} sigma under that single convention")
    print(f"    the draft's reported 0.32 sigma at c_200 = 6.0 implies median {6.0 * 10 ** (0.32 * DEX):.2f}")
    print(f"    the draft's reported -1.42 sigma at c_200 = 26.4 implies median {26.4 / 10 ** (1.42 * DEX):.2f}")

    # --- 2. Cloud-9 size ----------------------------------------------------
    rho_crit = 2.775e11 * (H0 / 100.0) ** 2 / 1.0e9  # Msun/kpc^3
    r200 = (3.0 * M200 / (4.0 * math.pi * 200.0 * rho_crit)) ** (1.0 / 3.0)
    r200_1e12 = (3.0 * 1.0e12 / (4.0 * math.pi * 200.0 * rho_crit)) ** (1.0 / 3.0)
    print(f"\n[2] rho_crit = {rho_crit:.1f} Msun/kpc^3 (H0={H0}); r_200(Cloud-9) = {r200:.1f} kpc")
    print(f"    scaling cross-check: r_200(1e12) = {r200_1e12:.0f} kpc x (5e9/1e12)^(1/3) = {r200_1e12 * (M200/1e12)**(1/3.0):.1f} kpc")

    # --- 3. AIDA-TNG eq (3) extrapolated to Cloud-9 mass --------------------
    # quoted verbatim from 2512.15869 sec 4.2:
    #   y(SIDM1) = 0.37 - 0.5x + 0.0026x^2 ; y(vSIDM) = 0.16 - 0.11x ; x = log M200c, y = log(rc/r200c)
    x = math.log10(M200)
    for name, y in (("SIDM1", 0.37 - 0.5 * x + 0.0026 * x ** 2), ("vSIDM", 0.16 - 0.11 * x)):
        rc = 10 ** y * r200
        print(f"    [3] AIDA-TNG eq (3) at log M = {x:.2f}, {name}: log(rc/r200c) = {y:+.2f} "
              f"-> rc = {100 * 10 ** y:.4f}% of r200 = {rc:.3f} kpc")
    print(f"        framework's own Cloud-9 core floors (sec 2.6d): 30% and 50% of r200 = {0.30 * r200:.1f} and {0.50 * r200:.1f} kpc")
    print(f"        AIDA-TNG sample: SIDM1 sigma/m = 1 cm^2/g, profiles shown for log M200c = [12,13] -> regime mismatch")

    # --- 4. the project's own Y24 implementation: validity window ----------
    import gravothermal_yang2024 as y24
    print(f"\n[4] gravothermal_yang2024.py TAU_FIT_RANGE_MAX = {y24.TAU_FIT_RANGE_MAX}")
    for tau in (1.0, 1.3):
        f = y24.f_rs_over_rs0(tau)
        print(f"    tau = {tau}: f_rs = {f:.4f} -> c_200 = c_0/f_rs = {C_0_NFW / f:.1f} (in range: {y24.tau_in_fit_range(tau)})")
    for tau in TAUS:
        f = y24.f_rs_over_rs0(tau)
        print(f"    tau = {tau}: f_rs = {f:.4g} in-range={y24.tau_in_fit_range(tau)}"
              + ("  -> UNPHYSICAL (r_s <= 0)" if f <= 0 else f"  -> c_200 = {C_0_NFW / f:.1f}"))
    print(f"    note: f_rs(tau=1) gives c_200 = {C_0_NFW / y24.f_rs_over_rs0(1.0):.1f}, "
          "which is exactly the retracted v40.39 'Yang+ Eq. 5 extrapolation' value 26.4")

    # --- 5. what each leg means --------------------------------------------
    print("\n[5] verdict is written in docs/V19_2_F_Y24_PROFILE_FAMILY_RECHECK.md")


if __name__ == "__main__":
    main()
