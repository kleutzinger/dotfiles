set -gx SCRIPTS_DIR /home/kevin/scripts/
set -gx PATH $PATH $SCRIPTS_DIR /home/kevin/.yarn/bin/ /home/kevin/.deno/bin
#xmodmap /home/kevin/.Xmodmap
set -gx NOTE_DIR /home/kevin/notes
set -gx EDITOR nvim
set fish_greeting
set pipenv_fish_fancy yes 
set -gx FZF_LEGACY_KEYBINDINGS 0 # set fzf https://github.com/jethrokuan/fzf#usage
set -gx DOKKU_HOST kevbot.xyz
set -gx MYVIMRC ~/.vimrc
set -gx SXHKD_SHELL '/usr/bin/sh'
set -gx BROWSER firefox 
abbr lg lazygit
abbr advent "source /home/kevin/gits/advent-of-code-2020/new_day.fish"
abbr remove_orphans "sudo pacman -Qtdq | sudo pacman -Rns -"
abbr eel "eel_server_run"
abbr r "python run.py"
# abbr v "source .venv/bin/activate.fish"
abbr pdb "python -m pdb"
abbr v "nvim"
abbr m "micro"
abbr ytp "youtube-dl (xclip -o)"
abbr note note.sh
abbr vim "nvim"
abbr nv "nvim"
abbr nano "nvim"
abbr vi "nvim"
abbr :q exit
abbr gll 'git log --graph --pretty=oneline --abbrev-commit'
alias p="xclip -o"

function chromium
    google-chrome-stable $argv
end
complete --command indent_function --arguments '(functions)'
complete -c ytpp -w youtube-dl
# complete -c yadm -w git
complete -c yadm -e

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
source /opt/asdf-vm/asdf.fish
