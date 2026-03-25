from pathlib import Path

from deploy.utils.stacks import StackBase

STACK_NAME = Path(__file__).parent.name
UNIFI_VOUCHER_MANAGER = StackBase(
    STACK_NAME,
)
