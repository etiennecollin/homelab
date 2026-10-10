from pathlib import Path

from deploy.utils.stacks import StackBase
from deploy.utils.types import Directory, FileCopy

STACK_NAME = Path(__file__).parent.name
TRAEFIK = StackBase(
    STACK_NAME,
    directories=[
        Directory("config"),
    ],
    template_files=[
        FileCopy("templates/traefik.yaml.j2", "config/traefik.yaml"),
    ],
    static_files=[
        FileCopy("config/routing.yaml", "config/routing.yaml"),
        FileCopy(None, "config/acme.json", "600"),
    ],
)
