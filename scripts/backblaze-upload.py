#!/usr/bin/env -S uv run --script --with click,pillow,b2sdk

"""
upload a file to backblaze and return its public (unlisted) url.

by default any file is uploaded as-is under files/, with a timestamp
prefix to avoid collisions. pass --screenshot to instead resize an
image to a large thumbnail, convert it to JPEG, and upload it under
screenshots/.

usage:
    backblaze-upload.py report.json
    backblaze-upload.py image.jpg --screenshot
"""

import mimetypes
import re
import time

import click
from PIL import Image
from io import BytesIO
from b2sdk.v2 import InMemoryAccountInfo, B2Api
import os

# Configuration (replace these with your real credentials or load from env)
B2_APPLICATION_KEY_ID = os.getenv("B2_APPLICATION_KEY_ID")
B2_APPLICATION_KEY = os.getenv("B2_APPLICATION_KEY")
B2_BUCKET_NAME = os.getenv("B2_BUCKET_NAME")
CDN_PREFIX = "https://cdn.kevbot.xyz/file/"


def make_url_safe(filename):
    name, ext = os.path.splitext(filename)
    name = re.sub(r"[^\w\-]", "_", name)
    return name + ext


@click.command()
@click.argument("file_path", type=click.Path(exists=True))
@click.option("--screenshot", is_flag=True, help="Resize to 800x800, convert to JPEG, and upload under screenshots/")
def upload(file_path, screenshot):
    # Connect to B2
    info = InMemoryAccountInfo()
    b2_api = B2Api(info)
    b2_api.authorize_account("production", B2_APPLICATION_KEY_ID, B2_APPLICATION_KEY)
    bucket = b2_api.get_bucket_by_name(B2_BUCKET_NAME)

    if screenshot:
        original_size = os.path.getsize(file_path)
        click.echo(f"Original size: {original_size / 1024:.2f} KB")
        with Image.open(file_path) as img:
            img.thumbnail((800, 800))
            if img.mode in ("RGBA", "P"):
                img = img.convert("RGB")
            buffer = BytesIO()
            img.save(buffer, format="JPEG")
            new_size = buffer.tell()
            buffer.seek(0)

        filename = os.path.basename(file_path)
        filename = os.path.splitext(filename)[0] + ".jpg"
        filename = f"{int(time.time())}_{filename}"
        b2_path = "screenshots/" + filename
        file_info = {"Content-Type": "image/jpeg"}
        bucket.upload_bytes(buffer.read(), b2_path, file_info=file_info)
        click.echo(f"new size: {new_size / 1024:.2f} KB")
    else:
        filename = make_url_safe(os.path.basename(file_path))
        filename = f"{int(time.time())}_{filename}"
        b2_path = "files/" + filename
        content_type, _ = mimetypes.guess_type(filename)
        file_info = {"Content-Type": content_type} if content_type else {}
        with open(file_path, "rb") as f:
            data = f.read()
        bucket.upload_bytes(data, b2_path, file_info=file_info)

    public_url = f"{CDN_PREFIX}{B2_BUCKET_NAME}/{b2_path}"
    click.echo(f"Uploaded to:\n\n{public_url}")


if __name__ == "__main__":
    upload()
