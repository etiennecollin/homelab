import inspect
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE_DIR))

import stacks
from deploy.utils.stacks import StackBase

OUTPUT = BASE_DIR / "config/stacks.pyi"


def is_stack(name: str, value) -> bool:
    """
    Detect stack constants like AUTHELIA, PIHOLE, etc.
    """
    return name.isupper() and isinstance(value, StackBase)


def main():
    lines = [
        "from deploy.utils.stacks import StackConfig",
        "",
        "",
        "class ConfigModule(Protocol):",
    ]

    members = inspect.getmembers(stacks)
    stack_members = [n for n, v in members if is_stack(n, v)]
    names = [f"{name.lower()}_config" for name in stack_members]

    lines = [
        "from deploy.utils.stacks import StackConfig",
        "",
        "__all__ = [",
    ]

    for n in sorted(names):
        lines.append(f'    "{n}",')

    lines.append("]\n")

    for n in sorted(names):
        lines.append(f"{n}: StackConfig")

    lines.append("")

    OUTPUT.write_text("\n".join(lines))
    print(f"Generated {OUTPUT}")


if __name__ == "__main__":
    main()
