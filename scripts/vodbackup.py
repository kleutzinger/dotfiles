#!/usr/bin/env -S uv run --script --with click

"""
https://github.com/porjo/youtubeuploader

usage: vodbackup.py <URL>
where URL is the URL of the video to download, usually a twitch VOD.
"""

import subprocess
import os
import click
import math
import sys
from datetime import datetime


CLIENT_SECRETS_PATH = os.path.join(
    os.path.expanduser("~"), ".config/youtubeuploader/client_secrets.json"
)
CLIENT_TOKEN_PATH = os.path.join(
    os.path.expanduser("~"), ".config/youtubeuploader/request.token"
)

assert os.path.exists(CLIENT_SECRETS_PATH), f"File not found: {CLIENT_SECRETS_PATH}"
assert os.path.exists(CLIENT_TOKEN_PATH), f"File not found: {CLIENT_TOKEN_PATH}"

# YouTube rejects videos over 12 hours; leave some slack for keyframe-aligned cuts
MAX_PART_SECONDS = 11 * 3600 + 55 * 60
YOUTUBE_MAX_TITLE = 100


def parse_seconds(value: str) -> float | None:
    try:
        return float(value)
    except ValueError:
        return None


def probe_format(path: str, field: str) -> float | None:
    result = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", f"format={field}", "-of", "csv=p=0", path],
        capture_output=True,
        text=True,
    )
    return parse_seconds(result.stdout.strip())


def probe_duration(path: str) -> float | None:
    return probe_format(path, "duration")


def format_seconds(seconds: float) -> str:
    seconds = int(seconds)
    return f"{seconds // 3600}h{seconds // 60 % 60:02d}m"


def parse_time(value: str) -> float:
    """Parse seconds, M:SS or H:MM:SS"""
    seconds = 0.0
    for piece in value.split(":"):
        seconds = seconds * 60 + float(piece)
    return seconds


def parse_skips(ctx, param, values) -> list[tuple[float, float]]:
    skips = []
    for value in values:
        try:
            start, end = (parse_time(v) for v in value.split("-"))
        except ValueError:
            raise click.BadParameter(
                f"{value!r} should look like START-END, e.g. 2:10:00-2:45:30"
            )
        if end <= start:
            raise click.BadParameter(f"{value!r} ends before it starts")
        skips.append((start, end))
    return sorted(skips)


def kept_segments(duration: float, skips) -> list[tuple[float, float]]:
    """The ranges of the original video left after removing the skips"""
    segments, pos = [], 0.0
    for start, end in skips:
        if start > pos:
            segments.append((pos, min(start, duration)))
        pos = max(pos, end)
    if pos < duration:
        segments.append((pos, duration))
    return segments


def slice_segments(segments, start: float, end: float) -> list[tuple[float, float]]:
    """Original-time ranges covering [start, end) of the video once skips are removed"""
    ranges, offset = [], 0.0
    for seg_start, seg_end in segments:
        seg_len = seg_end - seg_start
        lo, hi = max(start - offset, 0), min(end - offset, seg_len)
        if lo < hi:
            ranges.append((seg_start + lo, seg_start + hi))
        offset += seg_len
    return ranges


def concat_list(source: str, ranges, start_time: float) -> str:
    """An ffconcat script that plays the given ranges of source back to back"""
    quoted = "'" + source.replace("'", "'\\''") + "'"
    lines = ["ffconcat version 1.0"]
    for start, end in ranges:
        # inpoint/outpoint are stream timestamps, which don't start at 0 (~62s on Twitch)
        lines.append(f"file {quoted}")
        if start > 0:
            # Seeking to the very first timestamp fails, so only seek when needed
            lines.append(f"inpoint {start + start_time:.3f}")
        lines.append(f"outpoint {end + start_time:.3f}")
    return "\n".join(lines) + "\n"


@click.command()
@click.argument("url_or_path", required=False)
@click.option(
    "--cleanup", "-c", is_flag=True, help="Delete the downloaded file after uploading"
)
# add an option to specify bracket-url
@click.option(
    "-b",
    "--bracket-url",
    help="Bracket URL to use for the upload, if not specified, will use the default bracket URL",
)
# add a --title
@click.option(
    "-t",
    "--title",
    help="Specify the title of the video",
)
@click.option(
    "-d",
    "--description",
    help="Additional text to append to the description",
)
@click.option(
    "-l",
    "--local-video-file",
    type=click.Path(exists=True, dir_okay=False),
    help="Path to a local video file to upload, instead of URL_OR_PATH",
)
@click.option(
    "-s",
    "--stream/--no-stream",
    default=True,
    help="Pipe yt-dlp straight into youtubeuploader without saving to disk (default: on for URLs; local files are always uploaded directly)",
)
@click.option(
    "--skip",
    "skips",
    multiple=True,
    callback=parse_skips,
    metavar="START-END",
    help="Cut out a section, e.g. --skip 2:10:00-2:45:30. Can be given more than once",
)
@click.option(
    "--background",
    is_flag=True,
    help="Detach and keep running after the terminal closes, logging to ~/.local/state/vodbackup/",
)
def main(
    url_or_path: str = None,
    cleanup: bool = False,
    bracket_url: str = "",
    title: str = "",
    description: str = "",
    local_video_file: str = None,
    stream: bool = False,
    background: bool = False,
    skips: list[tuple[float, float]] = (),
):
    if not url_or_path and not local_video_file:
        raise click.UsageError("Provide either URL_OR_PATH or --local-video-file")
    if url_or_path and local_video_file:
        raise click.UsageError("Provide only one of URL_OR_PATH or --local-video-file")
    if local_video_file or os.path.exists(url_or_path):
        stream = False
    if background:
        # Re-run this script detached in its own session so it survives SSH hangups
        log_dir = os.path.expanduser("~/.local/state/vodbackup")
        os.makedirs(log_dir, exist_ok=True)
        log_path = os.path.join(
            log_dir, f"{datetime.now():%Y%m%d-%H%M%S}-{os.getpid()}.log"
        )
        args = [a for a in sys.argv[1:] if a != "--background"]
        with open(log_path, "w") as log:
            proc = subprocess.Popen(
                [sys.executable, os.path.abspath(__file__), *args],
                stdin=subprocess.DEVNULL,
                stdout=log,
                stderr=subprocess.STDOUT,
                start_new_session=True,
                env={**os.environ, "PYTHONUNBUFFERED": "1"},
            )
        print(f"Running in background (pid {proc.pid}). Follow output with:")
        print(f"  tail -f {log_path}")
        return
    yt_dlp = ["uvx", "--no-cache", "yt-dlp"]
    video_file = None
    original_title = None
    is_url = bool(url_or_path) and not os.path.exists(url_or_path)
    # check if url is a local absolute path that exists
    if local_video_file:
        video_file = local_video_file
    elif os.path.exists(url_or_path):
        video_file = os.path.basename(url_or_path)
    elif not stream:
        # Use yt-dlp to download and print the output filename
        result = subprocess.run(
            [*yt_dlp, "--print", "title", "--print", "after_move:filepath", url_or_path],
            capture_output=True,
            text=True,
        )
        lines = result.stdout.strip().splitlines()
        downloaded_file = lines[-1] if lines else None
        original_title = lines[0] if len(lines) > 1 else None
        if not downloaded_file or not os.path.exists(downloaded_file):
            print("Error: No file was downloaded.")
            return
        video_file = downloaded_file

    if video_file:
        duration = probe_duration(video_file)
        title = title or os.path.basename(video_file)
    else:
        info = subprocess.run(
            [*yt_dlp, "--print", "duration", "--print", "title", url_or_path],
            capture_output=True,
            text=True,
        ).stdout.splitlines()
        duration = parse_seconds(info[0]) if info else None
        original_title = info[1] if len(info) > 1 else None
        title = title or original_title or url_or_path

    if duration is None:
        if skips:
            raise click.ClickException("Couldn't determine the video length, so --skip can't be used")
        print("Warning: couldn't determine the video length. YouTube rejects videos over 12 hours.")
        segments = None
        num_parts = 1
    else:
        segments = kept_segments(duration, skips)
        kept = sum(end - start for start, end in segments)
        if skips:
            print(
                f"Skipping {format_seconds(duration - kept)} of {format_seconds(duration)}, "
                f"leaving {format_seconds(kept)}"
            )
        num_parts = math.ceil(kept / MAX_PART_SECONDS)
        part_len = kept / num_parts
        if num_parts > 1:
            print(
                f"{format_seconds(kept)} is over YouTube's 12 hour limit. "
                f"Uploading in {num_parts} parts of about {format_seconds(part_len)}."
            )

    description_text = "Find all my vods at https://vods.kevbot.xyz"
    if bracket_url:
        description_text += f"\nBracket URL: {bracket_url}"
    if is_url:
        description_text += f"\nOriginal video: {original_title or url_or_path}\n{url_or_path}"
    if description:
        description_text += "\n" + description
    sanitized_title = "".join(
        [
            c
            for c in title
            if c.isalnum() or c in [" ", "-", "_", ".", "$", "@", "[", "]"]
        ]
    )

    all_ok = True
    for i in range(num_parts):
        suffix = f" [Part {i + 1} of {num_parts}]" if num_parts > 1 else ""
        part_title = sanitized_title[: YOUTUBE_MAX_TITLE - len(suffix)] + suffix
        # Each part is piped from a producer process; a whole local file is uploaded directly
        ranges = (
            slice_segments(segments, i * part_len, (i + 1) * part_len)
            if segments and (skips or num_parts > 1)
            else None
        )
        concat_script = None
        if not ranges:
            # Video goes yt-dlp stdout -> youtubeuploader stdin, never touching disk
            producer_cmd = None if video_file else [*yt_dlp, "-o", "-", url_or_path]
        elif len(ranges) == 1 and video_file:
            (start, end), = ranges
            producer_cmd = [
                "ffmpeg", "-v", "error",
                "-ss", f"{start:.3f}", "-t", f"{end - start:.3f}",
                "-i", video_file,
                "-c", "copy", "-f", "mpegts", "-",
            ]
        elif len(ranges) == 1:
            (start, end), = ranges
            section_end = "inf" if end >= duration else f"{end:.3f}"
            producer_cmd = [
                *yt_dlp,
                "--download-sections", f"*{start:.3f}-{section_end}",
                "-o", "-",
                url_or_path,
            ]
        else:
            # Join the ranges on either side of a skip with ffmpeg's concat demuxer
            if video_file:
                # Explicit protocol, or ffmpeg resolves it relative to the stdin pipe
                source = "file:" + os.path.abspath(video_file)
            else:
                media_urls = subprocess.run(
                    [*yt_dlp, "-f", "b", "-g", url_or_path],
                    capture_output=True,
                    text=True,
                ).stdout.split()
                if len(media_urls) != 1:
                    raise click.ClickException(
                        "--skip needs a single combined audio+video stream, which this site doesn't provide. Try --no-stream"
                    )
                source = media_urls[0]
            # Fed on stdin rather than a temp file, which a snap-confined ffmpeg can't read
            concat_script = concat_list(
                source, ranges, probe_format(source, "start_time") or 0.0
            )
            producer_cmd = [
                "ffmpeg", "-v", "error",
                "-f", "concat", "-safe", "0",
                "-protocol_whitelist", "fd,pipe,file,http,https,tcp,tls,crypto,hls",
                "-i", "-",
                "-c", "copy", "-f", "mpegts", "-",
            ]
        if ranges:
            print(
                "Sections:",
                ", ".join(f"{format_seconds(a)}-{format_seconds(b)}" for a, b in ranges),
            )
        print("Uploading to youtube", part_title)
        producer = (
            subprocess.Popen(
                producer_cmd,
                stdin=subprocess.PIPE if concat_script else None,
                stdout=subprocess.PIPE,
            )
            if producer_cmd
            else None
        )
        if concat_script:
            producer.stdin.write(concat_script.encode())
            producer.stdin.close()
        # todo: install inline somehow
        upload = subprocess.run(
            [
                "youtubeuploader",
                "-secrets",
                CLIENT_SECRETS_PATH,
                "-cache",
                CLIENT_TOKEN_PATH,
                "-filename",
                "-" if producer else video_file,
                "-privacy",
                "unlisted",
                "-description",
                description_text,
                "-title",
                part_title,
            ],
            stdin=producer.stdout if producer else None,
        )
        if producer:
            producer.stdout.close()
            if producer.wait() != 0:
                name = "ffmpeg" if producer_cmd[0] == "ffmpeg" else "yt-dlp"
                print(f"Warning: {name} exited with an error, {part_title} may be incomplete")
                all_ok = False
        if upload.returncode != 0:
            print(f"Error: upload of {part_title} failed")
            all_ok = False

    if cleanup and video_file:
        if not all_ok:
            print(f"Keeping {video_file} because an upload failed")
            return
        try:
            os.remove(video_file)
            print(f"Deleted {video_file}")
        except Exception as e:
            print(f"Warning: could not delete {video_file}: {e}")

if __name__ == "__main__":
    main()
