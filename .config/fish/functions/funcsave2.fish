function funcsave2
    funcsave $argv[1]
    fish_indent --w (echo "/home/kevin/.config/fish/functions/"$argv[1]".fish")
end
