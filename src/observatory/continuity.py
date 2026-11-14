"""Observe allowlisted continuity metadata without reading handoff contents."""
from __future__ import annotations

from copy import deepcopy
from pathlib import Path

from . import public_reviews as shared

SCHEMA = "egohygiene.observatory.fleet-continuity/v1"
INPUT_SCHEMA = "egohygiene.observatory.continuity-observation/v1"
VERSION = "1.0.0-alpha.1"
OWNER_PIN = {
    "repository": "egohygiene/aether", "revision": "6f230affe30719f222c354c522db5c247559e47f",
    "path": "catalog/schemas/aether.repository-continuity.v1.schema.json",
    "sha256": "a725e004fe0db2bf96a968c6e3f300d37ecf8b00b9a0923be5c5f4c529655916",
    "contract": "aether.repository-continuity/v1", "version": "1.0.0", "lifecycle": "draft",
}
POLICY_PIN = {
    "repository": "egohygiene/hygiene", "revision": "a05b14f8b9e2772124f879f818e09a911e996ad8",
    "path": "catalog/repository-continuity-policy.json", "version": "1.0.0-alpha.1",
    "sha256": "2f694682df641f9c9741d79c7d23bca2ae5bd0d1e3aa6ca00cb31db17e0e2e2c",
    "status": "proposed", "mode": "observe",
}


def enum(value, choices):
    shared.require(isinstance(value, str) and value in choices)
    return value


def count(value):
    shared.require(value is None or (type(value) is int and 0 <= value <= 1000000))
    return value


def optional_instant(value):
    if value is not None:
        shared.instant(value)
    return value


def optional_commit(value):
    shared.require(value is None or (isinstance(value, str) and shared.base.SHA.fullmatch(value)))
    return value


def source_header(value, repository, allowed, as_of):
    """Validate metadata headers only after caller-selected public admission."""
    shared.base.unambiguous(value)
    shared.require(value["repository"] == repository)
    shared.require(isinstance(value["represented_commit"], str) and shared.base.SHA.fullmatch(value["represented_commit"]))
    observed = shared.instant(value["observed_at"])
    expires = shared.instant(value["valid_until"])
    shared.require(observed <= shared.instant(as_of) and expires >= observed)
    shared.public_url(value["source_url"], allowed)
    shared.closed(value["producer"], {"id", "version"})
    shared.text(value["producer"]["id"], 128)
    shared.text(value["producer"]["version"], 64)
    return "stale" if shared.instant(as_of) > expires else "fresh"


def validate_observation(value, repository, allowed, as_of):
    shared.closed(value, {"schema", "repository", "represented_commit", "observed_at", "valid_until",
                          "source_url", "producer", "file", "structure", "pointer", "declared", "git", "live", "applicability"})
    shared.require(value["schema"] == INPUT_SCHEMA)
    freshness = source_header(value, repository, allowed, as_of)
    file = shared.closed(value["file"], {"presence", "exact_case", "contract", "version"})
    enum(file["presence"], {"present", "absent", "unknown"})
    shared.require(file["exact_case"] is None or type(file["exact_case"]) is bool)
    for key in ("contract", "version"):
        if file[key] is not None:
            shared.text(file[key], 128)
    structure = shared.closed(value["structure"], {"status", "error_count", "warning_count", "validator"})
    enum(structure["status"], {"valid", "invalid", "not-run", "unavailable", "unsupported"})
    count(structure["error_count"]); count(structure["warning_count"])
    if structure["validator"] is not None:
        shared.text(structure["validator"], 128)
    if structure["status"] == "valid":
        shared.require(structure["error_count"] == 0 and structure["validator"] is not None and file["presence"] == "present")
    if structure["status"] == "invalid":
        shared.require(type(structure["error_count"]) is int and structure["error_count"] > 0)
    pointer = shared.closed(value["pointer"], {"presence", "managed_block_count"})
    enum(pointer["presence"], {"present", "absent", "unknown"})
    count(pointer["managed_block_count"])
    if pointer["presence"] == "absent":
        shared.require(pointer["managed_block_count"] == 0)
    if pointer["presence"] == "present":
        shared.require(type(pointer["managed_block_count"]) is int and pointer["managed_block_count"] > 0)
    declared = shared.closed(value["declared"], {"status", "updated_at", "reviewed_at", "base_revision"})
    enum(declared["status"], {"active", "stale", "provisional", "unknown"})
    optional_instant(declared["updated_at"]); optional_instant(declared["reviewed_at"])
    optional_commit(declared["base_revision"])
    git = shared.closed(value["git"], {"status", "file_commit", "file_commit_at"})
    enum(git["status"], {"verified", "unverified", "unavailable"})
    optional_commit(git["file_commit"]); optional_instant(git["file_commit_at"])
    if git["status"] == "verified":
        shared.require(git["file_commit"] is not None and git["file_commit_at"] is not None)
    live = shared.closed(value["live"], {"status", "verified_at"})
    enum(live["status"], {"verified", "unverified", "unavailable"})
    optional_instant(live["verified_at"])
    if live["status"] == "verified":
        shared.require(live["verified_at"] is not None)
    applicability = shared.closed(value["applicability"], {"status", "exception_reference"})
    enum(applicability["status"], {"applicable", "exempt", "unknown", "unsupported"})
    if applicability["exception_reference"] is not None:
        shared.public_url(applicability["exception_reference"], allowed)
    if applicability["status"] == "exempt":
        shared.require(applicability["exception_reference"] is not None)
    if file["presence"] != "present":
        shared.require(structure["status"] != "valid")
    result = deepcopy(value)
    result["observation_freshness"] = freshness
    return result


def posture(record):
    """Observation posture is not conformance, semantic truth or live freshness."""
    if record is None:
        return "unverifiable"
    applicability = record["applicability"]["status"]
    if applicability == "exempt":
        return "exempt"
    if applicability == "unsupported" or record["structure"]["status"] == "unsupported":
        return "unsupported"
    file = record["file"]
    if file["presence"] == "absent":
        return "absent"
    if file["presence"] == "unknown":
        return "unverifiable"
    if file["contract"] != OWNER_PIN["contract"] or file["version"] != OWNER_PIN["version"]:
        return "unsupported"
    if record["declared"]["status"] == "stale":
        return "stale-declared"
    if (file["exact_case"] is False or record["structure"]["status"] == "invalid"
            or record["pointer"]["presence"] == "absent"
            or (record["pointer"]["managed_block_count"] is not None and record["pointer"]["managed_block_count"] > 1)):
        return "invalid"
    if record["declared"]["status"] == "provisional":
        return "provisional"
    if (file["exact_case"] is True and record["structure"]["status"] == "valid"
            and record["pointer"]["presence"] == "present" and record["pointer"]["managed_block_count"] == 1):
        return "valid"
    return "unverifiable"


def build_continuity_view(observations, *, repositories, as_of, admission_root=shared.DEFAULT_ROOT):
    """Build deterministic public metadata from an explicit selector inventory.

    Private/unadmitted wrappers are discarded before validation, identities,
    counts or digests. Missing observation is not a missing file observation.
    """
    shared.instant(as_of)
    selected, rows, allowed = shared.targets(repositories, admission_root)
    wrappers = list(observations)
    output = []
    for repository, revision in selected.items():
        records = {}
        for raw, _metadata in shared.wrappers(wrappers, repository, allowed):
            if not isinstance(raw, dict) or raw.get("repository") != repository:
                continue
            if not shared.ownership_preflight(raw, allowed):
                continue
            record = validate_observation(raw, repository, allowed, as_of)
            key = (record["represented_commit"], record["observed_at"])
            shared.require(key not in records or records[key] == record)
            records[key] = record
            shared.require(len(records) <= shared.MAX_RECORDS)
        ordered = [records[key] for key in sorted(records)]
        current = [item for item in ordered if item["represented_commit"] == revision]
        latest = current[-1] if current else None
        output.append({"repository": shared.repository_identity(rows[repository]), "represented_commit": revision,
            "posture": posture(latest), "observation_freshness": latest["observation_freshness"] if latest else "unknown",
            "collection": "supplied" if current else "other-revision-only" if ordered else "unavailable",
            "latest": latest, "observations": ordered})
    return shared.seal({"schema": SCHEMA, "contract_version": VERSION, "visibility": "public", "as_of": as_of,
        "admission": shared.fleet_admission(selected, rows, admission_root), "owner_contract": OWNER_PIN,
        "policy": POLICY_PIN, "repositories": output})


def validate_view(value, *, admission_root=shared.DEFAULT_ROOT):
    """Rebuild a serialized view so a self-authored seal cannot forge fields."""
    shared.closed(value, {"schema", "contract_version", "visibility", "as_of", "admission", "owner_contract", "policy", "repositories", "digest"})
    shared.require(isinstance(value["repositories"], list))
    targets, wrappers = [], []
    for row in value["repositories"]:
        shared.closed(row, {"repository", "represented_commit", "posture", "observation_freshness", "collection", "latest", "observations"})
        identity = shared.plain(row["repository"])
        targets.append({"repository": identity.get("full_name"), "represented_commit": row["represented_commit"]})
        shared.require(isinstance(row["observations"], list))
        for item in row["observations"]:
            raw = deepcopy(shared.plain(item))
            raw.pop("observation_freshness", None)
            wrappers.append({"visibility": "public", "repository": identity.get("full_name"), "evidence": raw})
    expected = build_continuity_view(wrappers, repositories=targets, as_of=value["as_of"], admission_root=admission_root)
    shared.require(value == expected)
    return deepcopy(value)
