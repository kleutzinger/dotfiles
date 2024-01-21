#!/usr/bin/env python3
"""
Clone from github, except it'll use my personal account credentials instead
this lets me commit / push stuff as my personal acct when i'm on my work computer.

USAGE:
```
python clone_personal.py # clone inside some git folder
python clone_personal.py 'https://github.com/kleutzinger/url-shorten-dokku'
```

Now I can commit and push as https://github.com/kleutzinger/ rather than my work acct
"""

import contextlib
import os
import subprocess
import sys

GITHUB_NAME = "Kevin Leutzinger"
GITHUB_EMAIL = "6435727+kleutzinger@users.noreply.github.com"
EXAMPLE_URL = "https://github.com/kleutzinger/invidious-redirect"
EXAMPLE_URL_SSH = "git@github.com:kleutzinger/invidious-redirect.git"



def to_ssh(url: str, hostname="") -> str:
    url = url.replace("https://github.com/", "git@github.com:")
    if not url.endswith(".git"):
        url += ".git"
    return url


def clone(repo_url: str) -> str:
    "clone a git repo. return string of directory"
    dirs_before_clone = set(next(os.walk("."))[1])
    if repo_url.startswith("http"):
        # we want to clone ssh if possible
        repo_url = to_ssh(repo_url)
    cmd = ["git", "clone", repo_url]
    o = subprocess.check_output(cmd)
    print(o.decode("utf-8"))
    dirs_after_clone = set(next(os.walk("."))[1])
    new_dir = list((dirs_after_clone - dirs_before_clone))[0]
    return new_dir


@contextlib.contextmanager
def pushd(new_dir: str) -> None:
    previous_dir = os.getcwd()
    os.chdir(new_dir)
    try:
        yield
    finally:
        os.chdir(previous_dir)


def set_git_config(git_dir: str = ".") -> None:
    with pushd(git_dir):
        # todo overwrite ssh
        print("old git config:\n")
        print(
            subprocess.check_output(["git", "config", "--list", "--local"]).decode(
                "utf-8"
            )
        )
        input(f"change git config in {os.getcwd()}?")
        subprocess.run(["git", "config", "user.name", GITHUB_NAME])
        subprocess.run(["git", "config", "user.email", GITHUB_EMAIL])
        origin_url = (
            subprocess.check_output(["git", "remote", "get-url", "origin"])
            .decode("utf-8")
            .strip()
        )
        if origin_url.startswith("http"):
            if input(f"rewrite {origin_url=} to {to_ssh(origin_url)}?").lower() != "n":
                subprocess.check_output(
                    ["git", "remote", "set-url", "origin", to_ssh(origin_url)]
                )
        output = subprocess.check_output(["git", "config", "--list", "--local"])
        print(output.decode("utf-8"))


def main() -> None:
    if sys.argv[-1].startswith("http"):
        url = to_ssh(sys.argv[-1])
        new_repo_dir = clone(url)
        set_git_config(new_repo_dir)
    else:
        set_git_config(".")


def test():
    assert to_ssh(EXAMPLE_URL) == EXAMPLE_URL_SSH


if __name__ == "__main__":
    test()
    main()
