#!/usr/bin/env python

# https://rtpg.co/2020/12/11/dbg-in-python.html
def dbg(result):
    """
    Recover the expression giving the result, and then
    print a helpful debug statement showing this
    """
    import inspect

    frame = inspect.stack()[1]
    expr = extract_dbg(frame.code_context[0])
    filename = frame.filename.split("/")[-1]
    print(f"[{filename}: {frame.lineno}] {expr} = {result}")
    return result


def extract_dbg(code_fragment):
    import ast

    # from a line of source text, try and find the expression
    # given to a call to dbg
    expression_options = code_fragment.split("dbg(")
    if len(expression_options) != 2:
        # if there are either multiple dbg statements
        # or I can't find the dbg line, bail
        return "???"
    # get the part to the right of dbg(
    expr_candidate = expression_options[1]
    while expr_candidate:
        try:
            ast.parse(expr_candidate)
            return expr_candidate
        except SyntaxError:
            expr_candidate = expr_candidate[:-1]
    # didn't find anything, also give up
    return "???"
