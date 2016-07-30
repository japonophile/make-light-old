# board.py
#
# Copyright (C) 2015 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#
# Defines LED speaker base board

import os
import time

from make_light.boards.base.shapes.circular_board import CircularBoard
from make_light.paths import BOARDS_DIR

class LEDSpeaker(CircularBoard):
    NAME = 'LED Speaker'
    BOARD_DIR = os.path.join(BOARDS_DIR, 'led_speaker')
    WELCOME_IMAGE_PATH = os.path.join(BOARD_DIR, 'welcome.gif')

    LED_RINGS = [10]
    RING_RADII = [150]
    RING_THICKNESSES = [25]
    RING_OFFSETS = [-90]

    def __init__(self):
        CircularBoard.__init__(self)

        self.connected = True

    def arc(self, start, end, **kwargs):
        CircularBoard.arc(self, 0, start, end, **kwargs)

    def circle(self, **kwargs):
        CircularBoard.circle(self, 0, **kwargs)

    def spin(self, delay, **kwargs):
        col = self._parse_colour_kwargs(**kwargs)

        for led in board:
            self.on(led, colour=col)
            time.sleep(delay)
            self.clear()

class Board(LEDSpeaker):
    pass
