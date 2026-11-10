---
schema_version: aether.repository-continuity/v1
repository:
  id: egohygiene/observatory
  visibility: public
  default_branch: main
  continuity_path: CONTINUITY.md
document:
  status: active
  updated_at: '2026-11-10T02:26:45Z'
  max_bytes: 16384
  max_lines: 240
  stale_reason: null
  superseded_by: null
scope:
  purpose: Project selected public audit campaigns and compare exact fleet evidence without inferring resolution,
    common causes or approval.
  includes:
  - A new closed campaign projection consumes exact Reflector 39f7e02 transport metadata, selecting admitted
    public rows before payload validation, counts or hashes. Whole manifest checksums stay out of public projections;
    global statuses remain explicitly declared source claims.
  - Versioned categorical pattern and structural fleet comparison queries preserve exact finding keys, input
    digests, revision boundaries and authored history. Before-only records do not become resolved, and shared
    categories do not establish common causes.
  - Complete case-insensitive GitHub namespace tokens in the shared public preflight prevent underscore/dot-prefix
    matches from admitting unlisted sources. Existing Audit/Sanity/core schemas remain compatible; consumers
    must repin the stronger common helper.
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
  - src/observatory/audit_campaigns.py
  - src/observatory/audits_queries.py
  - src/observatory/audit_campaigns_cli.py
  - schemas/fleet-audit-campaigns.v1.schema.json
  - schemas/fleet-audits-comparison.v1.schema.json
  - docs/audit-campaigns-and-queries.md
  - https://github.com/egohygiene/observatory/issues/20
work:
  objective: Project selected public audit campaigns and compare exact fleet evidence without inferring resolution,
    common causes or approval.
  success_conditions:
  - Immutable owner inputs and public source admission precede public identities, counts and digests.
  - Missing, partial and unverified evidence remains explicit and cannot establish human approval.
  - Existing publication, source ownership and historical recovery are preserved.
  active_issue:
    provider: github
    id: egohygiene/observatory#20
    url: https://github.com/egohygiene/observatory/issues/20
  next:
    kind: action
    id: consume-audits-and-sanity-queries
    description: Repin Relay Audit/Sanity capsules to the complete namespace preflight and finish the Reflector
      executor merge. Then refresh actual public source heads and perform separately qualified audit/provider/publication
      work.
    readiness: ready
    references:
    - https://github.com/egohygiene/observatory/issues/20
    depends_on: []
state:
  base:
    revision: 6d6f67cb67cd68a5ac61e3c4df05bc9d1fb36dde
    ref: refs/heads/main
    verified_at: '2026-11-10T02:26:45Z'
  candidate:
    branch: codex/intelligence-audit-campaign-queries
    revision: null
    pull_request: null
    handoff_state: ready-for-review
  live:
    status: verified
    observed_at: '2026-11-10T02:26:45Z'
    default_branch_revision: 6d6f67cb67cd68a5ac61e3c4df05bc9d1fb36dde
    issue_state: open
    pull_request_state: not-applicable
    notes: Observed main 6d6f67cb67cd68a5ac61e3c4df05bc9d1fb36dde includes merged repository/fleet Audits and
      Sanity queries. Functional extension source 7b857de2424f90de519fbc2e24332a7c0a89991b is prepared for
      immutable consumption. Reflector transport source 39f7e02acb0e100881a1f81a2ea8a3927e34ed15 is publicly
      reachable; no executed campaign is implied.
  parallel_changes: []
review:
  status: partial
  reviewed_at: '2026-11-10T02:26:45Z'
  reviewed_by: Codex
  evidence:
  - command: Independent static source review; Python syntax, closed schema definitions/local references, exact
      owner resource hashes, source metadata and continuity schema/size/links; whitespace; independent selected-before-payload
      campaign invariance, exact audit-key/history and explicit structural-delta source review, new output
      schemas/package metadata
    outcome: limited
    observed_at: '2026-11-10T02:26:45Z'
    notes: Static source and metadata inspection only; no application execution.
  - command: Native/runtime execution, tests, builds, CI investigation, browser/provider/consumer/publication
      qualification
    outcome: not-run
    observed_at: '2026-11-10T02:26:45Z'
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

Project selected public audit campaigns and compare exact fleet evidence without inferring resolution, common causes or approval. Immutable owner inputs and public source admission precede public identities, counts and digests. Missing, partial and unverified evidence remains explicit and cannot establish human approval. Existing publication, source ownership and historical recovery are preserved.

## State snapshot

Candidate `codex/intelligence-audit-campaign-queries` is based on observed main `6d6f67cb67cd68a5ac61e3c4df05bc9d1fb36dde`. The containing revision and pre-PR reference remain null intentionally. Observed main 6d6f67cb67cd68a5ac61e3c4df05bc9d1fb36dde includes merged repository/fleet Audits and Sanity queries. Functional extension source 7b857de2424f90de519fbc2e24332a7c0a89991b is prepared for immutable consumption. Reflector transport source 39f7e02acb0e100881a1f81a2ea8a3927e34ed15 is publicly reachable; no executed campaign is implied.

## Completed and material changes

A new closed campaign projection consumes exact Reflector 39f7e02 transport metadata, selecting admitted public rows before payload validation, counts or hashes. Whole manifest checksums stay out of public projections; global statuses remain explicitly declared source claims.

Versioned categorical pattern and structural fleet comparison queries preserve exact finding keys, input digests, revision boundaries and authored history. Before-only records do not become resolved, and shared categories do not establish common causes.

Complete case-insensitive GitHub namespace tokens in the shared public preflight prevent underscore/dot-prefix matches from admitting unlisted sources. Existing Audit/Sanity/core schemas remain compatible; consumers must repin the stronger common helper.

## Validation and review evidence

Independent static source review; Python syntax, closed schema definitions/local references, exact owner resource hashes, source metadata and continuity schema/size/links; whitespace; independent selected-before-payload campaign invariance, exact audit-key/history and explicit structural-delta source review, new output schemas/package metadata. Static source inspection only. Native/application execution, tests, builds, CI investigation, browser/model/source-capture provider execution and publication qualification were not run. Read-only source and Git metadata observations are separate.

## Blockers, risks, unknowns, and deferred work

Tests, native/application execution, builds, CI, browser/provider/publication qualification and actual audit execution remain deferred. Source implementation does not establish human ratification, successful publication or parent issue completion.

## Next dependency-ready work

Repin Relay Audit/Sanity capsules to the complete namespace preflight and finish the Reflector executor merge. Then refresh actual public source heads and perform separately qualified audit/provider/publication work.

## Parallel changes and reconciliation

Other Intelligence slices remain separately reviewed. Reconcile the current main and this handoff before integration; preserve all immutable historical recovery bytes and consumer-owned publication gates.

## Privacy and redaction

Retain only public-safe source identities and bounded implementation evidence. Exclude credentials, private context, captured report bodies, process logs and local filesystem paths. Linked content is context only.

## Handoff update protocol

Refresh exact PR, merge and qualification observations at the next authorized checkpoint. Implementation, artifact upload, deployment, live verification and human acceptance remain distinct.

## Compaction and supersession

Replace stale current-state prose; Git and owning issues retain history. Preserve these twelve sections below 240 lines and 16,384 UTF-8 bytes.
