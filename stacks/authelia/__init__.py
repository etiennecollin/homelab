from io import StringIO

from pyinfra.operations import files

from deploy.utils.stacks import Stack, StackBase
from deploy.utils.utils import Directory, FileCopy, get_random_key, remote_path


def post_deploy(self: Stack):
    remote_stack_dir = remote_path(self.name)

    files.file(
        name=f"[{self.name}] remove config/authelia/db.sqlite3",
        present=False,
        path=str(remote_stack_dir / "config/authelia/db.sqlite3"),
        _sudo=True,
    )


AUTHELIA = StackBase(
    "authelia",
    directories=[
        Directory("config"),
        Directory("config/authelia"),
        Directory("config/secrets"),
    ],
    static_files=[
        FileCopy("config/authelia/configuration.yml", "config/authelia/configuration.yml"),
        FileCopy(StringIO(get_random_key(128)), "config/secrets/jwt"),
        FileCopy(StringIO(get_random_key(128)), "config/secrets/session_secret"),
        FileCopy(StringIO(get_random_key(128)), "config/secrets/storage_encryption_key"),
    ],
    template_files=[
        FileCopy("templates/users_database.yml.j2", "config/authelia/users_database.yml"),
    ],
    post_deploy=post_deploy,
)
