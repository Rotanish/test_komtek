#! bin/python


from pony.orm import *
from datetime import datetime, date

db = Database()


class Directory(db.Entity):
    identificator = PrimaryKey(int, auto=True)
    versions = Set('DirectoryVersion', reverse='directory')
    name = Required(str)
    short_name = Optional(str)
    description = Optional(str)


class DirectoryVersion(db.Entity):
    directory = Required('Directory', reverse='versions')
    version = Required(str)
    composite_key(directory, version)
    date_start = Required(date)
    items = Set('DirectoryItem')


class DirectoryItem(db.Entity):
    identificator = PrimaryKey(int, auto=True)
    version = Required('DirectoryVersion', reverse='items')
    code = Required(str)
    composite_key(versions, code)
    value = Required(str)


class Admin(db.Entity):
    login = PrimaryKey(str)
    password_hash = Required(str)
    password_salt = Required(str)
    session = Set('Session', reverse='user')
    reg_time = Required(datetime)


class Session(db.Entity):
    identificator = PrimaryKey(str)
    user = Required('Admin', reverse='session')
    login_time = Required(datetime)
    last_active_time = Optional(datetime)
    ip = Optional(str)


