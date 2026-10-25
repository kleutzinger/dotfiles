#!/usr/bin/env -S uv run --script --with click

"""
List running vodbackup.py jobs and optionally kill them.

usage: vodjobs.py            list jobs
       vodjobs.py kill       list jobs, then ask which to kill
       vodjobs.py kill 1 3   kill jobs 1 and 3
       vodjobs.py kill all   kill every job
Killing stops the job's whole pipeline (yt-dlp, ffmpeg, youtubeuploader).
"""

import os
import shlex
import signal
import subprocess
import time
from dataclasses import dataclass

import click


@dataclass
class Proc:
    pid: int
    ppid: int
    etime: str
    command: str


def all_procs() -> dict[int, Proc]:
    out = subprocess.run(
        ["ps", "-axo", "pid=,ppid=,etime=,command="], capture_output=True, text=True
    ).stdout
    procs = {}
    for line in out.splitlines():
        pid, ppid, etime, command = line.split(None, 3)
        procs[int(pid)] = Proc(int(pid), int(ppid), etime, command)
    return procs


def descendants(procs: dict[int, Proc], pid: int) -> list[int]:
    found = []
    for p in procs.values():
        if p.ppid == pid:
            found.append(p.pid)
            found.extend(descendants(procs, p.pid))
    return found


def find_jobs() -> list[Proc]:
    """Top-level vodbackup.py processes (not their uv wrappers' children or this script)"""
    procs = all_procs()
    me = os.getpid()
    matches = {
        p.pid: p
        for p in procs.values()
        if "vodbackup.py" in p.command and "vodjobs.py" not in p.command and p.pid != me
    }
    return sorted(
        (p for p in matches.values() if p.ppid not in matches), key=lambda p: p.pid
    )


def describe(job: Proc) -> str:
    try:
        args = shlex.split(job.command)
    except ValueError:
        args = job.command.split()
    title = next((args[i + 1] for i, a in enumerate(args[:-1]) if a in ("-t", "--title")), None)
    source = next((a for a in reversed(args) if a.startswith("http")), None)
    return f"{title or '(untitled)'}  {source or ''}".strip()


def show(jobs: list[Proc]) -> None:
    for i, job in enumerate(jobs, 1):
        click.echo(f"{i}. pid {job.pid}  running {job.etime}  {describe(job)}")


def kill_job(job: Proc) -> None:
    pids = [*descendants(all_procs(), job.pid), job.pid]
    for pid in pids:
        try:
            os.kill(pid, signal.SIGTERM)
        except ProcessLookupError:
            pass
    time.sleep(2)
    for pid in pids:
        try:
            os.kill(pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
    click.echo(f"Killed job pid {job.pid} ({len(pids)} processes)")


@click.group(invoke_without_command=True)
@click.pass_context
def cli(ctx):
    if ctx.invoked_subcommand:
        return
    jobs = find_jobs()
    if not jobs:
        click.echo("No vodbackup jobs running")
    show(jobs)


@cli.command()
@click.argument("targets", nargs=-1)
def kill(targets):
    """Kill jobs by number from the list, or 'all'"""
    jobs = find_jobs()
    if not jobs:
        click.echo("No vodbackup jobs running")
        return
    show(jobs)
    if not targets:
        targets = tuple(click.prompt("\nKill which? (numbers or 'all')").split())
    if "all" in targets:
        chosen = jobs
    else:
        try:
            chosen = [jobs[int(t) - 1] for t in targets if int(t) >= 1]
        except (ValueError, IndexError):
            raise click.ClickException(f"Pick numbers between 1 and {len(jobs)}, or 'all'")
    for job in chosen:
        kill_job(job)


if __name__ == "__main__":
    cli()
