function add-pkg --description 'add package and save it for bootstrapping'
    echo (string join '\n' $argv) >> ~/.config/yadm/arch_packages.txt
    yay -S $argv
end
