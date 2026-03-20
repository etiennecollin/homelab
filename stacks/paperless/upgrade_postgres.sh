#!/usr/bin/env bash

set -euo pipefail

START_DIR=$(pwd)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TIMESTAMP=$(date +"%Y%m%d%H%M%S")

container_app_name="paperless"
container_postgres_name="paperless-postgres"
postgres_user="paperless"
db_dump_file="./backup_${TIMESTAMP}.sql"
db_data_dir="./config/pgdata"
db_data_dir_old="${db_data_dir}-old-${TIMESTAMP}"

color() {
  local col="$1"
  shift
  local msg="$*"
  local code

  case "$col" in
    red)    code="31" ;; # errors
    green)  code="32" ;; # success
    yellow) code="33" ;; # warnings
    blue)   code="34" ;; # info
    *)
      echo "Usage: color {red|green|yellow|blue} \"message\"" >&2
      return 1
      ;;
  esac

  # ANSI escape: set color, print message, reset
  printf "\033[%sm%s\033[0m\n" "$code" "$msg"
}

confirm() {
  prompt=$1
  printf "\033[34m%s\033[0m \033[33m[y/N]\033[0m: " "$prompt"
  read answer || return 1

  case $answer in
  y | Y | yes | YES) return 0 ;;
  *) return 1 ;;
  esac
}

cd "${SCRIPT_DIR}"

if ! confirm "Have you set the new postgres version in the compose.yaml file?"; then
  color red "Please set the new postgres version in the compose.yaml file and run this script again."
  exit 1
fi

color blue "Stopping ${container_app_name} container..."
docker compose --env-file ../secret.env down --remove-orphans ${container_app_name}

color blue "Current postgres version:"
docker compose --env-file ../secret.env exec -T ${container_postgres_name} psql -U ${postgres_user} -c 'SELECT version();'

color blue "Backing up database to ${db_dump_file}..."
docker compose --env-file ../secret.env exec -T ${container_postgres_name} pg_dumpall -U ${postgres_user} >${db_dump_file}

color blue "Stopping ${container_postgres_name} container..."
docker compose --env-file ../secret.env down --remove-orphans ${container_postgres_name}

color blue "Backing up ${db_data_dir} to ${db_data_dir_old}"
mv ${db_data_dir} ${db_data_dir_old}

color blue "Pulling latest postgres image..."
docker compose --env-file ../secret.env pull ${container_postgres_name}

color blue "Starting container with new postgres image..."
docker compose --env-file ../secret.env up -d --force-recreate ${container_postgres_name}

color blue "Waiting for the new postgres container to initialize..."
until docker compose --env-file ../secret.env exec -T ${container_postgres_name} pg_isready -U ${postgres_user}; do
    sleep 2
done

color blue "Printing postgres logs:"
docker compose --env-file ../secret.env logs --tail 100 --timestamps ${container_postgres_name}

if ! confirm "Continue with database restore? Make sure to check the logs for any errors."; then
  color red "Aborting database restore."
  exit 1
fi

color blue "New postgres version:"
docker exec -i ${container_postgres_name} psql -U ${postgres_user} -c 'SELECT version();'

color blue "Restoring the database from ${db_dump_file}..."
docker exec -i ${container_postgres_name} psql -U ${postgres_user} <${db_dump_file}
color green "Database restored."

color blue "Restarting ${container_app_name} container..."
docker compose --env-file ../secret.env up -d --force-recreate ${container_app_name}

color blue "Once you have verified everything is working, you can delete the old db data with:"
color blue "sudo rm -rf ${db_data_dir_old} ${db_dump_file}"

cd "${START_DIR}"

