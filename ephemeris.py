"""Geometric lunar surface pointing calculations using Skyfield and pinned kernels."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, time, timedelta, timezone
import hashlib
import json
import math
from pathlib import Path
from typing import Iterable

import numpy as np
from skyfield.api import PlanetaryConstants, load

from sites import Site

MIN_SUPPORTED_DATE = date(2026, 1, 1)
MAX_SUPPORTED_DATE = date(2049, 12, 31)
SAMPLE_INTERVAL_HOURS = 1
MAX_INCLUSIVE_DAYS = 30
MAX_SAMPLES = MAX_INCLUSIVE_DAYS * 24
FRAME_NAME = "MOON_ME_DE421"


class EphemerisDataError(RuntimeError):
    """Raised when required local ephemeris assets are missing or invalid."""


class GeometryInputError(ValueError):
    """Raised for invalid geometry or sampling inputs."""


@dataclass(frozen=True)
class SiteSeries:
    site: Site
    timestamps_utc: tuple[datetime, ...]
    sun_elevation_deg: tuple[float, ...]
    sun_azimuth_deg: tuple[float, ...]
    earth_elevation_deg: tuple[float, ...]
    earth_azimuth_deg: tuple[float, ...]


def build_hourly_utc_grid(start_date: date, end_date: date) -> tuple[datetime, ...]:
    """Return hourly UTC samples over inclusive whole calendar days, 00:00–23:00."""
    if isinstance(start_date, datetime) or not isinstance(start_date, date):
        raise GeometryInputError("Start date must be a calendar date (UTC).")
    if isinstance(end_date, datetime) or not isinstance(end_date, date):
        raise GeometryInputError("End date must be a calendar date (UTC).")
    if start_date < MIN_SUPPORTED_DATE or end_date > MAX_SUPPORTED_DATE:
        raise GeometryInputError(
            f"Supported dates are {MIN_SUPPORTED_DATE.isoformat()} through "
            f"{MAX_SUPPORTED_DATE.isoformat()} UTC."
        )
    if end_date < start_date:
        raise GeometryInputError("End date must be on or after start date.")
    inclusive_days = (end_date - start_date).days + 1
    if inclusive_days > MAX_INCLUSIVE_DAYS:
        raise GeometryInputError(
            f"Choose no more than {MAX_INCLUSIVE_DAYS} inclusive UTC calendar days."
        )
    count = inclusive_days * 24
    if count > MAX_SAMPLES:
        raise GeometryInputError(f"The request exceeds the {MAX_SAMPLES}-sample limit.")
    first = datetime.combine(start_date, time.min, tzinfo=timezone.utc)
    return tuple(first + timedelta(hours=i) for i in range(count))


def local_altaz_from_body_fixed_vector(
    vector_body_fixed_km: Iterable[float], latitude_deg: float, longitude_deg: float
) -> tuple[float, float]:
    """Project a body-fixed topocentric vector onto the spherical local ENU basis.

    Latitude is planetocentric; longitude is signed, east-positive. The returned
    altitude is geometric and azimuth is clockwise from local north.
    """
    vector = np.asarray(tuple(vector_body_fixed_km), dtype=float)
    if vector.shape != (3,) or not np.all(np.isfinite(vector)):
        raise GeometryInputError("Topocentric vector must contain three finite values.")
    if not math.isfinite(latitude_deg) or not -90.0 <= latitude_deg <= 90.0:
        raise GeometryInputError("Latitude must be finite and between -90 and 90 degrees.")
    if not math.isfinite(longitude_deg) or not -180.0 <= longitude_deg <= 180.0:
        raise GeometryInputError("Longitude must be finite and between -180 and 180 degrees.")
    if np.linalg.norm(vector) == 0.0:
        raise GeometryInputError("Topocentric vector cannot be zero length.")

    lat = math.radians(latitude_deg)
    lon = math.radians(longitude_deg)
    east = np.array((-math.sin(lon), math.cos(lon), 0.0))
    north = np.array(
        (-math.sin(lat) * math.cos(lon), -math.sin(lat) * math.sin(lon), math.cos(lat))
    )
    up = np.array(
        (math.cos(lat) * math.cos(lon), math.cos(lat) * math.sin(lon), math.sin(lat))
    )
    e = float(np.dot(vector, east))
    n = float(np.dot(vector, north))
    u = float(np.dot(vector, up))
    altitude = math.degrees(math.atan2(u, math.hypot(e, n)))
    azimuth = math.degrees(math.atan2(e, n)) % 360.0
    return altitude, azimuth


def verify_kernel_files(data_dir: str | Path) -> dict[str, Path]:
    """Validate required local files against the checked-in SHA-256 manifest."""
    root = Path(data_dir)
    manifest_path = root / "manifest.json"
    if not manifest_path.is_file():
        raise EphemerisDataError(
            f"Kernel manifest is missing: {manifest_path}. Run "
            "`python scripts/provision_kernels.py` from the project root."
        )
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        entries = manifest["kernels"]
    except (OSError, json.JSONDecodeError, KeyError, TypeError) as exc:
        raise EphemerisDataError(f"Invalid kernel manifest: {manifest_path}") from exc

    verified: dict[str, Path] = {}
    for entry in entries:
        filename = entry["filename"]
        path = root / filename
        expected = entry["sha256"].lower()
        if not path.is_file():
            raise EphemerisDataError(
                f"Required data file is missing: {path}. Run "
                "`python scripts/provision_kernels.py` from the project root."
            )
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        if digest != expected:
            raise EphemerisDataError(
                f"SHA-256 mismatch for {path.name}: expected {expected}, got {digest}. "
                "Do not use or silently replace this file."
            )
        verified[filename] = path
    required = {"de421.bsp", "moon_080317.tf", "pck00011.tpc", "moon_pa_de421_1900-2050.bpc"}
    if set(verified) != required:
        raise EphemerisDataError("Kernel manifest does not contain the required fixed asset set.")
    return verified


class LunarGeometry:
    """Skyfield geometry engine. Instantiate only after explicit data provisioning."""

    def __init__(self, data_dir: str | Path):
        files = verify_kernel_files(data_dir)
        self._kernel_handles = []
        try:
            self.constants = PlanetaryConstants()
            for filename in ("moon_080317.tf", "pck00011.tpc"):
                handle = files[filename].open("rb")
                self._kernel_handles.append(handle)
                self.constants.read_text(handle)
            binary = files["moon_pa_de421_1900-2050.bpc"].open("rb")
            self._kernel_handles.append(binary)
            self.constants.read_binary(binary)
            self.frame = self.constants.build_frame_named(FRAME_NAME)
            self.ephemeris = load(str(files["de421.bsp"]))
            self.timescale = load.timescale(builtin=True)
            self.moon = self.ephemeris["moon"]
            self.targets = {"sun": self.ephemeris["sun"], "earth": self.ephemeris["earth"]}
        except Exception as exc:
            self.close()
            if isinstance(exc, EphemerisDataError):
                raise
            raise EphemerisDataError(
                "Skyfield could not load the pinned DE421 lunar geometry files. "
                "Check the data manifest and file integrity."
            ) from exc

    def close(self) -> None:
        for handle in getattr(self, "_kernel_handles", []):
            try:
                handle.close()
            except OSError:
                pass
        self._kernel_handles = []

    def calculate_site(self, site: Site, timestamps_utc: tuple[datetime, ...]) -> SiteSeries:
        if not isinstance(site, Site):
            raise GeometryInputError("A verified Site record is required.")
        if not timestamps_utc:
            raise GeometryInputError("At least one UTC timestamp is required.")
        for stamp in timestamps_utc:
            if stamp.tzinfo is None or stamp.utcoffset() != timedelta(0):
                raise GeometryInputError("All sample timestamps must be timezone-aware UTC.")
            if not MIN_SUPPORTED_DATE <= stamp.date() <= MAX_SUPPORTED_DATE:
                raise GeometryInputError("Sample timestamp is outside the supported date range.")

        times = self.timescale.from_datetimes(list(timestamps_utc))
        site_vector = self.constants.build_latlon_degrees(
            self.frame,
            site.latitude_deg,
            site.longitude_deg,
            elevation_m=site.elevation_m,
        )
        observer = self.moon + site_vector
        observer_position = observer.at(times).position.km
        rotation = self.frame.rotation_at(times)
        latitude, longitude = site.latitude_deg, site.longitude_deg
        lat_rad, lon_rad = math.radians(latitude), math.radians(longitude)
        east = np.array((-math.sin(lon_rad), math.cos(lon_rad), 0.0))
        north = np.array(
            (-math.sin(lat_rad) * math.cos(lon_rad), -math.sin(lat_rad) * math.sin(lon_rad), math.cos(lat_rad))
        )
        up = np.array(
            (math.cos(lat_rad) * math.cos(lon_rad), math.cos(lat_rad) * math.sin(lon_rad), math.sin(lat_rad))
        )

        calculated: dict[str, tuple[tuple[float, ...], tuple[float, ...]]] = {}
        for key, target in self.targets.items():
            target_position = target.at(times).position.km
            relative_inertial = target_position - observer_position
            relative_body_fixed = np.einsum("ijt,jt->it", rotation, relative_inertial)
            e = np.einsum("i,it->t", east, relative_body_fixed)
            n = np.einsum("i,it->t", north, relative_body_fixed)
            u = np.einsum("i,it->t", up, relative_body_fixed)
            elevation = np.degrees(np.arctan2(u, np.hypot(e, n)))
            azimuth = np.mod(np.degrees(np.arctan2(e, n)), 360.0)
            if not np.all(np.isfinite(elevation)) or not np.all(np.isfinite(azimuth)):
                raise EphemerisDataError(f"Non-finite {key} geometry returned by Skyfield.")
            if np.any(elevation < -90.0) or np.any(elevation > 90.0):
                raise EphemerisDataError(f"{key.capitalize()} elevation fell outside physical angular bounds.")
            calculated[key] = (
                tuple(float(x) for x in elevation),
                tuple(float(x) for x in azimuth),
            )

        return SiteSeries(
            site=site,
            timestamps_utc=timestamps_utc,
            sun_elevation_deg=calculated["sun"][0],
            sun_azimuth_deg=calculated["sun"][1],
            earth_elevation_deg=calculated["earth"][0],
            earth_azimuth_deg=calculated["earth"][1],
        )
