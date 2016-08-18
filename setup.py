#!/usr/bin/env python

from distutils.core import setup
import setuptools
import os
import sys

if '--install-scripts' not in sys.argv:
    sys.argv.push('--install-scripts=/usr/bin')

def get_locales():
    locale_dir = 'locale'
    locales = []

    for dirpath, dirnames, filenames in os.walk(locale_dir):
        for filename in filenames:
            locales.append(
                (os.path.join('/usr/share', dirpath),
                 [os.path.join(dirpath, filename)])
            )

    return locales


setup(name='Make Light',
      version='1.0',
      description='Turn code into light',
      author='Team Kano',
      author_email='dev@kano.me',
      url='https://github.com/KanoComputing/make-light',
      packages=['make_light'],
      scripts=['bin/make-light'],
      package_data={'make_light': ['media/css/*']},
      data_files=[
      ] + get_locales()
     )
