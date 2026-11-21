#!/bin/bash
# wait_for.sh FILE_OR_PATTERN [SECONDS] : return when the file exists (or the line is in logs/v04_queue.log), or after SECONDS
end=$(( $(date +%s) + ${2:-560} ))
while [ $(date +%s) -lt $end ]; do
  if [ -e "$1" ] || grep -q "$1" logs/v04_queue.log 2>/dev/null; then echo "ready: $1"; exit 0; fi
  sleep 10
done
echo "not yet: $1"
