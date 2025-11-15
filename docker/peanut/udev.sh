#!/usr/bin/env sh

set -eu

RULE_FILE="/etc/udev/rules.d/99-docker-nut-usb.rules"

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
      printf "Usage: color {red|green|yellow|blue} \"message\"" >&2
      return 1
      ;;
  esac

  # ANSI escape: set color, print message, reset
  printf "\033[%sm%s\033[0m\n" "$code" "$msg"
}


err() {
  color red "$@" >&2
}

info() {
  color blue "$@"
}

usage() {
  cat <<EOF
Usage: $0 [path/to/secret.env] [-c|--create] [-f|--force] [-r|--remove]

Must be run as root.

- --create allows creating ${RULE_FILE}.
- --force allows overwriting ${RULE_FILE} if it already exists.
- --remove allows you to remove the created ${RULE_FILE} file.
EOF
}

FILE=""
FORCE=0
REMOVE=0
CREATE=0

for arg in "$@"; do
  case "${arg}" in
    -f|--force)
      FORCE=1
      ;;
    -r|--remove)
      REMOVE=1
      ;;
    -c|--create)
      CREATE=1
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    --)
      shift
      break
      ;;
    *)
      if [ -z "${FILE}" ]; then
        FILE="${arg}"
      else
        err "Unexpected argument: ${arg}"
        usage
        exit 1
      fi
      ;;
  esac
done

# Ensure running as root
if [ "$(id -u)" != "0" ]; then
  err "This script must be run as root"
  exit 1
fi

if [ "${REMOVE}" -eq 1 ]; then
  if [ -f "${RULE_FILE}" ]; then
    rm -f "${RULE_FILE}" || {
      err "Failed to remove ${RULE_FILE}"
      exit 1
    }
    info "Removed ${RULE_FILE}"
  else
    info "No rules file to remove at ${RULE_FILE}"
  fi
  exit 0
fi

if [ "${CREATE}" -ne 1 ]; then
  usage
  exit 0
fi

# Set default FILE if var not set
: "${FILE:=./secret.env}"

# Check secret.env exists
if [ ! -f "${FILE}" ]; then
  err "Secret file not found: ${FILE}"
  err "Create the file with VENDORID and PRODUCTID variables (e.g. VENDORID=1234)"
  exit 1
fi

# POSIX: source the env file
. "${FILE}"
info "Loaded environment from ${FILE}"

# Check variables exist
missing=0
if [ -z "${VENDORID-}" ]; then
  err "VENDORID is not set in ${FILE}"
  missing=1
fi
if [ -z "${PRODUCTID-}" ]; then
  err "PRODUCTID is not set in ${FILE}"
  missing=1
fi

if [ "${missing}" -ne 0 ]; then
  err "Please set VENDORID and PRODUCTID in ${FILE}"
  exit 1
fi

# Basic format validation: expect 4 hex digits (common USB ID format)
valid_hex4() {
  case "${1}" in
    [0-9A-Fa-f][0-9A-Fa-f][0-9A-Fa-f][0-9A-Fa-f]) return 0 ;;
    *) return 1 ;;
  esac
}

bad_format=0
if ! valid_hex4 "$VENDORID"; then
  err "Warning: VENDORID ('$VENDORID') does not look like 4 hex digits"
  bad_format=1
fi
if ! valid_hex4 "$PRODUCTID"; then
  err "Warning: PRODUCTID ('$PRODUCTID') does not look like 4 hex digits"
  bad_format=1
fi

if [ "${bad_format}" -ne 0 ]; then
  err "Aborting due to format validation. Fix values in ${FILE} and re-run"
  exit 1
fi

# Compose udev rule
RULE="ACTION==\"add\", SUBSYSTEM==\"usb\", ATTRS{idVendor}==\"${VENDORID}\", ATTRS{idProduct}==\"${PRODUCTID}\", MODE=\"0660\", GROUP=\"nut\""

info "Prepared udev rule:"
info "  Rule:   ${RULE}"
info "  Target: ${RULE_FILE}"

# If target exists and --force not provided, abort
if [ -e "${RULE_FILE}" ] && [ "$FORCE" -ne 1 ]; then
  if [ "${FORCE}" -eq 1 ]; then
    info "Target ${RULE_FILE} already exists. Overwriting..."
  else
    err "Target ${RULE_FILE} already exists. To overwrite, re-run with --force"
    exit 1
  fi
fi

# Write rule atomically
TMP="$(mktemp /tmp/udev-rule.XXXXXX)" || {
  err "Failed to create temp file"
  exit 1
}
printf '%s\n' "${RULE}" > "${TMP}"

# Set mode to 0644 so udev can read it (root owns it)
chmod 0644 "${TMP}"

# Move into place
mv "${TMP}" "${RULE_FILE}" || {
  err "Failed to move rule into place"
  rm -f "${TMP}" || true
  exit 1
}
info "Wrote ${RULE_FILE}"

# Reload udev rules and trigger
udevadm control --reload-rules && udevadm trigger
info "Reloaded and triggered udev rules"

exit 0


