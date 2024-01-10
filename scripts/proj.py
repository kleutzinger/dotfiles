#!/usr/bin/env python3

import json
import os
import urllib.request
from iterfzf import iterfzf


home_dir = os.path.expanduser("~")
project_path = os.path.join(
    home_dir, "gits/kleutzinger.github.io/site-generator/generated/projects.json"
)
project_dl_uri = "https://kevinleutzinger.com/site-generator/generated/projects.json"
if not os.path.exists(project_path):
    project_path = os.path.join(home_dir, "projects.json")
    print("Downloading projects.json")
    urllib.request.urlretrieve(project_dl_uri, project_path)

with open(project_path, "r") as f:
    projects = json.load(f)
    # projcets is an array of dicts
    title = iterfzf([p["title"] for p in projects])
    proj = [p for p in projects if p["title"] == title][0]
    print(json.dumps(proj, indent=4))
