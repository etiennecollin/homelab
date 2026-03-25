from __future__ import annotations

import secrets
import string
import subprocess
import sys
import types
from functools import lru_cache
from pathlib import Path
from typing import Any, Optional, TypeVar, Union, overload

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


@lru_cache(maxsize=1)
def load_encrypted_module(path: Union[str, Path], key_file: Union[str, Path], module_name: str) -> types.ModuleType:
    """
    Decrypt an age-encrypted Python file and load it as a module.
    """
    path = str(path)
    key_file = str(key_file)

    # Decrypt
    try:
        proc = subprocess.run(
            ["age", "-d", "-i", key_file, path],
            check=True,
            capture_output=True,
        )
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Failed to decrypt {path} with key {key_file}:\n{e.stderr.decode()}") from e

    code = proc.stdout.decode("utf-8")

    # Register module
    module = types.ModuleType(module_name)
    module.__file__ = path
    sys.modules[module_name] = module

    # Execute module
    exec(code, module.__dict__)
    return module
