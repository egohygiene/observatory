"""Build deterministic organization-health snapshots from versioned evidence.

Hygiene owns the repository catalog and policy vocabulary. Evidence producers
such as Egolint own their findings. Observatory validates a deliberately small
consumer boundary, preserves source links, and computes explainable categorical
rollups without rerunning policy checks or inventing a numeric score.
"""

from __future__ import annotations

import hashlib
import json
import re
from collections import Counter
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence
from urllib.parse import urlparse

from .intelligence import ContractError, digest

CATALOG_SCHEMA_VERSION = "1.0.0"
EVIDENCE_SCHEMA = "egohygiene.observatory.repository-evidence/v1"
HEALTH_SCHEMA = "egohygiene.observatory.organization-health/v1"
CONTRACT_VERSION = "1.0.0-alpha.1"
GENERATOR = {
    "name": "egohygiene/observatory:organization-health",
    "version": "0.1.0",
}

_REPOSITORY_PATTERN = re.compile(
    r"^[a-z0-9][a-z0-9.-]*/(?:\.github|[a-z0-9][a-z0-9.-]*)$"
)
_COMMIT_PATTERN = re.compile(r"^[0-9a-f]{40}$")
_SHA256_PATTERN = re.compile(r"^(?:sha256:)?[0-9a-f]{64}$")
_IDENTIFIER_PATTERN = re.compile(r"^[a-z0-9][a-z0-9._:/-]*$")
_PRODUCER_PATTERN = re.compile(r"^[a-z0-9][a-z0-9._/-]*$")
_CHECK_STATUSES = (
    "pass",
    "fail",
    "partial",
    "unknown",
    "blocked",
    "not_applicable",
)
_EFFECTIVE_STATUSES = (*_CHECK_STATUSES, "stale")
_SEVERITIES = ("required", "advisory")
_ASSESSMENTS = ("conformance", "maturity")
_DOMAINS = (
    "lifecycle",
    "foundation",
    "identity",
    "architecture",
    "automation",
    "security",
    "documentation",
    "releases",
    "sites",
    "migration",
    "dependencies",
)

JsonObject = dict[str, Any]


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


def _require_choice(value: Any, choices: Sequence[str], location: str) -> str:
    selected = _require_string(value, location)
    if selected not in choices:
        raise ContractError(
            f"{location} has unsupported value {selected!r}; "
            f"expected one of {', '.join(choices)}"
        )
    return selected


def _require_url(value: Any, location: str) -> str:
    url = _require_string(value, location)
    parsed = urlparse(url)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise ContractError(f"{location} must be an absolute HTTP(S) URL")
    return url


def _require_timestamp(value: Any, location: str) -> tuple[str, datetime]:
    timestamp = _require_string(value, location)
    if not timestamp.endswith("Z"):
        raise ContractError(f"{location} must be an RFC 3339 UTC timestamp ending in Z")
    try:
        parsed = datetime.fromisoformat(timestamp[:-1] + "+00:00")
    except ValueError as error:
        raise ContractError(f"{location} is not a valid RFC 3339 timestamp") from error
    if parsed.tzinfo is None or parsed.utcoffset() != timezone.utc.utcoffset(parsed):
        raise ContractError(f"{location} must use UTC")
    canonical = (
        parsed.astimezone(timezone.utc)
        .isoformat(timespec="seconds")
        .replace("+00:00", "Z")
    )
    if timestamp != canonical:
        raise ContractError(f"{location} must use canonical whole-second UTC form")
    return timestamp, parsed


def _require_repository(value: Any, location: str) -> str:
    repository = _require_string(value, location)
    if not _REPOSITORY_PATTERN.fullmatch(repository):
        raise ContractError(
            f"{location} is not a canonical repository name: {repository!r}"
        )
    return repository


def _require_commit(value: Any, location: str) -> str:
    commit = _require_string(value, location)
    if not _COMMIT_PATTERN.fullmatch(commit):
        raise ContractError(
            f"{location} must be a lowercase 40-character Git commit SHA"
        )
    return commit


def _require_sha256(value: Any, location: str) -> str:
    checksum = _require_string(value, location)
    if not _SHA256_PATTERN.fullmatch(checksum):
        raise ContractError(f"{location} must be a lowercase SHA-256 digest")
    return checksum.removeprefix("sha256:")


def _optional_sha256(value: Any, location: str) -> str | None:
    if value is None:
        return None
    return _require_sha256(value, location)


def _validate_exact_keys(
    value: Mapping[str, Any], *, required: set[str], optional: set[str], location: str
) -> None:
    missing = sorted(required - set(value))
    unexpected = sorted(set(value) - required - optional)
    if missing:
        raise ContractError(
            f"{location} is missing required fields: {', '.join(missing)}"
        )
    if unexpected:
        raise ContractError(
            f"{location} has unsupported fields: {', '.join(unexpected)}"
        )


def file_sha256(path: str | Path) -> str:
    """Return the lowercase SHA-256 digest of one file."""

    checksum = hashlib.sha256()
    source = Path(path)
    try:
        with source.open("rb") as handle:
            for chunk in iter(lambda: handle.read(1024 * 1024), b""):
                checksum.update(chunk)
    except OSError as error:
        raise ContractError(f"cannot hash {source}: {error}") from error
    return checksum.hexdigest()


def load_json(path: str | Path) -> JsonObject:
    """Load one JSON object with a stable contract error on failure."""

    source = Path(path)
    try:
        with source.open(encoding="utf-8") as handle:
            value = json.load(handle)
    except (OSError, json.JSONDecodeError) as error:
        raise ContractError(f"cannot read JSON from {source}: {error}") from error
    return _require_object(value, str(source))


def validate_catalog(catalog: Any) -> JsonObject:
    """Validate only the catalog fields Observatory indexes defensively.

    This does not replace Hygiene's complete JSON Schema or semantic validator.
    Callers are expected to supply a catalog that passed Hygiene validation.
    """

    document = _require_object(catalog, "catalog")
    if document.get("schema_version") != CATALOG_SCHEMA_VERSION:
        raise ContractError(
            "unsupported Hygiene catalog schema version: "
            f"{document.get('schema_version')!r}; expected {CATALOG_SCHEMA_VERSION!r}"
        )
    organization = _require_string(document.get("organization"), "catalog.organization")
    _require_string(
        document.get("architecture_release"), "catalog.architecture_release"
    )
    _require_string(document.get("observed_at"), "catalog.observed_at")
    repositories = _require_list(document.get("repositories"), "catalog.repositories")
    if not repositories:
        raise ContractError("catalog.repositories must not be empty")

    names: set[str] = set()
    full_names: set[str] = set()
    for position, raw_repository in enumerate(repositories):
        location = f"catalog.repositories[{position}]"
        repository = _require_object(raw_repository, location)
        name = _require_string(repository.get("name"), f"{location}.name")
        full_name = _require_repository(
            repository.get("full_name"), f"{location}.full_name"
        )
        if full_name != f"{organization}/{name}":
            raise ContractError(
                f"{location}.full_name must equal organization/name: "
                f"{organization}/{name}"
            )
        if name in names:
            raise ContractError(f"duplicate catalog repository name: {name}")
        if full_name in full_names:
            raise ContractError(f"duplicate catalog repository full_name: {full_name}")
        names.add(name)
        full_names.add(full_name)
        for field in ("plane", "lifecycle", "maturity", "visibility"):
            _require_string(repository.get(field), f"{location}.{field}")
        _require_url(repository.get("source_url"), f"{location}.source_url")
    return document


def load_catalog(path: str | Path) -> JsonObject:
    """Load the JSON-compatible YAML catalog published by Hygiene."""

    return validate_catalog(load_json(path))


def validate_evidence(evidence: Any) -> JsonObject:
    """Validate and normalize one provider-neutral repository evidence record."""

    document = deepcopy(_require_object(evidence, "evidence"))
    _validate_exact_keys(
        document,
        required={
            "schema",
            "contract_version",
            "repository",
            "represented_commit",
            "observed_at",
            "valid_until",
            "producer",
            "source",
            "checks",
        },
        optional=set(),
        location="evidence",
    )
    if document.get("schema") != EVIDENCE_SCHEMA:
        raise ContractError(
            f"unsupported evidence schema: {document.get('schema')!r}; "
            f"expected {EVIDENCE_SCHEMA!r}"
        )
    if document.get("contract_version") != CONTRACT_VERSION:
        raise ContractError(
            "unsupported evidence contract version: "
            f"{document.get('contract_version')!r}; expected {CONTRACT_VERSION!r}"
        )
    _require_repository(document.get("repository"), "evidence.repository")
    _require_commit(document.get("represented_commit"), "evidence.represented_commit")
    _, observed_at = _require_timestamp(
        document.get("observed_at"), "evidence.observed_at"
    )
    _, valid_until = _require_timestamp(
        document.get("valid_until"), "evidence.valid_until"
    )
    if valid_until < observed_at:
        raise ContractError(
            "evidence.valid_until must not precede evidence.observed_at"
        )

    producer = _require_object(document.get("producer"), "evidence.producer")
    _validate_exact_keys(
        producer,
        required={"name", "version", "url"},
        optional=set(),
        location="evidence.producer",
    )
    producer_name = _require_string(producer.get("name"), "evidence.producer.name")
    if not _PRODUCER_PATTERN.fullmatch(producer_name):
        raise ContractError("evidence.producer.name must be a canonical lowercase name")
    _require_string(producer.get("version"), "evidence.producer.version")
    _require_url(producer.get("url"), "evidence.producer.url")

    source = _require_object(document.get("source"), "evidence.source")
    _validate_exact_keys(
        source,
        required={"kind", "url", "sha256"},
        optional=set(),
        location="evidence.source",
    )
    _require_string(source.get("kind"), "evidence.source.kind")
    _require_url(source.get("url"), "evidence.source.url")
    source["sha256"] = _optional_sha256(source.get("sha256"), "evidence.source.sha256")

    checks = _require_list(document.get("checks"), "evidence.checks")
    if not checks:
        raise ContractError("evidence.checks must not be empty")
    identifiers: set[str] = set()
    for position, raw_check in enumerate(checks):
        location = f"evidence.checks[{position}]"
        check = _require_object(raw_check, location)
        _validate_exact_keys(
            check,
            required={
                "id",
                "title",
                "domain",
                "status",
                "severity",
                "assesses",
                "contract",
                "evidence",
            },
            optional=set(),
            location=location,
        )
        identifier = _require_string(check.get("id"), f"{location}.id")
        if not _IDENTIFIER_PATTERN.fullmatch(identifier):
            raise ContractError(
                f"{location}.id must be a canonical lowercase identifier"
            )
        if identifier in identifiers:
            raise ContractError(f"duplicate evidence check id: {identifier}")
        identifiers.add(identifier)
        _require_string(check.get("title"), f"{location}.title")
        _require_choice(check.get("domain"), _DOMAINS, f"{location}.domain")
        _require_choice(check.get("status"), _CHECK_STATUSES, f"{location}.status")
        _require_choice(check.get("severity"), _SEVERITIES, f"{location}.severity")
        assesses = _require_list(check.get("assesses"), f"{location}.assesses")
        if not assesses:
            raise ContractError(f"{location}.assesses must not be empty")
        normalized_assessments = [
            _require_choice(item, _ASSESSMENTS, f"{location}.assesses")
            for item in assesses
        ]
        if len(normalized_assessments) != len(set(normalized_assessments)):
            raise ContractError(f"{location}.assesses contains duplicates")
        check["assesses"] = sorted(normalized_assessments)

        contract = _require_object(check.get("contract"), f"{location}.contract")
        _validate_exact_keys(
            contract,
            required={"id", "version", "url"},
            optional=set(),
            location=f"{location}.contract",
        )
        _require_string(contract.get("id"), f"{location}.contract.id")
        _require_string(contract.get("version"), f"{location}.contract.version")
        _require_url(contract.get("url"), f"{location}.contract.url")
        links = _require_list(check.get("evidence"), f"{location}.evidence")
        if not links:
            raise ContractError(f"{location}.evidence must not be empty")
        check["evidence"] = sorted(
            {_require_url(link, f"{location}.evidence") for link in links}
        )

    document["checks"] = sorted(document["checks"], key=lambda item: item["id"])
    return document


def load_evidence(path: str | Path) -> JsonObject:
    """Load and validate one repository evidence record."""

    return validate_evidence(load_json(path))


def _egolint_status(report: Mapping[str, Any]) -> str:
    status = _require_choice(
        report.get("status"), ("clean", "findings", "execution_error"), "report.status"
    )
    completeness = _require_choice(
        report.get("completeness"),
        ("adapter_exit_only", "partial", "normalized"),
        "report.completeness",
    )
    if status == "execution_error":
        return "blocked"
    if status == "findings":
        return "fail"
    if completeness != "normalized":
        return "partial"
    return "pass"


def adapt_egolint_report(
    report: Any,
    *,
    repository: str,
    represented_commit: str,
    valid_until: str,
    source_url: str,
    source_sha256: str,
    producer_version: str,
    contract_url: str,
) -> JsonObject:
    """Adapt the stable Egolint v1 run report into repository evidence.

    The adapter consumes report-level status only. Egolint retains ownership of
    rule semantics, finding normalization, suppressions, and exit-code policy.
    """

    document = _require_object(report, "report")
    if document.get("schema_version") != 1:
        raise ContractError(
            f"unsupported Egolint report schema version: {document.get('schema_version')!r}"
        )
    if document.get("operation") != "check":
        raise ContractError(
            "only read-only Egolint check reports can become health evidence"
        )
    generated_at = document.get("generated_at_unix")
    if (
        not isinstance(generated_at, int)
        or isinstance(generated_at, bool)
        or generated_at < 0
    ):
        raise ContractError("report.generated_at_unix must be a non-negative integer")
    observed_at = (
        datetime.fromtimestamp(generated_at, timezone.utc)
        .isoformat(timespec="seconds")
        .replace("+00:00", "Z")
    )
    profile = _require_object(document.get("profile"), "report.profile")
    profile_name = _require_choice(
        profile.get("name"),
        ("fast", "holistic", "security", "dependency-debt"),
        "report.profile.name",
    )
    profile_scope = _require_choice(
        profile.get("scope"),
        (
            "changed_files",
            "changed_files_with_repository_policy",
            "complete_repository",
        ),
        "report.profile.scope",
    )
    policy_source = _require_string(
        profile.get("policy_source"), "report.profile.policy_source"
    )
    domain = {
        "security": "security",
        "dependency-debt": "dependencies",
    }.get(profile_name, "automation")
    report_url = _require_url(source_url, "source_url")
    adapted = {
        "schema": EVIDENCE_SCHEMA,
        "contract_version": CONTRACT_VERSION,
        "repository": _require_repository(repository, "repository"),
        "represented_commit": _require_commit(represented_commit, "represented_commit"),
        "observed_at": observed_at,
        "valid_until": _require_timestamp(valid_until, "valid_until")[0],
        "producer": {
            "name": "egohygiene/egolint",
            "version": _require_string(producer_version, "producer_version"),
            "url": "https://github.com/egohygiene/egolint",
        },
        "source": {
            "kind": "egolint-report",
            "url": report_url,
            "sha256": _require_sha256(source_sha256, "source_sha256"),
        },
        "checks": [
            {
                "id": f"egolint:{profile_name}",
                "title": f"Egolint {profile_name} profile",
                "domain": domain,
                "status": _egolint_status(document),
                "severity": "required",
                "assesses": ["conformance"],
                "contract": {
                    "id": "egohygiene.egolint.report/v1",
                    "version": "1",
                    "url": _require_url(contract_url, "contract_url"),
                },
                "evidence": [report_url],
            }
        ],
    }
    adapted["checks"][0]["title"] += f" ({profile_scope}; {policy_source})"
    return validate_evidence(adapted)


def _freshness(observed_at: str, valid_until: str, as_of: datetime) -> str:
    _, observed = _require_timestamp(observed_at, "evidence.observed_at")
    _, expires = _require_timestamp(valid_until, "evidence.valid_until")
    if observed > as_of:
        raise ContractError(
            "evidence.observed_at must not be later than snapshot as_of"
        )
    return "stale" if expires < as_of else "current"


def _rollup(checks: Sequence[Mapping[str, Any]], assessment: str) -> JsonObject:
    relevant = [
        item
        for item in checks
        if assessment in item["assesses"] and item["severity"] == "required"
    ]
    counts = Counter(item["status"] for item in relevant)
    if not relevant:
        status = "unknown"
        reason = "no required evidence assesses this dimension"
    elif counts["fail"]:
        status = "non_conformant" if assessment == "conformance" else "contradicted"
        reason = "at least one current required check failed"
    elif counts["blocked"]:
        status = "blocked"
        reason = "at least one current required check was blocked"
    elif counts["stale"]:
        status = "stale"
        reason = "at least one required check is stale"
    elif counts["unknown"]:
        status = "unknown"
        reason = "at least one required check is unknown"
    elif counts["partial"]:
        status = "partial"
        reason = "at least one required check has partial coverage"
    elif counts["pass"]:
        status = "conformant" if assessment == "conformance" else "supported"
        reason = "all applicable required checks passed with current evidence"
    else:
        status = "not_applicable"
        reason = "every required check is explicitly not applicable"
    return {
        "status": status,
        "reason": reason,
        "rule": (
            "required checks only; precedence is fail, blocked, stale, unknown, "
            "partial, pass, not_applicable; no numeric score"
        ),
        "counts": {state: counts[state] for state in _EFFECTIVE_STATUSES},
        "check_ids": sorted(item["key"] for item in relevant),
    }


def _repository_entry(
    repository: Mapping[str, Any],
    evidence: Sequence[Mapping[str, Any]],
    as_of: datetime,
) -> JsonObject:
    checks: list[JsonObject] = []
    freshness_states: list[str] = []
    observed_times: list[str] = []
    commits: set[str] = set()
    producers: set[str] = set()
    identities: set[str] = set()
    for record in evidence:
        record_freshness = _freshness(
            record["observed_at"], record["valid_until"], as_of
        )
        freshness_states.append(record_freshness)
        observed_times.append(record["observed_at"])
        commits.add(record["represented_commit"])
        producer_name = record["producer"]["name"]
        producers.add(producer_name)
        for raw_check in record["checks"]:
            identity = f"{producer_name}:{raw_check['id']}"
            if identity in identities:
                raise ContractError(
                    f"duplicate check identity for {repository['full_name']}: {identity}"
                )
            identities.add(identity)
            reported = raw_check["status"]
            effective = "stale" if record_freshness == "stale" else reported
            check = deepcopy(raw_check)
            check.update(
                {
                    "key": identity,
                    "reported_status": reported,
                    "status": effective,
                    "freshness": record_freshness,
                    "observation": {
                        "observed_at": record["observed_at"],
                        "valid_until": record["valid_until"],
                        "represented_commit": record["represented_commit"],
                        "producer": deepcopy(record["producer"]),
                        "source": deepcopy(record["source"]),
                    },
                }
            )
            checks.append(check)
    checks.sort(key=lambda item: item["key"])
    if not freshness_states:
        overall_freshness = "unknown"
    elif len(set(freshness_states)) > 1:
        overall_freshness = "mixed"
    else:
        overall_freshness = freshness_states[0]
    return {
        "repository": {
            "name": repository["name"],
            "full_name": repository["full_name"],
            "url": repository["source_url"],
            "visibility": repository["visibility"],
            "plane": repository["plane"],
        },
        "declared": {
            "lifecycle": repository["lifecycle"],
            "maturity": repository["maturity"],
            "source": "Hygiene repository catalog",
        },
        "assessment": {
            "maturity": _rollup(checks, "maturity"),
            "conformance": _rollup(checks, "conformance"),
        },
        "evidence": {
            "freshness": overall_freshness,
            "record_count": len(evidence),
            "check_count": len(checks),
            "earliest_observed_at": min(observed_times) if observed_times else None,
            "latest_observed_at": max(observed_times) if observed_times else None,
            "represented_commits": sorted(commits),
            "producers": sorted(producers),
            "checks": checks,
        },
    }


def build_organization_health(
    catalog: Any,
    evidence_records: Iterable[Any],
    *,
    as_of: str,
    catalog_url: str,
    catalog_commit: str,
    catalog_sha256: str,
) -> JsonObject:
    """Build one deterministic fleet health snapshot."""

    normalized_catalog = validate_catalog(catalog)
    as_of_text, as_of_time = _require_timestamp(as_of, "as_of")
    normalized_evidence = [validate_evidence(item) for item in evidence_records]
    normalized_evidence.sort(
        key=lambda item: (
            item["repository"],
            item["producer"]["name"],
            item["observed_at"],
            digest(item),
        )
    )
    catalog_repositories = {
        item["full_name"]: item for item in normalized_catalog["repositories"]
    }
    evidence_by_repository: dict[str, list[JsonObject]] = {
        repository: [] for repository in catalog_repositories
    }
    for evidence in normalized_evidence:
        repository = evidence["repository"]
        if repository not in catalog_repositories:
            raise ContractError(
                f"evidence repository {repository!r} is absent from the Hygiene catalog"
            )
        evidence_by_repository[repository].append(evidence)

    repositories = [
        _repository_entry(
            catalog_repositories[repository],
            evidence_by_repository[repository],
            as_of_time,
        )
        for repository in sorted(catalog_repositories)
    ]
    conformance_counts = Counter(
        item["assessment"]["conformance"]["status"] for item in repositories
    )
    maturity_counts = Counter(
        item["assessment"]["maturity"]["status"] for item in repositories
    )
    source = {
        "schema_version": normalized_catalog["schema_version"],
        "architecture_release": normalized_catalog["architecture_release"],
        "observed_at": normalized_catalog["observed_at"],
        "freshness": "unknown",
        "freshness_reason": "the catalog contract does not declare a validity window",
        "url": _require_url(catalog_url, "catalog_url"),
        "commit": _require_commit(catalog_commit, "catalog_commit"),
        "sha256": _require_sha256(catalog_sha256, "catalog_sha256"),
    }
    identity = digest(
        {
            "as_of": as_of_text,
            "catalog": source,
            "evidence": normalized_evidence,
        }
    )
    return {
        "schema": HEALTH_SCHEMA,
        "contract_version": CONTRACT_VERSION,
        "snapshot_id": f"organization-health:{identity}",
        "as_of": as_of_text,
        "generator": deepcopy(GENERATOR),
        "organization": normalized_catalog["organization"],
        "sources": {
            "catalog": source,
            "evidence_record_count": len(normalized_evidence),
            "evidence_digests": sorted(digest(item) for item in normalized_evidence),
        },
        "summary": {
            "repository_count": len(repositories),
            "assessed_repository_count": sum(
                item["evidence"]["record_count"] > 0 for item in repositories
            ),
            "unknown_repository_count": sum(
                item["evidence"]["record_count"] == 0 for item in repositories
            ),
            "conformance": dict(sorted(conformance_counts.items())),
            "maturity_evidence": dict(sorted(maturity_counts.items())),
        },
        "repositories": repositories,
    }


def markdown_text(snapshot: Mapping[str, Any]) -> str:
    """Render a deterministic human-readable health snapshot."""

    if snapshot.get("schema") != HEALTH_SCHEMA:
        raise ContractError(
            "Markdown input must be an Observatory organization-health snapshot"
        )
    catalog = snapshot["sources"]["catalog"]
    lines = [
        f"# {snapshot['organization']} organization health",
        "",
        f"- Snapshot: `{snapshot['snapshot_id']}`",
        f"- As of: `{snapshot['as_of']}`",
        (
            f"- Catalog: [{catalog['architecture_release']}]({catalog['url']}) "
            f"at `{catalog['commit']}`"
        ),
        f"- Catalog freshness: `{catalog['freshness']}` — {catalog['freshness_reason']}",
        f"- Evidence records: `{snapshot['sources']['evidence_record_count']}`",
        "",
        "The declared maturity column comes from Hygiene. The evidence columns are "
        "Observatory rollups; they never replace the declaration or hide missing data "
        "behind a percentage.",
        "",
        "| Repository | Lifecycle | Declared maturity | Maturity evidence | Conformance | Evidence freshness |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for item in snapshot["repositories"]:
        repository = item["repository"]
        lines.append(
            "| "
            f"[{repository['full_name']}]({repository['url']}) | "
            f"{item['declared']['lifecycle']} | "
            f"{item['declared']['maturity']} | "
            f"{item['assessment']['maturity']['status']} | "
            f"{item['assessment']['conformance']['status']} | "
            f"{item['evidence']['freshness']} |"
        )
    lines.extend(
        [
            "",
            "## Calculation rules",
            "",
            "Only required checks affect a rollup. The effective precedence is fail, blocked, "
            "stale, unknown, partial, pass, then not applicable. Expired evidence is reported "
            "as stale before rollup. Maturity evidence maps a failure to "
            "`contradicted` and a pass to `supported`; conformance maps them to "
            "`non_conformant` and `conformant`. A repository without qualifying evidence "
            "remains `unknown`. Advisory checks stay visible in JSON but do not change the "
            "rollup. No numeric score is calculated.",
            "",
        ]
    )
    return "\n".join(lines)
