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
    """
    Retrieve a value from `host.data` with optional default.

    This is a thin wrapper around `host.data.get` with improved typing support
    via overloads.

    Args:
    - key:
        - Key to retrieve from pyinfra's `host.data`.
    - default:
        - Optional default value returned if the key is not present.

    Returns:
    - If `default` is provided: returns the value or the default (type `T`)
    - If `default` is omitted: returns the value or `None`

    Notes:
    - Type inference works correctly when a default is provided.

    Example if `docker_user` is `root`:
    >>> dget("docker_user")
    "root" | None

    >>> dget("docker_user", "root")
    "root"
    """
    return host.data.get(key, default)


def remote_path(*parts) -> Path:
    """
    Resolve a path inside the remote stack root directory.

    This function expands the configured `compose_stacks_path` and joins it
    with additional path components.

    Features:
    - Supports `~` expansion using the remote user's home directory
    - Uses pyinfra facts to resolve remote paths correctly on the current host

    Args:
    - *parts:
        - Additional path components appended to the stack root.

    Returns:
        - A `Path` object representing the absolute path on the remote host.

    Raises:
    - AssertionError:
        - If `compose_stacks_path` is not defined in host data.
        - If home directory resolution fails when using `~`.

    Notes:
    - `~` expansion uses the `docker_user`, not the SSH user.
    - This function does NOT validate existence of the path.
    """
    compose_stacks_path = dget("compose_stacks_path")
    assert compose_stacks_path is not None, "compose_stacks_path must be specified"

    if compose_stacks_path.startswith("~"):
        home = host.get_fact(Home, user=dget("docker_user"))
        assert home is not None, "Could not get path to home directory using Home fact"
        compose_stacks_path = compose_stacks_path.replace("~", home, 1)

    return Path(compose_stacks_path, *parts)


def get_random_key(length: int, env_safe: bool = False) -> str:
    """
    Generate a cryptographically secure random string.

    This function produces a random string suitable for use as secrets such as:
    - API keys
    - passwords
    - encryption tokens

    Args:
    - length:
        - Length of the generated string.
    - env_safe:
        - If True, escapes the string so it can be safely used as a value in a
            `.env` file (wrapped in double quotes with proper escaping).


    Returns:
    - A random string. If `env_safe=True`, the string is quoted and escaped.

    Security:
    - Uses `secrets.choice`, which is suitable for cryptographic use.
    - Output is non-deterministic and should not be reused.

    Notes:
    - The character set includes symbols that may require escaping in some
        contexts (e.g., shell, YAML, or `.env` files).

    Example:
    >>> get_random_key(32)
    "aB3$kL9!..."
    """
    alphabet = string.ascii_letters + string.digits + "`~!@#$%^&*()-_=+,<.>/?;:[{}]"
    raw = "".join(secrets.choice(alphabet) for _ in range(length))
    if not env_safe:
        return raw

    # Escape for .env compatibility
    escaped = raw.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n")
    return escaped


@lru_cache(maxsize=1)
def load_encrypted_module(path: Union[str, Path], key_file: Union[str, Path], module_name: str) -> types.ModuleType:
    """
    Decrypt and load an age-encrypted Python module at runtime.

    This function integrates encrypted configuration files into the Python
    runtime without ever writing decrypted content to disk.

    Responsibilities:
    - Decrypt a `.age` file using the provided key
    - Dynamically create a Python module
    - Register it in `sys.modules`
    - Execute the decrypted code within that module

    Args:
    - path:
        - Path to the encrypted Python file (e.g., `config/stacks.py.age`).
    - key_file:
        - Path to the age private key used for decryption.
    - module_name:
        - Fully-qualified module name under which the module will be registered
            (e.g., `"config.stacks"`).

    Returns:
    - A loaded `ModuleType` instance containing the executed code.

    Raises:
    - RuntimeError:
        - If decryption fails.

    Important:
    - This function MUST be called before importing the module:
        load_encrypted_module(..., "config.stacks")
        from config.stacks import *

    Example:
    >>> load_encrypted_module("config/stacks.py.age", "~/.age/key.txt", "config.stacks")
    >>> from config.stacks import authelia_config
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
