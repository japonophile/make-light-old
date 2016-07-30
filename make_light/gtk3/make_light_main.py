# make_light_main.py
#
# Copyright (C) 2015-2016 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#
# The main GUI window


import os
import atexit
import dbus
import dbus.service
from gi.repository import Gtk
from gi.types import GObjectMeta

from kano.gtk3.application_window import ApplicationWindow
from kano.gtk3.apply_styles import apply_common_to_screen, \
    apply_styling_to_screen
from kano.logging import logger
from kano_profile.challenge_progress_tracker import ChallengeProgressTracker
from kano_profile.app_progress_helpers import completed_at_least_one_challenge

from make_light.dbus_interface import BUS_NAME, OBJECT_PATH, BUS_INTERFACE
from make_light.gtk3.components.app_header import AppHeader
from make_light.gtk3.views.welcome_window import WelcomeWindow
from make_light.gtk3.views.main_menu_view import MainMenuView
from make_light.gtk3.views.group_list_view import GroupListView
from make_light.gtk3.views.challenge_list_view import ChallengeListView
from make_light.gtk3.views.challenge_view import ChallengeView
from make_light.gtk3.views.playground_view import PlaygroundView
from make_light.gtk3.dimensions import WINDOW_WIDTH, WINDOW_HEIGHT, \
    VIEW_WIDTH, VIEW_HEIGHT

from make_light.boards.router import BOARD_ROUTER, BoardNotSupportedError
from make_light.boards.router.ipc import remove_pipe
from make_light.logic import Challenges, CodeCache
from make_light.utils import show_confirm_dialog, AFFIRMATIVE_ACTION, \
    ABORT_ACTION
from make_light.errors import UNSUPPORTED_BOARD_ERROR, NOT_SAVED_WARNING
from make_light.paths import CSS_DIR, IMAGES_DIR
from make_light.utils import show_error_dialog
from make_light import app_name


class MakeLightMain(ApplicationWindow, dbus.service.Object):
    __metaclass__ = type(
        'Widget', (dbus.service.InterfaceType, GObjectMeta), {}
    )
    TITLE = "Make Light"

    def __init__(self, debug=False):
        ApplicationWindow.__init__(
            self, self.TITLE, WINDOW_WIDTH, WINDOW_HEIGHT
        )

        dbus.service.Object.__init__(self, BUS_NAME, OBJECT_PATH)

        self.debug_mode = debug
        self.router = None
        self.board = self._get_hardware_info()

        # window styling
        self.get_style_context().add_class('make-light')
        self.set_icon_from_file(os.path.join(IMAGES_DIR, 'make-light-logo.png'))
        apply_common_to_screen()
        apply_styling_to_screen(os.path.join(CSS_DIR, 'powerup.css'))

        # app window layout
        self.set_icon_from_file(os.path.join(IMAGES_DIR, 'make-light-logo.png'))

        window_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.set_main_widget(window_box)

        # add the app top bar
        header = AppHeader()
        header.connect('go-to-main-menu', self.show_main_menu)
        header.connect('quit-app', self.on_exit)
        atexit.register(self._clean_up)  # make sure we exit properly
        window_box.pack_start(header, False, False, 0)

        # add the container for the Views
        self.viewport = Gtk.Box(hexpand=True, vexpand=True)
        window_box.pack_start(self.viewport, False, False, 0)

        BOARD_ROUTER.connect('changed-board', self.on_hw_change)

        # if no challenges were completed, show a 'splash' screen
        if not completed_at_least_one_challenge(app_name):
            welcome = WelcomeWindow()

        # start the app with the MainMenuView
        self.current_view = None
        self.show_main_menu()

        # close the slash screen after the window has been loaded
        os.system('kano-stop-splash')

    def on_hw_change(self, widget, inp_str):
        Challenges.get_instance().device = inp_str

    def _get_hardware_info(self):
        """
        # Detect serial board
        # board = KanoLightBoard('/dev/ttyAMA0')
        board = LEDSpeaker()
        self.serial_available = board.detect_board()
        """

        self.serial_available = True

        # Bring up the networking between the 2 RaspberryPIs
        rc = os.system('sudo /usr/bin/powerup-network -u')
        self.ethernet_available = (rc == 0)

        BOARD_ROUTER.run_remotely = self.ethernet_available
        BOARD_ROUTER.initialise_hw_runners()

        # FIXME: Allow dynamic values for local and remote

        return BOARD_ROUTER.board

    def on_exit(self, dummy_button=None):
        complete = self._verify_code_saved()
        if not complete:
            return

        Gtk.main_quit()

    def _clean_up(self):
        ChallengeProgressTracker.get_instance().stop_all()
        os.system('sudo /usr/bin/powerup-network --down')
        BOARD_ROUTER.destroy_hw_runners()
        remove_pipe()

    def show_main_menu(self, button=None):
        if not self._confirm_exit():
            return
        ChallengeProgressTracker.get_instance().stop_all()
        main_menu = MainMenuView()
        main_menu.connect('go-to-group-list', self.show_challenge_groups)
        main_menu.connect('go-to-playground', self.show_playground)
        self._switch_view(main_menu)

    def show_challenge_groups(self, widget):
        if not self._confirm_exit():
            return
        # Ensure we will be showing the Challenge Groups for the right HW
        Challenges.get_instance().device = BOARD_ROUTER.board.NAME
        challenge_groups = GroupListView()
        challenge_groups.connect('go-to-main-menu', self.show_main_menu)
        challenge_groups.connect('go-to-challenge-list', self.show_challenges)
        self._switch_view(challenge_groups)

    def show_challenges(self, widgets, challege_group_id, no_confirm=False):
        if not no_confirm and not self._confirm_exit():
            return

        challenges = ChallengeListView(challege_group_id)
        challenges.connect('go-to-group-list', self.show_challenge_groups)
        challenges.connect('go-to-challenge', self.show_challenge)
        self._switch_view(challenges)

    def show_challenge(self, dummy_widget, challenge_group_id, challenge_id,
                       no_confirm=False):
        if not no_confirm:
            if not self._confirm_exit():
                return
        # Find the challenge information data and create a dict - set as
        # selected
        # And challenge details from the YAML file as a dictionary
        challenge = ChallengeView(
            self,
            Challenges.get_instance()[challenge_group_id][challenge_id]
        )
        challenge.connect('go-to-challenge-list', self.show_challenges)
        challenge.connect('go-to-challenge', self.show_challenge)
        self._switch_view(challenge)

    def show_playground(self, *dummy_args, **kwargs):
        no_confirm = kwargs.get('no_confirm', False)
        code = ''

        if not no_confirm:
            if not self._confirm_exit():
                return

        if len(dummy_args) == 2 and isinstance(dummy_args[1], basestring):
            code = dummy_args[1]

        file_path = kwargs.get('file_path', None)

        if file_path:
            code, board_type = CodeCache.get().load(file_path)
            if not BOARD_ROUTER.is_current_board(board_type):
                logger.info(
                    "File loaded is for board '{}', will change current board"
                    .format(board_type)
                )
                try:
                    BOARD_ROUTER.change_board(board_type)
                    self.on_hw_change('dummy', board_type)
                except BoardNotSupportedError:
                    show_error_dialog(UNSUPPORTED_BOARD_ERROR, self.window)
                else:
                    # The string attribute that gets passed with the refresh
                    # signal will be used to prepopulate the code editor
                    logger.debug('Will refresh with code {}'.format(code))

        playground = PlaygroundView(
            self,
            preloaded_text=code
        )

        playground.connect('go-to-main-menu', self.show_main_menu)
        playground.connect('refresh', self.show_playground)
        playground.connect('change-board', self._on_change_board_request)

        self._switch_view(playground)

    def _on_change_board_request(self, dummy_obj, board):
        proceed = self._verify_code_saved()

        if not proceed:
            return

        BOARD_ROUTER.change_board(board)
        self.show_playground(no_confirm=True)

    def _confirm_exit(self):
        switch = self._verify_code_saved()
        if not switch:
            return False
        return True

    def _switch_view(self, view):
        if BOARD_ROUTER and BOARD_ROUTER.is_running():
            BOARD_ROUTER.kill_code()

        self.current_view = view

        for widget in self.viewport:
            self.viewport.remove(widget)

        view.set_size_request(VIEW_WIDTH, VIEW_HEIGHT)
        self.viewport.add(view)
        self.show_all()

    def _verify_code_saved(self):
        """
        Prompt the user to save their code if they have not done so.

        Returns:
            True if the save was successful (and its OK to switch views),
            False otherwise.
        """
        try:
            if isinstance(self.current_view, ChallengeView) or \
               isinstance(self.current_view, PlaygroundView):
                code = self.current_view.light_ide.code_edit.get_code()
            else:
                # 1) nothing to save
                return True

        except Exception as e:
            logger.error('Something unexpected occurred when'
                         ' verfying if the code was saved - [{}]'.format(e))
            # 2) nasty error occurred
            return True

        is_code_saved = CodeCache.get().is_saved(code)

        if not is_code_saved:
            response = show_confirm_dialog(NOT_SAVED_WARNING, self)
            if response == AFFIRMATIVE_ACTION:
                complete = self.current_view.light_ide._on_save()
                return complete  # if saving failed, don't switch
            elif response == ABORT_ACTION:
                return False

        # 3) user chose to discard
        # 4) already saved
        return True

    def _run_on_view(self, method_name, *args, **kwargs):
        view = self.current_view

        try:
            method = getattr(view, method_name)
        except AttributeError:
            # Not implemented for this view
            return

        method(*args, **kwargs)

    @dbus.service.method(dbus_interface=BUS_INTERFACE)
    def make(self):
        self._run_on_view('make')

    @dbus.service.method(dbus_interface=BUS_INTERFACE)
    def load(self):
        self._run_on_view('load')

    @dbus.service.method(dbus_interface=BUS_INTERFACE, in_signature='s')
    def load_share(self, file_path):
        self._run_on_view('load', file_path=file_path)

    @dbus.service.method(dbus_interface=BUS_INTERFACE)
    def save(self):
        self._run_on_view('save')

    @dbus.service.method(dbus_interface=BUS_INTERFACE)
    def share(self):
        self._run_on_view('share')
