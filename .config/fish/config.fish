set -gx GEM_HOME /home/kevin/.local/share/gem/ruby/2.7.0
set -gx SCRIPTS_DIR /home/kevin/scripts/
set -gx PATH $PATH /home/kevin/.local/bin $SCRIPTS_DIR $PATH $GEM_HOME/bin /home/kevin/.yarn/bin/ /home/kevin/.deno/bin /home/kevin/.npm/bin/
#xmodmap /home/kevin/.Xmodmap
set -gx NOTE_DIR /home/kevin/notes
set -gx EDITOR nvim
set -gx MOZ_X11_EGL 1
set fish_greeting
set pipenv_fish_fancy yes 
set -gx FZF_LEGACY_KEYBINDINGS 0 # set fzf https://github.com/jethrokuan/fzf#usage
set -gx DOKKU_HOST kevbot.xyz
#set -gx PYTHONBREAKPOINT ipdb.set_trace
set -gx MYVIMRC ~/.vimrc
set -gx SXHKD_SHELL '/usr/bin/sh'
set -gx BROWSER firefox 
set -gx STEAM_COMPAT_DATA_PATH $HOME/.proton
alias p="xclip -o"
source /home/kevin/.config/fish/abbrs.fish

complete --command indent_function --arguments '(functions)'
complete -c ytpp -w youtube-dl
# complete -c yadm -w git
complete -c yadm -e

function fed
	$EDITOR ~/.config/fish/config.fish
	$EDITOR ~/.config/fish/abbrs.fish
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
