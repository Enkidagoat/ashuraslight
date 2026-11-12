# Ashura’s Light

A minimal Streamlit comparison of **geometric lunar Sun-center and Earth-center elevation** for three published candidate-region points. The app uses Python, Streamlit, and Skyfield. It does not process terrain or model lunar dust.

## Setup and explicit data provisioning

Requires Python 3.12 and network access only for the one-time, explicit kernel provisioning step. The application does not download scientific data when it is imported or run.

```bash
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.lock
python scripts/provision_kernels.py
python -m streamlit run app.py
```

The provisioner retrieves four named files from NASA/JPL NAIF URLs in [`data/kernels/manifest.json`](data/kernels/manifest.json). It checks each SHA-256 digest, refuses to overwrite mismatched local files, and stops on a hash mismatch. Kernel binaries are excluded from Git; provide them explicitly in a fresh environment with the command above. The app independently checks the manifest hashes before use. Set `ASHURASLIGHT_KERNEL_DIR` to use a different local directory containing the manifest and pinned files.

## Sites and coordinate source

The app includes three published comparison points from Peña-Asensio et al., *Evaluating potential landing sites for the Artemis III mission using a multi-criteria decision making approach*:

- **DM2 — Nobile Rim 2, point 358:** 84°12′5.61″ S, 60°41′59.61″ E; decimal `(-84.201558333333, 60.699891666667)`.
- **DM1 — Amundsen Rim, point 1121:** 84°11′30.63″ S, 67°13′44.55″ E; decimal `(-84.191841666667, 67.229041666667)`.
- **Site07 — Peak Near Shackleton, point 1223:** 89°0′18.22″ S, 125°18′33.49″ E; decimal `(-89.005061111111, 125.309302777778)`.

These are published points within candidate regions, **not NASA-selected touchdown coordinates**. The study publishes the coordinate values and S/E hemisphere labels, but does not state a reference frame in its coordinate table/full text. The MVP provisionally interprets them as planetocentric coordinates in the `MOON_ME_DE421` Mean Earth frame, following the USGS lunar-mapping standard. This is disclosed in the UI and in `docs/technical-decisions.md`; confirmation of the source datum is still required before claiming point-level absolute-location accuracy. Each point uses `0 m` relative to the spherical reference surface as an explicit calculation assumption; this is not a surveyed surface elevation.

## Scientific method and limitations

Skyfield loads JPL DE421 and the compatible lunar frame/orientation/constant files specified in the manifest. A lunar body-fixed surface observer is constructed in `MOON_ME_DE421`. At each epoch, target and observer positions are evaluated at the same time and transformed into the lunar body-fixed frame, then projected onto the local east/north/up basis. This is a geometric, topocentric center-direction calculation with no light-time or stellar-aberration correction and no atmospheric refraction.

Date inputs are inclusive whole UTC days. The fixed cadence is one sample per UTC hour, from 00:00 on the start date through 23:00 on the end date, with a maximum of 30 inclusive days and no interpolation. Supported date inputs are 2026-01-01 through 2049-12-31 UTC, within the pinned DE421/PCK coverage. Future leap seconds cannot be predicted; future UTC-to-TDB conversion is not represented as sub-second accurate.

**Important limitations:**

- Elevations refer to the centers of the Sun and Earth above a smooth local tangent horizon. Local terrain blockage is not modeled.
- The Sun-center elevation does not model the solar disk or actual surface illumination and is not a power-generation estimate.
- Earth-center elevation above zero does not guarantee communication availability. There is no link budget, terrain occultation, or relay-network model.
- No lunar dust model, mitigation control, LOLA processing, or power-system simulation is included.

## Verification

Install test tools and run the suite after provisioning kernels:

```bash
python -m pip install -r requirements-dev.txt
python -m pytest -q
```

The suite includes local-frame orientation/synthetic-vector tests, deterministic UTC sampling and input validation, file-integrity checks, fixed-epoch geometry comparisons, date-boundary coverage, multi-site timestamp alignment, and Streamlit `AppTest` behavior. The fixed-epoch values in the tests were independently generated with NAIF CSPICE N0067 using the same hashed scientific kernels; CSPICE is not an application dependency. Exact oracle values, epoch, and reference configuration are documented in `docs/reference-validation.md`. The oracle validates geometry under the selected frame interpretation, not the candidate paper’s unstated coordinate datum.

## Technical decisions

See [`docs/technical-decisions.md`](docs/technical-decisions.md) for the fixed frame, coordinate conventions, kernel sources/hashes, supported dates, sampling and calculation conventions.
