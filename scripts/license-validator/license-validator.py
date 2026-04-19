#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate npm dependency licenses against a list of denied licenses.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--deny",
        nargs="+",
        metavar="LICENSE",
        required=True,
        help="License identifiers to block (e.g. GPL-3.0 AGPL-3.0).",
    )
    return parser.parse_args()


def load_deps(cwd: Path) -> list[str]:
    pkg = json.loads((cwd / "package.json").read_text(encoding="utf-8"))
    return list({**pkg.get("dependencies", {}), **pkg.get("devDependencies", {})}.keys())


def fetch_license(dep: str, cwd: Path) -> str:
    result = subprocess.run(
        ["npm", "show", dep, "--json"],
        cwd=cwd,
        text=True,
        capture_output=True,
    )
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or "npm show failed")
    info = json.loads(result.stdout)
    return info.get("license") or "UNKNOWN"


def main() -> int:
    args = parse_args()
    denied: frozenset[str] = frozenset(args.deny)
    cwd = Path.cwd()

    try:
        deps = load_deps(cwd)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Failed to load package.json: {e}", file=sys.stderr)
        return 1

    has_violation = False

    for dep in deps:
        try:
            license_ = fetch_license(dep, cwd)
            if license_ in denied:
                print(f"[VIOLATION] {dep}: {license_}", file=sys.stderr)
                has_violation = True
            else:
                print(f"[OK] {dep}: {license_}")
        except (RuntimeError, json.JSONDecodeError) as e:
            print(f"[WARN] {dep}: failed to fetch ({e})", file=sys.stderr)

    if has_violation:
        print("\nRestricted or undisclosed license detected.", file=sys.stderr)
        return 1

    print("\nLicense check passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
