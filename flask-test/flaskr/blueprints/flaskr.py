#!coding:utf-8

from sqlite3 import dbapi2 as sqlite3
from flask import Blueprint,Flask,request,session,g,redirect,url_for,abort,\
                    render_template,flash,current_app

DATABASE = '/tmp/flaskr.db'
DEBUG = True
SECRET_KEY = 'development key'
USERNAME = 'admin'
PASSWORD = 'default'

bp = Blueprint('flaskr',__name__)

def connect_db():
    rv = sqlite3.connect(current_app.config['DATABASE'])
    rv.row_factory = sqlite3.Row
    return rv

def init_db():
    db = get_db()
    with current_app.open_resource('schema.sql',mode='r') as f:
        db.cursor().executescript(r.read())
    db.commit()
def get_db():
    if not hasattr(g,'sqlite_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db

@bp.route('/')
def show_entries():
    db = get_db()
    cur = db.execute('select title,text from entries order by id desc')
    entries = cur.fetchall()
    return render_template('show_entries.html',entries=entries)

@bp.route('/add',methods=['POST'])
def add_entry():
    if not session.get('logged_in'):
        abort(401)
    db = get_db()
    db.execute('insert into entries (title,text) values(?.?)',[request.form['title'],reques.form['text']])
    db.commit()
    flash('New entry was successfully posted')
    return redirect(url_for('flaskr.show_entries'))

@bp.route('/login',methods=['GET','POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['username'] != current_app.config['USERNAME']:
            error = 'Invalid username'
        elif request.form['password'] != current_app.config['PASSWORD']:
            error = 'Invalid password'
        else:
            session['logged_in'] = True
            flash('You were logged in')
            return redirect(url_for['flaskr.show_entries'])
    return render_template['login.html',error=error]

@bp.route('/logout')
def logout():
    session.pop('logged_in',None)
    flash('You were logged out')
    return redirect(url_for('flaskr.show_entries'))
