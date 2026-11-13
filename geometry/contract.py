"""Frozen Tier-1 geometry contract (Scientific Contract Correction 03).

All angles in degrees. All times timezone-aware UTC.
Python geometry service is the sole producer of these structures.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Literal, Optional


# ---------------------------------------------------------------------------
# Constants (server-side only)
# ---------------------------------------------------------------------------

SUN_DISK_RADIUS_DEG = 0.266
EARTH_GRAZING_CLEARANCE_DEG = 0.8
SUN_REMAINING_CAUTION_H = 48.0
EARTH_REMAINING_CAUTION_H = 24.0
LOW_SUNLIGHT_PCT = 15.0

EarthVisibilityState = Literal[
    "VISIBLE",
    "GRAZING",
    "TERRAIN_BLOCKED",
    "BELOW_HORIZON",
]

PlanningStatus = Literal[
    "FAVORABLE",
    "MARGINAL",
    "UNFAVORABLE",
    "DATA_INSUFFICIENT",
]


@dataclass(frozen=True)
class Provenance:
    method: Literal["spice_de421_skyfield", "horizons", "analytical_fallback"]
    frame: str
    kernels_or_source: str
    notes: str
    generated_at_utc: str


@dataclass(frozen=True)
class Limitations:
    geometric_only: bool = True
    no_refraction: bool = True
    no_terrain_dem: bool = True
    no_solar_disk_model_beyond_proxy: bool = True
    no_power_system_model: bool = True
    no_link_budget: bool = True
    no_flight_rule_status: bool = True
    summary: str = (
        "Geometric planning aid only. Elevations are vacuum center-of-body "
        "directions. Approximate mask is not real LOLA topography. "
        "Horizontal incidence proxy assumes a flat surface, vacuum, and "
        "cosine law only — not array power. Earth visibility is elevation-"
        "based and is not a validated communications link. Status labels "
        "are first-order heuristics, not flight rules."
    )


@dataclass(frozen=True)
class InstantRequest:
    latitude_deg: float
    longitude_deg: float
    epoch_utc: datetime
    horizon_mask_deg: float = 0.0
    site_id: Optional[str] = None


@dataclass(frozen=True)
class WindowRequest:
    latitude_deg: float
    longitude_deg: float
    start_utc: datetime
    duration_days: float = 30.0
    step_hours: float = 1.0
    horizon_mask_deg: float = 0.0
    site_id: Optional[str] = None


@dataclass(frozen=True)
class InstantGeometry:
    request: InstantRequest

    sun_elevation_deg: float
    sun_azimuth_deg: float
    earth_elevation_deg: float
    earth_azimuth_deg: float

    sun_terrain_mask_deg: float
    earth_terrain_mask_deg: float
    sun_clearance_deg: float
    earth_clearance_deg: float

    geometric_sun_visible: bool
    geometric_earth_visible: bool
    approx_sun_clear: bool
    approx_earth_clear: bool
    solar_disk_visible: bool
    solar_disk_fully_clear: bool

    solar_disk_fraction: float

    horizontal_incidence_proxy: float
    horizontal_incidence_pct: float

    earth_visibility: EarthVisibilityState
    earth_visibility_reason: str

    # Optional; None means not computed by the current geometry engine.
    # Must never be treated as a verified physical vector when None.
    sub_solar_lat_deg: Optional[float]
    sub_solar_lon_deg: Optional[float]
    sub_earth_lat_deg: Optional[float]
    sub_earth_lon_deg: Optional[float]

    provenance: Provenance
    limitations: Limitations


@dataclass(frozen=True)
class WindowSample:
    offset_hours: float
    offset_days: float
    epoch_utc: datetime
    sun_elevation_deg: float
    sun_azimuth_deg: float
    sun_clearance_deg: float
    geometric_sun_visible: bool
    approx_sun_clear: bool
    solar_disk_visible: bool
    horizontal_incidence_pct: float
    earth_elevation_deg: float
    earth_azimuth_deg: float
    earth_clearance_deg: float
    geometric_earth_visible: bool
    approx_earth_clear: bool
    earth_visible_for_aggregate: bool


@dataclass(frozen=True)
class WindowSummary:
    request: WindowRequest
    series: tuple

    sunlight_hours: float
    sunlight_pct: float
    earth_visible_hours: float
    earth_visible_pct: float
    simultaneous_sun_earth_visible_hours: float
    simultaneous_sun_earth_visible_pct: float

    peak_sun_elevation_deg: float
    min_sun_elevation_deg: float
    peak_earth_elevation_deg: float
    min_earth_elevation_deg: float

    hours_to_sun_state_change: Optional[float]
    hours_to_earth_state_change: Optional[float]

    status: PlanningStatus
    status_label: str
    status_reason: str

    provenance: Provenance
    limitations: Limitations


@dataclass(frozen=True)
class ScenarioComparison:
    scenario_a: WindowSummary
    scenario_b: WindowSummary
    sunlight_pct_delta: float
    earth_visible_pct_delta: float
    simultaneous_pct_delta: float
    primary_score: float
    primary_score_definition: str = (
        "Δ simultaneous Sun+Earth visibility percentage points (B − A)"
    )
