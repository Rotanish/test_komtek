#! bin/python


from hashlib import sha3_512 as my_hash

from flask import session, request, jsonify
from pony.orm import *

from model import *
from helpers import *
from config import app, csrf, my_login, password_secret


# API
@app.route("/api/v0/get-all-directorys", methods=["GET"])
def get_reviews_all():
    db_dirs = select(directory for directory in Directory)
    dirs = []
    for db_dir in db_dirs:
        directory = db_dir.to_dict()
        directory['versions'] = [ver.to_dict() for ver in db_dir.versions]
        for i in range(len(directory['versions'])):
            directory['versions'][i]['date_start']= \
                directory['versions'][i]['date_start'].strftime('%d.%m.%Y')
        dirs.append(directory)
    return jfy(dirs)


# AUTH
@app.route("/api/v0/csrf", methods=["GET"])
def create_csrf():
    csrf.generate_key(session)
    return csrf.create_token(session)

@app.route('/api/v0/whoami', methods=["GET"])
def whoami():
    current_user = my_login.get_user(session)
    if current_user:
        return jsonify({
            'status': "auth",
        })
    else:
        return jsonify({
            'status': "not auth",
        })

@app.route("/api/v0/login", methods=["POST"])
def login():
    current_user = my_login.get_user(session)
    if current_user:
        return "Already logined"
    form = strip_form(request.get_json(True))
    if csrf.check_token(session, form['csrf']):
        valid = validate_log(form)
        if valid[0]:
            user = Admin.get(login=form['login'])
            if user:
                if user.password_hash == my_hash(password_secret + str(form['password']).encode() + user.password_salt.encode()).hexdigest():
                    my_login.login(session, user, request.remote_addr)
                    return "Login success"
            return "Wrong login or password"
        return valid[1]+' '+valid[2]
    return "not valid csrf. Please get csrf on /api/v0/csrf"

@app.route('/api/v0/logout', methods=["POST"])
def logout():
    current_user = my_login.get_user(session)
    if current_user:
        form = request.get_json(True)
        form = strip_form(form)
        if form['csrf'] and csrf.check_token(session, form['csrf']):
            my_login.logout(session)
            return "Logout success"
        else:
            return "not valid csrf. Please get csrf on /api/v0/csrf"
    return "not auth"
