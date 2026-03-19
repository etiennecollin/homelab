# Homelab

A collection of docker compose templates

## Get Started

Rename the following files:

- `deploy/servers_def.template.py -> deploy/servers_def.template.py`
- `deploy/stacks_def.template.py -> deploy/stacks_def.template.py`

Fill-in and modify these two files as needed.

## Commands

In the following commands, use the `--limit` flag to target a specific server. Pass the server's hostname to the `--limit` flag.
For example, `--limit server.local.example.tld`. To target localhost, use `--limit "@local"`.

### Deploy

Deploy/start the compose stacks.

```shell
uv run pyinfra deploy/inventory.py deploy/operations/deploy.py
```

### Teardown

Teardown/stop the compose stacks.

```shell
uv run pyinfra deploy/inventory.py deploy/operations/teardown.py
```

### Prune

Prune unused and dangling docker images.

```shell
uv run pyinfra deploy/inventory.py deploy/operations/prune.py
```
