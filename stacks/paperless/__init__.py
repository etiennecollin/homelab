from pyinfra import logger
from pyinfra.context import host

from deploy.utils.stacks import Stack, StackBase
from deploy.utils.utils import Directory, FileCopy


def post_deploy(self: Stack):
    logger.warning(f"[{host.name}] [{self.name}] refer to README.md to restore a backup")


PAPERLESS = StackBase(
    "paperless",
    static_files=[
        FileCopy("upgrade_postgres.sh", "upgrade_postgres.sh", "755"),
    ],
    post_deploy=post_deploy,
)
