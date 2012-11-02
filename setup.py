#!/usr/bin/env python2

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


setup(
    name = 'bogie',
    version = '0.0',

    url = 'https://github.com/bhuztez/bogie',
    description = 'a simple wsgi server',

    classifiers = [
        "Development Status :: 1 - Planning",
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 2.7",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Server",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],

    author = 'bhuztez',
    author_email = 'bhuztez@gmail.com',

    packages = ['bogie', 'bogie.protocols', 'bogie.workers'],
    zip_safe = False,
)

