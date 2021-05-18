#! bin/python


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
            return json.dumps([i.to_dict(related_objects=related_objects, with_collections=with_collections, only=only) for i in dbo], default=str)
        return json.dumps([i.to_dict(related_objects=related_objects, with_collections=with_collections, exclude=exclude) for i in dbo], default=str)
    elif type(dbo) == None or not dbo:
        return json.dumps({})
    else:
        if only:
            return json.dumps(dbo.to_dict(related_objects=related_objects, with_collections=with_collections, only=only), default=str)
        return json.dumps(dbo.to_dict(related_objects=related_objects, with_collections=with_collections, exclude=exclude), default=str)


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
        if not valid[key]['condition'](form[key]):
            return (False, 'Not valid', key)
    return (True,'Ok',None)

def validate_form_new_item(form, dir_list):
    valid = {
        'directory': {'required': True,
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

def validate_form_new_ver(form, dir_list):
    valid = {
        'directory': {'required': True,
                      'condition': lambda put: (type(put) is str and 
                                                put in dir_list
                                                )
                      },
        'version': {'required': True,
                    'condition': lambda put: (type(put) is str and 
                                              len(put)>0 and 
                                              not put in dir_list[form['directory']]
                                              )
                    },
        'date': {'required': True,
                 'condition': lambda put: (type(put) is str and
                                           len(put) > 4 and 
                                           len(put) <= 50
                                           )
                 },
    }
    return validate_form(form, valid)

def validate_form_new_dir(form):
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
