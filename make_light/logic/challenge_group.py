# challenge_group.py
#
# Copyright (C) 2015 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#
# Challenge Groups

import json

from os.path import join, abspath, exists

from kano.logging import logger
from kano_profile.apps import load_app_state_variable

from make_light import app_name
from make_light.paths import CHALLENGE_FILES_FMT, CHALLENGE_GROUP_ASSET_DIR, \
    CO_CHAL_GROUP_COVER_FMT
from make_light.logic.challenge import Challenge
from make_light.logic.date_transform import date_from_string


class ChallengeGroup(object):
    @staticmethod
    def from_index(path):
        """ Create an instance of the ChallegeGroup by providing the index
        file. It assumes that the index.json shares a directory with the
        challenges folder. This is the recommended way of instantiating this
        Class
        :param path: Path to the index file
        :type path: string
        :returns: Fully formed instance of ChallengeGroup
        :rtype: ChallengeGroup
        """
        try:
            with open(path) as f:
                group_cfg = json.load(f)

        except (IOError, OSError) as ex_err:
            logger.warn(
                "Couldn't open index file {}. [{}]".format(path, ex_err)
            )
            return None
        except ValueError as ex_err:
            # Thrown by the json.load potentially
            logger.warn(
                "Index at '{}' is not a valid JSON. [{}]".format(path, ex_err)
            )
            return None

        try:
            id_str = group_cfg['world']['id']
            title = group_cfg['world']['title']
            desc = group_cfg['world']['description']
            board_type = group_cfg['world']['board_type']
            display_order = group_cfg['world']['display_order']
            date_added = date_from_string(group_cfg['date_added'])
            challenge_order = group_cfg['challenge_order']
        except KeyError as ex_err:
            logger.warn(
                "Index file '{}' is malformed. [{}] ".format(path, ex_err)
            )
            return None
        except (ValueError, TypeError) as ex_err:
            logger.warn(
                "Can't encode the date, check it is in the right format. [{}]"
                .format(ex_err)
            )
        else:
            basedir = abspath(join(path, '..'))
            return ChallengeGroup(basedir,
                                  id_str,
                                  title,
                                  desc,
                                  board_type,
                                  display_order,
                                  date_added,
                                  challenge_order)

    def __init__(self,
                 path,
                 id_str,
                 title,
                 desc,
                 board_type,
                 display_order,
                 date_added,
                 challenge_order):
        self.path = path
        self.id_str = id_str
        self.title = title
        self.description = desc
        self.board_type = board_type
        self.display_order = display_order
        self.date_added = date_added
        self._challenge_order = challenge_order
        self._challenges = []

    def __repr__(self):
        return "ChallengeGroup '{}'".format(self.id_str)

    @property
    def image_path(self):
        # first check if the asset is available in an adjacent folder
        # This is we expect them from kano_content
        co_path = abspath(
            join(self.path, CO_CHAL_GROUP_COVER_FMT.format(id_str=self.id_str))
        )
        if exists(co_path):
            return co_path
        else:
            return join(
                CHALLENGE_GROUP_ASSET_DIR, '{}.png'.format(self.id_str)
            )

    @property
    def challenges(self):
        if len(self._challenges) == 0:
            self._init_challenges()
        return self._challenges

    def _init_challenges(self):
        challenge_files = (join(self.path, CHALLENGE_FILES_FMT.format(k))
                           for k in self._challenge_order)
        for idx, chal_file in enumerate(challenge_files):
            # challenge_instances =
            inst = Challenge.get_from_challenge_file(chal_file, self)
            if inst is None:
                logger.warn("Couldn't import challenge {}".format(chal_file))
                continue
            self._challenges.append(inst)

    def _progress_from_profile(self):
        prof_var = load_app_state_variable(app_name, 'groups')
        if not prof_var:
            prof_var = {}
        group = prof_var.get(self.id_str, {})
        return group.get('challengeNo', 0)

    @property
    def completed(self):
        chal_no = self._progress_from_profile()
        # TODO: Find a different way of figuring out the total number of
        # challenges. This assumes that count of entries in the index.json
        # is correct
        # Avoid getting the length of the .challenges because that would load
        # them into memory
        return chal_no >= len(self._challenge_order)

    @property
    def locked(self):
        # TODO Add logic here
        return False

    def __getitem__(self, key):
        if not isinstance(key, basestring) and not isinstance(key, int):
            raise TypeError('key must be string or int')

        if isinstance(key, basestring):
            for challenge in self.challenges:
                if challenge.id_str == key:
                    return challenge

            raise KeyError(
                "Challenge with id_str '{}' not found in group '{}'"
                .format(key, self.id_str)
            )

        if isinstance(key, int):
            return self.challenges[key]

    def __iter__(self):
        return iter(self.challenges)

    def __len__(self):
        return len(self.challenges)

    def index(self, value):
        inst = self[value]
        return self.challenges.index(inst)

    @staticmethod
    def get_newer(a, b):
        """ Returns the newest of the two challenge groups
        :param a: One of the groups to be compared
        :type a: ChallengeGroup
        :param b: the other group to be compared
        :type b: ChallengeGroup
        :returns: The one with the most recent date_added
        :rtype: ChallengeGroup
        """

        if a.date_added >= b.date_added:
            return a
        else:
            return b
