from deploy.utils.stacks import StackBase
from deploy.utils.utils import Directory, FileCopy

COPYPARTY = StackBase(
    "copyparty",
    directories=[
        Directory("config"),
    ],
    static_files=[
        FileCopy("config/copyparty.conf", "config/copyparty.conf"),
    ],
)
