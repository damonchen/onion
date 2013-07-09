#coding=utf-8

import os
from distutils.core import setup
import onion

with open('README.md') as fp:
    long_description = fp.read()

packages, package_data = [], {}

root_dir = os.path.dirname(__file__)
if root_dir != '':
    os.chdir(root_dir)
onion_dir = 'onion'


def fullsplit(path, result=None):
    if result is None:
        result = []

    head, tail = os.path.split(path)
    if head == '':
        return [tail] + result
    if head == path:
        return result
    return fullsplit(head, [tail] + result)

EXCLUDE_FROM_PACKAGES = [
    'onion.template_files',        
    'onion.template_files.app',
    'onion.template_files.project',
]

def is_package(package_name):
    for pkg in EXCLUDE_FROM_PACKAGES:
        if package_name.startswith(pkg):
            return False
    return True


for dirpath, dirnames, filenames in os.walk(onion_dir):
    dirnames[:] = [d for d in dirnames if not d.startswith('.') and d != '__pycache__']
    parts = fullsplit(dirpath)
    package_name = '.'.join(parts)

    if '__init__.py' in filenames and is_package(package_name):
        packages.append(package_name)
    elif filenames:
        relative_path = []
        
        while '.'.join(parts) not in packages:
            relative_path.append(parts.pop())
        relative_path.reverse()

        path = os.path.join(*relative_path)
        package_files = package_data.setdefault('.'.join(parts), [])
        package_files.extend([os.path.join(path, f) for f in filenames])

setup(
    name='onion',
    version=onion.__version__,
    url='http://git.oschina.net/damon/onion',
    license=onion.__license__,
    author='Damon Chen',
    author_email='netubu@gmail.com',
    description='onion is a web framework with torando, sqlalchemy and jinja',
    long_description = long_description,
    packages = packages,
    package_data=package_data,
    scripts = ['scripts/onion-admin'],
)

