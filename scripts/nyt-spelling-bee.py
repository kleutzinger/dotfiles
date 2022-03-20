"""
I solve New York Times' game called Spelling Bee

play here: https://www.nytimes.com/puzzles/spelling-bee
"""
from pprint import pprint


allowed_alphabet = set("mheladp")
required_letter = "p"
valid_words = []


def verify(word):
    if len(word) < 4:
        return False
    if required_letter not in word:
        return False
    return set(word).issubset(allowed_alphabet)


with open("/usr/share/dict/words", "r") as f:
    for word in f.readlines():
        word = word.strip()
        if verify(word):
            valid_words.append(word)


pprint(sorted(valid_words, key=len))
