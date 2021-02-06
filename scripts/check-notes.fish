#!/usr/bin/env fish
# concat all `note.md`s to a single `tmp.html`
# open in $BROWSER
cd /home/kevin/notes/
set OUT (mktemp --suffix ".html")

for i in (ls *.md | sort -r)
    set FP (readlink -f $i)
    set FP "<a href='$FP'>$i</a>"
    echo "</br><hr></br><h1>$FP</h1>"
    cat $i
end | marked >> $OUT
echo "
<style>
* { font-family: monospace; }
a { 
    color: blue;
    text-decoration:none;
}
body {
  margin: 0 auto;
  width: 500px;
}
</style>" >> $OUT
$BROWSER $OUT > /dev/null
