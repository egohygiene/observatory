# Bounded repository conformance query

Owner: Observatory. Proposed contract:
`egohygiene.observatory.repository-conformance/v1`, `1.0.0-alpha.1`.
Refs [Observatory #5](https://github.com/egohygiene/observatory/issues/5) and
[Relay #75](https://github.com/egohygiene/relay/issues/75). This is assessed
contract evidence, not a complete applicability inventory or universal policy.

## Input and authority

The query reuses `repository-evidence/v1` alpha.1 and the existing organization
health validator, freshness rules, check identity and conformance rollup.
Hygiene owns applicability, validators own findings, Pace owns adoption and
remediation, and each repository owns source/publication. No validator is rerun.

Public admission uses only Hygiene #97's exact reviewed public artifact at
`49639c1845cdfd08fbd5a768261a8b3cf515f80f`. Its source, schema/helper digests and
packaged artifact are recorded in
[`hygiene.public-conformance.v1.lock.json`](../contracts/hygiene.public-conformance.v1.lock.json).
The original public JSON bytes are packaged under `observatory/data/`; their
digest is verified before admission. This is a pinned owner artifact, not a new
registry. Protected/full catalogs, their totals and raw digests are not inputs.
An unadmitted selector fails without a named missing/private placeholder.

Evidence is explicitly wrapped rather than inferring public visibility from a
repository name or a successful check:

```json
{
  "visibility": "public",
  "repository": "egohygiene/observatory",
  "evidence": {
    "schema": "egohygiene.observatory.repository-evidence/v1"
  }
}
```

The nested `evidence` must contain the complete existing evidence contract,
not merely the abbreviated example above. The wrapper has exactly those three
fields. Nonpublic, ambiguous-visibility and nonselected wrappers are discarded
before payload validation, identities, text, counts or digests. Selected payloads
must identify the same repository before any other fields are read. A malformed
selected public record denies the candidate; it does not become a passing gap.
Selected links must be credential-free HTTPS, without query credentials;
GitHub links may name only explicitly admitted public repositories. Text and
diagnostics are bounded and reject obvious secrets, emails and machine paths.

Inputs are limited to 256 selected public wrappers, 256 files, 4 MiB per JSON
document and 4096 resulting checks. JSON is parsed with duplicate-key awareness;
nested ambiguity is rejected only after public/target admission. GitHub links
use plain paths without percent encoding, dot segments or backslashes. These are transport bounds;
protected content changes within them never enter public counts or hashes.

## Query and CLI

`build_repository_conformance(wrappers, repository=..., represented_commit=...,
as_of=...)` returns one source-bound query. A caller may supply a trusted
`admission_root` containing the exact public artifact and an `admission` receipt
from Relay's shared loader. The receipt must equal the owner proof for exactly
the selected row; a self-asserted subset/digest cannot establish membership.

```bash
observatory-conformance \
  --repository egohygiene/observatory \
  --represented-commit 51be4a740c790f99364f577730c1a98f301bee47 \
  --as-of 2026-11-09T16:00:00Z \
  --evidence review/observatory-public-evidence.json \
  --output review/observatory-conformance.json
```

Repeat `--evidence` for multiple wrappers or arrays. Omitting evidence produces
an admitted repository with unavailable conformance evidence and an unknown
assessment. It never establishes that zero contracts apply. The CLI has no
network/provider discovery, source crawling, native validator, clock or writer
authority. Existing health/Intelligence CLI defaults, locks and golden artifacts
are unchanged.

## Meaning preserved

Only checks explicitly assessing `conformance` appear. Each retains its stable
producer/check identity, contract ID/version/source, domain, required/advisory
assessment severity, reported and effective status, evidence links, producer,
represented revision, observation and validity window. Fields are display data,
not executable instructions or policy assertions by Observatory.

Freshness follows existing health semantics: an observation after evaluation is
denied; expiry strictly before `as_of` is stale. A stale pass remains a reported
pass with effective stale status. Duplicate producer/check identities fail;
there is no implicit latest-wins merge.

Every row separately reports whether its represented commit matches the query.
Other-revision observations remain context but are excluded from the current
assessment. Required current-revision checks use the existing precedence:
fail, blocked, stale, unknown, partial, pass, not applicable. Advisory checks are
visible and excluded from that rollup. No current required evidence is unknown.
The assessment is explicitly limited to supplied evidence, never whole-repository
conformance or maturity and never a score.

Whole contract inventory and applicability are always `unknown` in this version.
No exemption, ratification, migration stage, universal obligation or remediation
completion is invented. A validator's reported `not_applicable` remains its
check result and does not establish general applicability. Suggested owner links
are navigation, not materialized remediation work.

## Renderer and validation boundary

The [standalone owner validator](../src/observatory/conformance_contract.py) and
[closed schema](../schemas/repository-conformance.v1.schema.json) bind identity,
exact public admission, clocks, row/revision states, supplied assessment and
canonical checks digest. Relay pins and executes these owner bytes rather than
rebuilding the conformance model. Its real Hygiene view may consume the query
as a separately bound optional input, without copying the input into a new
public asset or altering other Intelligence coverage domains.

This source pass performed static Python/schema/package-metadata and source
review only. Tests, fixture generation, native/consumer execution, builds, CI,
browser/accessibility review and publication remain deferred by the user.
Public/private invariance, duplicate/unknown/malformed inputs, stale/future and
other-revision observations, package installation and three diverse canaries
remain qualification work. #5/#75 remain open. A future organization sanity
sweep must independently assess applicability and human ratification; these
rows do not substitute for that evidence.

ADR disposition: existing observation/evidence/unknown boundaries and proposed
ADR-0004 govern the implementation; proposed ADR-0006 records this bounded query.
