#!/usr/bin/env python3
"""MedXP - Clean dependency folders

Removes folders and files that start_all.py will recreate:
- .venv (Python virtual environment)
- frontend/node_modules
- frontend/package-lock.json

Usage: python clean_deps.py
"""

import shutil
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent

TARGETS = [
    (PROJECT_ROOT / ".venv", "Python venv"),
    (PROJECT_ROOT / "frontend" / "node_modules", "Frontend node_modules"),
    (PROJECT_ROOT / "frontend" / "package-lock.json", "Frontend package-lock.json"),
]


def main() -> None:
    print("\033[36mCleaning dependency folders (start_all.py will recreate them)...\033[0m")
    for path, label in TARGETS:
        if path.exists():
            try:
                if path.is_dir():
                    shutil.rmtree(path)
                else:
                    path.unlink()
                print(f"\033[32m  Removed {label}\033[0m")
            except OSError as e:
                print(f"\033[31m  Failed to remove {label}: {e}\033[0m")
        else:
            print(f"\033[90m  Skipped {label} (not found)\033[0m")
    print("\033[32mDone. Run python start_all.py to reinstall.\033[0m\n")


if __name__ == "__main__":
    main()
