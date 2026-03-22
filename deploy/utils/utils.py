from __future__ import annotations

import secrets
import string
import subprocess
import sys
import types
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path
from typing import IO, Any, Optional, TypeVar, Union, overload

from argon2 import PasswordHasher
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
    compose_stacks_path = dget("compose_stacks_path")
    assert compose_stacks_path is not None, "compose_stacks_path must be specified"

    if compose_stacks_path.startswith("~"):
        home = host.get_fact(Home, user=dget("docker_user"))
        assert home is not None, "Could not get path to home directory using Home fact"
        compose_stacks_path = compose_stacks_path.replace("~", home, 1)

    return Path(compose_stacks_path, *parts)


def get_random_key(length: int) -> str:
    alphabet = string.ascii_letters + string.digits + "`~!@#$%^&*()-_=+,<.>/?;:[{}]"
    return "".join(secrets.choice(alphabet) for _ in range(length))


@dataclass
class AutheliaUser:
    username: str
    displayname: str
    password: str  # plaintext input
    groups: list[str] = field(default_factory=list)
    disabled: bool = False

    def hashed(self) -> dict:
        ph = PasswordHasher()
        ph.verify
        hashed = ph.hash(self.password)

        return {
            "username": self.username,
            "displayname": self.displayname,
            "password": hashed,
            "groups": self.groups,
            "disabled": self.disabled,
        }


@dataclass()
class PiHoleAddressMap:
    source: str
    target: str

    @classmethod
    def to_env(cls, maps: list["PiHoleAddressMap"], src_dst_sep: str):
        return ";".join([f"{map.source}{src_dst_sep}{map.target}" for map in maps])


@lru_cache(maxsize=1)
def load_encrypted_module(path: str, key_file: str, module_name: str) -> types.ModuleType:
    """
    Decrypt an age-encrypted Python file and load it as a module.
    """
    cmd = ["age", "-d", "-i", key_file, path]
    proc = subprocess.run(cmd, capture_output=True, check=True)
    code = proc.stdout.decode("utf-8")

    module = types.ModuleType(module_name)
    module.__file__ = path
    sys.modules[module_name] = module

    exec(code, module.__dict__)
    return module
