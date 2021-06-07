set -gx GEM_HOME $HOME/.local/share/gem/ruby/3.0.0
set -gx SCRIPTS_DIR $HOME/scripts/
set -gx PATH $PATH $HOME/.local/bin $SCRIPTS_DIR $PATH $GEM_HOME/bin $HOME/.yarn/bin/ $HOME/.deno/bin $HOME/.npm/bin/
#xmodmap $HOME/.Xmodmap
set -gx NOTE_DIR $HOME/notes
set -gx EDITOR nvim
set -gx MOZ_X11_EGL 1
set fish_greeting
set pipenv_fish_fancy yes 
set -gx FZF_LEGACY_KEYBINDINGS 0 # set fzf https://github.com/jethrokuan/fzf#usage
set -gx DOKKU_HOST kevbot.xyz
# set -gx PYTHONBREAKPOINT pdb.set_trace
set -gx MYVIMRC $HOME/.config/nvim/init.vim
set -gx SXHKD_SHELL '/usr/bin/sh'
set -gx STEAM_COMPAT_DATA_PATH $HOME/.proton
alias p="xclip -o"
source $HOME/.config/fish/abbrs.fish
if test -e $HOME/rescale/env.fish
    source $HOME/rescale/env.fish
else
    set -gx BROWSER firefox
end

# https://github.com/decors/fish-colored-man settings
set -g man_blink -o red
set -g man_bold -o green
set -g man_standout -b white 586e75
set -g man_underline -u 93a1a1

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
	$EDITOR ~/.config/nvim/init.vim
end

function e -d "open a file in a text editor"
    $EDITOR $argv
end
function fish_user_key_bindings
	bind \cH backward-kill-path-component
end

starship init fish | source
if test -e /opt/asdf-vm/asdf.fish
    source /opt/asdf-vm/asdf.fish
end
