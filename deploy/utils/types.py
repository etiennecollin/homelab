from dataclasses import dataclass, field
from pathlib import Path
from typing import IO, Any, Optional, Union

from argon2 import PasswordHasher


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
