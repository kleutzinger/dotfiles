#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "click",
# ]
# ///

"""
Turn a clipyt.kevbot.xyz link into a standalone rendered video.

A clipyt link looks like:
    https://clipyt.kevbot.xyz/#VIDEOID+START+END+VIDEOID+START+END+...+output_name

The fragment is a '+'-joined list of (youtube_id, start_seconds, end_seconds)
triples -- possibly spanning several different video ids -- optionally
followed by a trailing name used for the output file.

Before downloading or rendering anything, this prints how many source videos
need to be fetched (and their approximate total size) plus the final
rendered runtime, and asks for confirmation.
"""

import os
import platform
import shutil
import subprocess
import sys
import tempfile
import json
from dataclasses import dataclass
from urllib.parse import urlsplit

import click

YT_DLP_CMD = ["uvx", "--no-cache", "yt-dlp"]


@dataclass
class Clip:
    video_id: str
    start: float
    end: float

    @property
    def duration(self) -> float:
        return self.end - self.start


@dataclass
class SourceVideo:
    video_id: str
    local_path: str | None = None  # set once downloaded / found locally
    title: str | None = None
    size_bytes: int | None = None  # None = unknown size
    already_local: bool = False


def is_number(s: str) -> bool:
    try:
        float(s)
        return True
    except ValueError:
        return False


def human_size(num_bytes: float | None) -> str:
    if num_bytes is None:
        return "unknown size"
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if abs(num_bytes) < 1024:
            return f"{num_bytes:.1f}{unit}"
        num_bytes /= 1024
    return f"{num_bytes:.1f}PB"


def human_duration(seconds: float) -> str:
    seconds = int(round(seconds))
    h, rem = divmod(seconds, 3600)
    m, s = divmod(rem, 60)
    if h:
        return f"{h}:{m:02d}:{s:02d}"
    return f"{m}:{s:02d}"


def parse_clipyt(url_or_fragment: str) -> tuple[list[Clip], str | None]:
    fragment = url_or_fragment
    if "#" in fragment:
        fragment = urlsplit(fragment).fragment or fragment.split("#", 1)[1]

    tokens = [t for t in fragment.split("+") if t != ""]

    clips: list[Clip] = []
    i = 0
    while i + 2 < len(tokens) and is_number(tokens[i + 1]) and is_number(tokens[i + 2]):
        clips.append(Clip(tokens[i], float(tokens[i + 1]), float(tokens[i + 2])))
        i += 3

    name = "_".join(tokens[i:]) if i < len(tokens) else None

    if not clips:
        raise click.ClickException("Couldn't find any VIDEOID+START+END triples in that link.")

    return clips, name


def find_local_file(video_id: str, search_dirs: list[str]) -> str | None:
    needle = f"[{video_id}]"
    for d in search_dirs:
        if not os.path.isdir(d):
            continue
        for entry in os.listdir(d):
            if needle in entry:
                return os.path.join(d, entry)
    return None


def probe_remote(video_id: str, format_selector: str) -> tuple[str | None, int | None]:
    """Return (title, approx_size_bytes) for the format that would be downloaded."""
    url = f"https://www.youtube.com/watch?v={video_id}"
    result = subprocess.run(
        YT_DLP_CMD + ["-f", format_selector, "--no-warnings", "-J", url],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise click.ClickException(
            f"yt-dlp failed to look up {video_id}:\n{result.stderr.strip()}"
        )
    data = json.loads(result.stdout)
    title = data.get("title")
    downloads = data.get("requested_downloads") or [data]
    size = 0
    for d in downloads:
        fs = d.get("filesize") or d.get("filesize_approx")
        if fs:
            size += fs
        else:
            return title, None
    return title, size or None


def download_video(video_id: str, format_selector: str, download_dir: str) -> str:
    url = f"https://www.youtube.com/watch?v={video_id}"
    out_template = os.path.join(download_dir, "%(title)s [%(id)s].%(ext)s")
    subprocess.run(
        YT_DLP_CMD + ["-f", format_selector, "--no-playlist", "-o", out_template, url],
        check=True,
    )
    path = find_local_file(video_id, [download_dir])
    if not path:
        raise click.ClickException(f"yt-dlp said it downloaded {video_id} but no file was found.")
    return path


def get_clipboard() -> str:
    if platform.system() == "Darwin":
        return subprocess.check_output(["pbpaste"]).decode().strip()
    return subprocess.check_output(["xsel", "-ob"]).decode().strip()


def build_filter_complex(
    clips: list[Clip],
    video_id_to_input_idx: dict[str, int],
    normalize: bool,
    width: int,
    height: int,
    fps: int,
    sample_rate: int,
) -> str:
    parts = []
    for i, clip in enumerate(clips):
        idx = video_id_to_input_idx[clip.video_id]
        v_label, a_label = f"v{i}", f"a{i}"
        v_filters = f"trim=start={clip.start}:end={clip.end},setpts=PTS-STARTPTS"
        a_filters = f"atrim=start={clip.start}:end={clip.end},asetpts=PTS-STARTPTS"
        if normalize:
            v_filters += (
                f",scale={width}:{height}:force_original_aspect_ratio=decrease,"
                f"pad={width}:{height}:(ow-iw)/2:(oh-ih)/2:color=black,setsar=1,fps={fps}"
            )
            a_filters += f",aformat=sample_rates={sample_rate}:channel_layouts=stereo"
        parts.append(f"[{idx}:v]{v_filters}[{v_label}];")
        parts.append(f"[{idx}:a]{a_filters}[{a_label}];")

    concat_inputs = "".join(f"[v{i}][a{i}]" for i in range(len(clips)))
    parts.append(f"{concat_inputs}concat=n={len(clips)}:v=1:a=1[outv][outa]")
    return "".join(parts)


@click.command()
@click.argument("clipyt_url", required=False)
@click.option("--output", "-o", default=None, help="Output file path (overrides name embedded in the link).")
@click.option(
    "--dir", "-d", "search_dirs", multiple=True, default=(".",),
    help="Directories to look for already-downloaded sources (matched by '[VIDEO_ID]' in the filename). Repeatable.",
)
@click.option(
    "--download-dir", default=None,
    help="Where to save newly downloaded sources. Defaults to the first --dir.",
)
@click.option(
    "--format", "-f", "format_selector",
    default="bestvideo[height<=1080]+bestaudio/best[height<=1080]",
    help="yt-dlp format selector for downloads.",
)
@click.option("--crf", default=18, type=int, help="x264 CRF for the final render.")
@click.option("--preset", default="medium", help="x264 preset for the final render.")
@click.option("--width", default=1920, type=int, help="Normalized width when mixing multiple source videos.")
@click.option("--height", default=1080, type=int, help="Normalized height when mixing multiple source videos.")
@click.option("--fps", default=60, type=int, help="Normalized fps when mixing multiple source videos.")
@click.option("--sample-rate", default=48000, type=int, help="Normalized audio sample rate when mixing multiple source videos.")
@click.option(
    "--keep-downloads", is_flag=True,
    help="Keep freshly-downloaded source videos (deleted by default after rendering; files that were already local are always left alone).",
)
@click.option("--push", is_flag=True, help="Upload the final render to YouTube via vodbackup.py after rendering.")
@click.option("--push-title", default=None, help="Title to pass to vodbackup.py when --push is used (defaults to the output filename).")
@click.option("--dry-run", is_flag=True, help="Only show the preprocessing summary, don't download or render.")
@click.option("--yes", "-y", is_flag=True, help="Skip the confirmation prompt.")
def main(
    clipyt_url, output, search_dirs, download_dir, format_selector,
    crf, preset, width, height, fps, sample_rate, keep_downloads, push, push_title, dry_run, yes,
):
    """Render a clipyt.kevbot.xyz link (CLIPYT_URL) into a standalone video.

    If CLIPYT_URL is omitted, it's read from the clipboard.
    """
    if not clipyt_url:
        clipyt_url = get_clipboard()
        click.echo(f"No URL given, using clipboard: {clipyt_url}")

    clips, name = parse_clipyt(clipyt_url)
    search_dirs = list(search_dirs)
    download_dir = download_dir or search_dirs[0]

    unique_ids = list(dict.fromkeys(c.video_id for c in clips))

    sources: dict[str, SourceVideo] = {}
    for vid in unique_ids:
        local = find_local_file(vid, search_dirs)
        if local:
            sources[vid] = SourceVideo(video_id=vid, local_path=local, already_local=True)
        else:
            click.echo(f"Looking up {vid}...")
            title, size = probe_remote(vid, format_selector)
            sources[vid] = SourceVideo(video_id=vid, title=title, size_bytes=size)

    to_download = [s for s in sources.values() if not s.already_local]
    already_have = [s for s in sources.values() if s.already_local]
    total_runtime = sum(c.duration for c in clips)
    known_sizes = [s.size_bytes for s in to_download if s.size_bytes is not None]
    total_size = sum(known_sizes) if known_sizes else None
    size_unknown = any(s.size_bytes is None for s in to_download)

    click.echo()
    click.echo(f"{len(clips)} clip(s) from {len(unique_ids)} source video(s):")
    for s in already_have:
        click.echo(f"  - {s.video_id}: already have {os.path.basename(s.local_path)}")
    for s in to_download:
        click.echo(f"  - {s.video_id}: will download \"{s.title}\" (~{human_size(s.size_bytes)})")

    click.echo()
    click.echo(f"Downloads needed: {len(to_download)}")
    size_str = human_size(total_size) + (" (some unknown)" if size_unknown and total_size else "")
    if not to_download:
        size_str = "0B"
    click.echo(f"Approx. total download size: {size_str}")
    click.echo(f"Final rendered runtime: {human_duration(total_runtime)} ({len(clips)} clip(s))")
    click.echo()

    if dry_run:
        return

    if not yes and not click.confirm("Proceed?", default=True):
        click.echo("Aborted.")
        return

    for s in to_download:
        click.echo(f"Downloading {s.video_id}...")
        s.local_path = download_video(s.video_id, format_selector, download_dir)

    video_id_to_input_idx = {vid: i for i, vid in enumerate(unique_ids)}
    filter_complex = build_filter_complex(
        clips, video_id_to_input_idx,
        normalize=len(unique_ids) > 1,
        width=width, height=height, fps=fps, sample_rate=sample_rate,
    )

    if output:
        output_path = output
    elif name:
        output_path = name if os.path.splitext(name)[1] else f"{name}.mp4"
    else:
        output_path = "clipyt_output.mp4"

    cmd = ["ffmpeg", "-y"]
    for vid in unique_ids:
        cmd += ["-i", sources[vid].local_path]
    cmd += [
        "-filter_complex", filter_complex,
        "-map", "[outv]", "-map", "[outa]",
        "-c:v", "libx264", "-preset", preset, "-crf", str(crf),
        "-c:a", "aac", "-b:a", "192k",
        output_path,
    ]

    click.echo("Rendering...")
    subprocess.run(cmd, check=True)
    click.echo(f"\nFinished! Output: {output_path}")

    if push:
        vodbackup_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "vodbackup.py")
        title = push_title or os.path.splitext(os.path.basename(output_path))[0]
        click.echo(f"\nPushing to YouTube via vodbackup.py (title: {title!r})...")
        subprocess.run(
            [vodbackup_path, "--local-video-file", output_path, "--title", title],
            check=True,
        )

    if not keep_downloads:
        for s in to_download:
            if s.local_path and os.path.exists(s.local_path):
                os.remove(s.local_path)


if __name__ == "__main__":
    main()
