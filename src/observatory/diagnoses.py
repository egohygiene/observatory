"""Project already-validated, explicitly public diagnosis metadata; never records/logs."""
from __future__ import annotations

from copy import deepcopy
import re

from . import public_reviews as shared
from .continuity import count, enum, optional_commit, source_header

SCHEMA = "egohygiene.observatory.fleet-diagnoses/v1"
INPUT_SCHEMA = "egohygiene.observatory.diagnosis-observations/v1"
EXTENSION = "egohygiene.observatory.diagnoses/v1"
VERSION = "1.0.0-alpha.1"
OWNER_PIN = {
    "repository": "egohygiene/aether", "revision": "e9aa58bb70c8b29179329c1c989aed38c620f7fd",
    "path": "catalog/schemas/aether.diagnosis-record.v1.schema.json",
    "sha256": "e84bb047a51b398e94847b291a9dfefb1aaa38d0f8fefda5764a2f233080abf8",
    "contract": "aether.diagnosis-record/v1", "version": "1.0.0", "lifecycle": "draft",
}
POLICY = {"status": "unavailable", "reference": "https://github.com/egohygiene/hygiene/issues/41",
          "applicability": "source-declared", "enforcement": "none"}
RELATIONS = {"issue", "pull-request", "commit", "adr", "incident", "related-diagnosis", "supersedes", "superseded-by"}


def admitted_record(value):
    """Read disclosure selectors only, before IDs, paths, timestamps or counts."""
    if not isinstance(value, dict) or value.get("sensitivity") != "public":
        return False
    publication = value.get("publication")
    if not isinstance(publication, dict):
        return False
    if ({"sensitivity", "publication"} & getattr(value, "duplicate_keys", set())
            or {"status", "scope"} & getattr(publication, "duplicate_keys", set())):
        return False
    return publication.get("status") == "approved" and publication.get("scope") == "allowlisted-metadata"


def normalize_record(value, repository, allowed):
    shared.base.unambiguous(value)
    shared.closed(value, {"id", "canonical_url", "content_sha256", "contract", "represented_commit",
        "context", "status", "reproduction", "root_cause", "remediation", "validation", "hypothesis_counts",
        "sensitivity", "redactions", "publication", "conformance", "updated_at", "related"})
    shared.require(value["contract"] == OWNER_PIN)
    shared.require(isinstance(value["id"], str) and re.fullmatch(r"diag-[0-9]{8}-[a-z0-9]+(?:-[a-z0-9]+)*", value["id"]))
    shared.require(isinstance(value["content_sha256"], str) and shared.base.HASH.fullmatch(value["content_sha256"]))
    shared.public_url(value["canonical_url"], allowed)
    shared.require(bool(re.fullmatch(r"https://github\.com/" + re.escape(repository)
                   + r"/blob/[0-9a-f]{40}/(?:[^/#]+/)*[^/#]+\.md", value["canonical_url"])))
    optional_commit(value["represented_commit"])
    shared.instant(value["updated_at"])
    enum(value["status"], {"open", "monitoring", "resolved", "closed", "superseded"})
    enum(value["reproduction"], {"not-attempted", "blocked", "not-reproduced", "reproduced", "intermittent"})
    enum(value["root_cause"], {"unknown", "suspected", "confirmed"})
    enum(value["remediation"], {"not-authorized", "not-planned", "planned", "in-progress", "implemented", "reverted", "not-applicable"})
    enum(value["validation"], {"not-run", "partial", "passed", "failed", "blocked"})
    enum(value["redactions"], {"none", "present"})
    enum(value["conformance"], {"valid", "invalid", "unknown", "unavailable", "unsupported"})
    context = shared.closed(value["context"], {"component", "environment", "artifact_version", "correlation_ids"})
    for key in ("component", "environment", "artifact_version"):
        shared.text(context[key], 128)
    shared.require(isinstance(context["correlation_ids"], list) and len(context["correlation_ids"]) <= 128)
    for identifier in context["correlation_ids"]:
        shared.text(identifier, 128)
    shared.require(len(context["correlation_ids"]) == len(set(context["correlation_ids"])))
    hypotheses = shared.closed(value["hypothesis_counts"], {"open", "supported", "confirmed", "eliminated"})
    for number in hypotheses.values():
        count(number)
    publication = shared.closed(value["publication"], {"status", "scope", "reference"})
    shared.require(publication["status"] == "approved" and publication["scope"] == "allowlisted-metadata")
    shared.public_url(publication["reference"], allowed)
    shared.require(isinstance(value["related"], list) and len(value["related"]) <= 128)
    related, seen = [], set()
    for edge in value["related"]:
        shared.closed(edge, {"relation", "target"})
        enum(edge["relation"], RELATIONS)
        shared.public_url(edge["target"], allowed)
        key = (edge["relation"], edge["target"])
        shared.require(key not in seen)
        seen.add(key); related.append(deepcopy(edge))
    result = deepcopy(value)
    result["related"] = sorted(related, key=lambda e:(e["relation"], e["target"]))
    result["context"]["correlation_ids"] = sorted(context["correlation_ids"])
    return result


def normalize_observation(value, repository, allowed, as_of):
    shared.closed(value, {"schema", "repository", "represented_commit", "observed_at", "valid_until",
                          "source_url", "producer", "collection", "applicability", "records"})
    shared.require(value["schema"] == INPUT_SCHEMA)
    freshness = source_header({key:item for key,item in value.items() if key != "records"}, repository, allowed, as_of)
    enum(value["collection"], {"observed", "observed-empty", "partial", "unavailable", "withheld", "unsupported", "not-applicable", "unknown"})
    enum(value["applicability"], {"optional", "recommended", "required", "not-applicable", "unknown", "blocked"})
    # Availability metadata is public; withheld records and their counts are not.
    records, canonical_ids = {}, {}
    if value["collection"] in {"observed", "observed-empty", "partial"}:
        shared.require(isinstance(value["records"], list))
        for raw in value["records"]:
            if not admitted_record(raw) or not shared.ownership_preflight(raw, allowed):
                continue
            record = normalize_record(raw, repository, allowed)
            shared.require(record["canonical_url"] not in canonical_ids
                           or canonical_ids[record["canonical_url"]] == record["id"])
            canonical_ids[record["canonical_url"]] = record["id"]
            shared.require(shared.instant(record["updated_at"]) <= shared.instant(value["observed_at"]))
            key = (record["id"], record["represented_commit"] or "unknown")
            shared.require(key not in records or records[key] == record)
            records[key] = record
            shared.require(len(records) <= shared.MAX_RECORDS)
        if value["collection"] == "observed-empty":
            shared.require(not records)
    result = {key:deepcopy(item) for key,item in value.items() if key != "records"}
    result["records"] = [records[key] for key in sorted(records)]
    result["observation_freshness"] = freshness
    return result


def build_diagnosis_view(observations, *, repositories, as_of, admission_root=shared.DEFAULT_ROOT):
    """Build an optional derived view, without inferring truth or no-defect health."""
    shared.instant(as_of)
    shared.require(isinstance(repositories, list) and isinstance(observations, list))
    selected, rows, allowed = shared.targets(repositories, admission_root)
    wrappers = list(observations)
    output = []
    for repository, revision in selected.items():
        captures = {}
        for raw, _metadata in shared.wrappers(wrappers, repository, allowed):
            if not isinstance(raw, dict) or raw.get("repository") != repository:
                continue
            # Do not preflight record contents until their disclosure selectors pass.
            header = {key:item for key,item in raw.items() if key != "records"}
            if not shared.ownership_preflight(header, allowed):
                continue
            capture = normalize_observation(raw, repository, allowed, as_of)
            key = (capture["represented_commit"], capture["observed_at"])
            shared.require(key not in captures or captures[key] == capture)
            captures[key] = capture
            shared.require(len(captures) <= shared.MAX_RECORDS)
        ordered = [captures[key] for key in sorted(captures)]
        current = [item for item in ordered if item["represented_commit"] == revision]
        latest = current[-1] if current else None
        nodes, edges = [], []
        for record in latest["records"] if latest else []:
            stable_id = f"diagnosis:{repository}:{record['id']}"
            key = stable_id + "@" + (record["represented_commit"] or "unknown")
            nodes.append({"key":key, "stable_id":stable_id, "repository":repository, "metadata":deepcopy(record),
                          "revision_status":"matched" if record["represented_commit"] == revision else "unknown" if record["represented_commit"] is None else "different",
                          "content_integrity":"unverified-source-claim", "publication_authority":"source-declared-not-verified"})
            edges.extend({"source":key, **edge, "assertion":"source-declared"} for edge in record["related"])
        output.append({"repository":shared.repository_identity(rows[repository]), "represented_commit":revision,
            "collection":latest["collection"] if latest else "unavailable", "applicability":latest["applicability"] if latest else "unknown",
            "observation_freshness":latest["observation_freshness"] if latest else "unknown",
            "collection_revision":"matched" if current else "other-revision-only" if ordered else "unavailable",
            "public_record_count":len(nodes), "nodes":nodes, "edges":sorted(edges,key=lambda e:(e["source"],e["relation"],e["target"])),
            "observations":ordered})
    return shared.seal({"schema":SCHEMA, "contract_version":VERSION, "visibility":"public", "as_of":as_of,
        "admission":shared.fleet_admission(selected, rows, admission_root), "owner_contract":OWNER_PIN,
        "policy":POLICY, "repositories":output})


def validate_view(value, *, admission_root=shared.DEFAULT_ROOT):
    shared.closed(value, {"schema", "contract_version", "visibility", "as_of", "admission", "owner_contract", "policy", "repositories", "digest"})
    shared.require(isinstance(value["repositories"], list))
    targets, wrappers = [], []
    for row in value["repositories"]:
        shared.closed(row, {"repository", "represented_commit", "collection", "applicability", "observation_freshness",
            "collection_revision", "public_record_count", "nodes", "edges", "observations"})
        identity = shared.plain(row["repository"])
        targets.append({"repository":identity.get("full_name"), "represented_commit":row["represented_commit"]})
        shared.require(isinstance(row["observations"], list))
        for item in row["observations"]:
            raw = deepcopy(shared.plain(item)); raw.pop("observation_freshness", None)
            wrappers.append({"visibility":"public", "repository":identity.get("full_name"), "evidence":raw})
    expected = build_diagnosis_view(wrappers, repositories=targets, as_of=value["as_of"], admission_root=admission_root)
    shared.require(value == expected)
    return deepcopy(value)


def attach_to_snapshot(snapshot, view):
    """Join through existing Repository Intelligence extensions, not a second graph."""
    from .intelligence import READ_MODEL_SCHEMA, digest
    shared.require(isinstance(snapshot, dict) and snapshot.get("schema") == READ_MODEL_SCHEMA
                   and snapshot.get("visibility") == "public")
    normalized = validate_view(view)
    shared.require(len(normalized["repositories"]) == 1)
    row = normalized["repositories"][0]
    shared.require(row["repository"]["full_name"] == snapshot.get("repository", {}).get("repository")
                   and row["represented_commit"] == snapshot.get("represented_commit"))
    result = deepcopy(snapshot)
    shared.require(isinstance(result.get("extensions"), dict) and EXTENSION not in result["extensions"])
    result["extensions"][EXTENSION] = normalized
    result["snapshot_id"] += ":diagnoses:" + digest(normalized)
    return result
