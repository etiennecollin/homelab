from deploy.utils.stacks import StackBase
from deploy.utils.types import Directory, FileCopy

NUT = StackBase(
    "nut",
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
