#!/usr/bin/env python3
"""Verify that checked-in offline consumer fixtures are reproducible."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from observatory.intelligence import (
    build_fleet_snapshot,
    build_repository_snapshot,
    json_text,
    load_projection,
)


def main() -> int:
    fixtures = ROOT / "fixtures" / "repository-intelligence"
    expected = ROOT / "fixtures" / "expected"
    projections = [
        load_projection(fixtures / "observatory-active.input.json"),
        load_projection(fixtures / "relay-complete-quest.input.json"),
    ]
    snapshots = [build_repository_snapshot(item) for item in projections]
    artifacts = {
        "egohygiene--observatory.repository.json": snapshots[0],
        "egohygiene--relay.repository.json": snapshots[1],
        "fleet.json": build_fleet_snapshot(snapshots),
    }
    mismatches = []
    for filename, artifact in artifacts.items():
        path = expected / filename
        if not path.is_file() or path.read_text(encoding="utf-8") != json_text(artifact):
            mismatches.append(filename)
    if mismatches:
        sys.stderr.write(
            "fixture snapshots are stale or missing: " + ", ".join(mismatches) + "\n"
        )
        return 1
    print("verified 2 repository snapshots and 1 fleet snapshot")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
