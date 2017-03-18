from flask import (Flask, g, render_template, flash, request, redirect, url_for,
                   session)
from wtforms import Form, StringField, PasswordField, validators

app = Flask(__name__)
app.config.from_object(__name__)

app.config.update(dict(
    SECRET_KEY='_h{\x12\xa3\xce\xAdf\xa4H\x07\x9a\xa0\xea\n\xe0`\xec?+Q\x13\x17Hy\xafC#\x19\xcc\xc5MN',
    DB_URL='mongodb://127.0.0.1:27017'
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
        flash('Registered!', 'ok')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if session.get('logged_in', False):
        return redirect(url_for('root'))
    form = LoginForm(request.form)
    if request.method == 'POST' and form.validate():
        session['logged_in'] = True
        session['username'] = form.username.data
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
