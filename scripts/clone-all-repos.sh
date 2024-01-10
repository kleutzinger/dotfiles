#!/bin/bash

# clones all my repos from github
# from:
# https://stackoverflow.com/a/68770988

gh repo list --limit 4000 | while read -r repo _; do
  gh repo clone "$repo"
done
