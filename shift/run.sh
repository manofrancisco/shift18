source venv/bin/activate
sqlite3 /tmp/shift.db < schema.sql
FLASK_APP=shift
flask initdb
flask run
