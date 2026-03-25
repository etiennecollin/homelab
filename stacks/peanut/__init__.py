from pathlib import Path

from deploy.utils.stacks import StackBase
from deploy.utils.types import Directory, FileCopy

STACK_NAME = Path(__file__).parent.name
PEANUT = StackBase(
    STACK_NAME,
    directories=[
        Directory("config"),
    ],
    template_files=[
        FileCopy("templates/settings.yml.j2", "config/settings.yml"),
    ],
)
