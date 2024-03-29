#!/usr/bin/env fish

# Updates SSL certificates for my dokku instance on the domains
# kevbot.xyz and *.kevbot.xyz
# wildcard letsencrypt certs require manual .txt challenges
# so this script is not fully automated

# command to check if .TXT records are set:
if test (id -u) -eq 0
    echo "running as root"
else
    echo "Please run as root"
    exit 1
end

if type -q dokku
    function DOKKU_CMD
        dokku $argv
    end
else
    function DOKKU_CMD
        dokku_ $argv
    end
end

function read_confirm
    while true
        read -l -P 'Do you want to continue? [y/N] ' confirm
        switch $confirm
            case Y y
                return 0
            case '' N n
                return 1
        end
    end
end


set APPS (DOKKU_CMD --quiet apps:list)
mkdir -p /etc/letsencrypt/live/kevbot.xyz
cd /etc/letsencrypt/live/kevbot.xyz

echo "please run to check deployed .txt records:"
echo "nslookup -q=txt _acme-challenge.kevbot.xyz."
certbot certonly --manual --preferred-challenges=dns --domain "kevbot.xyz,*.kevbot.xyz"

 if test $status -eq 0
     echo "certbot OK"
 else
     echo "certbot Error!"
     exit 1
 end

# command worked?
echo "Combining certs to certs.tar"
cp privkey.pem server.key; cp fullchain.pem server.crt
tar cvf certs.tar server.crt server.key

echo "Overwrite certificates with certs.tar?"

if read_confirm
    echo "Setting certs on all apps"
else
    echo "Do not overwrite. Exiting"
    exit 0
end
set SSL_DIR /etc/nginx/ssl
mkdir -p $SSL_DIR
cp server.crt server.key $SSL_DIR

echo "$DOKKU_CMD global-cert:set < certs.tar"
DOKKU_CMD global-cert:set < certs.tar

for APP in $APPS
    echo "DOKKU_CMD certs:add $APP < certs.tar"
    DOKKU_CMD certs:add $APP < certs.tar
end

sudo service nginx reload
echo 'done'
