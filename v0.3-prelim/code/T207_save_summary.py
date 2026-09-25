"""Save the final T207 summary JSON."""
import json
from pathlib import Path

results = {
    't207_de_initial': {
        'prescription': 'free_f_H (9 free params)',
        'log_L_peak': -0.0000,
        'best_params': {
            'sigma_0': 0.1985,
            'sigma_peak_HH_1': 697.3731,
            'sigma_0_HL': 0.0938,
            'sigma_peak_HL': 1.8948,
            'v_HL': 178.1803,
            'sigma_0_LL': 0.0004,
            'a_slope': 1.2104,
            'f_H_cf': 0.9580,
            'f_H_cc': 0.0008,
        },
        'de_success': False,
        'note': 'DE maxiter reached, log L=0 found but not declared converged',
    },
    't207b_emcee_free': {
        'prescription': 'free_f_H emcee (32 walkers x 5000 steps)',
        'log_L_max': -0.0000,
        'converged': False,
        'autocorr_note': 'chain shorter than 50x tau; use with caution',
        'posterior_median': {
            'sigma_0': 0.2259,
            'sigma_peak_HH_1': 530.7,
            'sigma_0_HL': 0.1052,
            'sigma_peak_HL': 0.78,
            'v_HL': 132.9,
            'sigma_0_LL': 0.0009,
            'a_slope': 1.10,
            'f_H_cf': 0.7415,
            'f_H_cc': 0.0023,
        },
        'posterior_std': {
            'sigma_0': 0.1448,
            'sigma_peak_HH_1': 276.6,
            'sigma_0_HL': 0.1299,
            'sigma_peak_HL': 0.5563,
            'v_HL': 45.9,
            'sigma_0_LL': 0.0008,
            'a_slope': 0.2736,
            'f_H_cf': 0.1455,
            'f_H_cc': 0.0053,
        },
    },
    't207_prescription_modes_de': {
        'borrowed': {'log_L_peak': -0.728, 'sigma_peak_HH_1': 19.9, 'cloud_9_log_L': -0.445},
        'yang':     {'log_L_peak': -0.979, 'sigma_peak_HH_1': 10.0, 'cloud_9_log_L': -0.472},
        't202':     {'log_L_peak': -2.149, 'sigma_peak_HH_1': 10.0, 'cloud_9_log_L': -0.467},
    },
    't207_prescription_modes_emcee': {
        'borrowed': {'log_L_max': -0.758, 'sigma_peak_HH_1': 25.3, 'cloud_9_log_L_implied': '~-0.4'},
        'yang':     {'log_L_max': -0.991, 'sigma_peak_HH_1': 13.2, 'cloud_9_log_L_implied': '~-0.4'},
        't202':     {'log_L_max': 'CRASHED', 'note': 'initial state condition number; not run'},
    },
    't207c_smart_de_phase44_init': {
        'borrowed': {'log_L_peak': -0.728, 'sigma_peak_HH_1': 19.6, 'note': 'same as initial DE'},
        'yang':     {'log_L_peak': -0.980, 'sigma_peak_HH_1': 10.0, 'note': 'same as initial DE'},
        't202':     {'log_L_peak': -2.149, 'sigma_peak_HH_1': 10.0, 'note': 'same as initial DE'},
    },
    'physical_interpretation': {
        'sigma_peak_HH_1_implication': (
            '531-697 cm^2/g at v=29 km/s (Cloud-9 peak). 3.6-4.7x Yang+ peak. '
            'Requires (700/196)^(1/4)=1.42x larger coupling OR 1.42x lighter mediator. '
            'More tuned UV model than Phase 44 best-fit.'
        ),
        'f_H_cf_implication': (
            '0.74 +/- 0.15. Barely within Yang+ Fig. 2 range [0.40, 0.70]. '
            'Lower end of plausible segregation.'
        ),
        'f_H_cc_implication': (
            '0.0023 +/- 0.005. 200x below Yang+ lower bound. '
            'Extreme segregation regime: heavy component has sunk to the inner core, '
            'leaving observation radius (r=0.2 r_vir) light-dominated. '
            'NOT predicted by Yang+ 2025 (modest segregation).'
        ),
        'v_HL_implication': (
            '132 +/- 46 km/s. Off-target from SPARC v=100 by 32 km/s. '
            'HL contributes via Lorentzian tail at v=100, NOT via direct resonance. '
            'Requires two mediators with similar (not identical) mass scales. '
            'NOT the design-memo-assumed mediator B with HL peak exactly at 100.'
        ),
        'causality_at_cloud_9': (
            't_core = 0.02 Myr << t_cross = 11.6 Myr. '
            'Even after 3x TCROSS_CAP_FACTOR, t_core = 34.9 Myr. '
            'Causality is violated under standard Balberg+ 2002 interpretation. '
            'This regime is substructure-physics territory.'
        ),
        'prescription_modes_impossibility': (
            'Under borrowed/yang/t202 (f_H within Yang+/T202 range), '
            'NO solution satisfies all 8 channels. Even with sigma_peak_HH_1=200, '
            'the dSph ceiling is violated (sigma_eff(15)=0.45 for borrowed, '
            '1.02 for yang, 1.88 for t202 — all > 0.032 ceiling). '
            'The free-fit extreme solution (f_H_cf=0.96, f_H_cc=0.0008) '
            'is the ONLY way to satisfy all 8.'
        ),
    },
    'honest_verdict': {
        'what_works': (
            'Three-term decomposition DOES allow satisfying all 8 channels simultaneously. '
            'SPARC structural failure (F1) is resolved at the level of mathematical fit. '
            'Interior posterior found (no boundary peak), confirming the design memo claim.'
        ),
        'what_doesnt': (
            'The fit values require: sigma_peak_HH_1 = 531-697 cm^2/g (3.6-4.7x Yang+); '
            'f_H_cc = 0.0023 (200x below Yang+); v_HL = 132 km/s (off-target from SPARC 100); '
            'causality violated at Cloud-9 (t_core << t_cross). '
            'These are extreme regimes not motivated by first-principles physics.'
        ),
        'paper_implication': (
            'Under prescription modes (f_H within Yang+/T202 range), '
            '4 of 8 channels pass. Under free fit, 8 of 8 pass with extreme parameters. '
            'The design memo promised "7 of 8 with interior posterior". '
            'What we actually find: 4 of 8 under physical f_H constraints, '
            '8 of 8 under extreme f_H. The "interior posterior" finding is correct; '
            'the "7 of 8" is not.'
        ),
    },
}

out = Path(r'C:\Users\lamkuenai\projects\sidm-composite-dm-mediator\v0.3-prelim\data\results\t207_final_summary.json')
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(json.dumps(results, indent=2))
print(f'Saved: {out}')
print()
print(json.dumps(results['honest_verdict'], indent=2))