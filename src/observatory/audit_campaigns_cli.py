"""Explicit offline campaign projection; no discovery, audit execution or fetch."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

from . import audit_campaigns as campaigns


def parser():
    result = argparse.ArgumentParser(description=__doc__, allow_abbrev=False)
    result.add_argument("--targets", type=Path, required=True,
        help="Explicit public repository/represented_commit selector array.")
    result.add_argument("--as-of", required=True)
    result.add_argument("--evidence", type=Path, action="append", default=[])
    result.add_argument("--admission-root", type=Path, default=campaigns.DEFAULT_ROOT)
    result.add_argument("--output", type=Path, required=True)
    return result


def main(argv=None):
    args = parser().parse_args(argv)
    try:
        shared = campaigns.shared
        shared.require(len(args.evidence) <= 256)
        selectors = shared.parse(shared.base._read(args.targets))
        shared.require(isinstance(selectors, list))
        wrappers = []
        for path in args.evidence:
            value = shared.parse(shared.base._read(path))
            wrappers.extend(value if isinstance(value, list) else [value])
        model = campaigns.build_fleet_audit_campaigns(wrappers, repositories=selectors,
            as_of=args.as_of, admission_root=args.admission_root)
        destination = args.output.absolute()
        shared.require(".." not in destination.parts and not destination.exists()
            and not any(item.is_symlink() for item in (destination, *destination.parents)))
        content = (json.dumps(model, indent=2, sort_keys=True, ensure_ascii=False, allow_nan=False) + "\n").encode()
        shared.require(len(content) <= shared.base.MAX_BYTES)
        destination.parent.mkdir(parents=True, exist_ok=True)
        with destination.open("xb") as handle:
            handle.write(content)
        return 0
    except (ValueError, TypeError, KeyError, AttributeError, OSError, UnicodeError, RecursionError):
        print("Public campaign source, selector, owner resource or output is incompatible", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
