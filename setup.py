#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from setuptools import setup

# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "snotebook",
    version = "0.2.2",
    author = "Nicole A Montano",
    author_email = "n@nicolemon.com",
    description = ("A rudimentary CLI to write and organize text"),
    license = "MIT",
    keywords = "cli commandline terminal notes python",
    url = "https://github.com/nicolemon/snote",
    packages=['snote'],
    long_description=read('README.md'),
    classifiers=[
        "Development Status :: 3 - Alpha",
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.5',
    ],
    extras_require={
        'test': ['pytest'],
    },
    entry_points={
        'console_scripts': [
            'snote=snote:main',
        ],
    },
)
