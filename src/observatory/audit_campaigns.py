"""Public selected-row queries over byte-pinned Reflector campaign transports.

The transport describes orchestration and supplied report references. It does
not prove report content, successful checks, human approval or materialization.
"""

from __future__ import annotations

from copy import deepcopy
import importlib.util
from pathlib import Path

_spec = importlib.util.spec_from_file_location("observatory_campaign_public_reviews", Path(__file__).with_name("public_reviews.py"))
shared = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(shared)

SCHEMA = "egohygiene.observatory.fleet-audit-campaigns/v1"
VERSION = "1.0.0-alpha.1"
LOCK = "reflector.audit-campaign.v1.lock.json"
LOCK_SHA256 = "433d03dfe2729228e577fe29e8201e8a881101397f83776e0e35f4998f769222"
HELPER = "reflector/schemas/audit_campaign.py"
DEFAULT_ROOT = shared.DEFAULT_ROOT


def owner(root=DEFAULT_ROOT):
    lock, files = shared.owner_resources(root, LOCK, LOCK_SHA256)
    shared.require(lock["owner"] == "egohygiene/reflector")
    native = shared.load_owner(files[HELPER]["local"], "observatory_reflector_campaign_transport")
    return native, {"owner": lock["owner"], "revision": lock["revision"], "lock_sha256": LOCK_SHA256,
        "schema": native.MANIFEST, "contract_version": native.VERSION}


def _public_scope(value, allowed):
    return (isinstance(value, dict) and value.get("visibility") == "public"
        and not {"visibility", "repositories"} & getattr(value, "duplicate_keys", set())
        and isinstance(value.get("repositories"), list))


def _fields(value, names):
    # Ambiguity in excluded transport fields is not selected-query evidence.
    shared.require(isinstance(value, dict) and not set(names) & getattr(value, "duplicate_keys", set()))
    return {name: deepcopy(value[name]) for name in names}


def _reference(metadata, allowed):
    wrapper = metadata["wrapper"]
    shared.require(not {"visibility", "repository", "source", "evidence"} & getattr(wrapper, "duplicate_keys", set()))
    artifact = wrapper.get("source")
    if artifact is None:
        return None
    result = _fields(artifact, ("repository", "revision", "path", "url"))
    shared.require(result["repository"] in allowed and isinstance(result["revision"], str)
        and shared.base.SHA.fullmatch(result["revision"]))
    path = shared.text(result["path"], 512)
    shared.require(not path.startswith("/") and "\\" not in path and "%" not in path
        and all(part not in {"", ".", "..", ".git"} for part in path.split("/"))
        and result["url"] == f"https://github.com/{result['repository']}/blob/{result['revision']}/{path}")
    shared.public_url(result["url"], allowed)
    return result


def _project(manifest, selected):
    result = _fields(manifest, ("campaign_id", "observed_at", "mode", "status",
        "analysis_execution", "profiles", "passes", "candidate_backlog"))
    shared.require(not {"generator", "owner_inputs"} & getattr(manifest, "duplicate_keys", set()))
    result["generator"] = _fields(manifest["generator"], ("repository", "revision", "immutable"))
    result["owner_inputs"] = {name: _fields(pin, ("repository", "revision", "tree"))
        for name, pin in _fields(manifest["owner_inputs"], ("aether_audit", "aether_sanity")).items()}
    rows = []
    for row in manifest["repositories"]:
        if (not isinstance(row, dict) or "repository" in getattr(row, "duplicate_keys", set())
                or not isinstance(row.get("repository"), str) or row.get("repository") not in selected):
            continue
        projected = _fields(row, ("repository", "represented_commit", "source_observed_at", "state", "reason", "resume"))
        projected["revision_status"] = ("unknown" if row["represented_commit"] is None else
            "matched" if row["represented_commit"] == selected[row["repository"]] else "different")
        shared.require(not {"reports", "executions", "source_capabilities"} & getattr(row, "duplicate_keys", set())
            and isinstance(row["reports"], list) and len(row["reports"]) <= 16)
        projected["reports"] = []
        for report in row["reports"]:
            shared.require(not {"findings_count", "profiles"} & getattr(report, "duplicate_keys", set()))
            projected["reports"].append({**_fields(report, ("kind", "owner_schema", "source_revision",
                "source_path", "canonical_url", "completion")), "declared_findings_count": report["findings_count"],
                "profiles": deepcopy(report.get("profiles", []))})
        projected["executions"] = []
        executions = row.get("executions", [])
        shared.require(isinstance(executions, list) and len(executions) <= 33)
        for execution in executions:
            shared.require(not {"report"} & getattr(execution, "duplicate_keys", set()))
            projected["executions"].append({**_fields(execution, ("job_id", "state", "reason", "started_at", "completed_at")),
                "report": _fields(execution["report"], ("kind", "source_revision", "source_path")) if execution["report"] is not None else None})
        capabilities = row.get("source_capabilities")
        projected["source_capabilities"] = _fields(capabilities, ("state", "observed_at")) if capabilities is not None else None
        rows.append(projected)
    result["repositories"] = sorted(rows, key=lambda row: row["repository"])
    return result


def _validate_projection(value, selected, allowed, native, boundary):
    shared.closed(value, {"campaign_id", "observed_at", "mode", "status", "analysis_execution", "profiles", "passes",
        "candidate_backlog", "generator", "owner_inputs", "repositories"})
    shared.base.unambiguous(value)
    shared.require(shared.ownership_preflight(value, allowed))
    native.match(value["campaign_id"], native.TOKEN)
    observed = shared.instant(value["observed_at"])
    shared.require(observed <= boundary and value["mode"] in {"plan", "index", "discover", "run"}
        and value["status"] in {"planned", "indexed", "discovered", "partial", "cancelled"}
        and value["analysis_execution"] in {"external-captures-only", "local-adapter-requested", "not-executed"}
        and value["candidate_backlog"] in {"disabled", "proposed"})
    generator = shared.closed(value["generator"], {"repository", "revision", "immutable"})
    shared.require(generator["repository"] == "egohygiene/reflector" and type(generator["immutable"]) is bool)
    if generator["revision"] is not None:
        native.match(generator["revision"], native.REVISION)
    shared.require(not generator["immutable"] or generator["revision"] is not None)
    shared.closed(value["owner_inputs"], {"aether_audit", "aether_sanity"})
    for pin in value["owner_inputs"].values():
        shared.closed(pin, {"repository", "revision", "tree"})
        shared.require(pin["repository"] == "egohygiene/aether")
        native.match(pin["revision"], native.REVISION); native.match(pin["tree"], native.REVISION)
    profiles = shared.closed(value["profiles"], {"registry_version", "registry_sha256", "requested", "resolved"})
    shared.require(isinstance(profiles["registry_version"], str) and __import__("re").fullmatch(r"[0-9]+\.[0-9]+\.[0-9]+", profiles["registry_version"]))
    native.match(profiles["registry_sha256"], native.SHA256)
    native.profile_requests(profiles["requested"]); native.profile_requests(profiles["resolved"])
    shared.require(isinstance(value["passes"], list) and len(value["passes"]) == len(native.PASS_IDS))
    for item, expected in zip(value["passes"], native.PASS_IDS):
        shared.closed(item, {"id", "state"})
        shared.require(item["id"] == expected and item["state"] in {"selected", "resolved", "declared", "not-executed",
            "external-captures", "indexed", "partial", "disabled", "not-requested"})
    shared.require(isinstance(value["repositories"], list) and 1 <= len(value["repositories"]) <= 64)
    names = []
    def report_reference(report):
        shared.require(report["kind"] in {"audit", "sanity"})
        if report["source_revision"] is not None:
            native.match(report["source_revision"], native.REVISION)
        shared.require(native.relative(report["source_path"]).endswith(".json"))
    for row in value["repositories"]:
        shared.closed(row, {"repository", "represented_commit", "source_observed_at", "revision_status", "state", "reason", "resume", "reports", "executions", "source_capabilities"})
        shared.require(row["repository"] in selected and row["state"] in native.STATES and row["resume"] in {"new", "unchanged", "not-inspected"}
            and row["reason"] in {None, "source-not-selected", "source-unavailable", "reports-not-selected", "report-unavailable",
                "report-incompatible", "report-boundary", "report-limit", "budget-exhausted", "cancelled"})
        names.append(row["repository"])
        if row["represented_commit"] is not None:
            native.match(row["represented_commit"], native.REVISION)
            shared.require(shared.instant(row["source_observed_at"]) <= observed)
        else:
            shared.require(row["source_observed_at"] is None)
        shared.require(row["revision_status"] == ("unknown" if row["represented_commit"] is None else
            "matched" if row["represented_commit"] == selected[row["repository"]] else "different"))
        shared.require(isinstance(row["reports"], list) and len(row["reports"]) <= 16)
        for report in row["reports"]:
            shared.closed(report, {"kind", "owner_schema", "source_revision", "source_path", "canonical_url", "completion", "declared_findings_count", "profiles"})
            report_reference(report)
            shared.require(report["owner_schema"] == {"audit": "aether.repository-audit-report/v1", "sanity": "egohygiene.architecture-coherence-review/v1"}[report["kind"]]
                and report["completion"] in {"complete", "partial", "blocked", "failed", "unsupported", "not_applicable", "unknown"}
                and report["canonical_url"] == (f"https://github.com/{row['repository']}/blob/{report['source_revision']}/{report['source_path']}" if report["source_revision"] else None))
            count = report["declared_findings_count"]
            shared.require(count is None if report["kind"] == "sanity" else type(count) is int and 0 <= count <= 4096)
            shared.require(isinstance(report["profiles"], list) and len(report["profiles"]) <= 32)
            if report["profiles"]:
                native.profile_requests(report["profiles"])
        shared.require(isinstance(row["executions"], list) and len(row["executions"]) <= 33)
        for execution in row["executions"]:
            shared.closed(execution, {"job_id", "state", "reason", "started_at", "completed_at", "report"})
            shared.require(isinstance(execution["job_id"], str) and __import__("re").fullmatch(r"audit:[a-z][a-z0-9-]{0,63}|sanity:coherence", execution["job_id"])
                and execution["state"] in {"blocked", "failed", "partial", "complete", "resumed"}
                and execution["reason"] in {None, "source-or-isolation-unavailable", "budget-exhausted", "adapter-or-report-denied", "isolation-unavailable"})
            for name in ("started_at", "completed_at"):
                shared.require(execution[name] is None or shared.instant(execution[name]) <= observed)
            if execution["report"] is not None:
                shared.closed(execution["report"], {"kind", "source_revision", "source_path"}); report_reference(execution["report"])
            shared.require(execution["state"] not in {"complete", "resumed"} or execution["report"] is not None and execution["completed_at"] is not None)
        capabilities = row["source_capabilities"]
        if capabilities is not None:
            shared.closed(capabilities, {"state", "observed_at"})
            shared.require(capabilities["state"] in {"captured", "partial"} and shared.instant(capabilities["observed_at"]) <= observed)
    shared.require(names == sorted(set(names)))
    shared.require(value["status"] != "indexed" or value["mode"] in {"index", "run"} and all(row["state"] == "indexed" for row in value["repositories"]))


def build_fleet_audit_campaigns(evidence_wrappers, *, repositories, as_of, admission_root=DEFAULT_ROOT):
    selected, rows, allowed = shared.targets(repositories, admission_root)
    boundary = shared.instant(as_of)
    native, source_owner = owner(admission_root)
    campaigns, identifiers = [], set()
    supplied = shared.wrappers(evidence_wrappers, "egohygiene/reflector", allowed) if selected else ()
    for raw, transport in supplied:
        if not _public_scope(raw, allowed):
            continue
        # Selection precedes query identifiers, public counters and hashes.
        chosen = [row for row in raw["repositories"] if isinstance(row, dict)
            and "repository" not in getattr(row, "duplicate_keys", set())
            and isinstance(row.get("repository"), str) and row.get("repository") in selected]
        if not chosen:
            continue
        shared.require(len(campaigns) < shared.MAX_RECORDS)
        header = _fields(raw, ("schema", "contract_version", "organization", "mutation_authority"))
        shared.require(header == {"schema": native.MANIFEST, "contract_version": native.VERSION,
            "organization": "egohygiene", "mutation_authority": "none"})
        projection = _project(raw, selected)
        _validate_projection(projection, selected, allowed, native, boundary)
        shared.require(projection["campaign_id"] not in identifiers)
        identifiers.add(projection["campaign_id"])
        campaigns.append({"campaign": projection, "projection_sha256": shared.digest(projection),
            "input_kind": transport["input_kind"], "raw_checksum": "withheld-whole-manifest",
            "source_reference": _reference(transport, allowed)})
    campaigns.sort(key=lambda item: item["campaign"]["campaign_id"])
    result = {"schema": SCHEMA, "contract_version": VERSION, "visibility": "public", "as_of": as_of,
        "admission": shared.fleet_admission(selected, rows, admission_root), "source_owner": source_owner,
        "repositories": [{"repository": name, "represented_commit": revision} for name, revision in selected.items()],
        "campaigns": campaigns, "semantics": "declared-orchestration-only-selected-public-row-projection",
        "evidence": {"state": "supplied" if campaigns else "unavailable", "campaign_count": len(campaigns),
            "public_inputs_sha256": shared.digest([item["projection_sha256"] for item in campaigns])}}
    return validate(shared.seal(result), admission_root=admission_root)


def validate(value, *, admission_root=DEFAULT_ROOT):
    shared.closed(value, {"schema", "contract_version", "visibility", "as_of", "admission", "source_owner",
        "repositories", "campaigns", "semantics", "evidence", "digest"})
    shared.require(value["schema"] == SCHEMA and value["contract_version"] == VERSION and value["visibility"] == "public"
        and value["semantics"] == "declared-orchestration-only-selected-public-row-projection")
    selected, rows, allowed = shared.targets(value["repositories"], admission_root)
    shared.require(value["repositories"] == [{"repository": name, "represented_commit": revision} for name, revision in selected.items()]
        and value["admission"] == shared.fleet_admission(selected, rows, admission_root))
    boundary = shared.instant(value["as_of"])
    native, source_owner = owner(admission_root)
    shared.require(value["source_owner"] == source_owner and isinstance(value["campaigns"], list)
        and len(value["campaigns"]) <= shared.MAX_RECORDS)
    identifiers = []
    for item in value["campaigns"]:
        shared.closed(item, {"campaign", "projection_sha256", "input_kind", "raw_checksum", "source_reference"})
        manifest = item["campaign"]
        _validate_projection(manifest, selected, allowed, native, boundary)
        shared.require(item["projection_sha256"] == shared.digest(manifest) and item["input_kind"] in {"raw-json", "structured"}
            and item["raw_checksum"] == "withheld-whole-manifest")
        source = item["source_reference"]
        if source is not None:
            shared.closed(source, {"repository", "revision", "path", "url"})
            shared.require(source["repository"] in allowed and isinstance(source["revision"], str)
                and shared.base.SHA.fullmatch(source["revision"]))
            path = shared.text(source["path"], 512)
            shared.require(not path.startswith("/") and "\\" not in path and "%" not in path
                and all(part not in {"", ".", "..", ".git"} for part in path.split("/"))
                and source["url"] == f"https://github.com/{source['repository']}/blob/{source['revision']}/{path}")
            shared.public_url(source["url"], allowed)
        identifiers.append(manifest["campaign_id"])
    shared.require(identifiers == sorted(set(identifiers)))
    expected = {"state": "supplied" if identifiers else "unavailable", "campaign_count": len(identifiers),
        "public_inputs_sha256": shared.digest([item["projection_sha256"] for item in value["campaigns"]])}
    shared.require(shared.canonical(value["evidence"]) == shared.canonical(expected))
    shared.verify_seal(value)
    return value


def repository_references(value, *, repository, represented_commit, as_of, admission_root=DEFAULT_ROOT):
    # Authenticate the query target before looking up its rows or campaign IDs.
    shared.admission(repository, admission_root=admission_root)
    validate(value, admission_root=admission_root)
    shared.require(value["as_of"] == as_of)
    selected = {item["repository"]: item["represented_commit"] for item in value["repositories"]}
    shared.require(selected.get(repository) == represented_commit)
    references = []
    for item in value["campaigns"]:
        manifest = item["campaign"]
        row = next((row for row in manifest["repositories"] if row["repository"] == repository), None)
        if row is None:
            continue
        references.append({"campaign_id": manifest["campaign_id"], "observed_at": manifest["observed_at"],
            "mode": manifest["mode"], "status": manifest["status"], "analysis_execution": manifest["analysis_execution"],
            "repository_state": row["state"], "revision_status": "unavailable" if row["represented_commit"] is None else (
                "matched" if row["represented_commit"] == represented_commit else "different"),
            "report_count": len(row["reports"]), "execution_count": len(row.get("executions", [])),
            "manifest_projection_sha256": item["projection_sha256"],
            "source_url": item["source_reference"]["url"] if item["source_reference"] is not None else None})
    return {"state": "supplied" if references else "unavailable", "references": references,
        "reason": None if references else "No compatible orchestration manifests supplied."}
