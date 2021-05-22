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
@app.route('/api/v1/get-list-directorys', methods=['GET'])
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

@app.route('/api/v1/get-directory', methods=['GET'])
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
                        'text': 'directory not found',
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

# Directory
@app.route('/api/v1/directory/new', methods=['POST'])
@my_login.current_user(session)
@csrf.check_post(session, request)
def directory_new():
    '''Создание справочника'''
    form = strip_form(form)
    valid = validate_form_dir(form)
    if valid[0]:
        Directory(name=form['name'],
                  short_name=form.get('short_name'),
                  description=form.get('description')
                  )
        return jsonify({'status': 'OK', 
                        'text': 'new directory success'})
    return jsonify({
        'status': 'error', 
        'text': valid[1]+' '+valid[2],
        })

@app.route('/api/v1/directory/edit', methods=['POST'])
@my_login.current_user(session)
@csrf.check_post(session, request)
def directory_edit():
    '''Изменение справочника'''
    form = strip_form(form)
    # проверка id
    if 'id_dir' not in form:
        return jsonify({'status': 'error', 
                        'text': 'parameter id_dir not found',
                        })
    valid = validate_form_dir(form)
    if valid[0]:
        id_dir = form['id_dir']
        if not Directory.get(identificator = id_dir):
            return jsonify({'status': 'error', 
                            'text': 'directory not found',
                            })
        Directory.get(
            identificator = id_dir
        ).set(
            name=form['name'],
            short_name=form['short_name'],
            description=form['description']
            )
        return jsonify({'status': 'OK', 
                        'text': 'edit directory success'})
    return jsonify({
        'status': 'error', 
        'text': valid[1]+' '+valid[2],
        })

@app.route('/api/v1/directory/delete', methods=['POST'])
@my_login.current_user(session)
@csrf.check_post(session, request)
def directory_delete():
    '''Удаление справочника'''
    form = strip_form(form)
    if 'id_dir' not in form:
        return jsonify({'status': 'error', 
                        'text': 'parameter id_dir not found',
                        })
    id_dir = form['id_dir']
    if not Directory.get(identificator = id_dir):
            return jsonify({'status': 'error', 
                            'text': 'directory not found',
                            })
    Directory.get(identificator=id_dir).delete()
    return jsonify({'status': 'OK', 
                    'text': 'delete directory success'})

# Version
@app.route('/api/v1/version/new', methods=['POST'])
@my_login.current_user(session)
@csrf.check_post(session, request)
def version_new():
    '''Создание версии'''
    form = strip_form(form)
    dir_list = [i.identificator for i in Directory.get_all()]
    valid = validate_form_ver(form, dir_list)
    if valid[0]:
        id_dir = form['id_dir']
        version = form['version']
        if DirectoryVersion.get(
            directory = Directory.get(identificator=id_dir),
            version = version
            ):
            return jsonify({'status': 'error', 
                            'text': 'version already exists',
                            })
        DirectoryVersion(
            directory=form['directory'],
            version=form['version'],
            date_start=datetime.strptime(
                form['date'], '%d.%m.%Y'
            ).date(),
        )
        return jsonify({'status': 'OK', 
                        'text': 'new version success'})
    return jsonify({
        'status': 'error', 
        'text': valid[1]+' '+valid[2],
        })

@app.route('/api/v1/version/edit', methods=['POST'])
@my_login.current_user(session)
@csrf.check_post(session, request)
def version_edit():
    '''Изменение версии'''
    form = strip_form(form)
    dir_list = [i.identificator for i in Directory.get_all()]
    # проверка id
    if 'id_dir' not in form:
        return jsonify({'status': 'error', 
                        'text': 'parameter id_dir not found',
                        })
    if 'version' not in form:
        return jsonify({'status': 'error', 
                        'text': 'parameter version not found',
                        })
    valid = validate_form_ver(form, dir_list)
    if valid[0]:
        id_dir = form['id_dir']
        version = form['version']
        if not DirectoryVersion.get(
            directory = Directory.get(identificator=id_dir),
            version = version
            ):
            return jsonify({'status': 'error', 
                            'text': 'version not found',
                            })
        DirectoryVersion.get(
            directory=Directory.get(identificator=id_dir),
            version=version
        ).set(
            date_start=datetime.strptime(
                form['date'], '%d.%m.%Y'
                ).date(),
        )
        return jsonify({'status': 'OK', 
                        'text': 'edit version success'})
    return jsonify({
        'status': 'error', 
        'text': valid[1]+' '+valid[2],
        })

@app.route('/api/v1/version/delete', methods=['POST'])
@my_login.current_user(session)
@csrf.check_post(session, request)
def version_delete():
    '''Удаление версии'''
    form = strip_form(form)
    if 'id_dir' not in form:
        return jsonify({'status': 'error', 
                        'text': 'parameter id_dir not found',
                        })
    if 'version' not in form:
        return jsonify({'status': 'error', 
                        'text': 'parameter version not found',
                        })
    id_dir = form['id_dir']
    version = form['version']
    if not DirectoryVersion.get(
            directory = Directory.get(identificator=id_dir),
            version = version
            ):
        return jsonify({'status': 'error', 
                        'text': 'version not found',
                        })
    DirectoryVersion.get(
        directory=Directory.get(identificator=id_dir),
        version=version
    ).delete()
    return jsonify({'status': 'OK', 
                    'text': 'delete version success'})

# ITEM
@app.route('/api/v1/item/new', methods=['POST'])
@my_login.current_user(session)
@csrf.check_post(session, request)
def item_new():
    '''Создание элемента'''
    form = strip_form(form)
    if 'id_dir' not in form:
        return jsonify({'status': 'error', 
                        'text': 'parameter id_dir not found',
                        })
    if 'version' not in form:
        return jsonify({'status': 'error', 
                        'text': 'parameter version not found',
                        })
    dir_list = [i.identificator for i in Directory.get_all()]
    valid = validate_form_item(form, dir_list)
    if valid[0]:
        id_dir = form['id_dir']
        version = form['version']
        if DirectoryItem.get(
                version=DirectoryVersion.get(
                    directory=Directory.get(identificator=id_dir),
                    version=version
                    ),
                code=form['code']
                ):
            return jsonify({'status': 'error', 
                            'text': 'code already exists',
                            })
        DirectoryItem(
            version=DirectoryVersion.get(
                    directory = Directory.get(identificator=id_dir),
                    version = version
                ),
            code=form['code'],
            value=form['value']
            )
        return jsonify({'status': 'OK', 
                        'text': 'new item success'})
    return jsonify({
        'status': 'error', 
        'text': valid[1]+' '+valid[2],
        })

@app.route('/api/v1/item/edit', methods=['POST'])
@my_login.current_user(session)
@csrf.check_post(session, request)
def item_edit():
    '''Изменение элемента'''
    form = strip_form(form)
    if 'id_dir' not in form:
        return jsonify({'status': 'error', 
                        'text': 'parameter id_dir not found',
                        })
    if 'version' not in form:
        return jsonify({'status': 'error', 
                        'text': 'parameter version not found',
                        })
    dir_list = [i.identificator for i in Directory.get_all()]
    valid = validate_form_item(form, dir_list)
    if valid[0]:
        id_dir = form['id_dir']
        version = form['version']
        if not DirectoryItem.get(
                version=DirectoryVersion.get(
                    directory=Directory.get(identificator=id_dir),
                    version=version
                    ),
                code=form['code']
                ):
            return jsonify({'status': 'error', 
                            'text': 'code not found',
                            })
        DirectoryItem.get(
            version=DirectoryVersion.get(
                directory=Directory.get(identificator=id_dir),
                version=version
                ),
            code=form['code']
        ).set(
            value=form['value']
        )
        return jsonify({'status': 'OK', 
                        'text': 'edit item success'})
    return jsonify({
        'status': 'error', 
        'text': valid[1]+' '+valid[2],
        })

@app.route('/api/v1/item/delete', methods=['POST'])
@my_login.current_user(session)
@csrf.check_post(session, request)
def item_delete():
    '''Удаление элемента'''
    form = strip_form(form)
    if 'id_dir' not in form:
        return jsonify({'status': 'error', 
                        'text': 'parameter id_dir not found',
                        })
    if 'version' not in form:
        return jsonify({'status': 'error', 
                        'text': 'parameter version not found',
                        })
    id_dir = form['id_dir']
    version = form['version']
    if not DirectoryItem.get(
            version=DirectoryVersion.get(
                directory=Directory.get(identificator=id_dir),
                version=version
                ),
            code=form['code']
            ):
        return jsonify({'status': 'error', 
                        'text': 'code not found',
                        })
    DirectoryItem.get(
        version=DirectoryVersion.get(
            directory=Directory.get(identificator=id_dir),
            version=version
            ),
        code=form['code']
    ).delete()
    return jsonify({'status': 'OK', 
                        'text': 'delete item success'})

# AUTH
@app.route('/api/v1/csrf', methods=['GET'])
def create_csrf():
    '''Генерация CSRF токена'''
    csrf.generate_key(session)
    return csrf.create_token(session)

@app.route('/api/v1/whoami', methods=['GET'])
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

@app.route('/api/v1/login', methods=['POST'])
@csrf.check_post(session, request)
def login():
    current_user = my_login.get_user(session)
    if current_user:
        return jsonify({'status': 'error', 
                        'text': 'Already logined'
                        })
    form = strip_form(form)
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
    return jsonify({
        'status': 'error', 
        'text': valid[1]+' '+valid[2],
        })


@app.route('/api/v1/logout', methods=['POST'])
@my_login.current_user(session)
@csrf.check_post(session, request)
def logout():
    my_login.logout(session)
    return jsonify({'status': 'OK', 
                    'text': 'Logout success'
                    })
