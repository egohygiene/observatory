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
from .search_fields import (
    SEARCH_FIELDS_SCHEMA,
    SEARCH_FIELDS_VERSION,
    SEARCH_FIELD_NAMES,
    SearchContractError,
    match_search_record,
    normalize_search_query,
    validate_search_record,
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
    "SEARCH_FIELDS_SCHEMA",
    "SEARCH_FIELDS_VERSION",
    "SEARCH_FIELD_NAMES",
    "SearchContractError",
    "match_search_record",
    "normalize_search_query",
    "validate_search_record",
]

__version__ = "0.1.0"

# The optional conformance query does not change existing health or Intelligence
# defaults and introduces no additional repository-intelligence coverage domain.
from .conformance import build_repository_conformance

__all__.append("build_repository_conformance")

from .continuity import build_continuity_view
__all__.append("build_continuity_view")
