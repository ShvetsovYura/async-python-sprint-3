from datetime import datetime


def json_object_hook(obj):
    """ Преобразует указанные поля к datetime """
    ret = {}
    for key, value in obj.items():
        if key in {'created_at', 'delivery_at'} and value is not None:
            ret[key] = datetime.strptime(value, '%Y-%m-%d %H:%M:%S')
        else:
            ret[key] = value
    return ret
