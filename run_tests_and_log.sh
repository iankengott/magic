#!/usr/bin/env bash
set -euo pipefail

LOG_FILE="test_log.txt"

if [[ ! -f "$LOG_FILE" ]]; then
  touch "$LOG_FILE"
fi

{
  echo "===== Test run started: $(date -u '+%Y-%m-%d %H:%M:%S UTC') ====="
  python -m pytest
  echo "===== Test run finished: $(date -u '+%Y-%m-%d %H:%M:%S UTC') ====="
  echo
} | tee -a "$LOG_FILE"
