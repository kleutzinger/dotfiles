abbr q exit
abbr lg lazygit
abbr advent "source /home/kevin/gits/advent-of-code-2021/new_day.fish"
abbr remove_orphans "sudo pacman -Qtdq | sudo pacman -Rns -"
abbr pdb "python -m pdb"
abbr ytp "mpv (xclip -o)"
abbr :q exit
abbr gll 'git log --graph --pretty=oneline --abbrev-commit'
abbr hm 'history --merge'
abbr yg 'lazygit -w ~ -g ~/.local/share/yadm/repo.git'
function _kb_set_layout
    # On KDE (esp. Wayland), reorder kxkbrc via kb-layout.sh so games pick up
    # the change - a plain setxkbmap doesn't affect KDE's compositor-owned
    # keyboard state. Everywhere else (XFCE/X11) fall back to setxkbmap.
    if string match -qi '*kde*' -- $XDG_CURRENT_DESKTOP; and type -q kb-layout.sh
        kb-layout.sh $argv[1]
    else
        switch $argv[1]
            case colemak
                setxkbmap us -variant colemak -option ctrl:swap_lalt_lctl
            case qwerty
                setxkbmap us -option ctrl:swap_lalt_lctl
        end
    end
end
function arst
    _kb_set_layout qwerty
end
function arstarst
    _kb_set_layout qwerty
end
function asdf
    _kb_set_layout colemak
end
function asdfasdf
    _kb_set_layout colemak
end
abbr d deactivate
abbr gs 'git switch -'
abbr xt 'TERM=xterm'
abbr cdr 'cd (git rev-parse --show-toplevel)'
abbr ayy 'yay'
abbr ped sudoedit /etc/pacman.conf
abbr deploy_blog magic.py ~/gits/kleutzinger.github.io/site-generator/kevbot.xyz.py 0
abbr pkg add-pkg
abbr nn 'nvim .'
abbr ocr 'textsnatcher'
abbr yp 'yadm pull'
abbr ze 'zellij'
abbr yh 'GIT_DIR=~/.local/share/yadm/repo.git gh'
abbr yy 'yadm pull && yay --noconfirm'
abbr nn 'nvim'
abbr cc 'coconut.py'
abbr ccc 'coconut.py --sec'
abbr ccl 'coconut.py list'
abbr cccc 'coconut.py --first'
abbr yayy 'yay --noconfirm'
abbr cdt 'cd ~/.threads && gallery-dl (p)'
abbr cdtt 'cd ~/.threads && gallery-dl (p) --sleep 5'
abbr r 'reset'
abbr -a L --position anywhere --set-cursor "% | less"
abbr grv 'gh repo view --web'
abbr f 'food'
abbr bbb 'brackets.py bracket --execute'
abbr vz visidata
abbr fff 'coconut.py --path (readlink -f (fzf))'

alias define "sdcv"

if test (uname) != "Darwin"
  alias task "go-task"
end

alias fd "fd --hidden --no-ignore"

