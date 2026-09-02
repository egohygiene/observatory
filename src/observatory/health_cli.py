"""Command-line interface for deterministic organization-health snapshots."""

from __future__ import annotations

import argparse
import os
import sys
import tempfile
from pathlib import Path
from typing import Sequence

from .health import (
    adapt_egolint_report,
    build_organization_health,
    file_sha256,
    load_catalog,
    load_evidence,
    load_json,
    markdown_text,
)
from .intelligence import ContractError, json_text, write_json

EGOLINT_REPORT_V1_CONTRACT = (
    "https://github.com/egohygiene/egolint/blob/"
    "4b98b30eb3a574c81986fb9be585c4935f585f65/"
    "schemas/report.schema.json"
)


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="observatory-health",
        description="Build evidence-linked organization health snapshots.",
        allow_abbrev=False,
    )
    parser.add_argument("--version", action="version", version="%(prog)s 0.1.0")
    subparsers = parser.add_subparsers(dest="command", required=True)

    build = subparsers.add_parser(
        "build",
        help="build machine-readable and human-readable fleet snapshots",
        allow_abbrev=False,
    )
    build.add_argument("--catalog", required=True, type=Path)
    build.add_argument("--catalog-url", required=True)
    build.add_argument("--catalog-commit", required=True)
    build.add_argument(
        "--evidence",
        action="append",
        default=[],
        type=Path,
        help="repository evidence input; repeat for multiple records",
    )
    build.add_argument(
        "--as-of",
        required=True,
        help="explicit RFC 3339 UTC evaluation time used for deterministic freshness",
    )
    build.add_argument("--output", required=True, type=Path)

    adapt = subparsers.add_parser(
        "adapt-egolint",
        help="adapt one read-only Egolint v1 report into repository evidence",
        allow_abbrev=False,
    )
    adapt.add_argument("--report", required=True, type=Path)
    adapt.add_argument("--repository", required=True)
    adapt.add_argument("--represented-commit", required=True)
    adapt.add_argument("--valid-until", required=True)
    adapt.add_argument("--source-url", required=True)
    adapt.add_argument("--producer-version", required=True)
    adapt.add_argument("--output", type=Path)
    return parser


def _write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{path.name}.", dir=path.parent
    )
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(content)
        os.replace(temporary_name, path)
    except BaseException:
        try:
            os.unlink(temporary_name)
        except FileNotFoundError:
            pass
        raise


def _run(args: argparse.Namespace) -> int:
    if args.command == "build":
        catalog = load_catalog(args.catalog)
        evidence = [load_evidence(path) for path in args.evidence]
        snapshot = build_organization_health(
            catalog,
            evidence,
            as_of=args.as_of,
            catalog_url=args.catalog_url,
            catalog_commit=args.catalog_commit,
            catalog_sha256=file_sha256(args.catalog),
        )
        write_json(args.output / "organization-health.json", snapshot)
        _write_text(args.output / "organization-health.md", markdown_text(snapshot))
        sys.stdout.write(
            f"built health snapshot for {snapshot['summary']['repository_count']} "
            f"repositories from {snapshot['sources']['evidence_record_count']} "
            f"evidence record(s) in {args.output}\n"
        )
        return 0

    if args.command == "adapt-egolint":
        report = load_json(args.report)
        evidence = adapt_egolint_report(
            report,
            repository=args.repository,
            represented_commit=args.represented_commit,
            valid_until=args.valid_until,
            source_url=args.source_url,
            source_sha256=file_sha256(args.report),
            producer_version=args.producer_version,
            contract_url=EGOLINT_REPORT_V1_CONTRACT,
        )
        if args.output is None:
            sys.stdout.write(json_text(evidence))
        else:
            write_json(args.output, evidence)
        return 0
    raise AssertionError(f"unhandled command: {args.command}")


def main(argv: Sequence[str] | None = None) -> int:
    """Run the organization-health command-line interface."""

    try:
        return _run(_parser().parse_args(argv))
    except ContractError as error:
        sys.stderr.write(f"observatory-health: {error}\n")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
