# Versioned Search field attribution

Owner: Observatory. Status: proposed `1.0.0-alpha.1` extension under
[Observatory #24](https://github.com/egohygiene/observatory/issues/24), consumed by
[Relay #102](https://github.com/egohygiene/relay/issues/102). The repository,
fleet, query-view and Compare contracts remain `1.0.0-alpha.2`. Hygiene input
versions, source authority, graph identity and all collection claims are unchanged.

## Explicit adoption and compatibility

Existing build calls and CLI defaults retain their opaque `search_text` output.
Enable the extension explicitly with
`build_repository_snapshot(projection, search_attribution=True)`,
`build_bundle(projections, search_attribution=True)`, or:

```bash
observatory-intelligence build \
  --input fixtures/repository-intelligence/relay-complete-quest.input.json \
  --search-attribution \
  --output build/repository-intelligence
```

Every freshly opted-in repository Search record receives this optional member:

```json
{
  "search_fields": {
    "schema": "egohygiene.observatory.repository-intelligence-search-fields/v1",
    "contract_version": "1.0.0-alpha.1",
    "fields": [
      {"field": "title", "text": "review evidence"},
      {"field": "key", "text": "obs-q02"},
      {"field": "kind", "text": "roadmap_step"},
      {"field": "state", "text": "active"},
      {"field": "repository", "text": "egohygiene/observatory"}
    ]
  }
}
```

The block has exactly the three shown members. Its array contains exactly five
closed `{field, text}` objects in title, key, kind, state, repository order.
There are no optional field names, duplicate entries, unknown fields, URLs,
extensions, provider bodies, arbitrary prose or derived confidence values.
Titles remain nullable in the compact entity; a null title contributes `""`.
Each normalized value comes directly from the corresponding compact canonical
field. Metadata never expands the visibility of the original record.

Fleet composition preserves the optional block on each record and keeps the
existing global record order. Extracted Search views copy it without rebuilding
it. A fleet may legitimately contain opted-in records and older records without
attribution. Absence always means **attribution unavailable**, including a
matching older record. Consumers must not guess from displayed values.
Malformed or unknown-version supplied metadata is an error, not absence.

## One aggregate and one matching rule

For each approved field, apply frozen Unicode **14.0.0** full default lowercase
without a locale or casefold. Preserve its internal and edge whitespace. Join the five normalized
values with exactly one U+0020 separator, then trim only the outer whitespace of
the entire aggregate. The default opaque build path remains unchanged. The opted-in
versioned representation freezes the existing aggregate formula to one Unicode
baseline rather than the host runtime's evolving tables. Its values can differ
from a newer host's opaque output for newly introduced casing pairs; the explicit
extension version identifies those normalization semantics. Independently trimming
fields or collapsing whitespace would change matching.

The fixed trim set is U+0009–000D, U+001C–0020, U+0085, U+00A0, U+1680,
U+2000–200A, U+2028, U+2029, U+202F, U+205F and U+3000. U+FEFF is retained.
ECMAScript `trim()` has a different set and must not replace this rule.

An active query uses the same locale-independent lowercase and fixed outer trim.
Match the **whole query as one substring** of the supplied aggregate. Internal
spaces, tabs and newlines remain significant. Multiple tokens do not become an
AND query, ranking, fuzzy matching, normalization or a second local index.

Field attribution is the ordered union of fields whose nonempty normalized
text spans overlap any complete substring occurrence. Include every occurrence,
including overlapping occurrences and phrases crossing field separators.
Compute spans after lowercasing and adjust them for the aggregate's outer trim;
original-string offsets break on lowercase expansion such as U+0130. Inserted
separators have no field attribution. Repeated matches in two fields return both.

For the example above:

| Query | Matched | Matched fields |
| --- | --- | --- |
| `review` | true | title |
| `obs-q02` | true | key |
| `roadmap_step` | true | kind |
| `active` | true | state |
| `egohygiene/observatory` | true | repository |
| `evidence obs-q02` | true | title, key |
| `review active` | false | none |
| empty query | true | none; no query-specific explanation |

No match returns an empty field list with `matched: false`. Empty query returns
`matched: true` with an empty list. These states differ from unavailable
attribution, which is reported separately even when an older record matches.
Record order always remains Observatory's supplied order.

## Owner APIs and validation

The dependency-free Python reference is
[`src/observatory/search_fields.py`](../src/observatory/search_fields.py):

- `normalize_search_query(query)` returns the normalized query string.
- `validate_search_record(record)` returns the unchanged record or raises a
  sanitized `SearchContractError`.
- `match_search_record(record, query)` returns
  `{matched, attribution_status, matched_fields}`. Status is `available` or
  `unavailable`; field names always follow the fixed canonical order.

The framework-free classic-script reference is
[`contracts/search-fields.v1.js`](../contracts/search-fields.v1.js). It exports
only `globalThis.EgoHygieneSearchFieldsV1` with `normalizeQuery`, `validateRecord`
and `matchRecord`, using the same result shape. It reads no DOM, source files,
network, provider API, clock or external index. Errors contain no input values.
Consumers may retain the exact owner bytes with an immutable source and digest;
they should not independently rebuild the algorithm from displayed fields.

The [closed schema](../schemas/repository-intelligence-search-fields.v1.schema.json)
rejects unsupported versions, extra properties, duplicate/out-of-order/unknown
field names and missing members. Optional block validation is also present in
the repository, fleet and extracted-view schemas. JSON Schema cannot compare
normalized values across properties: semantic validation additionally requires
the exact lowercased compact canonical fields and identical aggregate text.
The owner helpers perform those equalities. Repository snapshot intake also
compares attributed records to their graph entities; fleet composition validates
each repository before copying it. No missing metadata is synthesized on intake.

Both reference helpers embed the same compact Unicode 14.0.0 lowercase mapping,
unconditional SpecialCasing, Cased and Case_Ignorable tables. They apply the
locale-independent Final_Sigma rule and preserve unmapped code points; they do
not call host lowercase APIs. Thus U+A7CB retains its Unicode-14 value even on a
newer runtime that introduces a lowercase mapping. Source URLs, exact SHA-256s
and table counts are recorded in the
[contract descriptor](../contracts/repository-intelligence-search-fields.v1.json).
The [Unicode license](../contracts/UNICODE-LICENSE.txt) is included in both
standalone helpers and distributed separately. No runtime data fetch or adjacent
data file is needed. Cross-runtime execution qualification remains deferred.
UTF-16 browser offsets and Python code-point offsets give
the same field participation when each implementation consistently uses its own
normalized-string units. Both helpers reject lone surrogate values so malformed
half-character queries cannot produce different substring results across runtimes.

## Relay handoff and deferred acceptance

Relay should pin the exact owner revision, Python helper, JavaScript reference,
schemas and contract descriptor. Older native collector runtime pins and receipts
remain unchanged. A separate opted-in composition profile can normalize the final
admitted graph with this Observatory version. The standalone engine loader must
retain its adjacent `search_fields.py` in the same verified runtime file set.

Relay renders entity type, key, state, repository, assertion, freshness and source
as before. Query-specific field labels are a JavaScript enhancement using text;
static evidence remains present without JavaScript. Missing metadata gets an
explicit unavailable label, and an empty query gets no match-field claim.
Escaping, public visibility filtering and source authority remain the renderer's
responsibility before it passes a record to the owner matching API.

This implementation was prepared from Observatory main
`f49b691deaa68a2bc9a79ef65b32d25b7aea20af`. Source/syntax/schema inspection and
independent source review are the permitted validation boundary. The user
deferred tests, fixture additions/regeneration, builds, native execution, CI,
browser review and deployment. Existing default golden artifacts remain unchanged.
Before acceptance, add and run canonical examples for all five fields,
multi-field/cross-field/repeated and overlapping matches, no match, empty query,
null title, hostile text, whitespace/Unicode, partial adoption and malformed
metadata. Qualify generated artifact determinism, accessibility and live behavior
separately. Neither Observatory #24 nor Relay #102 is closed by source preparation.

ADR disposition: implement the existing proposed ADR-0004 read-model design and
record proposed ADR-0005 for this optional versioned extension. Their human
lifecycle dispositions remain unchanged.
