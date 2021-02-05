function gist_pack --description 'send all installed packages to gist'
    pacman -Q | gist -f pacman-Q.txt -u d9e9649546f33346a8b903a8556b8616
end
