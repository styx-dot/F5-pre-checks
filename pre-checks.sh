#!/bin/bash

# Variables for the F5 BIG-IP connection
F5_HOST="your_f5_ip_or_hostname"
F5_USER="your_f5_username"
F5_PASS="your_f5_password"

# Log file to store the results
LOG_FILE="f5_bigip_info.log"

# Commands to be run on the F5 BIG-IP
COMMANDS=(
  "tmsh show sys version"
  "tmsh show sys hardware"
  "tmsh list sys provision"
  "tmsh list /sys application service"
)

# Log into the F5 and execute the commands
echo "Logging into F5 BIG-IP and retrieving system information..."

{
  echo "========== F5 BIG-IP Information =========="
  echo "Date: $(date)"
  echo "Host: $F5_HOST"
  echo ""

  for CMD in "${COMMANDS[@]}"; do
    echo "=== Output of '$CMD' ==="
    sshpass -p "$F5_PASS" ssh -o StrictHostKeyChecking=no "$F5_USER@$F5_HOST" "$CMD"
    echo ""
  done

} > "$LOG_FILE"

echo "Information gathered and saved to $LOG_FILE"

