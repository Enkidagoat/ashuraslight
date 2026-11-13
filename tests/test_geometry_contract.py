"""Unit tests for corrected Tier-1 physics and status logic.

These tests do not require SPICE kernels.
"""

from __future__ import annotations

import math

import pytest

from geometry.physics import (
    classify_earth_visibility,
    decide_planning_status,
    first_state_change_hours,
    horizontal_incidence_pct,
    horizontal_incidence_proxy,
    solar_disk_fraction,
)
from geometry.contract import SUN_DISK_RADIUS_DEG


# ---------------------------------------------------------------------------
# Solar disk fraction (geometric chord only)
# ---------------------------------------------------------------------------

def test_solar_disk_fraction_extremes() -> None:
    r = SUN_DISK_RADIUS_DEG
    assert solar_disk_fraction(-r - 1.0) == 0.0
    assert solar_disk_fraction(-r) == 0.0
    assert solar_disk_fraction(r) == 1.0
    assert solar_disk_fraction(r + 1.0) == 1.0
    assert solar_disk_fraction(0.0) == pytest.approx(0.5)


def test_solar_disk_fraction_midpoint() -> None:
    r = SUN_DISK_RADIUS_DEG
    assert solar_disk_fraction(r / 2) == pytest.approx(0.75)
    assert solar_disk_fraction(-r / 2) == pytest.approx(0.25)


# ---------------------------------------------------------------------------
# Horizontal incidence proxy
# ---------------------------------------------------------------------------

def test_horizontal_incidence_zenith() -> None:
    # e = 90°, fully clear → sin(90)=1 → 100%
    assert horizontal_incidence_proxy(90.0, 1.0) == pytest.approx(1.0)
    assert horizontal_incidence_pct(90.0, 1.0) == pytest.approx(100.0)


def test_horizontal_incidence_horizon() -> None:
    assert horizontal_incidence_proxy(0.0, 1.0) == pytest.approx(0.0)
    assert horizontal_incidence_pct(0.0, 1.0) == pytest.approx(0.0)


def test_horizontal_incidence_below_horizon() -> None:
    assert horizontal_incidence_proxy(-10.0, -10.0) == pytest.approx(0.0)


def test_horizontal_incidence_partial_disk() -> None:
    # e=30°, clearance=0 → f_disk=0.5, sin(30)=0.5 → 0.25
    proxy = horizontal_incidence_proxy(30.0, 0.0)
    assert proxy == pytest.approx(0.5 * 0.5)
    assert horizontal_incidence_pct(30.0, 0.0) == pytest.approx(25.0)


def test_horizontal_incidence_cosine_law() -> None:
    # Fully clear, e=30° → sin(30)=0.5
    assert horizontal_incidence_proxy(30.0, 1.0) == pytest.approx(0.5)
    # e=60° → √3/2
    assert horizontal_incidence_proxy(60.0, 1.0) == pytest.approx(math.sqrt(3) / 2)


# ---------------------------------------------------------------------------
# Earth visibility classification (no FAR_SIDE at instant)
# ---------------------------------------------------------------------------

def test_earth_visibility_states() -> None:
    state, _ = classify_earth_visibility(-5.0, -5.0)
    assert state == "BELOW_HORIZON"

    state, _ = classify_earth_visibility(2.0, -1.0)
    assert state == "TERRAIN_BLOCKED"

    state, _ = classify_earth_visibility(2.0, 0.4)
    assert state == "GRAZING"

    state, _ = classify_earth_visibility(5.0, 2.0)
    assert state == "VISIBLE"


def test_earth_visibility_never_returns_far_side() -> None:
    for el, cl in [(-90.0, -90.0), (0.0, -1.0), (10.0, 10.0), (-0.1, -0.1)]:
        state, _ = classify_earth_visibility(el, cl)
        assert state != "FAR_SIDE"
        assert state in {
            "VISIBLE",
            "GRAZING",
            "TERRAIN_BLOCKED",
            "BELOW_HORIZON",
        }


# ---------------------------------------------------------------------------
# Event timing
# ---------------------------------------------------------------------------

def test_first_state_change_hours() -> None:
    flags = [True, True, True, False, False]
    assert first_state_change_hours(flags, 1.0) == pytest.approx(3.0)

    flags2 = [False, False, True]
    assert first_state_change_hours(flags2, 2.0) == pytest.approx(4.0)

    assert first_state_change_hours([True, True, True], 1.0) is None
    assert first_state_change_hours([False], 1.0) is None


# ---------------------------------------------------------------------------
# Planning status matrix
# ---------------------------------------------------------------------------

def test_status_data_insufficient() -> None:
    s, label, _ = decide_planning_status(
        solar_disk_visible_at_t0=True,
        earth_visible_at_t0=True,
        sunlight_pct=80.0,
        earth_visible_pct=80.0,
        hours_to_sun_change=None,
        hours_to_earth_change=None,
        data_ok=False,
    )
    assert s == "DATA_INSUFFICIENT"
    assert "insufficient" in label.lower() or "Data" in label


def test_status_unfavorable_prolonged_night() -> None:
    s, label, _ = decide_planning_status(
        solar_disk_visible_at_t0=False,
        earth_visible_at_t0=True,
        sunlight_pct=5.0,
        earth_visible_pct=50.0,
        hours_to_sun_change=100.0,
        hours_to_earth_change=None,
    )
    assert s == "UNFAVORABLE"
    assert "sunlight" in label.lower() or "night" in label.lower() or "Prolonged" in label


def test_status_unfavorable_local_night() -> None:
    s, label, _ = decide_planning_status(
        solar_disk_visible_at_t0=False,
        earth_visible_at_t0=True,
        sunlight_pct=40.0,
        earth_visible_pct=50.0,
        hours_to_sun_change=12.0,
        hours_to_earth_change=None,
    )
    assert s == "UNFAVORABLE"


def test_status_marginal_sun_closing() -> None:
    s, label, _ = decide_planning_status(
        solar_disk_visible_at_t0=True,
        earth_visible_at_t0=True,
        sunlight_pct=60.0,
        earth_visible_pct=60.0,
        hours_to_sun_change=24.0,
        hours_to_earth_change=None,
    )
    assert s == "MARGINAL"
    assert "Sun" in label or "sun" in label.lower()


def test_status_marginal_no_earth_in_window() -> None:
    s, label, _ = decide_planning_status(
        solar_disk_visible_at_t0=True,
        earth_visible_at_t0=False,
        sunlight_pct=80.0,
        earth_visible_pct=0.0,
        hours_to_sun_change=None,
        hours_to_earth_change=None,
    )
    assert s == "MARGINAL"


def test_status_favorable() -> None:
    s, label, reason = decide_planning_status(
        solar_disk_visible_at_t0=True,
        earth_visible_at_t0=True,
        sunlight_pct=70.0,
        earth_visible_pct=70.0,
        hours_to_sun_change=100.0,
        hours_to_earth_change=100.0,
    )
    assert s == "FAVORABLE"
    assert "first-order" in reason.lower() or "Favorable" in label


def test_status_labels_are_neutral() -> None:
    """No GO / NO-GO flight-rule language in returned labels."""
    cases = [
        dict(
            solar_disk_visible_at_t0=True,
            earth_visible_at_t0=True,
            sunlight_pct=80,
            earth_visible_pct=80,
            hours_to_sun_change=None,
            hours_to_earth_change=None,
        ),
        dict(
            solar_disk_visible_at_t0=False,
            earth_visible_at_t0=True,
            sunlight_pct=5,
            earth_visible_pct=50,
            hours_to_sun_change=10,
            hours_to_earth_change=None,
        ),
    ]
    for kwargs in cases:
        _, label, reason = decide_planning_status(**kwargs)
        combined = (label + " " + reason).upper()
        assert "GO FOR LANDING" not in combined
        assert "NO-GO" not in combined
        assert "FLIGHT" not in combined
