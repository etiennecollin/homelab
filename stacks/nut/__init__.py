from pathlib import Path

from deploy.utils.stacks import StackBase
from deploy.utils.types import Directory, FileCopy

STACK_NAME = Path(__file__).parent.name
NUT = StackBase(
    STACK_NAME,
    directories=[
        Directory("config"),
    ],
    static_files=[
        FileCopy("udev.sh", "udev.sh", "755"),
    ],
    template_files=[
        FileCopy("templates/ups.conf.j2", "config/ups.conf"),
    ],
)
