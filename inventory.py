from pyinfra.context import config

from hosts import *
from stacks import *

config.TEMP_DIR = "/run/user/950"

hosts = [
    raspberrypi.deploy([pihole, nut]),
    truenas.deploy(
        [
            traefik,
            authelia,
            ntfy,
            peanut,
            homepage,
            # vaultwarden,
            # paperless,
            copyparty,
            unifi_voucher_manager,
            gatus,
            diun,
        ]
    ),
    localhost.deploy([], True),
]

single = [
    truenas.deploy([gatus, homepage]),
]

pi = [
    raspberrypi.deploy([pihole, nut]),
]
