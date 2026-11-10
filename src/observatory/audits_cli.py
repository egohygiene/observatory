"""Explicit offline Audits query adapter; no source discovery or audit execution."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

from . import audits
from . import audits_contract as contract
from . import audits_queries


def parser():
    result = argparse.ArgumentParser(description=__doc__, allow_abbrev=False)
    commands = result.add_subparsers(dest="command", required=True)
    for mode in ("repository", "fleet"):
        command = commands.add_parser(mode, allow_abbrev=False)
        command.add_argument("--as-of", required=True)
        command.add_argument("--evidence", type=Path, action="append", default=[])
        command.add_argument("--admission-root", type=Path, default=contract.DEFAULT_ROOT)
        command.add_argument("--maximum-age-seconds", type=int, default=contract.DEFAULT_AGE)
        command.add_argument("--output", type=Path, required=True)
        if mode == "repository":
            command.add_argument("--repository", required=True)
            command.add_argument("--represented-commit", required=True)
        else:
            command.add_argument("--targets", type=Path, required=True,
                help="Explicit repository/revision selector array; excluded identities are never placeholders.")
    patterns = commands.add_parser("patterns", allow_abbrev=False)
    patterns.add_argument("--fleet", type=Path, required=True)
    comparison = commands.add_parser("compare", allow_abbrev=False)
    comparison.add_argument("--before", type=Path, required=True)
    comparison.add_argument("--after", type=Path, required=True)
    for command in (patterns, comparison):
        command.add_argument("--admission-root", type=Path, default=contract.DEFAULT_ROOT)
        command.add_argument("--output", type=Path, required=True)
    return result


def main(argv=None):
    args = parser().parse_args(argv)
    try:
        if args.command in {"patterns", "compare"}:
            def read(path):
                return contract.parse(contract.shared.base._read(path))
            model = audits_queries.query_fleet_audits(read(args.fleet), admission_root=args.admission_root) if args.command == "patterns" else (
                audits_queries.compare_fleet_audits(read(args.before), read(args.after), admission_root=args.admission_root))
        else:
            contract.require(len(args.evidence) <= 256)
            wrappers = []
            for path in args.evidence:
                value = contract.parse(contract.shared.base._read(path))
                wrappers.extend(value if isinstance(value, list) else [value])
            options = {"as_of": args.as_of, "admission_root": args.admission_root,
                "maximum_age_seconds": args.maximum_age_seconds}
            if args.command == "repository":
                model = audits.build_repository_audits(wrappers, repository=args.repository,
                    represented_commit=args.represented_commit, **options)
            else:
                selected = contract.parse(contract.shared.base._read(args.targets))
                contract.require(isinstance(selected, list))
                model = audits.build_fleet_audits(wrappers, repositories=selected, **options)
        destination = args.output.absolute()
        contract.require(".." not in destination.parts and not destination.exists()
            and not any(item.is_symlink() for item in (destination, *destination.parents)))
        destination.parent.mkdir(parents=True, exist_ok=True)
        content = (json.dumps(model, indent=2, sort_keys=True, ensure_ascii=False, allow_nan=False) + "\n").encode()
        contract.require(len(content) <= contract.shared.base.MAX_BYTES)
        with destination.open("xb") as handle:
            handle.write(content)
        return 0
    except (ValueError, TypeError, KeyError, AttributeError, OSError, UnicodeError, RecursionError):
        print("Public Audits source, selector, owner resource or output is incompatible", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
