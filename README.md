# Homelab

Infrastructure-as-code for a Docker-based homelab. The repository contains reusable stack definitions, encrypted per-host configuration, and pyinfra deployment entrypoints.

<!-- vim-markdown-toc GFM -->

- [Requirements](#requirements)
- [Repository Layout](#repository-layout)
- [Command Overview](#command-overview)
  - [Deploy](#deploy)
  - [Teardown](#teardown)
  - [Prune](#prune)
- [Editing Encrypted Configuration](#editing-encrypted-configuration)
- [Adding a New Stack](#adding-a-new-stack)
- [Adding a New Host](#adding-a-new-host)

<!-- vim-markdown-toc -->

## Requirements

- [uv](https://github.com/astral-sh/uv)
- [age](https://github.com/FiloSottile/age)

## Repository Layout

- `./config/`: Encrypted runtime configuration.
- `./deploy/`: pyinfra inventory, operations, and helper utilities.
- `./stacks/`: Stack definitions and stack-specific helpers.
- `./scripts/`: Utility scripts such as `age.sh`.

## Command Overview

Use pyinfra's `--limit` flag to target one host or a group of hosts.

By default, `--limit` should match the host name defined in `inventory.py`, not necessarily the SSH hostname. For localhost, use `--limit @local`. You can also limit to a group of hosts. See the [pyinfra documentation](https://github.com/pyinfra-dev/pyinfra) for details.

### Deploy

Deploy and start the configured compose stacks.

```sh
uv run pyinfra inventory.py deploy/deploy.py
```

### Teardown

Stop the configured compose stacks.

```sh
uv run pyinfra inventory.py deploy/teardown.py
```

### Prune

Remove unused and dangling Docker images.

```sh
uv run pyinfra inventory.py deploy/prune.py
```

## Editing Encrypted Configuration

The repository uses [age](https://github.com/FiloSottile/age) to encrypt Python configuration files. The encrypted files are the source of truth at runtime.

If you do not have your own `age` key, generate it with:

```sh
./scripts/age.sh gen
```

If you already have a key, place your private and public keys in:

```text
~/.age/key.txt
~/.age/key.pub
```

To decrypt the configuration files, run:

```sh
./scripts/age.sh dec config/common.py.age config/stacks.py.age
```

After editing `./config/common.py` and `./config/stacks.py`, re-encrypt them with:

```sh
./scripts/age.sh enc -d config/common.py config/stacks.py
```

The `-d` flag removes the plaintext file after encryption.

## Adding a New Stack

1. Create a new directory under `./stacks/`.
   - Use lowercase letters and underscores only.
   - Example: `./stacks/authelia/`.
2. Add a `./stacks/<stack_name>/__init__.py` file for the stack.
   - Define a `StackBase` object with the stack's name in uppercase as the variable name. The `name` field of the `StackBase` object should be the stack's name in lowercase.
   - Use existing stacks as a reference, such as `./stacks/authelia/__init__.py`.
   - If the stack needs files copied into directories, make sure the directories are created explicitly. This avoids incorrect permissions from implicit directory creation.
3. Add the stack's configuration to `./config/stacks.py`.
   - Define a `<stack_name>_config` variable containing a `StackConfig` object.
   - Set environment variables and template variables as needed.
   - Re-encrypt the file after editing.
4. Register the stack in `./stacks/__init__.py`.
   - Create the `Stack` object from the `StackBase` and `StackConfig`.
5. Add the stack to the relevant hosts in `./inventory.py`.
   - Use the `Host` object for the target machine.
   - Add the stack to that host's deployment list.

## Adding a New Host

1. Add a new `Host` object in `./hosts.py`.
2. Register that host in `./inventory.py`.
   - Add it to the inventory and assign the stacks it should run.
