from deploy.utils.stacks import StackBase
from deploy.utils.types import Directory, FileCopy

GATUS = StackBase(
    "gatus",
    directories=[
        Directory("config"),
    ],
    static_files=[
        FileCopy("config/config.yaml", "config/config.yaml"),
    ],
)
