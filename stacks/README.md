# Docker

## Requirements

- docker
  - https://docs.docker.com/engine/install/
  - https://docs.docker.com/engine/install/linux-postinstall/

## Usage

When starting the containers with docker compose, use the following command to import the main `main.env` file.

```bash
docker compose --env-file ../secret.env up -d --force-recreate
```

## Useful bash aliases

Here are some aliases for docker compose:

```bash
alias dcu="docker compose --env-file ../secret.env up -d --force-recreate"
alias dcd="docker compose --env-file ../secret.env down --remove-orphans"
alias dcp="docker compose --env-file ../secret.env pull"
alias dcP="echo -n \"Are you sure you want to prune all containers, images, and networks? (y/n) \"; read -n 1 ans; echo \"\"; if [ \"\$ans\" = \"y\" ]; then f=0; echo \"Pruning containers...\"; docker container prune -f || f=1; echo \"Pruning images...\"; docker image prune -af || f=1; echo \"Pruning networks...\"; docker network prune -f || f=1; [ \$f -eq 1 ] && echo \"One or more prunes failed\" || echo \"Pruning done\"; else echo \"Pruning cancelled\"; fi"
```

for useful programs:

```bash
alias lag="lazygit"
alias lad="lazydocker"
```

and for a Raspberry Pi 5:

```bash
alias pifan="cat /sys/devices/platform/cooling_fan/hwmon/*/fan1_input"
alias pitemp="vcgencmd measure_temp"
```
