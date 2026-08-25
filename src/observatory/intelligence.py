"""Normalize Repository Intelligence projections into deterministic read models.

Hygiene owns the graph vocabulary and Egolint owns semantic validation. This
module deliberately limits itself to a defensive consumer boundary, stable
indexing, and transparent query projections.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import tempfile
from collections import Counter
from copy import deepcopy
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence
from urllib.parse import urlparse

UPSTREAM_SCHEMA = "egohygiene.repository-intelligence/v1"
UPSTREAM_CONTRACT_VERSION = "1.0.0-alpha.1"
READ_MODEL_SCHEMA = "egohygiene.observatory.repository-intelligence-read-model/v1"
FLEET_SCHEMA = "egohygiene.observatory.repository-intelligence-fleet/v1"
VIEW_SCHEMA = "egohygiene.observatory.repository-intelligence-view/v1"
COMPARE_SCHEMA = "egohygiene.observatory.repository-intelligence-compare/v1"
CONTRACT_VERSION = "1.0.0-alpha.1"
GENERATOR = {
    "name": "egohygiene/observatory:repository-intelligence",
    "version": "0.1.0",
}
VIEW_NAMES = (
    "roadmap",
    "decisions",
    "journey",
    "now",
    "dependencies",
    "health",
    "releases",
    "work",
    "search",
)

_REPOSITORY_PATTERN = re.compile(r"^[a-z0-9][a-z0-9.-]*/(?:\.github|[a-z0-9][a-z0-9.-]*)$")
_IDENTIFIED_COLLECTIONS = ("sources", "entities", "relationships", "events")
_FRESHNESS_STATES = ("current", "stale", "unknown", "not_applicable")
_ASSERTION_STATES = ("authoritative", "inferred", "unknown")

JsonObject = dict[str, Any]


class ContractError(ValueError):
    """Raised when an input cannot be consumed without inventing meaning."""


def _canonical_bytes(value: Any) -> bytes:
    return json.dumps(
        value,
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("utf-8")


def digest(value: Any) -> str:
    """Return a stable content digest for JSON-compatible data."""

    return f"sha256:{hashlib.sha256(_canonical_bytes(value)).hexdigest()}"


def _require_object(value: Any, location: str) -> JsonObject:
    if not isinstance(value, dict):
        raise ContractError(f"{location} must be an object")
    return value


def _require_list(value: Any, location: str) -> list[Any]:
    if not isinstance(value, list):
        raise ContractError(f"{location} must be an array")
    return value


def _require_string(value: Any, location: str) -> str:
    if not isinstance(value, str) or not value:
        raise ContractError(f"{location} must be a non-empty string")
    return value


def _require_url(value: Any, location: str) -> str:
    url = _require_string(value, location)
    parsed = urlparse(url)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise ContractError(f"{location} must be an absolute HTTP(S) URL")
    return url


def _unique_ids(records: Sequence[Any], location: str) -> dict[str, JsonObject]:
    index: dict[str, JsonObject] = {}
    for position, raw_record in enumerate(records):
        record = _require_object(raw_record, f"{location}[{position}]")
        identifier = _require_string(record.get("id"), f"{location}[{position}].id")
        if identifier in index:
            raise ContractError(f"duplicate {location} id: {identifier}")
        index[identifier] = record
    return index


def _validate_provenance(
    record: Mapping[str, Any], location: str, source_ids: set[str]
) -> None:
    provenance = _require_list(record.get("provenance"), f"{location}.provenance")
    if not provenance:
        raise ContractError(f"{location}.provenance must not be empty")
    for position, source_id in enumerate(provenance):
        _require_string(source_id, f"{location}.provenance[{position}]")
    if len(provenance) != len(set(provenance)):
        raise ContractError(f"{location}.provenance contains duplicates")
    dangling = sorted(set(provenance) - source_ids)
    if dangling:
        raise ContractError(f"{location}.provenance has unknown sources: {', '.join(dangling)}")


def _validate_assertion_and_freshness(record: Mapping[str, Any], location: str) -> None:
    assertion = _require_string(record.get("assertion"), f"{location}.assertion")
    if assertion not in _ASSERTION_STATES:
        raise ContractError(f"{location} has unsupported assertion {assertion!r}")
    freshness = _require_string(record.get("freshness"), f"{location}.freshness")
    if freshness not in _FRESHNESS_STATES:
        raise ContractError(f"{location} has unsupported freshness {freshness!r}")


def validate_projection(projection: Any) -> JsonObject:
    """Validate the safe subset Observatory requires before querying a graph.

    This is not a replacement for the complete Hygiene schema or Egolint's
    semantic rules. It protects Observatory from unsupported versions,
    collisions, dangling graph references, and unusable provenance.
    """

    document = _require_object(projection, "projection")
    if document.get("schema") != UPSTREAM_SCHEMA:
        raise ContractError(
            "unsupported projection schema: "
            f"{document.get('schema')!r}; expected {UPSTREAM_SCHEMA!r}"
        )
    if document.get("contract_version") != UPSTREAM_CONTRACT_VERSION:
        raise ContractError(
            "unsupported Repository Intelligence contract version: "
            f"{document.get('contract_version')!r}; expected {UPSTREAM_CONTRACT_VERSION!r}"
        )

    repository = _require_string(document.get("repository"), "projection.repository")
    if not _REPOSITORY_PATTERN.fullmatch(repository):
        raise ContractError(f"projection.repository is not canonical: {repository!r}")
    _require_string(document.get("projection_id"), "projection.projection_id")
    _require_string(document.get("represented_commit"), "projection.represented_commit")
    _require_string(document.get("observed_at"), "projection.observed_at")
    _require_string(document.get("visibility"), "projection.visibility")

    for collection in _IDENTIFIED_COLLECTIONS:
        _require_list(document.get(collection), f"projection.{collection}")
    _require_list(document.get("redactions"), "projection.redactions")
    _require_object(document.get("extensions"), "projection.extensions")

    sources = _unique_ids(document["sources"], "projection.sources")
    entities = _unique_ids(document["entities"], "projection.entities")
    relationships = _unique_ids(document["relationships"], "projection.relationships")
    events = _unique_ids(document["events"], "projection.events")
    source_ids = set(sources)
    entity_ids = set(entities)

    for source_id, source in sources.items():
        _require_string(source.get("kind"), f"source {source_id}.kind")
        _require_url(source.get("url"), f"source {source_id}.url")
        _require_string(source.get("repository"), f"source {source_id}.repository")
        _require_string(source.get("observed_at"), f"source {source_id}.observed_at")
        _require_string(source.get("visibility"), f"source {source_id}.visibility")
        _validate_assertion_and_freshness(source, f"source {source_id}")

    for entity_id, entity in entities.items():
        _require_string(entity.get("kind"), f"entity {entity_id}.kind")
        _require_string(entity.get("repository"), f"entity {entity_id}.repository")
        _require_string(entity.get("key"), f"entity {entity_id}.key")
        _require_url(entity.get("canonical_url"), f"entity {entity_id}.canonical_url")
        _require_string(entity.get("visibility"), f"entity {entity_id}.visibility")
        state = _require_object(entity.get("state"), f"entity {entity_id}.state")
        _require_string(state.get("value"), f"entity {entity_id}.state.value")
        assertion = _require_string(
            state.get("assertion"), f"entity {entity_id}.state.assertion"
        )
        if assertion not in _ASSERTION_STATES:
            raise ContractError(f"entity {entity_id} has unsupported assertion {assertion!r}")
        freshness = _require_string(entity.get("freshness"), f"entity {entity_id}.freshness")
        if freshness not in _FRESHNESS_STATES:
            raise ContractError(f"entity {entity_id} has unsupported freshness {freshness!r}")
        _validate_provenance(entity, f"entity {entity_id}", source_ids)

    for relationship_id, relationship in relationships.items():
        source = _require_string(
            relationship.get("source"), f"relationship {relationship_id}.source"
        )
        target = _require_string(
            relationship.get("target"), f"relationship {relationship_id}.target"
        )
        if source not in entity_ids or target not in entity_ids:
            raise ContractError(
                f"relationship {relationship_id} has dangling endpoints: {source!r} -> {target!r}"
            )
        _require_string(relationship.get("type"), f"relationship {relationship_id}.type")
        _validate_assertion_and_freshness(
            relationship, f"relationship {relationship_id}"
        )
        _validate_provenance(relationship, f"relationship {relationship_id}", source_ids)

    for event_id, event in events.items():
        subject = _require_string(event.get("subject"), f"event {event_id}.subject")
        if subject not in entity_ids:
            raise ContractError(f"event {event_id} has dangling subject: {subject!r}")
        _require_string(event.get("occurred_at"), f"event {event_id}.occurred_at")
        _require_string(event.get("recorded_at"), f"event {event_id}.recorded_at")
        _require_string(event.get("visibility"), f"event {event_id}.visibility")
        _validate_assertion_and_freshness(event, f"event {event_id}")
        _validate_provenance(event, f"event {event_id}", source_ids)

    repository_entities = [
        entity
        for entity in entities.values()
        if entity.get("kind") == "repository" and entity.get("repository") == repository
    ]
    if len(repository_entities) != 1:
        raise ContractError(
            "projection must contain exactly one repository entity for its root repository"
        )
    return document


def normalize_projection(projection: Any) -> JsonObject:
    """Return a defensive, deterministically ordered projection copy."""

    normalized = deepcopy(validate_projection(projection))
    for collection in ("sources", "entities", "relationships"):
        normalized[collection] = sorted(normalized[collection], key=lambda item: item["id"])
    normalized["events"] = sorted(
        normalized["events"], key=lambda item: (item["occurred_at"], item["id"])
    )
    normalized["redactions"] = sorted(
        normalized["redactions"],
        key=lambda item: (str(item.get("field", "")), str(item.get("reason", ""))),
    )
    return normalized


def load_json(path: str | Path) -> JsonObject:
    """Load one JSON object and report a stable contract error on failure."""

    source_path = Path(path)
    try:
        with source_path.open(encoding="utf-8") as handle:
            value = json.load(handle)
    except (OSError, json.JSONDecodeError) as error:
        raise ContractError(f"cannot read JSON from {source_path}: {error}") from error
    return _require_object(value, str(source_path))


def load_projection(path: str | Path) -> JsonObject:
    """Load, validate, and normalize one Hygiene projection."""

    return normalize_projection(load_json(path))


def _entity_ref(entity: Mapping[str, Any]) -> JsonObject:
    state = _require_object(entity["state"], f"entity {entity['id']}.state")
    assertion = str(state["assertion"])
    return {
        "id": entity["id"],
        "kind": entity["kind"],
        "repository": entity["repository"],
        "key": entity["key"],
        "title": entity.get("title"),
        "canonical_url": entity["canonical_url"],
        "visibility": entity["visibility"],
        "state": state["value"],
        "assertion": assertion,
        "confidence": assertion,
        "freshness": entity["freshness"],
    }


def _entity_index(projection: Mapping[str, Any]) -> dict[str, JsonObject]:
    return {entity["id"]: entity for entity in projection["entities"]}


def _relationships(
    projection: Mapping[str, Any],
    *,
    relation_type: str | None = None,
    source: str | None = None,
    target: str | None = None,
) -> list[JsonObject]:
    result = []
    for relationship in projection["relationships"]:
        if relation_type is not None and relationship["type"] != relation_type:
            continue
        if source is not None and relationship["source"] != source:
            continue
        if target is not None and relationship["target"] != target:
            continue
        result.append(relationship)
    return result


def _enriched_relationship(
    relationship: Mapping[str, Any], entities: Mapping[str, Mapping[str, Any]]
) -> JsonObject:
    return {
        "id": relationship["id"],
        "type": relationship["type"],
        "source": _entity_ref(entities[relationship["source"]]),
        "target": _entity_ref(entities[relationship["target"]]),
        "assertion": relationship["assertion"],
        "confidence": relationship["assertion"],
        "freshness": relationship["freshness"],
        "provenance": sorted(relationship["provenance"]),
    }


def _roadmap_readiness(
    entity: Mapping[str, Any],
    dependencies: Sequence[Mapping[str, Any]],
    blockers: Sequence[Mapping[str, Any]],
) -> JsonObject:
    state = entity["state"]
    value = state["value"]
    reasons: list[str] = []
    if value == "complete":
        result = "complete"
    elif blockers or value == "blocked":
        result = "blocked"
        reasons.append("an explicit block relationship or blocked canonical state exists")
    elif state["assertion"] == "unknown" or entity["freshness"] == "unknown":
        result = "unknown"
        reasons.append("canonical state assertion or freshness is unknown")
    else:
        uncertain_dependencies = [
            item
            for item in dependencies
            if item["state"]["assertion"] == "unknown" or item["freshness"] == "unknown"
        ]
        incomplete_dependencies = [
            item for item in dependencies if item["state"]["value"] != "complete"
        ]
        if uncertain_dependencies:
            result = "unknown"
            reasons.append("at least one prerequisite has unknown evidence")
        elif incomplete_dependencies:
            result = "waiting"
            reasons.append("at least one prerequisite is not canonically complete")
        elif value == "active":
            result = "active"
        elif value in {"planned", "ready"}:
            result = "ready"
        else:
            result = value
    return {
        "value": result,
        "assertion": "inferred",
        "confidence": "inferred",
        "reasons": reasons,
    }


def _roadmap_view(projection: Mapping[str, Any]) -> JsonObject:
    entities = _entity_index(projection)
    steps: list[JsonObject] = []
    for entity in projection["entities"]:
        if entity["kind"] != "roadmap_step":
            continue
        identifier = entity["id"]
        dependency_edges = _relationships(
            projection, relation_type="depends-on", source=identifier
        )
        blocker_edges = _relationships(projection, relation_type="blocks", target=identifier)
        dependencies = [entities[item["target"]] for item in dependency_edges]
        blockers = [entities[item["source"]] for item in blocker_edges]
        tracked = [
            entities[item["target"]]
            for item in _relationships(projection, relation_type="tracks", source=identifier)
        ]
        informed_by = [
            entities[item["source"]]
            for item in _relationships(projection, relation_type="informs", target=identifier)
        ]
        evidence = [
            entities[item["source"]]
            for item in _relationships(projection, relation_type="evidences", target=identifier)
        ]
        verified_by = [
            entities[item["source"]]
            for item in _relationships(projection, relation_type="verifies", target=identifier)
        ]
        steps.append(
            {
                "entity": _entity_ref(entity),
                "outcome": entity.get("attributes", {}).get("outcome"),
                "exit_criteria": entity.get("attributes", {}).get("exit_criteria", []),
                "dependencies": [_entity_ref(item) for item in dependencies],
                "blocked_by": [_entity_ref(item) for item in blockers],
                "tracked_by": [_entity_ref(item) for item in tracked],
                "informed_by": [_entity_ref(item) for item in informed_by],
                "evidence": [_entity_ref(item) for item in evidence],
                "verified_by": [_entity_ref(item) for item in verified_by],
                "readiness": _roadmap_readiness(entity, dependencies, blockers),
            }
        )
    return {
        "steps": steps,
        "roots": [
            item["entity"]["id"] for item in steps if not item["dependencies"]
        ],
    }


def _decisions_view(projection: Mapping[str, Any]) -> JsonObject:
    entities = _entity_index(projection)
    decisions = []
    for entity in projection["entities"]:
        if entity["kind"] != "architecture_decision":
            continue
        identifier = entity["id"]

        def refs(relation_type: str, *, incoming: bool) -> list[JsonObject]:
            edges = _relationships(
                projection,
                relation_type=relation_type,
                **({"target": identifier} if incoming else {"source": identifier}),
            )
            endpoint = "source" if incoming else "target"
            return [_entity_ref(entities[item[endpoint]]) for item in edges]

        decisions.append(
            {
                "entity": _entity_ref(entity),
                "decision_scope": entity.get("attributes", {}).get("decision_scope"),
                "implementation_status": entity.get("attributes", {}).get(
                    "implementation_status"
                ),
                "informs": refs("informs", incoming=False),
                "supersedes": refs("supersedes", incoming=False),
                "superseded_by": refs("supersedes", incoming=True),
                "tracked_by": refs("tracks", incoming=False),
                "evidence": refs("evidences", incoming=True),
                "verified_by": refs("verifies", incoming=True),
            }
        )
    return {"decisions": decisions}


def _journey_view(projection: Mapping[str, Any]) -> JsonObject:
    entities = _entity_index(projection)
    enriched_events = [
        {**deepcopy(event), "subject_entity": _entity_ref(entities[event["subject"]])}
        for event in projection["events"]
    ]
    chapters: list[JsonObject] = []
    pending: list[JsonObject] = []
    last_release: Mapping[str, Any] | None = None
    for event in enriched_events:
        pending.append(event)
        if event["type"] == "release.published":
            boundary = entities[event["subject"]]
            chapters.append(
                {
                    "id": f"chapter:through:{boundary['key']}",
                    "title": f"Through {boundary.get('title') or boundary['key']}",
                    "start_at": pending[0]["occurred_at"],
                    "end_at": pending[-1]["occurred_at"],
                    "boundary": _entity_ref(boundary),
                    "event_ids": [item["id"] for item in pending],
                }
            )
            pending = []
            last_release = boundary
    if pending:
        title = (
            f"After {last_release.get('title') or last_release['key']}"
            if last_release is not None
            else "Unreleased history"
        )
        suffix = last_release["key"] if last_release is not None else "unreleased"
        chapters.append(
            {
                "id": f"chapter:after:{suffix}",
                "title": title,
                "start_at": pending[0]["occurred_at"],
                "end_at": pending[-1]["occurred_at"],
                "boundary": None,
                "event_ids": [item["id"] for item in pending],
            }
        )
    return {"chapters": chapters, "events": enriched_events}


def _dependencies_view(projection: Mapping[str, Any]) -> JsonObject:
    entities = _entity_index(projection)
    edges = [
        _enriched_relationship(item, entities)
        for item in projection["relationships"]
        if item["type"] in {"depends-on", "blocks"}
    ]
    root_repository = projection["repository"]
    external = sorted(
        {
            endpoint["repository"]
            for edge in edges
            for endpoint in (edge["source"], edge["target"])
            if endpoint["repository"] != root_repository
        }
    )
    return {"relationships": edges, "external_repositories": external}


def _counter(records: Iterable[Mapping[str, Any]], field: str) -> JsonObject:
    return dict(sorted(Counter(str(record[field]) for record in records).items()))


def _health_view(projection: Mapping[str, Any]) -> JsonObject:
    checks = [item for item in projection["entities"] if item["kind"] == "check"]
    all_records = [
        *projection["sources"],
        *projection["entities"],
        *projection["relationships"],
        *projection["events"],
    ]
    assertions = []
    for record in all_records:
        if "assertion" in record:
            assertions.append({"assertion": record["assertion"]})
        elif "state" in record:
            assertions.append({"assertion": record["state"]["assertion"]})
    return {
        "checks": [_entity_ref(item) for item in checks],
        "check_states": _counter(
            ({"state": item["state"]["value"]} for item in checks), "state"
        ),
        "freshness": _counter(all_records, "freshness"),
        "assertions": _counter(assertions, "assertion"),
        "stale_ids": sorted(
            str(item["id"]) for item in all_records if item["freshness"] == "stale"
        ),
        "unknown_ids": sorted(
            str(item["id"])
            for item in all_records
            if item["freshness"] == "unknown"
            or item.get("assertion", item.get("state", {}).get("assertion")) == "unknown"
        ),
        "score": None,
        "score_reason": (
            "Observatory preserves evidence states instead of manufacturing a roll-up score."
        ),
    }


def _releases_view(projection: Mapping[str, Any]) -> JsonObject:
    entities = _entity_index(projection)
    releases = []
    for entity in projection["entities"]:
        if entity["kind"] != "release":
            continue
        identifier = entity["id"]
        included = [
            entities[item["target"]]
            for item in _relationships(projection, relation_type="releases", source=identifier)
        ]
        deployments = [
            entities[item["source"]]
            for item in _relationships(projection, relation_type="deploys", target=identifier)
        ]
        release_events = [
            item["id"]
            for item in projection["events"]
            if item["subject"] == identifier and item["type"] == "release.published"
        ]
        releases.append(
            {
                "entity": _entity_ref(entity),
                "published_at": entity.get("attributes", {}).get("published_at"),
                "includes": [_entity_ref(item) for item in included],
                "deployments": [_entity_ref(item) for item in deployments],
                "boundary_event_ids": release_events,
            }
        )
    return {"releases": releases}


def _work_view(projection: Mapping[str, Any], roadmap: Mapping[str, Any]) -> JsonObject:
    issues = [
        _entity_ref(item)
        for item in projection["entities"]
        if item["kind"] == "issue" and item["state"]["value"] == "open"
    ]
    pull_requests = [
        _entity_ref(item)
        for item in projection["entities"]
        if item["kind"] == "pull_request" and item["state"]["value"] == "open"
    ]
    queues: dict[str, list[JsonObject]] = {
        "active": [],
        "ready": [],
        "waiting": [],
        "blocked": [],
        "unknown": [],
    }
    for step in roadmap["steps"]:
        readiness = step["readiness"]["value"]
        if readiness in queues:
            queues[readiness].append(step["entity"])
    return {
        "open_issues": issues,
        "open_pull_requests": pull_requests,
        "roadmap_queues": queues,
    }


def _search_view(projection: Mapping[str, Any]) -> JsonObject:
    records = []
    for entity in projection["entities"]:
        reference = _entity_ref(entity)
        tokens = [
            str(reference.get("title") or ""),
            str(reference["key"]),
            str(reference["kind"]),
            str(reference["state"]),
            str(reference["repository"]),
        ]
        records.append({**reference, "search_text": " ".join(tokens).lower().strip()})
    return {"records": records}


def _coverage(projection: Mapping[str, Any]) -> JsonObject:
    records = [
        *projection["sources"],
        *projection["entities"],
        *projection["relationships"],
        *projection["events"],
    ]
    freshness = _counter(records, "freshness")
    assertions: list[JsonObject] = []
    for record in records:
        assertion = record.get("assertion", record.get("state", {}).get("assertion"))
        assertions.append({"assertion": assertion})
    assertion_counts = _counter(assertions, "assertion")
    if freshness.get("unknown", 0) or assertion_counts.get("unknown", 0):
        status = "unknown"
    elif freshness.get("stale", 0):
        status = "stale"
    elif freshness.get("current", 0):
        status = "current"
    else:
        status = "not_applicable"
    return {
        "status": status,
        "counts": {
            "sources": len(projection["sources"]),
            "entities": len(projection["entities"]),
            "relationships": len(projection["relationships"]),
            "events": len(projection["events"]),
            "redactions": sum(int(item.get("count", 0)) for item in projection["redactions"]),
        },
        "freshness": freshness,
        "assertions": assertion_counts,
    }


def build_repository_snapshot(projection: Any) -> JsonObject:
    """Build one deterministic repository graph and all initial page queries."""

    normalized = normalize_projection(projection)
    entities = _entity_index(normalized)
    root = next(
        item
        for item in normalized["entities"]
        if item["kind"] == "repository" and item["repository"] == normalized["repository"]
    )
    roadmap = _roadmap_view(normalized)
    journey = _journey_view(normalized)
    work = _work_view(normalized, roadmap)
    recent_events = list(reversed(journey["events"][-5:]))
    views: JsonObject = {
        "roadmap": roadmap,
        "decisions": _decisions_view(normalized),
        "journey": journey,
        "dependencies": _dependencies_view(normalized),
        "health": _health_view(normalized),
        "releases": _releases_view(normalized),
        "work": work,
        "search": _search_view(normalized),
    }
    views["now"] = {
        "current_focus": work["roadmap_queues"]["active"],
        "blockers": [
            item
            for item in views["dependencies"]["relationships"]
            if item["type"] == "blocks"
        ],
        "next_ready": work["roadmap_queues"]["ready"][:3],
        "recent_events": recent_events,
        "coverage_status": _coverage(normalized)["status"],
    }
    ordered_views = {name: views[name] for name in VIEW_NAMES}
    upstream_digest = digest(normalized)
    return {
        "schema": READ_MODEL_SCHEMA,
        "contract_version": CONTRACT_VERSION,
        "snapshot_id": f"{normalized['repository']}@{normalized['represented_commit']}",
        "repository": _entity_ref(root),
        "represented_commit": normalized["represented_commit"],
        "observed_at": normalized["observed_at"],
        "visibility": normalized["visibility"],
        "generator": deepcopy(GENERATOR),
        "upstream": {
            "schema": normalized["schema"],
            "contract_version": normalized["contract_version"],
            "projection_id": normalized["projection_id"],
            "digest": upstream_digest,
        },
        "coverage": _coverage(normalized),
        "graph": {
            "sources": normalized["sources"],
            "entities": normalized["entities"],
            "relationships": normalized["relationships"],
            "events": normalized["events"],
            "redactions": normalized["redactions"],
            "extensions": normalized["extensions"],
        },
        "views": ordered_views,
        "extensions": {},
    }


def build_fleet_snapshot(repository_snapshots: Iterable[Mapping[str, Any]]) -> JsonObject:
    """Build a deterministic fleet index without flattening repository context."""

    snapshots = sorted(
        (deepcopy(dict(item)) for item in repository_snapshots),
        key=lambda item: item["repository"]["repository"],
    )
    if not snapshots:
        raise ContractError("at least one repository snapshot is required")
    repositories = [item["repository"]["repository"] for item in snapshots]
    if len(repositories) != len(set(repositories)):
        raise ContractError("fleet input contains more than one snapshot for a repository")
    for item in snapshots:
        if item.get("schema") != READ_MODEL_SCHEMA:
            raise ContractError("fleet input must contain Observatory repository read models")

    repository_records = [
        {
            "repository": item["repository"],
            "snapshot_id": item["snapshot_id"],
            "snapshot_digest": digest(item),
            "represented_commit": item["represented_commit"],
            "observed_at": item["observed_at"],
            "coverage": item["coverage"],
        }
        for item in snapshots
    ]
    fleet_views: JsonObject = {}
    for name in VIEW_NAMES:
        if name == "search":
            records = [
                record
                for item in snapshots
                for record in item["views"]["search"]["records"]
            ]
            fleet_views[name] = {"records": sorted(records, key=lambda record: record["id"])}
        else:
            fleet_views[name] = {
                "repositories": [
                    {
                        "repository": item["repository"]["repository"],
                        "data": item["views"][name],
                    }
                    for item in snapshots
                ]
            }
    observation_times = [item["observed_at"] for item in snapshots]
    coverage_states = Counter(item["coverage"]["status"] for item in snapshots)
    return {
        "schema": FLEET_SCHEMA,
        "contract_version": CONTRACT_VERSION,
        "snapshot_id": digest(repository_records),
        "generator": deepcopy(GENERATOR),
        "observation_window": {
            "earliest": min(observation_times),
            "latest": max(observation_times),
        },
        "coverage": {
            "repositories": len(snapshots),
            "states": dict(sorted(coverage_states.items())),
        },
        "repositories": repository_records,
        "views": fleet_views,
        "extensions": {},
    }


def extract_view(snapshot: Mapping[str, Any], view: str) -> JsonObject:
    """Return a portable envelope for one named repository or fleet view."""

    if view not in VIEW_NAMES:
        raise ContractError(f"unsupported view {view!r}; choose one of {', '.join(VIEW_NAMES)}")
    if snapshot.get("schema") not in {READ_MODEL_SCHEMA, FLEET_SCHEMA}:
        raise ContractError("query input is not an Observatory repository or fleet snapshot")
    views = _require_object(snapshot.get("views"), "snapshot.views")
    if view not in views:
        raise ContractError(f"snapshot does not contain the {view!r} view")
    scope = "repository" if snapshot["schema"] == READ_MODEL_SCHEMA else "fleet"
    subject = (
        snapshot["repository"]["repository"] if scope == "repository" else "egohygiene"
    )
    return {
        "schema": VIEW_SCHEMA,
        "contract_version": CONTRACT_VERSION,
        "view": view,
        "scope": scope,
        "subject": subject,
        "snapshot_id": snapshot["snapshot_id"],
        "data": deepcopy(views[view]),
    }


def _changed_paths(before: Any, after: Any, prefix: str = "") -> list[str]:
    if type(before) is not type(after):
        return [prefix or "$root"]
    if isinstance(before, dict):
        paths = []
        for key in sorted(set(before) | set(after)):
            path = f"{prefix}.{key}" if prefix else key
            if key not in before or key not in after:
                paths.append(path)
            else:
                paths.extend(_changed_paths(before[key], after[key], path))
        return paths
    if isinstance(before, list):
        return [] if before == after else [prefix or "$root"]
    return [] if before == after else [prefix or "$root"]


def _collection_delta(
    before: Sequence[Mapping[str, Any]], after: Sequence[Mapping[str, Any]]
) -> JsonObject:
    old = {item["id"]: item for item in before}
    new = {item["id"]: item for item in after}
    shared = sorted(set(old) & set(new))
    return {
        "added": sorted(set(new) - set(old)),
        "removed": sorted(set(old) - set(new)),
        "changed": [
            {"id": identifier, "fields": _changed_paths(old[identifier], new[identifier])}
            for identifier in shared
            if old[identifier] != new[identifier]
        ],
    }


def compare_snapshots(before: Mapping[str, Any], after: Mapping[str, Any]) -> JsonObject:
    """Compare two snapshots of the same repository without inventing causality."""

    if before.get("schema") != READ_MODEL_SCHEMA or after.get("schema") != READ_MODEL_SCHEMA:
        raise ContractError("compare inputs must be Observatory repository read models")
    repository = before["repository"]["repository"]
    if after["repository"]["repository"] != repository:
        raise ContractError("compare inputs must represent the same repository")
    graph_before = before["graph"]
    graph_after = after["graph"]
    views = []
    for name in VIEW_NAMES:
        old_digest = digest(before["views"][name])
        new_digest = digest(after["views"][name])
        views.append(
            {
                "view": name,
                "changed": old_digest != new_digest,
                "before_digest": old_digest,
                "after_digest": new_digest,
            }
        )
    return {
        "schema": COMPARE_SCHEMA,
        "contract_version": CONTRACT_VERSION,
        "repository": repository,
        "before": {
            "snapshot_id": before["snapshot_id"],
            "represented_commit": before["represented_commit"],
            "observed_at": before["observed_at"],
        },
        "after": {
            "snapshot_id": after["snapshot_id"],
            "represented_commit": after["represented_commit"],
            "observed_at": after["observed_at"],
        },
        "entities": _collection_delta(graph_before["entities"], graph_after["entities"]),
        "relationships": _collection_delta(
            graph_before["relationships"], graph_after["relationships"]
        ),
        "events": _collection_delta(graph_before["events"], graph_after["events"]),
        "views": views,
    }


def repository_slug(repository: str) -> str:
    """Return the stable filesystem-safe slug for a canonical repository name."""

    if not _REPOSITORY_PATTERN.fullmatch(repository):
        raise ContractError(f"cannot create a snapshot path for {repository!r}")
    return repository.replace("/", "--")


def json_text(value: Any) -> str:
    """Serialize a durable artifact with stable keys and a final newline."""

    return json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n"


def write_json(path: str | Path, value: Any) -> None:
    """Atomically write a deterministic JSON artifact."""

    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{destination.name}.", dir=destination.parent
    )
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(json_text(value))
        os.replace(temporary_name, destination)
    except BaseException:
        try:
            os.unlink(temporary_name)
        except FileNotFoundError:
            pass
        raise


def build_bundle(projections: Iterable[Mapping[str, Any]]) -> tuple[list[JsonObject], JsonObject]:
    """Build repository snapshots and their fleet index in stable order."""

    repositories = [build_repository_snapshot(item) for item in projections]
    repositories.sort(key=lambda item: item["repository"]["repository"])
    return repositories, build_fleet_snapshot(repositories)
