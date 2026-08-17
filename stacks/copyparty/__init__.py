from pathlib import Path

from deploy.utils.stacks import StackBase
from deploy.utils.types import Directory, FileCopy
from hosts import COMMON

STACK_NAME = Path(__file__).parent.name
COPYPARTY = StackBase(
    STACK_NAME,
    directories=[
        Directory("config", user=COMMON["PUID"], group=COMMON["PGID"]),
    ],
    template_files=[
        FileCopy("templates/copyparty.conf.j2", "config/copyparty.conf", user=COMMON["PUID"], group=COMMON["PGID"]),
    ],
)
