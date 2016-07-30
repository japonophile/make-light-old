# arrow_button.py
#
# Copyright (C) 2015 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#
# TODO: description


from gi.repository import Gtk


class ArrowButton(Gtk.Button):

    def __init__(self, text, **kwargs):
        Gtk.Button.__init__(self, **kwargs)

        box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        self.add(box)

        label = Gtk.Label(text)
        label.set_halign(Gtk.Align.START)
        label.set_margin_left(20)
        box.pack_start(label, True, True, 0)

        arrow = Gtk.Label('>')
        arrow.set_margin_right(20)
        box.pack_start(arrow, False, False, 0)
