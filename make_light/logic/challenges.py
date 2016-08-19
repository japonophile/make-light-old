# challenges.py
#
# Copyright (C) 2015 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#
# Challenges


from os import listdir
from os.path import join, isdir, abspath, exists
from itertools import ifilter, chain

from kano.logging import logger

from make_light.paths import INDEX_FILE_NAME, \
    ADDITIONAL_CHALLENGE_GROUPS
from make_light.logic.challenge_group import ChallengeGroup
from make_light.utils import get_challenges_path


class Challenges(object):
    __singleton_inst = None

    @staticmethod
    def get_instance():
        if Challenges.__singleton_inst is None:
            return Challenges()
        else:
            return Challenges.__singleton_inst

    def __init__(self):
        self._groups = []
        self._device = ''

        Challenges.__singleton_inst = self

    @property
    def device(self):
        return self._device

    @device.setter
    def device(self, value):
        if self._device != value:
            # Clear the internal list
            self._groups = []
            self._device = value

    @property
    def groups(self):
        if len(self._groups) == 0:
            self._get_groups()
        return self._groups

    def _group_if_in_list(self, id_str):
        for challenge_group in self._groups:
            if challenge_group.id_str == id_str:
                return challenge_group

    def _add_to_group_list(self, chal_group):
        """ Add an instance of ChallengeGroup to the internal list only if it
        there isn't a newer version of that group.
        """
        # now check whether there is a group already in the list that
        # shares the same id
        chal_group_existent = self._group_if_in_list(chal_group.id_str)
        if chal_group_existent:
            keeper = ChallengeGroup.get_newer(
                chal_group_existent,
                chal_group
            )
            if keeper == chal_group:
                logger.debug(
                    'Replaced existing group {} with newer verion'.format(
                        chal_group_existent
                    )
                )
                self._groups.remove(chal_group_existent)
                self._groups.append(keeper)
        else:
            logger.debug(
                'Added group {}'.format(chal_group)
            )
            self._groups.append(chal_group)

    def _get_groups(self):
        dirs = chain(
            self._dirs_app_installed_iter(), self._dirs_from_kano_content()
        )

        for group in dirs:
            # Look for index.json
            group_index_file = join(group, INDEX_FILE_NAME)
            if not exists(group_index_file):
                logger.warn(
                    "Index file not found in {}, skipping...".format(group)
                )
                continue
            chal_group_new = ChallengeGroup.from_index(group_index_file)
            if chal_group_new is None:
                continue
            self._add_to_group_list(chal_group_new)

        # Now sort according to display_order
        self._groups.sort(
            key=lambda x: (-1 * x.display_order, x.date_added),
            reverse=True
        )
        # Filter challenge groups in device is set up
        if self.device:
            self._groups = [k for k in self._groups
                            if k.board_type == self.device]

    @staticmethod
    def _dirs_app_installed_iter():
        # First interate over the challenges folder
        challenges_path = get_challenges_path()
        dir_content = (
            abspath(join(challenges_path, d))
            for d in listdir(challenges_path)
        )
        # Get the directories

        return ifilter(isdir, dir_content)

    @staticmethod
    def _dirs_from_kano_content():
        return iter(ADDITIONAL_CHALLENGE_GROUPS)

    def __len__(self):
        return len(self.groups)

    def __getitem__(self, key):
        if not isinstance(key, basestring) and not isinstance(key, int):
            raise TypeError("key must be string or int")

        if isinstance(key, basestring):
            for group in self.groups:
                if key == group.id_str:
                    return group
            raise KeyError("Group with id_str '{}' not found".format(key))

        if isinstance(key, int):
            return self.groups[key]
