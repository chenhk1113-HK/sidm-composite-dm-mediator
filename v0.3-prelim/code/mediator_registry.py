"""Mediator-class registry for SIDM sigma/m(v) functional forms.

This module provides a registry of sigma/m(v) functional forms for the
Phase 5b channel-likelihood rewrite. The registry pattern allows channel
likelihoods to accept a generic 'mediator_class' parameter instead of
being baked into the power-law form.

Usage:
    from mediator_registry import MEDIATOR_FORMS

    # Power-law (T39 reference)
    sigma_m = MEDIATOR_FORMS['power_law'](sigma_m_0, a, v)

    # Yukawa (vector/dark photon kinetic mixing)
    sigma_m = MEDIATOR_FORMS['yukawa'](sigma_m_0, a, v)

    # Scalar/Higgs portal
    sigma_m = MEDIATOR_FORMS['scalar_portal'](sigma_m_0, a, v)

    # Composite (dark pion resonance)
    sigma_m = MEDIATOR_FORMS['composite'](sigma_m_0, a, v)
"""

import numpy as np


# Reference velocity (km/s) per T39 convention
V_REF = 100.0


def _sigma_m_power_law(sigma_m_0: float, a: float, v: float, **kwargs) -> float:
    """sigma/m(v) = sigma/m_0 * (v/v_ref)^(-a).

    Power-law phenomenological reference (T39 form).
    """
    return sigma_m_0 * (v / V_REF) ** (-a)


def _sigma_m_yukawa(
    sigma_m_0: float,
    a: float,
    v: float,
    m_chi_gev: float = 40.0,
    m_aprime_mev: float = 10.0,
    **kwargs,
) -> float:
    """Yukawa form (vector/dark photon kinetic mixing).

    sigma/m(v) = prefactor / (1 + (v/v_dm)^2)
    where v_dm ~ sqrt(m_chi * m_A') / m_chi is the characteristic velocity.

    For m_chi=40 GeV, m_A'=10 MeV: v_dm ~ 0.5 km/s.
    At v >> v_dm: sigma/m ~ 1/v^2 (over-strong velocity dependence).
    """
    m_chi_mev = m_chi_gev * 1000.0
    v_dm_units = np.sqrt(m_chi_mev * m_aprime_mev) / m_chi_mev  # in c=1 units
    v_dm_km_s = v_dm_units * 3e5  # convert c=1 to km/s
    if v_dm_km_s < 1e-6:
        v_dm_km_s = 1e-6
    prefactor = sigma_m_0 * (1 + (V_REF / v_dm_km_s) ** 2)
    return prefactor / (1 + (v / v_dm_km_s) ** 2)


def _sigma_m_scalar_portal(
    sigma_m_0: float,
    a: float,
    v: float,
    alpha_h: float = 0.5,
    **kwargs,
) -> float:
    """Scalar/Higgs portal (linear velocity dependence).

    sigma/m(v) = sigma/m_0 * (1 + alpha_h * (v/v_ref - 1))

    For alpha_h ~ 0.5: sigma/m drops by ~36% per decade in velocity.
    """
    return sigma_m_0 * (1 + alpha_h * (v / V_REF - 1))


def _sigma_m_composite(
    sigma_m_0: float,
    a: float,
    v: float,
    v_R: float = 30.0,
    delta_v: float = 50.0,
    **kwargs,
) -> float:
    """Composite (dark-pion resonance).

    sigma/m(v) = sigma/m_0 * exp(-(v - v_R)^2 / (2 * delta_v^2))

    Gaussian resonance at v_R = 30 km/s (dwarf regime), width delta_v = 50 km/s.
    For numerical stability, exponent is clipped at -100 to avoid underflow.
    """
    exponent = -((v - v_R) ** 2) / (2 * delta_v ** 2)
    exponent = max(exponent, -100.0)
    return sigma_m_0 * np.exp(exponent)


# Registry
MEDIATOR_FORMS = {
    "power_law": _sigma_m_power_law,
    "yukawa": _sigma_m_yukawa,
    "scalar_portal": _sigma_m_scalar_portal,
    "composite": _sigma_m_composite,
}


MEDIATOR_NAMES = {
    "power_law": "Power-law (phenomenological reference)",
    "yukawa": "Yukawa (dark photon kinetic mixing)",
    "scalar_portal": "Scalar/Higgs portal",
    "composite": "Composite (dark-pion resonance)",
}


def sigma_m_at_v(
    sigma_m_0: float,
    a: float,
    v: float,
    mediator_class: str = "power_law",
) -> float:
    """Dispatcher: sigma/m(v) for the specified mediator class.

    Backward-compatible wrapper. Defaults to 'power_law' to preserve
    existing call sites.
    """
    if mediator_class not in MEDIATOR_FORMS:
        raise ValueError(
            f"Unknown mediator_class: {mediator_class}. "
            f"Valid: {list(MEDIATOR_FORMS.keys())}"
        )
    return MEDIATOR_FORMS[mediator_class](sigma_m_0, a, v)