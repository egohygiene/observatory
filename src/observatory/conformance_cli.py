"""Explicit offline adapter for the bounded repository conformance query."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

from .conformance import DEFAULT_ADMISSION_ROOT, build_repository_conformance
from . import conformance_contract as contract
from .intelligence import write_json


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, allow_abbrev=False)
    parser.add_argument("--repository", required=True)
    parser.add_argument("--represented-commit", required=True)
    parser.add_argument("--as-of", required=True)
    parser.add_argument("--evidence", type=Path, action="append", default=[],
                        help="Closed declared-public wrapper or array of wrappers around repository-evidence/v1.")
    parser.add_argument("--admission-root", type=Path, default=DEFAULT_ADMISSION_ROOT,
                        help="Trusted directory containing the exact pinned public artifact.")
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args(argv)
    try:
        wrappers = []
        contract.require(len(args.evidence) <= 256)
        for path in args.evidence:
            value = contract.parse(contract._read(path))
            wrappers.extend(value if isinstance(value, list) else [value])
        value = build_repository_conformance(wrappers, repository=args.repository,
            represented_commit=args.represented_commit, as_of=args.as_of,
            admission_root=args.admission_root)
        write_json(args.output, value)
        print("Built bounded public repository conformance query")
        return 0
    except (ValueError, TypeError, KeyError, OSError, UnicodeError, RecursionError):
        print("Repository conformance input denied; inspect admitted public evidence and exact owner pins", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
