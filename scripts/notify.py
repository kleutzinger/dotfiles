#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""
send a desktop notification on macOS, Linux, or Windows.

uses only what ships with the OS: osascript (macOS), notify-send (Linux),
PowerShell toast (Windows). falls back to printing if none are available.

usage:
    notify.py "title" "message"
    notify.py "build done"            # message only

as a module:
    from notify import notify
    notify("title", "message")
"""

import argparse
import json
import shutil
import subprocess
import sys


def _run(cmd: list[str]) -> bool:
    try:
        return subprocess.run(cmd, capture_output=True).returncode == 0
    except OSError:
        return False


def _macos(title: str, message: str) -> bool:
    script = f"display notification {json.dumps(message)} with title {json.dumps(title)}"
    return _run(["osascript", "-e", script])


def _linux(title: str, message: str) -> bool:
    if not shutil.which("notify-send"):
        return False
    return _run(["notify-send", title, message])


def _windows(title: str, message: str) -> bool:
    shell = shutil.which("powershell") or shutil.which("pwsh")
    if not shell:
        return False
    # json.dumps yields a valid double-quoted string; escape $ and ` for PowerShell.
    q = lambda s: json.dumps(s).replace("`", "``").replace("$", "`$")  # noqa: E731
    ps = f"""
[Windows.UI.Notifications.ToastNotificationManager, Windows.UI.Notifications, ContentType = WindowsRuntime] | Out-Null
$t = [Windows.UI.Notifications.ToastNotificationManager]::GetTemplateContent('ToastText02')
$n = $t.GetElementsByTagName('text')
$n.Item(0).AppendChild($t.CreateTextNode({q(title)})) | Out-Null
$n.Item(1).AppendChild($t.CreateTextNode({q(message)})) | Out-Null
$toast = [Windows.UI.Notifications.ToastNotification]::new($t)
[Windows.UI.Notifications.ToastNotificationManager]::CreateToastNotifier('notify.py').Show($toast)
"""
    return _run([shell, "-NoProfile", "-Command", ps])


def notify(title: str, message: str = "") -> bool:
    """Send a notification; print to stdout if no native mechanism worked."""
    if not message:
        title, message = "Notification", title
    send = {"darwin": _macos, "win32": _windows}.get(sys.platform, _linux)
    ok = send(title, message)
    if not ok:
        print(f"[{title}] {message}")
    return ok


def main() -> None:
    p = argparse.ArgumentParser(description="Send a desktop notification.")
    p.add_argument("title", help="title (or the message, if it's the only argument)")
    p.add_argument("message", nargs="?", default="")
    args = p.parse_args()
    sys.exit(0 if notify(args.title, args.message) else 1)


if __name__ == "__main__":
    main()
