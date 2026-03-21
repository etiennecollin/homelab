import json
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from shlex import quote
from textwrap import dedent
from typing import Any, Callable, Optional

from pyinfra.context import host
from pyinfra.facts.server import Command
from pyinfra.operations import files, server

from deploy.utils.utils import dget, remote_path

BASE_DIR = Path(__file__).resolve().parents[2]
STACKS_DIR = BASE_DIR / "stacks"
TEMPLATES_DIR = BASE_DIR / "templates"


class StackName(str, Enum):
    AUTHELIA = "authelia"
    COPYPARTY = "copyparty"
    DDCLIENT = "ddclient"
    DIUN = "diun"
    GATUS = "gatus"
    HOMEPAGE = "homepage"
    NETSHOOT = "netshoot"
    NEXTCLOUD = "nextcloud"
    NGINX = "nginx"
    NTFY = "ntfy"
    NUT = "nut"
    PAPERLESS = "paperless"
    PEANUT = "peanut"
    PEANUT_MONITOR = "peanut-monitor"
    PIHOLE = "pihole"
    REDBOT = "redbot"
    STIRLING_PDF = "stirling-pdf"
    TRAEFIK = "traefik"
    UNIFI_VOUCHER_MANAGER = "unifi-voucher-manager"
    VAULTWARDEN = "vaultwarden"


@dataclass
class Stack:
    stack: StackName
    enabled: bool = True
    env: dict[str, str] = field(default_factory=dict)
    pre_deploy: Optional[Callable[["Stack"], None]] = None
    kwargs: dict[str, Any] = field(default_factory=dict)

    @property
    def name(self) -> str:
        return self.stack.value

    def deploy(self):
        # Directories
        local_stack_dir = STACKS_DIR / self.name
        remote_stack_dir = remote_path(self.name)

        # Environment
        shared_env = dget("env", {}) or {}
        sudo_docker = dget("docker_use_sudo", True)

        # -------------------------
        # Ensure directory
        # -------------------------
        files.directory(
            name=f"[{self.name}] create stack dir",
            path=str(remote_stack_dir),
            mode="755",
            _sudo=True,
            user=dget("docker_user"),
            group=dget("docker_group"),
        )

        # -------------------------
        # Deploy compose.yaml
        # -------------------------
        files.put(
            name=f"[{self.name}] deploy compose",
            src=str(local_stack_dir / "compose.yaml"),
            dest=str(remote_stack_dir / "compose.yaml"),
            mode="644",
            _sudo=True,
            user=dget("docker_user"),
            group=dget("docker_group"),
        )

        # -------------------------
        # Deploy stack.env
        # -------------------------
        files.template(
            name=f"[{self.name}] deploy stack.env",
            src=str(TEMPLATES_DIR / "env.stack.j2"),
            dest=str(remote_stack_dir / "stack.env"),
            mode="600",
            _sudo=True,
            user=dget("docker_user"),
            group=dget("docker_group"),
            shared_env=shared_env,
            stack_env=self.env,
        )

        # -------------------------
        # Pre-deploy hook
        # -------------------------
        if self.pre_deploy:
            self.pre_deploy(self)

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
                    docker compose --env-file stack.env up -d --remove-orphans
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
