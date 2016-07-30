# animation_plug.py
#
# Copyright (C) 2015 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#
# The widget that shows the animation
#
# This module is executed via Popen from MainWindow, and is bound to a widget in the app
# through a facility called GtkPlug. GtkPlug provides the ability to embed widgets from
# one process into another process in a fashion that is transparent to the user:
#
# https://developer.gnome.org/gtk3/stable/GtkPlug.html


import os
import sys
import imp
import json
import threading

from gi.repository import Gtk, GObject

from kano.logging import logger

logger.force_debug_level(None)

from make_light.gif.gif_recorder import GifRecorder
from make_light.paths import GIF_FRAMES_DIR, TEMP_DIR
from make_light.boards.router import BOARD_ROUTER

from make_light.paths import SIM_PIPE

# Multithread Gtk protection
GObject.threads_init()


class AnimationPlug(Gtk.Plug):
    """
    AnimationPlug controls a remote application Widget
    to display the animation - this is the simulator window
    """

    def __init__(self, board, plug_id, debug=False):
        Gtk.Plug.__init__(self)

        self.board = board
        self.debug = debug

        self.gif_recorder = GifRecorder(GIF_FRAMES_DIR)

        # PLUG_ID Is the window ID of the widget on the remote app,
        # on which we are allowed to work on - the Simulator image box.
        self.construct(plug_id)

        # This thread will listen for commands through stdin to play / stop animations
        self.stdin_thread = threading.Thread(target=self.thr_stdin_commands)
        self.stdin_thread.daemon = True
        self.stdin_thread.start()

        # FIXME: simulator box image is decorated?
        self.set_decorated(True)

        # Create an image widget to display the animation
        self.image = Gtk.Image.new_from_file(board.BOARD_IMAGE_PATH)

        self.connect('map-event', self.mapped)
        self.connect('delete-event', Gtk.main_quit)
        self.connect('realize', self._on_realize)

        # And insert the image widget into the remote one (gtk.box)
        self.add(self.image)
        self.show_all()

    def _on_realize(self, widget=None):
        sys.stdout.write('LOADING-COMPLETE\n')
        sys.stdout.flush()

    def thr_user_code_module(self):
        """
        This thread loads the code written by the user
        And renders the LEDs on top of the simulation board
        which is displayed in the simulator widget on the main app

        A function pass-through (imp) loads the user code as an embedded module
        """
        self._debug_('thr_user_code_module starts')
        try:
            self.board.all(False)
            imp.load_source("top", os.path.join(TEMP_DIR, "powerup-code-all.py"))
        except:
            import traceback
            error_text = traceback.format_exc().encode('string_escape')

            sys.stderr.write(error_text + '\n')
            sys.stderr.flush()

            sys.stdout.write('SCRIPT-ENCOUNTERED-ERROR\n')
            sys.stdout.flush()

            with open(SIM_PIPE, "w") as f:
                f.write(error_text + '\n')
                f.flush()

        else:
            # Send an ACKnowledge to the app that the animation has finished
            sys.stdout.write('ANIMATION-FINISHED\n')
            sys.stdout.flush()

        self._debug_('thr_user_code_module ends')

    def thr_stdin_commands(self):
        """
        Background thread listens for stdin command to start the animation.
        """
        self._debug_('stdin thread starting')
        while True:
            try:
                line = sys.stdin.readline()
            except AttributeError:
                # this happens when this process is terminated before the
                # QUIT-ANIMATION command is sent
                pass
            else:
                self._debug_('Stdin Command received: {}'.format(line))

                command = line.strip('\n')
                if command == 'START-ANIMATION':
                    # Start the animation thread
                    GObject.idle_add(self._launch_animation_thread)

                elif command == 'SAVE-ANIMATION':
                    GObject.idle_add(self._save_animation)

                elif command == 'QUIT-ANIMATION':
                    GObject.idle_add(self._quit_animation_process)

                else:
                    self._debug_('Stdin Command unknown')

    def _launch_animation_thread(self):
        self.gif_recorder.reset()

        # This is the thread that will run the user code
        self.user_code_thread = threading.Thread(target=self.thr_user_code_module)
        self.user_code_thread.daemon = True
        self.user_code_thread.start()

    def _save_animation(self):
        error = self.gif_recorder.save_frames()
        if error:
            # Send the serialized ERROR back to the Runner process
            error_str = json.dumps(error)
            sys.stdout.write(error_str + '\n')
        else:
            # Send an ACKnowledge to the app that the animation was saved
            sys.stdout.write('ANIMATION-SAVED\n')

        sys.stdout.flush()

    def _quit_animation_process(self):
        self._debug_('Terminating the simulator process')
        Gtk.main_quit()

    def set_image(self, im):
        """
        Render the next simulated image into the remote widget
        """
        self._debug_('called: set_image')
        self.pb = self.board.compose_image(im)
        self.gif_recorder.buffer_frame(im)
        GObject.idle_add(self.update)

    def update(self):
        self._debug_('called: update')
        self.image.set_from_pixbuf(self.pb)

    def mapped(self, widget, event):
        # FIXME: We do not need this anymore,
        # since we trigger the animation through a stdin command
        self._debug_('mapped')

    def _debug_(self, message):
        """
        Prints a debug message to the console to stderr
        if the class has been instantiated with debug=True
        """
        if self.debug:
            logger.debug(message)


def main(board, plug_id, debug=True):
    animation_plug = AnimationPlug(board=board, plug_id=plug_id, debug=debug)

    # the callback will be called by Gtk whenever the image needs be rendered
    animation_plug._debug_('setting callback from function')
    board.set_callback(animation_plug.set_image)
    animation_plug._debug_('launching GTK')
    Gtk.main()


if __name__ == "__main__":
    """
    We are being executed from a remote process - the main Make Light app
    """
    DEBUG = False

    # Collect debug parameter if requested
    if len(sys.argv) > 1 and sys.argv[1] == 'debug':
        DEBUG = True

    BOARD_NAME = os.environ['BOARD']
    BOARD_ROUTER.change_board(BOARD_NAME)
    BOARD = BOARD_ROUTER.board
    PLUG_ID = int(os.environ["PLUG_ID"])

    main(BOARD, PLUG_ID, DEBUG)
