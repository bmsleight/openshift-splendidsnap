#!/usr/bin/env python

from setuptools import setup

setup(
    # GETTING-STARTED: set your app name:
    name='SplendidSnap',
    # GETTING-STARTED: set your app version:
    version='1.0',
    # GETTING-STARTED: set your app description:
    description='Splendid Snap App',
    # GETTING-STARTED: set author name (your name):
    author='B Sleight',
    # GETTING-STARTED: set author email (your email):
    author_email='example@example.com',
    # GETTING-STARTED: set author url (your url):
    url='http://www.python.org/sigs/distutils-sig/',
    # GETTING-STARTED: define required django version:
    install_requires=[
        'Django==1.8.4',
        'django-bootstrap3',
        'reportlab',
        'tweepy',
        'Wand',
    ],
    dependency_links=[
        'https://pypi.python.org/simple/django/'
    ],
)
