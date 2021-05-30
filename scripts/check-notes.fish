#!/usr/bin/env fish
# concat all `note.md`s to a single `tmp.html`
# open in $BROWSER
cd $NOTE_DIR
# I use asciidoc rather than markdown now
set NOTE_EXT adoc
set OUT (mktemp --suffix ".html")

for i in (ls *.$NOTE_EXT | sort -r)
    # FP is filepath to note file
    set FP (readlink -f $i)
    set FP "<a href='$FP'>$i</a>"
    echo -e "\n\n'''\n\n"
    cat $i
end | asciidoctor - >> $OUT
xdg-open $OUT > /dev/null
