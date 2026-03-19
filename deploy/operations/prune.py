from pyinfra.operations import docker

from deploy.utils.utils import dget

ssh_user_requires_sudo_for_docker = dget("ssh_user_requires_sudo_for_docker", True)

docker.prune(
    name="Remove unused and dangling images",
    all=True,
    _sudo=ssh_user_requires_sudo_for_docker,
)
