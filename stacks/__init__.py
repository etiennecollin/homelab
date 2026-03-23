from config.stacks import *
from deploy.utils.stacks import Stack

from .authelia import AUTHELIA
from .copyparty import COPYPARTY
from .ddclient import DDCLIENT
from .diun import DIUN
from .dockge import DOCKGE
from .gatus import GATUS
from .homepage import HOMEPAGE
from .nextcloud import NEXTCLOUD
from .ntfy import NTFY
from .nut import NUT
from .paperless import PAPERLESS
from .peanut import PEANUT
from .peanut_monitor import PEANUT_MONITOR
from .pihole import PIHOLE
from .redbot import REDBOT
from .stirling_pdf import STIRLING_PDF
from .traefik import TRAEFIK
from .unifi_voucher_manager import UNIFI_VOUCHER_MANAGER
from .vaultwarden import VAULTWARDEN

authelia = Stack(AUTHELIA, authelia_config)
copyparty = Stack(COPYPARTY)
ddclient = Stack(DDCLIENT)
diun = Stack(DIUN, diun_config)
dockge = Stack(DOCKGE, dockge_config)
gatus = Stack(GATUS, gatus_config)
homepage = Stack(HOMEPAGE)
nextcloud = Stack(NEXTCLOUD, nextcloud_config)
ntfy = Stack(NTFY)
nut = Stack(NUT, nut_config)
paperless = Stack(PAPERLESS, paperless_config)
peanut = Stack(PEANUT, peanut_config)
peanut_monitor = Stack(PEANUT_MONITOR, peanut_monitor_config)
pihole = Stack(PIHOLE, pihole_config)
redbot = Stack(REDBOT, redbot_config)
stirling_pdf = Stack(STIRLING_PDF)
traefik = Stack(TRAEFIK, traefik_config)
unifi_voucher_manager = Stack(UNIFI_VOUCHER_MANAGER, unifi_voucher_manager_config)
vaultwarden = Stack(VAULTWARDEN, vaultwarden_config)
