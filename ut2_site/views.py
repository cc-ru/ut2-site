import io
import os.path

from flask import Blueprint, render_template, redirect, url_for, flash, \
    request, session

from ut2_site.main import get_db, hash_salt, LoginForm, RegisterForm, \
    AccountForm, set_skin, set_cape

mod = Blueprint('views', __name__)


@mod.route('/')
def root():
    return render_template('root.html')


@mod.route('/mods')
def mods():
    return render_template('mods.html')


@mod.route('/schedule')
def schedule():
    return render_template('schedule.html')


@mod.route('/register', methods=['GET', 'POST'])
def register():
    if session.get('logged_in', False):
        return redirect(url_for('views.root'))
    form = RegisterForm()
    if form.validate_on_submit():
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
            return redirect(url_for('views.login'))
    return render_template('register.html', form=form)


@mod.route('/login', methods=['GET', 'POST'])
def login():
    if session.get('logged_in', False):
        return redirect(url_for('views.root'))
    form = LoginForm()
    if form.validate_on_submit():
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
            return redirect(url_for('views.root'))
    return render_template('login.html', form=form)


@mod.route('/logout')
def logout():
    if session.get('logged_in', False):
        session.pop('logged_in', None)
        session.pop('username', None)
        flash('Logged out!', 'ok')
        return redirect(url_for('views.root'))
    return redirect(url_for('views.root'))


@mod.route('/account', methods=['GET', 'POST'])
def account():
    if not session.get('logged_in', False):
        return redirect(url_for('views.root'))
    form = AccountForm()
    if form.validate_on_submit():
        if form.delete.data:
            if form.subject.data == 'skin':
                set_skin(session['username'], None)
                flash('Skin removed!', 'ok')
            elif form.subject.data == 'cape':
                set_cape(session['username'], None)
                flash('Cape removed!', 'ok')
        elif form.submit.data:
            f = form.image.data
            if form.subject.data == 'skin':
                buf = io.BytesIO(b'')
                f.save(buf)
                set_skin(session['username'], buf)
                flash('Skin set!', 'ok')
            elif form.subject.data == 'cape':
                buf = io.BytesIO(b'')
                f.save(buf)
                set_cape(session['username'], buf)
                flash('Cape set!', 'ok')
    return render_template('account.html', form=form)
