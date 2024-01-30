#!/home/kevin/.virtualenvs/++scripts/bin/python

from trilium_py.client import ETAPI
import os

TRILIUM_TOKEN = os.getenv("TRILIUM_TOKEN")

if not TRILIUM_TOKEN:
    raise Exception("TRILIUM_TOKEN not set")
    os.exit(1)

server_url = "https://tril.kevbot.xyz/"
ea = ETAPI(server_url, TRILIUM_TOKEN)

res = ea.search_note(
    search="melee",
)

for x in res["results"]:
    print(x["noteId"], x["title"])
