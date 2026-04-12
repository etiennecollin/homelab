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
            dockge,
            peanut,
            # peanut_monitor, # FIXME
            homepage,
            vaultwarden,
            # paperless, # missing
            # copyparty, # FIXME: Environment missing XDG_CONFIG
            unifi_voucher_manager,
            gatus,
            diun,
        ]
    ),
    localhost.deploy([], True),
]

single = [
    localhost.deploy([traefik], True),
]

update = [
    truenas.deploy([vaultwarden]),
]

pi = [
    raspberrypi.deploy([pihole, nut]),
]
