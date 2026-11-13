# Ashura’s Light

**A small lunar-geometry MVP for comparing geometric Sun- and Earth-center elevation at published Artemis candidate-region points.**

Ashura’s Light is a Streamlit demonstration built with Python and Skyfield. Choose two or more points and a UTC date range to calculate and compare hourly elevation profiles above a smooth local horizon.

> **Interpretation matters:** the source study does not identify the coordinate reference frame for its published points. This MVP provisionally treats the coordinates as planetocentric in `MOON_ME_DE421`. That assumption is disclosed in the app, but has not been confirmed by the source. Results are not location-verified for mission planning.

## What it does

- Calculates geometric topocentric directions to the **centers** of the Sun and Earth.
- Shows their elevations and azimuths for selected published candidate-region points.
- Uses the lunar `MOON_ME_DE421` body-fixed frame and a spherical reference surface.
- Samples every hour in UTC for inclusive whole-day date ranges.
- Uses explicitly provisioned, SHA-256-verified NASA/JPL NAIF kernels.

The observer is constructed in a lunar frame; this is **not** an Earth WGS84 observer model.

## Quick start

Requires Python 3.12. Kernel provisioning needs network access to the NASA/JPL NAIF archive; running the app does not download data.

### Windows PowerShell

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.lock
python scripts/provision_kernels.py
python -m streamlit run app.py
```

### macOS or Linux

```bash
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.lock
python scripts/provision_kernels.py
python -m streamlit run app.py
```

Streamlit prints the local URL after startup. To use a different directory for the kernel manifest and files, set `ASHURASLIGHT_KERNEL_DIR` before starting the app.

## Using the app

1. Select at least two published points in the sidebar.
2. Choose the inclusive start and end dates in UTC.
3. Select **Calculate comparison** to display the Sun-center and Earth-center plots.

The supported date range is **2026-01-01 through 2049-12-31 UTC**. The app samples from 00:00 on the first date through 23:00 on the last date, at one-hour intervals. It accepts up to 30 inclusive calendar days and does not interpolate between samples.

## Sites and coordinate provenance

The site values are direct decimal conversions of coordinates published by Peña-Asensio et al. in [“Evaluating potential landing sites for the Artemis III mission using a multi-criteria decision making approach”](https://www.sciencedirect.com/science/article/pii/S0094576524006234).

| Candidate region and published point | Published coordinates | Decimal latitude, longitude used |
|---|---|---|
| DM2 — Nobile Rim 2, point 358 | 84°12′5.61″ S, 60°41′59.61″ E | `(-84.201558333333°, +60.699891666667°)` |
| DM1 — Amundsen Rim, point 1121 | 84°11′30.63″ S, 67°13′44.55″ E | `(-84.191841666667°, +67.229041666667°)` |
| Site07 — Peak Near Shackleton, point 1223 | 89°0′18.22″ S, 125°18′33.49″ E | `(-89.005061111111°, +125.309302777778°)` |

These are published points within candidate regions, **not NASA-selected touchdown coordinates**. The study publishes coordinates and hemisphere labels but does not state their reference frame in its coordinate table or full text. The implementation therefore provisionally interprets them as planetocentric coordinates in `MOON_ME_DE421`, following the [USGS lunar mapping standard](https://pubs.usgs.gov/tm/11/e1/tm11E1.pdf). The independent geometry checks validate calculations under this interpretation; they do not establish that it is the source datum.

Each point uses an elevation of `0 m` relative to the PCK-defined spherical lunar reference surface. This is a calculation convention, not a surveyed site elevation or a representation of local topography.

## Method and limitations

Skyfield evaluates the observer and target positions at the same epoch, transforms the relative direction into the lunar body-fixed frame, and projects it onto the local east/north/up basis. The reported values are geometric center elevations and azimuths, with light-time, stellar-aberration, and atmospheric-refraction corrections disabled.

This MVP does **not** calculate or claim:

- Terrain-aware visibility, terrain blockage, or LOLA-derived topography.
- Visibility of the full Sun or Earth disk, or actual surface illumination.
- Power-generation performance, communications availability, relay coverage, or link budgets.
- A validated physical lunar dust model.

The repository still contains a legacy root-level `dust_model.py` file. It is not imported or used by the app or geometry engine, has not been validated as physical, and is not part of this MVP.

## Scientific data

The required kernel names, NASA/JPL NAIF source URLs, and expected SHA-256 digests are recorded in [`data/kernels/manifest.json`](data/kernels/manifest.json). Provision the files explicitly:

```bash
python scripts/provision_kernels.py
```

The provisioner verifies each file against the manifest and refuses to replace a mismatched existing file. The application also verifies kernel hashes before calculation. Kernel binaries are local data and are excluded from Git; they must be provisioned in a fresh environment.

## Tests and verification

After provisioning the kernels, install the test dependency and run the suite:

```bash
python -m pip install -r requirements-dev.txt
python -m pytest -q
```

Tests cover UTC sampling and input bounds, lunar-frame geometry, kernel integrity, fixed-epoch comparisons against independently generated NAIF CSPICE reference values, and Streamlit behavior. CSPICE is used only to document and validate reference values; it is not an application dependency. See [`docs/reference-validation.md`](docs/reference-validation.md) for the epoch, values, and reference setup.

## Project notes

- [`docs/technical-decisions.md`](docs/technical-decisions.md) — frames, conventions, kernel sources, and limitations.
- [`docs/implementation-report.md`](docs/implementation-report.md) — implementation history and verification notes.
- [`docs/reference-validation.md`](docs/reference-validation.md) — independent fixed-epoch geometry reference.
