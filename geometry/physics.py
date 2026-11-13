"""Pure geometric helpers for the corrected Tier-1 contract.

No I/O. No ephemeris library dependency.
"""

from __future__ import annotations

import math
from typing import Optional, Sequence

from geometry.contract import (
    EARTH_GRAZING_CLEARANCE_DEG,
    EARTH_REMAINING_CAUTION_H,
    LOW_SUNLIGHT_PCT,
    SUN_DISK_RADIUS_DEG,
    SUN_REMAINING_CAUTION_H,
    EarthVisibilityState,
    PlanningStatus,
)


def solar_disk_fraction(clearance_deg: float) -> float:
    """Geometric chord fraction across ±R_sun. Not an energy quantity."""
    r = SUN_DISK_RADIUS_DEG
    if clearance_deg <= -r:
        return 0.0
    if clearance_deg >= r:
        return 1.0
    return (clearance_deg + r) / (2.0 * r)


def horizontal_incidence_proxy(
    sun_elevation_deg: float,
    clearance_deg: float,
) -> float:
    """First-order horizontal-surface incidence proxy in [0, 1].

    Assumptions (must appear in Limitations / UI):
    - flat horizontal collector
    - vacuum, no atmosphere
    - cosine law on geometric center elevation
    - optional geometric disk fraction when partially occulted by approximate mask
    - not an array power model
    """
    mu = max(0.0, math.sin(math.radians(sun_elevation_deg)))
    f_disk = solar_disk_fraction(clearance_deg)
    return mu * f_disk


def horizontal_incidence_pct(sun_elevation_deg: float, clearance_deg: float) -> float:
    return 100.0 * horizontal_incidence_proxy(sun_elevation_deg, clearance_deg)


def classify_earth_visibility(
    earth_elevation_deg: float,
    earth_clearance_deg: float,
) -> tuple[EarthVisibilityState, str]:
    """Instant Earth visibility from elevation and approximate clearance.

    FAR_SIDE is intentionally absent at the instant level.
    """
    if earth_elevation_deg < 0.0:
        return "BELOW_HORIZON", "Earth center below geometric horizon"
    if earth_clearance_deg < 0.0:
        return (
            "TERRAIN_BLOCKED",
            f"Blocked by approximate terrain mask (+{earth_clearance_deg * -1:.2f}° needed)",
        )
    if earth_clearance_deg < EARTH_GRAZING_CLEARANCE_DEG:
        return (
            "GRAZING",
            f"Low clearance ({earth_clearance_deg:.2f}°) — multipath risk",
        )
    return "VISIBLE", "Clear geometric line of sight above approximate mask"


def first_state_change_hours(
    flags: Sequence[bool],
    step_hours: float,
) -> Optional[float]:
    """Hours from series start until the first boolean change.

    Returns the sample boundary of the first change (no sub-step root finding).
    null if the flag is constant across the series.
    """
    if len(flags) < 2:
        return None
    initial = flags[0]
    for i in range(1, len(flags)):
        if flags[i] != initial:
            return i * step_hours
    return None


def decide_planning_status(
    *,
    solar_disk_visible_at_t0: bool,
    earth_visible_at_t0: bool,
    sunlight_pct: float,
    earth_visible_pct: float,
    hours_to_sun_change: Optional[float],
    hours_to_earth_change: Optional[float],
    data_ok: bool = True,
) -> tuple[PlanningStatus, str, str]:
    """Deterministic first-order planning heuristic. Never a flight rule."""
    if not data_ok:
        return (
            "DATA_INSUFFICIENT",
            "Data insufficient",
            "Geometry data missing or invalid for this request.",
        )

    if (not solar_disk_visible_at_t0) and sunlight_pct < LOW_SUNLIGHT_PCT:
        return (
            "UNFAVORABLE",
            "Prolonged low sunlight",
            f"Sun not visible at epoch and only {sunlight_pct:.0f}% of the window is sunlit.",
        )

    if not solar_disk_visible_at_t0:
        reason = "Sun not visible at selected epoch (local night)."
        if hours_to_sun_change is not None:
            reason += f" Next sun-state change in {hours_to_sun_change:.1f} h."
        return "UNFAVORABLE", "Local night at epoch", reason

    if hours_to_sun_change is not None and hours_to_sun_change < SUN_REMAINING_CAUTION_H:
        return (
            "MARGINAL",
            "Sun window closing soon",
            f"Only {hours_to_sun_change:.1f} h of continuous sunlight remain in the sample grid.",
        )

    if earth_visible_pct <= 0.0:
        return (
            "MARGINAL",
            "No Earth visibility in window",
            "Earth remains below the approximate horizon for the entire analysis window.",
        )

    if not earth_visible_at_t0:
        reason = "Earth not visible at selected epoch."
        if hours_to_earth_change is not None:
            reason += f" Next Earth-state change in {hours_to_earth_change:.1f} h."
        return "MARGINAL", "Earth not visible at epoch", reason

    if hours_to_earth_change is not None and hours_to_earth_change < EARTH_REMAINING_CAUTION_H:
        return (
            "MARGINAL",
            "Earth window closing soon",
            f"Only {hours_to_earth_change:.1f} h of continuous Earth visibility remain.",
        )

    return (
        "FAVORABLE",
        "Favorable (first-order)",
        "Sun and Earth are geometrically favorable at the epoch under the stated assumptions.",
    )
