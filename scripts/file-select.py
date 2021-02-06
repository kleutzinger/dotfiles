#!/usr/bin/env python3
import sys
import subprocess

encoding = sys.stdout.encoding
file_path = subprocess.check_output("zenity --file-selection", shell=1).strip()
file_path = file_path.decode(encoding)
print(file_path)
