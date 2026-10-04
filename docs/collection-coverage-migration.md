# Collection coverage migration for Relay

A roadmap-only collection must show “not checked” for Decisions, Journey, Health,
Releases, and provider Work. Observatory #25 adds this information to the
existing CLI output; it does not add a service or collect providers.

The input meaning belongs to Hygiene's proposed alpha.2 contract. Its immutable
revision and schema/fixture digests are in
[`hygiene.repository-intelligence.alpha2.lock.json`](../contracts/hygiene.repository-intelligence.alpha2.lock.json).
The existing alpha.1 lock is retained separately. The new schema is a candidate
until [Hygiene PR #67](https://github.com/egohygiene/hygiene/pull/67) is merged; this consumer must be reviewed with that dependency.

## Changes a renderer must consume

Read `data.collection_coverage` in a repository view envelope (or the corresponding
`views.<name>.collection_coverage` in a repository snapshot). For fleet views,
read it inside each `repositories[].data`. Fleet Search instead has
`collection_coverage[]` entries with `repository` and `domains`, alongside its
flattened record list. Repository metadata also retains all nine claims at
`repositories[].coverage.domains`. Do not flatten them into an organization-wide
claim that every repository was checked. Protected repositories are filtered
before collection, never represented as named or counted denied placeholders.

| Collection | Suggested label |
| --- | --- |
| uncollected | Not checked |
| unavailable | Unavailable (legacy_unspecified: Collection coverage unknown) |
| partial | Partially checked |
| observed_empty | Checked; no records found |
| observed | Checked |
| failed | Collection failed |
| not_applicable | Not applicable |

Always retain the separate freshness and observation time; append “stale” when
appropriate. These are display labels, not new provider semantics. A Work view
can have no open issues while `issues.collection` is `observed` because its
complete inventory contains closed issues. A zero-open-issues assertion requires
current, complete, authorized issue inventory (`observed` or `observed_empty`);
filtered, truncated, denied, old, or uncollected inputs cannot establish it.
This change implements no achievement rules.

`coverage.status`, `now.coverage_status`, and fleet `coverage.states` become
`coverage.record_status`, `now.record_freshness_status`, and `coverage.record_states`.
Those fields describe indexed record freshness/assertion, never collection or
conformance. The Health score remains null. An empty array never establishes
applicability. A roadmap's authored `issue_references` stay references, without
fabricated issue nodes or provider state.

## Repin order for Relay #112 / #113

1. Review and merge the Hygiene contract dependency, retaining its proposed
   lifecycle until the owner separately ratifies it. Select an eligible immutable
   revision whose locked artifacts match the checked-in SHA-256 values.
2. Update the EgoLint production validator to accept the exact alpha.2 contract
   and enforce these coverage semantics. Current alpha.1-only validation must
   continue to reject alpha.2 until that owner change is delivered; do not bypass
   EgoLint or relabel payload versions. This Observatory PR does not implement it.
3. Pin this Observatory implementation and its four alpha.2 output schemas by
   immutable revision. The implementation's commit is the PR head; the source
   tree does not embed its own future SHA. Query/fleet/compare require alpha.2
   snapshots. Rebuild old snapshots from their original projections.
4. Update Relay's collector, validator/runtime lock, fixture hashes, build
   integration, and existing renderer together. A reference-only issue lookup
   is `partial`; unqueried ADRs, Git, checks, releases, deployments, and history
   remain `uncollected`. Do not replace Observatory views or add private override
   extensions. Provider adapters own collection declarations; Observatory never
   guesses them from array lengths.
5. Exercise the pinned roadmap-only, provider-denied, partial, stale,
   observed-empty, full, not-applicable, failed, and mixed-fleet fixtures through
   collection → validation → normalization → existing rendering. Keep publication
   denied until every applicable renderer displays collection uncertainty.

Old full alpha.1 inputs still produce the same graph records. Their new outputs
explicitly mark completeness unknown (`legacy_unspecified`), even when the
fixture includes every entity kind. Alpha.1 consumers reject new alpha.2 input
and output; optional-field fallback is unsafe here.

## Reproduce locally without credentials

```bash
python3 -m pip install --editable ".[test]"
python3 -m unittest discover --start-directory tests --pattern 'test_*.py'
python3 scripts/verify_fixtures.py
observatory-intelligence build \
  --input fixtures/repository-intelligence/coverage/roadmap-only.json \
  --input fixtures/repository-intelligence/observatory-active.input.json \
  --output build/coverage-example
observatory-intelligence query \
  --snapshot build/coverage-example/repositories/egohygiene--relay.json \
  --view work
```

The result has no issue entities and an empty `open_issues`, with
`issues.collection: uncollected`. `fixtures/expected/coverage` is the stable,
privacy-safe renderer boundary. No source collection, deployment, architecture
rewrite, or canonical roadmap authoring is part of this migration.
