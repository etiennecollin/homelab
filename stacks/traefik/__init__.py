from deploy.utils.stacks import StackBase
from deploy.utils.utils import Directory, FileCopy

TRAEFIK = StackBase(
    "traefik",
    directories=[
        Directory("config"),
    ],
    static_files=[
        FileCopy("config/config.yaml", "config/config.yaml"),
        FileCopy("config/traefik.env", "config/traefik.env"),
        FileCopy(None, "config/acme.json", "600"),
    ],
)
