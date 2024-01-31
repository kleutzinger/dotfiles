#!/usr/bin/env fish
yay -S --needed (cat ./arch_packages.txt) --noconfirm
sudo pkgfile --update
systemctl enable --now pkgfile-update.timer
