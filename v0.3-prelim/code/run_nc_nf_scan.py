"""
T70.8 Wave B2 — Discrete (Nc, Nf) parameter scan driver.

Motivation (per v0.6 Wave B roadmap in CHANGELOG T70.7):
  T70.7 scaffolded `KSFR_NC_NF_RATIOS` for 7 (Nc, Nf) combinations but
  the full integration (running T41 at each combo and comparing log_Z)
  was deferred to Wave B. This driver closes that loop.

Why discrete scan (not continuous sampling):
  (Nc, Nf) are integers — number of colours / flavours of the dark
  gauge group. Sampling continuous integer-valued parameters in a
  nested-sampling framework is non-trivial. The project uses a
  discrete-scan driver: run T41 at each fixed (Nc, Nf), collect
  log_Z values, then compute Bayes factors.

Bayes factor convention:
  BF(Nc, Nf | data) := exp( log_Z(Nc, Nf) - log_Z(3, 3) )
  relative to the (3, 3) anchor (PDG/FLAG LATTICE physical point).
  The anchor's log_Z is taken as the reference; values > 1 mean the
  data prefer that (Nc, Nf) over (3, 3); values < 1 mean the opposite.

Confidence levels (per KSFR_NC_NF_TABLE.md §7 quick-ref):
  LATTICE  (3, 3)              -> +/-0.05 error  (PDG/FLAG physical point)
  LATTICE  (3, 2)              -> +/-0.3 error   (extrapolated from Nf=3)
  ANALYTICAL (4, 3), (4, 4)    -> +/-0.5 error   (large-Nc scaling)
  ESTIMATED (2, 2), (2, 3), (3, 4) -> +/-1.0 error

Usage:
  /home/lamkuenai/wimpy/bin/python v0.3-prelim/code/run_nc_nf_scan.py

  Or via WSL:
  wsl -e bash -lc "cd /home/lamkuenai/sidm-composite-dm-mediator && \\
      T41_NLIVE=500 /home/lamkuenai/wimpy/bin/python \\
      v0.3-prelim/code/run_nc_nf_scan.py"

Env vars (override defaults):
  T41_NLIVE            (default 500)  — nested-sampler live points
  T41_DLOGZ            (default 0.1)  — dynesty stopping criterion
  KSFR_SCAN_NLIVE      (default 500)  — same as T41_NLIVE for clarity
  SKIP_T41_RUN         (default 0)    — set to 1 to skip t41 subprocess
                                        (recompute summary from existing JSONs)
  KSFR_SCAN_DIR        (default v0.3-prelim/data/results)  — output dir
"""
from __future__ import annotations
import json
import math
import os
import platform
import subprocess
import sys
import time
from pathlib import Path

import numpy as np


# Resolve paths relative to THIS file so the script works from any cwd.
_HERE = Path(__file__).resolve().parent
# Code dir holds ksfr_pcac_validity.py + t41_mediator_mass_joint_fit.py
CODE_DIR = _HERE
# Repo root (one level above v0.3-prelim/code)
REPO_ROOT = _HERE.parent.parent

# Add CODE_DIR to sys.path so `import ksfr_pcac_validity` works in this script
if str(CODE_DIR) not in sys.path:
    sys.path.insert(0, str(CODE_DIR))

# Import the (Nc, Nf) table from the canonical Wave A3 module
from ksfr_pcac_validity import KSFR_NC_NF_RATIOS  # noqa: E402

# Confidence classification (LATTICE < ANALYTICAL < ESTIMATED) of the
# m_rho/f_pi ratio for each (Nc, Nf). Per KSFR_NC_NF_TABLE.md §7 quick-ref.
# Mapping mirrors the docstrings in ksfr_pcac_validity.py KSFR_NC_NF_RATIOS.
KSFR_NC_NF_CONFIDENCE = {
    (2, 2): "ESTIMATED",
    (2, 3): "ESTIMATED",
    (3, 2): "LATTICE",
    (3, 3): "LATTICE",   # anchor (PDG/FLAG physical point)
    (3, 4): "ESTIMATED",
    (4, 3): "ANALYTICAL",
    (4, 4): "ANALYTICAL",
}
# Per KSFR_NC_NF_TABLE.md §7 quick-ref uncertainty bars on the m_rho/f_pi
# RATIO (NOT on log_Z). These are propagated to the BF uncertainty.
KSFR_NC_NF_RATIO_ERR = {
    (2, 2): 1.0,
    (2, 3): 1.0,
    (3, 2): 0.3,
    (3, 3): 0.05,  # anchor (tightest)
    (3, 4): 0.4,
    (4, 3): 0.5,
    (4, 4): 0.5,
}

# Anchor (the "denominator" of every Bayes factor)
ANCHOR = (3, 3)

# ------------------------------------------------------------
# Output dir resolution (POSIX absolute path; mirror to Windows-side)
# ------------------------------------------------------------
if platform.system() == "Windows" or not Path("/home/lamkuenai/sidm-composite-dm-mediator").exists():
    _DEFAULT_RESULTS_DIR = "C:/Users/lamkuenai/projects/sidm-composite-dm-mediator/v0.3-prelim/data/results"
else:
    _DEFAULT_RESULTS_DIR = "/home/lamkuenai/sidm-composite-dm-mediator/v0.3-prelim/data/results"

RESULTS_DIR = Path(os.environ.get("KSFR_SCAN_DIR", _DEFAULT_RESULTS_DIR))
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

# Summary output filename (single source of truth — T70.8 deliverable)
SUMMARY_FILENAME = "nc_nf_scan_v0_6_summary.json"


def t41_result_path(nc: int, nf: int) -> Path:
    """The on-disk path that t41_mediator_mass_joint_fit.main() will write
    when called with T41_RESULT_SUFFIX=_v0_6_nc<N>_nf<M>."""
    return RESULTS_DIR / f"t41_mediator_mass_joint_fit_v0_6_nc{nc}_nf{nf}.json"


def run_t41_subprocess(nc: int, nf: int, nlive: int = 500,
                       dlogz: float = 0.1) -> Path:
    """Launch t41_mediator_mass_joint_fit as a subprocess with the right env vars.

    Why subprocess and not in-process: t41's main() mutates module-level state
    (the dynesty sampler) and reads env vars at module-import time via
    ksfr_pcac_validity.loglike_ksfr_pcac_validity. A fresh subprocess per
    (Nc, Nf) guarantees clean env-var propagation and avoids state leakage.

    Returns the Path of the resulting JSON. Raises if the subprocess fails.
    """
    env = os.environ.copy()
    env["KSFR_NC"] = str(nc)
    env["KSFR_NF"] = str(nf)
    env["T41_NLIVE"] = str(nlive)
    env["T41_DLOGZ"] = str(dlogz)
    env["T41_RESULT_SUFFIX"] = f"_v0_6_nc{nc}_nf{nf}"

    t41_path = CODE_DIR / "t41_mediator_mass_joint_fit.py"
    print(f"\n>>> launching t41 (Nc={nc}, Nf={nf}) via subprocess "
          f"(nlive={nlive}, dlogz={dlogz})")
    print(f"    env: KSFR_NC={nc}, KSFR_NF={nf}, T41_NLIVE={nlive}, "
          f"T41_DLOGZ={dlogz}, T41_RESULT_SUFFIX={env['T41_RESULT_SUFFIX']}")
    print(f"    script: {t41_path}")
    t0 = time.time()
    result = subprocess.run(
        [sys.executable, str(t41_path)],
        env=env,
        cwd=str(REPO_ROOT),
        capture_output=True,
        text=True,
    )
    wall = time.time() - t0
    if result.returncode != 0:
        # Surface the failure but don't silently mask it.
        sys.stderr.write(
            f"!!! t41 (Nc={nc}, Nf={nf}) FAILED (exit={result.returncode}, "
            f"wall={wall:.1f}s)\n"
            f"    STDOUT tail:\n{result.stdout[-2000:]}\n"
            f"    STDERR tail:\n{result.stderr[-2000:]}\n"
        )
        raise RuntimeError(
            f"t41 (Nc={nc}, Nf={nf}) subprocess failed: "
            f"exit={result.returncode}"
        )
    # Print the last few lines of stdout so the driver log shows progress.
    out_tail = "\n".join(result.stdout.splitlines()[-15:])
    print(f"    t41 (Nc={nc}, Nf={nf}) finished in {wall:.1f}s")
    print(f"    STDOUT tail:\n{out_tail}")

    out_path = t41_result_path(nc, nf)
    if not out_path.exists():
        # On Windows-side run, t41 writes to Windows path; on WSL, to POSIX path.
        # Accept either.
        win_mirror = Path("C:/Users/lamkuenai/projects/sidm-composite-dm-mediator/v0.3-prelim/data/results") / out_path.name
        if win_mirror.exists():
            out_path = win_mirror
        else:
            raise FileNotFoundError(
                f"t41 (Nc={nc}, Nf={nf}) returned 0 but produced no JSON at "
                f"{out_path} (also checked {win_mirror})"
            )
    return out_path


def load_log_z(json_path: Path) -> tuple[float, float]:
    """Return (log_Z, log_Z_err) from a T41 result JSON."""
    with json_path.open() as f:
        data = json.load(f)
    log_z = float(data["log_Z"])
    log_z_err = float(data.get("log_Z_err", 0.0))
    return log_z, log_z_err


def compute_bayes_factor(log_z: float, log_z_anchor: float) -> float:
    """BF(Nc, Nf | data) := exp( log_Z(Nc, Nf) - log_Z(anchor) ).

    Conventions:
      BF > 1  → data prefer (Nc, Nf) over the anchor
      BF = 1  → (Nc, Nf) is as good as the anchor
      BF < 1  → data prefer the anchor over (Nc, Nf)

    Per Jeffreys (1961): log BF > 1 is "strong"; log BF > 2 is "decisive".
    """
    return float(math.exp(log_z - log_z_anchor))


def parse_existing_summary(summary_path: Path) -> dict | None:
    """If a prior summary exists and SKIP_T41_RUN=1, return it for re-aggregation."""
    if not summary_path.exists():
        return None
    try:
        with summary_path.open() as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return None


def aggregate_summary(per_pair: dict) -> dict:
    """Given a per_pair dict (Nc, Nf) -> {log_Z, log_Z_err, json_path, ...},
    compute the Bayes factors relative to the (3, 3) anchor."""
    if ANCHOR not in per_pair:
        raise KeyError(f"Anchor {ANCHOR} missing from per_pair; cannot compute BFs")
    log_z_anchor = per_pair[ANCHOR]["log_Z"]

    out_entries = []
    # Iterate over the 7 known (Nc, Nf) combinations in a stable order
    sorted_keys = sorted(per_pair.keys())
    for (nc, nf) in sorted_keys:
        entry = per_pair[(nc, nf)]
        log_z = entry["log_Z"]
        log_z_rel = log_z - log_z_anchor
        bf = compute_bayes_factor(log_z, log_z_anchor)
        log_bf = log_z_rel
        # Gaussian-propagated uncertainty on log BF (independent errors):
        #   sigma_log_BF^2 = sigma_log_Z^2 + sigma_log_Z_anchor^2
        sigma_log_bf = math.sqrt(
            entry["log_Z_err"] ** 2
            + per_pair[ANCHOR]["log_Z_err"] ** 2
        )
        out_entries.append({
            "Nc": nc,
            "Nf": nf,
            "ratio_m_rho_over_f_pi": KSFR_NC_NF_RATIOS[(nc, nf)],
            "ratio_uncertainty": KSFR_NC_NF_RATIO_ERR[(nc, nf)],
            "confidence_class": KSFR_NC_NF_CONFIDENCE[(nc, nf)],
            "log_Z": log_z,
            "log_Z_err": entry["log_Z_err"],
            "log_Z_relative_to_3_3": log_z_rel,
            "Bayes_factor": bf,
            "log_Bayes_factor": log_bf,
            "log_Bayes_factor_err": sigma_log_bf,
            "is_anchor": (nc, nf) == ANCHOR,
            "result_json": str(entry["json_path"]),
        })
    return {"per_pair": out_entries, "log_Z_anchor": log_z_anchor}


def write_summary(summary: dict) -> Path:
    """Write the summary JSON to BOTH the WSL-side and Windows-side paths.

    Per the T70.8 wave-B2 pitfall, the WSL<->Windows sync can be flaky, so
    write to the local dir AND mirror to the Windows-side path if reachable.
    """
    summary_path = RESULTS_DIR / SUMMARY_FILENAME
    payload = json.dumps(summary, indent=2, default=str)
    summary_path.write_text(payload)

    # Mirror to the Windows-side path (best effort).
    # Inside WSL:  /mnt/c/Users/lamkuenai/projects/...
    # Native Win: C:/Users/lamkuenai/projects/...   (Path("/mnt/c/...") doesn't exist)
    win_path_wsl = Path("/mnt/c/Users/lamkuenai/projects/sidm-composite-dm-mediator/v0.3-prelim/data/results") / SUMMARY_FILENAME
    win_path_native = Path("C:/Users/lamkuenai/projects/sidm-composite-dm-mediator/v0.3-prelim/data/results") / SUMMARY_FILENAME
    try:
        if win_path_wsl.parent.exists():
            win_path_wsl.write_text(payload)
            print(f"\nsummary written -> {summary_path}")
            print(f"                -> {win_path_wsl}")
        elif win_path_native.parent.exists():
            win_path_native.write_text(payload)
            print(f"\nsummary written -> {summary_path}")
            print(f"                -> {win_path_native}")
        else:
            print(f"\nsummary written -> {summary_path} (Win mirror unreachable)")
    except (OSError, FileNotFoundError) as e:
        print(f"\nsummary written -> {summary_path} (Win mirror skipped: {e})")
    return summary_path


def print_summary(summary: dict) -> None:
    """Pretty-print the per-pair results + declare the preferred (Nc, Nf)."""
    entries = summary["per_pair"]
    anchor_log_z = summary["log_Z_anchor"]

    print("\n" + "=" * 80)
    print(f"  (Nc, Nf) DISCRETE SCAN SUMMARY — anchor (3, 3) log_Z = {anchor_log_z:.3f}")
    print("=" * 80)
    header = (
        f"  {'(Nc, Nf)':<10} {'class':<12} {'R':>6}  {'log_Z':>9}  "
        f"{'log_BF':>9}  {'BF':>11}  {'Jeffreys':<14}"
    )
    print(header)
    print("  " + "-" * (len(header) - 2))

    # Sort by log BF descending so the data-preferred model is on top
    entries_sorted = sorted(entries, key=lambda e: -e["log_Bayes_factor"])
    best = entries_sorted[0]
    for e in entries_sorted:
        if e["log_Bayes_factor"] > 1.0:
            verdict = "STRONG (data pref)"
        elif e["log_Bayes_factor"] > 0.5:
            verdict = "moderate"
        elif e["log_Bayes_factor"] > -0.5:
            verdict = "indistinguishable"
        elif e["log_Bayes_factor"] > -1.0:
            verdict = "moderate against"
        else:
            verdict = "STRONG (data reject)"
        marker = "  <-- ANCHOR" if e["is_anchor"] else ""
        print(
            f"  ({e['Nc']:>2}, {e['Nf']:>2})  {e['confidence_class']:<12} "
            f"{e['ratio_m_rho_over_f_pi']:>6.2f}  "
            f"{e['log_Z']:>9.3f}  {e['log_Bayes_factor']:>+9.3f}  "
            f"{e['Bayes_factor']:>11.4g}  {verdict}{marker}"
        )

    print()
    if best["is_anchor"]:
        print(f"  CONCLUSION: the (3, 3) anchor remains the data-preferred model.")
    elif best["log_Bayes_factor"] > 1.0:
        print(f"  CONCLUSION: data prefer ({best['Nc']}, {best['Nf']}) "
              f"over (3, 3) with log BF = {best['log_Bayes_factor']:+.3f} "
              f"({best['confidence_class']} ratio).")
    else:
        print(f"  CONCLUSION: data marginally prefer ({best['Nc']}, {best['Nf']}) "
              f"over (3, 3) with log BF = {best['log_Bayes_factor']:+.3f} — "
              f"WITHIN noise; the (3, 3) anchor is still adequate.")

    # Normalization sanity: exp(log_Z - max_log_Z) sum check
    log_zs = np.array([e["log_Z"] for e in entries])
    max_log_z = log_zs.max()
    weights = np.exp(log_zs - max_log_z)
    norm = weights.sum()
    n_loaded = len(entries)
    print(f"\n  Posterior weights (normalized to max): sum = {norm:.4f} "
          f"(== {n_loaded} only when all log_Zs are equal; otherwise < {n_loaded}).")
    if n_loaded == 1:
        print(f"  (Only {(entries[0]['Nc'], entries[0]['Nf'])} loaded — "
              f"normalization is trivially 1.0.)")
    else:
        print("  Per-pair normalized weights (approx posterior over the loaded "
              "(Nc, Nf) models under a flat prior):")
        for e in entries_sorted:
            w = math.exp(e["log_Z"] - max_log_z) / norm
            bar = "#" * int(round(40 * w))
            print(f"    ({e['Nc']:>2}, {e['Nf']:>2})  w = {w:.4f}  {bar}")
    print("=" * 80)


def main() -> int:
    print("=" * 80)
    print("  T70.8 Wave B2 — Discrete (Nc, Nf) scan over KSFR_NC_NF_RATIOS")
    print("=" * 80)
    print(f"  Number of (Nc, Nf) combinations: {len(KSFR_NC_NF_RATIOS)}")
    print(f"  Anchor: {ANCHOR}  (PDG/FLAG LATTICE physical point)")
    print(f"  Output dir: {RESULTS_DIR}")

    nlive = int(os.environ.get("KSFR_SCAN_NLIVE",
                  os.environ.get("T41_NLIVE", "500")))
    dlogz = float(os.environ.get("T41_DLOGZ", "0.1"))
    skip_run = os.environ.get("SKIP_T41_RUN", "0").strip() in ("1", "true", "yes", "on")
    print(f"  nlive = {nlive}   dlogz = {dlogz}   skip_run = {skip_run}")
    print()

    per_pair: dict = {}
    per_pair_missing: list = []
    t_start = time.time()
    for (nc, nf) in sorted(KSFR_NC_NF_RATIOS.keys()):
        out_path = t41_result_path(nc, nf)
        if skip_run and out_path.exists():
            print(f">>> SKIP_T41_RUN=1 and {out_path.name} exists; reusing")
        elif skip_run:
            # SKIP_T41_RUN=1 but no existing JSON → quietly skip; no subprocess
            print(f">>> SKIP_T41_RUN=1 but {out_path.name} does NOT exist; "
                  f"silently skipping (per_pair_missing tracks it)")
            per_pair_missing.append((nc, nf))
            continue
        else:
            try:
                out_path = run_t41_subprocess(nc, nf, nlive=nlive, dlogz=dlogz)
            except (RuntimeError, FileNotFoundError) as e:
                sys.stderr.write(f"!!  skipping (Nc={nc}, Nf={nf}): {e}\n")
                per_pair_missing.append((nc, nf))
                continue
        # Load log_Z (whether we just ran or are reusing)
        try:
            log_z, log_z_err = load_log_z(out_path)
        except (FileNotFoundError, KeyError, json.JSONDecodeError) as e:
            sys.stderr.write(f"!!  cannot load {out_path}: {e}; skipping\n")
            per_pair_missing.append((nc, nf))
            continue
        per_pair[(nc, nf)] = {
            "log_Z": log_z,
            "log_Z_err": log_z_err,
            "json_path": out_path,
        }
        print(f"    log_Z (Nc={nc}, Nf={nf}) = {log_z:.3f} ± {log_z_err:.3f}")
    wall_total = time.time() - t_start

    # In normal (non-skip) mode, missing results are noteworthy (a t41
    # subprocess failure). In SKIP_T41_RUN mode, missing JSONs are the
    # default expectation and we keep silent.
    if per_pair_missing and not skip_run:
        sys.stderr.write(
            f"NOTE: {len(per_pair_missing)} (Nc, Nf) combos did not produce "
            f"a result: {per_pair_missing}\n"
        )

    if ANCHOR not in per_pair:
        sys.stderr.write(
            f"FATAL: anchor {ANCHOR} missing — cannot compute Bayes factors.\n"
            f"  Loaded: {sorted(per_pair.keys())}\n"
        )
        return 1

    summary = aggregate_summary(per_pair)
    summary["wall_seconds_total"] = wall_total
    summary["t41_nlive"] = nlive
    summary["t41_dlogz"] = dlogz
    summary["scan_version"] = "T70.8 Wave B2"
    summary["anchor"] = list(ANCHOR)
    summary["anchor_log_Z"] = summary["log_Z_anchor"]
    summary["caveats"] = [
        "Per-pair log_Z_uncertainty comes from dynesty's dlogz criterion "
        f"(target dlogz={dlogz}); log_BF_err = sqrt(sigma_log_Z^2 + "
        "sigma_log_Z_anchor^2) — Gaussian propagation of independent errors.",
        "Ratio-uncertainty propagation (KSFR_NC_NF_TABLE.md §7): LATTICE "
        "(3,3) ±0.05, LATTICE (3,2) ±0.3, ANALYTICAL (4,3) (4,4) ±0.5, "
        "ESTIMATED (2,2) (2,3) (3,4) ±1.0. These affect the m_phi validity "
        "window position but the BAYES FACTOR over log_Z marginalises them.",
        "Caveat on (2, 3): the dark sector may be CONFORMAL (no KSFR "
        "regime). The ratio=7.5 here is a placeholder; the BF for (2, 3) "
        "should be read with caution.",
        "All 7 (Nc, Nf) combos share the same T41 prior box for "
        "(log_m_phi, log_m_chi, g_chi, log_eps, log_alpha, log_xi); only "
        "the KSFR/PCAC validity mask window shifts with (Nc, Nf).",
        "Normalization sanity: sum(exp(log_Z - max_log_Z)) = number of "
        "configs only if all log_Zs are equal; otherwise < number. "
        "Reported per-pair weights are PROPORTIONAL to the posterior "
        "under a flat prior over the 7 (Nc, Nf) models.",
    ]
    write_summary(summary)
    print_summary(summary)
    print(f"\nTotal wall time: {wall_total/60:.1f} min "
          f"({len(per_pair)} of 7 (Nc, Nf) combos loaded)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
