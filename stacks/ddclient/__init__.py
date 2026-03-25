from deploy.utils.stacks import StackBase
from deploy.utils.types import Directory, FileCopy

DDCLIENT = StackBase(
    "ddclient",
    directories=[
        Directory("config"),
    ],
    static_files=[
        FileCopy("config/ddclient.conf", "config/ddclient.conf"),
    ],
)
