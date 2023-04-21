#!/usr/bin/env python

import os
import sys


def main():
    if len(sys.argv) != 2:
        print("Usage: ./env-obfuscate.py [.env file]")
        sys.exit(1)

    env_file = sys.argv[1]
    if not os.path.exists(env_file):
        print("Error: {} does not exist".format(env_file))
        sys.exit(1)

    with open(env_file) as f:
        lines = f.readlines()

    outfile = env_file + ".example"
    wrote = []
    with open(outfile, "w") as f:
        for line in lines:
            if line.startswith("#"):
                f.write(line)
                continue
            key, value = line.strip().split("=", 1)
            to_write = f"{key}=*****\n"
            print(to_write)
            f.write(to_write)
    print(f"wrote {len(lines)} lines to {outfile}")


if __name__ == "__main__":
    main()
