from pyinfra.operations import docker

from deploy.utils.utils import dget

sudo_docker = dget("docker_use_sudo", True)

docker.prune(
    name="Remove unused and dangling images",
    all=True,
    _sudo=sudo_docker,
)
