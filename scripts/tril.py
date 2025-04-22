#!/usr/bin/env -S uv run --script --with click --with trilium_py

from trilium_py.client import ETAPI
import click
import os
import sys

TRILIUM_TOKEN = os.getenv("TRILIUM_TOKEN")
RADIO_NOTE_ID = "m6NTBP3tMMRV"

if not TRILIUM_TOKEN:
    raise Exception("TRILIUM_TOKEN not set")

server_url = "https://tril.kevbot.xyz/"
ea = ETAPI(server_url, TRILIUM_TOKEN)


@click.command()
@click.option("--url", help="Title of the note")
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
@click.option("--search", help="Search for a note")
def search_notes(search):
    if search:
        res = ea.search_note(
            search=search,
        )
        for x in res["results"]:
            print(x["noteId"], x["title"])


@click.command()
@click.argument("noteid", required=True, type=str)
def get_note_content(noteid):
    content = ea.get_note_content(
        noteId=noteid,
    )
    print(content)
    return content


# handle multiple commands
@click.group()
def cli():
    pass


if __name__ == "__main__":
    cli.add_command(add_radio)
    cli.add_command(search_notes)
    cli.add_command(get_note_content)
    cli()
