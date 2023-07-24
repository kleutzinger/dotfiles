abbr q exit
abbr lg lazygit
abbr advent "source /home/kevin/gits/advent-of-code-2021/new_day.fish"
abbr remove_orphans "sudo pacman -Qtdq | sudo pacman -Rns -"
abbr eel "eel_server_run"
abbr r "python run.py"
# abbr v "source .venv/bin/activate.fish"
abbr pdb "python -m pdb"
abbr m "micro"
abbr ytp "mpv (xclip -o)"
function note
    pushd ~/gits/foam && code . && popd
end
abbr :q exit
abbr gll 'git log --graph --pretty=oneline --abbrev-commit'
abbr hm 'history --merge'
abbr yg 'lazygit -w ~ -g ~/.local/share/yadm/repo.git'
abbr wb 'wallabag'
abbr arstarst 'setxkbmap us -option ctrl:swap_lalt_lctl'
abbr asdfasdf 'setxkbmap us -variant colemak -option ctrl:swap_lalt_lctl'
abbr pp pm2
abbr ppd 'pm2 delete all'
abbr d deactivate
abbr gs 'git switch -'
abbr gsm 'git switch master'
abbr xt 'TERM=xterm'
abbr gpm 'git switch master && git pull && git switch -'
abbr bbb 'bandcamp-downloader.sh'
abbr gam 'git commit -am'
abbr cdr 'cd (git rev-parse --show-toplevel)'
abbr s 'kitty +kitten ssh'
abbr ayy 'yay'
abbr ped sudoedit /etc/pacman.conf
abbr deploy_blog magic.py ~/gits/kleutzinger.github.io/site-generator/kevbot.xyz.py 0
abbr pkg add-pkg
abbr ij 'intellij-idea-ultimate-edition .'
abbr c 'code .'
abbr t '~'
