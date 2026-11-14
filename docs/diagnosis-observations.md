# Diagnosis metadata observations

This optional versioned view consumes **already validated, explicitly approved
public metadata projections**. It does not parse diagnosis Markdown, crawl
paths, read record bodies/logs, execute a validator or decide whether a diagnosis
is true. Aether's draft1.0.0 schema is pinned by exact revision/digest in
`observatory.diagnoses.OWNER_PIN`.

Hygiene #41's applicability/privacy policy is still unavailable as a versioned
artifact. Output therefore retains `policy.status: unavailable`, source-declared
applicability and no enforcement. A source publication approval is a claim with
a public reference, not verified human approval. Consumers must retain that
limitation; this adapter does not finish or ratify Hygiene's policy.

## Public boundary

The outer wrapper selects `{visibility, repository, evidence}` from the existing
pinned public catalog before metadata IDs, validation, counts or digests. Within
an admitted public repository, records are selected **before inspecting their
identities** only when `sensitivity: public` and publication has
`status: approved, scope: allowlisted-metadata`. Restricted, internal, pending
and withheld record content does not affect any public byte or count. A
withheld collection can expose its explicitly public availability state only;
record identities, timestamps, paths and total counts stay absent.

Approved records have a closed metadata shape. They preserve the canonical
link, owner pin, source-claimed content digest, represented commit/artifact,
component/environment/correlation IDs, lifecycle, independent reproduction,
root-cause, remediation and validation states, optional hypothesis counts,
redaction, structural-conformance result, authored update time, and explicit
issue/PR/commit/ADR/incident/supersession links. No arbitrary body/telemetry field
is accepted. The canonical source digest remains an **unverified source claim**;
only the normalized public view receives an actually calculated digest.

Nodes keep a stable diagnosis identity and a separate represented-artifact key.
Edges are source-declared relationships, not inferred causal or completion
claims. Neither a passed structural check nor a resolved lifecycle rewrites the
independent investigation states. Missing records or access never means no
defects. A later capture omitting a diagnosis never resolves the earlier record;
the ordered observation history remains available.

## Build and compose

```sh
PYTHONPATH=src python3 -m observatory.diagnoses_cli \
  --targets fixtures/diagnoses/targets.json \
  --evidence fixtures/diagnoses/observations.json \
  --as-of 2026-11-14T04:00:00Z --output /tmp/new-diagnosis-view.json
```

Targets explicitly bind public repositories to represented commits. Every
observation has a collection state, source reference, producer, collection and
expiry time. `observed-empty`, `partial`, `withheld`, `unavailable`, `unsupported`,
`not-applicable` and `unknown` remain distinct. An observation from another
revision is retained but cannot establish the selected revision's collection.
Equal revision/time captures must agree; identical captures deduplicate.
Conflicting or incompatible approved metadata fails closed without input text.

Use `build_diagnosis_view()` as a pure library function. For Repository
Intelligence, `attach_diagnosis_view(existing_snapshot, single_repository_view)`
or CLI `--snapshot` composes through the **existing extensions field**. Repository,
revision and public scope must match exactly. The graph, owned domain coverage
and existing queries remain untouched; the extension and snapshot identity bind
the derived metadata. The view is not a second canonical graph or a new Hygiene
collection domain. Default Intelligence snapshots remain byte-identical.

The CLI only reads selected metadata and writes a new explicit output. It never
overwrites a receipt or fetches a source URL. This alpha extension must be pinned
by schema/version/digest; consumers lacking it report unavailable rather than
guessing from empty graph collections. Superseding interfaces must preserve
source/represented-artifact relationships and independently declared states.

## Offline qualification

`fixtures/diagnoses/` contains synthetic metadata only. Tests cover public,
private/restricted, withheld, partially adopted, malformed, duplicate, stale,
different-revision and superseded inputs; metadata disclosure invariance;
owner-pin/state rejection; node/edge consistency; schema; no-overwrite CLI;
and composition into the existing Intelligence snapshot. No real diagnosis,
policy approval, private telemetry, provider/model or hosted publication is
qualified. Hygiene #41 and downstream presentation/rollout remain independent.
