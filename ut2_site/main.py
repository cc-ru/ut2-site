import hashlib
import os
import os.path
import re

from flask import Flask, g
import magic
from pymongo import MongoClient
from werkzeug.utils import secure_filename
from wtforms import Form, StringField, PasswordField, validators, \
    SubmitField, RadioField, ValidationError

app = Flask(__name__)
app.config.from_object(__name__)

app.config.update(dict(
    SECRET_KEY='_h{\x12\xa3\xce\xAdf\xa4H\x07\x9a\xa0\xea\n\xe0`\xec?+Q\x13\x17Hy\xafC#\x19\xcc\xc5MN',
    DB_URL='mongodb://127.0.0.1:27017',
    SALT=('\x14\x15\x99\x9b\xcf\xe7\xe1J\xda=dcM6\x1f\xc7\xb5\xe0\x80\x90\xd6'
          '\xed\x03\xa0\xd6\xfa\x99\x9d6r\x00\x02f\x00\xd3\x93\x10j\xb9$\x17%'
          '\xee\xe8C;\xf8\xba'),
    UPLOAD_FOLDER='/tmp/imagedata/',
    MAX_CONTENT_LENGTH=32 * 1024
))

app.config.from_envvar('UT2SITESETTINGS')

from flask_uploads import UploadSet, configure_uploads
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
png_images = UploadSet('pngimages', ('png',),
                       lambda app: app.config['UPLOAD_FOLDER'])

configure_uploads(app, (png_images,))

resolution_re = re.compile(r', (\d+) x (\d+),')
username_re = re.compile(r'^[A-Za-z0-9_]+$')


class RegisterForm(FlaskForm):
    username = StringField('Username', [validators.Length(min=3, max=25),
                                        validators.Regexp(
                                            username_re, 0,
                                            'Incorrect characters. Allowed '
                                            'are alphanumeric characters, and '
                                            'underscore.'
                                        )])
    password = PasswordField('Password', [validators.DataRequired()])
    confirm = PasswordField('Repeat password', [
        validators.EqualTo('password', 'Passwords must match')])


class LoginForm(FlaskForm):
    username = StringField('Username', [validators.DataRequired(),
                                        validators.Regexp(
                                            username_re, 0,
                                            'Incorrect characters. Allowed '
                                            'are alphanumeric characters, and '
                                            'underscore.'
                                        )])
    password = PasswordField('Password', [validators.DataRequired()])


class AccountForm(FlaskForm):
    image = FileField('Image file', [FileAllowed(png_images,
                                                  'Unsupported image type')])
    subject = RadioField('What to change', [validators.DataRequired()],
                         choices=[
                             ('skin', 'Skin'),
                             ('cape', 'Cape')
                         ])
    submit = SubmitField('Set')
    delete = SubmitField('Remove')

    def validate_image(form, field):
        if form.submit.data and not field.data:
            raise ValidationError("This field is required.")


def get_db():
    if not hasattr(g, 'mongo_client'):
        g.mongo_client = MongoClient(app.config['DB_URL'])
    return g.mongo_client.ut2_site


def hash_salt(username, password):
    hash_data = app.config['SALT'] + username + password
    return hashlib.sha512(hash_data.encode()).hexdigest()


def set_skin(username, buf):
    if not buf:
        try:
            os.remove(os.path.join(
                app.config['UPLOAD_FOLDER'],
                'skins',
                username + '.png'))
        except FileNotFoundError:
            pass
        return True
    try:
        m = magic.from_buffer(buf.read(2048))
    except:
        return False, "Bad image"
    match = resolution_re.search(m)
    if not match or len(match.groups()) != 2:
        return False, "Bad image"
    w, h = match.groups()
    w, h = int(w), int(h)
    if w != 64 or h != 32:
        return False, "Expected a 64x32 image"
    buf.seek(0, 0)
    with open(os.path.join(
            app.config['UPLOAD_FOLDER'],
            'skins',
            username + '.png'), 'wb') as f:
        f.write(buf.read())
    return True


def set_cape(username, buf):
    if not buf:
        try:
            os.remove(os.path.join(
                app.config['UPLOAD_FOLDER'],
                'capes',
                username + '.png'))
        except FileNotFoundError:
            pass
        return True
    try:
        m = magic.from_buffer(buf.read(8192))
    except:
        return False, "Bad image"
    match = resolution_re.search(m)
    if not match or len(match.groups()) != 2:
        return False, "Bad image"
    w, h = match.groups()
    w, h = int(w), int(h)
    if w != 64 or h != 32:
        return False, "Expected a 64x32 image"
    buf.seek(0, 0)
    with open(os.path.join(
            app.config['UPLOAD_FOLDER'],
            'capes',
            username + '.png'), 'wb') as f:
        f.write(buf.read())
    return True


@app.teardown_appcontext
def close_db(error):
    if hasattr(g, 'mongo_client'):
        g.mongo_client.close()


from ut2_site.views import mod
app.register_blueprint(mod)
