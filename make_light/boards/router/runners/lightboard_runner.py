# lightboard_runner.py
#
# Copyright (C) 2015 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#
# Controls the widget where the user enters python code.
# A ssh trust relationship is setup automatically.
# Provides for transferring and executing the code
# remotely on the Powerup Kit unit


import threading
from gi.repository import GObject


from make_light import lib_version
from make_light.paths import POWERUP_LOCAL_PATH, POWERUP_LOCAL_DIRNAME, FONTS_DIR


class LightBoardRunner(GObject.GObject):
    __gsignals__ = {
        "finished-run": (GObject.SIGNAL_RUN_FIRST, None,
                         (GObject.TYPE_STRING,)),
        "powerup-status": (GObject.SIGNAL_RUN_FIRST, None,
                           (GObject.TYPE_BOOLEAN,
                            GObject.TYPE_BOOLEAN,
                            GObject.TYPE_BOOLEAN,)),
        "error": (GObject.SIGNAL_RUN_FIRST, None, (GObject.TYPE_STRING,)),
    }

    def __init__(self, board):
        GObject.GObject.__init__(self)
        self.running = False
        self.filename = ''
        self._available = False
        self.board = board

    @property
    def available(self):
        return self._available

    def is_running(self):
        """
        Query whether the code is running
        """
        return self.running

    def kill_code(self):
        raise NotImplementedError

    def run_code(self, filename):
        self.filename = filename
        self.running = True

        thread = threading.Thread(target=self._run_thr_target)
        thread.daemon = True
        thread.start()

    def _run_thr_target(self):
        raise NotImplementedError
