#!/usr/bin/env -S uv run --script --with click,pillow,b2sdk

"""
take an image as a path via click
make it a large thumbnail size while keeping the aspect ratio
upload it to a specific path in  backblaze, return the url

usage:
    backblaze-upload.py image.jpg
"""

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
UPLOAD_PATH_PREFIX = "screenshots/"
CDN_PREFIX = "https://cdn.kevbot.xyz/file/"


@click.command()
@click.argument("image_path", type=click.Path(exists=True))
def upload_thumbnail(image_path):
    # Resize image
    original_size = os.path.getsize(image_path)
    click.echo(f"Original size: {original_size / 1024:.2f} KB")
    with Image.open(image_path) as img:
        img.thumbnail((800, 800))  # medium thumbnail
        buffer = BytesIO()
        img.save(buffer, format="JPEG")
        new_size = buffer.tell()
        buffer.seek(0)

    # Connect to B2
    info = InMemoryAccountInfo()
    b2_api = B2Api(info)
    b2_api.authorize_account("production", B2_APPLICATION_KEY_ID, B2_APPLICATION_KEY)
    bucket = b2_api.get_bucket_by_name(B2_BUCKET_NAME)

    # Upload file
    filename = os.path.basename(image_path)
    # replace file extension if present with jpg
    if not filename.endswith(".jpg"):
        filename = os.path.splitext(filename)[0] + ".jpg"
    filename = f"{int(time.time())}_{filename}"
    b2_path = UPLOAD_PATH_PREFIX + filename
    file_info = {"Content-Type": "image/jpeg"}

    b2_file = bucket.upload_bytes(buffer.read(), b2_path, file_info=file_info)

    public_url = f"{CDN_PREFIX}{B2_BUCKET_NAME}/{b2_path}"
    click.echo(f"new size: {new_size / 1024:.2f} KB")
    click.echo(f"Uploaded to:\n\t{public_url}")


if __name__ == "__main__":
    upload_thumbnail()
