from config.common import DOMAIN, DOMAIN_TLD
from deploy.utils.servers import Server

COMMON = {
    "DOMAIN": DOMAIN,
    "PUBLIC_EMAIL": f"contact@{DOMAIN_TLD}",
    "CITY": "Montreal",
    "TIMEZONE": "America/Toronto",
    "PGID": "1000",
    "PUID": "1000",
    "MAIN_DNS": "10.0.2.53",
    "NETWORK_AUTH": "172.21.21.0/24",
    "NETWORK_PROXY": "172.20.20.0/24",
}

truenas = Server(
    name="truenas",
    hostname=f"nas.{DOMAIN}",
    ssh_user="truenas_admin",
    docker_user="truenas_admin",
    docker_group="truenas_admin",
    compose_stacks_path="/mnt/flash/data/services",
    env=COMMON,
    temp_dir="/run/user/950",
)


raspberrypi = Server(
    name="raspberrypi",
    hostname=f"pi.{DOMAIN}",
    ssh_user="pi",
    docker_user="pi",
    docker_group="pi",
    compose_stacks_path="~/homelab",
    env=COMMON,
)

localhost = Server(
    name="localhost",
    hostname="@local",
    ssh_user="etiennecollin",
    docker_user="etiennecollin",
    docker_group="staff",
    docker_use_sudo=False,
    compose_stacks_path="~/Downloads/docker",
    env=COMMON,
)
