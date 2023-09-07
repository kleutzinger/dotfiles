#!/usr/bin/env fish

# USAGE: give me a name of a redis url on your dokku server
# (e.g. fredis, reno, reno-staging)
# I'll give back a REDIS_URL you can connect to from any computer
# and a shell command to get into the redis-cli


if not type -q dokku
    function dokku
        dokku_ $argv
    end
end

if not count $argv >/dev/null
    echo -e "supply db_name from" "\t dokku_ redis:list"
    dokku redis:list
    exit 1
end

set outfile (mktemp)
echo "made $outfile"

dokku redis:info $argv >$outfile
echo "wrote $outfile"
cat $outfile | python3 -c '
import fileinput
with fileinput.input() as f_input:
    for line in f_input:
        line = line.strip()
        if line.startswith("Dsn:"):
            dsn = line.split("Dsn:")[1].strip()
        if line.startswith("Exposed ports:"):
            if ("->" not in line):
                print(f"please run dokku redis:expose <db_name>")
                exit(1)
            port = line.split("->")[1]
password = dsn.split("@")[0].split(":")[-1]
print(f"{dsn}, {port}")
# redis://[:password@]host[:port][/db-number][?option=value]
connect_url = f"redis://:{password}@kevbot.xyz:{port}"
print("\t" + connect_url)
connect_cmd = f"redis-cli -h kevbot.xyz -p {port} -a {password}"
print("\t" + connect_cmd)
'
