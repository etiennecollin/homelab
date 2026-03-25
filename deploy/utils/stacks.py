import json
from dataclasses import dataclass, field
from pathlib import Path
from shlex import quote
from textwrap import dedent
from typing import Any, Callable, Optional, cast

from pyinfra.context import host
from pyinfra.facts.server import Command
from pyinfra.operations import files, server

from .types import Directory, FileCopy
from .utils import dget, remote_path

BASE_DIR = Path(__file__).resolve().parents[2]
STACKS_DIR = BASE_DIR / "stacks"
TEMPLATES_DIR = BASE_DIR / "deploy" / "templates"


@dataclass
class StackBase:
    name: str

    directories: list[Directory] = field(default_factory=list)
    static_files: list[FileCopy] = field(default_factory=list)
    template_files: list[FileCopy] = field(default_factory=list)
    post_deploy: Optional[Callable[["Stack"], None]] = None


@dataclass
class StackConfig:
    enabled: bool = True
    env: dict[str, str] = field(default_factory=dict)
    template_vars: dict[str, Any] = field(default_factory=dict)


@dataclass
class Stack:
    base: StackBase
    config: StackConfig = field(default_factory=StackConfig)

    @property
    def name(self) -> str:
        return self.base.name

    @property
    def enabled(self) -> bool:
        return self.config.enabled

    def deploy(self):
        # Directories
        local_stack_dir = STACKS_DIR / self.name
        remote_stack_dir = remote_path(self.name)

        # Environment
        shared_env = dget("env", {}) or {}

        # -------------------------
        # Ensure directory
        # -------------------------
        files.directory(
            name=f"[{self.name}] create stack directory",
            path=str(remote_stack_dir),
            mode="755",
            user=dget("docker_user"),
            group=dget("docker_group"),
            _sudo=True,
        )

        # -------------------------
        # Deploy directories
        # -------------------------
        for dir in self.base.directories:
            files.directory(
                name=f"[{self.name}] create directory {dir.path}",
                path=str(dir.resolve_path(remote_stack_dir)),
                mode=dir.mode,
                user=dget("docker_user"),
                group=dget("docker_group"),
                _sudo=True,
            )

        # -------------------------
        # Deploy compose.yaml
        # -------------------------
        files.put(
            name=f"[{self.name}] deploy compose.yaml",
            src=str(local_stack_dir / "compose.yaml"),
            dest=str(remote_stack_dir / "compose.yaml"),
            mode="644",
            user=dget("docker_user"),
            group=dget("docker_group"),
            _sudo=True,
        )

        # -------------------------
        # Deploy static files
        # -------------------------
        for file in self.base.static_files:
            dest = str(file.resolve_dest(remote_stack_dir))

            if file.src is not None:
                files.put(
                    name=f"[{self.name}] deploy {file.dest}",
                    src=str(file.resolve_src(local_stack_dir)) if isinstance(file.src, Path) else file.src,
                    dest=dest,
                    mode=file.mode,
                    create_remote_dir=False,  # Enforce usage of self.base.directories
                    user=dget("docker_user"),
                    group=dget("docker_group"),
                    _sudo=True,
                )
            else:
                files.file(
                    name=f"[{self.name}] create file {file.dest}",
                    path=dest,
                    mode=file.mode,
                    create_remote_dir=False,  # Enforce usage of self.base.directories
                    user=dget("docker_user"),
                    group=dget("docker_group"),
                    _sudo=True,
                )

        # -------------------------
        # Deploy stack.env
        # -------------------------
        files.template(
            name=f"[{self.name}] deploy stack.env",
            src=str(TEMPLATES_DIR / "stack.env.j2"),
            dest=str(remote_stack_dir / "stack.env"),
            mode="600",
            user=dget("docker_user"),
            group=dget("docker_group"),
            _sudo=True,
            shared_env=shared_env,
            stack_env=self.config.env,
        )

        # -------------------------
        # Deploy templates
        # -------------------------
        template_context = {
            **shared_env,  # shared
            **self.config.env,  # config
            **self.config.template_vars,  # template
        }

        for file in self.base.template_files:
            assert file.src is not None, "Template files require a source path"
            files.template(
                name=f"[{self.name}] deploy {file.dest}",
                src=str(file.resolve_src(local_stack_dir)) if isinstance(file.src, Path) else file.src,
                dest=str(file.resolve_dest(remote_stack_dir)),
                mode=file.mode,
                create_remote_dir=False,  # Enforce usage of self.base.directories
                user=dget("docker_user"),
                group=dget("docker_group"),
                _sudo=True,
                **cast(dict[str, Any], template_context),
            )

        # -------------------------
        # Post-deploy hook
        # -------------------------
        if self.base.post_deploy:
            self.base.post_deploy(self)

    def start(self):
        if dget("dry_run", False):
            return

        remote_stack_dir = remote_path(self.name)
        sudo_docker = dget("docker_use_sudo", True)

        # -------------------------
        # Validate
        # -------------------------
        server.shell(
            name=f"[{self.name}] validate compose",
            commands=[dedent(f"""
                    cd {quote(str(remote_stack_dir))} && \\
                    docker compose --env-file stack.env config > /dev/null
                """).strip()],
            _sudo=sudo_docker,
        )

        # -------------------------
        # Pull
        # -------------------------
        server.shell(
            name=f"[{self.name}] pull images",
            commands=[dedent(f"""
                    cd {quote(str(remote_stack_dir))} && \\
                    docker compose --env-file stack.env pull
                """).strip()],
            _sudo=sudo_docker,
        )

        # -------------------------
        # Up
        # -------------------------
        server.shell(
            name=f"[{self.name}] deploy stack",
            commands=[dedent(f"""
                    cd {quote(str(remote_stack_dir))} && \\
                    docker compose --env-file stack.env up -d --remove-orphans --force-recreate
                """).strip()],
            _sudo=sudo_docker,
        )

    def teardown(self):
        remote_stack_dir = remote_path(self.name)
        sudo_docker = dget("docker_use_sudo", True)

        # -------------------------
        # Check if stack is running
        # -------------------------
        output = host.get_fact(
            Command,
            command="docker compose ls --format json",
            _sudo=sudo_docker,
        )
        stacks = json.loads(output)
        is_running = any(
            stack["Name"] == self.name
            and str(stack["Status"]).startswith("running")
            and str(stack["ConfigFiles"]).startswith(str(remote_stack_dir))
            for stack in stacks
        )

        # -------------------------
        # Bring stack down if needed
        # -------------------------
        server.shell(
            name=f"[{self.name}] teardown stack",
            commands=[dedent(f"""
                cd {quote(str(remote_stack_dir))} && \\
                docker compose --env-file stack.env down --remove-orphans
            """).strip()],
            _if=lambda: is_running,
            _sudo=sudo_docker,
        )
