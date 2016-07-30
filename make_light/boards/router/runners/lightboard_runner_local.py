# lightboard_runner_local.py
#
# Copyright (C) 2015 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#
# Runs a make-light script on local hardware

import os
import os.path
import subprocess
from gi.repository import GObject

from kano.logging import logger

from make_light.boards.router.runners.lightboard_runner import LightBoardRunner


class LightBoardRunnerLocal(LightBoardRunner):
    def __init__(self, board):
        LightBoardRunner.__init__(self, board)
        # We assume the board is plugged in if it was plugged in at the start
        self._available = True

    def _run_thr_target(self):
        stderr = None
        try:
            # Always kill old processes before running.
            cmdline = 'pkill -fx python.{} ; python {}'.format(
                self.filename, self.filename
            )
            e = subprocess.check_output(cmdline, shell=True,
                                        stderr=subprocess.STDOUT)
            print '#', e
        except subprocess.CalledProcessError as e:
            if e.returncode != 143:
                # For some reason this is the return code we get when we
                # terminate the animation plug when we send the quit command
                logger.error(
                    'Error executing code locally: {}, [rc: {}]'
                    .format(cmdline, e.returncode)
                )
                stderr = e.output
            print '#', e.output

        self.running = False
        GObject.idle_add(self.emit, "finished-run", stderr)

    def kill_code(self):
        """
        Stops the code running on the locally
        """

        cmdline = 'pkill -fx python.{}'.format(self.filename)
        '''
        `os.system` returns 16 bit value - the high byte is the return code
        More info: https://docs.python.org/2/library/os.html#os.system
        '''
        rc = os.system(cmdline) >> 8

        '''
        `pkill` return codes:
            0 - One or more processes were matched.
            1 - No processes were matched.
            2 - Invalid options were specified on the command line.
            3 - An internal error occurred.

        More info: https://www.freebsd.org/cgi/man.cgi?query=pkill&sektion=1
        '''

        if rc > 1:
            logger.error('Error killing local code: rc={}'.format(rc))
            return False

        msg = 'No script to kill' if rc else 'Script killed successfully'
        logger.debug(msg)

        self.running = False
        return True
