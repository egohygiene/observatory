---
schema: aether.architecture-document/v1
id: observatory-architecture
title: Observatory Architecture
kind: architecture-document
version: 0.1.0
status: provisional
owners:
  - egohygiene
created: 2026-08-19
updated: 2026-08-19
governed_by:
  - architecture-architecture
depends_on:
  - observatory-foundations
  - observatory-system
related:
  - observatory-purpose
  - observatory-vision
  - observatory-principles
  - observatory-pillars
supersedes: []
---

# Observatory Architecture

## Purpose and scope

Observatory uses a layered, contract-driven architecture. This document owns structural boundaries, dependency direction, integration rules, and current-to-target evolution. Logical responsibilities remain canonical in [SYSTEM.md](SYSTEM.md).

## Layer model

1. **Intent and contracts** — identity, policy, specifications, schemas, and accepted decisions.
2. **Domain** — canonical concepts and pure domain behavior.
3. **Application** — planning, orchestration, use cases, and state transitions.
4. **Adapters** — filesystems, providers, frameworks, renderers, and external tools.
5. **Interfaces** — CLI, library, site, reports, generated artifacts, and automation contracts.
6. **Evidence** — tests, diagnostics, provenance, manifests, and health projections.

Dependencies point inward toward stable contracts and domain behavior. External details do not become canonical domain truth.

## Structural view

```mermaid
flowchart LR
  S1[Repository registry adapter]
  S2[Evidence collectors]
  S3[Normalization pipeline]
  S4[Metric and maturity engine]
  S5[Time-series store]
  S6[Dashboard and architecture landscape]
  S7[Report API]
  S1 --> S2
  S2 --> S3
  S3 --> S4
  S4 --> S5
  S5 --> S6
  S6 --> S7
```

The diagram is conceptual. [SYSTEM.md](SYSTEM.md) remains authoritative for responsibilities and implementation evidence determines current availability.

## Dependency rules

- Sibling domain capabilities integrate through versioned public contracts, not direct access to internals.
- Generated artifacts never become the canonical source unless an accepted decision explicitly changes ownership.
- Provider and platform adapters depend on application ports; core behavior does not depend on a provider implementation.
- Read, plan, apply, verify, publish, and recover remain separate authority boundaries when consequential.
- Cross-repository references use releases, immutable commits, schemas, packages, or documented APIs rather than mutable default-branch assumptions.

## Ecosystem interfaces

- Hygiene catalog
- Pace conformance
- GitHub and CI evidence
- Egolint reports
- Relay job summaries
- repository intelligence surfaces

## Current executable slices

Issue #7 implements the first provider-neutral data path under `src/observatory`:

```mermaid
flowchart LR
  H[Hygiene v1 projection] --> B[Defensive consumer boundary]
  B --> N[Deterministic graph normalization]
  N --> R[Repository read model]
  R --> V[Page query projections]
  R --> F[Fleet snapshot]
  R --> C[Before/after comparison]
  V --> X[Relay and Holon fixtures]
  F --> X
```

The implementation has no provider or database dependency. Filesystem I/O and CLI parsing remain adapters around pure transformation functions. The graph and query contracts are JSON, so a later storage engine or service can replace the Python process without changing identity or authority semantics.

Full Hygiene/Egolint validation precedes this boundary. Observatory performs only the defensive checks required to index safely; it does not import the validation implementation or vocabulary ownership.

Issue #1 adds the first organization-health path alongside that graph:

```mermaid
flowchart LR
  C[Hygiene catalog v1] --> J[Evidence join]
  E[Versioned repository evidence] --> J
  G[Egolint report v1] --> A[Egolint adapter]
  A --> E
  J --> M[Categorical rollups]
  M --> O[JSON and Markdown snapshots]
```

The collector supplies explicit source pins, evidence validity, and evaluation
time. Observatory never reads the ambient clock, picks among competing check
identities, reruns validator policy, or mutates a repository. The future #5
dashboard consumes this boundary rather than defining another conformance
model.

## Deployment and portability

The architecture favors independently usable local and self-hosted operation. Optional managed services may add availability, collaboration, support, and hosted infrastructure without becoming the canonical holder of portable state.

## Evidence and uncertainty

- **Observed:** The repository README establishes the intended boundary as the organization-wide visibility, maturity, health, and platform-observability system; significant implementation remains incomplete.
- **Decided for this draft:** The repository owns the bounded concern described here and participates through versioned contracts.
- **Proposed:** Target systems and later roadmap phases remain proposals until accepted and implemented.
- **Open question:** Which parts of this draft should become active in the first independently versioned release?
