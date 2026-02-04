#!/usr/bin/env python3
"""MedXP - Start All Services (cross-platform)

Brings up backend, middleware, and frontend.
Press Ctrl+C to stop all services; child processes are killed when this script exits.

Usage: python start_all.py
"""

import os
import signal
import subprocess
import sys
import time
from pathlib import Path

# Project root
PROJECT_ROOT = Path(__file__).resolve().parent

# Services: (name, work_dir, shell_command)
# Commands run via shell so PATH resolution works (e.g. npm.cmd on Windows)
SERVICES = [
    ("Backend", PROJECT_ROOT / "backend", "python main.py"),
    ("Middleware", PROJECT_ROOT / "middleware", "python app.py"),
    ("Frontend", PROJECT_ROOT / "frontend", "npm run dev"),
]

# Track child processes for cleanup
processes: list[tuple[str, subprocess.Popen]] = []


def start_service(name: str, work_dir: Path, cmd: str) -> subprocess.Popen:
    """Start a service via shell (cmd on Windows, bash on macOS/Linux) for PATH resolution."""
    print(f"\033[36mStarting {name}...\033[0m")
    kwargs: dict = {
        "shell": True,
        "cwd": work_dir,
        "stdout": subprocess.DEVNULL,
        "stderr": subprocess.DEVNULL,
    }
    if sys.platform == "win32":
        kwargs["creationflags"] = subprocess.CREATE_NEW_PROCESS_GROUP
    else:
        kwargs["executable"] = "/bin/bash"
        kwargs["start_new_session"] = True
    proc = subprocess.Popen(
        cmd,
        **kwargs,
    )
    processes.append((name, proc))
    print(f"\033[32m  {name} started (PID {proc.pid})\033[0m")
    return proc


def stop_all():
    """Stop all child processes (and their children)."""
    print("\n\033[33mStopping all services...\033[0m")
    for name, proc in processes:
        try:
            if proc.poll() is None and proc.pid:
                if sys.platform == "win32":
                    # Kill process tree on Windows
                    subprocess.run(
                        ["taskkill", "/PID", str(proc.pid), "/T", "/F"],
                        capture_output=True,
                        timeout=5,
                    )
                else:
                    os.killpg(os.getpgid(proc.pid), signal.SIGTERM)
                print(f"\033[90m  Stopped {name} (PID {proc.pid})\033[0m")
        except (ProcessLookupError, OSError, AttributeError, subprocess.TimeoutExpired):
            pass
    processes.clear()
    print("\033[32mAll services stopped.\033[0m")


def main():
    # Handle Ctrl+C and normal exit
    def handler(signum, frame):
        stop_all()
        sys.exit(0)

    signal.signal(signal.SIGINT, handler)
    signal.signal(signal.SIGTERM, handler)
    if hasattr(signal, "SIGBREAK"):  # Windows
        signal.signal(signal.SIGBREAK, handler)

    print("\033[35m========================================\033[0m")
    print("\033[35m  MedXP - Starting All Services\033[0m")
    print("\033[35m========================================\033[0m")

    for name, work_dir, cmd in SERVICES:
        if not work_dir.exists():
            print(f"\033[33m  Skipping {name}: {work_dir} not found\033[0m")
            continue
        start_service(name, work_dir, cmd)
        time.sleep(2 if name == "Backend" else 1)

    print("\n\033[35m========================================\033[0m")
    print("\033[35m  All services started\033[0m")
    print("\033[35m========================================\033[0m")
    print("\033[90m  Backend:    http://localhost:8000\033[0m")
    print("\033[90m  Middleware: http://localhost:5001\033[0m")
    print("\033[90m  Frontend:   http://localhost:5173\033[0m")
    print("\n\033[33mPress Ctrl+C to stop all services.\033[0m\n")

    # Keep running until Ctrl+C
    try:
        while True:
            # Exit if all processes have died
            if all(p.poll() is not None for _, p in processes):
                print("\033[33mAll services exited.\033[0m")
                break
            time.sleep(1)
    finally:
        stop_all()


if __name__ == "__main__":
    main()
