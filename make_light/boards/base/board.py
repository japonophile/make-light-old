# board.py
#
# Copyright (C) 2015 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#
# Defines the structure of the Board class

import os

from make_light.boards.base.colours.colour_palette import ColourPalette
from make_light.paths import BOARDS_BASE_DIR


class FeatureNotSupportedError(NotImplementedError):
    pass


class Board(ColourPalette):
    BASE_PREAMBLE = None
    BASE_POSTAMBLE = None
    PREAMBLE = None
    POSTAMBLE = None
    BOARD_DIR = None


    @property
    def base_preamble(self):
        if self.BASE_PREAMBLE:
            return self.BASE_PREAMBLE

        preamble_path = os.path.join(BOARDS_BASE_DIR, 'base_preamble.py')
        if not os.path.exists(preamble_path):
            return ''

        try:
            with open(preamble_path, 'r') as f:
                self.__class__.BASE_PREAMBLE = f.read()

            return self.__class__.BASE_PREAMBLE
        except IOError:
            return ''

    @property
    def base_postamble(self):
        if self.BASE_POSTAMBLE:
            return self.BASE_POSTAMBLE

        postamble_path = os.path.join(BOARDS_BASE_DIR, 'base_postamble.py')
        if not os.path.exists(postamble_path):
            return ''

        try:
            with open(postamble_path, 'r') as f:
                self.__class__.BASE_POSTAMBLE = f.read()

            return self.__class__.BASE_POSTAMBLE
        except IOError:
            return ''

    @property
    def preamble(self):
        if self.PREAMBLE:
            return self.PREAMBLE

        preamble_path = os.path.join(self.BOARD_DIR, 'preamble.py')
        if not os.path.exists(preamble_path):
            return self.base_preamble

        try:
            with open(preamble_path, 'r') as f:
                self.__class__.PREAMBLE = self.base_preamble + f.read()

            return self.__class__.PREAMBLE
        except IOError:
            return self.base_preamble

    @property
    def postamble(self):
        if self.POSTAMBLE:
            return self.POSTAMBLE

        postamble_path = os.path.join(self.BOARD_DIR, 'postamble.py')
        if not os.path.exists(postamble_path):
            return self.base_postamble

        try:
            with open(postamble_path, 'r') as f:
                self.__class__.POSTAMBLE = f.read() + self.base_postamble

            return self.__class__.POSTAMBLE
        except IOError:
            return self.base_postamble

    def clear(self):
        raise NotImplementedError

    def on(self, *args):
        raise NotImplementedError

    def off(self, *args):
        raise NotImplementedError

    def all(self, *args, **kwargs):
        raise FeatureNotSupportedError

    def rectangle(self, A, B, **kwargs):
        raise FeatureNotSupportedError

    def line(self, A, B, **kwargs):
        raise FeatureNotSupportedError

    def circle(self, size, where, **kwargs):
        raise FeatureNotSupportedError

    def ellipse(self, A, B, **kwargs):
        raise FeatureNotSupportedError

    def arc(self, middle, start, end, **kwargs):
        raise FeatureNotSupportedError

    def triangle(self, a, b, c, **kwargs):
        raise FeatureNotSupportedError

    def polygon(self, points, **kwargs):
        raise FeatureNotSupportedError

    def scroll(self, text, delay=0.1, portrait=False, top=3):
        raise FeatureNotSupportedError

    def text(self, where, text):
        raise FeatureNotSupportedError

    def spin(self, delay, **kwargs):
        raise FeatureNotSupportedError
