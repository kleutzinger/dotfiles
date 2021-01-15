# function eel_server_run
#     pushd ~/gits/find-classic-games.git
#     pipenv run python eel_server.py
#     popd
# end

function eel_server_run
    pushd ~/gits/find-classic-games.git
    source .venv/bin/activate.fish
    python eel_server.py
    deactivate
    popd
end
