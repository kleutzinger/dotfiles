#!/usr/bin/env python3
"""invoke magic spells from magic words inside a file

magic words are defined thusly: (must be all caps)

#__MAGICWORD__# echo 'followed by a shell command'

put something of that format inside a file to set up running that command

additionally, #__file__# will be substituted with the path of the file this is called on
#__dir__# is the file's containing directory

you can also call the script with a spell_idx argument
    `magic.py magic.py 0`

TODO:
if no args:
    look for other executables inside folder
    look for .MAGIC or MAGIC.txt inside folder?
`magic.py % 0` is <leader>0

examples:
    #__PUSH__# gist -u ed85631bcb75846d950258eb19cb6b2a #__file__#
    #__RUN__# python ~/scripts/magic.py
"""

import os
import re
import sys
import subprocess

MAGIC_REGEX = re.compile(r"\s*#\s*__([A-Z0-9_]+)__#\s*(\S.*)")
CAST_EMOJI = "(๑•ᴗ•)⊃━☆.*･｡ﾟ"


def main():
    if len(sys.argv) == 1:
        print(__doc__)
        exit()
    if len(sys.argv) >= 2:
        filename = sys.argv[1]
        if os.path.isfile(filename):
            with_arg(filename)
        else:
            print(f"no file {filename}")
            sys.exit(1)


def with_arg(filename):
    spells = []
    spell_counter = 0
    with open(filename, "r") as fileobj:
        for line in fileobj:
            matches = MAGIC_REGEX.search(line)
            if matches:
                name, command = matches.group(1), matches.group(2)
                command = sub_magic(command, filename)
                spells.append((name, command))
                spell_counter += 1
    if spell_counter == 0:
        print(f"no spells found in {filename}")
        print("executing shebang at top")
        subprocess.run(["perl", filename])
        exit(0)
    if len(sys.argv) >= 3:
        spell_idx = int(sys.argv[2])
    else:
        spell_idx = choose_spell_idx(spells)
    name, command = spells[spell_idx]

    print(f"{CAST_EMOJI}{name}")
    subprocess.call(command, shell=True)


def sub_magic(command, argfile):
    file_abs = os.path.abspath(argfile)
    file_dir = os.path.dirname(file_abs)
    command = command.replace("#__file__#", file_abs)
    command = command.replace("#__dir__#", file_dir)
    return command


def choose_spell_idx(spells):
    idx = 0
    for name, command in spells:
        print(f"{idx}.\t{CAST_EMOJI}{name}")
        print(f"{command}")
        print("-" * 5)
        idx += 1
    if len(spells) == 1:
        return 0
    inp = input("idx: ")
    if not inp:
        spell_idx = 0
    else:
        spell_idx = int(inp)
    return spell_idx


if __name__ == "__main__":
    main()
