function reset_db --argument dbname --description 'reset a flask app db and generate initial migration'
    set fish_trace 1
    set waitsec 3
    echo "destroying $dbname in $waitsec sec, ctrl +c to cancel"
    sleep $waitsec
    dropdb $dbname
    createdb $dbname
    rm -rf migrations
    flask db init
    cp ~/boilerplate/alembic.ini migrations/alembic.ini
    flask db migrate -m "initial migration"
    flask db upgrade
end
