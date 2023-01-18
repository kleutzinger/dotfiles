from typing import Any, Callable, Iterable
from requests_html import HTMLSession, HTMLResponse
from iterfzf import iterfzf


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
