#!/usr/bin/env python

from setuptools import setup

setup(
    name='storable',
    version='0.2.0',
    description='Python Perl Storable module',
    author='MikeHart',
    author_email='hart.michael+github@gmail.com',
    url='http://github.com/mike-hart/python-storable',
    license='LICENSE.txt',
    py_modules=['storable'],
    long_description=open('README.txt').read(),
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Programming Language :: Perl',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
    ]
)
