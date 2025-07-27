#!/usr/bin/env bash

set -euo pipefail

# The ignore‑file name
IGNORE_FILE=".projectignore"
SCRIPT_NAME="$(basename "${0}")"
SCRIPT_DIR="$(dirname "$(realpath "${0}")")"
DRY=false

# Arrays for actions and (optional) target project names
COMMANDS=()
TARGETS=()

usage() {
  cat <<EOF

Project discovery:
  - Any subdirectory of the script’s directory is a project.
  - Each project is assumed to have a 'docker‑compose.yaml' (or .yml) at its root.
  - Uses ../secret.env (relative to each project) to supply environment variables to Compose.

Ignoring projects:
  To skip a project entirely, place an (empty) file named '${IGNORE_FILE}' in that
  project’s root.

Usage:
  ${SCRIPT_NAME} [Options] [project1 project2 … | all]

Options:
  -p, --pull    append 'docker compose pull' to the action list
  -u, --up      append 'docker compose up -d --force-recreate'
  -d, --down    append 'docker compose down'
  -h, --help    show this help message
  --dry         run in dry-mode, does not make any changes to the machine

Order matters:
  ${SCRIPT_NAME} -p -u           # pull, then up for all projects
  ${SCRIPT_NAME} foo bar -u -p   # pull, then up, but only for projects 'foo' and 'bar'
  ${SCRIPT_NAME} -d all          # down for all projects

EOF
  exit 1
}

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


# Parse flags
while [ $# -gt 0 ]; do
  case "${1}" in
    -p | --pull) COMMANDS+=("pull") ;;
    -u | --up) COMMANDS+=("up") ;;
    -d | --down) COMMANDS+=("down") ;;
    -h | --help) usage ;;
    --dry) DRY=true ;;
    --) shift; break ;; # End of flags
    -*) color red "Unknown option: ${1}" >&2; usage ;;
    *) TARGETS+=("${1}") ;;
  esac
  shift
done

# Nothing to do?
if [ ${#COMMANDS[@]} -eq 0 ]; then
  color yellow "No commands specified; exiting."
  exit 0
fi

# Build full list of existing projects
ALL_PROJECTS=()
for path in "${SCRIPT_DIR}"/*/; do
  dir=${path%/}
  [ -d "$dir" ] || continue
  ALL_PROJECTS+=("$(basename "$dir")")
done

# Determine selected projects
if [ ${#TARGETS[@]} -eq 0 ] || printf '%s\n' "${TARGETS[@]}" | grep -qx "all"; then
  SELECTED_PROJECTS=("${ALL_PROJECTS[@]}")
else
  SELECTED_PROJECTS=()
  for target in "${TARGETS[@]}"; do
    if printf '%s\n' "${ALL_PROJECTS[@]}" | grep -qx "${target}"; then
      SELECTED_PROJECTS+=("${target}")
    else
      color yellow "Warning: project '${target}' not found – skipping." >&2
    fi
  done
fi

color green "Running ${SCRIPT_NAME} with actions: ${COMMANDS[*]}"
color green "Projects: ${SELECTED_PROJECTS[*]}"

prefix=""
if [ "$DRY" = "true" ]; then
  prefix="[DRY] "
fi

for project in "${SELECTED_PROJECTS[@]}"; do
  dir="${SCRIPT_DIR}/${project}"
  echo ""
  color blue "=== Project: ${project}"

  # Skip projectect if needed
  if [ -f "${dir}/${IGNORE_FILE}" ]; then
    color yellow "-> skipping project (${IGNORE_FILE} present)"
    continue
  fi

  pushd "${dir}" >/dev/null

  for action in "${COMMANDS[@]}"; do
    case "${action}" in
      pull)
        color blue "${prefix}-> pulling latest images"
        [ "${DRY}" = "true" ] && continue
        docker compose --env-file ../secret.env pull
        ;;
      up)
        color blue "${prefix}-> starting containers"
        [ "${DRY}" = "true" ] && continue
        docker compose --env-file ../secret.env up -d --force-recreate
        ;;
      down)
        color blue "${prefix}-> stopping containers"
        [ "${DRY}" = "true" ] && continue
        docker compose --env-file ../secret.env down
        ;;
    esac
  done

  popd >/dev/null
done
