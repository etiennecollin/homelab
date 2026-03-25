from pathlib import Path

from pyinfra.operations import files

from deploy.utils.stacks import Stack, StackBase
from deploy.utils.types import Directory
from deploy.utils.utils import dget, remote_path


def post_deploy(self: Stack):
    remote_stack_dir = remote_path(self.name)

    files.download(
        name=f"[{self.name}] download english tesseract traineddata",
        src="https://raw.githubusercontent.com/tesseract-ocr/tessdata/ced78752cc61322fb554c280d13360b35b8684e4/eng.traineddata",
        dest=str(remote_stack_dir / "config/tessdata/eng.traineddata"),
        mode="644",
        user=dget("docker_user"),
        group=dget("docker_group"),
        _sudo=True,
    )

    files.download(
        name=f"[{self.name}] download french tesseract traineddata",
        src="https://raw.githubusercontent.com/tesseract-ocr/tessdata/ced78752cc61322fb554c280d13360b35b8684e4/fra.traineddata",
        dest=str(remote_stack_dir / "config/tessdata/fra.traineddata"),
        mode="644",
        user=dget("docker_user"),
        group=dget("docker_group"),
        _sudo=True,
    )


STACK_NAME = Path(__file__).parent.name
STIRLING_PDF = StackBase(
    STACK_NAME,
    directories=[
        Directory("config"),
        Directory("config/tessdata"),
    ],
    post_deploy=post_deploy,
)
