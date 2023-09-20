#!/bin/sh
export BACKUP_TIME=$(date +%Y-%m-%d-%H-%M)
export DOKKU_VERSION=$(dokku version | awk '{print $3}')
sudo mkdir -p /var/lib/dokku/services
sudo chown dokku:dokku /var/lib/dokku/services
mkdir -p /tmp/dokku-backups/
sudo tar -czvf "/tmp/dokku-backups/${BACKUP_TIME}-dokku-${DOKKU_VERSION}-backup.tar.gz" /home/dokku /var/lib/dokku/config /var/lib/dokku/data /var/lib/dokku/services /var/lib/dokku/plugins

