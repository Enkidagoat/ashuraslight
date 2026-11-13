# Ashura’s Light — current architecture

**Reviewed implementation baseline:** `ee74fa520e0c45bc664bffa2ae9ea439f05c1ebc`  
**Review date:** 2026-11-13  
**Scope:** describes the code observed at the baseline above. This is not a future-state design.

## System summary

Ashura’s Light is a Python 3.12 / Streamlit demonstration. Its current user-facing workflow compares hourly geometric Sun-center and Earth-center elevation profiles for selected published lunar candidate-region points over an inclusive UTC date range.

The scientific calculation is performed in Python using Skyfield and explicitly provisioned, hash-verified NASA/JPL NAIF kernels. The app is not an Earth WGS84 observer application.

## Current component map

| Component | Responsibility | Current boundary |
|---|---|---|
| `app.py` | Streamlit controls, validation feedback, plots, and caveats | UI/presentation. It currently calls `LunarGeometry` directly. |
| `ephemeris.py` | UTC sample grid, lunar observer, Skyfield target geometry, local ENU projection, kernel integrity | Authoritative calculation path used by the current app. |
| `sites.py` | Curated candidate points and their source/provenance metadata | Source-published coordinates with a provisional frame interpretation. |
| `data/kernels/manifest.json` | Kernel filenames, source URLs, frame, coverage, SHA-256 digests | Scientific input manifest; binary kernels are local and Git-ignored. |
| `scripts/provision_kernels.py` | Explicit kernel provisioning and digest verification | Setup operation; not an import-time or app-startup download. |
| `geometry/contract.py` | Frozen request/result structures and status/provenance types | Newer Tier-1 service contract. |
| `geometry/physics.py` | Pure geometric helper functions and first-order status rules | No ephemeris I/O; helpers must retain their stated limitations. |
| `geometry/service.py` | Adapter from the contract to the existing `LunarGeometry` engine | Callable service path; currently not wired into `app.py`. |
| `tests/` | Unit, kernel-backed integration, independent-oracle, and UI tests | Project verification; kernel-backed tests require provisioned assets. |

## Current data flow

The production/demo path observed in `app.py` is:

```text
Streamlit controls
      |
      v
build_hourly_utc_grid(...)
      |
      v
LunarGeometry(KERNEL_DIR)
      |
      v
calculate_site(site, shared_UTC_epochs)
      |
      v
Sun/Earth center elevation + azimuth series
      |
      v
Plotly charts and explanatory caveats
```

The `geometry/` package is a separate service-contract layer over the same `LunarGeometry` engine:

```text
InstantRequest / WindowRequest
      |
      v
GeometryService
      |
      v
LunarGeometry
      |
      v
frozen result contracts + pure derived metrics
```

This second path must not be described as the app's active calculation route until the UI is deliberately migrated and integration tests demonstrate parity. There must not be a second, independently implemented ephemeris engine in the UI.

## Scientific calculation boundary

The existing engine uses:

- Skyfield for application calculations.
- The `MOON_ME_DE421` lunar body-fixed frame.
- Planetocentric latitude and signed east-positive longitude.
- A spherical PCK-defined reference surface with a zero-metre site elevation assumption.
- Same-epoch geometric directions to the Sun and Earth centers.
- No light-time, stellar-aberration, or atmospheric-refraction correction.
- Hourly UTC samples over inclusive whole calendar days, with the legacy app's 00:00 start through 23:00 end convention.
- Explicit kernel provisioning and SHA-256 verification.

The candidate-site study publishes point coordinates and hemispheres but does not identify their coordinate reference frame in the cited material. The implementation's assignment to planetocentric `MOON_ME_DE421` is provisional. Independent CSPICE comparison validates the calculation under the selected frame; it does not validate the source datum assignment.

See [technical decisions](technical-decisions.md) and [independent reference validation](reference-validation.md) for the detailed conventions, source records, hashes, and oracle values.

## Trust and dependency boundaries

1. The ephemeris engine owns geometric calculations. UI code consumes results and renders them.
2. The kernel manifest is the source of expected scientific asset digests. A digest mismatch is an error, not an invitation to overwrite.
3. Site metadata must retain its source coordinates, coordinate interpretation, and uncertainty.
4. Derived metrics and status labels must expose their assumptions and must not be promoted into physical performance claims.
5. Independent reference values are validation fixtures, not a runtime dependency. CSPICE is not an application dependency.
6. No live NASA resource, Horizons query, DEM, LOLA dataset, dust model, power model, or communications link budget is currently part of the active calculation path.

## Change implications

Changes to frames, kernels, coordinate transformations, UTC/TDB handling, sampling, local basis math, visibility definitions, or aggregate semantics are scientifically material. They require:

- A written decision and source/provenance update.
- A bounded implementation plan and independent oracle or other justified validation.
- Regression tests for affected existing behavior.
- Review through Software Research Studio before acceptance.
- A fresh evidence record tied to the exact candidate commit.

UI-only changes must not alter the calculation contract or reproduce geometry calculations in another language.
