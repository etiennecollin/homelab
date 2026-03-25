from pathlib import Path

from deploy.utils.stacks import StackBase
from deploy.utils.types import Directory, FileCopy

STACK_NAME = Path(__file__).parent.name
DDCLIENT = StackBase(
    STACK_NAME,
    directories=[
        Directory("config"),
    ],
    static_files=[
        FileCopy("config/ddclient.conf", "config/ddclient.conf"),
    ],
)
