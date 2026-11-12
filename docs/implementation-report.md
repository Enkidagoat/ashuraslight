# Ashura’s Light — bounded implementation report

**Date:** 2026-11-11  
**Base revision:** `7d26a3e849f4b14dd8d77ee8baf3459d20cd493e` (`origin/main` at start)  
**Branch:** `feature/verified-lunar-geometry`  
**Final repository state:** changes remain uncommitted on the dedicated branch; no commit or push was made. The NAIF kernel binaries are local, Git-ignored test assets.

## Outcome

The scaffold is now a runnable Streamlit demonstration of geometric Sun-center and Earth-center elevation for three published points in candidate landing regions, with a Skyfield lunar body-fixed observer, explicit data provisioning, and a reproducible test setup. It deliberately excludes terrain processing, dust, power, communication-link modeling, and interpolation.

**Verdict: CONDITIONAL GO.** The computational implementation and software acceptance tests passed. However, the candidate-site paper does not state the source coordinate reference frame in its point table or full text. The app therefore labels its `MOON_ME_DE421` interpretation as provisional. The demo may be shown with that caveat; do not claim point-level absolute-location accuracy or use the plotted site values for mission planning until the source datum is confirmed or authoritatively transformed.

## Repository and files changed

The initial working tree was clean at base revision `7d26a3e`, and the remote `main` ref matched that revision when implementation began. Changes are confined to `feature/verified-lunar-geometry` and have not been committed or pushed.

- Replaced `ephemeris.py` with a Skyfield-only lunar geometry engine, pinned-kernel integrity checks, explicit UTC sampling, and local east/north/up projection.
- Replaced approximate placeholders in `sites.py` with three source-published candidate-region points and per-record coordinate interpretation/provenance.
- Rebuilt `app.py` as a minimal multi-site UI with Sun and Earth comparison plots, horizon references, date controls, caveats, and actionable errors.
- Removed the unused `dust_model.py` scaffold and its UI controls.
- Added explicit NAIF kernel manifest/provisioning and excluded binary kernels from Git.
- Pinned direct dependencies and a full Python 3.12 runtime lock; added a separate test dependency file.
- Updated `README.md`; added `docs/technical-decisions.md`, `docs/reference-validation.md`, and this report.
- Added geometry, data-integrity, sampling, independent-reference, endpoint, and Streamlit `AppTest` coverage.

## Technical decisions

The application uses Python 3.12, Skyfield 1.55, Streamlit 1.67.0, Plotly 7.1.0, and NumPy 2.4.2. Runtime direct dependencies are in `requirements.txt`; the fully resolved runtime set is in `requirements.lock`. SpiceyPy is not an application dependency.

Calculations use `MOON_ME_DE421` and planetocentric latitude with signed east-positive longitude. The surface uses the PCK-defined spherical lunar reference radius and `elevation_m=0.0`; this is a reference-surface assumption, not terrain elevation. Results are geometric same-epoch topocentric directions to the Sun and Earth centers, with atmospheric refraction, light-time, and stellar-aberration corrections disabled. Azimuth is clockwise from local north. Sampling is hourly in UTC, inclusive of every whole calendar day from 00:00 through 23:00, capped at 30 inclusive days. The supported UI date range is 2026-01-01 through 2049-12-31 UTC.

The plot does not report interpolated horizon-duration metrics. While tests compare hourly and ten-minute crossing estimates on two fixed cases, these limited fixtures do not justify presenting a general mission-relevant duty-cycle metric.

## Site data and provenance

All coordinates below are directly converted from the published DMS values in Peña-Asensio et al., “Evaluating potential landing sites for the Artemis III mission using a multi-criteria decision making approach” ([ScienceDirect article](https://www.sciencedirect.com/science/article/pii/S0094576524006234)). The points are not NASA-selected touchdown coordinates.

| Candidate region / point | Source coordinates | Decimal latitude, longitude used |
|---|---|---|
| DM2 — Nobile Rim 2, point 358 | 84°12′5.61″ S, 60°41′59.61″ E | `(-84.201558333333°, +60.699891666667°)` |
| DM1 — Amundsen Rim, point 1121 | 84°11′30.63″ S, 67°13′44.55″ E | `(-84.191841666667°, +67.229041666667°)` |
| Site07 — Peak Near Shackleton, point 1223 | 89°0′18.22″ S, 125°18′33.49″ E | `(-89.005061111111°, +125.309302777778°)` |

The published point table supplies hemispheres and coordinates but not a stated coordinate frame or latitude type. The implementation provisionally treats them as planetocentric in the USGS-recommended DE421 Mean Earth standard; this assumption is disclosed in the UI and source records. The reference test validates the calculation under this assignment, not the assignment itself. Resolve this data-provenance gate before any unqualified geographic claim.

## NAIF kernel sources and hashes

The kernels were explicitly downloaded from the listed NASA/JPL NAIF sources, SHA-256 checked, loaded successfully in the fresh test environment, and rechecked by rerunning the provisioner. Binary kernels are present locally under `data/kernels/` but are ignored by Git; only the manifest is tracked.

| Asset | URL | SHA-256 | Recorded coverage/version |
|---|---|---|---|
| `de421.bsp` | [NAIF archived DE421](https://naif.jpl.nasa.gov/pub/naif/generic_kernels/spk/planets/a_old_versions/de421.bsp) | `08b20db2ae22488650641c5a9033e5bfda4b1c4b440cfeaf20f621cfa18ecdb3` | DE421, 1900–2050 |
| `moon_080317.tf` | [NAIF lunar frame kernel](https://naif.jpl.nasa.gov/pub/naif/generic_kernels/fk/satellites/moon_080317.tf) | `78732477b96f9863e7b0d65bcee3c22b8707ca5ed0db56d1173319cb2e8c7993` | Created 2008-03-17; revised 2008-03-21 |
| `pck00011.tpc` | [NAIF text PCK](https://naif.jpl.nasa.gov/pub/naif/generic_kernels/pck/pck00011.tpc) | `3dff7b1dbeceaa01f25467767d3fa25816051c85d162d1edf04acb310ee28bb1` | Dated 2022-12-27 |
| `moon_pa_de421_1900-2050.bpc` | [NAIF DE421 lunar orientation PCK](https://naif.jpl.nasa.gov/pub/naif/generic_kernels/pck/moon_pa_de421_1900-2050.bpc) | `656f90616403d75a75f0cd6c8830fc5b44f8cb4facb5ccb8915e752b397520cf` | DE421 lunar orientation, 1900–2050 |

The explicit provisioning command is `python scripts/provision_kernels.py`. The application does not download scientific assets at import or run time and rejects missing or mismatched data.

## Independent fixed-epoch comparisons

At 2026-12-01 00:00:00 UTC, Skyfield output was compared to separately generated NAIF CSPICE N0067 geometric reference values. The independent calculation used the same hashed four scientific kernels, `naif0012.tls` only for UTC parsing, SPICE `spkpos(..., "NONE", ...)`, the PCK radius of 1737.4 km, and a separate ENU projection. CSPICE was used only in the validation environment; it is not mixed into the application. Declared tolerance: `1e-6°` for elevation and azimuth.

| Point | Sun elevation / azimuth (°) | Earth elevation / azimuth (°) |
|---|---|---|
| DM2 / Nobile Rim 2 point 358 | `-3.0124595422 / 219.4192341214` | `+1.7962960425 / 305.9405277314` |
| DM1 / Amundsen Rim point 1121 | `-3.4095917613 / 212.8939134968` | `+1.2461286656 / 299.4334054708` |
| Site07 / Peak Near Shackleton point 1223 | `+0.5701006426 / 154.7678472202` | `-2.0868289308 / 241.3845697528` |

Full reference values and the exact method are in `docs/reference-validation.md`.

## Acceptance tests and executed evidence

The suite was run from a clean Python 3.12 virtual environment after installing the pinned lock and explicitly provisioning the kernels:

```bash
python3.12 -m venv /tmp/ashura-final-venv
/tmp/ashura-final-venv/bin/python -m pip install -r requirements-dev.txt
/tmp/ashura-final-venv/bin/python -m pytest -q
```

**Result: `18 passed`** (`18 passed in 1.56s` in the final run). No warning was emitted in that run.

| Gate | Result | Executed evidence |
|---|---|---|
| Lunar observer construction | PASS | Constructed a surface observer and verified its body-fixed radius equals 1737.4 km within `1e-6 km`. |
| Local frame and coordinate orientation | PASS | Cardinal synthetic vectors produced expected altitude signs and azimuths; DE421 frame rotation passed an orthonormality check. |
| Sun geometry | PASS | Three fixed-epoch Sun elevations/azimuths matched the independent CSPICE oracle within `1e-6°`. |
| Earth geometry | PASS | Three fixed-epoch Earth-center elevations/azimuths matched the independent CSPICE oracle within `1e-6°`. |
| Time sampling and coverage | PASS | Repeated UTC grids are identical; cadence, inclusive endpoints, 720-sample cap, invalid ranges, and first/final supported epochs were tested. |
| Horizon crossings / cadence sensitivity | PASS | Hourly and ten-minute estimates on fixed Earth and Sun crossing cases differed by less than `0.01 h`; no generalized metric is exposed in the UI. |
| Multi-site comparison | PASS | Three sites produced equal-length series on identical epochs; AppTest changed the selected site pair and rendered both plots. |
| Inputs, data integrity, and errors | PASS | Invalid coordinates/ranges, missing manifest, and hash mismatch were rejected; AppTest showed missing-data and insufficient-selection errors without crashing. |
| UI behavior | PASS | Streamlit AppTest submitted a valid comparison and found exactly two Plotly charts, then exercised selection and error cases. |
| Reproducibility / runtime | PASS | Clean Python 3.12 environment installed from `requirements-dev.txt`; `pip check` reported no broken requirements; compileall and `git diff --check` succeeded. Provisioner rerun confirmed all four hashes. Local Streamlit HTTP health endpoint returned `ok`. |

## Remaining limitations and blockers

1. **Coordinate datum confirmation is still required.** The source paper does not identify its point coordinates as DE421 ME or explicitly identify latitude as planetocentric. Obtain a source-author confirmation or authoritative geospatial product and, if necessary, perform a documented transformation. Until then, keep the provisional label visible and do not claim absolute point-location verification.
2. **No terrain-aware visibility.** The smooth horizon can overstate Sun/Earth center visibility at ridge or crater locations.
3. **Centers, not disks.** A center below zero does not mean the complete disk is hidden; center elevation is not full illumination or communication performance.
4. **Future time conversion.** Leap seconds after the bundled Skyfield table are unknowable in advance; future UTC-to-TDB conversion is not sub-second accurate.
5. **No dust, LOLA, power, or link-budget outputs.** These remain excluded by scope.

## Final decision

**CONDITIONAL GO — demonstrable geometric MVP only.** The code, data provisioning, and computational/software acceptance tests pass, and the interface states its limitations. The outstanding datum ambiguity is material to whether the points correspond to their true absolute lunar locations in the chosen frame; resolving it is a prerequisite for a final scientific GO or any mission-planning interpretation.
