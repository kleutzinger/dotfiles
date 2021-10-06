from pathlib import Path
import os
from subprocess import call
import time

HOME = str(Path.home())
SLEEPFILE = os.path.join(HOME, ".sleep-lock")
SLEEP_WAIT_SEC = 5


def notif(msg):
    try:
        from loguru import logger

        logger.info(msg, backtrace=True)
    except ImportError:
        print(msg)
    call(["notify-send", msg])


def suspend():
    # call(["xset", "dpms", "force", "off"])
    call(["systemctl", "suspend"])


def remove_sleep_file():
    try:
        os.remove(SLEEPFILE)
        notif("removed sleepfile")
    except:
        notif("no sleepfile to remove")
        pass


def write_sleep_file():
    "write a lock file to go to sleep"
    with open(SLEEPFILE, "w") as f:
        f.write("sleepin\n")
        notif("wrote sleepfile")


def try_to_sleep():
    "we write the file and go to sleep in 5 seconds then check again"
    write_sleep_file()
    time.sleep(SLEEP_WAIT_SEC)
    if sleep_file_exists():
        notif(f"{SLEEPFILE} file exists, going to sleep now")
        time.sleep(1)
        remove_sleep_file()
        suspend()
    else:
        notif("sleep avoided")


def sleep_file_exists():
    return os.path.exists(SLEEPFILE)


def main():
    if sleep_file_exists():
        remove_sleep_file()
    else:
        try_to_sleep()


if __name__ == "__main__":
    main()
