#!/bin/fish

# this script will read a .env file and output a dokku config:set
# command

set env_file ".env"
set app_name_probably (git rev-parse --show-toplevel | xargs basename)
set output "dokku config:set --no-restart $app_name_probably "


# loop through all relevant lines in the .env file
for line in (cat $env_file | grep -v '^#' | grep -v '^$')
    # encode all values (not keys) with base64
    set -l line2 (string split -m 1 = $line)
    set -l key $line2[1]
    set -l value (echo $line2[2] | string trim --chars '\n')
    set output "$output'$key=$value' "
end

echo $output
