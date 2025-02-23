import subprocess
import requests
from typing import Any, Callable, Iterable, Optional, TypeVar
import os
import sys
import asyncio
from pprint import pprint


T = TypeVar("T")


def identity(x: T) -> T:
    "return the input unchanged"
    return x


def fzf_iterable(iterable: Iterable) -> str:
    """
    Given an iterable, shells out to fzf with all the values and returns the chosen value.
    """
    fzf_command = ["fzf"]

    # Prepare the input for fzf
    input_str = "\n".join(str(item) for item in iterable)

    # Call fzf and get the chosen value
    with subprocess.Popen(
        fzf_command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True
    ) as proc:
        stdout, _ = proc.communicate(input_str)
        return stdout.strip()


def fzf_choose(
    inp: Iterable,
    display_func: Callable = identity,
    output_func: Callable = identity,
    **kwargs,
) -> Any:
    """
    Input: any iterable (which is indexable)
    * interactive prompt (fzf) *
    Output: a single value from that iterable

    TODO: add way to hide numbers on the left, aka do this without indexing
    """
    choices = []
    for idx, val in enumerate(inp):
        choices.append(f"{idx:2} {display_func(val)}")
    choice_idx = int(fzf_iterable(choices, **kwargs).strip().split(" ")[0])
    return output_func(inp[choice_idx])


def get_url(url: str, execute_js: bool = False):
    """
    get a webpage's html, optionally render javascript
    thanks to https://pypi.org/project/requests-html/
    """
    from requests_html import HTMLResponse, HTMLSession

    html_session = HTMLSession()
    req = html_session.get(url)
    if execute_js:
        req.html.render(timeout=20)
    return req


def get_processes():
    """
    Parse the output of `ps aux` into a list of dictionaries representing the parsed
    process information from each row of the output. Keys are mapped to column names,
    parsed from the first line of the process' output.
    :rtype: list[dict]
    :returns: List of dictionaries, each representing a parsed row from the command output
    """
    output = subprocess.Popen(["ps", "aux"], stdout=subprocess.PIPE).stdout.readlines()
    headers = [
        h for h in " ".join(output[0].decode("utf-8").strip().split()).split() if h
    ]
    raw_data = map(lambda s: s.strip().split(None, len(headers) - 1), output[1:])
    return [dict(zip(headers, r)) for r in raw_data]


def fetch_url_with_retry(
    url,
    max_retries=5,
    request_timeout=10,
    retry_timeout=3,
) -> Optional[requests.Response]:
    """
    Fetch the content of a URL using the requests library with retry.

    Parameters:
        url (str): The URL to fetch the content from.
        max_retries (int, optional): The maximum number of retry attempts. Default is 5.
        retry_timeout (int, optional): The timeout in seconds between retry attempts. Default is 10.
        request_timeout (int, optional): The timeout for the request in seconds. Default is 30.

    Returns:
        str: The content of the URL if successfully fetched, or None if all retry attempts failed.
    """
    for retry in range(max_retries + 1):
        try:
            response = requests.get(url, timeout=request_timeout)
            response.raise_for_status()  # Raise an exception for non-200 status codes
            return response
        except (requests.RequestException, requests.HTTPError, requests.Timeout) as e:
            print(f"Attempt {retry + 1}/{max_retries + 1} failed. Error: {e}")
            if retry < max_retries:
                print(f"Retrying in {retry_timeout} seconds...")
                time.sleep(retry_timeout)

    return None  # Return None if all retry attempts fail


def insertIntoPocketBase(record: dict = {}, db_name: str = "") -> None:
    """
    Insert a record into PocketBase, specifically the bandcamps collection

    params:
        record: dict - the record to insert
            example:
                {
                    "url": "https://kevin.bandcamp.com/album/album",
                    "full_cmd": "yt-dlp...",
                    "cwd": "/home/kevin/Downloads",
                    "hostname": "kevin-arch"
                }
    """
    from pocketbase import PocketBase

    POCKETBASE_URL = os.getenv("POCKETBASE_URL")
    POCKETBASE_USERNAME = os.getenv("POCKETBASE_ADMIN_USERNAME")
    POCKETBASE_PASSWORD = os.getenv("POCKETBASE_ADMIN_PASSWORD")

    if not all([POCKETBASE_URL, POCKETBASE_USERNAME, POCKETBASE_PASSWORD]):
        print("Missing environment variables")
        sys.exit(1)

    if not db_name:
        print("No database name provided")
        sys.exit(1)

    if not all([POCKETBASE_URL, POCKETBASE_USERNAME, POCKETBASE_PASSWORD]):
        print("Missing environment variables")
        sys.exit(1)

    pb = PocketBase(POCKETBASE_URL)

    async def inner(params=record):
        await pb.admins.auth.with_password(
            email=POCKETBASE_USERNAME, password=POCKETBASE_PASSWORD
        )

        collection = pb.collection("bandcamps")
        created = await collection.create(params=params)
        # print what was created
        pprint(created)

    asyncio.run(inner(record))
