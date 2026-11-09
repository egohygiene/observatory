---
schema: aether.architecture-document/v1
id: observatory-decisions
title: Observatory Decisions
kind: architecture-document
version: 0.1.0
status: provisional
owners:
  - egohygiene
created: 2026-08-19
updated: 2026-11-09
governed_by:
  - architecture-decisions
depends_on:
  - observatory-principles
  - observatory-epistemology
  - observatory-foundations
  - observatory-system
  - observatory-architecture
related:
  - observatory-purpose
  - observatory-vision
  - observatory-pillars
  - observatory-manifesto
supersedes: []
---

# Observatory Decisions

## Purpose

This document preserves significant accepted architectural choices and their rationale. Issues coordinate work, proposals explore alternatives, and this file records decisions that constrain future implementation.

## Governance

Do not rewrite historical context to fit current understanding. Amend a record for corrections that do not change meaning; supersede it with a new record when the decision changes materially.

## Index

- ADR-0001: Keep observation separate from enforcement
- ADR-0002: Link every health signal to source evidence
- ADR-0003: Represent unknown and unavailable states explicitly
- ADR-0004: Derive read models from pinned Repository Intelligence projections
- ADR-0005: Version optional Search field attribution at its owner boundary
- ADR-0006: Expose bounded conformance evidence without inventing applicability

## ADR-0001: Keep observation separate from enforcement

- **Status:** Accepted as the current architectural direction
- **Date:** 2026-08-19
- **Context:** Repository evidence and ecosystem ownership require an explicit durable boundary.
- **Decision:** Keep observation separate from enforcement.
- **Consequences:** The choice improves ownership and predictability while requiring maintained contracts, validation, and migration discipline.
- **Reconsider when:** New evidence shows that the boundary prevents standalone usefulness, safety, portability, or maintainability.

## ADR-0002: Link every health signal to source evidence

- **Status:** Accepted as the current architectural direction
- **Date:** 2026-08-19
- **Context:** Repository evidence and ecosystem ownership require an explicit durable boundary.
- **Decision:** Link every health signal to source evidence.
- **Consequences:** The choice improves ownership and predictability while requiring maintained contracts, validation, and migration discipline.
- **Reconsider when:** New evidence shows that the boundary prevents standalone usefulness, safety, portability, or maintainability.

## ADR-0003: Represent unknown and unavailable states explicitly

- **Status:** Accepted as the current architectural direction
- **Date:** 2026-08-19
- **Context:** Repository evidence and ecosystem ownership require an explicit durable boundary.
- **Decision:** Represent unknown and unavailable states explicitly.
- **Consequences:** The choice improves ownership and predictability while requiring maintained contracts, validation, and migration discipline.
- **Reconsider when:** New evidence shows that the boundary prevents standalone usefulness, safety, portability, or maintainability.

## ADR-0004: Derive read models from pinned Repository Intelligence projections

- **Status:** Proposed for acceptance with issue #7
- **Date:** 2026-08-25
- **Context:** Roadmap, decision, journey, health, and delivery views need shared identity and provenance semantics, while Hygiene and Egolint already own the contract and validation boundary.
- **Decision:** Consume exact, validated Hygiene Repository Intelligence projections and derive deterministic repository, fleet, page, and comparison read models without live provider access. Keep the implementation dependency-free and the JSON interfaces framework-neutral for the alpha slice.
- **Consequences:** Relay and Holon can develop from offline fixtures and one stable query model. Observatory must maintain compatibility fixtures and explicit input pins, and it must not absorb collection, validation policy, rendering, or canonical source ownership.
- **Reconsider when:** Measured fleet scale requires a storage/query backend, the Hygiene contract changes incompatibly, or a second implementation can prove equivalent deterministic artifacts with a safer maintenance profile.

## ADR-0005: Version optional Search field attribution at its owner boundary

- **Status:** Proposed
- **Date:** 2026-11-09
- **Context:** Observatory #24 and Relay #102 need an explanation of every approved field participating in a Search match. The current alpha.2 aggregate is opaque, and rebuilding an index in Relay would duplicate normalization and authority semantics.
- **Decision:** Offer an explicitly enabled, independently versioned closed Search-field extension containing only title, key, kind, state and repository. Keep current alpha.2/default output unchanged. Bind the five normalized fields to the existing aggregate exactly and own both Python and portable JavaScript reference matching. Preserve unavailable attribution for older records rather than inferring it.
- **Consequences:** Consumers can pin the same owner representation and matching algorithm while retaining record order and existing substring semantics. The optional version freezes Unicode 14 default lowercase tables and trim semantics; the default opaque path remains unchanged. Adoption needs the helper/schema/contract pins and later cross-runtime fixtures; source preparation supplies no test, native execution or publication acceptance. No source authority, visibility, canonical state or collection coverage changes.
- **Reconsider when:** The approved search fields or matching semantics need a versioned change, a stable contract is accepted, or measured scale requires a different query representation.
- **References:** [Observatory #24](https://github.com/egohygiene/observatory/issues/24), [Relay #102](https://github.com/egohygiene/relay/issues/102), [contract and migration](docs/search-field-attribution.md).

## ADR-0006: Expose bounded conformance evidence without inventing applicability

- **Status:** Proposed
- **Date:** 2026-11-09
- **Context:** Observatory #5 and Relay #75 need repository-level contract evidence. Existing health/evidence models supply check identities, status, revision and freshness, while complete applicability and adoption inventories remain unavailable.
- **Decision:** Derive an optional repository conformance query from the existing owner health/evidence rules and an exact reviewed Hygiene public admission artifact. Keep whole contract inventory and applicability unknown, retain other-revision observations as context, and assess only supplied current-revision conformance checks. Publish a closed schema and standalone owner validator for renderers.
- **Consequences:** Repository Hygiene pages can show genuine evidence without pretending complete policy coverage or rerunning validators. Public wrappers and authenticated admission precede payload processing. Existing defaults and locks remain unchanged; fixture, package, consumer and publication qualification stay deferred. This introduces no exemption, ratification, enforcement or remediation authority.
- **Reconsider when:** Hygiene supplies a reviewed applicability/adoption model, producers expose richer compatible evidence, or a stable conformance contract is reviewed.
- **References:** [Observatory #5](https://github.com/egohygiene/observatory/issues/5), [Relay #75](https://github.com/egohygiene/relay/issues/75), [query contract](docs/repository-conformance-query.md).

## Open decisions

- Release and compatibility policy for the first stable version.
- Exact self-hosted, managed, and organization-integrated deployment boundaries.
- Which target systems must exist before the architecture status may become active.

## Evidence and uncertainty

- **Observed:** The repository README establishes the intended boundary as the organization-wide visibility, maturity, health, and platform-observability system; significant implementation remains incomplete.
- **Decided for this draft:** The repository owns the bounded concern described here and participates through versioned contracts.
- **Proposed:** Target systems and later roadmap phases remain proposals until accepted and implemented.
- **Open question:** Which parts of this draft should become active in the first independently versioned release?

## Identifier format migration (2026-10-18)

The maintainer selected four-digit numbering in [Hygiene #73](https://github.com/egohygiene/hygiene/issues/73). This padding-only migration changes current labels and anchors; logical numbers, decision content, dates and disposition remain unchanged. Git retains prior versions. New canonical records use `ADR-NNNN` under Hygiene policy v1.2.0.

| Previous ID | Current ID | Record |
| --- | --- | --- |
| `ADR-001` | `ADR-0001` | [DECISIONS.md](DECISIONS.md#adr-0001-keep-observation-separate-from-enforcement) |
| `ADR-002` | `ADR-0002` | [DECISIONS.md](DECISIONS.md#adr-0002-link-every-health-signal-to-source-evidence) |
| `ADR-003` | `ADR-0003` | [DECISIONS.md](DECISIONS.md#adr-0003-represent-unknown-and-unavailable-states-explicitly) |
| `ADR-004` | `ADR-0004` | [DECISIONS.md](DECISIONS.md#adr-0004-derive-read-models-from-pinned-repository-intelligence-projections) |
