#!/usr/bin/env fish

# this script will read a .env file and output a dokku config:set
# command. Pass --interactive to pick which keys to include via fzf
# (tab to multiselect, enter to confirm).

set env_file ".env"
set app_name_probably (git rev-parse --show-toplevel | xargs basename)

# all relevant lines in the .env file
set lines (cat $env_file | grep -v '^#' | grep -v '^$')

if contains -- --interactive $argv
    set lines (printf '%s\n' $lines | fzf -m --header 'TAB to select keys, ENTER to confirm')
    if test (count $lines) -eq 0
        echo "no keys selected" >&2
        exit 1
    end
end

set output "dokku config:set --no-restart $app_name_probably "

for line in $lines
    set -l line2 (string split -m 1 = $line)
    set -l key $line2[1]
    set -l value (echo $line2[2] | string trim --chars '\n')
    set output "$output'$key=$value' "
end

echo $output
