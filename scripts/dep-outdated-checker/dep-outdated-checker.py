#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Check npm dependencies for outdated versions.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--days",
        type=int,
        default=180,
        metavar="N",
        help="Flag packages whose latest release is older than N days.",
    )
    parser.add_argument(
        "--severity",
        choices=["patch", "minor", "major"],
        default="minor",
        help="Minimum version bump level to consider.",
    )
    parser.add_argument(
        "--ignore",
        nargs="*",
        metavar="PKG",
        default=[],
        help="Package names to skip.",
    )
    parser.add_argument(
        "--format",
        choices=["text", "json"],
        default="text",
        help="Output format.",
    )
    return parser.parse_args()


def load_deps(cwd: Path) -> dict[str, str]:
    pkg = json.loads((cwd / "package.json").read_text(encoding="utf-8"))
    return {**pkg.get("dependencies", {}), **pkg.get("devDependencies", {})}


def fetch_info(dep: str, cwd: Path) -> dict:
    result = subprocess.run(
        ["npm", "show", dep, "--json"],
        cwd=cwd,
        text=True,
        capture_output=True,
    )
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or "npm show failed")
    return json.loads(result.stdout)


def parse_version(v: str) -> tuple[int, int, int]:
    v = v.lstrip("^~>=<")
    parts = v.split(".")
    try:
        return (int(parts[0]), int(parts[1]), int(parts[2].split("-")[0]))
    except (IndexError, ValueError):
        return (0, 0, 0)


def bump_level(current: tuple, latest: tuple) -> str:
    if latest[0] > current[0]:
        return "major"
    if latest[1] > current[1]:
        return "minor"
    if latest[2] > current[2]:
        return "patch"
    return "none"


SEVERITY_RANK = {"patch": 0, "minor": 1, "major": 2}


def days_since(iso_date: str) -> int:
    dt = datetime.fromisoformat(iso_date.replace("Z", "+00:00"))
    return (datetime.now(timezone.utc) - dt).days


def main() -> int:
    args = parse_args()
    ignored: frozenset[str] = frozenset(args.ignore)
    cwd = Path.cwd()

    try:
        deps = load_deps(cwd)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Failed to load package.json: {e}", file=sys.stderr)
        return 1

    results = []
    has_stale = False

    for dep, installed_range in deps.items():
        if dep in ignored:
            results.append({"name": dep, "status": "ignored"})
            if args.format == "text":
                print(f"[IGNORE] {dep}: skipped")
            continue

        try:
            info = fetch_info(dep, cwd)
        except (RuntimeError, json.JSONDecodeError) as e:
            results.append({"name": dep, "status": "error", "error": str(e)})
            if args.format == "text":
                print(f"[WARN]   {dep}: failed to fetch ({e})", file=sys.stderr)
            continue

        latest_version: str = info.get("version", "0.0.0")
        time_map: dict = info.get("time", {})
        latest_date: str | None = time_map.get(latest_version)

        current_tuple = parse_version(installed_range)
        latest_tuple = parse_version(latest_version)
        level = bump_level(current_tuple, latest_tuple)

        age_days = days_since(latest_date) if latest_date else None
        is_stale = (
            age_days is not None
            and age_days >= args.days
            and SEVERITY_RANK.get(level, -1) >= SEVERITY_RANK[args.severity]
        )

        status = "stale" if is_stale else "ok"
        if is_stale:
            has_stale = True

        age_str = f"{age_days} days ago" if age_days is not None else "unknown date"
        results.append({
            "name": dep,
            "status": status,
            "installed": installed_range,
            "latest": latest_version,
            "bump": level,
            "age_days": age_days,
        })

        if args.format == "text":
            tag = "[STALE]" if is_stale else "[OK]   "
            dest = sys.stderr if is_stale else sys.stdout
            print(
                f"{tag}  {dep}: {installed_range} → {latest_version}"
                f"  ({age_str}, {level} bump)",
                file=dest,
            )

    if args.format == "json":
        print(json.dumps(results, indent=2))
    elif has_stale:
        stale_count = sum(1 for r in results if r.get("status") == "stale")
        print(f"\n{stale_count} stale package(s) found.", file=sys.stderr)
        return 1
    else:
        print("\nAll packages are up to date.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
