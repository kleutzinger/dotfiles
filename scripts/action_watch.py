#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""Watch GitHub CI and send a notification when it finishes.

Accepts either:
  PR URL:      https://github.com/owner/repo/pull/123
  Run/job URL: https://github.com/owner/repo/actions/runs/123[/job/456]
               (a job URL watches only that job)

Requires the `gh` CLI to be installed and authenticated.
"""
import argparse
import json
import re
import subprocess
import sys
import time

from notify import notify

PASS = {"success", "skipped", "neutral"}


def gh(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(["gh", *args], capture_output=True, text=True)


def pr_checks(url: str) -> list[tuple[str, str]] | None:
    """[(name, state)] with state in pending/pass/fail; None if no checks yet."""
    r = gh("pr", "checks", url, "--json", "name,bucket")
    # gh exits 8 while checks are pending, so rely on stdout rather than the exit code.
    if r.stdout.strip():
        out = []
        for c in json.loads(r.stdout):
            b = c["bucket"]
            out.append((c["name"], "pending" if b == "pending" else "pass" if b in ("pass", "skipping") else "fail"))
        return out
    if "no checks reported" in r.stderr:
        return None
    sys.exit(f"gh failed: {r.stderr.strip()}")


def run_jobs(repo: str, run_id: str, job_id: str | None) -> list[tuple[str, str]]:
    r = gh("run", "view", run_id, "--repo", repo, "--json", "jobs")
    if r.returncode:
        sys.exit(f"gh failed: {r.stderr.strip()}")
    jobs = json.loads(r.stdout)["jobs"]
    if job_id:
        jobs = [j for j in jobs if str(j["databaseId"]) == job_id]
        if not jobs:
            sys.exit(f"job {job_id} not found in run {run_id}")
    return [
        (j["name"], "pending" if j["status"] != "completed" else "pass" if j["conclusion"] in PASS else "fail")
        for j in jobs
    ]


def main() -> None:
    p = argparse.ArgumentParser(description="Notify when GitHub CI finishes.")
    p.add_argument("url", help="PR URL or Actions run/job URL")
    p.add_argument("-i", "--interval", type=int, default=20, help="poll seconds (default 20)")
    args = p.parse_args()

    if m := re.match(r"https://github\.com/([^/]+/[^/]+)/actions/runs/(\d+)(?:/job/(\d+))?", args.url):
        repo, run_id, job_id = m.groups()
        label = f"{repo} run {run_id}" + (f" job {job_id}" if job_id else "")
        fetch = lambda: run_jobs(repo, run_id, job_id)  # noqa: E731
    elif m := re.match(r"https://github\.com/([^/]+/[^/]+)/pull/(\d+)", args.url):
        label = f"{m[1]}#{m[2]}"
        pr_url = m[0]
        fetch = lambda: pr_checks(pr_url)  # noqa: E731
    else:
        sys.exit("Unrecognized URL; expected a /pull/N or /actions/runs/N URL")

    print(f"Watching {label} ...")
    while True:
        checks = fetch()
        if checks and all(s != "pending" for _, s in checks):
            break
        n = sum(s == "pending" for _, s in checks or [])
        print(f"  {time.strftime('%H:%M:%S')} " + (f"pending: {n}" if checks else "waiting for checks to appear"))
        time.sleep(args.interval)

    failed = [n for n, s in checks if s == "fail"]
    if failed:
        title, msg = f"CI failed: {label}", f"{len(failed)} failing: {', '.join(failed)}"
    else:
        title, msg = f"CI passed: {label}", f"{len(checks)} checks finished"
    print(f"{title}\n{msg}")
    notify(title, msg)
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
