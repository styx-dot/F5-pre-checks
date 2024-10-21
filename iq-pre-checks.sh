IQ_LOG_FILE="f5_bigiq_info.log"

echo "Retrieving info from F5 BIG-IQ..."

{
  echo "=== Check image availability on BigIQ ==="
  echo ""

  # Loop through each file in the FILES array
  for FILE in "${FILES[@]}"; do
    if [ -e "/root/Git_prj/F5-pre-checks/$FILE" ]; then
      echo "'$FILE': OK"
    else
      echo "'$FILE': ERROR"
    fi

  done
  
  echo ""
  echo "------------------------------------------------------------------------------------"
  echo ""

} > "$IQ_LOG_FILE"

echo "Information gathered and saved to $IQ_LOG_FILE"