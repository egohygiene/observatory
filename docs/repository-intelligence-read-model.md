# Repository Intelligence read-model contract

- Repository schema: `egohygiene.observatory.repository-intelligence-read-model/v1`
- Fleet schema: `egohygiene.observatory.repository-intelligence-fleet/v1`
- View schema: `egohygiene.observatory.repository-intelligence-view/v1`
- Compare schema: `egohygiene.observatory.repository-intelligence-compare/v1`
- Contract version: `1.0.0-alpha.2`
- Owner: `egohygiene/observatory`
- Upstream: `egohygiene.repository-intelligence/v1` at exact `1.0.0-alpha.1` or `1.0.0-alpha.2`

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

Observatory accepts exactly alpha.1 (legacy) and alpha.2 (explicit collection
coverage). The existing [alpha.1 lock](../contracts/hygiene.repository-intelligence.v1.lock.json)
remains unchanged. The [alpha.2 lock](../contracts/hygiene.repository-intelligence.alpha2.lock.json)
pins the Hygiene schema, vocabulary, reference validator, and all eight coverage
fixtures. Other input versions fail closed.

Alpha.1 retains all existing graph content, but each domain becomes
`unavailable / unknown / legacy_unspecified` with a null observation time.
Neither a "complete quest" fixture name nor positive graph records establishes
collection completeness. Alpha.2 requires explicit coverage and rejects
contradictions, missing domains, unexpected fields, and unsupported states.

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
| `coverage` | Record counts, assertion/freshness distributions, `record_status`, and separate per-domain collection claims in `domains`. |
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

`coverage.record_status` describes existing records only:

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
| Now | Canonically active roadmap focus, explicit `blocks` edges, at most three inferred ready steps, five recent events, record freshness, and explicit domain collection coverage. Dependency edges are not mislabeled as blockers. |
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

Fleet and extracted-view envelopes carry visibility. Mixed-visibility fleet inputs fail closed. Search retains per-repository collection coverage alongside its flattened records. All other fleet views retain coverage within each repository group. No denied or undiscovered repository placeholders or counts are invented.

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

## Collection coverage and renderer boundary (alpha.2)

The [migration guide](collection-coverage-migration.md) pins the Hygiene-owned
meaning of each domain and collection state. A repository snapshot preserves
all nine entries at `coverage.domains`; every page's data contains
`collection_coverage` for the domains relevant to that query:

| View | Required collection domains |
| --- | --- |
| Roadmap | roadmap |
| Decisions | decisions |
| Journey | history |
| Health | checks |
| Releases | releases, deployments |
| Work | roadmap, issues, pull_requests |
| Now, Dependencies, Search | all nine |

Coverage describes the root repository's inventory. Contextual external graph
nodes are not a complete inventory of their repositories. Primary view coverage
does not certify the completeness of secondary evidence links on its cards.
Inventory and lifecycle history are independent, so an empty Journey never
becomes not-applicable merely because no events were collected.

Render the fixed collection claim before interpreting an empty list. A missing
field is a contract error. `partial`, `unavailable`, `uncollected`, and `failed`
do not mean zero. `observed_empty` means the declared complete collection found
no records, with its separate freshness and observation time. Only an explicit
`not_applicable` claim establishes that state. The Work query lists **open**
records, while its coverage describes the whole issue/PR inventory; a fully
collected inventory containing only closed issues legitimately has no open issues.

`coverage.record_status` replaces the ambiguous alpha.1 `coverage.status`.
`now.record_freshness_status` replaces `now.coverage_status`; fleet aggregate
`record_states` replaces `states`. These report record freshness/assertion only,
never collection completeness or conformance. Health continues to emit no score.

All repository, view, fleet, and compare outputs are now exact alpha.2. Query,
compare, and fleet composition reject alpha.1 snapshots; rebuild them from their
original projections to migrate. Saved views must preserve their repository's
coverage, so removing or upgrading a claim fails closed. Old exact-version
consumers must reject these outputs until repinned. This is intentionally not an
optional field an older renderer can safely ignore.
