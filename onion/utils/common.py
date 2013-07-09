#coding=utf-8

import os, sys, logging, shutil

from onion.utils._dict import JsDict
from onion.utils.tools import load_yaml_settings

logger = logging.getLogger('onion')


class MyPKG(object):

    @staticmethod
    def resource_filename(module, path):
        mod = import_module(module)
        p = os.path.dirname(mod.__file__)
        if path:
            p = os.path.join(p, path)

        return p

    @staticmethod
    def resouce_listdir(module, path):
        d = MyPKG.resource_filename(module, path)
        return os.listdir(d)

    @staticmethod
    def resource_isdir(module, path):
        d = MyPKG.resource_filename(module, path)
        return os.path.isdir(d)


try:
    import pkg_resources as pkg
except ImportError:
    pkg = MyPKG


def _resolve_name(name, package, level):
    if not hasattr(package, 'rindex'):
        raise ValueError("'package not set to a string'")

    dot = len(package)
    for x in xrange(level, 1, -1):
        try:
            dot = package.rindex('.', 0, dot)
        except ValueError:
            raise ValueError('attempted relative import beyond top-level package')

    return '%s.%s' %(package[:dot], name)


def import_module(name, package=None):

    if name.startswith('.'):
        if not package:
            raise TypeError("relative imports require the 'package' argument")
        level = 0
        for ch in name:
            if ch != '.':
                break
            level += 1
        name = _resolve_name(name[level:], package, level)

    __import__(name)
    return sys.modules[name]


def get_app_path(app):
    if hasattr(app, '__file__'):
        app_path = os.path.dirname(app.__file__)
    else:
        mod = import_module(app)
        app_path = os.path.dirname(mod.__file__)

    return app_path


def get_settings(app_path, settings_file):
    print '===============', app_path, settings_file
    settings_path = os.path.join(app_path, settings_file)
    settings = load_yaml_settings(settings_path)
    return settings


def _load_apps(app_name, settings_file):
    apps = []
    settings = JsDict()

    try:
        mod = import_module(app_name)
    except ImportError:
        mod = None
    else:
        apps.append(mod)

        settings = get_settings(os.path.dirname(mod.__file__), settings_file)
        apps.extend(load_installed_app(settings, settings_file))

    return apps, settings


def load_installed_app(settings, settings_file):
    installed_apps = settings.INSTALLED_APPS
    
    if installed_apps is None or not isinstance(installed_apps, (tuple, list)):
        return []

    apps = []
    for app in installed_apps:
        print '**************', app
        _apps, _settings = _load_apps(app, settings_file)
        apps.extend(_apps)
        settings.update(_settings)

    return apps


def load_apps(apps_path, settings_file='settings.yaml'):
    print '----------', apps_path, settings_file
    settings = get_settings(apps_path, settings_file)
    apps = load_installed_app(settings, settings_file)


    if not settings.GLOBAL:
        settings.GLOBAL = JsDict()

    if not settings.GLOBAL.FILESYSTEM_ENCODING:
        settings.GLOBAL.FILESYSTEM_ENCODING = sys.getfilesystemencoding() or settings.GLOBAL.DEFAULT_ENCODING
 
    return apps, settings


def extract_file(module, path, dst, verbose=False, replace=True):
    filename = pkg.resource_filename(module, path)
    base = os.path.basename(filename)

    if os.path.isdir(dst):
        dfile = os.path.join(dst, base)
    else:
        dfile = dst

    if replace or not os.path.exists(dfile):
        shutil.copy2(filename, dfile)
        if verbose:
            print 'Copy %s to %s' %(filename, dfile)

def extract_dirs(mod, path, dst, verbose=False, exclude=None, exclude_ext=None, recursion=True, replace=True):
    default_exclude = ['.git']
    default_exclude_ext = ['.pyc', '.pyo', '.bak', '.tmp', '.swp']

    exclude = exclude or []
    exclude_ext = exclude_ext or []


    if not os.path.exists(dst):
        os.makedirs(dst)
        if verbose:
            print 'Make directory %s' %dst

    for r in pkg.resource_listdir(mod, path):
        if r in exclude or r in default_exclude:
            continue

        fpath =os.path.join(path, r)
        if pkg.resource_isdir(mod, fpath):
            if recursion:
                extract_dirs(mod, fpath, os.path.join(dst, r), verbose, exclude, exclude_ext, recursion, replace)
        else:
            ext = os.path.splitext(fpath)[1]
            if ext in exclude_ext or ext in default_exclude_ext:
                continue
            extract_file(mod, fpath, dst, verbose, replace)

def get_app_handlers(app):
    return []

if __name__ == '__main__':
    print load_apps('/home/damon/workspace/fox/apps')
    print import_module('onion.contrib.auth')



