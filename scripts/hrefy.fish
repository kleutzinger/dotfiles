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
    exit 1
end

# get website.com from arbitrary urls / links
set SITE_NAME (echo $LINK | perl -l -0777 -ne 'print $1 if /https?:\/\/(www\.)?([a-zA-Z0-9-]+)\.[a-zA-Z0-9-]+/')

set TEXT (wget -qO- $LINK | perl -l -0777 -ne 'print $1 if /<title.*?>\s*(.*?)\s*<\/title/si')
# if no title found, use site name
if test -z $TEXT
    set TEXT $SITE_NAME
end

# make sure text is unescaped
set TEXT (echo $TEXT | perl -MHTML::Entities -pe 'decode_entities($_);')

set HREFD "<a href=\"$LINK\">$TEXT</a>"
# set HREFDMD "[$TEXT]($LINK)"
# echo -e "\t$HREFD"
echo -e "\t$HREFDMD"
echo $HREFD | xclip -selection clipboard -in
notify-send "Copied to clipboard: $HREFD"
