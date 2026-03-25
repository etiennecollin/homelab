from pathlib import Path
from shlex import quote
from textwrap import dedent

from pyinfra.operations import server

from deploy.utils.stacks import Stack, StackBase
from deploy.utils.utils import dget, remote_path


def post_deploy(self: Stack):
    remote_stack_dir = remote_path(self.name)

    compose_stacks_path = dget("compose_stacks_path")
    assert compose_stacks_path is not None, "compose_stacks_path must be specified"

    server.shell(
        name=f"[{self.name}] set STACKS_PATH variable based on host",
        commands=[dedent(f"""
        cd {quote(str(remote_stack_dir))} && \\
        sed -i 's|^STACKS_PATH=".*"|STACKS_PATH="{compose_stacks_path}"|' stack.env
    """).strip()],
        _sudo=True,
    )


STACK_NAME = Path(__file__).parent.name
DOCKGE = StackBase(
    STACK_NAME,
    post_deploy=post_deploy,
)
