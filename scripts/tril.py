#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.13"
# dependencies = [
#     "click",
#     "trilium_py",
# ]
# ///

from trilium_py.client import ETAPI
import click
import os
import sys
import json

TRILIUM_TOKEN = os.getenv("TRILIUM_TOKEN")
RADIO_NOTE_ID = "m6NTBP3tMMRV"

if not TRILIUM_TOKEN:
    raise Exception("TRILIUM_TOKEN not set")

server_url = os.getenv("TRILIUM_URL")

if not server_url:
    print("no TRILIUM_URL set")
    exit(1)

ea = ETAPI(server_url + "/", TRILIUM_TOKEN)


@click.command()
@click.option("--url", help="URL to add")
def add_radio(url):
    # append radio url as <a> tag to radio note
    radio_note_content = ea.get_note_content(
        noteId=RADIO_NOTE_ID,
    )
    if url in radio_note_content:
        print(f"URL {url} already in radio note, not adding")
        sys.exit(1)
    radio_note_content += f'<br><a href="{url}">{url}</a>'
    ea.update_note_content(
        noteId=RADIO_NOTE_ID,
        content=radio_note_content,
    )


@click.command()
@click.argument("search", required=True, type=str)
def search_notes(search):
    if search:
        res = ea.search_note(
            search=search,
        )["results"]
        if not res:
            print("no results found")
            exit(1)
        print(json.dumps(res))
        return res


@click.command()
@click.argument("noteid", required=True, type=str)
def get_note_content(noteid):
    content = ea.get_note_content(
        noteId=noteid,
    )
    print(content)
    return content


@click.command()
@click.argument("attribute", required=True)
@click.argument("value", required=True)
def search_for_attribute(attribute, value):
    print(attribute, value)
    """
    search for the attribute name
    then iterate through and find all that have the appropriate value
    """
    raise NotImplementedError


# handle multiple commands
@click.group()
def cli():
    pass


if __name__ == "__main__":
    cli.add_command(add_radio)
    cli.add_command(search_notes)
    cli.add_command(get_note_content)
    cli.add_command(search_for_attribute)
    cli()
