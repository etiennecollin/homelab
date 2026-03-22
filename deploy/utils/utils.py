import secrets
import string
from dataclasses import dataclass
from pathlib import Path
from typing import IO, Any, Optional, TypeVar, Union, overload

from pyinfra.context import host
from pyinfra.facts.server import Home


@dataclass
class FileCopy:
    src: Optional[Union[Path, IO[Any]]]
    dest: Path
    mode: str

    def __init__(
        self,
        src: Optional[Union[str, Path, IO[Any]]],
        dest: Union[str, Path],
        mode: Optional[str] = None,
    ):

        # Normalize to Path objects if strings
        if isinstance(src, str):
            src = Path(src)
        if isinstance(dest, str):
            dest = Path(dest)

        self.src = src
        self.dest = dest

        # Sane default: config files are usually readable, not executable
        self.mode = mode or "644"

    def resolve_src(self, stack_dir: Path) -> Path:
        assert isinstance(self.src, Path), "Source directory must be a Path to be resolved"
        return stack_dir / self.src

    def resolve_dest(self, stack_dir: Path) -> Path:
        return stack_dir / self.dest


@dataclass
class Directory:
    path: Path
    mode: str

    def __init__(
        self,
        path: Union[str, Path],
        mode: Optional[str] = None,
    ):

        # Normalize to Path objects if strings
        self.path = path if isinstance(path, Path) else Path(path)

        # Sane default: config files are usually readable, not executable
        self.mode = mode or "755"

    def resolve_path(self, stack_dir: Path) -> Path:
        return stack_dir / self.path


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


def get_key(length: int) -> str:
    alphabet = string.ascii_letters + string.digits + "`~!@#$%^&*()-_=+,<.>/?;:[{}]"
    return "".join(secrets.choice(alphabet) for _ in range(length))
