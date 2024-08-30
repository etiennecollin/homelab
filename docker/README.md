# Docker

## Usage

When starting the containers with docker compose, use the following command to import the main `main.env` file.

```bash
docker compose --env-file ../secret.env up -d --force-recreate
```

## Install

- Debian: https://docs.docker.com/engine/install/debian/#install-using-the-repository
- Ubuntu: https://docs.docker.com/engine/install/ubuntu/#install-using-the-repository

## Post-Install

To use docker without `sudo`:

```bash
sudo groupadd docker
sudo usermod -aG docker $USER
newgrp docker
```

Start docker on boot:

```bash
sudo systemctl enable docker.service
sudo systemctl enable containerd.service
```
