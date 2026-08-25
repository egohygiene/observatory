# Repository Intelligence read-model contract

- Repository schema: `egohygiene.observatory.repository-intelligence-read-model/v1`
- Fleet schema: `egohygiene.observatory.repository-intelligence-fleet/v1`
- View schema: `egohygiene.observatory.repository-intelligence-view/v1`
- Compare schema: `egohygiene.observatory.repository-intelligence-compare/v1`
- Contract version: `1.0.0-alpha.1`
- Owner: `egohygiene/observatory`
- Upstream: `egohygiene.repository-intelligence/v1` at `1.0.0-alpha.1`

## Purpose and authority

This contract is Observatory's deterministic query layer over a validated Hygiene Repository Intelligence projection. It exists so Holon components and Relay workflows can consume one stable read model instead of independently interpreting roadmap, ADR, Git, GitHub, check, release, and deployment records.

The read model is generated evidence, never canonical truth. Authority remains with the sources identified by Hygiene:

- `ROADMAP.md` owns intent and canonical step state;
- ADR Markdown owns decisions and lineage;
- Git owns commits;
- GitHub owns issue and pull-request state;
- check, release, and deployment providers own their records;
- Hygiene owns graph identity, relationship, freshness, assertion, visibility, and compatibility semantics;
- Egolint owns semantic validation; and
- Observatory owns deterministic indexing, queries, comparisons, and fleet composition.

Observatory does not fetch provider data in this slice. Relay or another approved collector supplies a pinned projection.

### Relationship to Observatory #1 and #5

Issue #7 supplies the shared graph, deterministic query layer, and offline fixtures. It deliberately extends the other Observatory outcomes:

- issue #1 remains responsible for ingesting the Hygiene catalog and real repository evidence, then adding transparent maturity and conformance calculations; and
- issue #5 remains responsible for the conformance-specific read model and organization/per-repository presentation.

Those issues can attach conformance evidence to this graph and Health view through a versioned extension. They do not need a second entity identity, provenance, freshness, fleet, or page-query implementation. This slice does not claim that live collection, maturity calculations, or the conformance dashboard already exist.

## Input boundary

Observatory currently accepts only:

```json
{
  "schema": "egohygiene.repository-intelligence/v1",
  "contract_version": "1.0.0-alpha.1"
}
```

The exact Hygiene source revision and SHA-256 values are recorded in [`contracts/hygiene.repository-intelligence.v1.lock.json`](../contracts/hygiene.repository-intelligence.v1.lock.json). Alpha consumers fail closed on any other version.

Hygiene and Egolint perform complete schema and semantic validation. Observatory additionally defends its query boundary against:

- unsupported contract versions;
- invalid root repository identity;
- duplicate source, entity, relationship, or event IDs;
- dangling relationship endpoints or event subjects;
- dangling or empty provenance; and
- non-absolute source and entity links.

These checks make a graph safe to index. They do not redefine the Hygiene vocabulary or claim policy conformance.

## Repository snapshot

One repository snapshot contains:

| Field | Meaning |
| --- | --- |
| `snapshot_id` | Root repository and represented commit. |
| `repository` | Compact repository entity reference. |
| `represented_commit` | Exact commit represented by the input projection. |
| `observed_at` | Collector-supplied observation time; never the build wall clock. |
| `upstream` | Exact Hygiene schema, version, projection ID, and canonical JSON digest. |
| `coverage` | Counts plus explicit assertion and freshness distributions. |
| `graph` | Deterministically ordered sources, entities, relationships, events, redactions, and extensions. |
| `views` | Renderer-ready queries derived from the same graph. |

Sources, entities, and relationships sort by stable ID. Events sort by occurrence time and then ID. Redactions sort by field and reason. JSON uses sorted keys, two-space indentation, UTF-8, and a final newline.

No generator timestamp exists. Rebuilding the same semantic projection produces byte-identical output.

## Assertion, confidence, and freshness

Observatory preserves the Hygiene categorical states:

- assertion and categorical confidence: `authoritative`, `inferred`, or `unknown`;
- freshness: `current`, `stale`, `unknown`, or `not_applicable`; and
- canonical entity state as reported by the owning source.

`confidence` is the preserved categorical assertion boundary, not a numeric probability. Observatory does not manufacture precision from missing evidence.

Coverage becomes:

1. `unknown` when any indexed claim has unknown freshness or assertion;
2. `stale` when evidence is known but at least one claim is stale;
3. `current` when current evidence exists and neither prior condition applies; or
4. `not_applicable` when every indexed record is explicitly not applicable.

This order is a transparent query rule, not a health score. The Health view intentionally emits `score: null`.

## Initial page queries

All views use global entity IDs and preserve canonical URLs. Repeated compact entity references let a renderer show useful content without live lookups; the complete graph remains available for deeper expansion.

| View | Query semantics |
| --- | --- |
| Roadmap | Roadmap steps, outcomes, exit criteria, prerequisites, blockers, coordinating work, informing decisions, evidence, verification, roots, and inferred readiness. |
| Decisions | ADR state and implementation status with informs, supersedes, superseded-by, tracking, evidence, and verification lineage. |
| Journey | Ordered lifecycle events grouped into human-scale chapters at release boundaries. Events after the latest release form a separate current chapter. |
| Now | Canonically active roadmap focus, explicit `blocks` edges, at most three inferred ready steps, five recent events, and coverage state. Dependency edges are not mislabeled as blockers. |
| Dependencies | Directed `depends-on` and `blocks` relationships with assertion, freshness, provenance, both endpoint references, and external repository names. |
| Health | Check entities, check-state counts, assertion/freshness distributions, and explicit stale/unknown IDs. No opaque score is calculated. |
| Releases | Releases, included entities, deployments, and release boundary events. |
| Work | Open issues and pull requests plus active, ready, waiting, blocked, and unknown roadmap queues. |
| Search | Stable entity records and a normalized search string formed only from already-publishable title, key, kind, state, and repository fields. |
| Compare | Separate two-snapshot query listing added, removed, and field-changed entities, relationships, and events plus per-view content digests. |

### Readiness

Readiness is always labeled `inferred`:

1. canonical `complete` remains complete;
2. a canonical blocked state or incoming `blocks` edge is blocked;
3. unknown state assertion, freshness, or prerequisite evidence is unknown;
4. an incomplete prerequisite is waiting;
5. canonical active remains active;
6. planned or ready with all prerequisites complete becomes ready; and
7. every other canonical state is preserved.

Observatory never changes canonical roadmap state or treats commit count as progress.

### Journey chapters

Events stay in canonical chronological order. Each `release.published` event closes a `Through <release>` chapter. Later events form `After <release>`. A history without a release forms one `Unreleased history` chapter. This grouping is disposable presentation structure; events and release records remain authoritative.

### Compare

Compare accepts snapshots for the same repository. It reports structural change, not causality. A changed title after a new represented commit is a title change; Observatory does not claim which commit caused it unless the graph provides an explicit relationship.

## Fleet snapshot

The fleet snapshot sorts repository snapshots by canonical repository name and records each repository's snapshot digest, represented commit, observation time, and coverage. Page views remain grouped by repository so organization aggregation does not flatten local context.

The fleet observation window reports the earliest and latest collector-supplied observation times. It is not a new observation and does not imply every repository was collected simultaneously.

Duplicate repository snapshots fail closed. Selecting among competing observations is a collector or orchestration decision, not an implicit "newest wins" rule inside Observatory.

## Privacy and trust

Observatory does not increase visibility. It preserves the snapshot visibility, redactions, nullable titles, actor fields, and source links it receives. It never loads linked URLs, reads provider tokens, or queries private records during normalization.

Public collection and redaction happen before Observatory. Unknown visibility must fail closed in the owning collector or validator. Renderers must continue to treat every title and extension as hostile display input.

## Compatibility

While alpha:

- consumers pin the exact schema and contract version;
- stable identity, authority, freshness, visibility, readiness meaning, or view shape changes require a reviewed version change;
- additive fields are compatible only when older consumers can ignore them safely;
- golden fixtures demonstrate current output; and
- the Hygiene input lock changes only through an explicit compatibility review.

The checked-in complete quest traces roadmap step → ADR → issue and pull request → commit and check → release and deployment. The active Observatory fixture demonstrates stale, inferred, unknown, blocked, and cross-repository dependency states without live access.
