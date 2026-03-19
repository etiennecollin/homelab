from pyinfra.operations import server

from deploy.utils.stacks import Stack, StackName


def test(name):
    server.shell(
        name=f"[{name}] say hello",
        commands=["echo 'hello world'"],
    )


nginx = Stack(
    stack=StackName.NGINX,
    pre_deploy=test,
    env={
        "AUTHELIA_LOG_LEVEL": "info",
    },
)
