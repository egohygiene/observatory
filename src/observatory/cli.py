"""Command-line interface for Repository Intelligence snapshots."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Sequence

from .intelligence import (
    VIEW_NAMES,
    ContractError,
    build_bundle,
    compare_snapshots,
    digest,
    extract_view,
    json_text,
    load_json,
    load_projection,
    repository_slug,
    write_json,
)


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="observatory-intelligence",
        description="Build deterministic Repository Intelligence read models.",
        allow_abbrev=False,
    )
    parser.add_argument("--version", action="version", version="%(prog)s 0.1.0")
    subparsers = parser.add_subparsers(dest="command", required=True)

    validate = subparsers.add_parser(
        "validate",
        help="validate Observatory's safe consumer boundary",
        allow_abbrev=False,
    )
    validate.add_argument("--input", required=True, type=Path)

    build = subparsers.add_parser(
        "build",
        help="build repository snapshots and a fleet snapshot",
        allow_abbrev=False,
    )
    build.add_argument(
        "--input",
        required=True,
        action="append",
        type=Path,
        help="Hygiene Repository Intelligence projection; repeat for a fleet",
    )
    build.add_argument("--output", required=True, type=Path)

    query = subparsers.add_parser(
        "query",
        help="extract one versioned page view",
        allow_abbrev=False,
    )
    query.add_argument("--snapshot", required=True, type=Path)
    query.add_argument("--view", required=True, choices=VIEW_NAMES)
    query.add_argument("--output", type=Path)

    compare = subparsers.add_parser(
        "compare",
        help="compare two repository read models",
        allow_abbrev=False,
    )
    compare.add_argument("--before", required=True, type=Path)
    compare.add_argument("--after", required=True, type=Path)
    compare.add_argument("--output", type=Path)
    return parser


def _emit(value: object, output: Path | None) -> None:
    if output is None:
        sys.stdout.write(json_text(value))
    else:
        write_json(output, value)


def _run(args: argparse.Namespace) -> int:
    if args.command == "validate":
        projection = load_projection(args.input)
        sys.stdout.write(
            f"valid {projection['schema']} projection "
            f"{projection['projection_id']} ({digest(projection)})\n"
        )
        return 0

    if args.command == "build":
        projections = [load_projection(path) for path in args.input]
        repositories, fleet = build_bundle(projections)
        repository_directory = args.output / "repositories"
        for snapshot in repositories:
            repository = snapshot["repository"]["repository"]
            write_json(repository_directory / f"{repository_slug(repository)}.json", snapshot)
        write_json(args.output / "fleet.json", fleet)
        sys.stdout.write(
            f"built {len(repositories)} repository snapshot(s) and fleet "
            f"{fleet['snapshot_id']} in {args.output}\n"
        )
        return 0

    if args.command == "query":
        _emit(extract_view(load_json(args.snapshot), args.view), args.output)
        return 0

    if args.command == "compare":
        _emit(
            compare_snapshots(load_json(args.before), load_json(args.after)),
            args.output,
        )
        return 0
    raise AssertionError(f"unhandled command: {args.command}")


def main(argv: Sequence[str] | None = None) -> int:
    """Run the command-line interface."""

    try:
        return _run(_parser().parse_args(argv))
    except ContractError as error:
        sys.stderr.write(f"observatory-intelligence: {error}\n")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
