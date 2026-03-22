from config import *
from config.servers import localhost, raspberrypi, truenas

# from pyinfra.context import config,
# config.TEMP_DIR = "/run/user/950"

servers = [
    # truenas.deploy([nginx]),
    raspberrypi.deploy([pihole]),
    localhost.deploy([traefik, authelia]),
]
