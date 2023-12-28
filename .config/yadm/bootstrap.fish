#!/usr/bin/env fish

for PKG in (cat arch_packages.txt)
    yay --noconfirm -S --needed $PKG
end
fish -c 'fisher update'
