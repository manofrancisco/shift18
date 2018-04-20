# all the imports
import os
import sqlite3
import requests
import json
from random import shuffle
from flask import Flask, request, jsonify, session, g, redirect, url_for, abort, \
     render_template, flash


app = Flask(__name__) # create the application instance :)
app.config.from_object(__name__) # load config from this file , flaskr.py


# Load default config and override config from an environment variable
app.config.update(dict(
    DATABASE=os.path.join(app.root_path, 'shift.db'),
    SECRET_KEY='development key',
    USERNAME='admin',
    PASSWORD='default'
))
app.config.from_envvar('FLASKR_SETTINGS', silent=True)


def connect_db():
    """Connects to the specific database."""
    rv = sqlite3.connect(app.config['DATABASE'])
    rv.row_factory = sqlite3.Row
    return rv


def get_db():
    """Opens a new database connection if there is none yet for the
    current application context.
    """
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db


@app.teardown_appcontext
def close_db(error):
    """Closes the database again at the end of the request."""
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()


def init_db():
    db = get_db()
    with app.open_resource('schema.sql', mode='r') as f:
        db.cursor().executescript(f.read())
    db.commit()


@app.cli.command('initdb')
def initdb_command():
    """Initializes the database."""
    init_db()
    print('Initialized the database.')



@app.route('/add/<title>/<text>', methods=['GET', 'POST'])
def add_entry(title, text):
    db = get_db()
    db.execute('insert into users (title, text) values (?, ?)',
                 [title, text])
    db.commit()
    flash('New entry was successfully posted')
    return jsonify({"title":title, "text":text});



@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['username'] != app.config['USERNAME']:
            error = 'Invalid username'
        elif request.form['password'] != app.config['PASSWORD']:
            error = 'Invalid password'
        else:
            session['logged_in'] = True
            flash('You were logged in')
            return redirect(url_for('show_users'))
    return render_template('login.html', error=error)


@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('You were logged out')
    return redirect(url_for('show_users'))



@app.route('/get_question/<facebook_id>', methods=['GET', 'POST'])
def get_question(facebook_id):
    db = get_db()
    cur = db.execute('select * from users where facebook_id =' + facebook_id)
    user = cur.fetchone()

    if not user:
        db.execute('insert into users (facebook_id) values (?)',
                     [facebook_id])
        db.commit()
        cur = db.execute('select * from users where facebook_id =' + facebook_id)
        user = cur.fetchone()

    print(json.dumps(list(user)))

    req = requests.get('https://opentdb.com/api.php?amount=1&type=multiple', )
    dic = req.json()
    category = dic.get("results")[0].get("category")
    difficulty = dic.get("results")[0].get("difficulty")
    question = dic.get("results")[0].get("question")
    incorrect_answers = dic.get("results")[0].get("incorrect_answers")
    correct_answer = dic.get("results")[0].get("correct_answer")

    options = incorrect_answers + [correct_answer]

    shuffle(options)

    text = question + "\n"
    abcd = "ABCD"

    for i in range(4):
        text += abcd[i] + " - " + options[i] + "\n"
    print(text)

    return text


@app.route('/')
def show_users():

    db = get_db()
    cur = db.execute('select id, username from users order by id desc')
    users = cur.fetchall()

    for user in users:
        print(json.dumps(list(user)))
    print(users)


    return "oi"
