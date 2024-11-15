#! /usr/bin/env fish
# call using ./hrefy.fish TEXT?
# Reads clipboard for a link and prompts for TEXT
# generates <a href=""$LINK"> $TEXT </a>


set LINK (xclip -o)
set regex '(https?|ftp|file)://[-A-Za-z0-9\+&@#/%?=~_|!:,.;]*[-A-Za-z0-9\+&@#/%=~_|]'

if string match -r $regex $LINK
    echo "Found link in clipboard"
else
    echo "No link found in clipboard"
    notify-send "No link found in clipboard"
    exit 1
end

# get website.com from arbitrary urls / links
set SITE_NAME (echo $LINK | perl -l -0777 -ne 'print $1 if /https?:\/\/(www\.)?([a-zA-Z0-9-]+)\.[a-zA-Z0-9-]+/')

# todo: make it so we run javascript on the site to get the title
set TEXT (wget -qO- $LINK | perl -l -0777 -ne 'print $1 if /<title.*?>\s*(.*?)\s*<\/title/si')
# if no title found, use site name
if test -z $TEXT
    set TEXT $SITE_NAME
end

# make sure text is unescaped
set TEXT (echo $TEXT | perl -MHTML::Entities -pe 'decode_entities($_);')

set HREFD "<a href=\"$LINK\">$TEXT</a>"

echo -n $HREFD | xclip -selection clipboard -i -t text/html

# todo: set plaintext target as well to bare url
# echo -n $LINK | xclip -selection clipboard -i -t text/plain
# this almost works but when i paste into certain apps it pastse the plaintext instead of the html

# i want to replicate the behavior of copying a link from a browser instead:
# when you copy a link from a browser, it copies the link as html and plaintext
# when you paste into a rich text editor, it pastes the html
# when you paste into a plaintext editor, it pastes the plaintext


echo -e "copied \t$HREFD"
notify-send "$LINK"
notify-send "$TEXT"
