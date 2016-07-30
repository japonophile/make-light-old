# challenge_list_view.py
#
# Copyright (C) 2015 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#
# Dialog with a list of available Challenges is shown for selection, inside an
# scrollable icon list
#


from gi.repository import Gtk, GObject

from make_light.logic import Challenges
from make_light.gtk3.components.headers import ListHeader
from make_light.gtk3.components.challenge_icons import ChallengeIcon
from make_light.gtk3.components.challenge_icon_list import ChallengeIconList


class ChallengeListView(Gtk.Box):
    """
    """

    __gsignals__ = {
        'go-to-group-list': (GObject.SIGNAL_RUN_LAST, GObject.TYPE_NONE, ()),
        'go-to-challenge':
            (GObject.SIGNAL_RUN_LAST, GObject.TYPE_NONE, (str, str))
    }

    def __init__(self, challege_group_id):
        Gtk.Box.__init__(self, orientation=Gtk.Orientation.VERTICAL)

        # add a Header to this View
        self.header = ListHeader(
            white_text='Powerup Kit',
            orange_text='Beginner Challenges',
            bottom_text='Select a challenge to start making'
        )
        self.pack_start(self.header, False, False, 0)

        # add the Challenge Icons to this View
        self.challenge_group = Challenges.get_instance()[challege_group_id]
        self.challenge_icon_list = ChallengeIconList(
            self.challenge_group,
            ChallengeIcon
        )
        self.pack_start(self.challenge_icon_list, True, True, 0)

        # connecting signals

        self.header.connect(
            'back-button-pressed',
            self._on_back_button_pressed
        )

        # listen for Challenge Icon click events
        self.challenge_icon_list.connect(
            'icon-clicked',
            self._on_challenge_icon_clicked
        )

    def _on_back_button_pressed(self, button=None):
        self.emit('go-to-group-list')

    def _on_challenge_icon_clicked(self, widget=None, flowbox=None, child=None):
        """
        """

        if not child:
            return

        chal = child.challenge_like

        if not chal.locked:
            self.emit(
                'go-to-challenge',
                self.challenge_group.id_str,
                chal.id_str
            )

    def __repr__(self):
        return "{} of group {}".format(
            self.__class__.__name__,
            self.challenge_group.id_str
        )
