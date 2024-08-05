#!/usr/bin/env python3
"""
clone all repos from my a given github org
"""

import subprocess
import json
import sys


def main():
    # get orgname from argv
    if len(sys.argv) < 2:
        print("Usage: git-clone-all.py orgname")
        sys.exit(1)
    orgname = sys.argv[1]
    if orgname == "me":
        orgname = ""

    repo_names = subprocess.check_output(
        ["gh", "repo", "list", orgname, "--json", "name", "--limit", "200"]
    ).decode("utf-8")
    for repo in json.loads(repo_names):
        repo_name = repo["name"]
        print(f"cloning {repo_name}")
        subprocess.run(["gh", "repo", "clone", f"{orgname}/{repo_name}"])


main()
