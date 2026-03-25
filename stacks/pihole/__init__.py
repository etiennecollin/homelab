from deploy.utils.stacks import StackBase
from deploy.utils.types import Directory, FileCopy

PIHOLE = StackBase(
    "pihole",
    directories=[
        Directory("config"),
    ],
    static_files=[
        FileCopy("config/adlists.list", "config/adlists.list"),
    ],
)
