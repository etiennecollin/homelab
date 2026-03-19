from typing import cast

from deploy.utils.stacks import Stack, dget

# Deploy all stacks assigned to this host
stacks = cast(list[Stack], dget("stacks", []))
for stack in stacks:
    if not stack.enabled:
        continue
    stack.deploy()
