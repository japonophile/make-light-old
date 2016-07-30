# physical_board.py
#
# Copyright (C) 2015-2016 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#
# Defines the abstraction of board used as base for the HW boards

from make_light.boards.base.board import Board


class PhysicalBoard(Board):

    def __init__(self):
        Board.__init__(self)

    def __del__(self):
        self._clean_up()

    def detect_board(self):
        raise NotImplementedError

    def _clean_up(self):
        pass

    def _get_api_token(self):
        return ''
