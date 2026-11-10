# Public repository and fleet Sanity queries

Refs [Observatory #21](https://github.com/egohygiene/observatory/issues/21).
These optional alpha.1 models are separate from existing Intelligence alpha.2,
Search, Health and conformance outputs. No old default, coverage domain or lock
is changed. The contracts are
`egohygiene.observatory.repository-sanity/v1` and
`egohygiene.observatory.fleet-sanity/v1`.

## Owners and exact source

The packaged byte lock selects Aether
`74490907bf3979ac45594d97fb1bb5fa7071346d`, its standalone review validator,
closed review schema and exact adjacent Hygiene governance resources. The
Aether helper loads Hygiene `d11580e9a9c5d78b9a5d21474deaa612712a0fb9`
through its byte-pinned cache. Hygiene owns applicability and freshness;
Aether owns assessment semantics. Observatory owns this bounded read model,
not an architecture assessment, policy, prompt or human-verification service.

The existing exact Hygiene public artifact `49639c1` / `af9c7186…` authenticates
each selected repository and all source ownership. Declared public wrappers,
the complete review scope and all referenced owners are admitted before source
IDs, prose validation, counts and hashes. A bounded recursive preflight excludes
protected names, scopes, source links and nested visibility. Mixed protected
organization scope is omitted entirely. Unknown selectors never create private
placeholders or counts. A public organization review covers its explicit
admitted members and does not imply coverage of private organization topology.

## Input and APIs

`build_repository_sanity(wrappers, repository=..., represented_commit=...,
as_of=..., admission_root=..., governance_wrappers=(), material_changes=(),
change_inventory="unknown")` accepts typed Aether review documents.
`build_fleet_sanity(wrappers, repositories=[{repository, represented_commit}],
as_of=..., ...)` selects an explicit public roster and returns full repository
queries. It never discovers a fleet or infers membership from a report.

Both review and independent-governance wrappers are
`{visibility, repository, evidence}` with an optional `source` artifact binding.
`evidence` can be a structured object or exact raw JSON string/bytes. Raw input
receives `raw_input_sha256`; structured input retains `null` there. Canonical
transport hashes, original raw byte hashes and Aether assessment hashes are
distinct. Optional artifact metadata binds repository/revision/path/exact GitHub
blob URL and declared SHA256. It is `verified-input-bytes` only when raw bytes
actually match, otherwise an explicit `unverified-claim`. No remote fetch or
actor authenticity is inferred.

`governance_wrappers` can carry a typed Hygiene declaration before the first
completed assessment, supporting unknown applicability, review-due or
in-progress. Its review reference must be null; completed-review dispositions
must instead accompany the actual matching Aether assessment. It is not a
second authored assessment or a fabricated absence record.

`material_changes` is an explicit list of Hygiene material-change sources,
filtered by admitted scope and exact review ID. A null review ID applies before
the first completed review. `change_inventory` is separately declared as
unknown, partial, complete or unavailable; empty events never prove complete
capture. No commit volume, changed filename or arbitrary source age determines
materiality. Source expiry and material events are evaluated by Hygiene with
the caller's explicit UTC `as_of`. Other current repository revisions are not
invented for organization reviews; target revision matching remains explicit.

The `observatory-sanity repository` CLI takes repository/SHA/as-of, repeated
`--evidence`, optional repeated `--governance` and `--material-changes` files,
`--change-inventory`, and a new `--output` path. `fleet` instead takes a
`--targets` selector array. It performs no scan, network, AI review, mutation,
overwrite or ambient clock read. The contract's `parse`, `validate`,
`validate_fleet`, `digest`, `instant` and `admission` are standalone standard
library APIs suitable for pinned downstream validation.

## Projection and human authority

Each `reviews[]` record retains source scope/revisions, reviewer and execution
metadata, exact source references, completion/generated time, revision context,
assessment metadata and source-input provenance. `assessment.explanation_summary`
is exactly the source's explanation summary. The full system/boundary/flow/
rationale prose and concern detail are not copied. Structured components,
relationships, dimensions, assumptions, strengths, concern summaries, questions,
alternatives and recommendation remain separate owner fields with evidence.

The original `assessment_sha256` remains source provenance. It cannot be
recomputed from a deliberately smaller projection. The standalone validator
uses deterministic placeholder narrative only to apply exact pinned owner
shape/reference rules to preserved fields; it never publishes that temporary
value or claims original-source replay equivalence. Source artifact verification
and the original digest remain separate facts.

`governance_source` preserves the typed public source claim. `governance` is the
exact pinned Hygiene evaluation with **empty trusted human context**. This
serializable model has no parameter or JSON field that creates
`TrustedHumanEvidence`. Raw authority strings, claimed approval URLs, AI
recommendations and serialized verified markers cannot ratify an architecture.
The validator recomputes the owner evaluation and rejects such promotion.

Effective human disposition is always null in this first JSON adapter.
Claimed dispositions remain visible as unverified. An unverified exemption or
deferral cannot become effective applicability. Schema enums reject verified
human evidence and effective ratified/rejected/not-applicable/deferral states
that this empty-trust adapter cannot produce. Material staleness remains visible
as freshness and review-due rather than erasing the historical claim. A genuine
human-source adapter requires separate typed provenance and a reviewed version.

The top `human_state` is the one shared governance state across current-target
revision records, `mixed` for differing states or `unavailable` when none exist.
`human_evidence` is `unverified` if current records contain human/applicability
claims, otherwise `absent`. Historical reviews retain their own context and
cannot set current posture. AI recommendation never determines human state.

## Counts, queries and compatibility

Summary counts use repository-review projections, not unique organization
reviews or a quality score. Current and other-revision review counts, strengths,
concerns, questions and governance states are separate. Queries preserve latest
completion/generated-time ties, explicit due/stale context and unverified human
claim IDs. They do not auto-resolve questions or infer acceptance from activity.

Fleet models contain explicit selected repository entries with the same as-of
boundary and a selected public admission digest. Missing public evidence stays
unavailable; no raw hidden input digest or exclusion total is emitted. Schemas
are standalone with embedded owner definitions and local references, allowing a
central fleet host to validate the same owner state without inventing a model.

The byte capsule, source, metadata and schema were statically inspected only.
Tests, fixtures, runtime/native evaluation, package builds, CI, provider capture,
browser/publication qualification, human verification and actual ratification
remain deferred. No source merge establishes those acceptance outcomes.
