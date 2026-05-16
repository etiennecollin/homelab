from dataclasses import dataclass, field
from pathlib import Path
from typing import IO, Any, Optional, Union

from argon2 import PasswordHasher


@dataclass
class Directory:
    """
    Representation of a directory to be created on the remote host.

    This class is used within `StackBase` to declare required directory
    structure prior to file deployment.
    """

    path: Path
    """
    Path relative to the stack root directory.
    """

    mode: Optional[str]
    """
    Directory permissions (example: "755").
    """

    user: Optional[str]
    """
    User to own the directory.
    """

    group: Optional[str]
    """
    Group to own the directory.
    """

    def __init__(
        self,
        path: Union[str, Path],
        mode: Optional[str] = None,
        user: Optional[str] = None,
        group: Optional[str] = None,
    ):

        # Normalize to Path objects if strings
        self.path = path if isinstance(path, Path) else Path(path)
        self.mode = mode
        self.user = user
        self.group = group

    def resolve_path(self, stack_dir: Path) -> Path:
        """
        Resolve the directory path relative to the stack root.

        Args:
        - stack_dir:
            - Root directory of the stack on the remote host.

        Returns:
            Absolute path where the directory should be created.
        """
        return stack_dir / self.path


@dataclass
class FileCopy:
    """
    Representation of a file deployment operation.

    This class is used for both static file copying and template rendering
    within a stack.

    Behavior:
    - If `src` is provided:
        - The file is copied from the local stack directory to the remote host.
    - If `src` is None:
        - An empty file is created at the destination.

    Notes:
    - Directory creation is NOT handled here and must be declared separately.
    """

    src: Optional[Union[Path, IO[Any]]]
    """
    Source of the file. Can be:
    - Path (relative to stack directory)
    - IO object (e.g., StringIO)
    - None (creates empty file)
    """

    dest: Path
    """
    Destination path relative to the stack root directory.
    """

    mode: Optional[str]
    """
    File permissions (example: "644" or "600").
    """

    user: Optional[str]
    """
    User to own the directory.
    """

    group: Optional[str]
    """
    Group to own the directory.
    """

    def __init__(
        self,
        src: Optional[Union[str, Path, IO[Any]]],
        dest: Union[str, Path],
        mode: Optional[str] = None,
        user: Optional[str] = None,
        group: Optional[str] = None,
    ):

        # Normalize to Path objects if strings
        if isinstance(src, str):
            src = Path(src)
        if isinstance(dest, str):
            dest = Path(dest)

        self.src = src
        self.dest = dest
        self.mode = mode
        self.user = user
        self.group = group

    def resolve_src(self, stack_dir: Path) -> Path:
        """
        Resolve the source path relative to the stack directory.

        Args:
        - stack_dir:
            - Local stack directory.

        Returns:
        - Absolute path to the source file.

        Raises:
        - AssertionError:
            - If the source is not a Path.
        """
        assert isinstance(self.src, Path), "Source directory must be a Path to be resolved"
        return stack_dir / self.src

    def resolve_dest(self, stack_dir: Path) -> Path:
        """
        Resolve the destination path relative to the stack root.

        Args:
        - stack_dir:
            - Remote stack root directory.

        Returns:
        - Absolute destination path.
        """
        return stack_dir / self.dest


@dataclass
class AutheliaUser:
    username: str
    displayname: str
    password: str  # plaintext input
    groups: list[str] = field(default_factory=list)
    disabled: bool = False

    def hashed(self) -> dict:
        ph = PasswordHasher()
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
