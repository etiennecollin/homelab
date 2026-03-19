from deploy.utils.servers import Server

COMMON = {
    "DOMAIN": "local.example.tld",
    "PUBLIC_EMAIL": "public.email@address",
    "CITY": "Montreal",
    "TIMEZONE": "America/Toronto",
    "PGID": "1000",
    "PUID": "1000",
    "MAIN_DNS": "8.8.8.8",
    "NETWORK_AUTH": "172.21.21.0/24",
    "NETWORK_PROXY": "172.20.20.0/24",
    "NETWORK_MAIN": "10.0.0.0/16",
}

localhost = Server(
    name="localhost",
    hostname="@local",
    ssh_user="etiennecollin",
    ssh_user_requires_sudo_for_docker=False,
    docker_user="etiennecollin",
    docker_group="staff",
    compose_stacks_path="~/Downloads/docker",
    env=COMMON,
)
