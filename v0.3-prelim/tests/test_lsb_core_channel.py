"""Regression tests for the LSB core check (channels_lsb_core.py).

Pins three things that must not drift silently:
  1. The literature constants imported from Sanchez-Salcedo+ 2005 (NGC 5963)
     and Kitazawa+ 2026 (five field LSBGs).
  2. The audit result that Kitazawa's printed t_core values are ~1e3 smaller
     than its own equations produce — if anyone "fixes" the catalogue or the
     formula, this test fires so the discrepancy is re-adjudicated, not buried.
  3. Channel behaviour: CDM (sigma -> 0) gets zero penalty, the likelihood is
     monotone non-increasing in sigma/m, and it is mediator-class aware.
"""
# CG-16: host-independent paths, matching tests/test_dm_dominated_udg_channel.py
import sys as _sys
import pathlib as _pathlib
import math

import numpy as np
import pytest

_CG16_ROOT = next(a for a in _pathlib.Path(__file__).resolve().parents
                  if (a / "scripts" / "paths.py").exists())
_sys.path.insert(0, str(_CG16_ROOT / "scripts"))
sys_path_root = str(_CG16_ROOT / "v0.3-prelim" / "code")
if sys_path_root not in _sys.path:
    _sys.path.insert(0, sys_path_root)

import channels_lsb_core as lsb  # noqa: E402


# ---------------------------------------------------------------------------
# 1. Literature constants pinned
# ---------------------------------------------------------------------------
class TestPinnedConstants:
    def test_ngc5963_limits(self):
        assert lsb.NGC5963_SIGMA_LIMIT_CM2G == 0.2
        assert lsb.NGC5963_SIGMA_LIMIT_TIGHT == 0.1
        assert lsb.NGC5963_SIGMA_CC_LIMIT == 0.08
        assert lsb.NGC5963_TRC_GYR_PER_CM2G == 0.8
        assert lsb.NGC5963_V_KMS == 150.0

    def test_v_ref_matches_repo_convention(self):
        # S05 quotes sigma_0 at v0 = 100 km/s, same as the repo's V_REF.
        from scripts.constants import V_REF_KMS
        assert V_REF_KMS == 100.0

    def test_kitazawa_catalogue(self):
        names = [r[0] for r in lsb.KITAZAWA_LSB_TABLE]
        assert names == ["F561-1", "F563-V1", "F571-V1", "F574-1", "F574-2"]
        assert all(r[4] == 1.8e6 for r in lsb.KITAZAWA_LSB_TABLE)
        assert lsb.KITAZAWA_CORE_RELAXATIONS == 30.0
        assert lsb.KITAZAWA_AGE_GYR == 11.0


# ---------------------------------------------------------------------------
# 2. Kitazawa reproduction audit
# ---------------------------------------------------------------------------
class TestKitazawaAudit:
    def test_printed_times_are_1e3_off(self):
        """Recomputed / printed ratio must be ~1000 on all five objects."""
        rows = lsb.reproduce_kitazawa_table()
        assert len(rows) == 5
        for r in rows:
            for key in ("sigma_1", "sigma_0p1"):
                ratio = r[key]["ratio_calc_over_printed"]
                assert 900.0 < ratio < 1150.0, (r["name"], key, ratio)

    def test_catalogue_params_are_self_consistent(self):
        """The 1e3 discrepancy is NOT in the halo parameters: an NFW mass
        integral over the printed rho_s / r_s reproduces the printed M_dyn."""
        rows = lsb.kitazawa_lsb_rows(1.0, 1.0, mediator_class="power_law")
        for r in rows:
            ratio = r["m_dyn_from_params_msun"] / r["m_dyn_from_paper_msun"]
            assert 0.7 < ratio < 1.4, (r["name"], ratio)

    def test_inversion_round_trip(self):
        """sigma_min_for_core_formation inverts t_core = 30 t_r,0 exactly."""
        rho, r_s, age = 1.8e6, 6.2, 11.0
        s = lsb.sigma_min_for_core_formation(rho, r_s, age)
        assert math.isclose(lsb.t_core_form_gyr(s, rho, r_s), age, rel_tol=1e-9)

    def test_cdm_gives_infinite_timescale(self):
        assert lsb.t_r0_gyr(0.0, 1.8e6, 6.2) == float("inf")

    def test_scalings(self):
        """t_r,0 ~ 1/(rho nu sigma): doubling sigma halves the time."""
        t1 = lsb.t_r0_gyr(1.0, 1.8e6, 6.2)
        t2 = lsb.t_r0_gyr(2.0, 1.8e6, 6.2)
        assert math.isclose(t1 / t2, 2.0, rel_tol=1e-12)
        # nu_s ~ r_s at fixed rho_s -> t_r,0 halves when r_s doubles
        assert math.isclose(lsb.nu_s_kms(1.8e6, 12.4) / lsb.nu_s_kms(1.8e6, 6.2),
                            2.0, rel_tol=1e-12)


# ---------------------------------------------------------------------------
# 3. NGC 5963 channel behaviour
# ---------------------------------------------------------------------------
class TestNgc5963Channel:
    def test_cdm_is_never_penalised(self):
        for a in (0.0, 1.0, 1.481, 1.93):
            out = lsb.loglike_lsb_ngc5963_core(1e-12, a)
            assert out["loglike"] == 0.0
            assert out["metadata"]["penalised"] is False

    def test_below_limit_is_never_penalised(self):
        out = lsb.loglike_lsb_ngc5963_core(0.15, 0.0)   # sigma_eff = 0.15 < 0.2
        assert out["loglike"] == 0.0
        assert out["metadata"]["sigma_eff_cm2_g"] == pytest.approx(0.15)

    def test_monotone_non_increasing_in_sigma(self):
        grid = np.logspace(-3, 1.5, 40)
        vals = [lsb.loglike_lsb_ngc5963_core(s, 1.481)["loglike"] for s in grid]
        assert all(np.isfinite(vals))
        diffs = np.diff(vals)
        assert np.all(diffs <= 1e-12), "likelihood must never reward a larger sigma/m"

    def test_pinned_penalty_at_twelve_channel_map(self):
        """sigma_m0 = 0.684, a = 1.481 (t13_v2 12-channel MAP) IS penalised by
        NGC 5963: sigma_eff(150 km/s) = 0.684 * (100/150)^1.481."""
        s0, a = 0.684, 1.481
        expected_eff = s0 * (100.0 / 150.0) ** a
        out = lsb.loglike_lsb_ngc5963_core(s0, a)
        assert out["metadata"]["sigma_eff_cm2_g"] == pytest.approx(expected_eff, rel=1e-9)
        assert expected_eff > lsb.NGC5963_SIGMA_LIMIT_CM2G
        expected = -0.5 * (math.log(expected_eff / 0.2) / 0.4) ** 2
        assert out["loglike"] == pytest.approx(expected, rel=1e-9)
        assert out["loglike"] < 0.0

    def test_collapse_time_pinned(self):
        assert lsb.ngc5963_trc_gyr(1.0) == pytest.approx(0.8)
        # S05's core-collapse bound: sigma_0 = 0.08 -> t_rc ~ 1 Hubble time
        assert lsb.ngc5963_trc_gyr(0.08) == pytest.approx(10.0, rel=1e-9)
        assert lsb.ngc5963_trc_gyr(0.0) == float("inf")

    def test_mediator_class_matters(self):
        """The channel must be mediator-aware, not a hidden power law."""
        out_pl = lsb.loglike_lsb_ngc5963_core(0.684, 1.481, mediator_class="power_law")
        out_cp = lsb.loglike_lsb_ngc5963_core(0.684, 1.481, mediator_class="composite")
        out_yk = lsb.loglike_lsb_ngc5963_core(0.684, 1.481, mediator_class="yukawa")
        assert out_pl["metadata"]["sigma_eff_cm2_g"] != out_cp["metadata"]["sigma_eff_cm2_g"]
        assert out_pl["metadata"]["sigma_eff_cm2_g"] != out_yk["metadata"]["sigma_eff_cm2_g"]
        assert all(np.isfinite(o["loglike"]) for o in (out_pl, out_cp, out_yk))

    def test_implied_sigma_m0_limit_reported_when_penalised(self):
        out = lsb.loglike_lsb_ngc5963_core(0.684, 1.481)
        lim = out["metadata"]["sigma_m0_implied_limit"]
        assert 0.0 < lim < 0.684
        # Inverse must actually map back to the adopted limit.
        from mediator_registry import sigma_m_at_v
        assert float(sigma_m_at_v(lim, 1.481, 150.0, mediator_class="power_law")) \
            == pytest.approx(0.2, rel=1e-6)

    def test_unknown_mediator_class_raises(self):
        with pytest.raises(ValueError):
            lsb.loglike_lsb_ngc5963_core(0.5, 1.0, mediator_class="not_a_class")


# ---------------------------------------------------------------------------
# 4. Report plumbing
# ---------------------------------------------------------------------------
class TestReport:
    def test_lsb_core_check_shape(self):
        rep = lsb.lsb_core_check(0.684, 1.481)
        assert rep["ngc5963"]["metadata"]["channel"] == "lsb_ngc5963_core"
        assert len(rep["kitazawa_rows"]) == 5
        v = rep["kitazawa_verdict"]
        assert v["n_lsb_total"] == 5
        assert 0 <= v["n_lsb_forming_core_within_age"] <= 5
        assert 0 <= v["n_lsb_collapsed_by_repo_timescale"] <= 5
        assert "diagnostic only" in v["note"]

    def test_repo_crosscheck_uses_gravothermal(self):
        """gravothermal.py must be reachable from this module (it lives with a
        v0.1-prelim dependency); a silent ImportError here would drop the only
        internal cross-check on the LSB timescale."""
        rows = lsb.kitazawa_lsb_rows(1.0, 1.481)
        assert all("repo_r_core_pred_kpc" in r for r in rows)
        assert all(r["repo_phase"] in ("collapsed", "expanded") for r in rows)

    def test_cdm_limit_verdict(self):
        rep = lsb.lsb_core_check(1e-12, 1.481)
        # CDM: no SIDM core formed within the age, and nothing penalised.
        assert rep["kitazawa_verdict"]["n_lsb_forming_core_within_age"] == 0
        assert rep["ngc5963"]["loglike"] == 0.0


# ---------------------------------------------------------------------------
# 4. Kitazawa+2026 adjudication, extended to all six printed tables
#    (added 2026-11-13 while deciding whether arXiv:2605.05588 may be cited)
# ---------------------------------------------------------------------------
class TestKitazawaAllScenarios:
    def test_three_scenarios_present(self):
        labels = [s["label"] for s in lsb.KITAZAWA_SCENARIOS]
        assert labels == ["z=2.45 (A=100)", "z=7.66 (A=10)", "z=7.88 (A=5)"]
        assert all(len(s["rows"]) == 5 for s in lsb.KITAZAWA_SCENARIOS)
        assert lsb.KITAZAWA_COLLAPSE_IN_T_CORE == 15.0

    def test_1e3_offset_is_uniform_over_all_thirty_entries(self):
        """3 scenarios x 2 cross sections x 5 LSBs = 30 recomputed times.

        All must land near 1e3 x the printed value.  Uniformity is the point: a
        per-object arithmetic slip would scatter; a fixed unit slip does not.
        """
        tables = lsb.reproduce_all_kitazawa_tables()
        assert len(tables) == 3
        n_total = 0
        for t in tables:
            assert t["n_ratios"] == 10
            assert 900.0 < t["ratio_min"] < 1150.0, t["label"]
            assert 900.0 < t["ratio_max"] < 1150.0, t["label"]
            n_total += t["n_ratios"]
        assert n_total == 30

    def test_scenario_catalogues_are_mass_consistent(self):
        """Each scenario's rho_s / r_s must still reproduce the quoted M_dyn.

        If this failed, the ~1e3 could be blamed on bad catalogue parameters
        instead of on the timescale arithmetic.  Measured spread 0.92 - 1.04.
        """
        base = {r[0]: (r[1], r[2]) for r in lsb.KITAZAWA_LSB_TABLE}  # log M, R_c
        for sc in lsb.KITAZAWA_SCENARIOS:
            for (name, r_s, rho_s, _t1, _t01) in sc["rows"]:
                log_m, r_c = base[name]
                ratio = lsb.nfw_mass_within_msun(rho_s, r_s, r_c) / 10.0 ** log_m
                assert 0.85 < ratio < 1.15, (sc["label"], name, ratio)

    def test_printed_test_cannot_discriminate_sigma_1_from_0p1(self):
        """The test the paper's captions apply ('t_core < age') gives 5/5 in
        EVERY table, for both sigma/m = 1 and 0.1 cm^2 g^-1.  It therefore
        cannot be what separates '1 excluded' from '0.1 favoured'."""
        for r in lsb.kitazawa_interpretation_audit():
            assert r["n_t_core_lt_age"] == r["n"] == 5, r

    def test_discrimination_needs_the_15x_collapse_threshold(self):
        """Only the paper's own collapse scale (~450 t_r,0 = 15 t_core) separates
        the two cross sections: several collapsed at sigma/m = 1, none at 0.1."""
        audit = lsb.kitazawa_interpretation_audit()
        for r in audit:
            if r["sigma_m"] == 0.1:
                assert r["n_collapse_lt_age"] == 0, r
            else:
                assert r["n_collapse_lt_age"] >= 3, r


# ---------------------------------------------------------------------------
# 5. Production adoption (Channel 14 in the T13_v2 ladder, adopted 2026-11-13)
# ---------------------------------------------------------------------------
class TestProductionAdoption:
    def _ladder(self):
        import t13_v2_12channel_2025_2026 as lad
        return lad

    def test_ladder_adds_exactly_the_lsb_term(self):
        """The production 13-channel ladder must equal the 12-channel ladder plus
        the NGC 5963 term — no extra factor, no double count."""
        lad = self._ladder()
        for s0, a in ((0.05, 1.5), (0.13, 1.49), (1.0, 1.2), (5.0, 0.5)):
            got = lad.loglike_13channel_lsb(s0, a)
            want = (lad.loglike_12channel(s0, a)
                    + lsb.loglike_lsb_ngc5963_core(s0, a)["loglike"])
            assert abs(got - want) < 1e-12, (s0, a, got, want)

    def test_ladder_stays_one_sided(self):
        """CDM must still be allowed: at sigma -> 0 the LSB term is exactly 0."""
        lad = self._ladder()
        for a in (-2.0, 0.0, 1.49, 2.0):
            delta = (lad.loglike_13channel_lsb(1e-12, a)
                     - lad.loglike_12channel(1e-12, a))
            assert delta == 0.0, (a, delta)
        # and it never rewards a larger sigma/m
        assert (lad.loglike_13channel_lsb(0.05, 1.5)
                > lad.loglike_13channel_lsb(1.0, 1.5))

    def test_artifact_records_adoption_and_seed(self):
        """The regenerated baseline artifact must carry the seed and the
        Channel 14 adoption (rule 32: seed pinned in the artifact itself)."""
        root = next(a for a in _pathlib.Path(__file__).resolve().parents
                    if (a / "scripts" / "paths.py").exists())
        art = (root / "v0.3-prelim" / "data" / "results"
               / "t13_v2_12channel_2025_2026.json")
        if not art.exists():
            pytest.skip(f"artifact not present: {art}")
        import json
        d = json.loads(art.read_text(encoding="utf-8"))
        ss = d["sampler_settings"]
        assert ss["seed"] and ss["nlive"] and ss["dlogz"]
        assert "PRODUCTION" in d["channel_14_status"]
        assert d["channel_14_limit_used_cm2_g"] == 0.2
        for key in ("res_12channel", "res_13channel_lsb", "res_13channel_lsb_tight"):
            assert d[key]["seed"] == ss["seed"], key
        # adding an upper bound can only lower the evidence
        assert d["res_13channel_lsb"]["log_Z"] < d["res_12channel"]["log_Z"]
        assert (d["res_13channel_lsb_tight"]["log_Z"]
                < d["res_13channel_lsb"]["log_Z"])


class TestKitazawaUnitAdjudication:
    """The ~1e3 offset adjudicated WITHOUT the author (owner decision 2026-11-13).

    Pins the three facts the verdict rests on: (i) printed x 1e3 reproduces our
    evaluation of eq. (11)+(7) on every halo, (ii) Yang+ 2024 eq. 2.2 has the same
    halo scaling (constant ratio) and reproduces its own BM2 anchor, (iii) the
    repo's Balberg+ 2002 convention sits between the two, so the disagreement is
    a convention/unit issue and not arithmetic.
    """

    def test_printed_times_1e3_reproduces_eq11_on_every_halo(self):
        rows = lsb.kitazawa_unit_adjudication()
        assert len(rows) == 5
        for r in rows:
            ratio = r["printed_x1000_over_recomputed"]
            assert 0.94 < ratio < 1.06, (r["name"], ratio)

    def test_yang_scaling_is_constant_across_halos(self):
        """Same functional form -> ratio must be identical on all five halos."""
        ratios = [r["yang_over_eq11"] for r in lsb.kitazawa_unit_adjudication()]
        assert max(ratios) - min(ratios) < 1e-9 * max(ratios), ratios
        assert 8.0 < ratios[0] < 9.0, ratios[0]

    def test_yang_bm2_anchor_matches_published_collapse_time(self):
        """Our cross-check must be calibrated, or the 1e3 argument is worthless."""
        import gravothermal_yang2024 as yang
        cal = yang.collapse_time_calibrated_gyr(7.1, 2.74e8, 0.141)
        assert abs(cal - 28.7) / 28.7 < 0.01, cal

    def test_balberg_convention_lands_between_printed_and_eq11(self):
        for r in lsb.kitazawa_unit_adjudication():
            bal = r["balberg2002_repo_gyr"]
            assert r["printed_gyr"] < bal < r["eq11_recomputed_gyr"], r
            assert 6.5 < bal < 7.5, r["name"]

    def test_four_conventions_span_four_orders_of_magnitude(self):
        """The honest headline: LSB core-formation time is convention-dominated."""
        rows = lsb.kitazawa_unit_adjudication()
        spans = [r["printed_gyr"] for r in rows] + \
                [r["yang2024_bm2_calibrated_gyr"] for r in rows]
        assert max(spans) / min(spans) > 1.0e4, (min(spans), max(spans))
