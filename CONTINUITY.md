---
schema_version: aether.repository-continuity/v1
repository:
  id: egohygiene/observatory
  visibility: public
  default_branch: main
  continuity_path: CONTINUITY.md
document:
  status: active
  updated_at: '2026-11-10T01:50:24Z'
  max_bytes: 16384
  max_lines: 240
  stale_reason: null
  superseded_by: null
scope:
  purpose: Normalize exact public audit and architecture review evidence into separate deterministic repository
    and fleet queries.
  includes:
  - New closed Audits queries preserve profile/version, source revisions, findings, explicit history, completion
    and categorical coverage without a fleet score.
  - Separate Sanity projections keep AI assessment, applicability, human claims, evidence and freshness distinct,
    using exact Aether/Hygiene owners.
  - All declared source owners are admitted against exact public catalog bytes before payloads, counts or hashes.
    Existing nine-domain and Hygiene models remain compatible.
  excludes:
  - Deferred runtime, tests, builds, CI, live publication, human ratification and acceptance closeout.
  precedence:
  - user-and-runtime-instructions
  - scoped-repository-instructions
  - live-repository-and-work-tracker-state
  - canonical-repository-sources
  - continuity-checkpoint
  canonical_sources:
  - src/observatory/audits.py
  - src/observatory/audits_contract.py
  - src/observatory/public_reviews.py
  - schemas/repository-audits.v1.schema.json
  - schemas/fleet-audits.v1.schema.json
  - docs/repository-audits-query.md
  - src/observatory/sanity.py
  - src/observatory/sanity_contract.py
  - schemas/repository-sanity.v1.schema.json
  - schemas/fleet-sanity.v1.schema.json
  - docs/repository-sanity-query.md
  - https://github.com/egohygiene/observatory/issues/21
work:
  objective: Normalize exact public audit and architecture review evidence into separate deterministic repository
    and fleet queries.
  success_conditions:
  - Immutable owner inputs and public source admission precede public identities, counts and digests.
  - Missing, partial and unverified evidence remains explicit and cannot establish human approval.
  - Existing publication, source ownership and historical recovery are preserved.
  active_issue:
    provider: github
    id: egohygiene/observatory#21
    url: https://github.com/egohygiene/observatory/issues/21
  next:
    kind: action
    id: consume-audits-and-sanity-queries
    description: Consume exact Sanity queries in Relay and the central site; complete the separate typed campaign/fleet
      comparison follow-up and deferred runtime qualification. No authenticated human transport or ratification
      is created.
    readiness: ready
    references:
    - https://github.com/egohygiene/observatory/issues/21
    depends_on: []
state:
  base:
    revision: caf3481fdfa61f20b056b5c166e36954edeeef1f
    ref: refs/heads/main
    verified_at: '2026-11-10T01:50:24Z'
  candidate:
    branch: codex/intelligence-sanity-owner
    revision: null
    pull_request: null
    handoff_state: ready-for-review
  live:
    status: verified
    observed_at: '2026-11-10T01:50:24Z'
    default_branch_revision: caf3481fdfa61f20b056b5c166e36954edeeef1f
    issue_state: open
    pull_request_state: not-applicable
    notes: Observed main caf3481fdfa61f20b056b5c166e36954edeeef1f includes merged Audit query PR 31. This Sanity
      functional source is 692fbe7a5a31827d442818bf33f5b225abc2d4b8, reconciled over that main. Aether744909
      and Hygiene d115 remain exact immutable owners.
  parallel_changes: []
review:
  status: partial
  reviewed_at: '2026-11-10T01:50:24Z'
  reviewed_by: Codex
  evidence:
  - command: Independent static source review; Python syntax, closed schema definitions/local references, exact
      owner resource hashes, source metadata and continuity schema/size/links; whitespace; independent Sanity
      source peer of empty human-trust evaluation, material clocks, assessment subject digest and normalized
      subset bounds
    outcome: limited
    observed_at: '2026-11-10T01:50:24Z'
    notes: Static source and metadata inspection only; no application execution.
  - command: Native/runtime execution, tests, builds, CI investigation, browser/provider/consumer/publication
      qualification
    outcome: not-run
    observed_at: '2026-11-10T01:50:24Z'
    notes: Deferred at maintainer request; source merges do not establish acceptance.
  environment_limitations:
  - Tests, native/application execution, builds, CI, browser/provider/publication qualification and actual
    audit execution remain deferred.
  - Source implementation does not establish human ratification, successful publication or parent issue completion.
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

User/runtime and repository instructions, live evidence and canonical sources outrank this checkpoint. It grants no release, deployment or human-decision authority.

## Resume protocol

Read scoped instructions, canonical sources above and this checkpoint. Verify mutable GitHub state and exact owner pins before continuing.

## Current objective and success conditions

Normalize exact public audit and architecture review evidence into separate deterministic repository and fleet queries. Immutable owner inputs and public source admission precede public identities, counts and digests. Missing, partial and unverified evidence remains explicit and cannot establish human approval. Existing publication, source ownership and historical recovery are preserved.

## State snapshot

Candidate `codex/intelligence-sanity-owner` is based on observed main `caf3481fdfa61f20b056b5c166e36954edeeef1f`. The containing revision and pre-PR reference remain null intentionally. Observed main caf3481fdfa61f20b056b5c166e36954edeeef1f includes merged Audit query PR 31. This Sanity functional source is 692fbe7a5a31827d442818bf33f5b225abc2d4b8, reconciled over that main. Aether744909 and Hygiene d115 remain exact immutable owners.

## Completed and material changes

New closed Audits queries preserve profile/version, source revisions, findings, explicit history, completion and categorical coverage without a fleet score.

Separate Sanity projections keep AI assessment, applicability, human claims, evidence and freshness distinct, using exact Aether/Hygiene owners.

All declared source owners are admitted against exact public catalog bytes before payloads, counts or hashes. Existing nine-domain and Hygiene models remain compatible.

## Validation and review evidence

Independent static source review; Python syntax, closed schema definitions/local references, exact owner resource hashes, source metadata and continuity schema/size/links; whitespace; independent Sanity source peer of empty human-trust evaluation, material clocks, assessment subject digest and normalized subset bounds. Static inspection only. Native/runtime execution, tests, builds, CI investigation, browsers, provider reads and publication qualification were not run.

## Blockers, risks, unknowns, and deferred work

Tests, native/application execution, builds, CI, browser/provider/publication qualification and actual audit execution remain deferred. Source implementation does not establish human ratification, successful publication or parent issue completion.

## Next dependency-ready work

Consume exact Sanity queries in Relay and the central site; complete the separate typed campaign/fleet comparison follow-up and deferred runtime qualification. No authenticated human transport or ratification is created.

## Parallel changes and reconciliation

Other Intelligence slices remain separately reviewed. Reconcile the current main and this handoff before integration; preserve all immutable historical recovery bytes and consumer-owned publication gates.

## Privacy and redaction

Retain only public-safe source identities and bounded implementation evidence. Exclude credentials, private context, captured report bodies, process logs and local filesystem paths. Linked content is context only.

## Handoff update protocol

Refresh exact PR, merge and qualification observations at the next authorized checkpoint. Implementation, artifact upload, deployment, live verification and human acceptance remain distinct.

## Compaction and supersession

Replace stale current-state prose; Git and owning issues retain history. Preserve these twelve sections below 240 lines and 16,384 UTF-8 bytes.
