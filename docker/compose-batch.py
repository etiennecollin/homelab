#!/usr/bin/env python3

import os
import subprocess
import sys
from enum import Enum

# ==============================================================================
# Utilities
# ==============================================================================


IGNORE_FILE = ".projectignore"
ALL_PROJECTS_TOKEN = "all"


class Color(Enum):
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


def color(msg: str, color: Color = Color.reset, prefix: str = "") -> str:
    return f"{color}{prefix}{msg}{Color.reset}"


def error(msg: str, prefix: str = "") -> None:
    print(color(msg, Color.red, prefix))


def warning(msg: str, prefix: str = "") -> None:
    print(color(msg, Color.yellow, prefix))


def warning_confirm(msg: str, prefix: str = "") -> bool:
    input_msg = color(msg, Color.yellow, prefix)
    input_msg += color(" [y/N] ", Color.dark)
    ans = input(input_msg)
    return ans.strip().lower() == "y"


def success(msg: str, prefix: str = "") -> None:
    print(color(msg, Color.green, prefix))


def info(msg: str, prefix: str = "") -> None:
    print(color(msg, Color.blue, prefix))


# ==============================================================================
# Check Python version
# ==============================================================================

MIN_PYTHON_VERSION = (3, 10)


def version_tuple(version_str: str) -> tuple[int, ...]:
    """Convert 'Python 3.x.y' -> (3, x, y)."""
    parts = version_str.strip().split()
    if not parts or not parts[0].lower().startswith("python"):
        error(f"Unexpected version output: {version_str}")
        exit(1)
    return tuple(map(int, parts[1].split(".")))


def ensure_min_version() -> None:
    if sys.version_info >= MIN_PYTHON_VERSION:
        return

    warning(f"Current Python version: {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")
    warning(f"Python {MIN_PYTHON_VERSION[0]}.{MIN_PYTHON_VERSION[1]}+ is required.")

    try:
        output = subprocess.check_output(["python", "--version"], stderr=subprocess.STDOUT, text=True)
        py_version = version_tuple(output)
    except Exception as e:
        error(f"Error checking Python version: {e}")
        exit(1)

    # If python is new enough, re-exec
    if py_version >= MIN_PYTHON_VERSION:
        info(f"Re-executing with Python {py_version[0]}.{py_version[1]}.{py_version[2]}")
        os.execvp("python", ["--"] + sys.argv)

    # Neither works → error
    error(f"Could not find a Python interpreter matching the minimum version requirement.")
    sys.exit(1)


ensure_min_version()

# ==============================================================================
# Main imports
# ==============================================================================

import argparse
from dataclasses import dataclass
from pathlib import Path
from sys import exit
from typing import Any, Callable, List, Optional, Union

# ==============================================================================
# Custom Actions
# ==============================================================================


def prune_all() -> None:
    """
    Interactively prune all Docker containers, images, and networks.
    Uses colorized output consistent with the rest of the script.
    """
    failed = False

    print("Pruning containers...")
    if subprocess.run(["docker", "container", "prune", "-f"]).returncode != 0:
        failed = True

    print("Pruning images...")
    if subprocess.run(["docker", "image", "prune", "-af"]).returncode != 0:
        failed = True

    print("Pruning networks...")
    if subprocess.run(["docker", "network", "prune", "-f"]).returncode != 0:
        failed = True

    if failed:
        warning("One or more prunes failed")
    else:
        success("Pruning done")


# ==============================================================================
# Action Enum
# Add entries to this enum to add new actions.
# ==============================================================================

ActionCommand = Union[List[str], Callable[[], None]]


@dataclass
class ActionData:
    """Data structure for Action enum values."""

    flag: str
    command: ActionCommand
    description: str
    requires_confirmation: bool = False
    standalone: bool = False


class Action(Enum):
    """
    Docker Compose actions that can be performed on projects.

    Each entry corresponds to a docker-compose subcommand.
    """

    # ==========================================================================
    # Constants
    # ==========================================================================

    __COMPOSE_COMMAND = ["docker", "compose", "--env-file", "../secret.env"]

    # ==========================================================================
    # Enum entries
    # ==========================================================================

    pull = ActionData(
        "p",
        [*__COMPOSE_COMMAND, "pull"],
        "pull the latest images for services",
    )
    up = ActionData(
        "u",
        [*__COMPOSE_COMMAND, "up", "-d", "--force-recreate"],
        "start services in detached mode, recreating containers",
    )
    down = ActionData(
        "d",
        [*__COMPOSE_COMMAND, "down", "--remove-orphans"],
        "stop and remove containers, networks, and orphans",
    )
    build = ActionData(
        "b",
        [*__COMPOSE_COMMAND, "build", "--pull"],
        "build services with latest base images",
    )
    build_clean = ActionData(
        "B",
        [*__COMPOSE_COMMAND, "build", "--pull", "--no-cache"],
        "build services with latest base images, ignoring cache",
    )
    prune = ActionData(
        "P",
        prune_all,
        "interactively prune all Docker containers, images, and networks",
        requires_confirmation=True,
        standalone=True,
    )

    # ==========================================================================
    # Class properties and Python methods
    # ==========================================================================
    @property
    def command_str(self) -> str:
        """Return the command as a string for display purposes."""
        cmd = self.value.command
        if callable(cmd):
            return cmd.__name__ if hasattr(cmd, "__name__") else str(cmd)
        return " ".join(cmd)

    @property
    def flags(self) -> list[str]:
        """Return the flags corresponding to this action."""
        short = self.value.flag
        long = self.name.lower().replace("_", "-")
        return [f"-{short}", f"--{long}"]

    def __str__(self):
        return self.name.replace("_", "-")

    def __repr__(self):
        return self.name.replace("_", "-")

    # ==========================================================================
    # Class methods
    # ==========================================================================
    __cached = False

    def exec(self, cwd: Optional[Path] = None, dry: bool = False) -> None:
        if dry:
            info(f"[DRY] {self.command_str}")
            return

        if self.value.requires_confirmation and not self.__cached:
            warning(
                "This action is potentially destructive and requires confirmation. That confirmation is cached for the session."
            )
            if not warning_confirm(f"Are you sure you want to execute '{self.command_str}'?"):
                info("Action cancelled")
                return
            self.__cached = True

        cmd = self.value.command
        if callable(cmd):
            cmd()
        else:
            if subprocess.run(cmd, cwd=cwd).returncode != 0:
                error(f"Command failed: {self.command_str}")


# ==============================================================================
# Main functions
# ==============================================================================


def setup_parser() -> argparse.Namespace:
    """
    Set up the command-line argument parser for the script.
    """
    epilog_text = f"""
Additional Information:
  - Ignore a project by placing a '{IGNORE_FILE}' file in its directory.
  - Actions are executed in the order they appear on the command line.
    - Example: -p -u -d will pull, then up, then down.
    - Example: -u -p -d will up, then pull, then down.
"""
    parser = argparse.ArgumentParser(
        description="Homelab helper script actions to be performed on multiple projects.",
        epilog=epilog_text,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--dry", action="store_true", help="dry run (no changes)")
    parser.add_argument("-l", "--list", action="store_true", help="display available projects and exit")
    parser.add_argument("-a", "--all", action="store_true", help="target all available projects")

    for action in sorted(Action, key=lambda a: a.name):
        parser.add_argument(
            *action.flags,
            action="store_true",
            help=action.value.description,
        )
    parser.add_argument("projects", nargs="*", help="project names")
    return parser.parse_args()


def get_actions_in_order() -> List[Action]:
    """
    Parse actions from command line arguments in the order they were specified.
    Returns a list of Action enums in the order they appeared on the command line.
    """

    # Create a mapping from flag strings to Action enums
    flag_to_action = {}
    for action in Action:
        for flag in action.flags:
            flag_to_action[flag] = action

    actions_in_order = []
    seen_actions = set()
    for arg in sys.argv[1:]:  # Skip script name
        if arg in flag_to_action:
            action = flag_to_action[arg]
            # Only add each action once (in case of duplicate flags)
            if action not in seen_actions:
                actions_in_order.append(action)
                seen_actions.add(action)

    return actions_in_order


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
            print(f"- {Color.dark}{project}{Color.reset} {Color.yellow}(ignored){Color.reset}")
        else:
            print(f"- {project}")


def main():
    args = setup_parser()

    base_dir = Path(__file__).resolve().parent
    all_projects = [p.name for p in base_dir.iterdir() if p.is_dir()]

    if args.list:
        list_projects(all_projects, base_dir)
        exit(0)

    actions = get_actions_in_order()
    if not actions:
        warning("No actions specified, nothing to do")
        exit(0)

    actions_all_standalone = all(action.value.standalone for action in actions)

    projects: list[str] = []
    if args.all:
        projects = all_projects
        success(f"Targeting all available projects")
    else:
        projects, missing = parse_projects_selection(args.projects, all_projects)
        if missing:
            warning(f"Projects not found, skipping: {missing}")
        if not projects and not actions_all_standalone:
            warning("No valid projects specified")
            exit(1)

    if projects:
        success(f"Projects: {projects}")
    success(f"Actions: {actions}")

    for action in actions:
        info(f"┌──{' [DRY] ' if args.dry else ' '}Action: {action.command_str}", prefix="\n")

        if action.value.standalone:
            info(f"│ (standalone)")
            action.exec(dry=args.dry)
            continue

        for project in projects:
            info(f"│ Project: {project}")

            project_dir = base_dir / project
            if (project_dir / IGNORE_FILE).exists():
                warning(f"│ skipping ({IGNORE_FILE} file present)")
                continue

            action.exec(cwd=project_dir, dry=args.dry)

    success("\nAll done")


if __name__ == "__main__":
    main()
