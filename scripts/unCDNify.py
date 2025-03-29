#!/usr/bin/env python3

"""
finds all <script> tags in the HTML files and replaces the src and href attributes with the local file path and downloads the file to a ./static folder
"""

import os
import urllib.request
from bs4 import BeautifulSoup


def process_html_file(file, static_dir="static"):
    replacements = None
    with open(file, "r") as f:
        content = f.read()
        soup = BeautifulSoup(content, "html.parser")
        scripts = soup.find_all("script")
        replacements = dict()
        for script in scripts:
            if script.has_attr("src"):
                src = script["src"]
                if src.startswith("http"):
                    try:
                        filename = os.path.join(static_dir, os.path.basename(src))
                        if not filename.endswith(".js"):
                            filename += ".js"
                        if not os.path.exists(static_dir):
                            os.makedirs(static_dir)
                        basename = os.path.basename(filename)
                        # skip if filename already exists
                        replacements[src] = f"/{basename}"  # todo add prefix param
                        if os.path.exists(filename):
                            print(f"File {filename} already exists, skipping download.")
                            continue
                        urllib.request.urlretrieve(src, filename)
                        print(f"Downloaded {src} to {filename}")
                        # script["src"] = filename
                    except Exception as e:
                        print(f"Error downloading {src}: {e}")
    if replacements:
        with open(file, "w") as f:
            for cdnurl, localurl in replacements.items():
                print(f"Replacing {cdnurl} with {localurl}")
                content = content.replace(cdnurl, localurl)
            f.write(content)
        print(f"Updated {file} with local script paths")


def main():
    """
    find all html files
    """
    for root, directories, files in os.walk("."):
        for file in files:
            if file.endswith(".html"):
                process_html_file(os.path.join(root, file), static_dir="public")


main()
