---
schema: aether.architecture-document/v1
id: observatory-system
title: Observatory System
kind: architecture-document
version: 0.1.0
status: provisional
owners:
  - egohygiene
created: 2026-08-19
updated: 2026-08-19
governed_by:
  - architecture-system
depends_on:
  - observatory-foundations
  - observatory-ontology
related:
  - observatory-purpose
  - observatory-vision
  - observatory-principles
  - observatory-pillars
supersedes: []
---

# Observatory System

## Purpose and scope

This document identifies Observatory's logical systems and responsibilities. It answers what the major systems do; [ARCHITECTURE.md](ARCHITECTURE.md) owns their structural organization and dependency rules.

## System inventory

| System | State | Responsibility |
| --- | --- | --- |
| Repository registry adapter | Alpha | Defensively consumes Hygiene catalog v1 with an exact source URL, commit, and digest while leaving complete validation and vocabulary ownership in Hygiene. |
| Evidence collectors | Target | Owns its bounded portion of the organization-wide visibility, maturity, health, and platform-observability system; exposes explicit inputs, outputs, failure states, and evidence. |
| Normalization pipeline | Alpha | Consumes pinned Hygiene Repository Intelligence projections, rejects unsafe graph inputs, and emits deterministic repository and fleet snapshots. |
| Metric and maturity engine | Alpha | Computes transparent categorical maturity-evidence and conformance rollups from required checks while preserving declarations, stale data, unknowns, and detailed evidence. |
| Time-series store | Target | Owns its bounded portion of the organization-wide visibility, maturity, health, and platform-observability system; exposes explicit inputs, outputs, failure states, and evidence. |
| Dashboard and architecture landscape | Target | Owns its bounded portion of the organization-wide visibility, maturity, health, and platform-observability system; exposes explicit inputs, outputs, failure states, and evidence. |
| Report API | Alpha, static | Exposes versioned Roadmap, Decisions, Journey, Now, Dependencies, Health, Releases, Work, Search, and Compare JSON projections through the CLI and checked artifacts. |

## External systems

- Hygiene catalog
- Pace conformance
- GitHub and CI evidence
- Egolint reports
- Relay job summaries
- repository intelligence surfaces

External systems are integrations, not hidden implementation units. Each requires version, authentication, availability, data, error, and replacement boundaries appropriate to its risk.

## System interactions

Inputs enter through an adapter or validated contract, move through domain systems, produce artifacts and diagnostics, and leave through a stable interface. Evidence flows back to validation, review, and future decisions.

The current executable path is intentionally narrower:

```text
validated Hygiene projection
  → defensive consumer boundary
  → deterministic graph index
  → repository page queries
  → repository and fleet JSON artifacts
```

The parallel organization-health path is also executable:

```text
validated Hygiene catalog + versioned repository evidence
  → defensive catalog/evidence join
  → explicit freshness and categorical rollups
  → fleet JSON and Markdown artifacts
```

Egolint report v1 is the first validator adapter. Live GitHub collection,
time-series persistence, policy evaluation, dashboard rendering, and network
service delivery remain target systems.

## Failure model

Systems fail closed at destructive, publication, privacy, and security boundaries. Partial results identify coverage and remain distinguishable from complete success.

## Evidence and uncertainty

- **Observed:** The repository README establishes the intended boundary as the organization-wide visibility, maturity, health, and platform-observability system; significant implementation remains incomplete.
- **Decided for this draft:** The repository owns the bounded concern described here and participates through versioned contracts.
- **Proposed:** Target systems and later roadmap phases remain proposals until accepted and implemented.
- **Open question:** Which parts of this draft should become active in the first independently versioned release?
