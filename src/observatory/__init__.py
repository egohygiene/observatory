"""Observatory's provider-neutral Repository Intelligence read model."""

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
    "ContractError",
    "build_fleet_snapshot",
    "build_repository_snapshot",
    "compare_snapshots",
    "extract_view",
    "load_projection",
    "write_json",
]

__version__ = "0.1.0"
