#!/usr/bin/env python3
"""Verify deterministic organization-health fixture outputs."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from observatory.health import (  # noqa: E402
    build_organization_health,
    file_sha256,
    load_catalog,
    load_evidence,
    markdown_text,
)
from observatory.intelligence import json_text  # noqa: E402


def main() -> int:
    fixtures = ROOT / "fixtures" / "health"
    catalog_path = fixtures / "hygiene.repositories.v1.input.yaml"
    snapshot = build_organization_health(
        load_catalog(catalog_path),
        [
            load_evidence(fixtures / "observatory.repository-evidence.input.json"),
            load_evidence(fixtures / "empathy.egolint.repository-evidence.input.json"),
        ],
        as_of="2026-09-02T12:00:00Z",
        catalog_url=(
            "https://github.com/egohygiene/hygiene/blob/"
            "28f9d6c7519d820644572634ba4476614f418d83/"
            "catalog/repositories.yaml"
        ),
        catalog_commit="28f9d6c7519d820644572634ba4476614f418d83",
        catalog_sha256=file_sha256(catalog_path),
    )
    expected = fixtures / "expected"
    artifacts = {
        "organization-health.json": json_text(snapshot),
        "organization-health.md": markdown_text(snapshot),
    }
    mismatches = [
        filename
        for filename, content in artifacts.items()
        if not (expected / filename).is_file()
        or (expected / filename).read_text(encoding="utf-8") != content
    ]
    if mismatches:
        sys.stderr.write(
            "organization-health fixtures are stale or missing: "
            + ", ".join(mismatches)
            + "\n"
        )
        return 1
    print("verified organization-health JSON and Markdown snapshots")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
