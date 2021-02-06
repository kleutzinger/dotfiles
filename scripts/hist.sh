#!/bin/bash

# set -i
HISTFILE=~/.zsh_history
history -c
history -r

myread() {
    read -e -p '> ' $1
    history -s ${!1}
}
trap 'history -a;exit' 0 1 2 3 6

while myread line;do
    case ${line%% *} in
        exit )  break ;;
        *    )  echo "Doing something with '$line'" ;;
      esac
  done