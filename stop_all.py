#!/usr/bin/env python3
"""MedXP - Stop All Services (cross-platform)

Kills backend, middleware, and frontend processes by port.
Use when services were started manually or from another terminal.

Usage: python stop_all.py
"""

import re
import subprocess
import sys

PORTS = [8000, 5001, 8080]  # backend, middleware, frontend


def kill_by_port(port: int) -> bool:
    """Kill process(es) listening on the given port. Returns True if any were killed."""
    killed = False
    if sys.platform == "win32":
        result = subprocess.run(
            ["netstat", "-ano"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        for line in result.stdout.splitlines():
            if f":{port}" not in line or "LISTENING" not in line.upper():
                continue
            match = re.search(r"\s+(\d+)\s*$", line)
            if match:
                pid = int(match.group(1))
                if pid > 0:
                    subprocess.run(
                        ["taskkill", "/PID", str(pid), "/T", "/F"],
                        capture_output=True,
                        timeout=5,
                    )
                    killed = True
    else:
        # lsof -ti:PORT
        result = subprocess.run(
            ["lsof", "-ti", f":{port}"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        for pid_str in result.stdout.strip().split():
            if pid_str.isdigit():
                try:
                    subprocess.run(
                        ["kill", "-9", pid_str],
                        capture_output=True,
                        timeout=5,
                    )
                    killed = True
                except Exception:
                    pass
    return killed


def main():
    print("\033[33mStopping MedXP services...\033[0m")
    for port in PORTS:
        if kill_by_port(port):
            print(f"\033[90m  Stopped process on port {port}\033[0m")
    print("\033[32mDone.\033[0m")


if __name__ == "__main__":
    main()
