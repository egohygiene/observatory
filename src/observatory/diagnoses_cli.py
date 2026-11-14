"""Offline diagnosis metadata projection and optional Intelligence composition."""
import argparse
import json
from pathlib import Path
import sys

from . import diagnoses
from . import public_reviews as shared


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, allow_abbrev=False)
    parser.add_argument("--targets", required=True, type=Path)
    parser.add_argument("--evidence", action="append", type=Path, default=[])
    parser.add_argument("--as-of", required=True)
    parser.add_argument("--snapshot", type=Path, help="Optional existing public repository Intelligence snapshot")
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args(argv)
    try:
        targets = shared.parse(shared.base._read(args.targets))
        wrappers = []
        for path in args.evidence:
            value = shared.parse(shared.base._read(path))
            shared.require(isinstance(value, list)); wrappers.extend(value)
        model = diagnoses.build_diagnosis_view(wrappers, repositories=targets, as_of=args.as_of)
        if args.snapshot is not None:
            model = diagnoses.attach_to_snapshot(shared.parse(shared.base._read(args.snapshot)), model)
        destination = args.output.absolute()
        shared.require(not destination.exists() and ".." not in destination.parts
                       and not any(p.is_symlink() for p in (destination,*destination.parents)))
        destination.parent.mkdir(parents=True, exist_ok=True)
        with destination.open("x", encoding="utf-8") as handle:
            handle.write(json.dumps(model,indent=2,sort_keys=True,ensure_ascii=False,allow_nan=False)+"\n")
        return 0
    except (ValueError, TypeError, KeyError, AttributeError, OSError, UnicodeError, RecursionError):
        print("Public diagnosis metadata selection or output is incompatible", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
