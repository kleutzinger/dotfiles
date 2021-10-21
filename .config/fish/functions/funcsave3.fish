function funcsave3
    set funcdir $__fish_config_dir/functions
    funcsave $argv[1]
    set script_name "$argv[1].fish"
    set script_path "$funcdir/$script_name"
    fish_indent --w (echo "$script_path")
    yadm add $script_path
end
