# challenge_view.py
#
# Copyright (C) 2015-2016 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#
# TODO: description


from gi.repository import Gtk, GObject

from kano_profile.challenge_progress_tracker import ChallengeProgressTracker

from make_light.gtk3.components.headers import ChallengeHeader
from make_light.gtk3.components.light_ide import LightIDE, \
    ChallangeSimulatorFooter


class ChallengeView(Gtk.Box):

    __gsignals__ = {
        'go-to-challenge-list': (
            GObject.SIGNAL_RUN_LAST,
            GObject.TYPE_NONE,
            (str, bool)
        ),
        'go-to-challenge': (
            GObject.SIGNAL_RUN_LAST,
            GObject.TYPE_NONE,
            (str, int, bool)
        )
    }

    def __init__(self, window, challenge):
        Gtk.Box.__init__(self, orientation=Gtk.Orientation.VERTICAL)

        self.window = window
        self.challenge = challenge

        # the view layout
        self.challenge_header = ChallengeHeader(
            challenge,
            is_final=challenge.is_final()
        )
        self.pack_start(self.challenge_header, False, False, 0)

        self.light_ide = LightIDE(window, ChallangeSimulatorFooter)
        self.pack_start(self.light_ide, True, True, 0)

        # connecting signals

        # on BACK / NEXT buttons pressed
        self.challenge_header.connect(
            'back-button-pressed',
            self._on_back_pressed
        )
        if challenge.is_final():
            self.challenge_header.connect(
                'done-button-pressed',
                self._on_done_pressed
            )
        else:
            self.challenge_header.connect(
                'next-button-pressed',
                self._on_next_pressed
            )

        # notify the Light IDE that the challenge was completed
        self.challenge_header.connect(
            'challenge-done',
            self.light_ide.on_challenge_done
        )

        # notify the Challenge Header that the MAKE button was pressed
        self.light_ide.code_edit.connect(
            'make',
            self.challenge_header.on_make
        )

        # notify the Challenge Header that the code has changed
        self.light_ide.code_edit.connect(
            'code-changed',
            self.challenge_header.on_code_changed
        )

        ChallengeProgressTracker.get_instance().start_challenge(
            self.challenge.group_id, self.challenge.idx
        )

    def make(self):
        self.light_ide.make()

    def _on_back_pressed(self, widget=None):
        ChallengeProgressTracker.get_instance().stop_challenge(
            self.challenge.group_id, self.challenge.idx
        )
        self.emit('go-to-challenge-list', self.challenge.group_id, False)

    def _on_next_pressed(self, widget=None):
        ChallengeProgressTracker.get_instance().stop_challenge(
            self.challenge.group_id, self.challenge.idx
        )
        self.emit(
            'go-to-challenge',
            self.challenge.group_id,
            self.challenge.idx + 1,
            True
        )

    def _on_done_pressed(self, widget=None):
        ChallengeProgressTracker.get_instance().stop_challenge(
            self.challenge.group_id, self.challenge.idx
        )
        self.emit(
            'go-to-challenge-list',
            self.challenge.group_id,
            self.challenge.is_final()
        )
