"""Tier-1 geometry contract and service adapter."""

from geometry.contract import (
    InstantGeometry,
    InstantRequest,
    Limitations,
    PlanningStatus,
    Provenance,
    ScenarioComparison,
    WindowRequest,
    WindowSample,
    WindowSummary,
)
from geometry.physics import (
    classify_earth_visibility,
    decide_planning_status,
    first_state_change_hours,
    horizontal_incidence_pct,
    horizontal_incidence_proxy,
    solar_disk_fraction,
)

# GeometryService imports Skyfield; import it only when kernels are available.
try:
    from geometry.service import GeometryService
except ModuleNotFoundError:  # pragma: no cover
    GeometryService = None  # type: ignore

__all__ = [
    "InstantGeometry",
    "InstantRequest",
    "Limitations",
    "PlanningStatus",
    "Provenance",
    "ScenarioComparison",
    "WindowRequest",
    "WindowSample",
    "WindowSummary",
    "classify_earth_visibility",
    "decide_planning_status",
    "first_state_change_hours",
    "horizontal_incidence_pct",
    "horizontal_incidence_proxy",
    "solar_disk_fraction",
    "GeometryService",
]
