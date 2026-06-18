from pyinfra.context import config

from hosts import *
from stacks import *

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
            actual_budget,
        ]
    ),
]

update = [
    truenas.deploy([actual_budget, traefik]),
    raspberrypi.deploy([pihole]),
]
