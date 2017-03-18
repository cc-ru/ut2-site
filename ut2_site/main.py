import hashlib

from flask import (Flask, g, render_template, flash, request, redirect, url_for,
                   session)
from wtforms import Form, StringField, PasswordField, validators
from pymongo import MongoClient

app = Flask(__name__)
app.config.from_object(__name__)

app.config.update(dict(
    SECRET_KEY='_h{\x12\xa3\xce\xAdf\xa4H\x07\x9a\xa0\xea\n\xe0`\xec?+Q\x13\x17Hy\xafC#\x19\xcc\xc5MN',
    DB_URL='mongodb://127.0.0.1:27017',
    SALT='\x14\x15\x99\x9b\xcf\xe7\xe1J\xda=dcM6\x1f\xc7\xb5\xe0\x80\x90\xd6\xed\x03\xa0\xd6\xfa\x99\x9d6r\x00\x02f\x00\xd3\x93\x10j\xb9$\x17%\xee\xe8C;\xf8\xba'
))


class RegisterForm(Form):
    username = StringField('Username', [validators.Length(min=3, max=25)])
    password = PasswordField('Password', [validators.DataRequired()])
    confirm = PasswordField('Repeat password', [
        validators.EqualTo('password', 'Passwords must match')])


class LoginForm(Form):
    username = StringField('Username', [validators.DataRequired()])
    password = PasswordField('Password', [validators.DataRequired()])


def get_db():
    if not hasattr(g, 'mongo_client'):
        g.mongo_client = MongoClient(app.config['DB_URL'])
    return g.mongo_client.ut2_site


def hash_salt(username, password):
    hash_data = app.config['SALT'] + username + password
    return hashlib.sha512(hash_data.encode()).hexdigest()


@app.teardown_appcontext
def close_db(error):
    if hasattr(g, 'mongo_client'):
        g.mongo_client.close()


@app.route('/')
def root():
    return render_template('root.html')


@app.route('/mods')
def mods():
    return render_template('mods.html')


@app.route('/schedule')
def schedule():
    return render_template('schedule.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if session.get('logged_in', False):
        return redirect(url_for('root'))
    form = RegisterForm(request.form)
    if request.method == 'POST' and form.validate():
        db = get_db()
        if db.users.find_one({'username': form.username.data.lower()}):
            flash('Such username is used', 'error')
        else:
            password = hash_salt(form.username.data, form.password.data)
            db.users.insert_one({
                'username': form.username.data.lower(),
                'realname': form.username.data,
                'password': password
            })
            flash('Registered!', 'ok')
            return redirect(url_for('login'))
    return render_template('register.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if session.get('logged_in', False):
        return redirect(url_for('root'))
    form = LoginForm(request.form)
    if request.method == 'POST' and form.validate():
        db = get_db()
        password = hash_salt(form.username.data, form.password.data)
        user = db.users.find_one({'username': form.username.data.lower(),
                                  'password': password})
        if not user:
            flash('Incorrect username and/or password', 'error')
        else:
            session['logged_in'] = True
            session['username'] = user['username']
            session['realname'] = user['realname']
            flash('Logged in!', 'ok')
            return redirect(url_for('root'))
    return render_template('login.html', form=form)


@app.route('/logout')
def logout():
    if session.get('logged_in', False):
        session.pop('logged_in', None)
        session.pop('username', None)
        flash('Logged out!', 'ok')
        return redirect(url_for('root'))
    return redirect(url_for('root'))
