from pathlib import Path

from deploy.utils.utils import load_encrypted_module

common = load_encrypted_module("config/common.py.age", f"{Path.home()}/.age/key.txt", "config.common")
stacks = load_encrypted_module("config/stacks.py.age", f"{Path.home()}/.age/key.txt", "config.stacks")
