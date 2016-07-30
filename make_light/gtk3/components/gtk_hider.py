# gtk_hider.py
#
# Copyright (C) 2015 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#
# This creates a hidable widget


from gi.repository import Gtk


class GtkHider(Gtk.Notebook):
    # This class implements a way of hiding a Gtk
    # Widget without changing the layout.
    def __init__(self, child):
        Gtk.Notebook.__init__(self)
        self.set_show_tabs(False)
        self.set_show_border(False)
        self.set_scrollable(False)
        self.append_page(child, Gtk.Label())
        self.append_page(Gtk.Label(), Gtk.Label())

    def set_hidden(self, hidden):
        if hidden:
            self.next_page()
        else:
            self.prev_page()
