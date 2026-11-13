# Ashura’s Light — current status

**Status date:** 2026-11-13  
**Implementation baseline reviewed:** `ee74fa520e0c45bc664bffa2ae9ea439f05c1ebc`  
**Documentation change branch:** `docs/engineering-baseline`  
**Disposition:** **M1 PARTIAL — acceptance HOLD**

This file is the single living summary of current project state. Historical reports remain evidence/history and must not override this status without a newer, candidate-bound review.

## Product state

Ashura’s Light is a Streamlit geometric lunar-geometry demonstration. The active app compares hourly geometric Sun-center and Earth-center elevation profiles for three published candidate-region points.

It is a planning/education aid only. It is not a landing-site approval tool, power model, communications link budget, terrain-aware visibility engine, or flight-rule system.

## Observed implementation baseline

- `app.py` uses Streamlit and calls `LunarGeometry` directly.
- `ephemeris.py` is the active Skyfield/DE421 geometry implementation.
- Four NAIF kernel assets are defined by `data/kernels/manifest.json`; the provisioner verifies SHA-256 digests. Kernel binaries are not committed.
- `geometry/contract.py`, `geometry/physics.py`, and `geometry/service.py` provide a newer service contract/adapter over the existing engine. The Streamlit UI does **not** currently use this service path.
- Kernel-backed tests exist in `tests/test_geometry_service.py` and skip when the required kernel files are not present.
- The fixed-epoch CSPICE reference is documented in `docs/reference-validation.md`. It validates the implementation under the chosen frame interpretation, not the source coordinate datum.
- The candidate-point source does not state its coordinate reference frame. The current planetocentric `MOON_ME_DE421` interpretation remains provisional.
- No current-revision full-suite result or verified CI result is recorded in this status baseline.

## Verification ledger

| Evidence | Classification | Result / boundary |
|---|---|---|
| Source inspection at `ee74fa5` | OBSERVED | Current app and geometry-service separation described above. |
| Kernel-backed service test definitions | OBSERVED | Tests exist; fixture skips if `data/kernels/de421.bsp` is absent. Test definitions do not prove execution. |
| `docs/implementation-report.md` reports 18 passed | DECLARED / HISTORICAL | The report identifies an earlier base revision (`7d26a3e`) and a clean environment. It does not establish that the newer geometry-service integration tests ran on `ee74fa5`. |
| Current complete test suite | NOT_RUN / NOT_VERIFIED | No exact command output for this candidate is recorded here. |
| Current CI result | UNKNOWN | No verified current-revision CI result is recorded here. |
| Candidate-site source datum | UNKNOWN | Published source coordinates do not identify the frame/latitude type needed to confirm the project's provisional assignment. |

## M1 acceptance blockers

The following items were identified in the review of the service implementation at the reviewed baseline and remain open until a later candidate and test output demonstrate closure:

1. **Window duration bound:** enforce the intended maximum 30-day duration in `GeometryService.window`, not only in the legacy app's date-grid helper.
2. **Endpoint semantics:** define and test behavior when duration is not divisible by `step_hours`. A 24-hour window with a 7-hour step must either reject the request or include the exact endpoint with a documented final interval. Aggregates must use a consistent convention.
3. **UTC validation:** reject naive timestamps and explicitly reject or normalize non-UTC offsets at the service boundary, with tests.
4. **Kernel-backed execution:** provision the four manifest assets and run the complete current suite. Report pure tests, kernel-backed tests, skips, failures, and unrun checks separately.
5. **Repository reconciliation:** record the exact working-fork and public-submission revisions and compare trees before claiming parity or publishing changes.

These are implementation/verification gates, not authorization to expand scope.

## Scientific and product limitations

- Coordinate frame assignment for published candidate points is provisional.
- The current app plots geometric centers, not complete apparent disks.
- The surface model is smooth/spherical; no azimuth-dependent terrain horizon or LOLA DEM is active.
- The approximate mask in the newer contract is not measured terrain.
- No physical dust, thermal, power-generation, relay, or communications model is active.
- No mission-planning or flight-rule conclusions are supported.

## Decision authority

Material changes to product scope, architecture, scientific assumptions, coordinate/data provenance, security/data handling, acceptance criteria, or release posture must be reviewed through [Software Research Studio](https://github.com/holeyfield33-art/software-research-studio), as directed by the project owner.

Studio is an external governance/review reference. It is not a runtime dependency, does not host Ashura’s Light code, and does not replace this repository's tests or evidence. Project implementation and project evidence remain here.

## Next bounded checkpoint

1. Close the three service-contract issues (duration, endpoint, UTC) with focused tests on a dedicated implementation branch.
2. Provision the exact four kernel assets from the manifest and run the complete test suite on the resulting candidate.
3. Reconcile the working/public repository revisions and submit the evidence for Studio review.

No M2, UI migration, new site catalog, DEM integration, dust model, power model, or communications model is authorized by this status note.
