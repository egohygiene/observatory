"""Bounded structural queries over independently admitted public audit models.

These queries describe supplied records. A missing record is never evidence
of resolution, and categorical recurrence is never an inferred common cause.
"""

from __future__ import annotations

from copy import deepcopy
import importlib.util
from pathlib import Path

_spec = importlib.util.spec_from_file_location("observatory_audit_query_contract", Path(__file__).with_name("audits_contract.py"))
contract = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(contract)
shared = contract.shared

PATTERNS_SCHEMA = "egohygiene.observatory.fleet-audit-patterns/v1"
COMPARISON_SCHEMA = "egohygiene.observatory.fleet-audits-comparison/v1"
VERSION = contract.VERSION


def _source(value):
    return {"schema": value["schema"], "digest": value["digest"], "as_of": value["as_of"],
        "repositories": [{"repository": item["repository"]["full_name"], "represented_commit": item["represented_commit"]}
            for item in value["repositories"]]}


def _records(value):
    reports, findings = {}, {}
    for repository in value["repositories"]:
        name = repository["repository"]["full_name"]
        for report in repository["runs"]:
            reports[f"{name}:{report['id']}"] = (name, report)
            for finding in report["findings"]:
                findings[finding["key"]] = (name, report, finding)
    return reports, findings


def query_fleet_audits(value, *, admission_root=contract.DEFAULT_ROOT):
    """Return cross-repository categorical groups with exact source finding keys."""
    contract.validate_fleet(value, admission_root=admission_root)
    _reports, findings = _records(value)
    groups = {}
    for key, (repository, report, finding) in sorted(findings.items()):
        categories = {name: finding[name] for name in ("classification", "nature", "area")}
        profile = finding["source_profile"]
        categories["source_profile"] = f"{profile['id']}@{profile['version']}"
        member = {"finding_key": key, "repository": repository, "audit_id": report["id"],
            "revision_status": report["revision_status"], "freshness": report["freshness"], "status": finding["status"]}
        for dimension, category in categories.items():
            groups.setdefault((dimension, category), []).append(member)
    patterns = []
    for (dimension, category), members in sorted(groups.items()):
        repositories = sorted({item["repository"] for item in members})
        if len(repositories) >= 2:
            patterns.append({"dimension": dimension, "value": category, "repositories": repositories,
                "finding_count": len(members), "members": members})
    result = shared.seal({"schema": PATTERNS_SCHEMA, "contract_version": VERSION, "visibility": "public",
        "as_of": value["as_of"], "admission": deepcopy(value["admission"]), "source": _source(value),
        "semantics": "categorical-source-grouping-no-inferred-common-cause", "patterns": patterns})
    return validate(result, admission_root=admission_root)


def _changes(before, after, kind):
    result = []
    for key in sorted(before.keys() | after.keys()):
        previous = before.get(key)
        current = after.get(key)
        left = previous[-1] if previous is not None else None
        right = current[-1] if current is not None else None
        if left == right:
            continue
        fields = sorted(name for name in (set(left or {}) | set(right or {}))
            if left is None or right is None or left.get(name) != right.get(name))
        row = current or previous
        result.append({"key": key, "repository": row[0], "kind": kind,
            "observation": "after-only" if previous is None else "before-only" if current is None else "changed",
            "changed_fields": fields, "before_sha256": contract.digest(left) if left is not None else None,
            "after_sha256": contract.digest(right) if right is not None else None})
    return result


def compare_fleet_audits(before, after, *, admission_root=contract.DEFAULT_ROOT):
    """Compare exact compatible fleet scopes without guessing continuity/resolution.

    Stable keys contain repository, authored audit ID and authored finding ID.
    A different authored run is a different record unless its own typed history
    explicitly relates findings. Neither timestamp ordering nor omission links it.
    """
    contract.validate_fleet(before, admission_root=admission_root)
    contract.validate_fleet(after, admission_root=admission_root)
    shared.require(before["admission"] == after["admission"]
        and shared.instant(before["as_of"]) <= shared.instant(after["as_of"]))
    left_repositories = before["repositories"]
    right_repositories = after["repositories"]
    shared.require([item["repository"]["full_name"] for item in left_repositories]
        == [item["repository"]["full_name"] for item in right_repositories])
    for previous, current in zip(left_repositories, right_repositories):
        shared.require(previous["source_owner"] == current["source_owner"]
            and previous["freshness_policy"] == current["freshness_policy"])
    previous_reports, previous_findings = _records(before)
    current_reports, current_findings = _records(after)
    changes = [*_changes(previous_reports, current_reports, "report"),
        *_changes(previous_findings, current_findings, "finding")]
    changes.sort(key=lambda item: (item["kind"], item["key"]))
    explicit_history = [{"finding_key": finding["key"], "repository": repository,
        "audit_id": report["id"], "history": deepcopy(finding["history"])}
        for _key, (repository, report, finding) in sorted(current_findings.items())
        if finding["history"]["delta"] != "not-compared"]
    result = shared.seal({"schema": COMPARISON_SCHEMA, "contract_version": VERSION, "visibility": "public",
        "as_of": after["as_of"], "admission": deepcopy(after["admission"]),
        "baseline": _source(before), "current": _source(after),
        "semantics": "structural-record-delta-no-absence-resolution-or-inferred-continuity",
        "changes": changes, "explicit_current_history": explicit_history,
        "counts": {kind: {observation: sum(item["kind"] == kind and item["observation"] == observation for item in changes)
            for observation in ("after-only", "before-only", "changed")} for kind in ("report", "finding")},
        "classification_inventory": {"before": deepcopy(before["summary"]["findings"]["classification"]),
            "after": deepcopy(after["summary"]["findings"]["classification"])}})
    return validate(result, admission_root=admission_root)


def _source_admission(source, as_of, admission_root):
    shared.closed(source, {"schema", "digest", "as_of", "repositories"})
    shared.require(source["schema"] == contract.FLEET_SCHEMA and isinstance(source["digest"], str)
        and shared.base.HASH.fullmatch(source["digest"]) and shared.instant(source["as_of"]) <= as_of
        and isinstance(source["repositories"], list) and len(source["repositories"]) <= shared.MAX_TARGETS)
    selected, rows, allowed = shared.targets(source["repositories"], admission_root)
    shared.require(source["repositories"] == [{"repository": name, "represented_commit": revision}
        for name, revision in selected.items()])
    return selected, rows, allowed


def _key(value, repository, native, *, finding):
    shared.require(isinstance(value, str) and value.startswith(repository + ":"))
    identifier = value[len(repository) + 1:]
    if finding:
        identifier, separator, finding_id = identifier.rpartition(":")
        shared.require(separator)
        native.identifier(finding_id, native.FINDING_ID)
    native.identifier(identifier)


def validate(value, *, admission_root=contract.DEFAULT_ROOT):
    """Validate one sealed derived model without pretending its source was fetched.

    Source digests identify the separately validated fleet inputs. Revalidation
    checks the closed public result, aggregate equalities and declared scope;
    rebuilding from those original inputs is the independent derivation proof.
    """
    shared.require(isinstance(value, dict))
    shared.base.unambiguous(value)
    common = {"schema", "contract_version", "visibility", "as_of", "admission", "semantics", "digest"}
    schema = value.get("schema")
    extra = {"source", "patterns"} if schema == PATTERNS_SCHEMA else {
        "baseline", "current", "changes", "explicit_current_history", "counts", "classification_inventory"}
    shared.closed(value, common | extra)
    shared.require(schema in {PATTERNS_SCHEMA, COMPARISON_SCHEMA}
        and value["contract_version"] == VERSION and value["visibility"] == "public")
    observed = shared.instant(value["as_of"])
    source = value["source"] if schema == PATTERNS_SCHEMA else value["current"]
    selected, rows, allowed = _source_admission(source, observed, admission_root)
    shared.require(source["as_of"] == value["as_of"]
        and value["admission"] == shared.fleet_admission(selected, rows, admission_root)
        and shared.ownership_preflight(value, allowed))
    native, _registry, _owner = contract.owners(admission_root)
    native._privacy(value, True)
    if schema == PATTERNS_SCHEMA:
        shared.require(value["semantics"] == "categorical-source-grouping-no-inferred-common-cause"
            and isinstance(value["patterns"], list))
        identities = []
        for pattern in value["patterns"]:
            shared.closed(pattern, {"dimension", "value", "repositories", "finding_count", "members"})
            dimension, category = pattern["dimension"], pattern["value"]
            shared.require(dimension in {"classification", "nature", "area", "source_profile"})
            native.text(category, 512)
            if dimension in {"classification", "nature"}:
                shared.require(category in (native.CLASSIFICATIONS if dimension == "classification" else native.NATURES))
            elif dimension == "source_profile":
                identifier, separator, version = category.partition("@")
                shared.require(separator and native.PROFILE_ID.fullmatch(identifier) and native.SEMVER.fullmatch(version))
            shared.require(isinstance(pattern["members"], list) and type(pattern["finding_count"]) is int
                and pattern["finding_count"] == len(pattern["members"]))
            keys, repositories = [], set()
            for member in pattern["members"]:
                shared.closed(member, {"finding_key", "repository", "audit_id", "revision_status", "freshness", "status"})
                repository = member["repository"]
                shared.require(repository in selected and member["revision_status"] in {"matched", "different"}
                    and member["freshness"] in {"current", "stale", "unknown"} and member["status"] in native.STATUSES)
                native.identifier(member["audit_id"])
                _key(member["finding_key"], repository, native, finding=True)
                shared.require(member["finding_key"].rsplit(":", 1)[0] == f"{repository}:{member['audit_id']}")
                keys.append(member["finding_key"])
                repositories.add(repository)
            shared.require(keys == sorted(set(keys)) and len(repositories) >= 2
                and pattern["repositories"] == sorted(repositories))
            identities.append((dimension, category))
        shared.require(identities == sorted(set(identities)))
    else:
        shared.require(value["semantics"] == "structural-record-delta-no-absence-resolution-or-inferred-continuity")
        before, _before_rows, _before_allowed = _source_admission(value["baseline"], observed, admission_root)
        shared.require(list(before) == list(selected) and shared.instant(value["baseline"]["as_of"]) <= observed)
        shared.require(isinstance(value["changes"], list))
        identities = []
        counts = {kind: {observation: 0 for observation in ("after-only", "before-only", "changed")}
            for kind in ("report", "finding")}
        for change in value["changes"]:
            shared.closed(change, {"key", "repository", "kind", "observation", "changed_fields", "before_sha256", "after_sha256"})
            kind, observation, repository = change["kind"], change["observation"], change["repository"]
            shared.require(kind in counts and observation in counts[kind] and repository in selected)
            _key(change["key"], repository, native, finding=kind == "finding")
            fields = change["changed_fields"]
            shared.require(isinstance(fields, list) and fields and fields == sorted(set(fields)))
            for field in fields:
                shared.require(isinstance(field, str) and __import__("re").fullmatch(r"[a-z][a-z_]{0,63}", field))
            for name in ("before_sha256", "after_sha256"):
                shared.require(change[name] is None or isinstance(change[name], str) and shared.base.HASH.fullmatch(change[name]))
            shared.require((change["before_sha256"] is None) == (observation == "after-only")
                and (change["after_sha256"] is None) == (observation == "before-only")
                and change["before_sha256"] != change["after_sha256"])
            counts[kind][observation] += 1
            identities.append((kind, change["key"]))
        shared.require(identities == sorted(set(identities))
            and shared.canonical(value["counts"]) == shared.canonical(counts))
        shared.require(isinstance(value["explicit_current_history"], list))
        history_keys = []
        for claim in value["explicit_current_history"]:
            shared.closed(claim, {"finding_key", "repository", "audit_id", "history"})
            shared.require(claim["repository"] in selected)
            native.identifier(claim["audit_id"])
            _key(claim["finding_key"], claim["repository"], native, finding=True)
            shared.require(claim["finding_key"].rsplit(":", 1)[0] == f"{claim['repository']}:{claim['audit_id']}")
            history = shared.closed(claim["history"], {"delta", "prior_audit_id", "prior_finding_id", "evidence_classification", "evidence_refs"})
            shared.require(history["delta"] in native.DELTAS and history["delta"] != "not-compared"
                and history["evidence_classification"] in native.LABELS)
            native.strings(history["evidence_refs"], 64)
            for name, pattern in (("prior_audit_id", native.ID), ("prior_finding_id", native.FINDING_ID)):
                shared.require(history[name] is None or isinstance(history[name], str) and pattern.fullmatch(history[name]))
            shared.require(history["prior_finding_id"] is None or history["prior_audit_id"] is not None)
            if history["delta"] in {"unchanged", "improved", "regressed", "resolved"}:
                shared.require(history["prior_audit_id"] is not None and history["prior_finding_id"] is not None
                    and bool(history["evidence_refs"]))
            if history["delta"] == "resolved":
                shared.require(history["evidence_classification"] == "observed")
            history_keys.append(claim["finding_key"])
        shared.require(history_keys == sorted(set(history_keys)))
        inventories = shared.closed(value["classification_inventory"], {"before", "after"})
        for inventory in inventories.values():
            shared.closed(inventory, native.CLASSIFICATIONS)
            shared.require(all(type(count) is int and count >= 0 for count in inventory.values()))
    shared.verify_seal(value)
    return value
