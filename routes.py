#! bin/python


import json
from hashlib import sha3_512 as my_hash
from datetime import datetime, date

from flask import session, request, jsonify
from pony.orm import *

from model import *
from helpers import *
from config import app, csrf, my_login, password_secret


# API
@app.route('/api/v0/get-list-directorys', methods=['GET'])
def get_list_directorys():
    '''Получение списка справочников'''
    # проверка страницы
    get_all = request.args.get('all', False, bool)
    try:
        page = int(request.args.get('page',1, type = int))
    except Exception as e:
        print(e)
        return jsonify({'status': 'error', 
                        'text': 'page not found',
                        'all_page':all_page
                        })

    # проверка даты
    date = request.args.get('date',None)
    if date:
        try:
            date = datetime.strptime(date, '%d.%m.%Y').date()
        except Exception as e:
            print(e)
            return jsonify({'status': 'error', 
                            'text': 'date not formated',
                            'date_farmat':'date.mount.year',
                            'example':'31.03.2021'
                            })

    # формирование страниц
    items_count = count(i for i in Directory)

    all_page = int((items_count-1)/10) + 1
    if page>all_page or page<1:
        return jsonify({'status': 'error', 
                        'text': 'page not found',
                        'all_page':all_page
                        })

    end = page*10
    if page == all_page or get_all:
        end = items_count

    # формирование списка
    db_dirs = select(
        d for d in Directory
        ).order_by(Directory.identificator)[page*10-10:end]
    if date:
        dirs = db_dirs_to_list_dict(db_dirs, date)
    else:
        dirs = db_dirs_to_list_dict(db_dirs)

    if get_all:
        return jfy({'directorys': dirs})
    return jfy({'directorys': dirs,
                'page': page,
                'all_page':all_page
                })

@app.route('/api/v0/get-directory', methods=['GET'])
def get_directory():
    '''Получение элементов справочникa'''
    # проверка страницы
    get_all = request.args.get('all', False, bool)
    try:
        page = int(request.args.get('page',1, type = int))
    except Exception as e:
        print(e)
        return jsonify({'status': 'error', 
                        'text': 'page not found',
                        'all_page':all_page
                        })

    # проверка id
    id_dir = request.args.get('id_dir', None, int)
    if id_dir == None:
        return jsonify({'status': 'error', 
                        'text': 'parameter id_dir not found',
                        })
    if not count(i for i in Directory if i.identificator == id_dir):
        return jsonify({'status': 'error', 
                        'text': 'id directory not found',
                        })

    version = request.args.get('version','')
    if version:
        if version not in select(
                v.version for v in DirectoryVersion if v.directory.identificator==id_dir
                ):
            return jsonify({'status': 'error', 
                            'text': 'version directory not found',
                            })

    # формирование списка
    if version:
        db_ver = select(
            v for v in DirectoryVersion if (v.directory.identificator == id_dir and 
                                   v.version == version
                                   )
            ).order_by(desc(DirectoryVersion.date_start)).first()
    else:
        db_ver = select(
            v for v in DirectoryVersion if (
                                   v.directory.identificator == id_dir and
                                   v.date_start < date.today()
                                   )
            ).order_by(desc(DirectoryVersion.date_start)).first()


    # формирование страниц
    items_count = len(db_ver.items)
    all_page = int((items_count-1)/10) + 1
    if page>all_page or page<1:
        return jsonify({'status': 'error', 
                        'text': 'page not found',
                        'all_page':all_page
                        })

    end = page*10
    if page == all_page or get_all:
        end = items_count

    items = dbo_to_json(
        db_ver.items.order_by(DirectoryItem.identificator)[page*10-10:end]
        )

    if get_all:
        return jsonify({'items': items})
    return jsonify({'items': items,
                'page': page,
                'all_page':all_page
                })

@app.route('/api/v0/directory/new', methods=['POST'])
def directory_new():
    '''Создание справочника'''
    # Проверка пользователя
    current_user = my_login.get_user(session)
    if current_user:
        form = request.get_json(True)
        form = strip_form(form)
        if form['csrf'] and csrf.check_token(session, form['csrf']):
            valid = validate_form_new_dir(form)
            if valid[0]:
                Directory(name=form['name'],
                          short_name=form['short_name'],
                          description=form['description']
                          )
                return jsonify({'status': 'OK', 
                                'test': 'new directory success'})
            return valid[1]+' '+valid[2]
        else:
            return jsonify({'status': 'error', 
                            'text': 'not valid csrf. Get csrf on /api/v0/csrf'
                            })
    return jsonify({'status': 'error', 
                    'text': 'not auth'
                    })

@app.route('/api/v0/directory/edit', methods=['POST'])
def directory_edit():
    '''Изменение справочника'''
    return {'status': 'coming soon'}
    # Проверка пользователя
    current_user = my_login.get_user(session)
    if current_user:
        form = request.get_json(True)
        form = strip_form(form)
        if form['csrf'] and csrf.check_token(session, form['csrf']):
            valid = validate_form_new_dir(form)
            if valid[0]:

                return jsonify({'status': 'OK', 
                                'test': 'edit directory success'})
            return valid[1]+' '+valid[2]
        else:
            return jsonify({'status': 'error', 
                            'text': 'not valid csrf. Get csrf on /api/v0/csrf'
                            })
    return jsonify({'status': 'error', 
                    'text': 'not auth'
                    })

@app.route('/api/v0/directory/delete', methods=['POST'])
def directory_delete():
    '''Удаление справочника'''
    return {'status': 'coming soon'}
    # Проверка пользователя
    current_user = my_login.get_user(session)
    if current_user:
        form = request.get_json(True)
        form = strip_form(form)
        if form['csrf'] and csrf.check_token(session, form['csrf']):
            valid = validate_log(form)
            if valid[0]:

                return jsonify({'status': 'OK', 
                                'test': 'delete directory success'})
            return valid[1]+' '+valid[2]
        else:
            return jsonify({'status': 'error', 
                            'text': 'not valid csrf. Get csrf on /api/v0/csrf'
                            })
    return jsonify({'status': 'error', 
                    'text': 'not auth'
                    })

@app.route('/api/v0/version/new', methods=['POST'])
def version_new():
    '''Создание версии'''
    return {'status': 'coming soon'}
    # Проверка пользователя
    current_user = my_login.get_user(session)
    if current_user:
        form = request.get_json(True)
        form = strip_form(form)
        if form['csrf'] and csrf.check_token(session, form['csrf']):
            valid = validate_log(form)
            if valid[0]:

                return jsonify({'status': 'OK', 
                                'test': 'new version success'})
            return valid[1]+' '+valid[2]
        else:
            return jsonify({'status': 'error', 
                            'text': 'not valid csrf. Get csrf on /api/v0/csrf'
                            })
    return jsonify({'status': 'error', 
                    'text': 'not auth'
                    })

@app.route('/api/v0/version/edit', methods=['POST'])
def version_edit():
    '''Изменение версии'''
    return {'status': 'coming soon'}
    # Проверка пользователя
    current_user = my_login.get_user(session)
    if current_user:
        form = request.get_json(True)
        form = strip_form(form)
        if form['csrf'] and csrf.check_token(session, form['csrf']):
            valid = validate_log(form)
            if valid[0]:

                return jsonify({'status': 'OK', 
                                'test': 'edit version success'})
            return valid[1]+' '+valid[2]
        else:
            return jsonify({'status': 'error', 
                            'text': 'not valid csrf. Get csrf on /api/v0/csrf'
                            })
    return jsonify({'status': 'error', 
                    'text': 'not auth'
                    })

@app.route('/api/v0/version/delete', methods=['POST'])
def version_delete():
    '''Удаление версии'''
    return {'status': 'coming soon'}
    # Проверка пользователя
    current_user = my_login.get_user(session)
    if current_user:
        form = request.get_json(True)
        form = strip_form(form)
        if form['csrf'] and csrf.check_token(session, form['csrf']):
            valid = validate_log(form)
            if valid[0]:

                return jsonify({'status': 'OK', 
                                'test': 'delete version success'})
            return valid[1]+' '+valid[2]
        else:
            return jsonify({'status': 'error', 
                            'text': 'not valid csrf. Get csrf on /api/v0/csrf'
                            })
    return jsonify({'status': 'error', 
                    'text': 'not auth'
                    })

@app.route('/api/v0/item/new', methods=['POST'])
def item_new():
    '''Создание элемента'''
    return {'status': 'coming soon'}
    # Проверка пользователя
    current_user = my_login.get_user(session)
    if current_user:
        form = request.get_json(True)
        form = strip_form(form)
        if form['csrf'] and csrf.check_token(session, form['csrf']):
            valid = validate_log(form)
            if valid[0]:

                return jsonify({'status': 'OK', 
                                'test': 'new item success'})
            return valid[1]+' '+valid[2]
        else:
            return jsonify({'status': 'error', 
                            'text': 'not valid csrf. Get csrf on /api/v0/csrf'
                            })
    return jsonify({'status': 'error', 
                    'text': 'not auth'
                    })

@app.route('/api/v0/item/edit', methods=['POST'])
def item_edit():
    '''Изменение элемента'''
    return {'status': 'coming soon'}
    # Проверка пользователя
    current_user = my_login.get_user(session)
    if current_user:
        form = request.get_json(True)
        form = strip_form(form)
        if form['csrf'] and csrf.check_token(session, form['csrf']):
            valid = validate_log(form)
            if valid[0]:

                return jsonify({'status': 'OK', 
                                'test': 'edit item success'})
            return valid[1]+' '+valid[2]
        else:
            return jsonify({'status': 'error', 
                            'text': 'not valid csrf. Get csrf on /api/v0/csrf'
                            })
    return jsonify({'status': 'error', 
                    'text': 'not auth'
                    })

@app.route('/api/v0/item/delete', methods=['POST'])
def item_delete():
    '''Удаление элемента'''
    return {'status': 'coming soon'}
    # Проверка пользователя
    current_user = my_login.get_user(session)
    if current_user:
        form = request.get_json(True)
        form = strip_form(form)
        if form['csrf'] and csrf.check_token(session, form['csrf']):
            valid = validate_log(form)
            if valid[0]:

                return jsonify({'status': 'OK', 
                                'test': 'delete item success'})
            return valid[1]+' '+valid[2]
        else:
            return jsonify({'status': 'error', 
                            'text': 'not valid csrf. Get csrf on /api/v0/csrf'
                            })
    return jsonify({'status': 'error', 
                    'text': 'not auth'
                    })

# AUTH
@app.route('/api/v0/csrf', methods=['GET'])
def create_csrf():
    '''Генерация CSRF токена'''
    csrf.generate_key(session)
    return csrf.create_token(session)

@app.route('/api/v0/whoami', methods=['GET'])
def whoami():
    '''Статус пользователя'''
    current_user = my_login.get_user(session)
    if current_user:
        return jsonify({
            'status': 'auth',
        })
    else:
        return jsonify({
            'status': 'not auth',
        })

@app.route('/api/v0/login', methods=['POST'])
def login():
    current_user = my_login.get_user(session)
    if current_user:
        return jsonify({'status': 'error', 
                        'text': 'Already logined'
                        })
    form = strip_form(request.get_json(True))
    if csrf.check_token(session, form['csrf']):
        valid = validate_log(form)
        if valid[0]:
            user = Admin.get(login=form['login'])
            if user:
                if user.password_hash == my_hash(
                        password_secret + 
                        str(form['password']).encode() + 
                        user.password_salt.encode()
                        ).hexdigest():
                    my_login.login(session, user, request.remote_addr)
                    return jsonify({'status': 'OK', 
                                    'text': 'Login success'
                                    })
            return jsonify({'status': 'error', 
                            'text': 'Wrong login or password'
                            })
        return valid[1]+' '+valid[2]
    return jsonify({'status': 'error', 
                    'text': 'not valid csrf. Get csrf on /api/v0/csrf'
                    })


@app.route('/api/v0/logout', methods=['POST'])
def logout():
    current_user = my_login.get_user(session)
    if current_user:
        form = request.get_json(True)
        form = strip_form(form)
        if form['csrf'] and csrf.check_token(session, form['csrf']):
            my_login.logout(session)
            return jsonify({'status': 'OK', 
                            'text': 'Logout success'
                            })
        else:
            return jsonify({'status': 'error', 
                            'text': 'not valid csrf. Get csrf on /api/v0/csrf'
                            })
    return jsonify({'status': 'error', 
                    'text': 'not auth'
                    })