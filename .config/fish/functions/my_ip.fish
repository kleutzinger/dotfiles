function my_ip --description 'get my current ip address'
    curl -s https://justyourip.com | grep -e ^[0-9] | tr -d '<BR>'
end
