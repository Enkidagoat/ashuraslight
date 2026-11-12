from __future__ import annotations

from datetime import date, datetime, timedelta, timezone
import json
from pathlib import Path

import numpy as np
import pytest

from ephemeris import (
    EphemerisDataError,
    GeometryInputError,
    LunarGeometry,
    build_hourly_utc_grid,
    local_altaz_from_body_fixed_vector,
    verify_kernel_files,
)
from sites import CANDIDATE_SITES, get_site_by_id

ROOT = Path(__file__).resolve().parents[1]
KERNEL_DIR = ROOT / "data" / "kernels"
SPICE_REFERENCE = {
    "DM2-358": {
        "sun": (-3.012459542225528, 219.41923412141995),
        "earth": (1.7962960425281513, 305.94052773137696),
    },
    "DM1-1121": {
        "sun": (-3.4095917612616016, 212.89391349445208),
        "earth": (1.246128665641467, 299.4334054707526),
    },
    "SITE07-1223": {
        "sun": (0.5701006426223459, 154.76784722017246),
        "earth": (-2.086828930833153, 241.38456975275744),
    },
}


@pytest.fixture(scope="module")
def geometry() -> LunarGeometry:
    instance = LunarGeometry(KERNEL_DIR)
    yield instance
    instance.close()


def test_hourly_grid_is_inclusive_utc_and_deterministic() -> None:
    stamps = build_hourly_utc_grid(date(2026, 12, 1), date(2026, 12, 2))
    assert len(stamps) == 48
    assert stamps[0] == datetime(2026, 12, 1, 0, tzinfo=timezone.utc)
    assert stamps[-1] == datetime(2026, 12, 2, 23, tzinfo=timezone.utc)
    assert all(stamp.utcoffset() == timedelta(0) for stamp in stamps)
    assert all(b - a == timedelta(hours=1) for a, b in zip(stamps, stamps[1:]))
    assert stamps == build_hourly_utc_grid(date(2026, 12, 1), date(2026, 12, 2))


def test_hourly_grid_enforces_supported_range_and_sample_limit() -> None:
    assert len(build_hourly_utc_grid(date(2026, 1, 1), date(2026, 1, 30))) == 720
    with pytest.raises(GeometryInputError):
        build_hourly_utc_grid(date(2025, 12, 31), date(2026, 1, 1))
    with pytest.raises(GeometryInputError):
        build_hourly_utc_grid(date(2026, 1, 1), date(2050, 1, 1))
    with pytest.raises(GeometryInputError):
        build_hourly_utc_grid(date(2026, 1, 2), date(2026, 1, 1))
    with pytest.raises(GeometryInputError):
        build_hourly_utc_grid(date(2026, 1, 1), date(2026, 1, 31))


def test_local_horizon_projection_synthetic_cardinal_directions() -> None:
    cases = [
        ((1, 0, 0), 90.0, 0.0),   # up at lat=0, lon=0
        ((-1, 0, 0), -90.0, 0.0), # down
        ((0, 1, 0), 0.0, 90.0),   # east
        ((0, 0, 1), 0.0, 0.0),    # north
        ((0, -1, 0), 0.0, 270.0), # west
        ((0, 0, -1), 0.0, 180.0), # south
    ]
    for vector, expected_alt, expected_az in cases:
        altitude, azimuth = local_altaz_from_body_fixed_vector(vector, 0.0, 0.0)
        assert altitude == pytest.approx(expected_alt, abs=1e-12)
        assert azimuth == pytest.approx(expected_az, abs=1e-12)


def test_local_horizon_rejects_invalid_vectors_and_coordinates() -> None:
    with pytest.raises(GeometryInputError):
        local_altaz_from_body_fixed_vector((0, 0, 0), 0.0, 0.0)
    with pytest.raises(GeometryInputError):
        local_altaz_from_body_fixed_vector((1, 2), 0.0, 0.0)
    with pytest.raises(GeometryInputError):
        local_altaz_from_body_fixed_vector((1, 0, 0), 91.0, 0.0)
    with pytest.raises(GeometryInputError):
        local_altaz_from_body_fixed_vector((1, 0, 0), 0.0, 181.0)


def test_site_catalogue_is_source_traceable_and_in_expected_convention() -> None:
    assert len(CANDIDATE_SITES) == 3
    dm2 = get_site_by_id("DM2-358")
    dm1 = get_site_by_id("DM1-1121")
    site07 = get_site_by_id("SITE07-1223")
    assert (dm2.latitude_deg, dm2.longitude_deg) == pytest.approx(
        (-84.201558333333, 60.699891666667), abs=1e-12
    )
    assert (dm1.latitude_deg, dm1.longitude_deg) == pytest.approx(
        (-84.191841666667, 67.229041666667), abs=1e-12
    )
    assert (site07.latitude_deg, site07.longitude_deg) == pytest.approx(
        (-89.005061111111, 125.309302777778), abs=1e-12
    )
    for site in CANDIDATE_SITES:
        assert site.latitude_convention == "planetocentric"
        assert site.longitude_convention == "signed east-positive degrees"
        assert site.reference_frame == "MOON_ME_DE421"
        assert site.source_coordinate_text
        assert site.coordinate_interpretation
        assert site.elevation_m == 0.0


def test_kernel_integrity_manifest_and_missing_data(tmp_path: Path) -> None:
    with pytest.raises(EphemerisDataError, match="manifest is missing"):
        verify_kernel_files(tmp_path)

    manifest = json.loads((KERNEL_DIR / "manifest.json").read_text(encoding="utf-8"))
    (tmp_path / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
    (tmp_path / "de421.bsp").write_bytes(b"not a kernel")
    with pytest.raises(EphemerisDataError, match="SHA-256 mismatch"):
        verify_kernel_files(tmp_path)


def test_kernel_files_verify_and_frame_is_orthonormal(geometry: LunarGeometry) -> None:
    verified = verify_kernel_files(KERNEL_DIR)
    assert set(verified) == {
        "de421.bsp",
        "moon_080317.tf",
        "pck00011.tpc",
        "moon_pa_de421_1900-2050.bpc",
    }
    t = geometry.timescale.utc(2026, 12, 1)
    rotation = geometry.frame.rotation_at(t)
    np.testing.assert_allclose(rotation @ rotation.T, np.eye(3), atol=1e-12)


def test_lunar_surface_observer_is_on_pck_reference_radius(geometry: LunarGeometry) -> None:
    site = get_site_by_id("DM2-358")
    body_fixed = geometry.constants.build_latlon_degrees(
        geometry.frame, site.latitude_deg, site.longitude_deg, elevation_m=site.elevation_m
    )
    observer = geometry.moon + body_fixed
    t = geometry.timescale.utc(2026, 12, 1)
    offset_inertial = observer.at(t).position.km - geometry.moon.at(t).position.km
    offset_body_fixed = geometry.frame.rotation_at(t) @ offset_inertial
    assert np.linalg.norm(offset_body_fixed) == pytest.approx(1737.4, abs=1e-6)


@pytest.mark.parametrize("site_id", ["DM2-358", "DM1-1121", "SITE07-1223"])
def test_fixed_epoch_matches_independent_cspice_reference(
    geometry: LunarGeometry, site_id: str
) -> None:
    site = get_site_by_id(site_id)
    stamps = (datetime(2026, 12, 1, 0, tzinfo=timezone.utc),)
    result = geometry.calculate_site(site, stamps)
    expected = SPICE_REFERENCE[site_id]
    assert result.sun_elevation_deg[0] == pytest.approx(expected["sun"][0], abs=1e-6)
    assert result.sun_azimuth_deg[0] == pytest.approx(expected["sun"][1], abs=1e-6)
    assert result.earth_elevation_deg[0] == pytest.approx(expected["earth"][0], abs=1e-6)
    assert result.earth_azimuth_deg[0] == pytest.approx(expected["earth"][1], abs=1e-6)
    assert -90.0 <= result.sun_elevation_deg[0] <= 90.0
    assert -90.0 <= result.earth_elevation_deg[0] <= 90.0
    assert 0.0 <= result.sun_azimuth_deg[0] < 360.0
    assert 0.0 <= result.earth_azimuth_deg[0] < 360.0


def test_multi_site_results_use_identical_hourly_epochs(geometry: LunarGeometry) -> None:
    stamps = build_hourly_utc_grid(date(2026, 12, 1), date(2026, 12, 2))
    results = [geometry.calculate_site(site, stamps) for site in CANDIDATE_SITES]
    assert len(results) == 3
    assert all(result.timestamps_utc == stamps for result in results)
    assert len(results[0].sun_elevation_deg) == len(results[1].earth_elevation_deg) == 48
    assert all(np.isfinite(results[0].sun_elevation_deg))
    assert all(np.isfinite(results[1].earth_elevation_deg))


def test_calculation_within_first_and_last_supported_file_epochs(geometry: LunarGeometry) -> None:
    site = get_site_by_id("DM2-358")
    endpoints = (
        datetime(2026, 1, 1, 0, tzinfo=timezone.utc),
        datetime(2049, 12, 31, 23, tzinfo=timezone.utc),
    )
    for stamp in endpoints:
        result = geometry.calculate_site(site, (stamp,))
        assert np.isfinite(result.sun_elevation_deg[0])
        assert np.isfinite(result.earth_elevation_deg[0])


def _linear_positive_duration_hours(values: tuple[float, ...], step_hours: float) -> float:
    duration = 0.0
    for first, second in zip(values, values[1:]):
        if first >= 0.0 and second >= 0.0:
            duration += step_hours
        elif first < 0.0 <= second:
            duration += step_hours * second / (second - first)
        elif first >= 0.0 > second:
            duration += step_hours * first / (first - second)
    return duration


def test_horizon_crossings_and_hourly_sampling_sensitivity(geometry: LunarGeometry) -> None:
    site = get_site_by_id("DM2-358")
    cases = (
        (date(2026, 12, 2), "earth_elevation_deg"),
        (date(2026, 12, 10), "sun_elevation_deg"),
    )
    for day, attribute in cases:
        start = datetime(day.year, day.month, day.day, tzinfo=timezone.utc)
        hourly = build_hourly_utc_grid(day, day)
        ten_minute = tuple(start + timedelta(minutes=10 * i) for i in range(139))
        coarse_values = getattr(geometry.calculate_site(site, hourly), attribute)
        fine_values = getattr(geometry.calculate_site(site, ten_minute), attribute)

        def crosses_horizon(values: tuple[float, ...]) -> bool:
            return any(
                (first < 0.0 <= second) or (first >= 0.0 > second)
                for first, second in zip(values, values[1:])
            )

        assert crosses_horizon(coarse_values)
        assert crosses_horizon(fine_values)
        coarse_hours = _linear_positive_duration_hours(coarse_values, 1.0)
        fine_hours = _linear_positive_duration_hours(fine_values, 1.0 / 6.0)
        assert abs(coarse_hours - fine_hours) < 0.01  # 36 seconds over this fixture
