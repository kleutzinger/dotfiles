#!/bin/bash

# launch trilium so that it syncs to .local/share/trilium-data/
# but don't show the GUI
# this should be added to a cron job

timeout 30 bash -c 'Xvfb :99 & DISPLAY=:99 trilium' | ts | tee -a /tmp/trilium-sync.log

# note: it would be better to try and wait for the output
# Sending message to all clients: {"type":"sync-finished","lastSyncedPush":6192}
# but the timeout is good enough for now
