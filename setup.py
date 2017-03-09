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
    version='0.2.1',

    description='Python Perl Storable module',
    long_description=long_description,

    url='http://github.com/mike-hart/python-storable',

    author='Michael Hart',
    author_email='hart.michael+github@gmail.com',

    license='zlib/libpng',

    packages=find_packages(exclude=["tests.*", "tests", "docs"]),
    install_requires=[],
    package_data={'': ['LICENSE.txt']},
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Programming Language :: Perl',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: zlib/libpng License',
    ]
)
