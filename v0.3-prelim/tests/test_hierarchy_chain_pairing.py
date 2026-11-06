"""Guard for the hierarchy-bound chain pairing (finding F30).

Release-gate layer 10 failed on commit a91ea53 for the reason this guard exists:
scripts/audit_hierarchy_chain.py inherited whichever f_H/amplitude pairing
scripts/constants.py happened to expose, while the values it audits (the t235
artifact and the paper's printed chain) are the archived pair. Ten links broke,
all by exactly the pairing factor.

What this test pins:

  1. the auditor passes on the current tree and reports NO failures;
  2. it audits BOTH pairings and the committed artifact agrees with a fresh run;
  3. the arithmetic identity between the chains is exact (amplitudes scale by
     1/K, every g_N/g_chi bound loosens by sqrt(K), sigma_eff is invariant);
  4. a half-paired constants.py is refused outright rather than audited;
  5. the paper states both chains: the archived-pair values stay printed (they
     are the historical record) and the live-pair values appear as the current
     claim;
  6. link 7 (claim-site scan): every scientific-notation quantity printed inside
     a pairing-labelled claim is a quantity the auditor recomputes at the printed
     precision. Link 4/6 only ask whether a value appears SOMEWHERE, which a
     mutation satisfies by leaving one copy behind - the mutation harness proved
     it, and this link is the fix.
"""
import json
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "scripts"))

import audit_hierarchy_chain as auditor  # noqa: E402
import constants as framework_constants  # noqa: E402

AUDITOR = REPO / "scripts" / "audit_hierarchy_chain.py"
ARTIFACT = REPO / "v0.3-prelim" / "data" / "results" / "hierarchy_chain_pairing.json"
PAPER = REPO / "v0.3-prelim" / "docs" / "PAPER_V1_DRAFT.md"

# Values the paper prints, per pairing.
ARCHIVED_PRINTED = ["65.91", "166.02", "1.25e+25", "2.83e-13", "3.3e+25",
                    "1.74e-13", "9.85e+21", "1.01e-11"]
LIVE_PRINTED = ["10.33", "26.02", "1.96e+24", "7.15e-13", "5.16e+24",
                "4.40e-13", "1.54e+21", "2.55e-11"]


def _run(out_path=None):
    cmd = [sys.executable, str(AUDITOR), "--json"]
    if out_path is not None:
        cmd += ["--out", str(out_path)]
    proc = subprocess.run(cmd, cwd=str(REPO), capture_output=True, text=True)
    return proc


@pytest.fixture(scope="module")
def fresh_json():
    proc = _run()
    assert proc.returncode == 0, (
        f"audit_hierarchy_chain.py failed:\n{proc.stdout[-4000:]}\n{proc.stderr[-2000:]}")
    return json.loads(proc.stdout)


@pytest.fixture(scope="module")
def stored():
    assert ARTIFACT.exists(), f"missing hierarchy chain artifact: {ARTIFACT}"
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def test_auditor_passes_with_no_failures(fresh_json):
    assert fresh_json["result"] == "PASS"
    assert fresh_json["failures"] == [], fresh_json["failures"]
    # Both pairings must be represented among the checks, not just one.
    names = [c["name"] for c in fresh_json["checks"]]
    assert any("live pairing" in n for n in names)
    assert any(n.startswith("link 1") or n.startswith("known-system") for n in names)


def test_artifact_matches_a_fresh_run(stored, fresh_json):
    """The committed artifact is a real product of the auditor, not a paste."""
    assert stored["result"] == "PASS"
    assert stored["chains"] == fresh_json["chains"], "committed chain artifact drifted"
    assert stored["producer"] == "scripts/audit_hierarchy_chain.py"
    assert len(stored["checks"]) == len(fresh_json["checks"])


def test_out_flag_reproduces_the_committed_artifact(tmp_path):
    out = tmp_path / "hierarchy_chain_pairing.json"
    proc = _run(out_path=out)
    assert proc.returncode == 0, proc.stdout[-2000:] + proc.stderr[-2000:]
    assert json.loads(out.read_text(encoding="utf-8"))["chains"] == json.loads(
        ARTIFACT.read_text(encoding="utf-8"))["chains"]


def test_pairing_arithmetic_is_exact(fresh_json):
    """amplitudes scale by 1/K, bounds loosen by sqrt(K), sigma_eff is invariant."""
    K = framework_constants.PAIRING_K_LEGACY_TO_CANONICAL  # archived -> live
    chains = fresh_json["chains"]
    arch, live, pair = chains["archived_pair"], chains["live_pair"], chains["pairing"]

    for key in ("sigma_0_cm2_per_g", "sigma_peak_cm2_per_g",
                "sigma_m_28_sigma1_1_cm2_per_g", "sigma_m_28_sigma1_44_cm2_per_g",
                "sigma_m_v100_background_cm2_per_g"):
        assert live[key] == pytest.approx(arch[key] * K, rel=1e-12), key

    loosen = 1.0 / K ** 0.5
    assert pair["bound_loosening_factor_sqrt_inverse"] == pytest.approx(loosen, rel=1e-12)
    for key in ("g_n_over_g_chi_v28", "g_n_over_g_chi_peak", "g_n_over_g_chi_v100"):
        assert live[key] == pytest.approx(arch[key] * loosen, rel=1e-12), key

    # sigma_eff must NOT move.
    fh_a, fh_l = arch["f_H"], live["f_H"]
    assert fh_a == framework_constants.F_H_LEGACY_PLACEHOLDER_0297
    assert fh_l == framework_constants.F_H_CANONICAL
    for key in ("sigma_m_28_sigma1_1_cm2_per_g", "sigma_m_28_sigma1_44_cm2_per_g",
                "sigma_peak_cm2_per_g"):
        assert fh_l ** 2 * live[key] == pytest.approx(fh_a ** 2 * arch[key], rel=1e-12), key


def test_auditor_uses_the_archived_pair_for_the_historical_links(fresh_json):
    """Links 1-4 audit history; they must not follow the live constants."""
    const = fresh_json["constants"]
    assert const["SIGMA_PEAK_CM2_PER_G"] == framework_constants.SIGMA_PEAK_LEGACY_PAIR_174
    assert const["SIGMA_0_CM2_PER_G"] == framework_constants.SIGMA_0_LEGACY_PAIR_052
    assert const["LIVE_SIGMA_PEAK_CM2_PER_G"] == framework_constants.SIGMA_PEAK_CM2_PER_G
    assert const["LIVE_SIGMA_0_CM2_PER_G"] == framework_constants.SIGMA_0_CM2_PER_G


def _mutate_line(src, prefix, replacement):
    """Replace the first top-level assignment starting with `prefix`."""
    lines = src.split("\n")
    hits = [i for i, ln in enumerate(lines) if ln.startswith(prefix)]
    assert hits, f"no line starting with {prefix!r} in constants.py"
    lines[hits[0]] = replacement
    return "\n".join(lines)


def test_half_paired_constants_file_is_refused(tmp_path):
    """Guard 2: if the two live amplitudes are not scaled by the same factor,
    the layer must refuse to run rather than audit a broken pairing."""
    src = (REPO / "scripts" / "constants.py").read_text(encoding="utf-8")
    mutated = _mutate_line(src, "SIGMA_PEAK_CM2_PER_G =",
                           "SIGMA_PEAK_CM2_PER_G = 100.0  # MUTATED (half-paired probe)")
    assert mutated != src
    broken = tmp_path / "constants.py"
    broken.write_text(mutated, encoding="utf-8")
    original = auditor.CONSTANTS
    try:
        auditor.CONSTANTS = broken
        with pytest.raises(SystemExit) as excinfo:
            auditor.read_constants()
        assert "half-paired" in str(excinfo.value), str(excinfo.value)
    finally:
        auditor.CONSTANTS = original


def test_archived_pair_swap_is_refused(tmp_path):
    """Guard 1: the historical links audit the published archived pair; quietly
    redefining it must stop the layer instead of silently re-deriving history."""
    src = (REPO / "scripts" / "constants.py").read_text(encoding="utf-8")
    mutated = _mutate_line(src, "SIGMA_PEAK_LEGACY_PAIR_174 =",
                           "SIGMA_PEAK_LEGACY_PAIR_174 = 200.0  # MUTATED")
    assert mutated != src
    broken = tmp_path / "constants.py"
    broken.write_text(mutated, encoding="utf-8")
    original = auditor.CONSTANTS
    try:
        auditor.CONSTANTS = broken
        with pytest.raises(SystemExit) as excinfo:
            auditor.read_constants()
        assert "ARCHIVED pair" in str(excinfo.value), str(excinfo.value)
    finally:
        auditor.CONSTANTS = original


def test_paper_prints_both_chains():
    paper = PAPER.read_text(encoding="utf-8")
    for value in ARCHIVED_PRINTED:
        assert any(form in paper for form in auditor.UNICODE_EQUIV.get(value, [value])), \
            f"archived-pair value {value} disappeared from the paper"
    for value in LIVE_PRINTED:
        assert any(form in paper for form in auditor.UNICODE_EQUIV_CANONICAL.get(value, [value])), \
            f"live-pair value {value} is not stated in the paper"
    assert "finding F30" in paper, "the pairing dependence is not declared in the paper"


def test_paper_labels_which_pairing_the_hierarchy_numbers_use():
    """The pairing must be stated where the claim is made, not only in an appendix."""
    paper = PAPER.read_text(encoding="utf-8").replace("\r\n", "\n")
    paragraphs = [p for p in paper.split("\n") if "Hierarchy constraint" in p
                  or "Pairing dependence of this chain" in p]
    assert len(paragraphs) >= 2, "expected the abstract and A.3 pairing statements"
    for para in paragraphs:
        assert "archived pair" in para or "archived pair**" in para
    abstract = next(p for p in paragraphs if "**Hierarchy constraint.**" in p)
    assert "4.40×10⁻¹³" in abstract or "4.40e-13" in abstract


# --- link 7: the claim-site scan (added after the mutation harness proved the
#     weaker "does this value appear anywhere" rule can be satisfied by leaving
#     one copy behind) ----------------------------------------------------------

def _audited_pool(stored):
    pool = []
    for chain in stored["chains"].values():
        pool.extend(v for v in chain.values() if isinstance(v, (int, float)))
    return pool


def test_link7_claim_site_scan_is_green_and_covers_the_claims(fresh_json):
    entry = [c for c in fresh_json["checks"]
             if c["name"].startswith("link 7: quantities in pairing-labelled")]
    assert entry, "the claim-site check is missing from the auditor"
    assert entry[0]["ok"] is True, entry[0]
    assert entry[0]["actual"] == 0
    assert "claim slices scanned" in entry[0]["note"]
    # 6 anchors, and each of the two chains plus the invariance claims contribute
    # several quantities; a scan that checked almost nothing would be a silent
    # no-op rather than a guard.
    checked = int(entry[0]["note"].split("scanned, ")[1].split(" ")[0])
    assert checked >= 20, f"only {checked} quantities checked across the pairing claims"
    stored = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    unrecognised, missing, checked_again = auditor.scan_pairing_claim_sites(
        PAPER.read_text(encoding="utf-8"), _audited_pool(stored))
    assert unrecognised == [], unrecognised
    assert missing == [], missing
    assert checked_again == checked


def test_link7_catches_a_wrong_coefficient_printed_at_a_claim_site(stored):
    """The whole point of link 7: a corrupted number IN THE CLAIM is detected even
    though the correct value still appears elsewhere in the paper."""
    paper = PAPER.read_text(encoding="utf-8").replace("\r\n", "\n")
    pool = _audited_pool(stored)

    mutated = paper.replace("the same chain gives 4.40×10⁻¹³ at the resonance peak",
                            "the same chain gives 9.99×10⁻¹³ at the resonance peak", 1)
    assert mutated != paper, "the abstract claim anchor drifted"
    unrecognised, _, _ = auditor.scan_pairing_claim_sites(mutated, pool)
    assert unrecognised, "a fabricated live-pair bound in the abstract was not caught"
    assert "abstract live-pair claim" in unrecognised[0]

    mutated = paper.replace("sigma/m = 27.27    -> ratio 5.16 × 10²⁴ -> g_N/g_chi < 4.40 × 10⁻¹³",
                            "sigma/m = 27.27    -> ratio 5.16 × 10²⁴ -> g_N/g_chi < 9.99 × 10⁻¹³", 1)
    assert mutated != paper, "the A.3 live chain anchor drifted"
    unrecognised, _, _ = auditor.scan_pairing_claim_sites(mutated, pool)
    assert unrecognised, "a fabricated live-pair bound in A.3 was not caught"
    assert "A.3 live chain" in unrecognised[0]

    # The unmutated paper must stay clean, otherwise the guard is just loud.
    clean, _, _ = auditor.scan_pairing_claim_sites(paper, pool)
    assert clean == [], clean


def test_link7_catches_a_claim_that_is_tighter_than_the_arithmetic(stored):
    """A rounding LIE, not a rounding error: claiming agreement to 1.0e-17 when
    the recomputed residual is 1.35e-17. This is the defect the scan found in
    its own first run and the paper was corrected for it."""
    paper = PAPER.read_text(encoding="utf-8").replace("\r\n", "\n")
    assert "1.3×10⁻¹⁷" in paper, "the invariance claim is no longer stated as recomputed"
    mutated = paper.replace("to 1.3×10⁻¹⁷ relative", "to 1.0×10⁻¹⁷ relative", 1)
    unrecognised, _, _ = auditor.scan_pairing_claim_sites(mutated, _audited_pool(stored))
    assert unrecognised, "an over-precise invariance claim was accepted"


def test_link7_refuses_a_paper_that_stops_naming_its_pairing_claims(stored):
    paper = PAPER.read_text(encoding="utf-8").replace("\r\n", "\n")
    stripped = paper.replace("LIVE CANONICAL PAIR", "(chain)")
    _, missing, _ = auditor.scan_pairing_claim_sites(stripped, _audited_pool(stored))
    assert missing, "the auditor accepted a paper whose live-chain claim vanished"
    assert any("A.3 live chain" in m for m in missing), missing


def test_link7_new_anchors_loosen_by_the_same_pairing_factor(stored):
    k = stored["chains"]["pairing"]["amplitude_factor_archived_over_live"]
    expected = k ** 0.5
    for key in ("g_n_over_g_chi_sigma1_3", "option_b_g_n_over_g_chi"):
        arch = stored["chains"]["archived_pair"][key]
        live = stored["chains"]["live_pair"][key]
        assert live / arch == pytest.approx(expected, rel=1e-9), (key, live / arch, expected)
    # and the new anchors must be looser than the peak bound, same ordering rule
    assert (stored["chains"]["live_pair"]["g_n_over_g_chi_sigma1_3"]
            > stored["chains"]["live_pair"]["g_n_over_g_chi_peak"])
    assert (stored["chains"]["archived_pair"]["g_n_over_g_chi_sigma1_3"]
            > stored["chains"]["archived_pair"]["g_n_over_g_chi_peak"])
