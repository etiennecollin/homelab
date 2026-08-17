from pathlib import Path

from deploy.utils.stacks import StackBase
from deploy.utils.types import Directory, FileCopy

STACK_NAME = Path(__file__).parent.name
IMMICH = StackBase(
    STACK_NAME,
    directories=[
        Directory("library"),
        Directory("postgres"),
    ],
)
