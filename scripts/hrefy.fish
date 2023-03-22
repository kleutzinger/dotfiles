#! /usr/bin/env fish
# call using ./hrefy.fish TEXT?
# Reads clipboard for a link and prompts for TEXT
# generates <a href=""$LINK"> $TEXT </a>

set LINK (xclip -o)
set regex '(https?|ftp|file)://[-A-Za-z0-9\+&@#/%?=~_|!:,.;]*[-A-Za-z0-9\+&@#/%=~_|]'

if string match -r $regex $LINK
    echo "Found link in clipboard"
else
    # prompt user for link
    read -P "URL: " LINK
end

echo $LINK

if not set -q argv[1]
    # Prompt for <a>TEXT</a>
    # get <title> tag from page, hopefully
    set TEXT (wget -qO- $LINK | perl -l -0777 -ne 'print $1 if /<title.*?>\s*(.*?)\s*<\/title/si')
else
    # TEXT Found in args
    set TEXT $argv[1]
end

set HREFD "<a href=\"$LINK\">$TEXT</a>"
set HREFDMD "[$LINK]($TEXT)"
echo -e "\t$HREFD"
echo -e "\t$HREFDMD"
echo "Put in clipboard?"
read -P "Ctrl+C to cancel: " YESNO
echo $HREFD | xclip -selection clipboard -in
