#coding=utf-8

import yaml
from onion.utils._dict import JsDict



def list2jsdict(v):
    result = [value2jsdict(t) for t in v]
    
    if isinstance(v, tuple):
        return tuple(result)
    else:
        return result

def dict2jsdict(v):
    j = JsDict()
    for key, value in v.iteritems():
        j[key] = value2jsdict(value) 

    return j

def value2jsdict(v):
    if isinstance(v, (tuple, list)):
        return list2jsdict(v)
    elif isinstance(v, dict):
        return dict2jsdict(v)
    else:
        return v


def load_yaml_settings(setting_path):
    try:
        with open(setting_path) as fp:
            v = yaml.load(fp)
    except:
        v = JsDict()
    else:
        v = dict2jsdict(v)
    return v



def update_settings(settings, patch):
    pass


if __name__ == '__main__':
    d = {'a': {'b': {'c': ['d', 'cc', {'p': ['aaa', 'bbb']}]}}}
    d = value2jsdict(d)
    print d.a.b.c

    print type(d.a.b.c[2])
    


