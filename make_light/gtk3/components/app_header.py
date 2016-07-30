# app_header.py
#
# Copyright (C) 2015 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#
# This is the Application Header
# It contains the 'Make Light' name on the left and the [X] button on the right


from os.path import join

from gi.repository import Gtk, GObject

from kano.gtk3.cursor import attach_cursor_events

from make_light.gtk3.dimensions import WINDOW_WIDTH, VIEW_WIDTH, \
    HEADER_HEIGHT, WINDOW_PADDING
from make_light.paths import IMAGES_DIR


class AppHeader(Gtk.EventBox):

    __gsignals__ = {
        'go-to-main-menu': (GObject.SIGNAL_RUN_LAST, GObject.TYPE_NONE, ()),
        'quit-app': (GObject.SIGNAL_RUN_LAST, GObject.TYPE_NONE, ())
    }

    def __init__(self):
        Gtk.EventBox.__init__(self)
        self.set_size_request(WINDOW_WIDTH, HEADER_HEIGHT)
        self.set_halign(Gtk.Align.FILL)
        self.get_style_context().add_class('make-light-app-header')

        box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        box.set_size_request(VIEW_WIDTH, HEADER_HEIGHT)
        box.set_halign(Gtk.Align.CENTER)
        self.add(box)

        # the Make Light logo image
        logo = Gtk.Image.new_from_file(join(IMAGES_DIR, 'make-light-logo.png'))
        logo.set_margin_left(WINDOW_PADDING)
        box.pack_start(logo, False, False, 0)

        # the 'Make Light' title button
        title_button = Gtk.Button('Make Light')
        title_button.connect('clicked', self._on_title_button)
        title_button.get_style_context().add_class('make-light-header-button')
        title_button.set_margin_top(10)
        attach_cursor_events(title_button)
        box.pack_start(title_button, False, False, 0)

        # the app close button
        close_button = Gtk.Button('x')
        close_button.connect('clicked', self._on_close_button)
        close_button.get_style_context().add_class('make-light-close-button')
        close_button.set_size_request(HEADER_HEIGHT, HEADER_HEIGHT)
        attach_cursor_events(close_button)
        box.pack_end(close_button, False, False, 0)

    def _on_title_button(self, button=None):
        self.emit('go-to-main-menu')

    def _on_close_button(self, button=None):
        self.emit('quit-app')
