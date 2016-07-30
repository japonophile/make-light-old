# simulation_runner.py
#
# Copyright (C) 2015 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#
# The main GUI window


import os
import json
import threading
import subprocess

from gi.repository import GObject

from make_light.boards.router.runners.lightboard_runner import LightBoardRunner

from make_light.paths import SIM_PIPE


class SimulationRunner(LightBoardRunner):

    __gsignals__ = {
        'gif-encoded': (GObject.SIGNAL_RUN_LAST, GObject.TYPE_NONE, ()),
        'plug-loaded': (GObject.SIGNAL_RUN_LAST, GObject.TYPE_NONE, ()),
        'plug-error': (GObject.SIGNAL_RUN_LAST, GObject.TYPE_NONE, (GObject.TYPE_PYOBJECT,))
    }

    def __init__(self, board, anim_socket, debug=False):
        LightBoardRunner.__init__(self, board)

        self.debug = debug
        self.anim_socket = anim_socket
        self.anim_process = None
        self._available = True

    def run_code(self):
        """
        Send a signal to the Animation process to start the animation
        """

        # TODO: Disable any UI components ?

        if self.anim_process and self.anim_process.returncode is None:
            # Send a command the process through the stdin pipe
            self.anim_process.stdin.write('START-ANIMATION\n')
            self.running = True

    def save_animation(self):
        """
        """
        if self.anim_process and self.anim_process.returncode is None:
            self.anim_process.stdin.write('SAVE-ANIMATION\n')

    def stop_animation(self):
        """
        Terminates the animation process - Should be called when application quits
        """
        if self.anim_process and self.anim_process.returncode is None:
            self.anim_process.stdin.write('QUIT-ANIMATION\n')

    def thr_animation_completed(self, anim_process):
        # Expect a confirmation message

        # This thread corresponds to one anim process.
        # A new thread is started whenever a new anim_process is started.

        while anim_process.returncode is None:
            response = anim_process.stdout.readline()
            command = response.strip('\n')
            # print 'RESPONSE RECEIVED "{}"'.format(command)

            if command == 'ANIMATION-SAVED':
                GObject.idle_add(self.emit, 'gif-encoded')

            elif command == 'ANIMATION-FINISHED':
                self.running = False
                GObject.idle_add(self.emit, "finished-run", "")

            elif command == 'SCRIPT-ENCOUNTERED-ERROR':
                self.running = False

                with open(SIM_PIPE) as f:
                    error_text = f.readline()

                error_text = error_text.strip('\n')
                error_text = error_text.decode('string_escape')
                GObject.idle_add(self.emit, "finished-run", error_text)

            elif command == 'LOADING-COMPLETE':
                GObject.idle_add(self.emit, 'plug-loaded')

            else:
                try:
                    # we have just received a Standard Error
                    error = json.loads(command)
                    GObject.idle_add(self.emit, 'plug-error', error)

                except ValueError:
                    # received debugging messages (or not a Standard Error)
                    # TODO: print them here, currently not used
                    pass
                except:
                    # TODO: logger.warn here throws an AttributeError, its None
                    pass
            anim_process.poll()

    def start_animation_process(self):
        """
        Starts the animation process in the background
        """
        script_path = os.path.join(
            os.path.dirname(os.path.realpath(__file__)),
            "animation_plug.py"
        )

        # Setup how we are going to start the separate process
        # Nothing is reading stderr yet, so don't redirect it
        # otherwise we will  lock up.
        redirected_stderr = None

        # If in Debug mode, we want to see what the simulator is doing,
        # to the console
        debug_parameter = 'debug' if self.debug else ''

        command = ['python', script_path, debug_parameter]
        new_env = os.environ.copy()
        new_env['POWERUP_TEST'] = '1'
        new_env['PLUG_ID'] = str(self.anim_socket.get_id())
        new_env['BOARD'] = self.board.NAME

        # TODO: Remove this?
        # Only here to facilitate running of local version of package
        dir_path = os.path.abspath(
            os.path.join(os.path.dirname(__file__), '..')
        )
        if not dir_path.startswith('/usr'):
            new_env['PYTHONPATH'] = os.getcwd()

        self.anim_process = subprocess.Popen(
            command,
            env=new_env,
            bufsize=1,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=redirected_stderr
        )

        # Start a thread that will listen for animation completion
        self.thread_id_animation_complete = threading.Thread(
            target=self.thr_animation_completed,
            args=(self.anim_process,))
        self.thread_id_animation_complete.daemon = True
        self.thread_id_animation_complete.start()

    def kill_animation_process(self):
        if self.running:
            self.stop_animation()
            self.anim_process.terminate()
            self.anim_process.poll()
            if self.anim_process.returncode is None:
                self.anim_process.kill()

    def kill_code(self):
        try:
            # Only kill the process when it is still running
            # as the AnimationPlug can run more than one process.
            if self.running:
                self.kill_animation_process()
                self.start_animation_process()
        except:
            print "kill_animation() failed"

    def destroy(self):
        self.kill_animation_process()
