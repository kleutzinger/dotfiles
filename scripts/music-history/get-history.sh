#!/bin/bash

set -ex

# connects to your phone and pulls the history_db file from the music id app
# your phone must be rooted

# copy the history_db file to the download folder
adb shell "su -c 'cp /data/data/com.google.android.as/databases/history_db /storage/emulated/0/Download'"
adb pull /storage/emulated/0/Download/history_db

RECENT_TIMESTAMP=$(sqlite3 history_db "SELECT timestamp FROM recognition_history ORDER BY timestamp DESC LIMIT 1;")
# parse timestamp from unix ms to local time
RECENT_TIMESTAMP=$(date -d @$((RECENT_TIMESTAMP/1000)) +"%Y-%m-%d %H:%M:%S")
echo "Recent timestamp: $RECENT_TIMESTAMP"
