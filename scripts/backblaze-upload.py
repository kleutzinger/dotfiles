#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.13"
# dependencies = [
#     "click",
#     "pillow",
#     "b2sdk",
#     "tqdm",
# ]
# ///

"""
upload a file to backblaze and return its public (unlisted) url.

by default any file is uploaded as-is under files/, with a timestamp
prefix to avoid collisions. pass --screenshot to instead resize an
image to a large thumbnail, convert it to JPEG, and upload it under
screenshots/.

usage:
    backblaze-upload.py report.json
    backblaze-upload.py image.jpg --screenshot
    backblaze-upload.py secret.pdf --private --expires 2

--private uploads to the bucket named by B2_PRIVATE_BUCKET_NAME (which must
be a private bucket) and prints a signed URL that expires after --expires
hours (default 24, max 168). Add --no-link to skip the signed URL and just
print the uploaded file's bucket path.
"""

import mimetypes
import re
import time

import click
from PIL import Image
from io import BytesIO
from b2sdk.v2 import InMemoryAccountInfo, B2Api, TqdmProgressListener
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
@click.option("--private", is_flag=True, help="Upload to the private bucket (B2_PRIVATE_BUCKET_NAME) and print a time-limited signed URL")
@click.option("--expires", default=24, show_default=True, type=click.IntRange(1, 168), help="Signed URL lifetime in hours (max 168 = 7 days). Only used with --private")
@click.option("--no-link", is_flag=True, help="With --private, don't create a signed URL; just print the uploaded path")
def upload(file_path, screenshot, private, expires, no_link):
    bucket_name = B2_BUCKET_NAME
    if private:
        bucket_name = os.getenv("B2_PRIVATE_BUCKET_NAME")
        if not bucket_name:
            raise click.UsageError("--private requires the B2_PRIVATE_BUCKET_NAME env var")

    # Connect to B2
    info = InMemoryAccountInfo()
    b2_api = B2Api(info)
    b2_api.authorize_account("production", B2_APPLICATION_KEY_ID, B2_APPLICATION_KEY)
    bucket = b2_api.get_bucket_by_name(bucket_name)

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
        # streams from disk and switches to multipart for large files
        size = os.path.getsize(file_path)
        click.echo(f"Uploading {size / 1024 / 1024:.1f} MB to {bucket_name}/{b2_path}", err=True)
        bucket.upload_local_file(
            local_file=file_path,
            file_name=b2_path,
            content_type=content_type,
            progress_listener=TqdmProgressListener(filename),
        )

    if private and no_link:
        click.echo(f"Uploaded privately to {bucket_name}/{b2_path}")
        return

    if private:
        # Signed URL via B2's native download host (the public CDN doesn't
        # forward the auth token). The application key needs shareFiles.
        token = bucket.get_download_authorization(b2_path, expires * 3600)
        signed_url = f"{bucket.get_download_url(b2_path)}?Authorization={token}"
        click.echo(f"Uploaded privately. Link expires in {expires}h:\n\n{signed_url}")
        return

    public_url = f"{CDN_PREFIX}{bucket_name}/{b2_path}"
    click.echo(f"Uploaded to:\n\n{public_url}")


if __name__ == "__main__":
    upload()
