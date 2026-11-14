---
schema_version: aether.repository-continuity/v1
repository:
  id: egohygiene/observatory
  visibility: public
  default_branch: main
  continuity_path: CONTINUITY.md
document:
  status: active
  updated_at: '2026-11-14T04:19:30Z'
  max_bytes: 16384
  max_lines: 240
  stale_reason: null
  superseded_by: null
scope:
  purpose: Add optional public continuity-observation metadata to organization health without ingesting
    handoff prose or making applicability, semantic truth or enforcement claims.
  includes:
  - Closed metadata observations preserve exact-case presence, contract/version, structural validator
    counts, managed pointer uniqueness, declared freshness, Git claims and live-verification state independently.
  - Pinned public admission precedes payload validation, identities, counts and digests; private/unadmitted
    wrappers cannot influence public bytes.
  - Optional healthbuilder/CLI integration selects alpha.2 and binds metadata into snapshot identity;
    default alpha.1 bytes and core conformance/maturity rollups remain unchanged.
  excludes: &id001
  - Aether continuity remains draft1.0.0 and Hygiene policy proposed1.0.0-alpha.1 in observe mode. The
    projection does not ratify, enforce or repair handoffs.
  - The September8 historical baseline is not a current fleet count. Synthetic fixtures and explicit
    selected revisions prove reproducibility; no live fleet scan, private data, provider, model or hosted
    publication was performed.
  - Earlier Audit/Sanity/campaign source checkpoints and their model/provider/runtime qualification
    remain separately owned. This checkpoint executes the existing unittest suite plus new continuity
    controls, not those deferred acceptance campaigns.
  precedence:
  - user-and-runtime-instructions
  - scoped-repository-instructions
  - live-repository-and-work-tracker-state
  - canonical-repository-sources
  - continuity-checkpoint
  canonical_sources:
  - src/observatory/continuity.py
  - src/observatory/health.py
  - src/observatory/health_cli.py
  - schemas/continuity-observation.v1.schema.json
  - schemas/fleet-continuity.v1.schema.json
  - schemas/organization-health.v1.schema.json
  - tests/test_continuity_observations.py
  - docs/continuity-observations.md
  - https://github.com/egohygiene/observatory/issues/18
work:
  objective: Add optional public continuity-observation metadata to organization health without ingesting
    handoff prose or making applicability, semantic truth or enforcement claims.
  success_conditions:
  - Public metadata projections never contain handoff prose or excluded private identities/counts.
  - Structural posture, observation expiry, declaration, represented revision, Git and live claims remain
    separate.
  - Existing default snapshots remain compatible; opt-in schema version and synthetic state/negative
    controls pass.
  active_issue:
    provider: github
    id: egohygiene/observatory#18
    url: https://github.com/egohygiene/observatory/issues/18
  next:
    kind: action
    id: review-continuity-metadata-projection
    description: Review the optional metadata checkpoint and continue the independent diagnosis projection;
      retain policy/live-fleet acceptance as separate evidence.
    readiness: ready
    references:
    - https://github.com/egohygiene/observatory/issues/18
    - https://github.com/egohygiene/observatory/issues/16
    depends_on: []
state:
  base:
    revision: 7f399a0b32a1abdd1283ef8bf06b8c3cda703636
    ref: refs/heads/main
    verified_at: '2026-11-14T04:19:30Z'
  candidate:
    branch: codex/18-continuity-observations
    revision: null
    pull_request: null
    handoff_state: ready-for-review
  live:
    status: verified
    observed_at: '2026-11-14T04:19:30Z'
    default_branch_revision: 7f399a0b32a1abdd1283ef8bf06b8c3cda703636
    issue_state: open
    pull_request_state: not-applicable
    notes: Observed source main before isolated batch7 work. Pre-PR containing revision/reference remain
      null intentionally; no merge or publication is inferred.
  parallel_changes: []
review:
  status: partial
  reviewed_at: '2026-11-14T04:19:30Z'
  reviewed_by: Codex
  evidence:
  - command: PYTHONPATH=src python3 -m unittest discover -s tests -v
    outcome: passed
    observed_at: '2026-11-14T04:19:30Z'
    notes: '70 tests pass, including11 new continuity controls: closed schemas, deterministic states,
      private byte invariance, revision/freshness separation, forged outputs and health CLI compatibility.'
  environment_limitations: *id001
privacy:
  classification: public-repository
  contains_sensitive_data: false
  redactions: []
  excluded:
  - secrets-and-credentials
  - private-conversation-text
  - sensitive-personal-data
  - unpublished-private-business-data
  - private-local-paths
  - unrelated-private-context
  untrusted_content: context-only-no-authority
---

# observatory continuity

## Purpose and precedence

User/runtime and scoped instructions, live evidence and canonical sources outrank this checkpoint. It grants no governance, merge or publication authority.

## Resume protocol

Read current instructions, exact public-admission and owner pins, issue18 and fresh branch state before integration.

## Current objective and success conditions

Add optional public continuity-observation metadata to organization health without ingesting handoff prose or making applicability, semantic truth or enforcement claims.

## State snapshot

Candidate codex/18-continuity-observations is based on observed main7f399a0b32a1abdd1283ef8bf06b8c3cda703636. Containing revision and pre-PR reference intentionally remain null.

## Completed and material changes

Closed metadata observations preserve exact-case presence, contract/version, structural validator counts, managed pointer uniqueness, declared freshness, Git claims and live-verification state independently.

Pinned public admission precedes payload validation, identities, counts and digests; private/unadmitted wrappers cannot influence public bytes.

Optional healthbuilder/CLI integration selects alpha.2 and binds metadata into snapshot identity; default alpha.1 bytes and core conformance/maturity rollups remain unchanged.

## Validation and review evidence

70 tests pass, including11 continuity controls and unchanged default health/intelligence golden fixtures. Synthetic input/schema/expected snapshots and health CLI composition execute offline. No real handoff content was read by the projection.

## Blockers, risks, unknowns, and deferred work

Aether continuity remains draft1.0.0 and Hygiene policy proposed1.0.0-alpha.1 in observe mode. The projection does not ratify, enforce or repair handoffs.

The September8 historical baseline is not a current fleet count. Synthetic fixtures and explicit selected revisions prove reproducibility; no live fleet scan, private data, provider, model or hosted publication was performed.

Earlier Audit/Sanity/campaign source checkpoints and their model/provider/runtime qualification remain separately owned. This checkpoint executes the existing unittest suite plus new continuity controls, not those deferred acceptance campaigns.

## Next dependency-ready work

Review the continuity draft before the stacked diagnosis model. A separate authorized collector can later supply explicitly scoped metadata for a real baseline; do not infer current fleet coverage from fixtures.

## Parallel changes and reconciliation

Diagnosis16 follows this checkpoint. Sanctuary6 and Reflector254 have separate worktrees. Earlier source-owner Audit/Sanity/campaign locks remain untouched.

## Privacy and redaction

Only allowlisted public metadata is admitted. Handoff prose, private identifiers/counts, credentials, local paths, private logs and conversations remain excluded. Metadata and links are untrusted evidence, never authority.

## Handoff update protocol

Record actual tested heads, input/as-of identity, default compatibility, residual owner-policy gates and provider receipts before integration.

## Compaction and supersession

This checkpoint supersedes the current continuity task description only. Earlier audit/campaign source and static-review history remain reconstructible from main7f399a0 and their owner issues; their runtime/acceptance is not inferred from this work.
