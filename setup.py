#!/usr/bin/env python

# To use a consistent encoding
from codecs import open
from os import path

from setuptools import setup, find_packages


here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='storable',
    version='1.2.4',

    description='Python Perl Storable module',
    long_description=long_description,

    url='http://github.com/CowboyTim/python-storable',

    author='CowboyTim',
    author_email='aardbeiplantje@gmail.com',

    license='zlib/libpng',

    packages=find_packages(exclude=["tests.*", "tests", "docs"]),
    install_requires=[],
    extras_require={
        'test': ['pytest', 'verlib']
    },
    package_data={
        '': ['LICENSE.txt']
    },
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Programming Language :: Perl',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: zlib/libpng License',
    ]
)
