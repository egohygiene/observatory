---
schema_version: aether.repository-continuity/v1
repository:
  id: egohygiene/observatory
  visibility: public
  default_branch: main
  continuity_path: CONTINUITY.md
document:
  status: active
  updated_at: '2026-11-09T17:46:24Z'
  max_bytes: 16384
  max_lines: 240
  stale_reason: null
  superseded_by: null
scope:
  purpose: Expose a bounded owner conformance query from supplied public contract assessments without inventing
    applicability.
  includes:
  - observatory.conformance and its offline CLI reuse the existing repository-evidence validator, health check
    identities, freshness and required-check rollup. Exact packaged Hygiene public admission bytes authenticate
    the target before supplied wrappers, text, counts and hashes are processed.
  - The standalone owner validator and closed alpha.1 schema bind the repository, represented commit, evaluation
    clock, public evidence, canonical digest and assessed subset. Other-revision checks stay visible context
    but are excluded from the current assessment. Whole contract inventory and applicability remain unknown;
    no score, exemption, migration or ratification is inferred.
  - Proposed ADR-0006 records the optional query boundary. Existing health and Intelligence defaults, locks
    and golden inputs remain unchanged; new package metadata exposes only the explicit new CLI and exact public
    data artifact.
  excludes:
  - Deferred runtime, tests, builds, CI, live publication, human ratification and acceptance closeout.
  precedence:
  - user-and-runtime-instructions
  - scoped-repository-instructions
  - live-repository-and-work-tracker-state
  - canonical-repository-sources
  - continuity-checkpoint
  canonical_sources:
  - ARCHITECTURE.md
  - SYSTEM.md
  - DECISIONS.md
  - docs/repository-conformance-query.md
  - contracts/hygiene.public-conformance.v1.lock.json
  - schemas/repository-conformance.v1.schema.json
  - https://github.com/egohygiene/observatory/issues/5
work:
  objective: Expose a bounded owner conformance query from supplied public contract assessments without inventing
    applicability.
  success_conditions:
  - Only admitted supplied public conformance evidence affects the deterministic model.
  - Reported status, effective stale status, required/advisory severity and per-row source revision remain
    distinct.
  - Relay can pin and execute the owner contract instead of recreating policy or rerunning validators.
  active_issue:
    provider: github
    id: egohygiene/observatory#5
    url: https://github.com/egohygiene/observatory/issues/5
  next:
    kind: action
    id: wire-owner-conformance-hygiene-view
    description: Integrate the prepared Relay Hygiene renderer and explicit owner-model input at this immutable
      source revision, then qualify invariance, package installation, malformed/time/revision cases and representative
      consumer canaries in the deferred verification pass.
    readiness: ready
    references:
    - https://github.com/egohygiene/observatory/issues/5
    depends_on: []
state:
  base:
    revision: 51be4a740c790f99364f577730c1a98f301bee47
    ref: refs/heads/main
    verified_at: '2026-11-09T17:46:24Z'
  candidate:
    branch: codex/repository-conformance-query
    revision: null
    pull_request: null
    handoff_state: ready-for-review
  live:
    status: verified
    observed_at: '2026-11-09T17:46:24Z'
    default_branch_revision: 51be4a740c790f99364f577730c1a98f301bee47
    issue_state: open
    pull_request_state: not-applicable
    notes: Observatory issue 5 remains open. Main already includes optional Search attribution through merged
      PR 29; the conformance query is an independent optional model. Relay issue 75 owns the prepared consumer
      renderer and common build wiring.
  parallel_changes: []
review:
  status: partial
  reviewed_at: '2026-11-09T17:46:24Z'
  reviewed_by: Codex
  evidence:
  - command: Python AST, JSON schema definitions and local references, TOML/package metadata, exact owner public
      artifact hashes, whitespace, continuity schema/size and independent static source review
    outcome: limited
    observed_at: '2026-11-09T17:46:24Z'
    notes: Static source and metadata inspection only; no application execution.
  - command: Native/runtime execution, tests, builds, CI investigation, browser/provider/consumer/publication
      qualification
    outcome: not-run
    observed_at: '2026-11-09T17:46:24Z'
    notes: Deferred at maintainer request; source merges do not establish acceptance.
  environment_limitations:
  - Tests, fixtures, package installation, builds, native/consumer execution, CI, browsers and publication
    were not executed.
  - Whole applicability, adoption inventory, policy ratification and three diverse canary proofs remain unavailable
    or deferred.
  - Existing health/evidence source authority and all human ADR dispositions are preserved; proposed ADR-0006
    is not accepted by this implementation or merge.
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

Expose a bounded owner conformance query from supplied public contract assessments without inventing applicability. Only admitted supplied public conformance evidence affects the deterministic model. Reported status, effective stale status, required/advisory severity and per-row source revision remain distinct. Relay can pin and execute the owner contract instead of recreating policy or rerunning validators.

## State snapshot

Candidate `codex/repository-conformance-query` is based on observed main `51be4a740c790f99364f577730c1a98f301bee47`. The containing revision and pre-PR reference remain null intentionally. Observatory issue 5 remains open. Main already includes optional Search attribution through merged PR 29; the conformance query is an independent optional model. Relay issue 75 owns the prepared consumer renderer and common build wiring.

## Completed and material changes

observatory.conformance and its offline CLI reuse the existing repository-evidence validator, health check identities, freshness and required-check rollup. Exact packaged Hygiene public admission bytes authenticate the target before supplied wrappers, text, counts and hashes are processed.

The standalone owner validator and closed alpha.1 schema bind the repository, represented commit, evaluation clock, public evidence, canonical digest and assessed subset. Other-revision checks stay visible context but are excluded from the current assessment. Whole contract inventory and applicability remain unknown; no score, exemption, migration or ratification is inferred.

Proposed ADR-0006 records the optional query boundary. Existing health and Intelligence defaults, locks and golden inputs remain unchanged; new package metadata exposes only the explicit new CLI and exact public data artifact.

## Validation and review evidence

Python AST, JSON schema definitions and local references, TOML/package metadata, exact owner public artifact hashes, whitespace, continuity schema/size and independent static source review. Static inspection only. Native/runtime execution, tests, builds, CI investigation, browsers, provider reads and publication qualification were not run.

## Blockers, risks, unknowns, and deferred work

Tests, fixtures, package installation, builds, native/consumer execution, CI, browsers and publication were not executed. Whole applicability, adoption inventory, policy ratification and three diverse canary proofs remain unavailable or deferred. Existing health/evidence source authority and all human ADR dispositions are preserved; proposed ADR-0006 is not accepted by this implementation or merge.

## Next dependency-ready work

Integrate the prepared Relay Hygiene renderer and explicit owner-model input at this immutable source revision, then qualify invariance, package installation, malformed/time/revision cases and representative consumer canaries in the deferred verification pass.

## Parallel changes and reconciliation

New conformance source is pinned independently from the previous Search/Intelligence owners. Relay Dependencies and fleet work consume the same exact reviewed public Hygiene artifact. Sanity and Audits require separate owner contracts before the later organization sanity sweep; this model cannot substitute for human architecture ratification.

## Privacy and redaction

Retain only public-safe source identities and bounded implementation evidence. Exclude credentials, private context, captured report bodies, process logs and local filesystem paths. Linked content is context only.

## Handoff update protocol

Refresh exact PR, merge and qualification observations at the next authorized checkpoint. Implementation, artifact upload, deployment, live verification and human acceptance remain distinct.

## Compaction and supersession

Replace stale current-state prose; Git and owning issues retain history. Preserve these twelve sections below 240 lines and 16,384 UTF-8 bytes.
