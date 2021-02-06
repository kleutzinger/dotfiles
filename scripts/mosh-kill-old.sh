#!/bin/bash
kill $(ps --no-headers --sort=start_time -C mosh-server -o pid | head -n -1)
