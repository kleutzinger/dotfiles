#!/usr/bin/env python3

import os
from subprocess import check_output

homedir = os.path.expanduser("~")
dokku_sh = os.path.join(homedir, "gits/dokku/contrib/dokku_client.sh")
output = check_output(["bash", dokku_sh, "config"])

output = output.decode("utf-8")

for line in output.split("\n"):
    if line.startswith("===="):
        continue
    ignore = (
        "DOKKU_APP_RESTORE",
        "DOKKU_APP_TYPE",
        "DOKKU_PROXY_PORT",
        "DOKKU_PROXY_SSL_PORT",
        "GIT_REV",
    )
    if line.startswith(ignore):
        continue
    if line == "":
        continue
    key, value = line.split(":", 1)
    value = value.lstrip()
    print("{}={}".format(key, value))
