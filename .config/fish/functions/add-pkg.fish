function add-pkg --description 'add package and save it for bootstrapping'
    if test -z $argv
        echo "No package specified"
        return 1
    end
    set PKGFILE ~/.config/yadm/arch_packages.txt
    echo (string join '\n' $argv) >> $PKGFILE
    sort $PKGFILE | uniq | sponge $PKGFILE
    yay -S $argv
end
