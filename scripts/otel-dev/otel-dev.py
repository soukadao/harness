#!/usr/bin/env python3
"""otel-dev: local observability stack manager (Vector + VictoriaMetrics/Logs/Traces)"""

import argparse
import os
import subprocess
import sys
import urllib.request
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
COMPOSE_FILE = SCRIPT_DIR / "docker-compose.yml"

SERVICES = {
    "Victoria Metrics": ("http://localhost:{VM_PORT}/health", "VM_PORT", "8428", "PromQL: http://localhost:{VM_PORT}/vmui"),
    "Victoria Logs":    ("http://localhost:{VL_PORT}/health", "VL_PORT", "9428", "LogQL: http://localhost:{VL_PORT}/select/vmui"),
    "Victoria Traces":  ("http://localhost:{VT_PORT}/health", "VT_PORT", "9999", "TraceQL: http://localhost:{VT_PORT}/vmui"),
}

OTLP_GRPC_PORT = os.environ.get("OTLP_GRPC_PORT", "4317")
OTLP_HTTP_PORT = os.environ.get("OTLP_HTTP_PORT", "4318")


def _compose(*args: str) -> int:
    cmd = ["docker", "compose", "-f", str(COMPOSE_FILE)] + list(args)
    return subprocess.run(cmd).returncode


def _port(env_key: str, default: str) -> str:
    return os.environ.get(env_key, default)


def _check_health(url: str) -> bool:
    try:
        with urllib.request.urlopen(url, timeout=2) as r:
            return r.status == 200
    except Exception:
        return False


def cmd_start() -> int:
    print("Starting observability stack...")
    rc = _compose("up", "-d", "--wait")
    if rc != 0:
        print("[FAIL] Failed to start stack.", file=sys.stderr)
        return rc
    print("\n[OK] Stack is running.\n")
    _print_endpoints()
    return 0


def cmd_stop() -> int:
    print("Stopping observability stack...")
    return _compose("down")


def cmd_status() -> int:
    print("Checking stack status...\n")
    all_ok = True
    for name, (url_tmpl, env_key, default, ui_tmpl) in SERVICES.items():
        port = _port(env_key, default)
        url = url_tmpl.replace("{" + env_key + "}", port)
        ok = _check_health(url)
        status = "[OK]  " if ok else "[DOWN]"
        if not ok:
            all_ok = False
        print(f"  {status} {name} ({url})")
    print()
    if all_ok:
        _print_endpoints()
    else:
        print("Some services are not running. Try: python3 otel-dev.py start", file=sys.stderr)
    return 0 if all_ok else 1


def cmd_reset() -> int:
    print("Stopping stack and removing all data volumes...")
    rc = _compose("down", "-v")
    if rc == 0:
        print("[OK] All data has been reset.")
    return rc


def _print_endpoints() -> None:
    print("  OTLP endpoints (configure your app here):")
    print(f"    gRPC : localhost:{OTLP_GRPC_PORT}")
    print(f"    HTTP : localhost:{OTLP_HTTP_PORT}")
    print()
    print("  Query endpoints:")
    for name, (_, env_key, default, ui_tmpl) in SERVICES.items():
        port = _port(env_key, default)
        ui = ui_tmpl.replace("{" + env_key + "}", port)
        print(f"    {name}: {ui}")
    print()


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Manage local observability stack for development"
    )
    subparsers = parser.add_subparsers(dest="command", metavar="COMMAND")
    subparsers.add_parser("start",  help="Start the stack")
    subparsers.add_parser("stop",   help="Stop the stack")
    subparsers.add_parser("status", help="Check stack health and show endpoints")
    subparsers.add_parser("reset",  help="Stop and remove all data volumes")

    args = parser.parse_args()

    commands = {
        "start":  cmd_start,
        "stop":   cmd_stop,
        "status": cmd_status,
        "reset":  cmd_reset,
    }

    if args.command not in commands:
        parser.print_help()
        return 1

    return commands[args.command]()


if __name__ == "__main__":
    sys.exit(main())
