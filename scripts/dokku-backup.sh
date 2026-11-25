#!/bin/sh
# Back up the whole dokku install (per https://dokku.com/docs/advanced-usage/backup-recovery/)
# and upload it to the private backblaze bucket.
# Run when no deploys / dokku commands are in progress.
# Restore: sudo tar -xzvf backup.tar.gz -C /   (then rebuild apps; cache rebuilds on first deploy)
set -eu

SCRIPT_DIR=$(cd "$(dirname "$0")" && pwd)
BACKUP_TIME=$(date +%Y-%m-%d-%H-%M)
DOKKU_VERSION=$(cat /var/lib/dokku/VERSION)
BACKUP_DIR=/tmp/dokku-backups
BACKUP_FILE="${BACKUP_DIR}/${BACKUP_TIME}-dokku-${DOKKU_VERSION}-backup.tar.gz"

SOURCES="/home/dokku /var/lib/dokku/config /var/lib/dokku/data /var/lib/dokku/services /var/lib/dokku/plugins"
START=$(date +%s)
step() { printf '\n==> [%s] %s\n' "$(date +%H:%M:%S)" "$*"; }

sudo mkdir -p /var/lib/dokku/services
sudo chown dokku:dokku /var/lib/dokku/services
mkdir -p "$BACKUP_DIR"

step "Dokku $DOKKU_VERSION, writing $BACKUP_FILE"
step "Measuring source directories (build cache excluded)"
# shellcheck disable=SC2086
sudo du -sch --exclude='home/dokku/*/cache' $SOURCES

# Excludes the per-app herokuish build cache (/home/dokku/<app>/cache);
# it is regenerated on the next build.
# Prints a progress line roughly every 100MB read.
step "Creating archive"
# shellcheck disable=SC2086
sudo tar -czf "$BACKUP_FILE" \
    --totals \
    --checkpoint=10000 \
    --checkpoint-action='echo=  %{%H:%M:%S}t  read %{r}T' \
    --no-wildcards-match-slash \
    --exclude='home/dokku/*/cache' \
    $SOURCES

# tar ran as root; hand the archive to us so the uploader can read it
sudo chown "$(id -u):$(id -g)" "$BACKUP_FILE"
step "Archive done: $(du -h "$BACKUP_FILE" | cut -f1)"

step "Uploading to backblaze (private)"
"$SCRIPT_DIR/backblaze-upload.py" "$BACKUP_FILE" --private --no-link

rm -f "$BACKUP_FILE"
step "Done in $(( ($(date +%s) - START) / 60 ))m $(( ($(date +%s) - START) % 60 ))s; local archive removed"
