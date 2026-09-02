"""Observatory's provider-neutral read models."""

from .health import (
    EVIDENCE_SCHEMA,
    HEALTH_SCHEMA,
    adapt_egolint_report,
    build_organization_health,
    load_catalog,
    load_evidence,
    markdown_text,
)

from .intelligence import (
    COMPARE_SCHEMA,
    FLEET_SCHEMA,
    READ_MODEL_SCHEMA,
    VIEW_SCHEMA,
    ContractError,
    build_fleet_snapshot,
    build_repository_snapshot,
    compare_snapshots,
    extract_view,
    load_projection,
    write_json,
)

__all__ = [
    "COMPARE_SCHEMA",
    "FLEET_SCHEMA",
    "READ_MODEL_SCHEMA",
    "VIEW_SCHEMA",
    "EVIDENCE_SCHEMA",
    "HEALTH_SCHEMA",
    "ContractError",
    "adapt_egolint_report",
    "build_fleet_snapshot",
    "build_organization_health",
    "build_repository_snapshot",
    "compare_snapshots",
    "extract_view",
    "load_catalog",
    "load_evidence",
    "load_projection",
    "markdown_text",
    "write_json",
]

__version__ = "0.1.0"
