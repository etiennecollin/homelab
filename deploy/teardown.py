from typing import cast

from deploy.utils.stacks import Stack
from deploy.utils.utils import dget

# Deploy all stacks assigned to this host
stacks = cast(list[Stack], dget("stacks", []))
for stack in reversed(stacks):
    if not stack.enabled:
        continue
    stack.teardown()
