from pathlib import Path

from pyinfra import logger
from pyinfra.context import host
from pyinfra.operations import docker

from deploy.utils.stacks import Stack, StackBase
from deploy.utils.types import FileCopy
from deploy.utils.utils import dget


def post_deploy(self: Stack):
    sudo_docker = dget("docker_use_sudo", True)

    docker.volume(
        name=f"[{self.name}] create backup volume",
        volume="vaultwarden-rclone-data",
        _sudo=sudo_docker,
    )

    logger.warning(f"[{host.name}] [{self.name}] refer to README.md to restore a backup")
    logger.warning(f"[{host.name}] [{self.name}] refer to README.md to initialize the rclone backup target")


STACK_NAME = Path(__file__).parent.name
VAULTWARDEN = StackBase(
    STACK_NAME,
    static_files=[
        FileCopy("README.md", "README.md"),
    ],
    post_deploy=post_deploy,
)
