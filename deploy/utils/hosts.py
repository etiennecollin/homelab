from dataclasses import dataclass, field
from typing import Any

from pyinfra.context import config

from .stacks import Stack


@dataclass
class Host:
    """
    Definition of a deployment target.

    This class represents a single host in the infrastructure and encapsulates
    all connection details, runtime configuration, and environment variables
    required for stack deployment via pyinfra.

    Responsibilities:
    - Define SSH connection parameters
    - Define Docker execution context (user/group/sudo)
    - Provide shared environment variables for all stacks on this host
    - Materialize pyinfra-compatible host data
    """

    name: str
    """
    Name of the host. Used for identification and grouping.
    """

    hostname: str
    """
    SSH target used by pyinfra. Can be an IP address, FQDN, or special
    value like "@local".
    """

    ssh_user: str
    """
    User used for SSH connections.
    """

    compose_stacks_path: str
    """
    Root directory on the remote host where all stacks will be deployed.
    """

    docker_user: str
    """
    User that owns deployed files and runs Docker commands.
    """

    docker_group: str
    """
    Group that owns deployed files.
    """

    docker_use_sudo: bool = field(default=True)
    """
    Whether Docker commands should be executed with sudo.
    """

    env: dict[str, str] = field(default_factory=dict)
    """
    Shared environment variables applied to all stacks on this host.
    These are merged with stack-specific variables during deployment.
    """

    temp_dir: str = field(default=config.DEFAULT_TEMP_DIR)
    """
    Temporary directory used by pyinfra for file transfers.
    """

    kwargs: dict[str, Any] = field(default_factory=dict)
    """
    Additional arbitrary pyinfra host data. This allows extending the
    host definition without modifying the core schema.
    """

    def deploy(self, stacks: list[Stack], dry: bool = False) -> tuple[str, dict]:
        """
        Convert this host definition into pyinfra inventory data.

        Args:
        - stacks:
            - List of `Stack` instances to deploy on this host.
        - dry:
            - If True, enables dry-run mode where stacks are deployed, but docker
            images are not pulled and containers are not started.

        Returns:
        - A`(hostname, host_data)` tuple compatible with pyinfra inventory definitions.
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
