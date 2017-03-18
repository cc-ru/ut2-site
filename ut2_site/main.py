import hashlib

from flask import Flask, g
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


from ut2_site.views import mod
app.register_blueprint(mod)
