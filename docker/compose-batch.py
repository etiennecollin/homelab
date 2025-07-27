#!/usr/bin/env python3

import argparse
import subprocess
import sys
from pathlib import Path

# ANSI color codes
COLORS = {
    "red": "\033[31m",
    "green": "\033[32m",
    "yellow": "\033[33m",
    "blue": "\033[34m",
    "reset": "\033[0m",
}

IGNORE_FILE = ".projectignore"


def color(msg: str, color: str = "reset", prefix: str = ""):
    code = COLORS.get(color, COLORS["reset"])
    print(f"{code}{prefix}{msg}{COLORS['reset']}")


def error(msg: str, prefix: str = ""):
    color(msg, "red", prefix)


def warning(msg: str, prefix: str = ""):
    color(msg, "yellow", prefix)


def success(msg: str, prefix: str = ""):
    color(msg, "green", prefix)


def info(msg: str, prefix: str = ""):
    color(msg, "blue", prefix)


def main():
    parser = argparse.ArgumentParser(description="Batch Docker Compose helper across projects")
    parser.add_argument("-p", "--pull", action="store_true", help="docker compose pull")
    parser.add_argument("-u", "--up", action="store_true", help="docker compose up")
    parser.add_argument("-d", "--down", action="store_true", help="docker compose down")
    parser.add_argument("--dry", action="store_true", help="dry run (no changes)")
    parser.add_argument("projects", nargs="*", help="project names or 'all'")
    args = parser.parse_args()

    actions = []
    if args.pull:
        actions.append("pull")
    if args.up:
        actions.append("up")
    if args.down:
        actions.append("down")

    if not actions:
        warning("No actions specified; exiting.")
        sys.exit(0)

    base_dir = Path(__file__).resolve().parent

    # Discover all projects
    all_projects = [p.name for p in base_dir.iterdir() if p.is_dir()]

    # Determine targets
    if not args.projects or "all" in args.projects:
        projects = all_projects
    else:
        projects = [p for p in args.projects if p in all_projects]
        for p in args.projects:
            if p not in all_projects:
                warning(f"Warning: project '{p}' not found – skipping.")

    success(f"Actions: {actions}")
    success(f"Projects: {projects}")

    for project in projects:
        project_dir = base_dir / project
        info(f"=== Project: {project}")

        if (project_dir / IGNORE_FILE).exists():
            color(f"-> skipping (ignore file present)", "yellow")
            continue

        prefix = "[DRY] " if args.dry else ""
        for action in actions:
            cmd = ["docker", "compose", "--env-file", "../secret.env"]
            if action == "pull":
                info(f"-> pulling latest images", prefix)
                cmd.append("pull")
            elif action == "up":
                info(f"-> starting containers", prefix)
                cmd.extend(["up", "-d", "--force-recreate"])
            elif action == "down":
                info(f"-> stopping containers", prefix)
                cmd.append("down")

            if not args.dry:
                subprocess.run(cmd, cwd=project_dir, check=True)


if __name__ == "__main__":
    main()
