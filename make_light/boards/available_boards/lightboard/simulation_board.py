# board.py
#
# Copyright (C) 2015 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#
# Handle serial connection to lights board.


import os
from kano.logging import logger

from make_light.boards.base.shapes.rectangular_board import RectangularBoard
from make_light.paths import BOARDS_DIR


class KanoLightBoard(RectangularBoard):
    NAME = 'Lightboard'
    BOARD_DIR = os.path.join(BOARDS_DIR, 'lightboard')
    WELCOME_IMAGE_PATH = os.path.join(BOARD_DIR, 'welcome.gif')

    ASPECT_RATIO = 1.76
    MONOCHROME = True

    H_LED_COUNT = 9
    V_LED_COUNT = 14

    H_LED_SPACING = 0
    V_LED_SPACING = 0

    # These values can be higher, they have been decreased to allow led drawing
    # to overflow
    H_OFFSET = 55  # should be 60, to allow overflow
    V_OFFSET = 85  # should be 90, to allow overflow

    def __init__(self, debug=True):
        RectangularBoard.__init__(self)

        self._debug = debug

        self.connected = True

class Board(KanoLightBoard):
    pass
