from pathlib import Path
from typing import Any, Optional, TypeVar, overload

from pyinfra.context import host
from pyinfra.facts.server import Home

T = TypeVar("T")


@overload
def dget(key: str) -> Optional[Any]: ...


@overload
def dget(key: str, default: T) -> T: ...


def dget(key: str, default=None) -> Optional[Any]:
    return host.data.get(key, default)


def remote_path(*parts) -> Path:
    compose_stacks_path = dget("compose_stacks_path", "/srv/homelab")

    if compose_stacks_path.startswith("~"):
        home = host.get_fact(Home, user=dget("docker_user"))
        assert home is not None, "Could not get path to home directory using Home fact"
        compose_stacks_path = compose_stacks_path.replace("~", home, 1)

    return Path(compose_stacks_path, *parts)
