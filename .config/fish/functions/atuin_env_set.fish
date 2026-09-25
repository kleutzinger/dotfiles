function atuin_env_set --description "Set/update a var in atuin kv (namespace 'env') and export it in the current shell"
    if test (count $argv) -lt 1 -o (count $argv) -gt 2
        echo "Usage: atuin_env_set KEY [VALUE]" >&2
        echo "  If VALUE is omitted, you'll be prompted (input hidden, not saved to shell history)." >&2
        return 1
    end

    set -l key $argv[1]
    set -l value

    if test (count $argv) -eq 2
        set value $argv[2]
    else
        read -s -P "Value for $key: " -l value
        echo >&2
    end

    if test -z "$value"
        echo "atuin_env_set: empty value, aborting" >&2
        return 1
    end

    printf '%s' $value | atuin kv set --namespace env --key $key
    or begin
        echo "atuin_env_set: failed to write $key to atuin kv" >&2
        return 1
    end

    set -gx $key $value
    echo "$key set in atuin kv (namespace 'env') and exported in this shell." >&2
    echo "It'll auto-load in new fish sessions; run 'atuin_load_dotfiles_vars' to pick it up elsewhere too." >&2
end
