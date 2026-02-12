#!/usr/bin/env bash

set -euo pipefail

ENV_FILE="secret.env"
OUTPUT_FILE="./config/settings.yml"

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

# Apply defaults
NUT_SERVER_PORT="${NUT_SERVER_PORT:-3493}"
NUT_SERVER_API_USERNAME="${NUT_SERVER_API_USERNAME:-upsmon}"

# Validate required variables
if [[ -z "${NUT_SERVER_ADDRESS:-}" ]]; then
    echo "Error: NUT_SERVER_ADDRESS is not set in ${ENV_FILE}"
    exit 1
fi

if [[ -z "${NUT_SERVER_API_PASSWORD:-}" ]]; then
    echo "Error: NUT_SERVER_API_PASSWORD is not set in ${ENV_FILE}"
    exit 1
fi

# Generate YAML
cat > "${OUTPUT_FILE}" <<EOF
NUT_SERVERS:
  - HOST: ${NUT_SERVER_ADDRESS}
    PORT: ${NUT_SERVER_PORT}
    USERNAME: ${NUT_SERVER_API_USERNAME}
    PASSWORD: ${NUT_SERVER_API_PASSWORD}
    NAME: eaton_9px1500rt-l
    DISABLED: false
INFLUX_HOST: ''
INFLUX_TOKEN: ''
INFLUX_ORG: ''
INFLUX_BUCKET: ''
INFLUX_INTERVAL: 10
DATE_FORMAT: YYYY/MM/DD
TIME_FORMAT: 24-hour
DASHBOARD_SECTIONS:
  - key: KPIS
    enabled: true
  - key: CHARTS
    enabled: true
  - key: VARIABLES
    enabled: true
DISABLE_VERSION_CHECK: false
TEMPERATURE_UNIT: celsius
EOF

echo "Configuration written to ${OUTPUT_FILE}"
