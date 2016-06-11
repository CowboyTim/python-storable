#!/usr/bin/env python

from distutils.core import setup

setup(
    name             = 'storable',
    version          = '0.1.0',
    description      = 'Python Perl Storable module',
    author           = 'CowboyTim',
    author_email     = 'aardbeiplantje@gmail.com',
    url              = 'http://github.com/CowboyTim/python-storable',
    license          = 'LICENSE.txt',
    py_modules       = ['storable'],
    long_description = open('README.txt').read(),
    classifiers      = [
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Programming Language :: Perl',
        'Programming Language :: Python',
    ]
)
