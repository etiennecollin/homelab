from deploy.servers_def import *
from deploy.stacks_def import *

servers = [
    truenas.deploy([authelia]),
    raspberrypi.deploy([pihole]),
    localhost.deploy([nginx]),
]
