from dataclasses import dataclass, field

from deploy.utils.stacks import Stack


@dataclass
class Server:
    name: str
    hostname: str
    ssh_user: str
    compose_stacks_path: str
    docker_user: str
    docker_group: str

    # Global env variables ONLY
    env: dict[str, str] = field(default_factory=dict)

    def deploy(self, stacks: list[Stack]) -> tuple[str, dict]:
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
                "compose_stacks_path": self.compose_stacks_path,
                # Stacks to deploy
                "stacks": stacks,
                # Global env
                "env": self.env,
            },
        )
