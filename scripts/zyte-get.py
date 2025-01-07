#!/usr/bin/env python3

import requests
import os
import sys

OUTPUT_FILE = "browser_html.html"

if len(sys.argv) < 2:
    print(f"Usage: {sys.argv[0]} <url>")
    sys.exit(1)

url = sys.argv[1]

# check url
if not url.startswith("http"):
    print(f"Invalid URL: {url}")
    sys.exit(1)

api_response = requests.post(
    "https://api.zyte.com/v1/extract",
    auth=(os.getenv("ZYTE_API_KEY", ""), ""),
    json={
        "url": url,
        "browserHtml": True,
    },
)
browser_html: str = api_response.json()["browserHtml"]
with open(OUTPUT_FILE, "w") as fp:
    fp.write(browser_html)
    print(f"wrote {len(browser_html)} bytes to {OUTPUT_FILE}")
