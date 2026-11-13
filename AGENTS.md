# Ashura’s Light — agent entrypoint

## Read order

1. [README.md](README.md) — purpose, setup, user-facing scientific caveats.
2. [docs/STATUS.md](docs/STATUS.md) — current implementation state, blockers, and next checkpoint.
3. [docs/SDLC.md](docs/SDLC.md) — project-specific engineering and decision workflow.
4. [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) — actual component boundaries and data flow.
5. [docs/technical-decisions.md](docs/technical-decisions.md) — scientific conventions, kernels, and unresolved coordinate provenance.
6. Read the relevant source and tests before changing them.

Do not treat historical implementation reports as current status. Check their base revision and date.

## Engineering invariants

- `ephemeris.py` / `LunarGeometry` is the verified application calculation path. Preserve the pinned Skyfield and NAIF kernel workflow unless a reviewed scientific defect requires a change.
- The Streamlit layer presents results; it must not independently reimplement lunar geometry.
- The `geometry/` package defines a newer service contract and adapter. It is not currently the Streamlit app's calculation path. Do not claim it is integrated until source and tests prove that.
- The candidate-site source does not declare the points' coordinate reference frame. The `MOON_ME_DE421` planetocentric interpretation remains provisional. Never remove that caveat or describe the points as location-verified.
- Coordinates are planetocentric latitude and signed east-positive longitude in the current engine. Preserve units, frame labels, UTC semantics, and provenance.
- Kernel assets are explicit, local, SHA-256-verified inputs. Do not silently download, replace, regenerate, or change pinned kernels. Update the manifest and scientific decision record only through a reviewed change.
- Missing geometry must remain missing. Do not replace unavailable values with zero or another plausible-looking placeholder.
- Geometric center elevation is not full-disk visibility, actual illumination, electrical power, communications availability, a link budget, or a flight rule.
- The approximate constant horizon mask is not a DEM or terrain model. Do not imply LOLA-derived terrain, dust physics, power-system behavior, or relay performance exists when it does not.
- Preserve fixed-epoch independent CSPICE oracle tolerances. Do not weaken tests to make a change pass.

## Change workflow

1. Pin the base commit and inspect the working tree, relevant code, tests, docs, and repository state.
2. State the user outcome, bounded scope, non-goals, and observable acceptance criteria. Ask only if an essential decision is missing.
3. For material scope, architecture, scientific, security/data, or release decisions, obtain review through [Software Research Studio](https://github.com/holeyfield33-art/software-research-studio). Studio is an external governance reference, not a runtime dependency or a place to store this project's code/evidence.
4. Make the smallest coherent change. Do not mix unrelated cleanup, UI redesign, site expansion, or speculative physics into a focused task.
5. Run the relevant project tests. Provision kernels explicitly before kernel-backed tests. Report pure tests, kernel-backed tests, skips, failures, and unrun checks separately.
6. Update [docs/STATUS.md](docs/STATUS.md) when the current state or next action changes. Update [CHANGELOG.md](CHANGELOG.md) for meaningful behavior changes. Update stable engineering docs only when their facts change. Preserve old evidence rather than rewriting it.
7. Handoff the exact branch/commit, changed paths, commands, actual results, limitations, and next bounded action.

## Evidence language

Use these labels precisely:

- `OBSERVED`: checked directly against the pinned source, file, command output, or independent measurement.
- `DECLARED`: reported by an agent or historical document but not re-executed for the candidate under review.
- `PROPOSED`: a recommendation not yet implemented or accepted.
- `UNKNOWN`: necessary information is missing or contradictory.

For checks use `PASS`, `FAIL`, `NOT_RUN`, or `INCOMPLETE`. A skipped kernel-backed test is not a pass. A historical test result is not evidence for a later commit. A successful test suite does not by itself authorize a release or scientific claim.

## Repository and release boundaries

- Work on the explicitly designated working fork/branch. Do not assume the public submission repository is synchronized.
- Do not push, merge, overwrite, or release to the public submission repository without explicit authorization.
- Keep project code, project tests, and project evidence in this repository. Do not merge this project into Software Research Studio or MOTHERSHIP.
- A release/demo decision is separate from implementation completion and must preserve the scientific limitations in the README and UI.
