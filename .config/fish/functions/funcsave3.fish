function funcsave3
    set funcdir $__fish_config_dir/functions
    funcsave $argv[1]
    set script_name "$argv[1].fish"
    fish_indent --w (echo "$funcdir/$script_name")
end
