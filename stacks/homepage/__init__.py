from deploy.utils.stacks import StackBase
from deploy.utils.types import Directory, FileCopy

HOMEPAGE = StackBase(
    "homepage",
    directories=[
        Directory("config"),
        Directory("config/images"),
        Directory("config/settings"),
    ],
    static_files=[
        FileCopy(
            "config/images/ancient_bristlecone_pine_forest.jpg", "config/images/ancient_bristlecone_pine_forest.jpg"
        ),
        FileCopy("config/images/favicon.ico", "config/images/favicon.ico"),
        FileCopy("config/settings/bookmarks.yaml", "config/settings/bookmarks.yaml"),
        FileCopy("config/settings/custom.css", "config/settings/custom.css"),
        FileCopy("config/settings/custom.js", "config/settings/custom.js"),
        FileCopy("config/settings/docker.yaml", "config/settings/docker.yaml"),
        FileCopy("config/settings/kubernetes.yaml", "config/settings/kubernetes.yaml"),
        FileCopy("config/settings/proxmox.yaml", "config/settings/proxmox.yaml"),
        FileCopy("config/settings/services.yaml", "config/settings/services.yaml"),
        FileCopy("config/settings/settings.yaml", "config/settings/settings.yaml"),
        FileCopy("config/settings/widgets.yaml", "config/settings/widgets.yaml"),
    ],
)
