# profile_helpers.py
#
# Copyright (C) 2015-2016 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#
# Implement functionality that should be taken care of by kano-profile, under
# normal circumstances. However we are not sure whether this will be available
# and thus in order not to introduce an update for our users, also do the same
# functionality here.

from kano.utils import run_bg

challenge_sound_file = \
    '/usr/share/kano-media/sounds/kano_challenge_complete.wav'


def play_completion_sound():
    # Play a rewarding sound in the background
    run_bg('/usr/bin/aplay {}'.format(challenge_sound_file))
