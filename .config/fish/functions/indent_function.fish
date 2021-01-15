function indent_function
    set funcdir $__fish_config_dir/functions
    set script_name "$argv[1].fish"
    fish_indent --w (echo "$funcdir/$script_name")
end
