# group_list_view.py
#
# Copyright (C) 2015 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#
# TODO: description


from gi.repository import Gtk, GObject

from make_light.logic import Challenges
from make_light.gtk3.components.headers import ListHeader
from make_light.gtk3.components.challenge_icons import ChallengeGroup
from make_light.gtk3.components.challenge_icon_list import ChallengeIconList


class GroupListView(Gtk.Box):
    """
    """

    __gsignals__ = {
        'go-to-main-menu': (GObject.SIGNAL_RUN_LAST, GObject.TYPE_NONE, ()),
        'go-to-challenge-list':
            (GObject.SIGNAL_RUN_LAST, GObject.TYPE_NONE, (str,))
    }

    def __init__(self):
        Gtk.Box.__init__(self, orientation=Gtk.Orientation.VERTICAL)

        # add a Header to this View
        self.header = ListHeader(
            white_text=_('Powerup Kit'),  # TODO: get these from challenge_group_data
            orange_text=_('Challenges'),
            bottom_text=_('Select a set of challenges to start making')
        )
        self.pack_start(self.header, False, False, 0)

        # add the Challenge Icons to this View
        self.challenge_groups = Challenges.get_instance()
        self.group_icon_list = ChallengeIconList(
            self.challenge_groups,
            ChallengeGroup
        )
        self.pack_start(self.group_icon_list, True, True, 0)

        # connecting signals

        # clicking BACK will take you to the app Main Menu
        self.header.connect(
            'back-button-pressed',
            self._on_back_button_pressed
        )

        # listen for Challenge Icon click events
        self.group_icon_list.connect(
            'icon-clicked',
            self._on_group_icon_clicked
        )

    def _on_back_button_pressed(self, button=None):
        self.emit('go-to-main-menu')

    def _on_group_icon_clicked(self, widget=None, flowbox=None, child=None):
        """
        """

        if not child:
            return

        grp = child.challenge_like

        if not grp.locked:
            self.emit(
                'go-to-challenge-list',
                grp.id_str
            )
