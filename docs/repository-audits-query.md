# Public repository and fleet Audits queries

This optional owner boundary implements Observatory #20 alongside the existing
Intelligence and conformance contracts. It does not extend alpha.2 views,
coverage keys, defaults or locks. The separate alpha.1 contracts are
`egohygiene.observatory.repository-audits/v1` and
`egohygiene.observatory.fleet-audits/v1`.

## Source and authority

Inputs are Aether's typed `aether.repository-audit-report/v1` sidecars and exact
versioned profile registry, validated by the immutable standard-library owner
helper. The byte lock and packaged mirrors record every source path, revision
and digest. Arbitrary audit Markdown and the old Reflector AuditReport are not
adapters for this contract. No auditor, validator, provider or AI is executed.

The exact reviewed Hygiene public catalog already packaged for conformance
authenticates targets and every referenced repository. Public wrappers and the
entire report scope/source ownership are admitted before report identities,
prose validation, counts or hashes. A mixed organization report with a protected
member is excluded as a whole. A bounded recursive ownership preflight also
checks repository tokens and URLs in narrative fields before whole-input hashes.
No excluded count, name, failure placeholder or raw mixed-inventory digest is
published. Malformed selected public data denies the candidate; missing evidence
stays unavailable. All output links and metadata remain bounded public data.

Wrappers have `visibility`, `repository`, `evidence` and optional `source`.
`evidence` may be a structured owner object or exact raw JSON bytes/string.
The latter receives a verified byte digest; structured input has
`raw_input_sha256: null`. Canonical transport JSON and Aether's newline-terminated
semantic digest are named separately. Optional `source` binds the JSON artifact's
repository, revision, path, exact GitHub blob URL and declared SHA-256. Its digest
is verified against raw input when available; a structured-input digest remains
an unverified claim. This never proves remote fetch, report execution or human
approval. Canonical Markdown remains at `run.source.canonical_report`.

## Repository and fleet APIs

`build_repository_audits(wrappers, repository=..., represented_commit=...,
as_of=..., admission_root=..., maximum_age_seconds=...)` returns one model.
`build_fleet_audits(wrappers, repositories=[{repository, represented_commit}],
as_of=..., ...)` returns a separate fleet model containing full repository
queries. Fleet selectors are explicitly supplied; unadmitted selectors disappear
before revisions, duplicates, counts or lookup. The complete public catalog is
not an inferred target or audit-completion inventory.

`audits_contract.parse`, `validate`, `validate_fleet`, `digest`, `instant` and
`admission` are standard-library owner APIs suitable for exact Relay vendoring.
The validator depends on its adjacent `public_reviews.py`, existing unchanged
`conformance_contract.py`, exact packaged public JSON, owner lock and four Aether
resources. Schemas remain independently consumable by the central fleet host.

The CLI `observatory-audits repository` takes explicit repository/SHA/as-of,
repeated `--evidence` JSON wrapper files and a new `--output` path. The `fleet`
subcommand takes an explicit `--targets` selector array instead of one repository.
There is no ambient clock, network, discovery, source crawl or overwrite.

## Meaning and boundaries

Runs retain scope/exclusions, exact profile selection, source/completion clocks,
completion state, reported producer/command states and source references.
Original completion and effective freshness are separate. An incomplete run is
not a clean audit, and a complete run never means conformance or ratification.
The explicit maximum age defaults to thirty days; unknown completion keeps
freshness unknown. Other-revision runs remain labeled context.

Findings retain source classification, nature, severity, confidence, status,
effort/impact, area, evidence labels, profile/version and explicit history.
Opportunities and experiments stay separate from defects/conformance drift;
experimental observations retain the owner's informational severity. Resolution
and recurrence claims are projected only from explicit source history/evidence.
Absence from a later input never resolves an earlier finding.

Candidate issues remain suggested proposals with materialization unavailable.
Repository subsets of cross-repository proposals are explicitly labeled.
Summary counts use repository-report projections, not unique campaign runs or
an organization score. Latest-by-profile retains ties rather than arbitrarily
picking one source. The base repository model's campaign field remains
unavailable. Separate [campaign, pattern and comparison models](audit-campaigns-and-queries.md)
now accept explicit typed source inputs without changing that default or
scraping or inventing records.

## Source checkpoint and qualification

Prepared from Observatory main
`2eebdb63c3239cbb790be4146df5340c7ad59c17` on
`codex/intelligence-audits-sanity-20261110`. Root coordinates final Aether pins,
shared continuity, publishing and consumer wiring. Existing Search, health,
conformance and their golden/default behavior are preserved.

The user deferred tests, runtime/native execution, fixtures, package builds,
CI, provider/browser/publication and acceptance checks. Only static Python,
schema, package-data, exact-source digest and source peer inspection is in
scope. No audit completion, real issue materialization, policy acceptance,
human ratification or live surface is established by this source checkpoint.

Refs [Observatory #20](https://github.com/egohygiene/observatory/issues/20) and
[organization #41](https://github.com/egohygiene/.github/issues/41).
