#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.13"
# dependencies = [
#     "click",
#     "requests",
# ]
# ///

"""
Downloads a YouTube video's audio (as mp3, with embedded thumbnail) via
yt-dlp, then uploads it as a soundbite source to bag.kevbot.xyz,
authenticated via API key.

usage:
    bag-soundbite-upload.py <youtube-url>
    bag-soundbite-upload.py <youtube-url> --title "Custom title"

Re-running with the same URL updates the existing source in place
(the server dedups sources by URL).

Prerequisites:
1. uv (yt-dlp itself is fetched on the fly via `uvx`)
2. BAG_KEVBOT_XYZ_API_KEY env var set to a key generated at
   https://bag.kevbot.xyz/account
"""

import mimetypes
import os
import subprocess
import sys
import tempfile
import webbrowser

import click
import requests

API_KEY = os.getenv("BAG_KEVBOT_XYZ_API_KEY")
if not API_KEY:
    raise ValueError("BAG_KEVBOT_XYZ_API_KEY environment variable is required")


def download(url: str, dest_dir: str) -> tuple[str, str]:
    """Downloads url's audio into dest_dir with yt-dlp as an mp3, embedding
    the thumbnail. Returns (filepath, title)."""
    result = subprocess.run(
        [
            "uvx", "--no-cache", "yt-dlp",
            "-f", "bestaudio",
            "-x", "--audio-format", "mp3",
            "--embed-thumbnail",
            "--print", "TITLE:%(title)s",
            "--print", "after_move:FILEPATH:%(filepath)s",
            "-o", "%(title).200B [%(id)s].%(ext)s",
            url,
        ],
        cwd=dest_dir,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise click.ClickException(f"yt-dlp failed:\n{result.stderr}")

    filepath = None
    video_title = None
    for line in result.stdout.splitlines():
        if line.startswith("FILEPATH:"):
            filepath = os.path.join(dest_dir, line[len("FILEPATH:"):])
        elif line.startswith("TITLE:"):
            video_title = line[len("TITLE:"):]

    if not filepath or not os.path.exists(filepath):
        raise click.ClickException(f"yt-dlp didn't report a downloaded file:\n{result.stdout}")
    return filepath, video_title or os.path.basename(filepath)


def upload(api_base: str, youtube_url: str, filepath: str, title: str) -> dict:
    content_type = mimetypes.guess_type(filepath)[0] or "application/octet-stream"
    with open(filepath, "rb") as f:
        resp = requests.post(
            f"{api_base}/soundbites/admin/sources/upload",
            headers={"Authorization": f"Bearer {API_KEY}"},
            data={"url": youtube_url, "title": title},
            files={"file": (os.path.basename(filepath), f, content_type)},
        )
    if not resp.ok:
        try:
            detail = resp.json().get("detail", resp.text)
        except ValueError:
            detail = resp.text
        raise click.ClickException(f"Upload failed ({resp.status_code}): {detail}")
    return resp.json()


@click.command()
@click.argument("youtube_url")
@click.option("--title", default=None, help="Override the source title (default: the video's own title)")
@click.option(
    "--api-base",
    default=lambda: os.getenv("BAG_KEVBOT_XYZ_API_BASE", "https://bag.kevbot.xyz"),
    help="Base URL of the bag.kevbot.xyz deployment",
)
def main(youtube_url: str, title: str, api_base: str):
    if not youtube_url.startswith("http"):
        raise click.UsageError(f"Not a URL: {youtube_url}")

    with tempfile.TemporaryDirectory(prefix="bag-soundbite-") as tmp_dir:
        click.echo(f"Downloading {youtube_url} ...")
        filepath, video_title = download(youtube_url, tmp_dir)
        final_title = title or video_title
        click.echo(f"Downloaded: {os.path.basename(filepath)}")

        click.echo(f"Uploading as {final_title!r} to {api_base} ...")
        source = upload(api_base, youtube_url, filepath, final_title)

    click.echo(
        f"Done: source #{source['source_id']} {source['title']!r} "
        f"({source['duration_ms']}ms, status={source['status']}, "
        f"thumbnail={'yes' if source.get('has_thumbnail') else 'no'})"
    )

    source_page = f"{api_base}/soundbites/admin/sources/{source['source_id']}"
    click.echo(f"Opening {source_page} ...")
    webbrowser.open(source_page)


if __name__ == "__main__":
    main()
