# physical_board.py
#
# Copyright (C) 2015 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#
# Defines interfaces for the Lioghtboard physical Board

from make_light.boards.base.physical_board import PhysicalBoard
from make_light.boards.base.coords.cartesian import Cartesian
from make_light.boards.available_boards.lightboard.hw_io import LightBoardHW

api = LightBoardHW()

class KanoLightBoardPhysical(PhysicalBoard, Cartesian):
    MONOCHROME = True

    def __init__(self):
        PhysicalBoard.__init__(self)
        Cartesian.__init__(self, h_led_count=9, v_led_count=14)

    def detect_board(self):
        # FIXME
        return True

    def clear(self):
        api.set_to_all(False)

    def on(self, *args):
        leds, intensity = self._parse_coord_args(*args)
        api.set_elements(leds, intensity)

    def off(self, *args):
        api.unset_elements(args)

    def all(self, spec=True):
        api.set_to_all(spec)

    def rectangle(self, A, B, spec=True):
        api.rectangle(A, B, spec)

    def line(self, A, B, spec=True):
        api.line(A, B, spec)

    def circle(self, size, where, spec=True):
        api.circle(size, where, spec)

    def ellipse(self, A, B, spec=True):
        api.ellipse(A, B, spec)

    def arc(self, middle, start, end, spec=True):
        api.arc(middle, start, end, spec)

    def triangle(self, a, b, c, spec=True):
        api.triangle(a, b, c, spec)

    def polygon(self, points, spec=True):
        api.polygon(points, spec)

    def scroll(self, text, delay=0.1, portrait=False, top=3):
        api.scroll(text, delay, portrait, top)

    def text(self, where, text):
        api.text(where, text)

class Board(KanoLightBoardPhysical):
    pass
