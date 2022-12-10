from typing import Any, Callable, Iterable
from iterfzf import iterfzf

def identity(x: Any) -> Any:
    return x


def fzf_choose(
    inp: Iterable,
    display_func: Callable = identity,
    output_func: Callable = identity,
) -> Any:
    """
    Input: any iterable
    * interactive prompt (fzf) *
    Output: a single value from that iterable
    """
    choices = []
    for idx, val in enumerate(inp):
        choices.append(f"{idx} {display_func(val)}")
    choice_idx = int(iterfzf(choices).split(" ")[0])
    return output_func(inp[choice_idx])
