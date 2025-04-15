function p --wraps='xsel -ob' --description paste
    if type -q pbpaste
        pbpaste
    else
        xsel -ob
    end
end
