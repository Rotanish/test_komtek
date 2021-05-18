#! bin/python


from flask import Flask
from pony.flask import Pony
from model import db
from no_csrf import CSRF
from login import Login

password_secret = b'\x03\x18\xe3\xb07\xdb%(\x8b\x8f\xa6qJ&-\x1br!\xb9\xd0'
csrf = CSRF('\x00\x8e\xb0\x0f\x11A\x9dU\xfc;\xb9\x8f\x0f=\xeb\x00\xcf\x9e\xedk')

app = Flask(__name__)

app.config.update(dict(
    DEBUG=False,
    SECRET_KEY=b'\xbb\xdb\xcd|r\xe3,\xe2~Q\x04\xcfT\x98\xd62\xae\x0f\xdf<',
    PONY={
        'provider': 'sqlite',
        'filename': 'main.db',
        'create_db': True
    }

))


my_login = Login(db)

Pony(app)
