---
schema_version: aether.repository-continuity/v1
repository:
  id: egohygiene/observatory
  visibility: public
  default_branch: main
  continuity_path: CONTINUITY.md
document:
  status: active
  updated_at: '2026-11-14T04:27:40Z'
  max_bytes: 16384
  max_lines: 240
  stale_reason: null
  superseded_by: null
scope:
  purpose: Project already-validated public diagnosis metadata and compose through existing Repository
    Intelligence extensions without ingesting records or inferring diagnosis truth, policy approval
    or health.
  includes:
  - Public catalog admission and per-record public/approved metadata selectors precede IDs, timestamps,
    paths, counts and digests; restricted, pending and withheld payloads cannot influence public bytes.
  - Closed node/edge metadata preserves independent lifecycle/reproduction/root-cause/remediation/validation/conformance,
    represented artifact/revision, source and expiry, redaction, optional hypotheses and explicit relationships.
    Missing records never imply no defects.
  - Pure library and explicit offline CLI build sealed repository/fleet views. Composition uses existing
    RI extensions with exact repository/revision binding and retains the core graph, queries and default
    bytes.
  excludes: &id001
  - Hygiene41 still has no versioned applicability/publication policy. Output explicitly preserves policy
    unavailable, source-declared applicability/publication and no enforcement; synthetic approval references
    are not human ratification.
  - Aether diagnosis1.0.0 remains draft. Content digests and publication authority are unverified source
    claims; only normalized public view digests are calculated. No source validator, private record,
    raw telemetry, provider/model or hosted publication was executed.
  - The stacked continuity projection remains observe-mode optional metadata. Historical fleet counts
    and deferred Audit/Sanity/campaign runtime/acceptance remain separately owned.
  precedence:
  - user-and-runtime-instructions
  - scoped-repository-instructions
  - live-repository-and-work-tracker-state
  - canonical-repository-sources
  - continuity-checkpoint
  canonical_sources:
  - src/observatory/diagnoses.py
  - src/observatory/diagnoses_cli.py
  - contracts/aether.diagnosis-record.v1.lock.json
  - schemas/diagnosis-observations.v1.schema.json
  - schemas/fleet-diagnoses.v1.schema.json
  - tests/test_diagnosis_observations.py
  - docs/diagnosis-observations.md
  - https://github.com/egohygiene/observatory/issues/16
work:
  objective: Project already-validated public diagnosis metadata and compose through existing Repository
    Intelligence extensions without ingesting records or inferring diagnosis truth, policy approval
    or health.
  success_conditions:
  - Public metadata remains closed and cannot reveal excluded record identities or counts.
  - Independent states, represented artifacts, source claims, freshness and policy uncertainty remain
    distinct.
  - Default RI graph/views and fixtures are unchanged; optional extension and snapshot identity bind
    the selected metadata.
  active_issue:
    provider: github
    id: egohygiene/observatory#16
    url: https://github.com/egohygiene/observatory/issues/16
  next:
    kind: action
    id: review-diagnosis-metadata-projection
    description: Review the stacked continuity34 and diagnosis draft. Keep Hygiene41 policy and downstream
      real-data acceptance open; consumers must pin the alpha metadata contract before selecting the
      extension.
    readiness: ready
    references:
    - https://github.com/egohygiene/observatory/pull/34
    - https://github.com/egohygiene/observatory/issues/16
    - https://github.com/egohygiene/hygiene/issues/41
    depends_on: []
state:
  base:
    revision: d126ff87c68121a2eaab6fd0cb106369abf360f8
    ref: refs/heads/codex/18-continuity-observations
    verified_at: '2026-11-14T04:27:40Z'
  candidate:
    branch: codex/16-diagnosis-observations
    revision: null
    pull_request: null
    handoff_state: ready-for-review
  live:
    status: verified
    observed_at: '2026-11-14T04:27:40Z'
    default_branch_revision: 7f399a0b32a1abdd1283ef8bf06b8c3cda703636
    issue_state: open
    pull_request_state: not-applicable
    notes: Diagnosis work stacks on continuity PR34 headd126ff8. Containing revision and pre-PR reference
      remain null intentionally; no merge/publication or policy approval is inferred.
  parallel_changes: []
review:
  status: partial
  reviewed_at: '2026-11-14T04:27:40Z'
  reviewed_by: Codex
  evidence:
  - command: PYTHONPATH=src python3 -m unittest discover -s tests -v; python3 scripts/verify_fixtures.py;
      python3 scripts/verify_health_fixtures.py
    outcome: passed
    observed_at: '2026-11-14T04:27:40Z'
    notes: 86 tests pass:15 diagnosis controls,12 continuity controls and59 existing. All15 RI repository/view/fleet
      goldens and health JSON/Markdown fixtures verify unchanged. Synthetic schema/metadata/CLI/RI extension
      and private-byte invariance checks execute offline.
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

Read exact owner/admission pins, current issue16/Hygiene41 state and stacked PR34 before selecting a metadata consumer.

## Current objective and success conditions

Project already-validated public diagnosis metadata and compose through existing Repository Intelligence extensions without ingesting records or inferring diagnosis truth, policy approval or health.

## State snapshot

Candidate codex/16-diagnosis-observations is stacked on PR34 headd126ff87c68121a2eaab6fd0cb106369abf360f8, based on main7f399a0b32a1abdd1283ef8bf06b8c3cda703636. Containing revision and pre-PR reference intentionally remain null.

## Completed and material changes

Public catalog admission and per-record public/approved metadata selectors precede IDs, timestamps, paths, counts and digests; restricted, pending and withheld payloads cannot influence public bytes.

Closed node/edge metadata preserves independent lifecycle/reproduction/root-cause/remediation/validation/conformance, represented artifact/revision, source and expiry, redaction, optional hypotheses and explicit relationships. Missing records never imply no defects.

Pure library and explicit offline CLI build sealed repository/fleet views. Composition uses existing RI extensions with exact repository/revision binding and retains the core graph, queries and default bytes.

## Validation and review evidence

86 tests pass, including15 diagnosis and12 continuity controls. All15 RI goldens and health JSON/Markdown fixtures verify unchanged. Synthetic metadata schemas, state/privacy controls, no-overwrite CLI and RI extension composition execute offline; no diagnosis body is parsed.

## Blockers, risks, unknowns, and deferred work

Hygiene41 still has no versioned applicability/publication policy. Output explicitly preserves policy unavailable, source-declared applicability/publication and no enforcement; synthetic approval references are not human ratification.

Aether diagnosis1.0.0 remains draft. Content digests and publication authority are unverified source claims; only normalized public view digests are calculated. No source validator, private record, raw telemetry, provider/model or hosted publication was executed.

The stacked continuity projection remains observe-mode optional metadata. Historical fleet counts and deferred Audit/Sanity/campaign runtime/acceptance remain separately owned.

## Next dependency-ready work

Review continuity PR34 and the stacked diagnosis draft. Keep the source policy gate and real source/provider/consumer acceptance separate. Do not interpret a structural adapter pass as diagnosis truth or policy approval.

## Parallel changes and reconciliation

Sanctuary6 and Reflector254 have separate worktrees/PRs. No audit/sanity/campaign owner bytes or interfaces were changed.

## Privacy and redaction

Only explicitly approved public metadata enters projections. Restricted, withheld, pending and unadmitted payloads are excluded before identities/counts/digests. Credentials, source bodies, private telemetry and private conversation text remain absent.

## Handoff update protocol

Record exact tested heads, selected metadata/as-of identity, unresolved policy/authority claims and actual provider receipts before integration.

## Compaction and supersession

This checkpoint advances from optional continuity metadata to diagnosis projection. Earlier Audit/Sanity/campaign source and deferred acceptance history remain in owner issues/main7f399a0; no previous qualification is implied.
