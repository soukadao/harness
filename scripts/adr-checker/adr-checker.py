#!/usr/bin/env python3
"""adr-checker: Extract, validate, and filter ADR frontmatter."""

import argparse
import json
import sys
from pathlib import Path

VALID_STATUSES = {"proposed", "accepted", "deprecated", "superseded", "rejected"}


def parse_frontmatter(content: str) -> dict:
    if not content.startswith("---"):
        return {}
    parts = content.split("---", 2)
    if len(parts) < 3:
        return {}
    result = {}
    for line in parts[1].strip().splitlines():
        if ": " in line:
            key, val = line.split(": ", 1)
            val = val.strip()
            result[key.strip()] = None if val == "null" else val.strip('"')
    return result


def load_adrs(adr_dir: Path) -> list[dict]:
    adrs = []
    for path in sorted(adr_dir.glob("*.md")):
        if path.name == "template.md":
            continue
        content = path.read_text()
        fm = parse_frontmatter(content)
        if fm:
            fm["_path"] = str(path)
            adrs.append(fm)
    return adrs


def validate(adrs: list[dict]) -> list[str]:
    violations = []
    ids = {a["id"]: a for a in adrs if "id" in a}

    for adr in adrs:
        path = adr.get("_path", "")

        # Required fields
        for field in ("id", "title", "status", "date"):
            if not adr.get(field):
                violations.append(f"{path}: required field '{field}' is missing")

        # Status value
        status = adr.get("status")
        if status and status not in VALID_STATUSES:
            violations.append(f"{path}: invalid status '{status}'")

        # superseded_by reference integrity
        superseded_by = adr.get("superseded_by")
        if superseded_by and superseded_by not in ids:
            violations.append(f"{path}: superseded_by '{superseded_by}' does not exist")

        # supersedes reference integrity
        supersedes = adr.get("supersedes")
        if supersedes and supersedes not in ids:
            violations.append(f"{path}: supersedes '{supersedes}' does not exist")

        # superseded status requires superseded_by
        if status == "superseded" and not superseded_by:
            violations.append(f"{path}: status is superseded but superseded_by is not set")

        # accepted status must not have superseded_by
        if status == "accepted" and superseded_by:
            violations.append(f"{path}: status is accepted but superseded_by is set")

    # Duplicate id check
    seen_ids: dict[str, str] = {}
    for adr in adrs:
        adr_id = adr.get("id")
        if adr_id:
            if adr_id in seen_ids:
                violations.append(f"duplicate id '{adr_id}': {seen_ids[adr_id]} and {adr.get('_path')}")
            else:
                seen_ids[adr_id] = adr.get("_path", "")

    return violations


def format_adr(adr: dict) -> dict:
    return {k: v for k, v in adr.items() if not k.startswith("_")}


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate and filter ADR frontmatter.")
    parser.add_argument("--dir", default="docs/adr", help="ADR directory (default: docs/adr)")
    parser.add_argument("--status", help="Show only ADRs with the given status")
    parser.add_argument("--format", choices=["text", "json"], default="text", help="Output format")
    parser.add_argument("--validate", action="store_true", help="Run integrity validation (exit 1 on violations)")
    args = parser.parse_args()

    adr_dir = Path(args.dir)
    if not adr_dir.exists():
        print(f"[WARN] directory not found: {adr_dir}", file=sys.stderr)
        return 1

    adrs = load_adrs(adr_dir)

    if args.validate:
        violations = validate(adrs)
        for v in violations:
            print(f"[VIOLATION] {v}", file=sys.stderr)
        if violations:
            return 1
        print(f"[OK] {len(adrs)} ADR(s) passed validation")
        return 0

    # Filter by status
    filtered = adrs
    if args.status:
        filtered = [a for a in adrs if a.get("status") == args.status]

    if args.format == "json":
        print(json.dumps([format_adr(a) for a in filtered], ensure_ascii=False, indent=2))
    else:
        for adr in filtered:
            sid = adr.get("id", "-")
            title = adr.get("title", "-")
            status = adr.get("status", "-")
            date = adr.get("date", "-")
            sup_by = adr.get("superseded_by") or "-"
            print(f"[{status.upper():10}] ADR-{sid} ({date}) {title}  superseded_by={sup_by}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
