#!/bin/bash

# Variables for the F5 BIG-IP connection
F5_HOST="10.171.230.191"
F5_USER="root"
F5_PASS="default"

# Log file to store the results
LOG_FILE="f5_bigip_info.log"

# Commands to be run on the F5 BIG-IP
COMMANDS=(
  "tmsh show sys version"
  "tmsh list sys provision"
  "tmsh show cm failover-status"
  "tmsh list cm device-group"
  "tmsh show cm sync-status"
  "tmsh show sys license | grep -E 'Service Check Date'"
  "ls -al /var/config/rest/iapps/"
  "ls -al /var/core"
  "tmsh show /sys mcp"
  "tmsh list /sys db systemauth.disablerootlogin value"
  "tmsh list sys icall script auto_backup"
  "df -h" 
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
    echo "------------------------------------------------------------------------------------"
    echo ""
  done

} > "$LOG_FILE"

echo "Information gathered and saved to $LOG_FILE"