function random_chars
    cat /dev/urandom | tr -dc A-Za-z0-9 | head -c16
end
