"""Source-traceable lunar candidate-region comparison points."""

from __future__ import annotations

from dataclasses import dataclass
import math


@dataclass(frozen=True)
class Site:
    site_id: str
    name: str
    latitude_deg: float
    longitude_deg: float
    latitude_convention: str
    longitude_convention: str
    reference_frame: str
    elevation_m: float
    coordinate_interpretation: str
    source_url: str
    source_coordinate_text: str

    def __post_init__(self) -> None:
        if not self.site_id or not self.name or not self.source_url:
            raise ValueError("Site ID, name, and source URL are required.")
        if self.latitude_convention != "planetocentric":
            raise ValueError("Only planetocentric latitude is supported.")
        if self.longitude_convention != "signed east-positive degrees":
            raise ValueError("Longitude must be signed degrees with east positive.")
        if self.reference_frame != "MOON_ME_DE421":
            raise ValueError("Site coordinates must use the MOON_ME_DE421 frame.")
        if not math.isfinite(self.latitude_deg) or not -90.0 <= self.latitude_deg <= 90.0:
            raise ValueError(f"Invalid latitude for {self.name}.")
        if not math.isfinite(self.longitude_deg) or not -180.0 <= self.longitude_deg <= 180.0:
            raise ValueError(f"Invalid longitude for {self.name}.")
        if not math.isfinite(self.elevation_m):
            raise ValueError(f"Invalid elevation assumption for {self.name}.")
        if not self.coordinate_interpretation:
            raise ValueError(f"Coordinate interpretation is required for {self.name}.")


COORDINATE_SOURCE = "https://www.sciencedirect.com/science/article/pii/S0094576524006234"
FRAME_INTERPRETATION = (
    "The source publishes exact DMS coordinates and hemisphere labels but does not state "
    "a coordinate reference frame in its coordinate table/full text. The app provisionally "
    "interprets them as planetocentric in the USGS-recommended DE421 Mean Earth frame."
)

# Published candidate points from Table 3 of Peña-Asensio et al.
# Decimal values are direct conversions of the published DMS coordinates. The source
# coordinate frame is not explicit; see FRAME_INTERPRETATION and docs/technical-decisions.md.
CANDIDATE_SITES: tuple[Site, ...] = (
    Site(
        site_id="DM2-358",
        name="Nobile Rim 2 — published point 358",
        latitude_deg=-84.201558333333,
        longitude_deg=60.699891666667,
        latitude_convention="planetocentric",
        longitude_convention="signed east-positive degrees",
        reference_frame="MOON_ME_DE421",
        elevation_m=0.0,
        coordinate_interpretation=FRAME_INTERPRETATION,
        source_url=COORDINATE_SOURCE,
        source_coordinate_text="84°12′5.61″ S, 60°41′59.61″ E",
    ),
    Site(
        site_id="DM1-1121",
        name="Amundsen Rim — published point 1121",
        latitude_deg=-84.191841666667,
        longitude_deg=67.229041666667,
        latitude_convention="planetocentric",
        longitude_convention="signed east-positive degrees",
        reference_frame="MOON_ME_DE421",
        elevation_m=0.0,
        coordinate_interpretation=FRAME_INTERPRETATION,
        source_url=COORDINATE_SOURCE,
        source_coordinate_text="84°11′30.63″ S, 67°13′44.55″ E",
    ),
    Site(
        site_id="SITE07-1223",
        name="Peak Near Shackleton — published point 1223",
        latitude_deg=-89.005061111111,
        longitude_deg=125.309302777778,
        latitude_convention="planetocentric",
        longitude_convention="signed east-positive degrees",
        reference_frame="MOON_ME_DE421",
        elevation_m=0.0,
        coordinate_interpretation=FRAME_INTERPRETATION,
        source_url=COORDINATE_SOURCE,
        source_coordinate_text="89°0′18.22″ S, 125°18′33.49″ E",
    ),
)


def get_site_list() -> tuple[Site, ...]:
    """Return immutable, source-traceable candidate comparison points."""
    return CANDIDATE_SITES


def get_site_by_id(site_id: str) -> Site:
    for site in CANDIDATE_SITES:
        if site.site_id == site_id:
            return site
    raise KeyError(f"Unknown site ID: {site_id}")
