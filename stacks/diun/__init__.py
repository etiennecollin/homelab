from pathlib import Path

from deploy.utils.stacks import StackBase

STACK_NAME = Path(__file__).parent.name
DIUN = StackBase(
    STACK_NAME,
)
