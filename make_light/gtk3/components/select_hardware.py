# select_hardware.py
#
# Copyright (C) 2015 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#
# Dialog used to change HW

from gi.repository import Gtk, GdkPixbuf

from kano.gtk3.cursor import attach_cursor_events

from make_light.boards.available_boards import AVAILABLE_BOARDS


class SelectHardwareDialog(Gtk.Dialog):
    WIDTH = -1
    HEIGHT = -1
    _BUTTON_WIDTH = 200
    _BUTTON_HEIGHT = 200

    def __init__(self, parent):
        Gtk.Dialog.__init__(self, parent=parent)
        self.parent = parent

        self.set_decorated(False)  # custom top bar
        self.set_resizable(False)  # do not resize the dialog
        self.set_skip_taskbar_hint(True)  # hide dialog from taskbar
        self.set_size_request(self.WIDTH, self.HEIGHT)
        self.get_style_context().add_class('dialog')
        self.get_style_context().add_class('select-hardware')
        self.parent.blur()

        self.content = self.get_content_area()

        label = Gtk.Label('Select Hardware'.upper())
        label.get_style_context().add_class('title')
        label.get_style_context().add_class('main-menu-small-label')
        self.content.pack_start(label, False, False, 0)

        board_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        board_box.set_margin_right(5)
        board_box.set_margin_left(5)
        board_box.set_margin_bottom(10)
        self.content.pack_start(board_box, False, False, 0)

        for board_metadata in AVAILABLE_BOARDS.itervalues():
            board_button = self._create_board_button(
                board_metadata['name'],
                board_metadata['board_image']
            )
            board_box.pack_start(board_button, False, False, 0)

        self.show_all()

    def _create_board_button(self, board_name, board_img_path):
        button = Gtk.Button()
        button.get_style_context().add_class('board-select-button')
        button.set_margin_left(5)
        button.set_margin_right(5)
        button.connect('clicked', self._on_board_selected, board_name)
        attach_cursor_events(button)

        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        button.add(box)

        pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_size(
            board_img_path, self._BUTTON_WIDTH, self._BUTTON_HEIGHT
        )
        img = Gtk.Image.new_from_pixbuf(pixbuf)
        box.pack_start(img, False, False, 0)

        label = Gtk.Label(board_name)
        label.get_style_context().add_class('board-label')
        box.pack_start(label, False, False, 0)

        return button

    def _on_board_selected(self, dummy_button, board_name):
        self.response(Gtk.ResponseType.OK)
        self.data = {
            'board_name': board_name
        }
        self._close()

    def _close(self, button=None):
        self.parent.unblur()
        self.close()

    def get_responses(self):
        return self.data

