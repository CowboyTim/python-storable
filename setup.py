#!/usr/bin/env python3

from distutils.core import setup

setup(
    name             = 'storable',
    version          = '0.2.0',
    description      = 'Python Perl Storable module, python3 port',
    author           = 'CowboyTim <aardbeiplantje@gmail.com>, Quasar Jarosz <quasar@ja.rosz.org>',
    author_email     = 'quasar@ja.rosz.org',
    url              = 'https://github.com/quasarj/python-storable3',
    license          = 'LICENSE.txt',
    packages         = ['storable'],
    long_description = open('README.md').read(),
    classifiers      = [
        'Development Status :: 3 - Beta',
        'Intended Audience :: Developers',
        'Programming Language :: Perl',
        'Programming Language :: Python',
    ]
)
