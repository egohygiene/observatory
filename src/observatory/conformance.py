"""Build the bounded conformance query from existing owner health/evidence models."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any, Iterable

from . import health
from . import conformance_contract as contract

DEFAULT_ADMISSION_ROOT = Path(__file__).resolve().parent / "data"


def build_repository_conformance(evidence_wrappers: Iterable[Any], *, repository: str,
        represented_commit: str, as_of: str, admission_root: Path = DEFAULT_ADMISSION_ROOT,
        admission: dict | None = None) -> dict:
    """Admit declared public evidence before touching its identity or payload.

    Wrappers are {visibility, repository, evidence}; evidence remains the existing
    repository-evidence/v1 alpha.1 contract. Nonpublic/nonselected wrappers never
    enter validation, diagnostics, counts or digests. A target mismatch inside a
    selected wrapper is denied before its text is read.
    """
    row, metadata, _allowed = contract.admission(repository, admission_root=admission_root)
    if admission is not None:
        contract.require(admission == metadata)
    contract.require(isinstance(represented_commit, str) and contract.SHA.fullmatch(represented_commit))
    evaluated = contract.instant(as_of)
    selected = []
    for wrapper in evidence_wrappers:
        if not isinstance(wrapper, dict) or wrapper.get("visibility") != "public" or "visibility" in getattr(wrapper, "duplicate_keys", set()):
            continue
        if wrapper.get("repository") != repository:
            continue
        contract.closed(wrapper, {"visibility", "repository", "evidence"})
        raw = contract.plain(wrapper["evidence"])
        contract.require(raw.get("repository") == repository)
        contract.unambiguous(raw)
        contract.require(len(selected) < 256)
        try:
            selected.append(health.validate_evidence(raw))
        except (ValueError, TypeError, KeyError):
            raise contract.ConformanceError("Selected public conformance evidence is incompatible") from None
    catalog_row = {"name": row["name"], "full_name": row["full_name"], "source_url": row["source_url"],
        "visibility": "public", **{name: row["role"][name] for name in ("plane", "lifecycle", "maturity")}}
    try:
        entry = health._repository_entry(catalog_row, selected, evaluated)
    except (ValueError, TypeError, KeyError):
        raise contract.ConformanceError("Selected public conformance observations conflict") from None
    checks = []
    for item in entry["evidence"]["checks"]:
        if "conformance" not in item["assesses"]:
            continue
        check = deepcopy(item)
        check["revision_status"] = "matched" if check["observation"]["represented_commit"] == represented_commit else "different"
        checks.append(check)
    current = [item for item in checks if item["revision_status"] == "matched"]
    value = {"schema": contract.SCHEMA, "contract_version": contract.VERSION, "visibility": "public",
        "repository": {name: row[name] for name in ("full_name", "repository_id", "visibility", "source_url")},
        "represented_commit": represented_commit, "as_of": as_of, "admission": metadata,
        "scope": {"contracts": "supplied-conformance-assessments-only", "applicability": "unknown", "contract_inventory": "unknown"},
        "assessment": health._rollup(current, "conformance"), "checks": checks,
        "evidence": {"state": "supplied" if checks else "unavailable",
            "record_count": len({contract.digest(item["observation"]) for item in checks}),
            "checks_sha256": contract.digest(checks), "current_check_count": len(current),
            "other_revision_check_count": len(checks) - len(current)}}
    return contract.validate(value, admission_root=admission_root)
