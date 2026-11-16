# Ashura’s Light — software development lifecycle

**Purpose:** lightweight, risk-adaptive engineering rules for this repository. This is a working project contract, not a mandatory document-production process. Apply only the controls relevant to the change.

## Governance and authority

- The project owner sets product intent and authorizes scope.
- [Software Research Studio](https://github.com/holeyfield33-art/software-research-studio) is the external engineering-governance and decision-review reference by explicit project direction. Material SDLC decisions are reviewed there before they are treated as accepted.
- This repository remains the authority for Ashura’s Light implementation, project-specific decisions, tests, and execution evidence.
- Studio review does not execute code, prove a test result, or authorize a repository write/release by itself.
- The public submission repository and the working fork are distinct operational targets. Verify remotes, branch, commit, and tree before synchronization. Do not push, merge, or overwrite the public submission repository without explicit approval.

## 1. Intake and scope

For each non-trivial change, capture a short statement in the task/PR description:

- User or scientific problem being solved.
- Intended outcome and observable acceptance criteria.
- Relevant repository and exact base commit.
- Allowed files/operations and explicit non-goals.
- Risks, assumptions, data dependencies, and unresolved questions.
- Required verification and who decides acceptance.

Keep the scope narrow. A UI task does not authorize a new geometry engine; a geometry task does not authorize site expansion or new physics models.

## 2. Risk-adaptive change levels

| Level | Typical change | Minimum engineering response |
|---|---|---|
| **T0 — editorial** | Documentation wording, typo, formatting | Check links and factual accuracy; no code test claim needed. |
| **T1 — routine** | UI presentation, low-risk refactor, non-scientific behavior | Focused tests, relevant smoke check, update docs/status if behavior changes. |
| **T2 — scientific/contract** | Ephemeris math, frames, coordinate transforms, time, sampling, aggregation, visibility, kernel manifest, public service contract | Explicit decision record; independent oracle or justified validation; positive and negative tests; full relevant suite with kernel-backed results distinguished; Studio review. |
| **T3 — high consequence** | New external data ingestion, deployment/security boundary, user-impacting automation, or any proposed operational/mission-use claim | Stop for explicit owner scope approval, threat/data review as applicable, independent validation, Studio review, and a separate release decision. Mission-use claims remain out of scope unless a new project mandate and evidence standard are explicitly approved. |

Unknown risk is not automatically low risk. If a change crosses levels, use the higher level.

## 3. Requirements and acceptance

Translate the request into a small set of testable behaviors. For scientific work, specify:

- Coordinate frame, latitude type, longitude sign convention, units, and reference surface.
- Time scale and timezone behavior.
- Source/provenance of every external coordinate or scientific asset.
- Exact meaning of visibility, clearance, sampling, interpolation, and aggregate metrics.
- Model assumptions and what the result must not be used to claim.
- Independent reference values, tolerances, and negative controls where appropriate.

Do not convert an assumption into a fact merely because code and tests agree with each other.

## 4. Design and decisions

Before changing a material boundary, record the problem, options considered, chosen approach, consequences, validation, and supersession status. Keep detailed scientific conventions in [technical decisions](technical-decisions.md); keep this SDLC focused on how work is governed.

An architectural or scientific decision should identify:

- The source of truth and component that owns the behavior.
- Inputs, outputs, units, errors, and trust boundaries.
- Compatibility and migration effects.
- Failure modes and rollback/recovery.
- Verification that could falsify the intended behavior.

Avoid speculative abstractions and parallel implementations. The existing Skyfield path remains the geometry authority unless a reviewed decision changes it.

## 5. Implementation

- Pin the starting commit and work on an explicit branch.
- Inspect relevant source, tests, dependencies, docs, and current status before editing.
- Make the smallest coherent patch; do not mix unrelated cleanup or future features.
- Preserve deterministic behavior, explicit scientific data provisioning, and pinned asset hashes.
- Keep UI and calculation responsibilities separate.
- Do not suppress errors, silently substitute data, or fabricate missing values.
- Update user-facing caveats whenever a change affects interpretation.

## 6. Verification and evidence

Run the narrowest useful checks first, then the broader suite required by risk. Typical commands from the repository root:

```bash
# Pure geometry-contract tests (no ephemeris kernels required)
python -m pytest -q tests/test_geometry_contract.py

# Kernel-backed application and service tests
python scripts/provision_kernels.py
python -m pytest -q

# Optional syntax sanity check for Python modules
python -m compileall -q .
```

Provisioning requires network access to the NAIF archive. It is an explicit operation and must not be run as an incidental side effect. Confirm the manifest hashes after provisioning.

For every material verification claim, record:

- Candidate commit SHA and environment/Python version.
- Exact command and actual output.
- Passed, failed, skipped, and deselected counts.
- Whether kernels were present and verified.
- Independent oracle/reference and tolerance, if applicable.
- Known limitations and tests not run.

Use `PASS`, `FAIL`, `NOT_RUN`, and `INCOMPLETE` for checks. A skipped integration test is not a pass. Historical test counts are not current-candidate evidence. CI status must be checked on the exact commit; absence of a result is not a pass.

## 7. Review and acceptance

A change is ready for project review only when:

- Scope and acceptance criteria are satisfied.
- The diff is limited to authorized paths and behavior.
- Relevant tests and independent checks have truthful results.
- Documentation and user-facing limitations match the implementation.
- No unresolved blocker is hidden by a broad test count.

The reviewer may return `GO`, `CONDITIONAL`, `NO-GO`, or `HOLD`, with the scope and evidence boundary stated. A local test pass is not a release decision.

## 8. Release and operation

Release is a separate decision after implementation acceptance. Before a public demo or tagged release:

- Re-run the applicable suite on the exact candidate.
- Verify kernel manifest and provenance behavior in a clean environment.
- Confirm supported date range, UTC behavior, and disclosed scientific limitations.
- Confirm the public repository/branch/commit explicitly.
- Review README, status, changelog, license, and reproducible setup instructions.
- Obtain the project owner's release approval and Studio review for material release claims.

Never describe this MVP as mission-ready, location-verified, power-capable, communications-capable, or terrain-aware on the current evidence.

## 9. Maintenance and documentation

- `README.md`: public purpose, setup, use, limitations, and links.
- `AGENTS.md`: short agent entrypoint, invariants, read order, and handoff rules.
- `docs/STATUS.md`: the one living current-state summary and next bounded checkpoint.
- `docs/SDLC.md`: this engineering lifecycle and acceptance policy.
- `docs/ARCHITECTURE.md`: current component boundaries and data flow.
- `docs/technical-decisions.md`: scientific conventions, kernel provenance, and unresolved assumptions.
- `docs/reference-validation.md`: fixed-epoch independent oracle details.
- `docs/implementation-report.md`: historical implementation report; do not silently rewrite it into current status.
- `CHANGELOG.md`: meaningful user-visible changes, not a task diary.

Update only the documents whose authoritative content changed. Preserve historical evidence; add a new dated/candidate-bound report rather than rewriting old results.
