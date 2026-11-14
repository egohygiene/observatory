# Continuity observations

The optional `fleet-continuity/v1` view consumes explicitly supplied, closed
metadata observations. It never opens, parses, summarizes or publishes
`CONTINUITY.md` contents. A source collector/validator supplies safe fields;
Observatory does not replace Aether's contract or Hygiene's applicability policy.

The exact draft Aether schema and proposed Hygiene policy are pinned in
`observatory.continuity.OWNER_PIN` and `POLICY_PIN`. This is observe-mode adoption;
structural validity does not make a handoff true, current, approved or enforced.
No EgoLint migration or human ratification is selected here.

## Build and consume

```python
from observatory import build_continuity_view, build_organization_health

view = build_continuity_view(
    observation_wrappers, repositories=explicit_public_targets,
    as_of="2026-11-14T04:00:00Z",
)
# The existing health builder accepts the same explicit selection as an opt-in:
# build_organization_health(..., continuity={
#     "repositories": explicit_public_targets, "observations": observation_wrappers})
```

Public targets are `{repository, represented_commit}` objects. Wrapper arrays
use `{visibility, repository, evidence}`; evidence is the closed observation
shape in [`continuity-observation.v1.schema.json`](../schemas/continuity-observation.v1.schema.json).
No arbitrary extension/body field is accepted. Private, inaccessible and
unlisted repository wrappers are excluded before validation, identities, counts
or digests; changing their content cannot alter a public projection. Inaccessible
**public** targets remain selected with no observation and `unverifiable` posture.
The projection cannot reveal the existence of an excluded private repository.

The health CLI opts in with `--continuity-targets targets.json` and repeatable
`--continuity-evidence wrappers.json`. No flag preserves existing output bytes
and identity. Selected metadata is linked from the same health snapshot, never
maintained as a parallel canonical fleet catalog; the snapshot ID includes the
view digest. Existing consumers must repin the schema before selecting this
optional field. Pace can consume the metadata without scraping Markdown.
An opted-in health snapshot explicitly selects `contract_version: 1.0.0-alpha.2`;
the default remains alpha.1. The schema rejects the extension on an alpha.1
snapshot. This version change is a projection capability, not policy promotion.

## Independent evidence dimensions

- Exact-case root file presence is an observation; absence differs from missing
  collector access. Unknown presence is `unverifiable`.
- Structural validity and validator/error counts remain separate from declared
  freshness, Git evidence and actual live verification. A recent timestamp is
  not proof of any other dimension.
- The managed `AGENTS.md` pointer has presence and a unique-block count. Missing
  or duplicate blocks cannot yield a structurally valid adoption posture.
- Applicability/exception is a source claim under the pinned proposed policy;
  exemptions need an explicit public reference. Template/archive/mirror
  exceptions must be supplied, never inferred from an empty file list.
- Observation freshness uses only explicit observed/valid-until/as-of times.
  `stale-declared` describes the handoff declaration, while expired observations
  retain their independent `stale` observation freshness.
- A different represented commit is retained but cannot establish the selected
  revision's latest state. Equal revision/time records must agree exactly.
- Unsupported contract versions remain `unsupported`; no version is guessed.

Output postures are `absent`, `provisional`, `valid`, `invalid`, `stale-declared`,
`unverifiable`, `exempt` and `unsupported`. They are not Hygiene conformance or a
semantic quality score. No observation means unavailable collection, never an
absent-file finding or a healthy repository.

## Reproducing a baseline

The issue's September 8 baseline is historical, not a permanent 29-repository
claim. Reproduce any baseline by retaining an explicit public selector inventory,
each represented revision, observation metadata/source links and fixed as-of
time; the output is sorted and sealed deterministically. The pinned public
catalog determines eligible public selection, not a hard-coded fleet count.
Collectors must separately account for inaccessible/private scope without
publishing its identities or content. This implementation does not claim a new
live fleet scan.

[`fixtures/continuity/`](../fixtures/continuity/) is synthetic and covers the
state boundaries. Local contract tests exercise metadata projection, privacy
invariance, schema rejection, revision/freshness separation and opt-in health
compatibility. No real handoff, GitHub provider, model or hosted publication is
qualified by those fixtures.
