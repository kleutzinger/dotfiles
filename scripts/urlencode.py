#!/usr/bin/env python3
"""
URL-encode a string from stdin
maintain newlines as they are
"""

import sys
import urllib.parse


# take from stdin
input = sys.stdin.read()
# output = urllib.parse.quote(input)
output = "\n".join([urllib.parse.quote(line) for line in input.split("\n")])

print(output, end='')
