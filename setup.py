#!/usr/bin/env python

from distutils.core import setup
import setuptools
import os
import sys

if '--install-scripts' not in sys.argv:
    sys.argv.append('--install-scripts=/usr/bin')

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
      packages=['make_light', 'make_light.boards', 'make_light.boards.available_boards',
          'make_light.boards.available_boards.led_speaker', 'make_light.boards.available_boards.lightboard',
          'make_light.boards.base', 'make_light.boards.base.colours', 'make_light.boards.base.coords',
          'make_light.boards.base.shapes', 'make_light.boards.router', 'make_light.boards.router.runners',
          'make_light.gif', 'make_light.gtk3', 'make_light.gtk3.components', 'make_light.gtk3.components.light_ide',
          'make_light.gtk3.views', 'make_light.logic', 'powerup_network' ],
      scripts=['bin/make-light'],
      package_data={'make_light': ['media/css/*']},
      data_files=[
      ] + get_locales()
     )
