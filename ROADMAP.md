---
schema: aether.architecture-document/v1
id: observatory-roadmap
title: Observatory Roadmap
kind: architecture-document
version: 0.1.0
status: provisional
owners:
  - egohygiene
created: 2026-08-19
updated: 2026-08-25
governed_by:
  - architecture-roadmap
depends_on:
  - observatory-vision
  - observatory-pillars
  - observatory-architecture
  - observatory-decisions
related:
  - observatory-purpose
  - observatory-principles
  - observatory-manifesto
  - observatory-epistemology
supersedes: []
---

# Observatory Roadmap

<!-- BEGIN ROADMAP EXECUTION SNAPSHOT -->
<!-- roadmap-manifest
schema: hygiene.roadmap/v1alpha1
repository: egohygiene/observatory
visibility: public
publication: central
route: /roadmap/observatory/
updated: 2026-08-25
-->
## 2026-08-25 execution snapshot

> This evidence-reconciled snapshot is the issue-generation and visual-roadmap handoff. The longer-horizon strategy below remains canonical context; generated HTML, JSON, progress, issue plans, and commit lists are projections.

**Lifecycle:** seed, executable alpha
**Current gate:** Review and merge issue #1's deterministic catalog/evidence health snapshot, then design live GitHub collection without weakening the offline boundary.
**North-star outcome:** Evidence-linked portfolio, maturity, dependency, and roadmap views across the organization.

### Visual roadmap publication

**Mode:** `central`  
**Route:** `/roadmap/observatory/`  
**Current publication evidence:** Versioned static artifacts and CI exist; no Pages route or release publication is claimed.

Publish the public-safe projection through egohygiene.io at /roadmap/observatory/. This repository owns intent and acceptance evidence; it does not add a second site deployment.

### Quest line

<!-- roadmap-step
id: OBS-Q01
status: complete
depends_on: []
issues: []
-->
#### OBS-Q01 — Define the observability architecture

**State:** `complete`  
**Depends on:** None

**Outcome:** The repository documents its intended portfolio-observability role.

**Exit criteria:**

- [x] Architecture and ownership boundaries are recorded.
- [x] The intended inputs and views are named.

**Current evidence:**

- Architecture merge 1d97773d5169 was observed.

<!-- roadmap-step
id: OBS-Q02
status: active
depends_on: [OBS-Q01]
issues: [1, 7]
-->
#### OBS-Q02 — Build the executable foundation

**State:** `active`  
**Depends on:** `OBS-Q01`

**Outcome:** Issues #1 and #7 produce runnable ingestion and a minimal evidence/read model without live provider coupling.

**Exit criteria:**

- [x] A command ingests deterministic Repository Intelligence fixtures.
- [x] Tests validate repository, fleet, query, and comparison results.
- [x] Issue #1 connects the model to the first approved real evidence collection path.

**Current evidence:**

- Issue #7 provides the versioned graph/read model, nine page queries, comparison, offline fixtures, and CI contract checks.
- Issue #1 adds pinned Hygiene catalog ingestion, a provider-neutral evidence contract, an Egolint v1 adapter, transparent categorical rollups, and JSON/Markdown snapshots.

<!-- roadmap-step
id: OBS-Q03
status: planned
depends_on: [OBS-Q02]
issues: []
-->
#### OBS-Q03 — Ingest live GitHub evidence safely

**State:** `planned`  
**Depends on:** `OBS-Q02`

**Outcome:** Issues, PRs, commits, releases, workflows, and publication state become normalized evidence records.

**Exit criteria:**

- [ ] Pagination, rate limits, and unavailable private evidence are handled explicitly.
- [ ] Every record retains repository, timestamp, and immutable source identity where available.

**Current evidence:**

- No GitHub ingestion implementation was observed.

<!-- roadmap-step
id: OBS-Q04
status: planned
depends_on: [OBS-Q03]
issues: []
-->
#### OBS-Q04 — Compute gates without commit-count progress

**State:** `planned`  
**Depends on:** `OBS-Q03`

**Outcome:** Lifecycle and quest state derive from acceptance evidence and declared rules.

**Exit criteria:**

- [ ] State transitions cite the evidence and rule used.
- [ ] Commit volume is never treated as completion percentage.

**Current evidence:**

- The audit identified the need for evidence-linked rather than activity-linked maturity.

<!-- roadmap-step
id: OBS-Q05
status: planned
depends_on: [OBS-Q04]
issues: []
-->
#### OBS-Q05 — Publish portfolio and quest views

**State:** `planned`  
**Depends on:** `OBS-Q04`

**Outcome:** A tested static or web surface provides portfolio, dependency, maturity, and quest-line views.

**Exit criteria:**

- [ ] The view deep-links to public evidence and sanitizes private entries.
- [ ] CI and Pages or equivalent publication are green.

**Current evidence:**

- No UI, CI, or Pages deployment was observed.

### Roadmap-to-issue handoff

- A step is complete only when its exit criteria and required evidence are satisfied; commit count never determines progress.
- Ready steps without an issue are candidates for the private, duplicate-aware roadmap.issue-plan.json dry run. Planned steps remain preview-only unless a reviewer explicitly opts them in with issue_policy: propose.
- Issue creation or reconciliation requires human approval or an explicitly authorized Pace operation and returns issue references through a reviewable roadmap pull request.
- Pull requests and commits should include Roadmap-Step: <ID>; historical evidence may be linked through existing issue and pull-request relationships.
- Public rendering uses only allowlisted build-time evidence and never places a GitHub token or private issue plan in the browser artifact.

<!-- END ROADMAP EXECUTION SNAPSHOT -->

## Strategic context

This roadmap describes capability evolution, not promised dates or an issue queue. Sequence follows architecture dependencies and may change when evidence or risk changes.

## Phase 1: Define evidence and metric schemas

**Outcome:** A bounded capability advances from documented intent to validated, independently usable behavior.

**Exit signals:**

- The owning contract and acceptance criteria are versioned.
- Implementation and documentation agree.
- Relevant tests and safety checks pass.
- Downstream consumers and migration impact are understood.
- Remaining uncertainty is visible.

## Phase 2: Ingest repository health snapshots

**Outcome:** A bounded capability advances from documented intent to validated, independently usable behavior.

**Exit signals:**

- The owning contract and acceptance criteria are versioned.
- Implementation and documentation agree.
- Relevant tests and safety checks pass.
- Downstream consumers and migration impact are understood.
- Remaining uncertainty is visible.

## Phase 3: Publish the organization landscape

**Outcome:** A bounded capability advances from documented intent to validated, independently usable behavior.

**Exit signals:**

- The owning contract and acceptance criteria are versioned.
- Implementation and documentation agree.
- Relevant tests and safety checks pass.
- Downstream consumers and migration impact are understood.
- Remaining uncertainty is visible.

## Phase 4: Add trends and maturity views

**Outcome:** A bounded capability advances from documented intent to validated, independently usable behavior.

**Exit signals:**

- The owning contract and acceptance criteria are versioned.
- Implementation and documentation agree.
- Relevant tests and safety checks pass.
- Downstream consumers and migration impact are understood.
- Remaining uncertainty is visible.

## Phase 5: Support bounded alerts and planning

**Outcome:** A bounded capability advances from documented intent to validated, independently usable behavior.

**Exit signals:**

- The owning contract and acceptance criteria are versioned.
- Implementation and documentation agree.
- Relevant tests and safety checks pass.
- Downstream consumers and migration impact are understood.
- Remaining uncertainty is visible.

## Cross-cutting tracks

- Security, privacy, accessibility, licensing, and provenance.
- Documentation, architecture portals, examples, and onboarding.
- Packaging, release, compatibility, and self-hosting.
- Organization integration through explicit contracts.
- Observatory evidence and Pace conformance when those systems exist.

## Deferred direction

Optional managed services, enterprise controls, marketplaces, and the conversational organization compiler remain later architecture work. Current choices should preserve portability and avoid foreclosing them.

## Evidence and uncertainty

- **Observed:** The repository README establishes the intended boundary as the organization-wide visibility, maturity, health, and platform-observability system; significant implementation remains incomplete.
- **Decided for this draft:** The repository owns the bounded concern described here and participates through versioned contracts.
- **Proposed:** Target systems and later roadmap phases remain proposals until accepted and implemented.
- **Open question:** Which parts of this draft should become active in the first independently versioned release?
