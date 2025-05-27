#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.9"
# dependencies = [
#     "pocketbase",
#     "diskcache",
#     "click",
#     "shortuuid"
# ]
# ///

import json
import os
import sys
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
import time
import concurrent.futures
from shortuuid import uuid

# Third-party imports (inline dependencies managed by uv)
import click
from pocketbase import PocketBase
from pocketbase.client import FileUpload
import diskcache as dc

# Initialize cache
cache = dc.Cache("/tmp/coconut-cache")

# Environment variables
POCKETBASE_URL = os.environ.get("POCKETBASE_URL")
POCKETBASE_USERNAME = os.environ.get("POCKETBASE_USERNAME")
POCKETBASE_PASSWORD = os.environ.get("POCKETBASE_PASSWORD")

# Initialize PocketBase client
pb = PocketBase(POCKETBASE_URL)


def relative_time(date: datetime) -> str:
    """Convert datetime to relative time string (e.g. 1 year, 2 months, 3 days, 4 hours ago)"""
    now = datetime.now()
    elapsed = now - date

    units = [
        {"label": "year", "seconds": 365 * 24 * 60 * 60},
        {"label": "month", "seconds": 30 * 24 * 60 * 60},
        {"label": "day", "seconds": 24 * 60 * 60},
        {"label": "hour", "seconds": 60 * 60},
    ]

    result = []
    remaining_seconds = elapsed.total_seconds()

    for unit in units:
        unit_time = int(remaining_seconds // unit["seconds"])
        if unit_time > 0:
            plural = "s" if unit_time > 1 else ""
            result.append(f"{unit_time} {unit['label']}{plural}")
            remaining_seconds -= unit_time * unit["seconds"]

    if not result:
        return "0 hours ago"

    return ", ".join(result) + " ago"


def hours_ago(date: datetime) -> str:
    """Convert datetime to hours ago format"""
    now = datetime.now()
    elapsed = now - date
    hours = int(elapsed.total_seconds() // 3600)
    return f"{hours}hr"


# Equivalent paths across different machines
EQUIV_PATH_ARR = [
    os.path.expanduser("~"),
    "/home/kevin",
    "/Volumes/orico",
    "/run/media/kevin/orico",
    "/run/media/kevin/tosh",
    "/Users/kevin",
]


def concurrent_path_finder(records: List[Any]) -> List[Dict]:
    """Find existing paths for records concurrently"""
    path_map = {}
    unique_paths = set(record.path for record in records)

    def resolve_path(original_path: str) -> Dict[str, Any]:
        if original_path in path_map:
            return path_map[original_path]

        if os.path.exists(original_path):
            result = {"path": original_path, "exists": True}
            path_map[original_path] = result
            return result

        # Find present prefix
        present_prefix = None
        for prefix in EQUIV_PATH_ARR:
            if original_path.startswith(prefix):
                present_prefix = prefix
                break

        if present_prefix:
            for equivalent_path in EQUIV_PATH_ARR:
                new_path = original_path.replace(present_prefix, equivalent_path, 1)
                if os.path.exists(new_path):
                    result = {"path": new_path, "exists": True}
                    path_map[original_path] = result
                    return result

        result = {"path": original_path, "exists": False}
        path_map[original_path] = result
        return result

    # Process paths concurrently using threading for I/O operations
    with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
        futures = {executor.submit(resolve_path, path): path for path in unique_paths}
        for future in concurrent.futures.as_completed(futures):
            future.result()  # Ensure all complete

    # Update records with resolved paths
    updated_records = []
    for record in records:
        resolved = path_map[record.path]
        # Convert record to dict and merge with resolved path info
        record_dict = {
            "id": record.id,
            "created": record.created,
            "updated": record.updated,
            "path": record.path,
            "hostname": record.hostname,
            "sec": record.sec,
            "image": record.image,
            "imageUrl": getattr(record, "imageUrl", None),
            "timeAgo": getattr(record, "timeAgo", None),
            **resolved,
        }
        updated_records.append(record_dict)

    return updated_records


def hhmmss_to_sec(time_str: str) -> int:
    """Convert time string (hh:mm:ss, mm:ss, or ss) to seconds"""
    time_str = time_str.replace(".", ":")
    parts = [int(x) for x in time_str.split(":")]

    total_seconds = 0
    for part in parts:
        total_seconds = total_seconds * 60 + part

    return total_seconds


def run_command(cmd: List[str], capture: bool = True) -> str:
    """Run shell command and return output"""
    if capture:
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            raise subprocess.CalledProcessError(result.returncode, cmd, result.stderr)
        return result.stdout.strip()
    else:
        # Run without capturing output to allow terminal interaction
        result = subprocess.run(cmd)
        if result.returncode != 0:
            raise subprocess.CalledProcessError(result.returncode, cmd)
        return ""


def countdown_clear(seconds: int):
    """Countdown and clear screen"""
    print(f"clearing in {seconds} seconds...")
    for i in range(seconds, 0, -1):
        print(f"{i} ", end="", flush=True)
        time.sleep(1)
    run_command(["clear"])


def list_coconuts():
    """List all coconut records"""
    # Authenticate with PocketBase
    pb.collection("users").auth_with_password(POCKETBASE_USERNAME, POCKETBASE_PASSWORD)

    records = pb.collection("coconuts").get_full_list()

    # Add imageUrl to each record
    for record in records:
        record_id = record.id
        updated = record.updated
        key = f"{record_id}-{updated}-imageUrl"

        if key in cache:
            record.imageUrl = cache[key]
        else:
            record.imageUrl = pb.files.get_url(record, record.image)
            cache[key] = record.imageUrl

        # Handle datetime - could be string or datetime object
        if isinstance(record.created, str):
            created_datetime = datetime.fromisoformat(
                record.created.replace(".000Z", "").replace("Z", "+00:00")
            )
        else:
            created_datetime = record.created

        record.timeAgo = (
            f"({hours_ago(created_datetime)}) {relative_time(created_datetime)}"
        )

    resolved_records = sorted(
        concurrent_path_finder(records), key=lambda x: x["created"]
    )
    print(json.dumps(resolved_records, indent=2, default=str))


def create_coconut(sec: Optional[int] = None):
    """Create a new coconut record"""
    # Authenticate with PocketBase
    pb.collection("users").auth_with_password(POCKETBASE_USERNAME, POCKETBASE_PASSWORD)

    # Get hostname
    hostname = run_command(["hostname"])

    # Get recent played VLC data
    vlc_data = run_command(["fish", "-c", "recent_played_vlc.py --json"])
    data = json.loads(vlc_data)
    uri = data["uri"]
    vlc_sec = data["sec"]
    path = data["path"]
    duration = data["duration"]

    # Use provided sec value if given, otherwise use VLC's position
    sec_value = sec if sec is not None else vlc_sec

    seek_to = f"00:00:{sec_value}" if sec_value > 0 else "30%"

    def generate_and_select_thumbnail(path: str, seek_to: str) -> str:
        """Generate multiple thumbnails and let user select one.
        Returns the path to the selected thumbnail."""
        while True:
            # Create multiple thumbnails at different positions
            thumbnail_paths = []
            seek_positions = []

            # Calculate 5 positions around the seek point plus quarter marks
            base_sec = int(seek_to[6:]) if seek_to.startswith("00:00:") else 30
            offsets = [-10, -5, 0, 5, 10]

            # Add positions around the seek point
            for offset in offsets:
                pos_sec = max(0, base_sec + offset)
                seek_positions.append(f"00:00:{pos_sec}")

            # Add quarter mark positions
            duration_sec = int(duration)
            quarter_positions = [
                int(duration_sec * 0.25),
                int(duration_sec * 0.5),
                int(duration_sec * 0.75),
            ]
            for pos_sec in quarter_positions:
                seek_positions.append(f"00:00:{pos_sec}")
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            temp_dir = f"/tmp/thumb-{timestamp}-{uuid()}"
            os.makedirs(temp_dir, exist_ok=True)
            # Generate thumbnails
            for pos in seek_positions:
                thumb_path = f"{temp_dir}/{uuid()}.jpg"
                thumbnail_paths.append(thumb_path)
                run_command(
                    [
                        "ffmpegthumbnailer",
                        f"-t{pos}",
                        "-s512",
                        "-i",
                        path,
                        "-o",
                        thumb_path,
                    ]
                )

            # Let user select preferred thumbnail
            selector_args = ["image_selector.py"] + thumbnail_paths
            selected_path = run_command(selector_args, capture=True).strip()

            # Show selected thumbnail
            print(f"Selected: timg '{selected_path}'")
            print(f"temp_dir: {temp_dir}")
            run_command(["timg", selected_path], capture=False)
            return selected_path

    # Get thumbnail using the new function
    thumbnail_path = generate_and_select_thumbnail(path, seek_to)

    # Prepare upload data

    # Upload to PocketBase
    with open(thumbnail_path, "rb") as f:
        to_upload = {
            "path": path,
            "hostname": hostname,
            "sec": sec_value,
            "image": FileUpload((os.path.basename(thumbnail_path), f)),
        }

        print(to_upload)
        print("upload? ctrl+c to cancel")
        countdown_clear(5)
        out = pb.collection("coconuts").create(to_upload)
        print("upload complete")
        print(out.path)
        countdown_clear(5)

    # Clean up thumbnail
    try:
        os.unlink(thumbnail_path)
    except OSError:
        pass


@click.group(invoke_without_command=True)
@click.pass_context
@click.option("--sec", help="Timestamp in format hh:mm:ss, mm:ss, or ss (also accepts 5.02 for 5:02)")
def cli(ctx, sec):
    """Coconut media thumbnail manager"""
    if ctx.invoked_subcommand is None:
        # Default behavior - create coconut
        # Convert sec to integer if provided
        sec_value = hhmmss_to_sec(sec) if sec else None
        create_coconut(sec_value)


@cli.command()
def list():
    """List all coconut records"""
    list_coconuts()


if __name__ == "__main__":
    cli()
