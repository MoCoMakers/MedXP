#!/usr/bin/env python3
"""MedXP - Start All Services (cross-platform)

Brings up backend, middleware, and frontend. Requires .env (errors and quits if missing).
Creates .venv and installs npm deps if needed. Press Ctrl+C to stop all services.

Usage: python start_all.py
"""

import os
import shutil
import signal
import subprocess
import sys
import time
from pathlib import Path

# Project root
PROJECT_ROOT = Path(__file__).resolve().parent
VENV_DIR = PROJECT_ROOT / ".venv"
if sys.platform == "win32":
    VENV_PYTHON = VENV_DIR / "Scripts" / "python.exe"
else:
    VENV_PYTHON = VENV_DIR / "bin" / "python"

# Requirement files to install into venv (order matters)
REQUIREMENTS_FILES = [
    PROJECT_ROOT / "requirements.txt",
    PROJECT_ROOT / "backend" / "requirements.txt",
    PROJECT_ROOT / "middleware" / "requirements.txt",
]

# Services: (name, work_dir, shell_command)
# Python services use venv; Frontend uses npm
SERVICES = [
    ("Backend", PROJECT_ROOT / "backend", None),   # cmd built from venv + main.py
    ("Middleware", PROJECT_ROOT / "middleware", None),
    ("Frontend", PROJECT_ROOT / "frontend", "npm run dev"),
]

# Track child processes for cleanup
processes: list[tuple[str, subprocess.Popen]] = []


def get_python_cmd(work_dir: Path, script: str) -> str:
    """Build shell command to run Python script with venv."""
    py = VENV_PYTHON.resolve()
    return f'"{py}" {script}'


def check_env() -> bool:
    """Check .env exists. Returns False and quits if missing."""
    if not (PROJECT_ROOT / ".env").exists():
        print("\033[31mPreflight failed: .env missing.\033[0m")
        print("\033[31m  Copy .env.example to .env and set MINIMAX_API_KEY or OPENAI_API_KEY.\033[0m\n")
        return False
    return True


def ensure_npm_deps() -> bool:
    """Install frontend npm deps if node_modules missing or empty."""
    frontend_dir = PROJECT_ROOT / "frontend"
    if not frontend_dir.exists() or not (frontend_dir / "package.json").exists():
        return True
    node_modules = frontend_dir / "node_modules"
    if node_modules.is_dir() and any(node_modules.iterdir()):
        return True
    if not shutil.which("npm"):
        print("\033[31m  npm not found in PATH. Install Node.js/npm and retry.\033[0m")
        return False
    print("\033[36mInstalling frontend npm dependencies...\033[0m")
    result = subprocess.run("npm install", cwd=frontend_dir, shell=True)
    if result.returncode != 0:
        print("\033[31m  npm install failed.\033[0m")
        return False
    print("\033[32m  npm install done.\033[0m")
    return True


def ensure_venv_and_deps() -> bool:
    """Create venv if needed and install requirements."""
    if not VENV_DIR.exists():
        print("\033[36mCreating project venv at .venv...\033[0m")
        result = subprocess.run(
            [sys.executable, "-m", "venv", str(VENV_DIR)],
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            print("\033[31m  Failed to create venv:\033[0m", result.stderr or result.stdout)
            return False
        print("\033[32m  Venv created.\033[0m")
    for req in REQUIREMENTS_FILES:
        if not req.exists():
            continue
        rel = req.relative_to(PROJECT_ROOT)
        print(f"\033[36mInstalling {rel} into venv...\033[0m")
        result = subprocess.run(
            [str(VENV_PYTHON), "-m", "pip", "install", "-r", str(req)],
            cwd=PROJECT_ROOT,
        )
        if result.returncode != 0:
            print(f"\033[33m  Warning: pip install -r {rel} had issues (continuing)\033[0m")
    return True


def run_preflight() -> bool:
    """Check .env (error and quit if missing), then ensure venv and npm deps."""
    if not check_env():
        return False
    if not ensure_npm_deps():
        return False
    if not ensure_venv_and_deps():
        return False
    return True


def start_service(name: str, work_dir: Path, cmd: str | None) -> subprocess.Popen:
    """Start a service via shell. Python services use venv."""
    print(f"\033[36mStarting {name}...\033[0m")
    if cmd is None:
        # Python service: use venv
        script = "main.py" if "backend" in str(work_dir).replace("\\", "/") else "app.py"
        cmd = get_python_cmd(work_dir, script)
    env = os.environ.copy()
    env["PYTHONPATH"] = str(PROJECT_ROOT)
    kwargs: dict = {
        "shell": True,
        "cwd": work_dir,
        "env": env,
        "stdout": subprocess.DEVNULL,
        "stderr": subprocess.DEVNULL,
    }
    if sys.platform == "win32":
        kwargs["creationflags"] = subprocess.CREATE_NEW_PROCESS_GROUP
    else:
        kwargs["executable"] = "/bin/bash"
        kwargs["start_new_session"] = True
    proc = subprocess.Popen(cmd, **kwargs)
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
    def handler(signum, frame):
        stop_all()
        sys.exit(0)

    signal.signal(signal.SIGINT, handler)
    signal.signal(signal.SIGTERM, handler)
    if hasattr(signal, "SIGBREAK"):
        signal.signal(signal.SIGBREAK, handler)

    # Preflight first; quit immediately if prerequisites missing
    if not run_preflight():
        sys.exit(1)

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
    print("\033[90m  Frontend:   http://localhost:8080\033[0m")
    print("\n\033[33mPress Ctrl+C to stop all services.\033[0m\n")

    try:
        while True:
            if all(p.poll() is not None for _, p in processes):
                print("\033[33mAll services exited.\033[0m")
                break
            time.sleep(1)
    finally:
        stop_all()


if __name__ == "__main__":
    main()
