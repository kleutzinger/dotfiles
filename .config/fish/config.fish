set -gx SCRIPTS_DIR /home/kevin/scripts/
set -gx PATH $PATH $SCRIPTS_DIR /home/kevin/.yarn/bin/ /home/kevin/.deno/bin
#xmodmap /home/kevin/.Xmodmap
set -Ux NOTE_DIR /home/kevin/notes
set -Ux EDITOR /usr/bin/nvim
set fish_greeting
set pipenv_fish_fancy yes 
set -Ux FZF_LEGACY_KEYBINDINGS 0 # set fzf https://github.com/jethrokuan/fzf#usage
set -Ux DOKKU_HOST kevbot.xyz
set -Ux LEKTOR_DEV 1
set -Ux MYVIMRC ~/.vimrc
abbr advent "source /home/kevin/gits/advent-of-code-2020/new_day.fish"
abbr remove_orphans "sudo pacman -Qtdq | sudo pacman -Rns -"
abbr eel "eel_server_run"
abbr r "python run.py"
# abbr v "source .venv/bin/activate.fish"
abbr v "nvim"
abbr m "micro"
abbr ytp "youtube-dlc (xclip -o)"
abbr note note.sh
abbr vim "nvim"
abbr nv "nvim"
abbr nano "nvim"
abbr vi "nvim"
alias p="xclip -o"

complete --command indent_function --arguments '(functions)'
complete -c ytpp -w youtube-dlc


function fed
	$EDITOR ~/.config/fish/config.fish
	source ~/.config/fish/config.fish
end

function ved
	$EDITOR ~/.vimrc
end

function e -d "open a file in a text editor"
    $EDITOR $argv
end

function fish_user_key_bindings
	bind \cH backward-kill-path-component
end

starship init fish | source
