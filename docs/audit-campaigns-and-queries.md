# Separate public campaign and audit queries

Three optional alpha.1 models extend the public Audits program independently
of the merged repository/fleet Audits and Sanity models and Intelligence defaults.

| Model | API | Closed schema |
| --- | --- | --- |
| Selected public campaign index | `audit_campaigns.build_fleet_audit_campaigns` / `audit_campaigns.validate` | `fleet-audit-campaigns.v1.schema.json` |
| Categorical patterns | `audits_queries.query_fleet_audits` / `audits_queries.validate` | `fleet-audit-patterns.v1.schema.json` |
| Structural fleet before/after | `audits_queries.compare_fleet_audits` / `audits_queries.validate` | `fleet-audits-comparison.v1.schema.json` |

## Selected campaign source

Reflector owns the transport grammar, pinned at
`39f7e02acb0e100881a1f81a2ea8a3927e34ed15` in
`contracts/reflector.audit-campaign.v1.lock.json`. Packaged mirrors retain the
exact helper and manifest schema. This grammar already permits
plan/index/discover/run, declared passes, capability headers and execution
states. It does not prove audit execution or review truth. Actual producer
implementation remains its declared generator revision, separate from the
contract pin and the referenced Aether report authority.

`build_fleet_audit_campaigns(wrappers, repositories=[{repository,
represented_commit}], as_of=..., admission_root=...)` authenticates explicit
selectors using the existing exact packaged Hygiene public catalog. Wrappers
declare `visibility: public`, `repository: egohygiene/reflector`, `evidence` and
optional `source`. Evidence may be structured data or raw JSON. Excluded
selectors/private wrappers/manifests without selected rows do not become names,
counts, placeholders or failures.

Rows are selected before payload validation and hashing. Only selected rows and
allowlisted declared global metadata enter the model. Malformed states, hashes,
duplicate payload fields and inventory in unselected rows cannot alter a
selected projection. Retained selected fields remain ambiguity checked,
bounded and validated against the pinned transport vocabulary. This deliberately
does not claim whole-manifest validation: whole request/catalog/row input hashes,
generator implementation maps and omitted capability inventories are ignored.

Global status/mode/profiles/passes remain literal declared source facts. They
are not recomputed as a selected-scope verdict and establish no approval,
conformance, audit completion or issue materialization. Each row retains its
original SHA/clock and an explicit matched/different/unknown relation to the
requested revision. Report references, completion, profiles and finding counts
are declared orchestration metadata, not newly admitted findings. Capability
counts, omitted-entry diagnostics and source/capture hashes remain withheld;
only declared capability state and original clock are projected.

Whole-manifest raw/canonical hashes and source checksum claims are not used.
`raw_checksum: withheld-whole-manifest` names that boundary; output digests bind
only admitted projection bytes. An optional source reference is a declared exact
public GitHub blob citation with its whole-input checksum withheld, not proof
of fetched/verified bytes. Evidence counts supplied selected campaign projections,
not unique audits, findings or executions. Referenced reports still require
their own owner admission. The base Audits campaign field stays unavailable;
this separate index creates no synthetic bridge or report.

## Patterns and comparison

Pattern queries first validate a supplied public fleet-audits model. They group
exact source finding keys by classification, nature, area and profile/version,
and emit a category only when at least two admitted repositories contribute.
Members retain revision match, freshness and authored status. Counts retain the
repository-report-projection unit. Category recurrence is not an inferred
common cause, fleet defect, conformance failure or confidence escalation.

Before/after requires the same public repository names, admission, owner
contracts and freshness policy, and ordered explicit evaluation clocks.
Represented SHAs may differ and remain inspectable. Keys preserve repository,
complete authored audit ID (including any colons) and finding ID. A new authored
audit is a separate record unless its own source history relates it.

Results use only `after-only`, `before-only`, `changed`, named changed fields
and exact public record hashes. Omission never resolves a finding. Authored
current history stays separate with evidence labels, explicit prior IDs and
references. Related history requires prior audit/finding identities and
references; resolved claims retain the observed-evidence label. No cause,
improvement, regression, acceptance or continuity is inferred from the delta.

Derived validators check closed shape, exact admission, source descriptors,
key bindings, typed counts, ordering and canonical digest. Source digests name
separately validated inputs; derived-model revalidation does not fetch them or
prove the derivation independently. Rebuild from retained original fleet models
for that proof. There is no ambient clock, discovery, provider or overwrite.

## Explicit offline adapters

```sh
observatory-audit-campaigns --targets selected-public.json --as-of "$AS_OF" \
  --evidence campaign-wrapper.json --output campaign-index.json
observatory-audits patterns --fleet fleet-audits.json --output patterns.json
observatory-audits compare --before before-fleet-audits.json \
  --after after-fleet-audits.json --output comparison.json
```

Inputs must exist and outputs must be new paths. No CLI executes a campaign,
discovers sources or materializes a backlog. Existing repository/fleet Audits
commands keep their inputs and defaults.

## Source and qualification checkpoint

This follow-up resumes `codex/intelligence-audits-sanity-20261110` after Audits
and Sanity reconciled at `692fbe7a5a31827d442818bf33f5b225abc2d4b8`, merged as
`6d6f67cb67cd68a5ac61e3c4df05bc9d1fb36dde`. Root cherry-picks only the new
functional commit and handles shared continuity; the historical `7596d88`
Sanity commit must not be introduced again under a different hash.
Existing schemas, owner locks and default models remain unchanged. One shared
privacy correction scans complete `egohygiene/[A-Za-z0-9_.-]+` namespaces before
exact public admission, preventing private suffixes from matching public-name
prefixes. Downstream Audit and Sanity capsules must pin these corrected bytes.

The user deferred tests, application/native/source execution, fixture runs,
installation/builds, CI and provider/browser/publication acceptance. Only static
Python/schema/package metadata, exact owner hashes and source peer inspection
are in scope. Mixed-scope invariance, malformed/chronology cases, generated data,
installation and consumer acceptance remain in the deferred verification pass.
No audit, human review, policy ratification or issue completion is claimed.

Refs [Observatory #20](https://github.com/egohygiene/observatory/issues/20) and
[organization #41](https://github.com/egohygiene/.github/issues/41).
