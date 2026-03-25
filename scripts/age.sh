#!/usr/bin/env bash
set -euo pipefail

AGE_DIR="${HOME}/.age"
KEY_FILE="${AGE_DIR}/key.txt"
RECIPIENT_FILE="${AGE_DIR}/key.pub"

cmd="${1:-}"
shift || true

mkdir -p "${AGE_DIR}"

encrypt_file() {
  local input="${1}"
  if [[ "${input}" == *.age ]]; then
    echo "==> Skipping already encrypted file: ${input}"
    return
  fi

  local output="${2:-${input}.age}"

  echo "==> Encrypting ${input} -> ${output}"
  age -R "${RECIPIENT_FILE}" -o "${output}" "${input}"

  if [[ "${DELETE_AFTER:-0}" -eq 1 ]]; then
    echo "==> Deleting original file: ${input}"
    rm -f "${input}"
  fi
}

decrypt_file() {
  local input="${1}"
  if [[ "$input" != *.age ]]; then
    echo "==> Skipping non-encrypted file: ${input}"
    return
  fi

  local output="${2:-${input%.age}}"

  echo "==> Decrypting ${input} -> ${output}"
  age -d -i "${KEY_FILE}" -o "${output}" "${input}"

  if [[ "${DELETE_AFTER:-0}" -eq 1 ]]; then
    echo "==> Deleting encrypted file: ${input}"
    rm -f "${input}"
  fi
}

generate_key() {
  if [[ -f "${KEY_FILE}" || -f "${RECIPIENT_FILE}" ]]; then
    echo "Key files already exist:"
    [[ -f "${KEY_FILE}" ]] && echo "   - ${KEY_FILE}"
    [[ -f "${RECIPIENT_FILE}" ]] && echo "   - ${RECIPIENT_FILE}"
    echo
    echo "Refusing to overwrite existing keys."
    echo "If you really want to regenerate them, delete the files manually:"
    echo "  rm -f \"${KEY_FILE}\" \"${RECIPIENT_FILE}\""
    exit 1
  fi

  echo "==> Generating post-quantum age key..."
  age-keygen -pq -o "${KEY_FILE}"

  echo "==> Extracting public key..."
  age-keygen -y "${KEY_FILE}" >"${RECIPIENT_FILE}"

  chmod 600 "${KEY_FILE}"

  echo "Keys generated:"
  echo "   Private: ${KEY_FILE}"
  echo "   Public : ${RECIPIENT_FILE}"
}

case "$cmd" in
gen)
  generate_key
  ;;

enc)
  DELETE_AFTER=0
  # Parse flags
  while getopts ":d" opt; do
    case $opt in
    d) DELETE_AFTER=1 ;;
    *)
      echo "Usage: ${0} enc [-d] <file1> [file2 ...]"
      exit 1
      ;;
    esac
  done
  shift $((OPTIND - 1))

  if [ "$#" -lt 1 ]; then
    echo "Usage: ${0} enc [-d] <file1> [file2 ...]"
    exit 1
  fi

  for file in "$@"; do
    encrypt_file "${file}"
  done
  ;;

dec)
  DELETE_AFTER=0
  # Parse flags
  while getopts ":d" opt; do
    case $opt in
    d) DELETE_AFTER=1 ;;
    *)
      echo "Usage: ${0} dec [-d] <file1.age> [file2.age ...]"
      exit 1
      ;;
    esac
  done
  shift $((OPTIND - 1))

  if [ "$#" -lt 1 ]; then
    echo "Usage: ${0} dec [-d] <file1.age> [file2.age ...]"
    exit 1
  fi

  for file in "$@"; do
    decrypt_file "${file}"
  done
  ;;

*)
  cat <<EOF
Usage:
  ${0} gen
  ${0} enc [-d] <file1> [file2 ...]
  ${0} dec [-d] <file1.age> [file2.age ...]

Examples:
  ${0} enc config/stacks.py
  ${0} enc -d config/stacks.py
  ${0} dec config/stacks.py.age
  ${0} dec -d config/stacks.py.age
EOF
  exit 1
  ;;
esac
