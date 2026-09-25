function atuin_load_dotfiles_vars --description "Export vars stored in atuin kv namespace 'env' into the fish environment (atuin dropped dotfiles auto-export in v18.23.0)"
    if not type -q atuin
        return
    end

    for key in (atuin kv list --namespace env 2>/dev/null)
        if test -n "$key"
            set -l value (atuin kv get --namespace env -- $key 2>/dev/null)
            set -gx $key $value
        end
    end
end
