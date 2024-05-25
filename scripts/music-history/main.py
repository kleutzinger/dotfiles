# read sqlite db at music_history.db and parse the data
# https://dfir.pubpub.org/pub/xbvsrjt5/release/1

import sqlite3
import subprocess
import webbrowser
from collections.abc import MutableMapping
from typing import TypedDict

import blackboxprotobuf
import click
from blackboxprotobuf.lib.exceptions import DecoderException

TABLE_NAME = "recognition_history"
MUSIC_HISTORY_DB = "music_history.db"


def flatten(dictionary, parent_key=False, separator="."):
    """
    Turn a nested dictionary into a flattened dictionary
    """
    items = []
    for key, value in dictionary.items():
        new_key = str(parent_key) + separator + key if parent_key else key
        if isinstance(value, MutableMapping):
            items.extend(flatten(value, new_key, separator).items())
        elif isinstance(value, list):
            for k, v in enumerate(value):
                items.extend(flatten({str(k): v}, new_key).items())
        else:
            items.append((new_key, value))
    return dict(items)


schema = """
CREATE TABLE recognition_history (timestamp LONG PRIMARY KEY, history_entry BLOB, track_id STRING, artist STRING, title STRING, fingerprints BLOB, shards_region STRING, downloaded_shards_version INTEGER, core_shard_version INTEGER);
"""

columns_we_care_about = "timestamp history_entry artist title track_id".split(" ")


class Entry(TypedDict):
    timestamp: int
    history_entry: bytes
    artist: str
    title: str
    track_id: str


def remove_adjacent_dupes(iterable, keyname):
    """
    Remove adjacent duplicates from an iterable
    """
    last = None
    for item in iterable:
        if item[keyname] != last:
            yield item
            last = item[keyname]


# parse the history_entry column as protobuf
def parse_protobuf(blob):
    try:
        msg = blackboxprotobuf.decode_message(blob)[0]
        return flatten(msg)
    except DecoderException:
        return None


def get_all_rows(no_adjacent_dupes=True) -> list[Entry]:
    # connect to the database
    conn = sqlite3.connect(MUSIC_HISTORY_DB)
    cur = conn.cursor()

    # get all the data
    cur.execute(f"SELECT {','.join(columns_we_care_about)} FROM {TABLE_NAME}")
    rows = cur.fetchall()
    # zip the column names and the data
    rows = [Entry(**dict(zip(columns_we_care_about, row))) for row in rows]
    if no_adjacent_dupes:
        return list(remove_adjacent_dupes(rows, "track_id"))
    else:
        return rows


@click.group()
def cli():
    pass


# click command to select random song
@click.command()
def jukebox():
    rows = get_all_rows()
    import random

    random_row = random.choice(rows)
    click.echo(random_row)
    parsed = parse_protobuf(random_row["history_entry"])
    click.echo(parsed)
    # find value that has music.youtube.com in it
    url = [v for _, v in parsed.items() if "music.youtube.com" in str(v)][0]
    click.echo(url)
    try:
        subprocess.run(
            ["playerctl", "--player", "YoutubeMusic", "open", url], check=True
        )
    except subprocess.CalledProcessError:
        webbrowser.open(url)


cli.add_command(jukebox)

if __name__ == "__main__":
    cli()
