function my_ip --description 'get my current ip address'
    curl -s https://justyourip.com | grep cli | cut -d, -f2 | tail -n 1
end
