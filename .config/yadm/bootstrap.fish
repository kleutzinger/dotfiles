#!/usr/bin/env fish

yay -S (cat arch_packages.txt)
fish -c 'fisher update'
nvim +'PlugInstall --sync' +qa
echo -e "run in nvim:\nCocInstall" (cat coc_packages.txt)
