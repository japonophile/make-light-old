# challenge.py
#
# Copyright (C) 2015 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#
# Challenge

import json
import re
import weakref

from os.path import join, abspath, exists

from kano.logging import logger
from kano_profile.apps import load_app_state_variable
from kano_profile.badges import save_app_state_variable_with_dialog
from kano_profile.challenge_progress_tracker import ChallengeProgressTracker

from make_light import app_name
from make_light.paths import CHALLENGE_ASSET_DIR, CO_CHAL_COVER_FMT
from make_light.profile_helpers import play_completion_sound


class Challenge(object):

    @staticmethod
    def get_from_challenge_file(path, group_instance):
        group_path = abspath(join(path, '..'))
        try:
            with open(path) as f_handle:
                challenge = json.load(f_handle)
            id_str = challenge["id"]
            title = challenge["title"]
            description = challenge["description"]
            content = challenge["content"]
        except (IOError, OSError) as err_exc:
            logger.error(
                "Can't open challenge file {}. [{}]".format(path, err_exc)
            )
            return None
        except ValueError as err_exc:
            # Thrown by the json.load potentially
            logger.error(
                "Invalid JSON: Challenge file '{}'. [{}]".format(path, err_exc)
            )
            return None
        except KeyError as err_exc:
            logger.error(
                "Challenge file '{}' is malformed. [{}]".format(path, err_exc)
            )
            return None

        return Challenge(
            group_path, group_instance, id_str, title, description, content
        )

    @property
    def image_path(self):
        co_path = abspath(
            join(
                self._group_path,
                CO_CHAL_COVER_FMT.format(id_str=self.id_str)
            )
        )
        if exists(co_path):
            return co_path
        else:
            return join(CHALLENGE_ASSET_DIR, '{}.png'.format(self.id_str))

    def __init__(self,
                 group_path,
                 group_instance,
                 id_str,
                 title,
                 description,
                 content):
        self._group_path = group_path
        # Add a weakref to the group_instance (which is a parent) to allow it
        # to be garbage collected if we need to delete it
        self._group_instance = weakref.proxy(group_instance)
        self.id_str = id_str
        self.title = title
        self.description = description
        self.content = content
        self._code = ''

    @property
    def idx(self):
        if self._group_instance:
            return self._group_instance.index(self.id_str)

    @property
    def group_id(self):
        if self._group_instance:
            return self._group_instance.id_str

    @property
    def code(self):
        if not self._code:
            self._code = self._read_code(self._group_path)
        return self._code

    def is_final(self):
        """Returns whether this challenge is the last one in its challenge
        group. This information may be necessary to adjust the corresponding
        view
        :returns: True if it is the last challenge, False otherwise
                  Also returns None if the challenge doesn't know of the
                  challenge group it belongs to
        :rtype: Boolean
        """
        if self._group_instance:
            return self.idx == (len(self._group_instance) - 1)

    def _read_code(self, group_path):
        code_file = join(group_path, '{}.py'.format(self.id_str))
        try:
            with open(code_file) as f_handle:
                challenge_code = f_handle.read().strip()
        except (IOError, OSError) as err_exc:
            logger.error("Can't open '{}' [{}]".format(code_file, err_exc))
            challenge_code = ''

        return challenge_code

    def _progress_from_profile(self):
        prof_var = load_app_state_variable(app_name, 'groups')
        if not prof_var:
            prof_var = {}
        group = prof_var.get(self.group_id, {})
        return group.get('challengeNo', 0)

    def _set_profile_progress_to_current(self):
        """ Set profile progress to the current challenge index.
        Only updates the progress if the index of the current challenge is
        greater than the one currently stored
        """
        prof_var = load_app_state_variable(app_name, 'groups')
        if not prof_var:
            prof_var = {}
        group = prof_var.setdefault(self.group_id, {})
        profile_progress = group.setdefault('challengeNo', 0)
        if self.idx >= profile_progress:
            prof_var[self.group_id]['challengeNo'] = self.idx + 1
            save_app_state_variable_with_dialog(app_name, 'groups', prof_var)

            play_completion_sound()

            ChallengeProgressTracker.get_instance().unlocked_challege(
                self.group_id, self.idx
            )
        else:
            ChallengeProgressTracker.get_instance().completed_challenge(
                self.group_id, self.idx
            )

    @property
    def completed(self):
        chal_no = self._progress_from_profile()
        return chal_no > self.idx

    @completed.setter
    def completed(self, value):
        # ATM we can't relock challenges
        if value is True or value == 1:
            self._set_profile_progress_to_current()

    @property
    def locked(self):
        # TODO add logic here
        # Unlock only if previous is completed
        chal_no = self._progress_from_profile()

        return chal_no < self.idx

    def get_re(self, stepnum):
        """
        Return the regexp for a particular step
        """
        try:
            code_line = self.content[stepnum].get("code")
            if code_line is not None:
                code_re = re.compile(code_line)
            else:
                code_re = None
        except IndexError as exc_err:
            logger.error(
                "Step number {} doesn't exist [{}]".format(stepnum, exc_err)
            )
            code_line = ""
            code_re = None
        return (code_line, code_re)

    def __repr__(self):
        return "Challenge: '{}'".format(self.id_str)

    def __len__(self):
        return len(self.content)
