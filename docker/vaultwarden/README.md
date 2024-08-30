# Restore

> **Important:** Restore will overwrite the existing files.

1. You need to stop the Docker container before the restore.

2. You also need to download the backup files to your local machine.

3. Go to the directory where your backup files to be restored are located.

```shell
docker run --rm -it \
  --mount type=bind,source=./config,target=/bitwarden/data/ \
  --mount type=bind,source=$(pwd),target=/bitwarden/restore/ \
  ttionya/vaultwarden-backup:latest restore \
  --zip-file backup.xxx.7z
```

