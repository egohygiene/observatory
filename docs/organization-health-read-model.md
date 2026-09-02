# Organization-health read-model contract

- Evidence schema: `egohygiene.observatory.repository-evidence/v1`
- Snapshot schema: `egohygiene.observatory.organization-health/v1`
- Contract version: `1.0.0-alpha.1`
- Owner: `egohygiene/observatory`
- Upstream catalog: Hygiene repository catalog v1
- First validator adapter: Egolint report v1

## Purpose and authority

This contract is Observatory's deterministic, read-only organization-health
layer. It joins the canonical Hygiene repository catalog to evidence supplied
by approved collectors and validators, then emits one fleet JSON snapshot and
one Markdown projection.

The snapshot is a read model, not policy truth:

- Hygiene owns repository membership, lifecycle, declared maturity, and policy
  contracts;
- Egolint and other validators own check semantics and findings;
- collectors own observation time, represented commit, and evidence validity;
- Observatory owns defensive ingestion, categorical rollups, provenance
  preservation, and deterministic output; and
- Pace owns remediation plans and reviewable convergence changes.

Observatory does not inspect repositories to reproduce policy checks, select a
newer record when observations conflict, mutate repositories, or calculate a
compliance percentage.

## Inputs

### Hygiene catalog

`--catalog` accepts Hygiene's JSON-compatible YAML catalog v1. The CLI records
the exact caller-supplied source URL, commit, and file SHA-256. Observatory
checks the small subset it must index: schema version, organization identity,
unique repository identities, source links, and lifecycle/maturity fields.
Hygiene validation remains a prerequisite for complete catalog semantics.

The catalog currently has an `observed_at` date but no validity window.
Observatory therefore reports catalog freshness as `unknown` instead of
inventing a staleness threshold.

### Repository evidence

Each evidence record identifies:

- its repository and exact represented commit;
- an observation time and explicit `valid_until` boundary;
- a versioned producer and immutable or reviewable source link; and
- one or more checks with stable IDs, policy contracts, evidence links,
  severity, domain, and assessed dimensions.

The record's producer name plus check ID is the fleet-local check identity.
Duplicate identities for one repository fail closed. The orchestration layer
must resolve competing observations explicitly; Observatory never applies an
implicit latest-wins rule.

Supported check statuses are `pass`, `fail`, `partial`, `unknown`, `blocked`,
and `not_applicable`. A record whose `valid_until` is earlier than the explicit
snapshot `as_of` time contributes `stale` checks regardless of its historical
reported status. Both effective and reported status remain available in JSON.

`--as-of` is mandatory and must be a canonical whole-second UTC timestamp. The
wall clock is never read, so identical inputs produce byte-identical outputs.

## Calculations

Declared maturity is copied from Hygiene and never overwritten by evidence.
The separate maturity-evidence rollup answers whether current evidence supports
that declaration.

Only `required` checks affect either rollup. `advisory` checks remain visible.
For each assessed dimension, the deterministic precedence is:

1. `fail`;
2. `blocked`;
3. `stale`;
4. `unknown`;
5. `partial`;
6. `pass`; and
7. `not_applicable` when every required check is explicitly not applicable.

A missing required assessment is `unknown`.

| Effective check result | Conformance rollup | Maturity-evidence rollup |
| --- | --- | --- |
| fail | non_conformant | contradicted |
| blocked | blocked | blocked |
| stale | stale | stale |
| unknown | unknown | unknown |
| partial | partial | partial |
| all applicable pass | conformant | supported |
| all not applicable | not_applicable | not_applicable |

Every rollup includes the rule, human-readable reason, contributing check IDs,
and exact status counts. There is intentionally no numeric score.

## Egolint adapter

`observatory-health adapt-egolint` consumes a validated, read-only Egolint v1
run report and creates one repository evidence record:

- `clean` plus `normalized` completeness becomes `pass`;
- `clean` with incomplete normalization becomes `partial`;
- `findings` becomes `fail`; and
- `execution_error` becomes `blocked`.

The adapter uses only the report-level result. It does not reinterpret finding
severity, suppressions, tool policy, or exit codes. `fix` reports are rejected
because health collection is read-only. The supported Egolint schema revision
is pinned in `contracts/egolint.report.v1.lock.json`.

## Outputs

`observatory-health build` writes:

- `organization-health.json`, the complete versioned read model; and
- `organization-health.md`, a compact human-readable table with the explicit
  calculation rules.

Repositories without supplied evidence remain in the fleet with `unknown`
assessments. Proposed repositories are not materialized as current inventory.
The checked fixtures prove the current 27-entry catalog with one current
Observatory record and one deliberately stale adapted Egolint record. The
other 25 repositories have no supplied evidence and remain unknown by design;
the Egolint-only record also leaves maturity support unknown.

## Privacy and trust

Inputs must already be sanitized for their target visibility. Observatory
retains only supplied public HTTP(S) provenance links and never loads them.
Tokens, raw private logs, local paths, and secret material do not belong in the
evidence contract. Human renderers must continue treating titles and other
producer-provided text as untrusted display content.

## Compatibility

While alpha, consumers pin the exact contract version. Changes to status
meaning, precedence, evidence identity, freshness, or output shape require a
reviewed version change and regenerated golden fixtures. Adding a producer
adapter does not transfer policy ownership to Observatory.
