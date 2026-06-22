#!/bin/zsh
set -eu

REPO="/Volumes/Disk 2/Local Folder/conCOREdance-transmission-archive-github"
LOG_DIR="/Volumes/Disk 2/Local Folder/ConCOREdance/04_Sync_Reports"
LOG_FILE="${LOG_DIR}/launchd_local_google_drive_sync.log"

mkdir -p "${LOG_DIR}"
cd "${REPO}"

{
  echo "== $(date -u '+%Y-%m-%dT%H:%M:%SZ') local Google Drive sync =="
  /usr/bin/python3 scripts/local_google_drive_sync.py --commit
  echo
} >> "${LOG_FILE}" 2>&1
