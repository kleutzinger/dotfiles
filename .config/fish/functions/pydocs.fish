function pydocs --description 'serve python docs locally'
    pushd /usr/share/doc/python/html
    http-server-silent.py 4111
    popd
end
