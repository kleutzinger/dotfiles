function atuin_load_dotfiles_vars --description "Stopgap: re-export atuin's legacy dotfiles vars (removed from atuin init in v18.23.0)"
    if not type -q atuin
        return
    end

    if not test -e $HOME/.config/fish/atuin_dotfiles_env.bash
        return
    end

    for line in (bash $HOME/.config/fish/atuin_dotfiles_env.bash 2>/dev/null)
        set -l parts (string split -m 1 \t -- $line)
        if test (count $parts) -eq 2
            set -gx $parts[1] $parts[2]
        end
    end
end
