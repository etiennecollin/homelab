# Vaultwarden

The following commands should be executed from this directory (`vaultwarden` directory containing the `compose.yaml`).

## Setup Vaultwarden


## Setup Backups

Make sure the `vaultwarden-rclone-data` volume exists. Create it with:

```bash
docker volume create vaultwarden-rclone-data
```

Use the remote name `VaultwardenBackup`. Setup rclone with:

```bash
docker run --rm -it \
  --volumes-from=vaultwarden \
  --mount type=volume,source=vaultwarden-rclone-data,target=/config/ \
  ttionya/vaultwarden-backup:latest \
  rclone config
```

And verify the configuration with:

```bash
docker run --rm -it \
  --volumes-from=vaultwarden \
  --mount type=volume,source=vaultwarden-rclone-data,target=/config/ \
  ttionya/vaultwarden-backup:latest \
  rclone config show
```

## Manual Local Backup

Make sure to create a rclone remote called `Local` that backs up to the local disk, then execute:

```bash
docker run --rm -it \
  --volumes-from=vaultwarden \
  --mount type=bind,source=./config,target=/bitwarden/data/ \
  --mount type=bind,source=$(pwd),target=/VaultwardenBackup/ \
  --mount type=volume,source=vaultwarden-rclone-data,target=/config/ \
  --env BACKUP_FILE_SUFFIX="%Y%m%d" \
  --env RCLONE_REMOTE_DIR="/VaultwardenBackup/" \
  --env RCLONE_REMOTE_NAME="Local" \
  --env TIMEZONE="Canada/Eastern" \
  --env ZIP_ENABLE="TRUE" \
  --env ZIP_TYPE="7z" \
  --env ZIP_PASSWORD="DEFAULTPASSWORD" \ # MODIFY THIS PASSWORD
  ttionya/vaultwarden-backup:latest backup
```

> **DO NOT FORGET TO EDIT `ZIP_PASSWORD` IN THE COMMAND**

The backup will be generated in the current directory.

## Restore Backup

> **Important:** Restore will overwrite the existing files.

1. Stop the Vaultwarden container before the restore.

2. Download the backup files to your local machine.

3. Place the backup files to be restored in this directory (`vaultwarden` directory containing the `compose.yaml`).

```bash
docker run --rm -it \
  --mount type=bind,source=./config,target=/bitwarden/data/ \
  --mount type=bind,source=$(pwd),target=/bitwarden/restore/ \
  ttionya/vaultwarden-backup:latest restore \
  --zip-file <backup.xxx.7z> # MODIFY THIS FILE NAME
```

> **DO NOT FORGET TO EDIT `<backup.xxx.7z>` IN THE COMMAND**
