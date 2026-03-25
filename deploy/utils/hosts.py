from dataclasses import dataclass, field
from typing import Any

from pyinfra.context import config

from .stacks import Stack


@dataclass
class Host:
    name: str
    hostname: str
    ssh_user: str
    compose_stacks_path: str
    docker_user: str
    docker_group: str
    docker_use_sudo: bool = field(default=True)
    env: dict[str, str] = field(default_factory=dict)
    temp_dir: str = field(default=config.DEFAULT_TEMP_DIR)
    kwargs: dict[str, Any] = field(default_factory=dict)

    def deploy(self, stacks: list[Stack], dry: bool = False) -> tuple[str, dict]:
        """
        Convert this server definition into pyinfra host.data.
        """
        return (
            self.hostname,
            {
                "name": self.name,
                "ssh_hostname": self.hostname,
                "ssh_user": self.ssh_user,
                "docker_user": self.docker_user,
                "docker_group": self.docker_group,
                "docker_use_sudo": self.docker_use_sudo,
                "compose_stacks_path": self.compose_stacks_path,
                "dry_run": dry,
                "stacks": stacks,
                "env": self.env,
                "_temp_dir": self.temp_dir,
                **self.kwargs,
            },
        )
