#!/bin/bash
# push static file to vps /
VPS_STATIC_FOLDER="kevin@kevbot.xyz:/home/kevin/pushed/"

DEST=""
# if [ $1 = "live" ]; then
#   DEST="root@kevbot.xyz:/root/sites/the-lounge/"
# elif [ $1 = "test" ]; then
#   DEST="root@kevbot.xyz:/root/sites/the-lounge-test/"
# else
#   echo "expected one argument: [live, test]"
#   exit 1
# fi

rsync -v --stats --progress -az -zz "$@"  $VPS_STATIC_FOLDER
echo "pushed to $VPS_STATIC_FOLDER"

#
#curl -i -F 'files[]=@hi.txt' https://uguu.se/upload.php


#curl -i -F 'files[]=@hi.txt' https://uguu.se/upload.php

#curl -i -F 'file=@hi.txt' https://tmp.ninja/api.php?d=upload
