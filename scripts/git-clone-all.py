#!/usr/bin/env python3
"""
clone all repos from my own github
"""

def main():
    # uset the gh command
    import subprocess
    import json

    repo_names = subprocess.check_output(
        ["gh", "repo", "list", "--json", "name"]
    ).decode("utf-8")
    for repo in json.loads(repo_names):
        repo_name = repo["name"]
        print(f"cloning {repo_name}")
        subprocess.run(["gh", "repo", "clone", repo_name])

main()
