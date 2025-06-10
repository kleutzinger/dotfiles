#!/usr/bin/env -S uv run --script --with zyte-api
"""
    Usage:
    ./zyte-get.py <url>
    or
    uv run --script --with zyte-api zyte-get.py <url>

Fetches the browser HTML of a given URL using the Zyte API.
It will render js and return the HTML as seen in a browser.


Output will be written to browser_html.html

Prerequisites:
1. install uv
2. set env var ZYTE_API_KEY with your Zyte API key
"""

from zyte_api import ZyteAPI
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

client = ZyteAPI(api_key=os.getenv("ZYTE_API_KEY", ""))
response = client.get({"url": url, "browserHtml": True})

browser_html: str = response["browserHtml"]
with open(OUTPUT_FILE, "w") as fp:
    fp.write(browser_html)
    print(f"wrote {len(browser_html)} bytes to {OUTPUT_FILE}")
