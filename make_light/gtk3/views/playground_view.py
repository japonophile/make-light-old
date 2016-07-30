# playground_view.py
#
# Copyright (C) 2015-2016 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#
# TODO: description


from gi.repository import Gtk, GObject

from kano.logging import logger
from kano_profile.challenge_progress_tracker import ChallengeProgressTracker

from make_light.gtk3.components.headers import PlaygroundHeader
from make_light.gtk3.components.light_ide import LightIDE, \
    PlaygroundSimulatorFooter
from make_light.logic import CodeCache
from make_light.boards.router import BOARD_ROUTER, BoardNotSupportedError
from make_light.utils import show_error_dialog
from make_light.errors import UNSUPPORTED_BOARD_ERROR


class PlaygroundView(Gtk.Box):

    __gsignals__ = {
        'go-to-main-menu': (GObject.SIGNAL_RUN_LAST, GObject.TYPE_NONE, ()),
        'refresh': (
            GObject.SIGNAL_RUN_LAST,
            GObject.TYPE_NONE,
            (
                GObject.TYPE_STRING,
            )
        ),
        'change-board': (
            GObject.SIGNAL_RUN_LAST,
            GObject.TYPE_NONE,
            (
                GObject.TYPE_STRING,
            )
        )
    }

    def __init__(self, window, load_file=None, preloaded_text=None):
        """ Playground view.
        :param preloaded_text: Text to add in the code editor on creation of
                               this view (has precedence over `load_file`)
        :type preloaded_text: basestring
        :param load_file: Path to a file to be loaded into the code editor. If
                          a value is given for the preloaded_text, that content
                          will be used instead
        :type load_file: basestring
        """
        Gtk.Box.__init__(self, orientation=Gtk.Orientation.VERTICAL)

        self.window = window

        # TODO: why does it fall to the left without this?
        self.set_hexpand(True)

        # the view layout
        self.playground_header = PlaygroundHeader()
        self.pack_start(self.playground_header, False, False, 0)

        self.light_ide = LightIDE(self.window, PlaygroundSimulatorFooter)
        self.pack_start(self.light_ide, True, True, 0)

        # connecting signals

        # The refresh signal will come with a string argument that potentially
        # contains the code to pre populate the code editor with
        self.light_ide.connect('refresh', self._on_receive_refresh)
        self.light_ide.connect('change-board', self._on_receive_change_board)

        # on BACK button pressed
        self.playground_header.connect(
            'back-button-pressed',
            self._on_back_pressed
        )
        if preloaded_text:
            # preloaded text takes precedence over loading of files
            self.light_ide.code_edit.set_code(preloaded_text)
        else:
            if load_file:
                code, board_type = CodeCache.get().load(load_file)

                # FIXME this is duplicated in light_ide, we need a better way
                # of dealing with it
                if BOARD_ROUTER.is_current_board(board_type):
                    self.light_ide.code_edit.set_code(code)
                else:
                    logger.info(
                        "File loaded is for board '{}', will change current board".format(board_type)
                    )
                    try:
                        BOARD_ROUTER.change_board(board_type)
                    except BoardNotSupportedError:
                        show_error_dialog(UNSUPPORTED_BOARD_ERROR, self.window)
                    else:
                        # The string attribute that gets passed with the refresh signal
                        # will be used to prepopulate the code editor
                        logger.debug('Will refresh with code {}'.format(code))
                        self.emit('refresh', code)
                        return None
        ChallengeProgressTracker.get_instance().start_playground(
            BOARD_ROUTER.board.NAME
        )

    def _on_back_pressed(self, widget=None):
        ChallengeProgressTracker.get_instance().stop_playground(
            BOARD_ROUTER.board.NAME
        )
        self.emit('go-to-main-menu')

    def _on_receive_refresh(self, widget=None, code=''):
        ChallengeProgressTracker.get_instance().stop_playground(
            BOARD_ROUTER.board.NAME
        )
        self.emit('refresh', code)

    def _on_receive_change_board(self, widget=None, board_type=''):
        ChallengeProgressTracker.get_instance().stop_playground(
            BOARD_ROUTER.board.NAME
        )
        self.emit('change-board', board_type)

    def make(self):
        self.light_ide.make()

    def load(self, file_path=None):
        self.light_ide.load(file_path=file_path)

    def save(self):
        self.light_ide.save()

    def share(self):
        self.light_ide.share()
