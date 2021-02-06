DEST=""
if [ $1 = "blog" ]; then
  cd /home/kevin/blog.kevbot.xyz/
  eleventy
  DEST="root@kevbot.xyz:/var/lib/dokku/data/storage/blog/"
  SRC="/home/kevin/blog.kevbot.xyz/_site/"

elif [ $1 = "static" ]; then
  DEST="root@kevbot.xyz:/root/sites/the-lounge-test/"
  echo "nvm"
  exit 1
else
  echo "expected one argument: [blog, static]"
  exit 1
fi

echo pushing to $DEST

rsync -v -ah \
    --cvs-exclude --exclude="node_modules" --exclude-from="$(git -C ./ ls-files \
        --exclude-standard -oi --directory >.git/ignores.tmp && \
        echo .git/ignores.tmp)" \
    $SRC $DEST --delete
