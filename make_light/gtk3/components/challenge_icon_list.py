# challenge_icon_list.py
#
# Copyright (C) 2015 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#
# TODO: description


from gi.repository import Gtk, Gdk, GObject
from gi.repository.GdkPixbuf import Pixbuf

from kano.gtk3.scrolled_window import ScrolledWindow

from make_light.gtk3.dimensions import VIEW_WIDTH


class ChallengeIconList(Gtk.EventBox):
    """
    """

    __gsignals__ = {
        'icon-clicked': (
            GObject.SIGNAL_RUN_LAST, GObject.TYPE_NONE, (GObject.TYPE_PYOBJECT, GObject.TYPE_PYOBJECT)),
    }

    def __init__(self, challenge_like, filler_class):
        Gtk.EventBox.__init__(self, hexpand=True, vexpand=True)

        self.challenge_like = challenge_like
        self.filler_class = filler_class

        # create the iconview that collects the challenges
        iconview = self._create_iconview()
        self._fill_iconview()
        self.add(iconview)

        self.show_all()

    def _create_iconview(self):
        """
        Creates an icon listview inside a scrollable.
        Returns the scrollable widget.
        """
        self.flowbox = flowbox = Gtk.FlowBox()
        flowbox.set_column_spacing(0)
        flowbox.set_row_spacing(5)
        flowbox.set_halign(Gtk.Align.CENTER)

        # Trick to make the items not be in one single column
        flowbox.set_min_children_per_line(2)

        flowbox.set_margin_top(15)
        flowbox.set_margin_bottom(0)
        flowbox.set_margin_left(15)
        flowbox.set_margin_right(0)

        # The listview will be contained inside a scrolledview
        scrolledwindow = ScrolledWindow(hexpand=True, vexpand=True)
        scrolledwindow.apply_styling_to_widget()

        # expand the scrollview horizontally, then insert the listview
        # FIXME: Shouldn't need to hardcode this
        scrolledwindow.set_min_content_width(VIEW_WIDTH)
        scrolledwindow.set_halign(Gtk.Align.CENTER)

        scrolledwindow.add(flowbox)

        return scrolledwindow

    def _fill_iconview(self):
        """
        Collects the list of challenges and inserts them in the Liststore,
        bound to the icon Listview
        """
        for challenge in self.challenge_like:
            tile = self.filler_class(challenge)

            if challenge.locked:
                tile.set_sensitive(False)
            else:
                tile.connect('clicked', self._on_icon_button_click)

            self.flowbox.insert(tile, -1)

    def _on_icon_button_click(self, button):
        self.emit('icon-clicked', None, button)
