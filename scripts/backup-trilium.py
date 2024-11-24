#!/usr/bin/env python3
"""
back up my local trilium db to a gzipped file
"""

import os
import subprocess
import datetime
import urllib.request
import json

LOCAL_ENDPOINT = "http://127.0.0.1:37840/custom/version"
DEPLOYED_ENDPOINT = "https://tril.kevbot.xyz/custom/version"


def main():
    # check if /home/kevin/.local/share/trilium-data/document.db exists
    home = os.path.expanduser("~")
    trilium_db = os.path.join(home, ".local/share/trilium-data/document.db")
    if not os.path.exists(trilium_db):
        print(f"{trilium_db} does not exist")
        exit(1)
    print(f"Backing up {trilium_db}")
    version = "unknown"
    for endpoint in [LOCAL_ENDPOINT, DEPLOYED_ENDPOINT]:
        try:
            with urllib.request.urlopen(endpoint) as response:
                version = json.loads(response.read())
                break
        except Exception:
            continue
    today = datetime.date.today()
    time = datetime.datetime.now().strftime("%H-%M-%S")
    output_filepath = f"trilium-next-{version}-{today}-{time}.sql"
    if os.path.exists(output_filepath) or os.path.exists(output_filepath + ".gz"):
        print(f"{output_filepath} already exists")
        exit(1)
    size_before = os.path.getsize(trilium_db)
    print(f"Size before: {size_before / 1024 / 1024:.2f} MB")

    # dump the database to file, output to current dir
    with open(output_filepath, "w") as f:
        subprocess.run(["sqlite3", trilium_db, ".dump"], stdout=f)
    # compress the file
    subprocess.run(["gzip", "--force", output_filepath])
    print("gzipped")
    size_after = os.path.getsize(output_filepath + ".gz")
    # print size both before and after in MB
    print(f"Size after: {size_after / 1024 / 1024:.2f} MB")
    print("backed up to", output_filepath + ".gz")


main()
