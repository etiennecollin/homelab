from pathlib import Path

from pyinfra import logger
from pyinfra.context import host

from deploy.utils.stacks import Stack, StackBase
from deploy.utils.types import FileCopy


def post_deploy(self: Stack):
    logger.warning(f"[{host.name}] [{self.name}] refer to README.md to restore a backup")


STACK_NAME = Path(__file__).parent.name
PAPERLESS = StackBase(
    STACK_NAME,
    static_files=[
        FileCopy("upgrade_postgres.sh", "upgrade_postgres.sh", "755"),
    ],
    post_deploy=post_deploy,
)
