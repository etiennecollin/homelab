#!/usr/bin/env bash

set -euo pipefail

ENV_FILE="secret.env"
OUTPUT_FILE="./config/ups.conf"

# Ensure .env exists
if [[ ! -f "${ENV_FILE}" ]]; then
  echo "Error: ${ENV_FILE} not found"
  exit 1
fi

if [[ -f "${OUTPUT_FILE}" ]]; then
  echo "Error: ${OUTPUT_FILE} already exists"
  exit 1
fi

# Export variables from .env safely
set -o allexport
source "${ENV_FILE}"
set +o allexport

# Validate required variables
if [[ -z "${UPS_IP_ADDRESS:-}" ]]; then
  echo "Error: UPS_IP_ADDRESS is not set in ${ENV_FILE}"
  exit 1
fi

if [[ -z "${UPS_DESCRIPTION:-}" ]]; then
  echo "Error: UPS_DESCRIPTION is not set in ${ENV_FILE}"
  exit 1
fi

if [[ -z "${SNMP_USERNAME:-}" ]]; then
  echo "Error: SNMP_USERNAME is not set in ${ENV_FILE}"
  exit 1
fi

if [[ -z "${SNMP_PASSWORD:-}" ]]; then
  echo "Error: SNMP_PASSWORD is not set in ${ENV_FILE}"
  exit 1
fi

# Generate config file
cat >"${OUTPUT_FILE}" <<EOF
[eaton_9px1500rt-l]
    driver = "snmp-ups"
    port = "${UPS_IP_ADDRESS}"
    snmp_version = "v3"
    secLevel = "authNoPriv" # noAuthNoPriv | authNoPriv | authPriv
    secName = "${SNMP_USERNAME}" # SNMPv3 username
    authPassword = "${SNMP_PASSWORD}"
    authProtocol = "SHA512"
    pollfreq = "15"
    desc = "${UPS_DESCRIPTION}"
EOF

echo "Configuration written to ${OUTPUT_FILE}"
