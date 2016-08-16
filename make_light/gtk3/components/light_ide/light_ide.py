# light_ide.py
#
# Copyright (C) 2015-2016 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#
# TODO: description

from gi.repository import Gtk, GObject

from kano.gtk3.cursor import attach_cursor_events
from kano.logging import logger
from kano_profile.badges import increment_app_state_variable_with_dialog
from kano_world.share_helpers import login_and_share

from make_light import app_name
from make_light.gtk3.components.light_ide.code_edit import CodeEdit
from make_light.gtk3.components.light_ide.save_dialog import \
    SaveDialog, ShareDialog
from make_light.gtk3.components.light_ide.load_dialog import LoadDialog
from make_light.gtk3.components.select_hardware import SelectHardwareDialog
from make_light.gtk3.dimensions import VIEW_WIDTH, WINDOW_PADDING, \
    HEADER_BUTTON_HEIGHT
from make_light.boards.router import BOARD_ROUTER, BoardNotSupportedError
from make_light.logic import CodeCache
from make_light.utils import show_error_dialog
from make_light.errors import UNSUPPORTED_BOARD_ERROR


class LightIDE(Gtk.Box):

    __gsignals__ = {
        'gif-encoded': (GObject.SIGNAL_RUN_LAST, GObject.TYPE_NONE, ()),
        'plug-error': (
            GObject.SIGNAL_RUN_LAST,
            GObject.TYPE_NONE,
            (
                GObject.TYPE_PYOBJECT,
            )
        ),
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

    def __init__(self, window, SimulatorFooter,
                 is_simulator_on=True):
        Gtk.Box.__init__(self, orientation=Gtk.Orientation.HORIZONTAL)

        self.window = window

        # container styling
        self.set_size_request(VIEW_WIDTH, -1)
        self.set_halign(Gtk.Align.CENTER)  # center component in window
        self.set_margin_top(WINDOW_PADDING)
        self.set_margin_bottom(WINDOW_PADDING)

        self.simulator_footer = SimulatorFooter()

        if isinstance(self.simulator_footer, ChallangeSimulatorFooter):
            self._configure_challenge_simulator_footer()
        elif isinstance(self.simulator_footer, PlaygroundSimulatorFooter):
            self._configure_playground_simulator_footer()

        # The left side of the IDE has the Code Editor
        self.code_edit = CodeEdit()
        self.code_edit.set_code('')
        self.code_edit.set_margin_left(WINDOW_PADDING)
        self.code_edit.set_margin_right(WINDOW_PADDING)
        self.code_edit.connect('make', self._run_code)
        self.code_edit.connect('kill', self._stop_code)
        # Prevent artifacts from resizing
        self.code_edit.set_redraw_on_allocate(True)
        self.pack_start(self.code_edit, True, True, 0)

        # The right side of the IDE has the Light Board Simulator
        # if not is_simulator_on:
        #     return

        simulator_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        simulator_box.set_margin_right(WINDOW_PADDING)

        self.anim_socket = Gtk.Socket()
        self.anim_socket.connect('realize', self._on_show)
        self.anim_socket.connect("plug-removed", lambda x: True)
        simulator_box.pack_start(self.anim_socket, False, False, 0)

        BOARD_ROUTER.set_animation_socket(self.anim_socket)
        BOARD_ROUTER.connect('gif-encoded', self._on_gif_encoded)
        BOARD_ROUTER.connect('plug-error', self._on_plug_error)

        simulator_box.pack_start(self.simulator_footer, False, False, 0)
        self.pack_start(simulator_box, False, False, 0)

    def _on_show(self, *args, **kwargs):
        BOARD_ROUTER.start_animation_process()
        self.code_edit.give_focus(self.window)

    def _configure_challenge_simulator_footer(self):
        self.simulator_footer.share_button.connect('clicked', self._on_share)
        self.simulator_footer.save_button.connect('clicked', self._on_save)

    def _configure_playground_simulator_footer(self):
        self.simulator_footer.change_hardware_button.connect(
            'clicked', self._on_switch_hardware
        )
        self.simulator_footer.save_button.connect('clicked', self._on_save)
        self.simulator_footer.share_button.connect('clicked', self._on_share)
        self.simulator_footer.load_button.connect('clicked', self._on_load)

    def _run_code(self, *args, **kwargs):
        self.code_edit.run_code()

    def make(self):
        self._run_code()

    def _stop_code(self, *args, **kwargs):
        self.code_edit.kill_code()

    def destroy(self):
        self._stop_code()

    def on_challenge_done(self, widget=None):
        # sanity check
        if isinstance(self.simulator_footer, ChallangeSimulatorFooter):
            # show the Share button when a challenge is done
            self.simulator_footer.set_buttons_sensitivity(True)

    def _on_gif_encoded(self, widget=None):
        # simply re-emiting the signals here
        self.emit('gif-encoded')

    def _on_plug_error(self, widget=None, error=None):
        if error:
            show_error_dialog(error, self.window)
            # TODO: properly return/handle error['error_code']

        self.emit('plug-error', error)

    def _on_share(self, button=None):
        self.share()

    def share(self):
        # TODO(?): if CodeEdit is empty, open file browser to Share sth Saved
        complete = self._on_save(DialogClass=ShareDialog)
        if complete:
            code_file = CodeCache.get().get_last_saved_code_file()
            title = CodeCache.get().get_last_saved_info()['title']

            no_errors, txt = login_and_share(code_file, title, app_name)
            if not no_errors:
                logger.error(txt)

            increment_app_state_variable_with_dialog(app_name, 'shared', 1)

    def _on_save(self, button=None, DialogClass=SaveDialog):
        # trigger the GIF encoding in the animation runner process
        BOARD_ROUTER.save_animation()

        # show the dialog with the share, title, and description
        dialog = DialogClass(self, self.window)
        response = dialog.run()
        dialog.destroy()

        # check if the user cancelled
        if response != Gtk.ResponseType.OK:
            return False

        # save the code, metadata, and GIF animation
        code = self.code_edit.get_code()
        info = dialog.get_responses()

        # Add the name of the board to the metadata
        info['hwRef'] = {'code': BOARD_ROUTER.board.NAME}
        error = CodeCache.get().save(code, info)

        # show any Standard Errors that might have occurred
        if error:
            show_error_dialog(error, self.window)
            return False

        return True

    def save(self):
        self._on_save()

    def _on_load(self, button=None):
        self.load()

    def load(self, file_path=None):
        if not file_path:
            file_path = self._select_file()

        self._load_from_file(file_path)

    def _select_file(self):
        # Open file manager
        dialog = LoadDialog(parent=self.get_toplevel())
        response = dialog.run()

        file_path = ""
        if response == Gtk.ResponseType.OK:
            file_path = dialog.get_filename()

        dialog.destroy()

        return file_path


    def _load_from_file(self, file_path):
        code, board_type = CodeCache.get().load(file_path)

        if BOARD_ROUTER.is_current_board(board_type):
            self.code_edit.set_code(code)
        else:
            logger.info(
                "File loaded is for board '{}', will change current board"
            )
            try:
                BOARD_ROUTER.change_board(board_type)
            except BoardNotSupportedError:
                show_error_dialog(UNSUPPORTED_BOARD_ERROR, self.window)
            else:
                # The string attribute that gets passed with the refresh signal
                # will be used to prepopulate the code editor
                self.emit('refresh', code)

    def _on_switch_hardware(self, dummy_button=None):
        win = self.get_toplevel()
        dialog = SelectHardwareDialog(parent=win)
        dialog.run()

        res = dialog.get_responses()
        try:
            board = res['board_name']
        except KeyError:
            return

        if not BOARD_ROUTER.is_current_board(board):
            dialog.hide()
            self.emit('change-board', board)


class TemplateSimulatorFooter(Gtk.Box):

    BUTTON_SPACING = 3  # px

    def __init__(self):
        Gtk.Box.__init__(self, orientation=Gtk.Orientation.VERTICAL)

        self._h_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        self.pack_end(self._h_box, True, True, 0)

        self.get_style_context().add_class('light-ide-simulator-footer')

    def _add_change_hardware_button(self):
        self.change_hardware_button = Gtk.Button(_('Switch Hardware').upper())
        self.change_hardware_button.set_size_request(-1, HEADER_BUTTON_HEIGHT)
        self.change_hardware_button.set_margin_bottom(self.BUTTON_SPACING)
        self.change_hardware_button.get_style_context().add_class(
            'light-ide-simulator-button'
        )
        attach_cursor_events(self.change_hardware_button)

        self.pack_start(self.change_hardware_button, True, True, 0)

    def _add_share_button(self):
        self.share_button = Gtk.Button(_('Share').upper())
        self.share_button.set_size_request(-1, HEADER_BUTTON_HEIGHT)
        self.share_button.get_style_context().add_class(
            'light-ide-simulator-button'
        )
        attach_cursor_events(self.share_button)

        self._h_box.pack_start(self.share_button, True, True, 0)

    def _add_save_button(self):
        self.save_button = Gtk.Button(_('Save').upper())
        self.save_button.set_size_request(-1, HEADER_BUTTON_HEIGHT)
        self.save_button.get_style_context().add_class(
            'light-ide-simulator-button'
        )
        attach_cursor_events(self.save_button)

        self._h_box.pack_start(self.save_button, True, True, 0)

    def _add_load_button(self):
        self.load_button = Gtk.Button(_('Load').upper())
        self.load_button.set_size_request(-1, HEADER_BUTTON_HEIGHT)
        self.load_button.get_style_context().add_class(
            'light-ide-simulator-button'
        )
        attach_cursor_events(self.load_button)

        self._h_box.pack_start(self.load_button, True, True, 0)


class ChallangeSimulatorFooter(TemplateSimulatorFooter):

    def __init__(self):
        TemplateSimulatorFooter.__init__(self)

        # the buttons specific to this footer
        self._add_share_button()
        self._add_save_button()

        # additional styling
        self.share_button.set_margin_right(self.BUTTON_SPACING)

        # hiding the SHARE / SAVE buttons by disabling them
        self.set_buttons_sensitivity(False)

    def set_buttons_sensitivity(self, is_sensitive):
        self.share_button.set_sensitive(is_sensitive)
        self.save_button.set_sensitive(is_sensitive)


class PlaygroundSimulatorFooter(TemplateSimulatorFooter):

    def __init__(self):
        TemplateSimulatorFooter.__init__(self)

        # the buttons specific to this footer
        self._add_change_hardware_button()
        self._add_share_button()
        self._add_save_button()
        self._add_load_button()

        # additional styling
        self.share_button.set_margin_right(self.BUTTON_SPACING)
        self.save_button.set_margin_right(self.BUTTON_SPACING)
