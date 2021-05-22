#! bin/python

from datetime import datetime
import json
from collections.abc import Iterable
from flask import jsonify


def jfy(obj):
    return jsonify(json.loads(json.dumps(obj, default=str)))

def dbo_to_json(dbo, metod="only", exclude='', only=[]):
    related_objects = False
    with_collections = False
    if metod == "all":
        related_objects = True
        with_collections = True
    if isinstance(dbo, Iterable):
        if only:
            return [i.to_dict(related_objects=related_objects, with_collections=with_collections, only=only) for i in dbo]
        return [i.to_dict(related_objects=related_objects, with_collections=with_collections, exclude=exclude) for i in dbo]
    elif type(dbo) == None or not dbo:
        return {}
    else:
        if only:
            return dbo.to_dict(related_objects=related_objects, with_collections=with_collections, only=only)
        return dbo.to_dict(related_objects=related_objects, with_collections=with_collections, exclude=exclude)

def db_dirs_to_list_dict(db_dirs, date=None):
    '''Перевод обьекта справочника базы данных в список словарей'''
    dirs = []
    for db_dir in db_dirs:
        directory = db_dir.to_dict()
        
        # добавление информации о версиях справочника
        if date:
            directory['versions'] = [ver.to_dict() for ver in db_dir.versions if ver.date_start < date]
        else:
            directory['versions'] = [ver.to_dict() for ver in db_dir.versions]

        # приведение даты к формату
        for i in range(len(directory['versions'])):
            directory['versions'][i]['date_start']= \
                directory['versions'][i]['date_start'].strftime('%d.%m.%Y')

        if not date or len(directory['versions']) != 0:
            dirs.append(directory)
    return dirs


def strip_form(form):
    s_form = {}
    for key in form:
        if type(key) is str:
            s_key = key.strip()
        else:
            s_key = key
        if type(form[key]) is str:
            s_val = form[key].strip()
        else:
            s_val = form[key]
        s_form[s_key] = s_val
    return s_form

def validate_form(form, valid):
    for key in valid:
        if not key in form and key['required']:
            return (False, 'Not fount', key)
        try:
            v = valid[key]['condition'](form[key])
        except Exception as e:
            print(e)
            return (False, 'Not valid', key)
        if not v:
            return (False, 'Not valid', key)
    return (True,'Ok',None)

def validate_form_item(form, dir_list):
    valid = {
        'id_dir': {'required': True,
                      'condition': lambda put: (type(put) is str and 
                                                put in dir_list
                                                )
                      },
        'version': {'required': True,
                    'condition': lambda put: (type(put) is str and 
                                              put in dir_list[form['directory']]
                                              )
                    },
        'code': {'required': True,
                 'condition': lambda put: (type(put) is str and
                                           len(put) > 0 and 
                                           len(put) <= 50000
                                           )
                 },
        'value': {'required': True,
                  'condition': lambda put: (type(put) is str and 
                                            len(put) > 0 and 
                                            len(put) <= 50000
                                            )
                  }
    }
    return validate_form(form, valid)

def validate_form_ver(form, dir_list):
    valid = {
        'id_dir': {'required': True,
                      'condition': lambda put: (type(put) is str and 
                                                put in dir_list
                                                )
                      },
        'version': {'required': True,
                    'condition': lambda put: (type(put) is str and 
                                              len(put)>0
                                              )
                    },
        'date': {'required': True,
                 'condition': lambda put: (type(put) is str and
                                           len(put) > 4 and 
                                           len(put) <= 50 and
                                           datetime.strptime(put, '%d.%m.%Y')
                                           )
                 },
    }
    return validate_form(form, valid)

def validate_form_dir(form):
    valid = {
        'name': {'required': True,
                 'condition': lambda put: (type(put) is str and 
                                           len(put)>0,
                                           len(put) <= 50000
                                           )
                 },
        'short_name': {'required': False,
                       'condition': lambda put: (type(put) is str and 
                                                 len(put)>0,
                                                 len(put) <= 50000
                                                 )
                       },
        'description': {'required': False,
                        'condition': lambda put: (type(put) is str and 
                                                  len(put)>0,
                                                  len(put) <= 50000
                                                  )
                        },
    }
    return validate_form(form, valid)

def validate_log(form):
    valid = {
        'login': {'required': True,
                  'condition': lambda put: (type(put) is str and 
                                            len(put) <= 25 and 
                                            len(put) >= 1 and 
                                            " " not in put
                                            )
                  },
        'password': {'required': True,
                     'condition': lambda put: (type(put) is str and 
                                               len(put) <= 50 and 
                                               len(put) >= 1
                                               )
                     }
    }
    return validate_form(form, valid)
