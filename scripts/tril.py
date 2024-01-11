#!/usr/bin/env python3

from trilium_py.client import ETAPI
import os

TRILIUM_TOKEN = os.getenv("TRILIUM_TOKEN")

server_url = "https://tril.kevbot.xyz/"
ea = ETAPI(server_url, TRILIUM_TOKEN)

res = ea.search_note(
    search="melee",
)

for x in res["results"]:
    print(x["noteId"], x["title"])
