# main_menu_view.py
#
# Copyright (C) 2015 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#
# TODO: description


import os

from gi.repository import Gtk, GObject, GdkPixbuf

from kano.gtk3.cursor import attach_cursor_events

from make_light.gtk3.components.arrow_button import ArrowButton
from make_light.gtk3.components.select_hardware import SelectHardwareDialog
from make_light.gtk3.dimensions import VIEW_WIDTH, MAIN_MENU_BUTTON_HEIGHT, \
    WINDOW_PADDING
from make_light.paths import IMAGES_DIR
from make_light.boards.router import BOARD_ROUTER


class MainMenuView(Gtk.Box):

    __gsignals__ = {
        'go-to-group-list': (GObject.SIGNAL_RUN_LAST, GObject.TYPE_NONE, ()),
        'go-to-playground': (GObject.SIGNAL_RUN_LAST, GObject.TYPE_NONE, ())
    }

    def __init__(self):
        Gtk.Box.__init__(self, orientation=Gtk.Orientation.HORIZONTAL)

        # setting up the layout
        self.set_size_request(-1, VIEW_WIDTH)
        self.set_halign(Gtk.Align.CENTER)
        self.set_hexpand(True)

        left_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        left_box.set_margin_top(WINDOW_PADDING * 3)
        left_box.set_margin_left(WINDOW_PADDING * 2)
        self.pack_start(left_box, False, False, 0)

        right_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        right_box.set_margin_top(WINDOW_PADDING * 3)
        right_box.set_margin_left(WINDOW_PADDING)
        right_box.set_margin_right(WINDOW_PADDING)
        self.pack_start(right_box, True, True, 0)

        # populating the left box
        # TODO: replace this with hardware detection
        welcome_label = Gtk.Label(_('Welcome').upper())
        welcome_label.set_halign(Gtk.Align.START)
        welcome_label.get_style_context().add_class('main-menu-small-label')
        welcome_label.set_margin_bottom(WINDOW_PADDING)
        left_box.pack_start(welcome_label, False, False, 0)

        self._placeholder_gif = Gtk.Image()
        self._set_placeholder_gif()
        left_box.pack_start(self._placeholder_gif, False, False, 0)

        change_hardware_btn = Gtk.Button(_('Change hardware').upper())
        change_hardware_btn.connect('clicked', self._on_change_hardware_clicked)
        change_hardware_btn.set_size_request(-1, -1)
        change_hardware_btn.get_style_context().add_class('main-menu-gray-button')
        change_hardware_btn.get_style_context().add_class('main-menu-small-button')
        attach_cursor_events(change_hardware_btn)
        left_box.pack_start(change_hardware_btn, False, False, 0)

        # populating the right box
        get_started_label = Gtk.Label(_('Get started').upper())
        get_started_label.set_halign(Gtk.Align.START)
        get_started_label.get_style_context().add_class('main-menu-small-label')
        get_started_label.set_margin_bottom(WINDOW_PADDING)
        right_box.pack_start(get_started_label, False, False, 0)

        # TODO: use a custom ArrowButton component instead of Gtk.Button
        self.challenges_button = ArrowButton(_('Play Challenges'))
        self.challenges_button.set_size_request(-1, MAIN_MENU_BUTTON_HEIGHT)
        self.challenges_button.get_style_context().add_class('main-menu-orange-button')
        self.challenges_button.set_margin_bottom(15)
        self.challenges_button.connect('clicked', self._on_challenges_button_clicked)
        attach_cursor_events(self.challenges_button)
        right_box.pack_start(self.challenges_button, False, False, 0)

        self.playground_button = ArrowButton(_('Code in the Playground'))
        self.playground_button.set_size_request(-1, MAIN_MENU_BUTTON_HEIGHT)
        self.playground_button.get_style_context().add_class('main-menu-gray-button')
        self.playground_button.connect('clicked', self._on_playground_button_clicked)
        attach_cursor_events(self.playground_button)
        right_box.pack_start(self.playground_button, False, False, 0)

    def _on_challenges_button_clicked(self, button=None):
        self.emit('go-to-group-list')

    def _on_playground_button_clicked(self, button=None):
        self.emit('go-to-playground')

    def _on_change_hardware_clicked(self, button=None):
        win = self.get_toplevel()
        dialog = SelectHardwareDialog(parent=win)
        dialog.run()

        res = dialog.get_responses()
        board = res['board_name']

        if not BOARD_ROUTER.is_current_board(board):
            BOARD_ROUTER.change_board(board)
            self._set_placeholder_gif()


    def _set_placeholder_gif(self):
        dummy, ext = os.path.splitext(BOARD_ROUTER.board.WELCOME_IMAGE_PATH)

        if ext == '.gif':
            self._placeholder_gif.set_from_file(
                BOARD_ROUTER.board.WELCOME_IMAGE_PATH
            )
        else:
            pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_size(
                BOARD_ROUTER.board.WELCOME_IMAGE_PATH, 375, 375
            )
            self._placeholder_gif.set_from_pixbuf(pixbuf)
