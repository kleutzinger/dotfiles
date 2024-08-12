#!/usr/bin/env python3
"""
back up my local trilium db to a gzipped file
"""

import os
import subprocess
import datetime


def main():
    # check if /home/kevin/.local/share/trilium-data/document.db exists
    home = os.path.expanduser("~")
    trilium_db = os.path.join(home, ".local/share/trilium-data/document.db")
    if not os.path.exists(trilium_db):
        print(f"{trilium_db} does not exist")
        exit(1)
    print(f"Backing up {trilium_db}")
    output = subprocess.check_output(["yay", "-Q", "trilium-bin"])
    version = output.decode().split(" ")[1].strip().split("-")[0]
    today = datetime.date.today()
    output_filepath = f"trilium-{version}-{today}.sql"
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
