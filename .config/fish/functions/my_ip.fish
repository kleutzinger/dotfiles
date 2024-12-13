function my_ip --description 'get my current ip address'
  curl --silent 'https://api.ipify.org'
end
