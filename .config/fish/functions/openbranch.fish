function openbranch
    for i in (git diff master --name-only)
        code $i
    end
end
