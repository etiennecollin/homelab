from pathlib import Path

from deploy.utils.stacks import StackBase
from deploy.utils.types import Directory, FileCopy

STACK_NAME = Path(__file__).parent.name
TRAEFIK = StackBase(
    STACK_NAME,
    directories=[
        Directory("config"),
    ],
    static_files=[
        FileCopy("config/config.yaml", "config/config.yaml"),
        FileCopy("config/traefik.env", "config/traefik.env"),
        FileCopy(None, "config/acme.json", "600"),
    ],
)
