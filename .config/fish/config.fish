set -gx GEM_HOME $HOME/.local/share/gem/ruby/3.0.0
set -gx SCRIPTS_DIR $HOME/scripts/
#xmodmap $HOME/.Xmodmap
set -gx NOTE_DIR $HOME/notes
set -gx EDITOR nvim
set -gx PAGER less
set -gx MOAR '--statusbar=inverse --no-linenumbers'
set -gx MOZ_X11_EGL 1
set fish_greeting
set pipenv_fish_fancy yes 
set -gx FZF_LEGACY_KEYBINDINGS 0 # set fzf https://github.com/jethrokuan/fzf#usage
set -gx DOKKU_HOST kevbot.xyz
# set -gx PYTHONBREAKPOINT pdb.set_trace
set -gx MYVIMRC $HOME/.config/nvim/init.vim
set -gx SXHKD_SHELL '/usr/bin/sh'
set -gx STEAM_COMPAT_DATA_PATH $HOME/.proton
set -gx GDK_SCALE 1
set -gx QT_AUTO_SCREEN_SCALE_FACTOR 1
set -gx QT_SCALE_FACTOR 2
alias p="xsel -ob"
alias bunx="bun x"
source $HOME/.config/fish/abbrs.fish
if test -e $HOME/rescale/env.fish
    source $HOME/rescale/env.fish
else
    set -gx BROWSER firefox
end

if test -e $HOME/.config/fish/secrets.fish
    source $HOME/.config/fish/secrets.fish
end

# https://github.com/decors/fish-colored-man settings
set -g man_blink -o red
set -g man_bold -o green
set -g man_standout -b white 586e75
set -g man_underline -u 93a1a1

complete --command indent_function --arguments '(functions)'
complete -c ytpp -w youtube-dl
complete -c yay -w yay
# complete -c yadm -w git
complete -c yadm -e

function fed
	$EDITOR ~/.config/fish/config.fish
	$EDITOR ~/.config/fish/abbrs.fish
	exec fish
end

function ved
  pushd ~/.config/nvim
  GIT_DIR=~/.local/share/yadm/repo.git GIT_WORK_TREE=~ $EDITOR ./
  popd
end

function yedit --description "edit with yadm as git dir"
  # if no args, search for  a file with yadm ls-files
  if count $argv > /dev/null
    set FILE $argv
  else
    set FILE (yadm ls-files | fzf)
    if test -z $FILE
      echo "No file selected"
      return 1
    end
  end
  set FILE "$HOME/$FILE"
  GIT_DIR=~/.local/share/yadm/repo.git GIT_WORK_TREE=~ $EDITOR $FILE
  # if file exitst, add
  if test -e $FILE
    yadm add $FILE
  end
end

function e -d "open a file in a text editor"
    $EDITOR $argv
end
function fish_user_key_bindings
	bind \cH backward-kill-path-component
end

function rr
    set PREV_CMD (history | head -1)
    set PREV_OUTPUT (eval $PREV_CMD)
    set CMD $argv[1]
    echo "Running '$CMD $PREV_OUTPUT'"
    eval "$CMD $PREV_OUTPUT"
end

function read_confirm
  while true
    read -l -P 'Do you want to continue? [y/N] ' confirm

    switch $confirm
      case Y y
        return 0
      case '' N n
        return 1
    end
  end
end

function cdg --description "cd to root of git project"
    cd (git rev-parse --show-toplevel)
end

function bh -d "bat history"
    bat ~/.local/share/fish/fish_history
end

if type -q zoxide
    zoxide init fish | source
end

if type -q starship
    starship init fish | source
end

if test -e /opt/asdf-vm/asdf.fish
    source /opt/asdf-vm/asdf.fish
end
set -gx PATH $PATH $HOME/.local/bin $SCRIPTS_DIR $PATH $GEM_HOME/bin $HOME/.yarn/bin/ $HOME/.deno/bin $HOME/.npm/bin/ $HOME/.cargo/bin $HOME/.bin $HOME/go/bin
