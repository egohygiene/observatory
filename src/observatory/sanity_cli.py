"""Explicit offline Sanity query adapter; no source discovery or audit execution."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

from . import sanity
from . import sanity_contract as contract


def parser():
    result = argparse.ArgumentParser(description=__doc__, allow_abbrev=False)
    commands = result.add_subparsers(dest="command", required=True)
    for mode in ("repository", "fleet"):
        command = commands.add_parser(mode, allow_abbrev=False)
        command.add_argument("--as-of", required=True)
        command.add_argument("--evidence", type=Path, action="append", default=[])
        command.add_argument("--admission-root", type=Path, default=contract.DEFAULT_ROOT)
        command.add_argument("--governance", type=Path, action="append", default=[])
        command.add_argument("--material-changes", type=Path, action="append", default=[])
        command.add_argument("--change-inventory", choices=("unknown", "partial", "complete", "unavailable"), default="unknown")
        command.add_argument("--output", type=Path, required=True)
        if mode == "repository":
            command.add_argument("--repository", required=True)
            command.add_argument("--represented-commit", required=True)
        else:
            command.add_argument("--targets", type=Path, required=True,
                help="Explicit repository/revision selector array; excluded identities are never placeholders.")
    return result


def main(argv=None):
    args = parser().parse_args(argv)
    try:
        contract.require(len(args.evidence) <= 256)
        wrappers = []
        for path in args.evidence:
            value = contract.parse(contract.shared.base._read(path))
            wrappers.extend(value if isinstance(value, list) else [value])
        declarations, changes = [], []
        contract.require(len(args.governance) <= 256 and len(args.material_changes) <= 256)
        for paths, target in ((args.governance, declarations), (args.material_changes, changes)):
            for path in paths:
                value = contract.parse(contract.shared.base._read(path))
                target.extend(value if isinstance(value, list) else [value])
        options = {"as_of": args.as_of, "admission_root": args.admission_root,
            "governance_wrappers": declarations, "material_changes": changes, "change_inventory": args.change_inventory}
        if args.command == "repository":
            model = sanity.build_repository_sanity(wrappers, repository=args.repository,
                represented_commit=args.represented_commit, **options)
        else:
            selected = contract.parse(contract.shared.base._read(args.targets))
            contract.require(isinstance(selected, list))
            model = sanity.build_fleet_sanity(wrappers, repositories=selected, **options)
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
        print("Public Sanity source, selector, owner resource or output is incompatible", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
