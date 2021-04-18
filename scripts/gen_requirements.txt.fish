#!/usr/bin/env fish

set TEMP (mktemp -d)
for f in $argv
    cp $f $TEMP
end

pushd $TEMP
pigar
cat requirements.txt
echo 'writing in 2 seconds'
sleep 3
popd
cp $TEMP/requirements.txt .
echo 'done!'
