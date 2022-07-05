#!/usr/bin/env python3
"""
I solve New York Times' game called Spelling Bee

play here: https://www.nytimes.com/puzzles/spelling-bee
"""
import json

inp = input("what letters? (required letter first):")
allowed_alphabet = set(inp)
required_letter = inp[0]
valid_words = []
pangrams = []


def verify(word):
    sword = set(word)
    if len(word) < 4:
        return False
    if required_letter not in sword:
        return False
    if not sword.issubset(allowed_alphabet):
        return False
    if allowed_alphabet == sword:
        pangrams.append(word)
    return True


with open("/usr/share/dict/words", "r") as f:
    for word in f.readlines():
        word = word.strip()
        if verify(word):
            valid_words.append(word)


print(
    json.dumps(
        dict(valid_words=sorted(valid_words, key=len), pangrams=pangrams), indent=2
    )
)
