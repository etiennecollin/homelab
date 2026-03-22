from deploy.utils.stacks import StackBase
from deploy.utils.utils import Directory, FileCopy

PEANUT = StackBase(
    "peanut",
    directories=[
        Directory("config"),
    ],
    template_files=[
        FileCopy("templates/settings.yml.j2", "config/settings.yml"),
    ],
)
