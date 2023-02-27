from typing import Any, Callable, Iterable
from requests_html import HTMLSession, HTMLResponse
from iterfzf import iterfzf
import subprocess


def identity(x: Any) -> Any:
    return x


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
    choice_idx = int(iterfzf(choices, **kwargs).strip().split(" ")[0])
    return output_func(inp[choice_idx])


def get_url(url: str, execute_js: bool = False) -> HTMLResponse:
    """
    get a webpage's html, optionally render javascript
    thanks to https://pypi.org/project/requests-html/
    """
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
    headers = [h for h in " ".join(output[0].decode('utf-8').strip().split()).split() if h]
    raw_data = map(lambda s: s.strip().split(None, len(headers) - 1), output[1:])
    return [dict(zip(headers, r)) for r in raw_data]
