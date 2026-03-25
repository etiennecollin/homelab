from pathlib import Path

from deploy.utils.stacks import StackBase
from deploy.utils.types import Directory, FileCopy

STACK_NAME = Path(__file__).parent.name
COPYPARTY = StackBase(
    STACK_NAME,
    directories=[
        Directory("config"),
    ],
    static_files=[
        FileCopy("config/copyparty.conf", "config/copyparty.conf"),
    ],
)
