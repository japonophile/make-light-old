# dimensions.py
#
# Copyright (C) 2015 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#
# TODO: description


import os

from gi.repository import Gdk


WINDOW_WIDTH = Gdk.Screen.width()
WINDOW_HEIGHT = Gdk.Screen.height()
WINDOW_PADDING = 20  # caution: this is used in many places

# if we're in Desktop Mode, then narrow the window height for LXPanel
if not os.getenv('KANO_BLOCKS_SCREEN_HEIGHT'):
    WINDOW_HEIGHT -= 44  # Taskbar height

HEADER_HEIGHT = 80

CHALLENGE_PROGRESS_WIDTH = 730
CHALLENGE_PROGRESS_HEIGHT = 170

VIEW_WIDTH = min(1024, WINDOW_WIDTH)
VIEW_HEIGHT = WINDOW_HEIGHT - HEADER_HEIGHT

HEADER_BUTTON_WIDTH = 110
HEADER_BUTTON_HEIGHT = 60

MAIN_MENU_BUTTON_HEIGHT = 85
