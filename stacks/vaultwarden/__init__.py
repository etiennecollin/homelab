from pyinfra import logger
from pyinfra.context import host
from pyinfra.operations import docker, server

from deploy.utils.stacks import Stack, StackBase
from deploy.utils.utils import Directory, FileCopy, dget, remote_path


def post_deploy(self: Stack):
    sudo_docker = dget("docker_use_sudo", True)

    docker.volume(
        name=f"[{self.name}] create backup volume",
        volume="vaultwarden-rclone-data",
        _sudo=sudo_docker,
    )

    logger.warning(f"[{host.name}] [{self.name}] refer to README.md to restore a backup")
    logger.warning(f"[{host.name}] [{self.name}] refer to README.md to initialize the rclone backup target")


VAULTWARDEN = StackBase(
    "vaultwarden",
    static_files=[
        FileCopy("README.md", "README.md"),
    ],
    post_deploy=post_deploy,
)
