function k3 --description 'how much battery does my k3 have'
    upower --dump | awk '/Keychron K3/ {p=1};
     /icon-name/ {p=0; print $0};
     {if (p==1) print $0}' | grep percentage | awk '{print $2}'
end
