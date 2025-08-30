#!/usr/bin/env python3

import argparse
import subprocess
from enum import Enum
from pathlib import Path
from sys import exit
from typing import Any

# ==============================================================================
# Docker Compose actions
# Add entries to this enum to add new actions.
# ==============================================================================


class Action(Enum):
    """
    Docker Compose actions that can be performed on projects.

    Each entry corresponds to a docker-compose subcommand.
    """

    pull = {"flag": "p", "cmd": ["pull"]}
    up = {"flag": "u", "cmd": ["up", "-d", "--force-recreate"]}
    down = {"flag": "d", "cmd": ["down", "--remove-orphans"]}
    build = {"flag": "b", "cmd": ["build", "--pull"]}
    build_clean = {"flag": "B", "cmd": ["build", "--pull", "--no-cache"]}

    @property
    def command(self) -> list[str]:
        """Return the docker-compose subcommand arguments for this action."""
        return ["docker", "compose", "--env-file", "../secret.env", *self.value["cmd"]]

    @property
    def command_str(self) -> str:
        """Return the command as a string for display purposes."""
        return " ".join(self.command)

    @property
    def flags(self) -> list[str]:
        """Return the flags corresponding to this action."""
        short = self.value["flag"]
        long = self.name.lower().replace("_", "-")
        return [f"-{short}", f"--{long}"]

    def __str__(self):
        return self.name.replace("_", "-")

    def __repr__(self):
        return self.name.replace("_", "-")


# ==============================================================================
# Utilities
# ==============================================================================


class Colors(Enum):
    """
    ANSI color codes for terminal output.
    """

    red = "\033[31m"
    green = "\033[32m"
    yellow = "\033[33m"
    blue = "\033[34m"
    dark = "\033[90m"
    reset = "\033[0m"

    def __str__(self):
        return self.value

    def __repr__(self):
        return self.name


IGNORE_FILE = ".projectignore"
ALL_PROJECTS_TOKEN = "all"


def color(msg: str, color: Colors = Colors.reset, prefix: str = "") -> None:
    print(f"{color}{prefix}{msg}{Colors.reset}")


def error(msg: str, prefix: str = "") -> None:
    color(msg, Colors.red, prefix)


def warning(msg: str, prefix: str = "") -> None:
    color(msg, Colors.yellow, prefix)


def success(msg: str, prefix: str = "") -> None:
    color(msg, Colors.green, prefix)


def info(msg: str, prefix: str = "") -> None:
    color(msg, Colors.blue, prefix)


# ==============================================================================
# Main functions
# ==============================================================================


def setup_parser() -> argparse.Namespace:
    """
    Set up the command-line argument parser for the script.
    """
    parser = argparse.ArgumentParser(
        description="Batch Docker Compose helper across projects.",
        epilog=f"Ignore a project by placing a '{IGNORE_FILE}' file in its directory.",
    )
    parser.add_argument("--dry", action="store_true", help="dry run (no changes)")
    parser.add_argument("-l", "--list", action="store_true", help="display available projects and exit")
    parser.add_argument("-a", "--all", action="store_true", help="target all available projects")
    for action in Action:
        parser.add_argument(
            *action.flags,
            action="store_true",
            help=f"docker compose {action}",
        )
    parser.add_argument("projects", nargs="*", help="project names")
    return parser.parse_args()


def parse_projects_selection(user_targets: list[Any], all_projects: list[str]) -> tuple[list[str], list[str]]:
    """
    Filter and validate the user-selected projects against the available projects.

    Returns a tuple containing:
    - The list of valid user-selected projects.
    - The list of invalid user-selected projects.
    """
    projects: list[str] = []
    missing: list[str] = []

    for project in user_targets:
        if project in all_projects:
            projects.append(project)
        else:
            missing.append(project)

    return projects, missing


def list_projects(projects: list[str], base_dir: Path) -> None:
    """
    List all available projects in the current directory.
    Indicates if a project is ignored.
    """
    print("Available projects:")
    for project in sorted(projects):
        project_dir = base_dir / project
        if (project_dir / IGNORE_FILE).exists():
            print(f"- {Colors.dark}{project}{Colors.reset} {Colors.yellow}(ignored){Colors.reset}")
        else:
            print(f"- {project}")


def main():
    args = setup_parser()

    base_dir = Path(__file__).resolve().parent
    all_projects = [p.name for p in base_dir.iterdir() if p.is_dir()]

    if args.list:
        list_projects(all_projects, base_dir)
        exit(0)

    actions = [action for action in Action if getattr(args, action.name)]
    if not actions:
        warning("No actions specified, nothing to do")
        exit(0)

    projects: list[str] = []
    if args.all:
        projects = all_projects
        success(f"Targeting all available projects")
    else:
        projects, missing = parse_projects_selection(args.projects, all_projects)
        if missing:
            warning(f"Projects not found, skipping: {missing}")
        if not projects:
            warning("No valid projects specified")
            exit(1)

    success(f"Projects: {projects}")
    success(f"Actions: {actions}")

    for project in projects:
        info(f"=== Project: {project}", prefix="\n")

        project_dir = base_dir / project
        if (project_dir / IGNORE_FILE).exists():
            warning(f"-> skipping ({IGNORE_FILE} file present)")
            continue

        prefix = "[DRY] " if args.dry else ""
        for action in actions:
            info(f"-> {action.command_str}", prefix)
            if not args.dry:
                subprocess.run(action.command, cwd=project_dir, check=True)


if __name__ == "__main__":
    main()
